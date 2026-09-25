# AI CLI MCP Server - Installation & Client Configuration Guide

This guide explains how to install and connect the **AI CLI MCP Server** to any AI model or client interface, including **Claude Desktop**, **Cursor IDE**, **Google Antigravity**, **Gemini**, **Windsurf**, and **VS Code (Cline / Roo-Code)**.

---

## 1. Prerequisites

1. **Python 3.10+**: Verify with `python --version`.
2. **CLIs Installed on System**:
   - **Codex CLI**: `codex --version`
   - **Antigravity CLI**: `agy --version`

---

## 2. Quick Installation

### Method A: Install via pip (Editable / Local)
```powershell
# From the repository root
pip install -e .
```
This registers the global command `ai-cli-mcp` or `python -m ai_cli_mcp_server`.

### Method B: Install directly from GitHub
```powershell
pip install git+https://github.com/kiranmaya/ai-cli-mcp.git
```

### Method C: Run via UV / UVX (Zero-Install)
```bash
uvx --from git+https://github.com/kiranmaya/ai-cli-mcp.git ai-cli-mcp
```

### Method D: Run via Windows Scripts (Batch / PowerShell)
No package installation needed. The scripts automatically detect any virtual environment (`.venv`, `venv`, `env`) or system Python 3.10+:
```cmd
:: Batch runner
run_server.bat

:: PowerShell runner
.\run_server.ps1
```

---

## 3. Client Configuration Configurations

### A. Claude (Claude Desktop & Claude Code CLI)

#### 1. Claude Desktop
Open or create your Claude Desktop configuration file:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

Add the server definition:
```json
{
  "mcpServers": {
    "ai-cli-gateway": {
      "command": "python",
      "args": [
        "c:/Projects2026/AgentsCLI_MCP_Server/ai_cli_mcp_server.py"
      ],
      "env": {
        "CLI_YOLO_MODE": "true",
        "CLI_DEFAULT_TIMEOUT": "300"
      }
    }
  }
}
```

#### 2. Claude Code CLI
Add to your user settings (`~/.claude.json`):
```json
{
  "mcpServers": {
    "ai-cli-gateway": {
      "command": "python",
      "args": [
        "c:/Projects2026/AgentsCLI_MCP_Server/ai_cli_mcp_server.py"
      ],
      "env": {
        "CLI_YOLO_MODE": "true",
        "CLI_DEFAULT_TIMEOUT": "300"
      }
    }
  }
}
```

---

### B. OpenAI Codex CLI & Desktop

#### 1. One-Line Command via CLI
```powershell
codex mcp add ai-cli-gateway --env CLI_YOLO_MODE=true --env CLI_DEFAULT_TIMEOUT=300 -- python c:/Projects2026/AgentsCLI_MCP_Server/ai_cli_mcp_server.py
```

#### 2. Direct Configuration in `~/.codex/config.toml`
Add to `~/.codex/config.toml`:
```toml
[mcp_servers.ai-cli-gateway]
command = "python"
args = ["c:/Projects2026/AgentsCLI_MCP_Server/ai_cli_mcp_server.py"]

[mcp_servers.ai-cli-gateway.env]
CLI_YOLO_MODE = "true"
CLI_DEFAULT_TIMEOUT = "300"
```

Verify with:
```powershell
codex mcp get ai-cli-gateway
```

---

### C. Gemini CLI & Google Antigravity

#### 1. Gemini CLI
Add using the Gemini CLI command:
```powershell
gemini mcp add ai-cli-gateway python c:/Projects2026/AgentsCLI_MCP_Server/ai_cli_mcp_server.py
```
Or add to global `~/.gemini/settings.json`:
```json
{
  "mcpServers": {
    "ai-cli-gateway": {
      "command": "python",
      "args": [
        "c:/Projects2026/AgentsCLI_MCP_Server/ai_cli_mcp_server.py"
      ],
      "env": {
        "CLI_YOLO_MODE": "true",
        "CLI_DEFAULT_TIMEOUT": "300"
      }
    }
  }
}
```

