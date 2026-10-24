"""DFD Studio composition root: application first, Vela runtime second."""

from vela.core.app import VelaApp

from apps.dfd.app import DFD_APP, register_presentation
from apps.dfd.bridge import DFDBridge


def create_app() -> VelaApp:
    # Compatibility with the current Vela release: decorators are registered by import.
    register_presentation()
    app = VelaApp(settings_module="config.settings", bridge_class=DFDBridge)
    app.register_app(DFD_APP.module)
    return app


def run():
    create_app().run()
