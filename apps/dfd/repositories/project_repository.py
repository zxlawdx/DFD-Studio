"""Persistência local: nunca gravar em diretório congelado do PyInstaller.
O conteúdo continua acessível mesmo após trocar de versão do executável.
"""
import json
import os
import re
from pathlib import Path
import model

class ProjectRepository:
    def __init__(self, home=None):
        self.home = Path(home or os.getenv('DFD_STUDIO_DATA_DIR') or (Path.home() / 'Documents' / 'DFD Studio'))
        self.projects = self.home / 'projetos'
        self.exports = self.home / 'exportacoes'
        self.projects.mkdir(parents=True, exist_ok=True)
        self.exports.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def safe_name(name):
        value = re.sub(r'[^\w-]+', '_', str(name or 'diagrama').strip(), flags=re.UNICODE).strip('_')[:70]
        if value in ('', '.', '..'):
            raise ValueError('Nome de arquivo inválido.')
        return value

    def list(self):
        return sorted(({'name': p.name[:-len('.dfd.json')], 'modified': p.stat().st_mtime} for p in self.projects.glob('*.dfd.json')),
                      key=lambda i: i['modified'], reverse=True)

    def save(self, name, diagram):
        model.validate(diagram)
        name = self.safe_name(name)
        path = self.projects / (name + '.dfd.json')
        model.write(path, diagram)  # write atômico do modelo anterior
        return str(path)

    def load(self, name):
        name = self.safe_name(name)
        path = self.projects / (name + '.dfd.json')
        if not path.is_file():
            raise ValueError('Projeto não encontrado.')
        return model.read(path)

    def export_path(self, name, kind):
        if kind not in ('svg', 'html', 'json'):
            raise ValueError('Formato não suportado.')
        suffix = '.dfd.json' if kind == 'json' else '.' + kind
        return self.exports / (self.safe_name(name) + suffix)
