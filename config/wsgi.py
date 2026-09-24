"""Uma só instância VelaApp; APIs registradas por import explícito."""
from vela.core.app import VelaApp
import apps.dfd.api  # noqa: F401  -- registra @api.* no Bottle do Vela

INSTALLED_APPS = ['apps.dfd']

def run():
    app = VelaApp(settings_module='config.settings')
    for app_name in INSTALLED_APPS:
        app.register_app(app_name)
    app.run()
