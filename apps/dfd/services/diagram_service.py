"""Regras de negócio e exportação com motor vetorial preservado do editor Tkinter."""
import json
import sys
from pathlib import Path
import model
import exporter
from apps.dfd.repositories.project_repository import ProjectRepository

class DiagramService:
    def __init__(self, repository=None):
        self.repo = repository or ProjectRepository()

    @staticmethod
    def example():
        base = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parents[3]))
        p = base / 'assets' / 'modulo_01.dfd.json'
        return model.read(p)

    def list_projects(self):
        return self.repo.list()

    def load(self, name):
        return self.repo.load(name)

    def save(self, name, diagram):
        return {'path': self.repo.save(name, diagram)}

    def export(self, name, kind, diagram):
        model.validate(diagram)
        path = self.repo.export_path(name, kind)
        if kind == 'svg':
            content = exporter.svg(diagram)
        elif kind == 'html':
            content = exporter.html(diagram)
        else:
            content = json.dumps(diagram, ensure_ascii=False, indent=2)
        path.write_text(content, encoding='utf-8')
        return {'path': str(path), 'content': content, 'name': path.name, 'type': kind}
