"""Async process execution with streaming, timeout management, and Windows tree cleanup."""

import asyncio
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


ANSI_ESCAPE_PATTERN = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def strip_ansi(text: str) -> str:
    """Removes ANSI color and cursor control sequences from terminal output."""
    return ANSI_ESCAPE_PATTERN.sub("", text)


@dataclass
class ProcessResult:
    """Detailed result of an executed CLI process."""

    command: List[str]
    cwd: str
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    timed_out: bool = False

    @property
    def success(self) -> bool:
        """Process succeeded if exit code is 0 and it did not time out."""
        return self.exit_code == 0 and not self.timed_out

    def to_dict(self) -> dict:
        """Serializes result to dictionary."""
        return {
            "success": self.success,
            "exit_code": self.exit_code,
            "duration_seconds": round(self.duration_seconds, 2),
            "timed_out": self.timed_out,
            "cwd": self.cwd,
            "command": " ".join(self.command),
            "stdout": self.stdout,
            "stderr": self.stderr,
        }


def _kill_process_tree(pid: int) -> None:
    """Forcefully terminates a process and all its child subprocesses."""
    if sys.platform == "win32":
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        except Exception:
            pass
    else:
        try:
            os.killpg(os.getpgid(pid), 9)
        except Exception:
            pass


async def run_process(
    cmd: List[str],
    cwd: Path,
    timeout_seconds: int = 300,
    env: Optional[Dict[str, str]] = None,
) -> ProcessResult:
    """
    Executes a command asynchronously, captures stdout and stderr, handles timeouts,
    and terminates hanging child processes cleanly.
    """
    start_time = time.perf_counter()
    full_env = os.environ.copy()
    if env:
        full_env.update(env)

    # Ensure UTF-8 output across standard Python and child tools
    full_env["PYTHONIOENCODING"] = "utf-8"
    full_env["PYTHONUTF8"] = "1"

    proc = None
    timed_out = False
    stdout_str = ""
    stderr_str = ""

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(cwd),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=full_env,
        )

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(),
                timeout=float(timeout_seconds),
            )
            stdout_str = strip_ansi(stdout_bytes.decode("utf-8", errors="replace"))
            stderr_str = strip_ansi(stderr_bytes.decode("utf-8", errors="replace"))
            exit_code = proc.returncode if proc.returncode is not None else -1

        except asyncio.TimeoutError:
            timed_out = True
            if proc and proc.pid:
                _kill_process_tree(proc.pid)
            try:
                if proc:
                    await asyncio.wait_for(proc.wait(), timeout=5.0)
            except Exception:
                pass
            exit_code = -1
            stderr_str = f"Execution timed out after {timeout_seconds} seconds."

    except Exception as e:
        exit_code = -1
        stderr_str = f"Failed to execute process: {str(e)}"
    finally:
        duration = time.perf_counter() - start_time

    return ProcessResult(
        command=cmd,
        cwd=str(cwd),
        exit_code=exit_code,
        stdout=stdout_str.strip(),
        stderr=stderr_str.strip(),
        duration_seconds=duration,
        timed_out=timed_out,
    )
