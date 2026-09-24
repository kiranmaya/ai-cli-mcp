"""AI CLI MCP Server - Gateway to OpenAI Codex CLI and Google Antigravity CLI."""

import asyncio
import json
import logging
import platform
import sys
from pathlib import Path
from typing import Optional

# Support both MCP v2 (MCPServer) and MCP v1 (FastMCP)
try:
    from mcp.server.mcpserver import MCPServer
except ImportError:
    try:
        from mcp.server.fastmcp import FastMCP as MCPServer
    except ImportError:
        raise ImportError("Please install mcp SDK: pip install mcp")

from cli.antigravity import AntigravityAdapter
from cli.codex import CodexAdapter
from config import Config
from process import run_process

# Set up logging to stderr so stdio JSON-RPC transport remains clean
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger("ai_cli_mcp_server")

# Initialize MCP Server
app = MCPServer(
    name="ai-cli-gateway",
    version="1.0.0",
    description="Production MCP Gateway for OpenAI Codex and Google Antigravity CLIs",
)

SKILLS_DOC_PATH = Path(__file__).parent / "skills" / "document.md"


@app.tool()
async def codex_run(
    prompt: str,
    working_directory: str,
    model: Optional[str] = None,
    timeout: Optional[int] = 300,
    yolo: bool = True,
) -> str:
    """Executes a coding prompt non-interactively using the OpenAI Codex CLI.

    Args:
        prompt: Detailed instruction or task description for the Codex agent.
        working_directory: Target project root directory where the task executes.
        model: Optional model override (e.g. o3-mini, o1, gpt-4o).
        timeout: Execution timeout in seconds (default: 300, max: 1800).
        yolo: When true, runs in YOLO mode (--dangerously-bypass-approvals-and-sandbox)
              for automated non-blocking execution.

    Returns:
        JSON string containing success status, exit code, execution time, stdout, and stderr.
    """
    try:
        res = await CodexAdapter.run(
            prompt=prompt,
            working_directory=working_directory,
            model=model,
            timeout=timeout,
            yolo=yolo,
        )
        return json.dumps(res.model_dump(), indent=2)
    except Exception as e:
        logger.exception("Error during codex_run")
        return json.dumps(
            {
                "success": False,
                "cli": "codex",
                "action": "run",
                "exit_code": -1,
                "duration_seconds": 0.0,
                "timed_out": False,
                "cwd": working_directory,
                "output": "",
                "stderr": str(e),
                "summary": f"Failed to execute Codex: {str(e)}",
            },
            indent=2,
        )


@app.tool()
async def antigravity_run(
    prompt: str,
    working_directory: str,
    model: Optional[str] = None,
    timeout: Optional[int] = 300,
    yolo: bool = True,
) -> str:
    """Executes a coding prompt non-interactively using Google Antigravity CLI (agy).

    Args:
        prompt: Detailed instruction or task description for the Antigravity agent.
        working_directory: Target project root directory where the task executes.
        model: Optional model override (e.g. gemini-2.5-pro, gemini-2.5-flash).
        timeout: Execution timeout in seconds (default: 300, max: 1800).
        yolo: When true, runs in YOLO mode (--dangerously-skip-permissions)
              for automated non-blocking execution.

    Returns:
        JSON string containing success status, exit code, execution time, stdout, and stderr.
    """
    try:
        res = await AntigravityAdapter.run(
            prompt=prompt,
            working_directory=working_directory,
            model=model,
            timeout=timeout,
            yolo=yolo,
        )
        return json.dumps(res.model_dump(), indent=2)
    except Exception as e:
        logger.exception("Error during antigravity_run")
        return json.dumps(
            {
                "success": False,
                "cli": "antigravity",
                "action": "run",
                "exit_code": -1,
                "duration_seconds": 0.0,
                "timed_out": False,
                "cwd": working_directory,
                "output": "",
                "stderr": str(e),
                "summary": f"Failed to execute Antigravity: {str(e)}",
            },
            indent=2,
        )


@app.tool()
async def codex_review(
    working_directory: str,
    instructions: Optional[str] = None,
    model: Optional[str] = None,
    timeout: Optional[int] = 300,
    uncommitted: bool = True,
) -> str:
    """Performs an automated code review on a git repository using OpenAI Codex CLI.

    Args:
        working_directory: Root directory of the Git repository to review.
        instructions: Optional review focus areas or guidelines (e.g. security, memory leaks).
        model: Optional model override.
        timeout: Execution timeout in seconds (default: 300).
        uncommitted: When true, reviews uncommitted staged and unstaged changes.

    Returns:
        JSON string containing code review output, exit code, and execution summary.
    """
    try:
        res = await CodexAdapter.review(
            working_directory=working_directory,
            instructions=instructions,
            model=model,
            timeout=timeout,
            uncommitted=uncommitted,
        )
        return json.dumps(res.model_dump(), indent=2)
    except Exception as e:
        logger.exception("Error during codex_review")
        return json.dumps(
            {
                "success": False,
                "cli": "codex",
                "action": "review",
                "exit_code": -1,
                "duration_seconds": 0.0,
                "timed_out": False,
                "cwd": working_directory,
                "output": "",
                "stderr": str(e),
                "summary": f"Failed to execute Codex review: {str(e)}",
            },
            indent=2,
        )


