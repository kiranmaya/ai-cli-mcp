"""Configuration and environment management for AI CLI MCP Server."""

import os
import shutil
from pathlib import Path
from typing import List, Optional


class Config:
    """Server configuration with environment variable overrides and path discovery."""

    # Default YOLO mode (autonomous non-interactive execution without permission prompts)
    DEFAULT_YOLO_MODE: bool = os.getenv("CLI_YOLO_MODE", "true").lower() in ("true", "1", "yes")

    # Timeouts in seconds
    DEFAULT_TIMEOUT: int = int(os.getenv("CLI_DEFAULT_TIMEOUT", "300"))
    MAX_TIMEOUT: int = int(os.getenv("CLI_MAX_TIMEOUT", "1800"))

    # Default models (None means use CLI default)
    CODEX_DEFAULT_MODEL: Optional[str] = os.getenv("CODEX_DEFAULT_MODEL", None)
    ANTIGRAVITY_DEFAULT_MODEL: Optional[str] = os.getenv("ANTIGRAVITY_DEFAULT_MODEL", None)

    # Allowed directories (comma/semicolon separated, or * for unrestricted)
    _raw_allowed = os.getenv("ALLOWED_WORKING_DIRECTORIES", "*")
    ALLOWED_DIRECTORIES: List[Path] = []
    if _raw_allowed and _raw_allowed.strip() != "*":
        for p in _raw_allowed.replace(";", ",").split(","):
            p_clean = p.strip()
            if p_clean:
                ALLOWED_DIRECTORIES.append(Path(p_clean).resolve())

    @classmethod
    def find_codex_path(cls) -> Optional[Path]:
        """Locates the Codex CLI binary."""
        # 1. Explicit environment variable
        env_path = os.getenv("CODEX_CLI_PATH")
        if env_path and Path(env_path).is_file():
            return Path(env_path).resolve()

        # 2. PATH resolution
        which_path = shutil.which("codex")
        if which_path:
            return Path(which_path).resolve()

        # 3. Known Windows locations
        local_app_data = os.getenv("LOCALAPPDATA", "")
        if local_app_data:
            known_paths = [
                Path(local_app_data) / "Programs" / "OpenAI" / "Codex" / "bin" / "codex.exe",
                Path(local_app_data) / "OpenAI" / "Codex" / "bin" / "codex.exe",
                Path(local_app_data) / "codex" / "bin" / "codex.exe",
            ]
            for kp in known_paths:
                if kp.is_file():
                    return kp.resolve()

        return None

    @classmethod
    def find_antigravity_path(cls) -> Optional[Path]:
        """Locates the Antigravity CLI (agy) binary."""
        # 1. Explicit environment variable
        env_path = os.getenv("AGY_CLI_PATH") or os.getenv("ANTIGRAVITY_CLI_PATH")
        if env_path and Path(env_path).is_file():
            return Path(env_path).resolve()

        # 2. PATH resolution
        which_path = shutil.which("agy") or shutil.which("antigravity")
        if which_path:
            return Path(which_path).resolve()

        # 3. Known Windows locations
        local_app_data = os.getenv("LOCALAPPDATA", "")
        if local_app_data:
            known_paths = [
                Path(local_app_data) / "agy" / "bin" / "agy.exe",
                Path(local_app_data) / "antigravity" / "bin" / "agy.exe",
                Path(local_app_data) / "Programs" / "agy" / "bin" / "agy.exe",
            ]
            for kp in known_paths:
                if kp.is_file():
                    return kp.resolve()

        return None

    @classmethod
    def validate_working_directory(cls, working_directory: str) -> Path:
        """Validates that a working directory exists and is permitted."""
        if not working_directory or not working_directory.strip():
            raise ValueError("Working directory must not be empty.")

        resolved = Path(working_directory).resolve()
        if not resolved.exists():
            raise FileNotFoundError(f"Working directory does not exist: {resolved}")
        if not resolved.is_dir():
            raise NotADirectoryError(f"Working directory path is not a directory: {resolved}")

        # Enforce sandbox if restricted directories are configured
        if cls.ALLOWED_DIRECTORIES:
            allowed = False
            for allowed_root in cls.ALLOWED_DIRECTORIES:
                try:
                    resolved.relative_to(allowed_root)
                    allowed = True
                    break
                except ValueError:
                    continue
            if not allowed:
                allowed_str = ", ".join(str(d) for d in cls.ALLOWED_DIRECTORIES)
                raise PermissionError(
                    f"Access denied: '{resolved}' is outside allowed directories: [{allowed_str}]"
                )

        return resolved

    @classmethod
    def clamp_timeout(cls, timeout: Optional[int]) -> int:
        """Clamps the requested timeout within [1, MAX_TIMEOUT]."""
        if timeout is None or timeout <= 0:
            return cls.DEFAULT_TIMEOUT
        return min(timeout, cls.MAX_TIMEOUT)
