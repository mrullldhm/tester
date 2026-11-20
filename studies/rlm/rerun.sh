#!/usr/bin/env bash
# Full RLM dev re-run after a strategy change: grid -> merge -> screen -> family collect -> Reality Check.
# Memory: 3 workers, 4.5 GB address cap per process (11 GB machine). Run detached: setsid nohup studies/rlm/rerun.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
ulimit -v 4500000
export PYTHONPATH=.
PY=.venv/bin/python
$PY -m studies.rlm.grid --workers 3
$PY -m studies.rlm.grid --merge
grid=$(ls -t studies/rlm/grid_dev_*.csv | grep -v screened | head -1)
$PY -m studies.rlm.screen "$grid" > studies/rlm/screen_dev.txt
$PY -m studies.rlm.family --collect --workers 3
$PY -m studies.rlm.family --boots 1000 --block 5 > studies/rlm/family_check.txt
echo RERUN DONE
