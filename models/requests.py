"""Request and response models for MCP tools."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CodexRunRequest(BaseModel):
    """Parameters for running Codex CLI."""

    prompt: str = Field(..., description="The task instruction or prompt for Codex agent.")
    working_directory: str = Field(
        ..., description="The target workspace directory for task execution."
    )
    model: Optional[str] = Field(
        default=None, description="Model to override (e.g. o3-mini, o1, gpt-4o)."
    )
    timeout: Optional[int] = Field(
        default=300, description="Execution timeout in seconds (default: 300, max: 1800)."
    )
    yolo: bool = Field(
        default=True,
        description="Enable YOLO mode (--dangerously-bypass-approvals-and-sandbox) for autonomous execution without interactive confirmation prompts.",
    )


class AntigravityRunRequest(BaseModel):
    """Parameters for running Antigravity CLI."""

    prompt: str = Field(..., description="The task instruction or prompt for Antigravity agent.")
    working_directory: str = Field(
        ..., description="The target workspace directory for task execution."
    )
    model: Optional[str] = Field(
        default=None, description="Model override for Antigravity CLI session."
    )
    timeout: Optional[int] = Field(
        default=300, description="Execution timeout in seconds (default: 300, max: 1800)."
    )
    yolo: bool = Field(
        default=True,
        description="Enable YOLO mode (--dangerously-skip-permissions) for auto-approving tool permissions.",
    )


class CodexReviewRequest(BaseModel):
    """Parameters for running Codex code review."""

    working_directory: str = Field(
        ..., description="Directory containing the repository or files to review."
    )
    instructions: Optional[str] = Field(
        default=None, description="Custom review criteria, guidelines, or focus areas."
    )
    model: Optional[str] = Field(
        default=None, description="Model to use for code review."
    )
    timeout: Optional[int] = Field(
        default=300, description="Execution timeout in seconds (default: 300)."
    )
    uncommitted: bool = Field(
        default=True, description="Review staged, unstaged, and untracked changes."
    )


class AntigravityReviewRequest(BaseModel):
    """Parameters for running Antigravity code review."""

    working_directory: str = Field(
        ..., description="Directory containing the repository or files to review."
    )
    instructions: Optional[str] = Field(
        default=None, description="Custom review criteria, guidelines, or focus areas."
    )
    model: Optional[str] = Field(
        default=None, description="Model to use for code review."
    )
    timeout: Optional[int] = Field(
        default=300, description="Execution timeout in seconds (default: 300)."
    )


class ToolExecutionResponse(BaseModel):
    """Structured response returned by MCP tools."""

    success: bool = Field(..., description="Whether the CLI command succeeded.")
    cli: str = Field(..., description="Name of the CLI invoked (codex or antigravity).")
    action: str = Field(..., description="Action performed (run or review).")
    exit_code: int = Field(..., description="Process exit code.")
    duration_seconds: float = Field(..., description="Duration in seconds.")
    timed_out: bool = Field(..., description="Whether execution timed out.")
    cwd: str = Field(..., description="Working directory.")
    output: str = Field(..., description="Combined stdout output.")
    stderr: Optional[str] = Field(default="", description="Stderr output if any.")
    summary: str = Field(..., description="Human-readable execution summary.")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Extra metadata.")
