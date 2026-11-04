"""Compatibility entrypoint for the automatic research supervisor."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tvtester.resource_guard import main

if __name__ == '__main__':
    main()
