"""Antigravity CLI (agy) adapter for executing runs and reviews."""

import logging
from pathlib import Path
from typing import Optional

from config import Config
from models.requests import ToolExecutionResponse
from process import ProcessResult, run_process

logger = logging.getLogger("ai_cli_mcp.antigravity")


class AntigravityAdapter:
    """Adapter for spawning and managing Google Antigravity CLI (agy) processes."""

    @classmethod
    def get_binary_path(cls) -> Path:
        """Resolves binary path or raises FileNotFoundError."""
        binary = Config.find_antigravity_path()
        if not binary or not binary.exists():
            raise FileNotFoundError(
                "Antigravity CLI executable ('agy' or 'agy.exe') was not found on PATH or known directories. "
                "Please install Antigravity CLI or set the AGY_CLI_PATH environment variable."
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
        Executes a prompt using Antigravity CLI in print mode (-p).
        """
        binary = cls.get_binary_path()
        cwd = Config.validate_working_directory(working_directory)
        timeout_sec = Config.clamp_timeout(timeout)

        # Build command arguments
        cmd = [str(binary), "--print", prompt]

        # YOLO mode: auto-approve all tool permissions without prompting
        if yolo:
            cmd.append("--dangerously-skip-permissions")

        # Set output format to plain text
        cmd.extend(["--output-format", "text"])

        # Model selection
        chosen_model = model or Config.ANTIGRAVITY_DEFAULT_MODEL
        if chosen_model:
            cmd.extend(["--model", chosen_model])

        # CLI internal timeout flag (formatted as e.g. 300s)
        cmd.extend(["--print-timeout", f"{timeout_sec}s"])

        logger.info(f"Running Antigravity command in {cwd}: {' '.join(cmd)}")
        result: ProcessResult = await run_process(cmd, cwd=cwd, timeout_seconds=timeout_sec)

        summary = (
            f"Antigravity run completed successfully in {result.duration_seconds:.1f}s."
            if result.success
            else f"Antigravity run failed with exit code {result.exit_code} (timed_out={result.timed_out})."
        )

        return ToolExecutionResponse(
            success=result.success,
            cli="antigravity",
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
        yolo: bool = True,
    ) -> ToolExecutionResponse:
        """
        Executes an automated code review using Antigravity CLI in print mode.
        """
        binary = cls.get_binary_path()
        cwd = Config.validate_working_directory(working_directory)
        timeout_sec = Config.clamp_timeout(timeout)

        custom_part = f"\nFocus Areas & Custom Guidelines:\n{instructions.strip()}" if instructions else ""
        review_prompt = (
            "Perform a rigorous code review of the workspace and recent changes. "
            "Inspect git diff or modified files if present, check code structure, edge cases, "
            "security vulnerabilities, performance bottlenecks, and style consistency. "
            f"Provide actionable suggestions and code diffs if improvements are needed.{custom_part}"
        )

        cmd = [str(binary), "--print", review_prompt]

        if yolo:
            cmd.append("--dangerously-skip-permissions")

        cmd.extend(["--output-format", "text"])

        chosen_model = model or Config.ANTIGRAVITY_DEFAULT_MODEL
        if chosen_model:
            cmd.extend(["--model", chosen_model])

        cmd.extend(["--print-timeout", f"{timeout_sec}s"])

        logger.info(f"Running Antigravity review in {cwd}: {' '.join(cmd)}")
        result: ProcessResult = await run_process(cmd, cwd=cwd, timeout_seconds=timeout_sec)

        summary = (
            f"Antigravity review completed successfully in {result.duration_seconds:.1f}s."
            if result.success
            else f"Antigravity review failed with exit code {result.exit_code} (timed_out={result.timed_out})."
        )

        return ToolExecutionResponse(
            success=result.success,
            cli="antigravity",
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
                "yolo": yolo,
                "timeout_configured": timeout_sec,
            },
        )
