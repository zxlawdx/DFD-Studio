from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol


class DiagramRepository(Protocol):
    """Persistence port consumed by the application service."""

    @staticmethod
    def safe_name(name: str) -> str: ...

    def list(self) -> list[dict[str, Any]]: ...

    def save(self, name: str, diagram: dict[str, Any]) -> str: ...

    def load(self, name: str) -> dict[str, Any]: ...

    def export_path(self, name: str, kind: str) -> Path: ...
