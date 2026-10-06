import sys

from scripts.run_bounded import run_bounded


def test_returns_the_child_failure_instead_of_a_false_pass():
    assert run_bounded([sys.executable, '-c', 'raise SystemExit(7)'], timeout=5) == 7


def test_hanging_child_is_terminated_with_nonzero_status():
    assert run_bounded([sys.executable, '-c', 'import time; time.sleep(30)'], timeout=0.1) == 124


def test_successful_child_completes():
    assert run_bounded([sys.executable, '-c', 'pass'], timeout=5) == 0


def test_deadline_kills_descendant_when_parent_exits_on_term(tmp_path):
    import os
    import signal
    import time
    pidfile = tmp_path / 'pid'
    heartbeat = tmp_path / 'heartbeat'
    child = f'''import os, signal, time
from pathlib import Path
signal.signal(signal.SIGTERM, signal.SIG_IGN)
Path({str(pidfile)!r}).write_text(str(os.getpid()))
while True:
    Path({str(heartbeat)!r}).touch()
    time.sleep(0.05)
'''
    parent = f'import subprocess, sys, time; subprocess.Popen([sys.executable, "-c", {child!r}]); time.sleep(30)'
    try:
        assert run_bounded([sys.executable, '-c', parent], timeout=1) == 124
        before = heartbeat.stat().st_mtime_ns
        time.sleep(0.2)
        assert heartbeat.stat().st_mtime_ns == before, 'descendant survived the deadline'
    finally:
        if pidfile.exists():
            try:
                os.kill(int(pidfile.read_text()), signal.SIGKILL)
            except ProcessLookupError:
                pass
