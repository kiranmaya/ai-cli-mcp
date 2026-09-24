"""Unit and integration tests for AI CLI MCP Server."""

import asyncio
import json
from pathlib import Path
import unittest

from config import Config
from models.requests import (
    AntigravityReviewRequest,
    AntigravityRunRequest,
    CodexReviewRequest,
    CodexRunRequest,
    ToolExecutionResponse,
)
from process import strip_ansi, run_process
import server


class TestAICLIMCPServer(unittest.TestCase):
    """Test suite for server components and adapters."""

    def test_strip_ansi(self):
        colored = "\x1b[31mError:\x1b[0m Failed to parse"
        self.assertEqual(strip_ansi(colored), "Error: Failed to parse")

    def test_config_paths(self):
        codex_path = Config.find_codex_path()
        agy_path = Config.find_antigravity_path()
        self.assertIsNotNone(codex_path, "Codex CLI should be discovered on system")
        self.assertIsNotNone(agy_path, "Antigravity CLI should be discovered on system")
        self.assertTrue(codex_path.exists())
        self.assertTrue(agy_path.exists())

    def test_directory_validation(self):
        cwd = Path.cwd()
        validated = Config.validate_working_directory(str(cwd))
        self.assertEqual(validated, cwd.resolve())

        with self.assertRaises(ValueError):
            Config.validate_working_directory("")

        with self.assertRaises(FileNotFoundError):
            Config.validate_working_directory("C:/NonExistentPathXYZ123456789")

    def test_timeout_clamping(self):
        self.assertEqual(Config.clamp_timeout(None), Config.DEFAULT_TIMEOUT)
        self.assertEqual(Config.clamp_timeout(0), Config.DEFAULT_TIMEOUT)
        self.assertEqual(Config.clamp_timeout(60), 60)
        self.assertEqual(Config.clamp_timeout(99999), Config.MAX_TIMEOUT)

    def test_models_validation(self):
        req = CodexRunRequest(
            prompt="Write a hello world",
            working_directory=str(Path.cwd()),
            model="o3-mini",
            timeout=120,
            yolo=True,
        )
        self.assertEqual(req.model, "o3-mini")
        self.assertTrue(req.yolo)

    def test_cli_status_tool(self):
        status_json = asyncio.run(server.cli_status())
        data = json.loads(status_json)
        self.assertEqual(data["server_status"], "healthy")
        self.assertTrue(data["codex"]["installed"])
        self.assertTrue(data["antigravity"]["installed"])

    def test_get_agent_skills_tool(self):
        skills_text = asyncio.run(server.get_agent_skills())
        self.assertIn("AI Agent Orchestration & CLI Gateway Skills Guide", skills_text)
        self.assertIn("codex_run", skills_text)
        self.assertIn("antigravity_run", skills_text)
        self.assertIn("YOLO", skills_text)


if __name__ == "__main__":
    unittest.main()
