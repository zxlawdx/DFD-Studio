"""Windows: usar Qt5/QtWebEngine e verificar o build sem abrir GUI."""
import os
import sys
from pathlib import Path

os.environ["QT_API"] = "pyqt5"
os.environ["PYWEBVIEW_GUI"] = "qt"
from PyQt5.QtWidgets import QApplication  # noqa: F401
from PyQt5.QtWebEngineWidgets import QWebEngineView  # noqa: F401
import webview
import webview.platforms.qt as qt_backend

webview.settings["OPEN_DEVTOOLS_IN_DEBUG"] = False
_original_start = webview.start


def start_with_qt(*args, **kwargs):
    kwargs["gui"] = "qt"
    kwargs["debug"] = False
    return _original_start(*args, **kwargs)


webview.start = start_with_qt
BASE_DIR = (Path(sys.executable).resolve().parent if getattr(sys, "frozen", False)
            else Path(__file__).resolve().parent)
os.chdir(BASE_DIR)
sys.path.insert(0, str(BASE_DIR))


def self_test():
    assert qt_backend.is_webengine, "QtWebEngine nao carregado"
    assert not qt_backend._qt6, "Esperado Qt5, mas backend diferente foi carregado"
    for rel in (
        "apps/dfd/templates/dfd/index.html",
        "staticfiles/dfd/js/app.js",
        "staticfiles/dfd/css/app.css",
        "assets/modulo_01.dfd.json",
        "VERSION",
    ):
        if not (BASE_DIR / rel).is_file():
            raise RuntimeError(f"Arquivo obrigatorio ausente: {rel}")
    from config.wsgi import run  # noqa: F401
    print("DFD Studio Windows Qt5 / QtWebEngine OK")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
    else:
        from config.wsgi import run
        run()
