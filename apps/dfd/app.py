from __future__ import annotations

from dataclasses import dataclass
from threading import RLock

from apps.dfd.application.diagram_service import DiagramService
from apps.dfd.infrastructure.persistence.project_repository import ProjectRepository


@dataclass(frozen=True, slots=True)
class AppDefinition:
    name: str = "dfd"
    module: str = "apps.dfd"
    api_module: str = "apps.dfd.api"
    routes_module: str = "apps.dfd.urls"
    static_dirs: tuple[str, ...] = ("apps/dfd/static",)


@dataclass(slots=True)
class DFDApplication:
    diagrams: DiagramService


DFD_APP = AppDefinition()
_application: DFDApplication | None = None
_lock = RLock()


def build_application(repository=None) -> DFDApplication:
    return DFDApplication(DiagramService(repository or ProjectRepository()))


def get_application() -> DFDApplication:
    global _application
    with _lock:
        if _application is None:
            _application = build_application()
        return _application


def register_presentation() -> None:
    """Current Vela requires decorator modules to be imported before startup."""
    from apps.dfd import api as _api  # noqa: F401
