#!/usr/bin/env bash
# Follow-up checks on the RLM lead after a re-run: ledger (touch + strict), random-date null, trade study, sessions.
# One heavy process at a time. Run detached: setsid nohup studies/rlm/followup.sh > studies/rlm/followup.log
set -euo pipefail
cd "$(dirname "$0")/../.."
ulimit -v 6000000
export PYTHONPATH=.
PY=.venv/bin/python
S="sig_tf=1h reg=confirm sources=all weight=flat tol=0.4 score=50 clv=0.6 entry=close stop=band exit=r1"
$PY -m cltester.cli test rlm --period dev --set $S session=all
$PY -m cltester.cli test rlm --period dev --through 1 --set $S session=all
$PY -m studies.rlm.null --runs 300 --tag lead --set $S session=all
$PY -m studies.rlm.trades --tag lead --set $S session=all > studies/rlm/trades_lead_dev.txt
$PY -m studies.rlm.sessions > studies/rlm/sessions_dev.txt
echo FOLLOWUP DONE
