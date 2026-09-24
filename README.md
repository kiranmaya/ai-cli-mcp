# AI CLI MCP Server

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Spec](https://img.shields.io/badge/MCP-2.2.0-green.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://github.com/kiranmaya/ai-cli-mcp/actions/workflows/publish.yml/badge.svg)](https://github.com/kiranmaya/ai-cli-mcp/actions)

A production-ready [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that acts as a secure, unified gateway to both **OpenAI Codex CLI** and **Google Antigravity CLI (`agy`)**.

It empowers primary AI orchestrators (such as **Claude Desktop**, **Gemini**, **Cursor**, or **Windsurf**) to delegate complex coding tasks, file refactorings, and deep automated code reviews to autonomous CLI agents running in **YOLO mode** with robust process lifecycle supervision.

---

## Architecture

```
                 ┌───────────────────────────────────┐
                 │          Any AI Agent             │
                 │ Claude / Gemini / Cursor / etc.   │
                 └─────────────────┬─────────────────┘
                                   │ MCP Protocol
                                   ▼
                ┌────────────────────────────────────┐
                │        Python MCP Server           │
                │        (ai_cli_mcp_server)         │
                ├────────────────────────────────────┤
                │ • codex_run     • codex_review     │
                │ • antigravity_run • antigravity_rvw│
                │ • cli_status    • get_agent_skills │
                └──────────────┬──────────────┬──────┘
                               │              │
                   ┌───────────┘              └───────────┐
                   ▼                                      ▼
     ┌───────────────────────────┐          ┌───────────────────────────┐
     │      OpenAI Codex CLI     │          │  Google Antigravity CLI   │
     │  (--dangerously-bypass)   │          │  (--dangerously-skip)     │
     └───────────────────────────┘          └───────────────────────────┘
```

---

## Key Features

- **Unified CLI Gateway**: Controls both OpenAI Codex and Google Antigravity agents through clean, standard MCP tools.
- **True Autonomous YOLO Mode**:
  - Automatically applies `--dangerously-bypass-approvals-and-sandbox` for Codex.
  - Automatically applies `--dangerously-skip-permissions` for Antigravity (`agy`).
  - Guarantees non-blocking, headless execution without hanging on confirmation dialogs.
- **Safer by Design**: Does **not** expose arbitrary shell execution (`cmd.exe`/`bash`). Only structured, sandboxed tasks are dispatched to vetted agent CLIs.
- **Process Supervision & Windows Tree-Killing**: When a task times out, child processes (compilers, servers, node) are terminated cleanly via process-tree signals.
- **Built-in Agent Skills**: Exposes an embedded, self-contained skills document via tool (`get_agent_skills`) and MCP resource (`skills://usage-guide`) so calling agents know how to orchestrate multi-agent workflows.
- **Multi-Client Support**: Out-of-the-box configuration for Claude Desktop, Cursor, Antigravity, Gemini, and VS Code.

---

## Available MCP Tools

| Tool | Parameters | Description |
| :--- | :--- | :--- |
| `codex_run` | `prompt`, `working_directory`, `model?`, `timeout?`, `yolo?` | Runs an autonomous coding task with OpenAI Codex CLI. |
| `antigravity_run` | `prompt`, `working_directory`, `model?`, `timeout?`, `yolo?` | Runs an autonomous coding task with Google Antigravity CLI. |
| `codex_review` | `working_directory`, `instructions?`, `model?`, `timeout?`, `uncommitted?` | Runs a non-interactive Git diff code review via Codex. |
| `antigravity_review` | `working_directory`, `instructions?`, `model?`, `timeout?` | Runs an automated codebase critique and review via Antigravity. |
| `cli_status` | *(none)* | Inspects local CLI binary health, versions, paths, and platform info. |
| `get_agent_skills` | *(none)* | Returns the comprehensive orchestration guide for calling agents. |

---

## Quickstart

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/kiranmaya/ai-cli-mcp.git
cd ai-cli-mcp

# Install dependencies or install in editable mode
pip install -e .
```

### 2. Verify Host Binaries

Run the server status check directly in Python:
```bash
python -c "import asyncio, server; print(asyncio.run(server.cli_status()))"
```

### 3. Add to Claude Desktop

Edit `%APPDATA%\Claude\claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "ai-cli-gateway": {
      "command": "python",
      "args": [
        "C:/Projects2026/AgentsCLI_MCP_Server/ai_cli_mcp_server.py"
      ],
      "env": {
        "CLI_YOLO_MODE": "true"
      }
    }
  }
}
```

### 4. Add to Cursor IDE

In Cursor, add to `.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "ai-cli-gateway": {
      "command": "python",
      "args": [
        "C:/Projects2026/AgentsCLI_MCP_Server/ai_cli_mcp_server.py"
      ]
    }
  }
}
```

*(For detailed setup in Antigravity IDE, Windsurf, and VS Code Cline, see [INSTALLATION_AND_CLIENTS.md](INSTALLATION_AND_CLIENTS.md).)*

---

## Multi-Agent Workflow Example

A calling agent (e.g. Claude) can execute an end-to-end task and peer review:

```python
# 1. Dispatch feature implementation to Codex
codex_run(
    prompt="Implement JWT refresh token rotation with SQLite in src/auth.py",
    working_directory="C:/MyProject"
)

# 2. Dispatch cross-verification review to Antigravity
antigravity_review(
    working_directory="C:/MyProject",
    instructions="Audit security edge cases for token invalidation in src/auth.py"
)
```

---

## Project Structure

```
ai-cli-mcp/
├── ai_cli_mcp_server.py     # Main CLI entrypoint
├── server.py                # MCP Server & Tool definitions
├── config.py                # Path discovery & sandbox validation
├── process.py               # Async process execution & tree killing
├── cli/
│   ├── codex.py             # OpenAI Codex CLI adapter
│   └── antigravity.py       # Google Antigravity CLI adapter
├── models/
│   └── requests.py          # Pydantic schemas & response models
├── skills/
│   └── document.md          # In-depth agent usage & skills documentation
├── pyproject.toml           # Packaging & build configuration
├── requirements.txt         # Core dependencies
├── INSTALLATION_AND_CLIENTS.md # Client configuration reference
└── README.md
```

---

## Environment Configuration

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `CLI_YOLO_MODE` | `true` | Runs commands with permission-bypass flags. |
| `CLI_DEFAULT_TIMEOUT` | `300` | Default timeout in seconds (5 min). |
| `CLI_MAX_TIMEOUT` | `1800` | Maximum timeout ceiling (30 min). |
| `ALLOWED_WORKING_DIRECTORIES` | `*` | Sandbox directory whitelist (comma-separated). |
| `CODEX_CLI_PATH` | Auto | Override path to `codex.exe`. |
| `AGY_CLI_PATH` | Auto | Override path to `agy.exe`. |

---

## License

MIT License. See [LICENSE](LICENSE) for details.
