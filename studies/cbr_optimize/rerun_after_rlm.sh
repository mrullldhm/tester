#!/usr/bin/env bash
# Waits for the RLM dev re-run to finish (RAM: one heavy job at a time), then regenerates the CBR optimize study.
cd "$(dirname "$0")/../.."
while pgrep -f "studies/rlm/rerun.sh" >/dev/null; do sleep 60; done
ulimit -v 7500000
PYTHONPATH=. .venv/bin/python -m studies.cbr_optimize.run > studies/cbr_optimize/results_dev.txt 2>&1
echo "CBR DONE exit $?"
