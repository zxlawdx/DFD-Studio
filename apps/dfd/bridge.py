"""Thin optional WebView facade for DFD application services."""

from vela.core.bridge import BaseBridge

from apps.dfd.app import get_application


class DFDBridge(BaseBridge):
    def list_projects(self):
        return get_application().diagrams.list_projects()

    def load_project(self, name):
        return get_application().diagrams.load(name)

    def save_project(self, name, diagram):
        return get_application().diagrams.save(name, diagram)
