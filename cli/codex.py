"""Codex CLI adapter for executing runs and reviews."""

import logging
from pathlib import Path
from typing import Optional

from config import Config
from models.requests import ToolExecutionResponse
from process import ProcessResult, run_process

logger = logging.getLogger("ai_cli_mcp.codex")


class CodexAdapter:
    """Adapter for spawning and managing OpenAI Codex CLI processes."""

    @classmethod
    def get_binary_path(cls) -> Path:
        """Resolves binary path or raises FileNotFoundError."""
        binary = Config.find_codex_path()
        if not binary or not binary.exists():
            raise FileNotFoundError(
                "Codex CLI executable ('codex' or 'codex.exe') was not found on PATH or known directories. "
                "Please install Codex CLI or set the CODEX_CLI_PATH environment variable."
            )
        return binary

    @classmethod
    async def run(
        cls,
        prompt: str,
        working_directory: str,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
        yolo: bool = True,
    ) -> ToolExecutionResponse:
        """
        Executes a prompt using Codex CLI in non-interactive exec mode.
        """
        binary = cls.get_binary_path()
        cwd = Config.validate_working_directory(working_directory)
        timeout_sec = Config.clamp_timeout(timeout)

        # Build command arguments
        cmd = [str(binary), "exec"]

        # YOLO mode: bypass approvals and sandboxing for autonomous execution
        if yolo:
            cmd.append("--dangerously-bypass-approvals-and-sandbox")

        # Allow running outside git repo
        cmd.append("--skip-git-repo-check")

        # Explicit working directory
        cmd.extend(["--cd", str(cwd)])

        # Clean output without terminal escape codes
        cmd.extend(["--color", "never"])

        # Model selection
        chosen_model = model or Config.CODEX_DEFAULT_MODEL
        if chosen_model:
            cmd.extend(["-m", chosen_model])

        # Prompt instruction
        cmd.append(prompt)

        logger.info(f"Running Codex command in {cwd}: {' '.join(cmd)}")
        result: ProcessResult = await run_process(cmd, cwd=cwd, timeout_seconds=timeout_sec)

        summary = (
            f"Codex run completed successfully in {result.duration_seconds:.1f}s."
            if result.success
            else f"Codex run failed with exit code {result.exit_code} (timed_out={result.timed_out})."
        )

        return ToolExecutionResponse(
            success=result.success,
            cli="codex",
            action="run",
            exit_code=result.exit_code,
            duration_seconds=result.duration_seconds,
            timed_out=result.timed_out,
            cwd=str(cwd),
            output=result.stdout,
            stderr=result.stderr,
            summary=summary,
            details={
                "model": chosen_model,
                "yolo": yolo,
                "timeout_configured": timeout_sec,
            },
        )

    @classmethod
    async def review(
        cls,
        working_directory: str,
        instructions: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
        uncommitted: bool = True,
    ) -> ToolExecutionResponse:
        """
        Executes a code review using Codex CLI review mode.
        """
        binary = cls.get_binary_path()
        cwd = Config.validate_working_directory(working_directory)
        timeout_sec = Config.clamp_timeout(timeout)

        # Check git repo existence
        git_dir = cwd / ".git"
        if not git_dir.exists():
            return ToolExecutionResponse(
                success=False,
                cli="codex",
                action="review",
                exit_code=1,
                duration_seconds=0.0,
                timed_out=False,
                cwd=str(cwd),
                output="",
                stderr=f"Directory '{cwd}' is not a Git repository. Codex review requires a Git repository.",
                summary="Codex review aborted: Target directory is not a Git repository.",
                details={"git_present": False},
            )

        cmd = [str(binary), "review"]

        if uncommitted:
            cmd.append("--uncommitted")

        chosen_model = model or Config.CODEX_DEFAULT_MODEL
        if chosen_model:
            cmd.extend(["-c", f'model="{chosen_model}"'])

        if instructions and instructions.strip():
            cmd.append(instructions.strip())

        logger.info(f"Running Codex review in {cwd}: {' '.join(cmd)}")
        result: ProcessResult = await run_process(cmd, cwd=cwd, timeout_seconds=timeout_sec)

        summary = (
            f"Codex review completed successfully in {result.duration_seconds:.1f}s."
            if result.success
            else f"Codex review failed with exit code {result.exit_code} (timed_out={result.timed_out})."
        )

        return ToolExecutionResponse(
            success=result.success,
            cli="codex",
            action="review",
            exit_code=result.exit_code,
            duration_seconds=result.duration_seconds,
            timed_out=result.timed_out,
            cwd=str(cwd),
            output=result.stdout,
            stderr=result.stderr,
            summary=summary,
            details={
                "model": chosen_model,
                "uncommitted": uncommitted,
                "timeout_configured": timeout_sec,
            },
        )
