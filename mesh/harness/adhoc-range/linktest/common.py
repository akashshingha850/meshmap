"""Shared helpers: errors, logging and subprocess wrappers."""

from __future__ import annotations

import logging
import shutil
import subprocess
from typing import Sequence


class LinkTestError(RuntimeError):
    """A failure the user can act on; CLIs print it without a traceback."""


def setup_logging(verbose: bool = False) -> None:
    """Configure root logging for the CLIs."""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(message)s",
        datefmt="%H:%M:%S",
    )


def require_tools(tools: Sequence[str]) -> None:
    """Raise LinkTestError naming every missing executable."""
    missing = [t for t in tools if shutil.which(t) is None]
    if missing:
        raise LinkTestError(
            f"missing required tool(s): {', '.join(missing)}. "
            f"Install with: sudo apt install iw iperf3 iputils-ping"
        )


def run(cmd: Sequence[str], timeout: float) -> tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr).

    A non-zero exit is not an error here: iperf3 reports failures in its JSON
    and `iw` failures are handled by the caller.
    """
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
    except FileNotFoundError as exc:
        raise LinkTestError(f"command not found: {cmd[0]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise LinkTestError(f"timed out after {timeout:.0f}s: {' '.join(cmd)}") from exc
    return proc.returncode, proc.stdout, proc.stderr
