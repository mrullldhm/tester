"""Automatic research supervisor; import before numerical libraries.

Resource limits change scheduling/allocation only, never trading or swing rules.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
import ctypes
import fcntl
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time
import uuid

GIB = 1024 ** 3
ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = Path('/tmp/tradingview-tester-research.lock')
FD_ENV = 'TVTESTER_GUARD_FD'
TOKEN_ENV = 'TVTESTER_GUARD_TOKEN'


@dataclass(frozen=True)
class Policy:
    address_bytes: int = 6 * GIB
    tree_rss_bytes: int = 5 * GIB
    reserve_bytes: int = 2 * GIB
    reserve_fraction: float = 0.20
    swap_free_fraction: float = 0.20
    pressure_full_percent: float = 2.0
    pressure_seconds: float = 5.0
    poll_seconds: float = 0.5
    terminate_seconds: float = 1.0
    log_seconds: float = 10.0


def memory_info():
    values = {}
    for line in Path('/proc/meminfo').read_text().splitlines():
        name, _, value = line.partition(':')
        if name in ('MemTotal', 'MemAvailable', 'SwapTotal', 'SwapFree'):
            values[name] = int(value.split()[0]) * 1024
    if set(values) != {'MemTotal', 'MemAvailable', 'SwapTotal', 'SwapFree'}:
        raise RuntimeError('cannot read complete Linux memory telemetry')
    return values


def memory_pressure():
    path = Path('/proc/pressure/memory')
    if not path.exists():
        return 0.0  # Older kernels may lack PSI; RAM/swap checks remain mandatory.
    for line in path.read_text().splitlines():
        if line.startswith('full '):
            return float(dict(part.split('=', 1) for part in line.split()[1:])['avg10'])
    raise RuntimeError('cannot read Linux memory-pressure telemetry')


def group_rss(pgid):
    total = 0
    for path in Path('/proc').iterdir():
        if not path.name.isdigit():
            continue
        try:
            fields = (path / 'stat').read_text().rsplit(')', 1)[1].split()
            if int(fields[2]) == pgid:
                total += int((path / 'statm').read_text().split()[1]) * resource.getpagesize()
        except (FileNotFoundError, ProcessLookupError):
            continue
        except PermissionError:
            try:
                if os.getpgid(int(path.name)) == pgid:
                    raise RuntimeError('cannot account for a research process')
            except ProcessLookupError:
                continue
    return total


def unsafe_reason(info, rss, policy, starting=False):
    reserve = max(policy.reserve_bytes, int(info['MemTotal'] * policy.reserve_fraction))
    required = reserve + policy.address_bytes if starting else reserve
    if info['MemAvailable'] < required:
        label = 'startup requirement' if starting else 'system reserve'
        return f'available RAM {info["MemAvailable"] / GIB:.2f} GiB is below the {label} {required / GIB:.2f} GiB'
    if info['SwapTotal'] and info['SwapFree'] < info['SwapTotal'] * policy.swap_free_fraction:
        return 'less than 20% of WSL swap remains free'
    if rss > policy.tree_rss_bytes:
        return f'research process group exceeded {policy.tree_rss_bytes / GIB:g} GiB resident memory'
    return None


def validate_workers(args):
    for i, arg in enumerate(args):
        if arg == '--jobs' and (i + 1 == len(args) or args[i + 1] != '1'):
            raise SystemExit('The memory-limited runner requires --jobs 1')
        if arg.startswith('--jobs=') and arg != '--jobs=1':
            raise SystemExit('The memory-limited runner requires --jobs 1')


def guarded():
    """An environment flag alone cannot bypass the inherited lock FD and token."""
    try:
        fd = int(os.environ[FD_ENV])
        actual, expected = os.fstat(fd), LOCK_PATH.stat()
        if (actual.st_dev, actual.st_ino) != (expected.st_dev, expected.st_ino):
            return False
        meta = json.loads(os.pread(fd, 65536, 0))
        if meta['token'] != os.environ[TOKEN_ENV]:
            return False
        with LOCK_PATH.open('r') as probe:
            try:
                fcntl.flock(probe, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return True
            fcntl.flock(probe, fcntl.LOCK_UN)
    except (KeyError, ValueError, OSError, json.JSONDecodeError):
        pass
    return False


def stop_group(proc, grace):
    """Stop only this job's new session, including descendants, never the caller group."""
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    deadline = time.monotonic() + grace
    while time.monotonic() < deadline:
        proc.poll()
        try:
            os.killpg(proc.pid, 0)
        except ProcessLookupError:
            return
        time.sleep(min(0.05, max(0, deadline - time.monotonic())))
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    proc.wait()


