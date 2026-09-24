"""Execute: python3 -m unittest discover -s ."""
import copy
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
import model
import exporter
import example

class ModelTests(unittest.TestCase):
    def test_roundtrip_keeps_routes_and_details(self):
        d=example.build()
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'a.dfd.json';model.write(path,d)
            self.assertEqual(model.read(path),d)

    def test_required_connections_and_discount(self):
        d=example.build();pairs={(e['source'],e['target']) for e in d['edges']}
        for pair in [('p8','p11'),('p13','p4'),('p15','p16'),('p16','p8')]:self.assertIn(pair,pairs)
        self.assertEqual(sum(n['code']=='1.04' for n in d['nodes']),1)

    def test_moving_nodes_updates_endpoints(self):
        d=example.build();e=next(e for e in d['edges'] if e['source']=='p8' and e['target']=='p11')
        before=model.path_points(d,e);n=next(n for n in d['nodes'] if n['id']=='p8');n['x']+=45
        after=model.path_points(d,e)
        self.assertEqual(after[0][0],before[0][0]+45)
        self.assertEqual(after[-1],before[-1])
        self.assertEqual(e['bends'][0],list(before[1]))

    def test_svg_and_html_escape_user_content(self):
        d=model.blank();d['title']='<script>alert(1)</script>'
        d['nodes'].append(model.node('process','1','A & <B>',0,0,details='<img src=x onerror=alert(1)>'))
        svg=exporter.svg(d);ET.fromstring(svg)
        page=exporter.html(d)
        self.assertNotIn('<img src=x',page)
        self.assertNotIn('<script>alert(1)',page)
        self.assertIn('A &amp; &lt;B&gt;',svg)

    def test_reject_missing_connection_target(self):
        d=example.build();d['edges'][0]['target']='absent'
        with self.assertRaises(ValueError):model.validate(d)

    def test_empty_project_exports(self):
        ET.fromstring(exporter.svg(model.blank()))
        self.assertIn('Detalhamento',exporter.html(model.blank()))

    def test_centered_horizontal_label(self):
        d=model.blank();a=model.node('entity','','A',0,0,id='a');b=model.node('process','1','B',400,0,id='b')
        d['nodes']=[a,b];e=model.edge('a','b')
        self.assertEqual(model.label_pos(model.path_points(d,e),e),(295,38))

if __name__=='__main__':unittest.main()
