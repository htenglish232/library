"""Compatibility command: the pilot is now rolled out to all 53 games."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('minimal-exam-smoke-browser.py')),run_name='__main__')