def supervise(args, policy=Policy(), *, read_memory=memory_info, read_pressure=memory_pressure,
              read_rss=group_rss, lock_path=None, log_dir=None):
    validate_workers(args)
    lock_path = LOCK_PATH if lock_path is None else Path(lock_path)
    log_dir = ROOT / 'logs/resource_guard' if log_dir is None else Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + f'_{os.getpid()}_{uuid.uuid4().hex[:8]}'
    with (log_dir / f'{run_id}.jsonl').open('x', buffering=1) as log, lock_path.open('a+') as lock:
        def record(event, **fields):
            log.write(json.dumps({'utc': datetime.now(timezone.utc).isoformat(), 'event': event, **fields}) + '\n')

        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            record('refused', reason='another research job holds the execution lock')
            print('Research refused: another research job or chart replay is running.', file=sys.stderr)
            return 75
        try:
            reason = unsafe_reason(read_memory(), 0, policy, starting=True)
        except Exception as error:
            reason = str(error)
        if reason:
            record('refused', reason=reason)
            print(f'Research refused: {reason}', file=sys.stderr)
            return 75
        token = uuid.uuid4().hex
        lock.seek(0)
        lock.truncate()
        json.dump({'token': token, 'supervisor_pid': os.getpid(), 'log': str(log.name)}, lock)
        lock.flush()
        env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                   NUMEXPR_NUM_THREADS='1', MALLOC_ARENA_MAX='2', MPLCONFIGDIR='/tmp/tvtester-mpl')
        env[FD_ENV], env[TOKEN_ENV] = str(lock.fileno()), token
        supervisor_pid = os.getpid()

        def limit():
            # Linux PR_SET_PDEATHSIG: the workload must not outlive its monitor.
            libc = ctypes.CDLL(None, use_errno=True)
            libc.prctl.argtypes = [ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong]
            if libc.prctl(1, signal.SIGKILL, 0, 0, 0) != 0:
                raise OSError(ctypes.get_errno(), "cannot install supervisor-death protection")
            if os.getppid() != supervisor_pid:
                os._exit(125)
            inherited = resource.getrlimit(resource.RLIMIT_AS)[1]
            cap = policy.address_bytes if inherited == resource.RLIM_INFINITY else min(policy.address_bytes, inherited)
            resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
            os.nice(10)

        requested = []
        previous = {sig: signal.signal(sig, lambda signum, frame: requested.append(signum))
                    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)}
        proc, peak = None, 0
        try:
            proc = subprocess.Popen([sys.executable, '-u', *args], env=env, preexec_fn=limit,
                                    pass_fds=(lock.fileno(),), start_new_session=True)
            record('started', pid=proc.pid, address_limit_bytes=policy.address_bytes,
                   rss_limit_bytes=policy.tree_rss_bytes,
                   entrypoint=args[1] if args[0] == '-m' else Path(args[0]).name)
            print(f'Research guard: one job, {policy.address_bytes / GIB:g} GiB address-space cap, '
                  f'{policy.tree_rss_bytes / GIB:g} GiB group RSS cap; log {log.name}', file=sys.stderr)
            pressure_since, last_log, reason = None, 0.0, None
            while proc.poll() is None:
                if requested:
                    reason = f'received signal {requested[0]}'
                    break
                try:
                    info, rss, pressure = read_memory(), read_rss(proc.pid), read_pressure()
                    peak = max(peak, rss)
                    now = time.monotonic()
                    reason = unsafe_reason(info, rss, policy)
                    if pressure >= policy.pressure_full_percent:
                        pressure_since = now if pressure_since is None else pressure_since
                        if now - pressure_since >= policy.pressure_seconds:
                            reason = 'sustained full memory pressure'
                    else:
                        pressure_since = None
                    if now - last_log >= policy.log_seconds or reason:
                        record('sample', available_bytes=info['MemAvailable'], swap_free_bytes=info['SwapFree'],
                               group_rss_bytes=rss, pressure_full_avg10=pressure)
                        last_log = now
                except Exception as error:
                    reason = f'memory telemetry failed: {error}'
                if reason:
                    break
                time.sleep(policy.poll_seconds)
            if reason:
                stop_group(proc, policy.terminate_seconds)
                code = 128 + requested[0] if requested else 75
                record('aborted', reason=reason, exit_code=code, peak_group_rss_bytes=peak)
                print(f'Research stopped safely: {reason}. Partial outputs remain incomplete; use a new run tag.', file=sys.stderr)
                return code
            code = proc.wait()
            code = code if code >= 0 else 128 - code
            record('complete' if code == 0 else 'failed', exit_code=code, peak_group_rss_bytes=peak)
            print(f'Research finished: exit {code}; observed peak group RSS {peak / GIB:.2f} GiB', file=sys.stderr)
            return code
        finally:
            if proc is not None:
                stop_group(proc, policy.terminate_seconds)
            for sig, handler in previous.items():
                signal.signal(sig, handler)


def entrypoint(args):
    validate_workers(args)
    if not guarded():
        raise SystemExit(supervise(args))


def main():
    if not sys.argv[1:]:
        raise SystemExit('Pass Python arguments, for example: -m tvtester.cli test tupa_trade --jobs 1')
    raise SystemExit(supervise(sys.argv[1:]))


if __name__ == '__main__':
    main()
