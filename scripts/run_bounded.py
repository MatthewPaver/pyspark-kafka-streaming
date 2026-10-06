"""Run a local command with a hard deadline, including its child processes."""
import argparse
import os
import signal
import subprocess
import sys


def run_bounded(command, *, timeout):
    process = subprocess.Popen(command, start_new_session=True)
    try:
        return process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        print(f"FAILED: command exceeded {timeout}s; terminating its process group", file=sys.stderr)
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass
        # The direct parent may have exited while a descendant ignored TERM.
        # Its process group remains ours even after the parent has been reaped.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()
        return 124


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--timeout', type=float, default=180)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if not args.command or args.timeout <= 0:
        parser.error('provide a command and positive timeout')
    raise SystemExit(run_bounded(args.command, timeout=args.timeout))
