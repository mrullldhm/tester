# WSL crash prevention

The 4 November failure was confirmed WSL memory exhaustion. Protection now has two layers: automatic
project supervision and a Windows-side WSL budget. Swing detection, prices, fills and trading rules are unchanged.

## Automatic project limits

Standard research CLI commands, Feature 0 default runs, data updates, the CL importer and private chart
workers launch `tvtester/resource_guard.py` before numerical libraries are imported. No special command
is needed. Custom scripts must use `tools/run_limited.py`.

| Protection | Current setting | Effect |
|---|---|---|
| Execution lock | One heavy workload | Reject another job or chart worker until the lock is free |
| Workers / numerical threads | One worker, one BLAS thread | Reject `--jobs` values other than 1 |
| Address space | 6 GiB, hard `RLIMIT_AS` | The kernel refuses larger allocations in the workload process |
| Process-group resident memory | 5 GiB, sampled every 0.5 seconds | Stop the job group before it grows further |
| System RAM reserve | 20% of WSL RAM, at least 2 GiB | Refuse at startup unless reserve plus 6 GiB is available; stop if the reserve is breached |
| Swap reserve | 20% free when swap is configured | Refuse/stop before swap is exhausted |
| Full memory pressure | PSI avg10 >= 2% for 5 seconds | Stop a persistently stalled workload |
| Scheduling | Nice level +10 | Let normal interactive processes take priority |
| Supervisor failure | Linux parent-death signal | Kill the workload if its supervisor unexpectedly dies |
| Chart idle cleanup | 30 seconds | Release cached bars and the execution lock without stopping the dev server |

The supervisor sends SIGTERM to its own job session, then SIGKILL after a one-second grace period. It
forwards Ctrl-C, termination and terminal-close requests. It does not terminate unrelated jobs. It also
cleans up descendants remaining in that process group after the main workload exits.

`logs/resource_guard/*.jsonl` records startup, sampled RAM/swap/group RSS, successful completion, failure,
refusal or safety abort. Command contents and environment secrets are not logged. The chart worker's
stdout remains its existing JSON protocol; diagnostics go to stderr.

A safety abort is a failed/incomplete attempt, never a completed research result. Read its log, close idle
memory consumers or reduce the requested data interval only if the research protocol permits it. Never
change swing rules or loosen guards to force a successful run. Preserve partial artifacts and choose a
new `--run-tag` where required.

## Windows-side WSL budget

The reviewed file is `config/wslconfig.recommended`; installer: `tools/apply-wsl-prevention.ps1`.
The installer creates `%USERPROFILE%\.wslconfig`, refuses to overwrite a different existing configuration,
and never shuts WSL down itself. If PowerShell script execution is disabled, copy the reviewed template
as a data file instead; changing execution policy is unnecessary.

The current Windows file was installed at `C:\Users\mrull\.wslconfig` and verified byte-for-byte against
the reviewed template. Activation is pending a WSL restart.

```ini
[wsl2]
memory=12GB
processors=6
swap=8GB
```

The laptop has 29.67 GiB usable RAM and 12 logical processors. This budget leaves Windows substantial RAM
and CPU headroom. It applies globally to WSL 2 distributions, including workloads sharing WSL with Docker;
it does not change network, mounts, existing Linux data or strategy settings.

These settings take effect after WSL fully stops and starts. When ready, save work and close WSL/Docker
workloads, run `wsl --shutdown` from Windows PowerShell, then reopen WSL. A laptop restart is not required.
The command stops all running WSL distributions. See [Microsoft's WSL configuration documentation](https://learn.microsoft.com/en-us/windows/wsl/wsl-config).

The project safeguards work immediately, before that restart. After reopening WSL, check `free -h` and
`nproc` to confirm the memory/swap budget and six CPUs. The safety guard refuses a job when the remaining
headroom is insufficient, rather than relying on swap to keep the job running.

## Verification

Tests simulate low RAM, exhausted swap, process-group growth and pressure without exhausting real host
resources. They check allocation refusal, overlapping-job rejection, unrelated-process survival, inherited
limits, automatic CLI enforcement, parent-death cleanup and chart JSON compatibility. Run with unittest;
pytest is not required. A full-history default-strategy smoke run verifies unchanged saved trading totals
under the new limits.

Verification on 4 November 2026: 35 targeted unittest checks passed. The 5,674,164-bar CL default-run
smoke test retained 3,656 closed trades and net P&L of -21,527.12 USD, with 2.15 GiB observed peak
process-group RSS. The chart integration passed Node syntax checking and Astro reported no type errors
or warnings. Pytest was not run.

These measures address the observed research-memory failure. They do not guarantee that unrelated
unmanaged WSL programs, kernel faults or hardware failures cannot cause a different crash.
