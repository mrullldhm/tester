"""Safe supervisor tests: simulate pressure; never exhaust actual host RAM or swap."""
import contextlib
from dataclasses import replace
import fcntl
import io
import json
import os
from pathlib import Path
import resource
import select
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from tvtester import resource_guard as guard

ROOT = Path(__file__).resolve().parents[1]
HEALTHY = dict(MemTotal=14 * guard.GIB, MemAvailable=12 * guard.GIB,
               SwapTotal=4 * guard.GIB, SwapFree=4 * guard.GIB)


class ResourceGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.policy = replace(guard.Policy(), poll_seconds=0.01, terminate_seconds=0.05,
                              pressure_seconds=0.02, log_seconds=0.01)

    def run_guard(self, args, **kw):
        with contextlib.redirect_stderr(io.StringIO()):
            return guard.supervise(args, self.policy, lock_path=self.base/'lock', log_dir=self.base/'logs',
                                   read_memory=kw.pop('read_memory', lambda: dict(HEALTHY)),
                                   read_pressure=kw.pop('read_pressure', lambda: 0.0), **kw)

    def events(self):
        return [json.loads(line) for p in (self.base/'logs').glob('*.jsonl')
                for line in p.read_text().splitlines()]

    def test_startup_reserve_refuses_before_spawn(self):
        low = dict(HEALTHY, MemAvailable=guard.GIB)
        with patch.object(guard.subprocess, 'Popen') as popen:
            self.assertEqual(self.run_guard(['-c','pass'], read_memory=lambda: low), 75)
            popen.assert_not_called()
        self.assertEqual(self.events()[-1]['event'], 'refused')

    def test_swap_exhaustion_refuses_before_spawn(self):
        with patch.object(guard.subprocess, 'Popen') as popen:
            self.assertEqual(self.run_guard(['-c','pass'], read_memory=lambda: dict(HEALTHY, SwapFree=0)),75)
            popen.assert_not_called()

    def test_no_swap_configuration_is_supported(self):
        self.assertIsNone(guard.unsafe_reason(dict(HEALTHY, SwapTotal=0, SwapFree=0), 0, self.policy))

    def test_execution_lock_rejects_overlap(self):
        with (self.base/'lock').open('a+') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with patch.object(guard.subprocess, 'Popen') as popen:
                self.assertEqual(self.run_guard(['-c','pass']),75)
                popen.assert_not_called()

    def test_runtime_low_memory_stops_the_child(self):
        n = 0
        def memory():
            nonlocal n
            n += 1
            return dict(HEALTHY) if n == 1 else dict(HEALTHY, MemAvailable=guard.GIB)
        self.assertEqual(self.run_guard(['-c','import time; time.sleep(20)'],read_memory=memory),75)
        self.assertEqual(self.events()[-1]['event'],'aborted')
        self.assertIn('system reserve',self.events()[-1]['reason'])

    def test_runtime_swap_pressure_stops_the_child(self):
        values=iter([dict(HEALTHY),dict(HEALTHY,SwapFree=0)])
        self.assertEqual(self.run_guard(['-c','import time; time.sleep(20)'],
                                       read_memory=lambda:next(values,dict(HEALTHY,SwapFree=0))),75)
        self.assertIn('swap',self.events()[-1]['reason'])

    def test_group_rss_limit_stops_the_child(self):
        self.assertEqual(self.run_guard(['-c','import time; time.sleep(20)'],
                                       read_rss=lambda pid:6*guard.GIB),75)
        self.assertIn('resident memory',self.events()[-1]['reason'])

    def test_sustained_pressure_stops_the_child(self):
        self.assertEqual(self.run_guard(['-c','import time; time.sleep(20)'],read_pressure=lambda:3.0),75)
        self.assertEqual(self.events()[-1]['reason'],'sustained full memory pressure')

    def test_missing_telemetry_stops_the_child(self):
        n=0
        def memory():
            nonlocal n
            n+=1
            if n>1:raise OSError('simulated unreadable telemetry')
            return dict(HEALTHY)
        self.assertEqual(self.run_guard(['-c','import time; time.sleep(20)'],read_memory=memory),75)
        self.assertIn('telemetry failed',self.events()[-1]['reason'])

    def test_small_address_limit_refuses_large_allocation(self):
        self.policy=replace(self.policy,address_bytes=64*1024**2)
        code='try:\n bytearray(128*1024**2)\nexcept MemoryError:\n raise SystemExit(0)\nraise SystemExit(1)'
        self.assertEqual(self.run_guard(['-c',code]),0)
        self.assertEqual(self.events()[-1]['event'],'complete')

    def test_direct_cli_cannot_enable_parallel_workers(self):
        p=subprocess.run([sys.executable,'-B','-m','tvtester.cli','test','tupa_trade','--jobs','2'],
                         cwd=ROOT,capture_output=True,text=True,timeout=10)
        self.assertNotEqual(p.returncode,0)
        self.assertIn('requires --jobs 1',p.stderr)

    def test_forged_environment_is_not_a_guard(self):
        with patch.dict(os.environ,{guard.FD_ENV:'999999',guard.TOKEN_ENV:'fake'}):
            self.assertFalse(guard.guarded())

    def test_child_inherits_actual_limits_and_valid_guard(self):
        code=('import json,os,resource;from tvtester.resource_guard import guarded;'
              'print(json.dumps([resource.getrlimit(resource.RLIMIT_AS)[0],'
              'os.environ["OPENBLAS_NUM_THREADS"],guarded()]))')
        p=subprocess.run([sys.executable,'-B','tools/run_limited.py','-c',code],cwd=ROOT,
                         capture_output=True,text=True,timeout=10)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(json.loads(p.stdout),[6*guard.GIB,'1',True])

    def test_chart_worker_stdout_remains_json_only(self):
        p=subprocess.run([sys.executable,'-B','web/tools/trade_replay.py'],input='invalid json\n',
                         cwd=ROOT,capture_output=True,text=True,timeout=15)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(len(p.stdout.splitlines()),1)
        self.assertIn('error',json.loads(p.stdout))
        self.assertIn('Research guard:',p.stderr)

    def test_stop_group_kills_descendants_but_not_other_jobs(self):
        unrelated=subprocess.Popen([sys.executable,'-c','import time;time.sleep(20)'])
        self.addCleanup(unrelated.wait)
        self.addCleanup(lambda:unrelated.poll() is None and unrelated.kill())
        pidfile=self.base/'grandchild'
        code=('import subprocess,sys,time;from pathlib import Path;'
              'p=subprocess.Popen([sys.executable,"-c","import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);time.sleep(20)"]);'
              f'Path({str(pidfile)!r}).write_text(str(p.pid));time.sleep(20)')
        def rss(pid):
            return 6*guard.GIB if pidfile.exists() else 0
        self.assertEqual(self.run_guard(['-c',code],read_rss=rss),75)
        self.assertIsNone(unrelated.poll())
        grandchild=int(pidfile.read_text())
        stat=Path(f'/proc/{grandchild}/stat')
        if stat.exists():self.assertEqual(stat.read_text().rsplit(')',1)[1].split()[0],'Z')
        unrelated.terminate();unrelated.wait()

    def test_supervisor_death_stops_the_workload(self):
        code='import os,time;print(os.getpid(),flush=True);time.sleep(20)'
        parent=subprocess.Popen([sys.executable,'-B','tools/run_limited.py','-c',code],
                                cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True)
        try:
            self.assertTrue(select.select([parent.stdout],[],[],5)[0])
            child=int(parent.stdout.readline())
            parent.kill();parent.wait(timeout=3)
            deadline=time.monotonic()+2
            while time.monotonic()<deadline:
                stat=Path(f'/proc/{child}/stat')
                if not stat.exists() or stat.read_text().rsplit(')',1)[1].split()[0]=='Z':break
                time.sleep(0.02)
            else:self.fail('workload survived loss of its supervisor')
        finally:
            if parent.poll() is None:parent.kill()
            parent.wait();parent.stdout.close()


if __name__=='__main__':unittest.main()
