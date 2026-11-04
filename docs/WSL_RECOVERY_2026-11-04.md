# WSL out-of-memory event and research recovery, 4 November 2026

The previous-boot kernel journal records global memory exhaustion at **22:25:14 MYT**. All **4 GiB of swap
was exhausted**. Linux killed Python PID 23022 with **6,853,348 KiB anonymous resident memory** (about 6.54 GiB).
It also killed a Chrome process. At 22:26:46, systemd reported `init.scope` failed with `oom-kill`.

Several research workloads had been launched concurrently: a parameter search with three workers,
validation, and a sequence of default runs/replays. This scheduling was unsafe for the approximately
14.47 GiB WSL memory allocation. Earlier measurements had already shown nearly full swap. The task was a
major contributor to the confirmed memory exhaustion; the logs do not separately establish a Windows
host bugcheck or hardware fault. The Windows critical-event query found no matching events that day.

Two validation retention issues amplified peak usage: the command kept the full-history Bars reference
while folds were running, and the fold loop could retain the previous result/Bars while allocating the
next yearly prefix. Those references are now released before the next allocation. No trading or swing
rules changed.

Recovery safeguards:

- `tools/run_limited.py` applies a hard **8 GiB address-space limit**, forces one BLAS thread, rejects
  multiple workers, and takes a shared process lock. At least 10 GiB available memory is required to start.
- Heavy commands run sequentially with `--jobs 1`; CLI grid and exit-study defaults are also one worker.
- Interrupted attempts remain intact. New search/validation attempts use `--run-tag recovery_20261104`.
- Durable command logs are under `logs/owner-swing-recovery-20261104/`; `/tmp` logs were lost on restart.
- Incomplete validation folders are excluded from publication unless a closing ledger event exists.

The London and Asia validation recovery runs completed with **3.17 GiB peak resident memory each** and
no swap usage at the observed checkpoints. Their validation matrices matched the saved search trials.
The authoritative swing indicator remained unchanged:

`162bba6a226acdcc518042b100f7ff33186501479dd4d0634be1c48a70f5be13`

Both current F1 reports survived the interruption. Summing their saved trade profits matched each
reported net profit to the cent. A current website export and the remaining research artifacts must finish
before the overall update is complete. The final research summary records completion separately.

## Additional preventive hardening

The initial recovery wrapper above was subsequently replaced by automatic supervision at standard entrypoints,
continuous RAM/swap/pressure checks, a 6 GiB address-space ceiling and a 5 GiB observed group-RSS threshold.
See [the current prevention policy](WSL_PREVENTION.md). The earlier 8 GiB numbers describe the completed
recovery, not the current default.
