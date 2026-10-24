import ast
import unittest
from pathlib import Path

from apps.dfd.app import DFD_APP, build_application
from apps.dfd.infrastructure.persistence.project_repository import ProjectRepository

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "dfd"


def imports(path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    result = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            result.add(node.module)
    return result


class ArchitectureTests(unittest.TestCase):
    def test_domain_does_not_depend_on_vela_or_webview(self):
        offenders = []
        for path in (APP / "domain").rglob("*.py"):
            for imported in imports(path):
                if imported.split(".", 1)[0] in {"vela", "bottle", "webview", "pywebview"}:
                    offenders.append(f"{path.relative_to(ROOT)} -> {imported}")
        self.assertEqual(offenders, [])

    def test_application_does_not_import_vela(self):
        offenders = []
        for path in (APP / "application").rglob("*.py"):
            for imported in imports(path):
                if imported.split(".", 1)[0] in {"vela", "bottle", "webview", "pywebview"}:
                    offenders.append(f"{path.relative_to(ROOT)} -> {imported}")
        self.assertEqual(offenders, [])

    def test_composition_root_uses_explicit_app_definition(self):
        self.assertEqual(DFD_APP.module, "apps.dfd")
        self.assertEqual(DFD_APP.api_module, "apps.dfd.api")

    def test_application_can_be_built_without_vela(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            application = build_application(ProjectRepository(directory))
            self.assertEqual(application.diagrams.list_projects()[0]["name"], "modulo_01")


if __name__ == "__main__":
    unittest.main()
