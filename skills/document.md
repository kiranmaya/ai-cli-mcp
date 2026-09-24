# AI Agent Orchestration & CLI Gateway Skills Guide

This document defines the agent usage skills, interaction patterns, and operational protocols for any AI agent (Claude, Gemini, Cursor, Windsurf, Roo, etc.) acting as a primary orchestrator over the **AI CLI MCP Server**.

---

## 1. Architecture & Gateway Role

```
   ┌─────────────────────────────────────────────────────────────┐
   │                  Primary AI Agent (Orchestrator)            │
   │               (Claude, Gemini, Cursor, ChatGPT)             │
   └──────────────────────────────┬──────────────────────────────┘
                                  │ MCP Protocol (JSON-RPC)
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │                    AI CLI MCP Server                        │
   │  • Process Supervision       • Tree-Kill on Timeout         │
   │  • Sandbox Path Enforcement  • ANSI / Stream Formatting     │
   ├──────────────────────────────┬──────────────────────────────┤
   │ Tools:                       │ Resources & Prompts:         │
   │  - codex_run                 │  - skills://usage-guide      │
   │  - antigravity_run           │  - agent_orchestration_skills│
   │  - codex_review              │                              │
   │  - antigravity_review        │                              │
   │  - cli_status                │                              │
   │  - get_agent_skills          │                              │
   └───────────────┬──────────────────────────────┬──────────────┘
                   │ Spawns Process               │ Spawns Process
                   ▼                              ▼
      ┌──────────────────────────┐   ┌──────────────────────────┐
      │     OpenAI Codex CLI     │   │  Google Antigravity CLI  │
      │  (--dangerously-bypass)  │   │  (--dangerously-skip)    │
      └──────────────────────────┘   └──────────────────────────┘
```

The MCP Server operates as a **controlled, sandboxed gateway**. Rather than exposing dangerous arbitrary shell execution (`cmd.exe`, `powershell`), it gives the primary agent high-level, dedicated tool access to two state-of-the-art autonomous coding agents: **Codex CLI** and **Antigravity CLI (`agy`)**.

---

## 2. Tools Reference

### `codex_run`
Executes an end-to-end coding task or prompt non-interactively using the OpenAI Codex CLI.
- **`prompt`** *(string, required)*: The detailed coding prompt or instruction.
- **`working_directory`** *(string, required)*: Absolute path to the project directory where the task executes.
- **`model`** *(string, optional)*: Specific model to invoke (e.g., `o3-mini`, `o1`, `gpt-4o`). If omitted, uses CLI default or `CODEX_DEFAULT_MODEL`.
- **`timeout`** *(integer, optional, default: 300)*: Timeout in seconds (clamped to max configured, default max 1800s).
- **`yolo`** *(boolean, optional, default: true)*: Run in YOLO mode with `--dangerously-bypass-approvals-and-sandbox` for autonomous completion without terminal prompt blocking.

### `antigravity_run`
Executes a task non-interactively using Google Antigravity CLI (`agy`).
- **`prompt`** *(string, required)*: The prompt or instruction for the Antigravity agent.
- **`working_directory`** *(string, required)*: Absolute path to the project directory.
- **`model`** *(string, optional)*: Specific model override (e.g. `gemini-2.5-pro`, `gemini-2.5-flash`).
- **`timeout`** *(integer, optional, default: 300)*: Timeout in seconds.
- **`yolo`** *(boolean, optional, default: true)*: Run in YOLO mode with `--dangerously-skip-permissions` to auto-approve tool execution.

### `codex_review`
Runs a non-interactive code review against the local repository using Codex.
- **`working_directory`** *(string, required)*: Target repository root (must be a Git repo).
- **`instructions`** *(string, optional)*: Specific focus areas (e.g. security audits, concurrency bugs, API backwards compatibility).
- **`model`** *(string, optional)*: Model to perform the review.
- **`timeout`** *(integer, optional, default: 300)*: Timeout in seconds.
- **`uncommitted`** *(boolean, optional, default: true)*: Focus review on staged, unstaged, and untracked changes.

### `antigravity_review`
Runs an automated review and critique using Antigravity CLI across the target workspace.
- **`working_directory`** *(string, required)*: Target repository root.
- **`instructions`** *(string, optional)*: Custom review guidelines and focus points.
- **`model`** *(string, optional)*: Model override.
- **`timeout`** *(integer, optional, default: 300)*: Timeout in seconds.

### `cli_status`
Reports local health, detection of CLI binaries (`agy.exe`, `codex.exe`), versions, OS details, and directory restrictions. Always run this first if you need to inspect available engines.