#### 2. Google Antigravity CLI (`agy`) & Antigravity IDE
Add using `agy mcp add`:
```powershell
agy mcp add --env CLI_YOLO_MODE=true --env CLI_DEFAULT_TIMEOUT=300 ai-cli-gateway python c:/Projects2026/AgentsCLI_MCP_Server/ai_cli_mcp_server.py
```
Or configure in `~/.gemini/config/mcp_config.json`:
```json
{
  "mcpServers": {
    "ai-cli-gateway": {
      "command": "python",
      "args": [
        "c:/Projects2026/AgentsCLI_MCP_Server/ai_cli_mcp_server.py"
      ],
      "env": {
        "CLI_YOLO_MODE": "true",
        "CLI_DEFAULT_TIMEOUT": "300"
      }
    }
  }
}
```

---

### D. Cursor IDE
In Cursor, open **Settings > Features > MCP** (or edit `.cursor/mcp.json` in your workspace):
```json
{
  "mcpServers": {
    "ai-cli-gateway": {
      "command": "python",
      "args": [
        "c:/Projects2026/AgentsCLI_MCP_Server/ai_cli_mcp_server.py"
      ],
      "env": {
        "CLI_YOLO_MODE": "true"
      }
    }
  }
}
```

---

### E. Windsurf IDE (Codeium)
Edit `~/.codeium/windsurf/mcp_config.json`:
```json
{
  "mcpServers": {
    "ai-cli-gateway": {
      "command": "python",
      "args": [
        "c:/Projects2026/AgentsCLI_MCP_Server/ai_cli_mcp_server.py"
      ],
      "env": {
        "CLI_YOLO_MODE": "true"
      }
    }
  }
}
```

---

### F. VS Code (Cline / Roo-Code Extension)
Open Cline / Roo-Code MCP Settings (`cline_mcp_settings.json`):
```json
{
  "mcpServers": {
    "ai-cli-gateway": {
      "command": "python",
      "args": [
        "c:/Projects2026/AgentsCLI_MCP_Server/ai_cli_mcp_server.py"
      ],
      "env": {
        "CLI_YOLO_MODE": "true"
      },
      "disabled": false,
      "autoApprove": [
        "cli_status",
        "get_agent_skills"
      ]
    }
  }
}
```

---

## 4. Environment Variables Reference

| Variable | Description | Default |
| :--- | :--- | :--- |
| `CLI_YOLO_MODE` | Enable autonomous non-interactive execution (`true`/`false`) | `true` |
| `CLI_DEFAULT_TIMEOUT` | Default process timeout in seconds | `300` |
| `CLI_MAX_TIMEOUT` | Maximum allowable timeout in seconds | `1800` |
| `ALLOWED_WORKING_DIRECTORIES` | Comma-separated list of permitted workspace roots (`*` for unrestricted) | `*` |
| `CODEX_CLI_PATH` | Explicit path to `codex.exe` / `codex` | Auto-detected |
| `AGY_CLI_PATH` | Explicit path to `agy.exe` / `agy` | Auto-detected |
| `CODEX_DEFAULT_MODEL` | Default model for Codex runs (e.g. `o3-mini`, `o1`) | CLI default |
| `ANTIGRAVITY_DEFAULT_MODEL` | Default model for Antigravity runs (e.g. `gemini-2.5-pro`) | CLI default |

---

## 5. Health Check & Verification

Once configured in your client, ask your AI model:
> "Run `cli_status` tool to verify the AI CLI MCP gateway connection."

Expected response:
```json
{
  "server_status": "healthy",
  "platform": "Windows-10...",
  "python_version": "3.12.x",
  "default_yolo_mode": true,
  "codex": { "installed": true, "version": "codex-cli 0.155.0" },
  "antigravity": { "installed": true, "version": "1.2.5" }
}
```