@app.tool()
async def antigravity_review(
    working_directory: str,
    instructions: Optional[str] = None,
    model: Optional[str] = None,
    timeout: Optional[int] = 300,
) -> str:
    """Performs an automated code review on a workspace using Google Antigravity CLI.

    Args:
        working_directory: Root directory of the workspace or repository to review.
        instructions: Optional custom review criteria, guidelines, or focus areas.
        model: Optional model override.
        timeout: Execution timeout in seconds (default: 300).

    Returns:
        JSON string containing review critique, exit code, and execution summary.
    """
    try:
        res = await AntigravityAdapter.review(
            working_directory=working_directory,
            instructions=instructions,
            model=model,
            timeout=timeout,
            yolo=True,
        )
        return json.dumps(res.model_dump(), indent=2)
    except Exception as e:
        logger.exception("Error during antigravity_review")
        return json.dumps(
            {
                "success": False,
                "cli": "antigravity",
                "action": "review",
                "exit_code": -1,
                "duration_seconds": 0.0,
                "timed_out": False,
                "cwd": working_directory,
                "output": "",
                "stderr": str(e),
                "summary": f"Failed to execute Antigravity review: {str(e)}",
            },
            indent=2,
        )


@app.tool()
async def cli_status() -> str:
    """Checks the operational status of Codex CLI and Antigravity CLI binaries on the host."""
    codex_binary = Config.find_codex_path()
    antigravity_binary = Config.find_antigravity_path()

    codex_version = None
    if codex_binary:
        res = await run_process([str(codex_binary), "--version"], cwd=Path.cwd(), timeout_seconds=10)
        codex_version = res.stdout if res.success else "Installed (version check failed)"

    antigravity_version = None
    if antigravity_binary:
        res = await run_process([str(antigravity_binary), "--version"], cwd=Path.cwd(), timeout_seconds=10)
        antigravity_version = res.stdout if res.success else "Installed (version check failed)"

    allowed_dirs = [str(d) for d in Config.ALLOWED_DIRECTORIES] if Config.ALLOWED_DIRECTORIES else ["* (unrestricted)"]

    status_data = {
        "server_status": "healthy",
        "platform": platform.platform(),
        "python_version": sys.version.split()[0],
        "default_yolo_mode": Config.DEFAULT_YOLO_MODE,
        "default_timeout_seconds": Config.DEFAULT_TIMEOUT,
        "max_timeout_seconds": Config.MAX_TIMEOUT,
        "allowed_working_directories": allowed_dirs,
        "codex": {
            "installed": codex_binary is not None,
            "path": str(codex_binary) if codex_binary else None,
            "version": codex_version,
            "default_model": Config.CODEX_DEFAULT_MODEL or "CLI default",
        },
        "antigravity": {
            "installed": antigravity_binary is not None,
            "path": str(antigravity_binary) if antigravity_binary else None,
            "version": antigravity_version,
            "default_model": Config.ANTIGRAVITY_DEFAULT_MODEL or "CLI default",
        },
    }
    return json.dumps(status_data, indent=2)


@app.tool()
async def get_agent_skills() -> str:
    """Returns the comprehensive AI Agent Skills & Usage Guide for delegating tasks to Codex and Antigravity.

    Calling agents should read this guide to understand:
    - Tool invocation parameters and return formats
    - YOLO autonomous mode execution mechanics
    - Decision matrix for choosing Codex vs. Antigravity
    - Multi-agent collaboration pipelines and prompt patterns
    """
    if SKILLS_DOC_PATH.exists():
        return SKILLS_DOC_PATH.read_text(encoding="utf-8")
    return "Error: skills/document.md not found."


@app.resource("skills://usage-guide")
def read_skills_resource() -> str:
    """MCP Resource providing the Agent Skills & Orchestration Guide."""
    if SKILLS_DOC_PATH.exists():
        return SKILLS_DOC_PATH.read_text(encoding="utf-8")
    return "Agent skills documentation is missing."


@app.prompt("agent_orchestration_skills")
def prompt_agent_skills() -> str:
    """MCP Prompt that primes an LLM with instructions on using the AI CLI gateway."""
    return (
        "You are an AI Orchestrator with direct access to OpenAI Codex CLI and Google Antigravity CLI "
        "via the AI CLI MCP gateway. Follow the instructions in get_agent_skills() to delegate complex "
        "tasks, run non-interactive YOLO executions, and conduct automated dual-agent peer reviews."
    )


def main() -> None:
    """Runs the MCP server using standard IO transport."""
    logger.info("Starting AI CLI MCP Server on stdio transport...")
    app.run(transport="stdio")


if __name__ == "__main__":
    main()