### `get_agent_skills`
Returns the content of this skill document, allowing the calling LLM to self-instruct and dynamically adapt its orchestration strategy.

---

## 3. YOLO Mode Deep-Dive

When calling sub-agent CLIs in automated pipelines, interactive prompts (e.g. *"Allow model to execute `npm test`? [y/N]"*) will cause headless MCP server processes to hang indefinitely until a timeout kills them.

To enable true agentic delegation, **YOLO mode is enabled by default (`yolo=true`)**:
* **Codex CLI**: Passes `--dangerously-bypass-approvals-and-sandbox`. The agent executes shell commands, file modifications, and git actions without manual approval.
* **Antigravity CLI**: Passes `--dangerously-skip-permissions`. Auto-approves all tool invocations and system actions.

### Safety Guardrails
1. **Directory Whitelisting**: If `ALLOWED_WORKING_DIRECTORIES` is set in the MCP server environment, any path outside those roots is rejected with a `PermissionError`.
2. **Process Tree Supervision**: On timeout or termination, the MCP server invokes Windows process tree termination (`taskkill /F /T /PID`) to prevent orphaned compiler or server processes.
3. **No Raw Shell Tool**: The primary agent cannot execute arbitrary shell commands through this server; only vetted Codex and Antigravity agents can run tasks.

---

## 4. Engine Selection Matrix

| Scenario / Task Type | Recommended Tool | Rationale |
| :--- | :--- | :--- |
| **Complex Algorithms & Rust / C++ / Python Systems** | `codex_run` | OpenAI reasoning models (o3-mini, o1) excel at tight algorithmic logic, formal validation, and math. |
| **Full Stack & Modern Web (Next.js, Vite, FastHTML)** | `antigravity_run` | Antigravity has specialized multi-file project scaffolding, rich CSS/design sensibilities, and tool integration. |
| **Deep Git Diff Review** | `codex_review` | Native `codex review --uncommitted` reads git diffs directly with high precision. |
| **Architectural / Holistic Code Review** | `antigravity_review` | Inspects workspace structure, documentation integrity, and cross-cutting concerns. |
| **Dual-Verification (Double Check)** | `codex_run` + `antigravity_review` | Implement with Codex, then verify with Antigravity (or vice-versa) for critical code paths. |

---

## 5. Multi-Agent Orchestration Patterns

### Pattern A: Implement and Peer-Review
```
   [User Request]
          │
          ▼
   1. Primary Agent calls codex_run(prompt="Implement feature X in src/", working_directory=dir)
          │
          ▼
   2. Codex implements changes and runs tests locally
          │
          ▼
   3. Primary Agent calls antigravity_review(working_directory=dir, instructions="Verify edge cases for feature X")
          │
          ▼
   4. If issues found -> Primary Agent dispatches codex_run to fix them
          │
          ▼
   5. Primary Agent presents verified results to User
```

### Pattern B: Architectural Plan -> Parallel Execution
```
   1. Primary Agent formulates exact specifications and modular file boundaries.
   2. Sub-task 1 (Backend API) -> delegated to codex_run in working_directory.
   3. Sub-task 2 (Frontend Client) -> delegated to antigravity_run in working_directory.
   4. Validation -> Primary Agent reviews or runs tests.
```

---

## 6. Prompt Engineering for Sub-Agents

When constructing the `prompt` string for `codex_run` or `antigravity_run`:
1. **Specify Exact Files**: Give absolute or relative file paths rather than vague descriptions (e.g. `Update src/auth/jwt.py to add refresh token rotation`).
2. **Include Verification Instructions**: Explicitly tell the CLI agent to run local tests or type checks before finishing (e.g. `After making changes, run pytest tests/test_auth.py and verify that all pass with zero errors`).
3. **Set Constraints**: Tell the sub-agent what NOT to modify (e.g. `Do not modify database schema migrations`).
4. **Demand Clean Code**: State that all modifications must compile with zero warnings or errors.

---

## 7. Error Handling & Recovery Protocol

- **Exit Code Non-Zero**: Inspect `stderr` and `output` in `ToolExecutionResponse`. Many CLI errors (like missing dependencies or syntax errors) are clearly articulated in `output`.
- **Timed Out (`timed_out: true`)**: The task was too large for the configured timeout. Break the task into smaller sub-tasks or increase `timeout` (e.g. 600 or 900 seconds).
- **Git Repo Missing**: `codex_review` requires a `.git` folder. Ensure `git init` has been run on the workspace before requesting review.
