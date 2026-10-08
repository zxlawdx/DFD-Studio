"""Testes portáveis: não precisam abrir GUI nem instalar Vela."""
import os
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from apps.dfd.repositories.project_repository import ProjectRepository
from apps.dfd.services.diagram_service import DiagramService
import model

class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = ProjectRepository(self.tmp.name)
        self.service = DiagramService(self.repo)
        self.d = self.service.example()

    def tearDown(self):
        self.tmp.cleanup()

    def test_schema_original_com_revisoes(self):
        model.validate(self.d)
        codes = {n['id']: n['code'] for n in self.d['nodes']}
        pairs = {(codes[e['source']],codes[e['target']]) for e in self.d['edges']}
        for pair in [('1.8','1.11'),('1.13','1.04'),('1.15','1.16'),('1.16','1.8')]:
            self.assertIn(pair, pairs)
        self.assertEqual(sum(n['code']=='1.04' for n in self.d['nodes']), 1)

    def test_default_project_is_listed_and_loadable(self):
        projects = self.service.list_projects()
        self.assertEqual(projects[0]['name'], 'modulo_01')
        self.assertTrue(projects[0]['bundled'])
        self.assertEqual(self.service.load('modulo_01'), self.d)

    def test_save_load_original(self):
        p=self.service.save('módulo 01',self.d)
        self.assertTrue(Path(p['path']).is_file())
        self.assertEqual(self.service.load('módulo 01'),self.d)
        names = {item['name'] for item in self.service.list_projects()}
        self.assertEqual(names, {'modulo_01', 'módulo_01'})

    def test_saved_default_overrides_bundled_default(self):
        changed = json.loads(json.dumps(self.d))
        changed['title'] = 'Versão salva pelo usuário'
        self.service.save('modulo_01', changed)
        projects = self.service.list_projects()
        self.assertEqual(sum(item['name'] == 'modulo_01' for item in projects), 1)
        self.assertEqual(self.service.load('modulo_01')['title'], 'Versão salva pelo usuário')

    def test_export_svg_html_json(self):
        for kind in ('svg','html','json'):
            result=self.service.export('trabalho',kind,self.d)
            self.assertTrue(Path(result['path']).is_file())
            self.assertEqual(Path(result['path']).read_text(encoding='utf-8'),result['content'])
            if kind=='svg': ET.fromstring(result['content'])
            if kind=='html': self.assertIn('Detalhamento e observações',result['content'])
            if kind=='json': self.assertEqual(json.loads(result['content']),self.d)

    def test_no_path_traversal(self):
        p=self.repo.save('../../outro',self.d)
        self.assertTrue(Path(p).resolve().is_relative_to(self.repo.projects.resolve()))
        with self.assertRaises(ValueError): self.repo.export_path('ok','exe')

if __name__=='__main__': unittest.main()
