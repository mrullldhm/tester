"""Recovery safety checks, runnable with unittest without executing the pytest suite."""
from pathlib import Path
import subprocess
import sys
import unittest

from tvtester.experiment import tagged_run_id


class RecoverySafety(unittest.TestCase):
    def test_attempt_tags_preserve_original_ids(self):
        self.assertEqual(tagged_run_id("ny_filters"), "ny_filters")
        self.assertEqual(tagged_run_id("ny_filters", "recovery_20261104"),
                         "ny_filters_recovery_20261104")
        for tag in ("../overwrite", "", "bad-tag", "RECOVERY"):
            if tag:
                with self.assertRaises(ValueError):
                    tagged_run_id("ny_filters", tag)

    def test_limited_runner_rejects_multiple_workers(self):
        runner = Path(__file__).resolve().parents[1] / "tools/run_limited.py"
        for setting in (("--jobs", "2"), ("--jobs=3",)):
            proc = subprocess.run([sys.executable, str(runner), "-m", "tvtester.cli", "test",
                                   "tupa_trade", *setting], capture_output=True, text=True)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("requires --jobs 1", proc.stderr)


if __name__ == "__main__":
    unittest.main()
