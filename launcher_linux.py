"""Linux: usar PyQt6 e QtWebEngine como backend grafico do Vela."""
import os
import sys
from pathlib import Path
from linux_graphics import configure_linux_graphics

RENDER_MODE = configure_linux_graphics()

# Definir ANTES da importacao de qtpy e pywebview.
os.environ["QT_API"] = "pyqt6"
os.environ["PYWEBVIEW_GUI"] = "qt"
from PyQt6.QtWidgets import QApplication  # noqa: F401
from PyQt6.QtWebEngineWidgets import QWebEngineView  # noqa: F401
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
    """Teste de importacao e dos arquivos de runtime, sem abrir a GUI."""
    assert qt_backend.is_webengine, "QtWebEngine nao carregado"
    assert qt_backend._qt6, "Esperado PyQt6, mas backend diferente foi carregado"
    for rel in (
        "apps/dfd/templates/dfd/index.html",
        "staticfiles/dfd/js/app.js",
        "staticfiles/dfd/css/app.css",
        "assets/modulo_01.dfd.json",
        "VERSION",
    ):
        if not (BASE_DIR / rel).is_file():
            raise RuntimeError(f"Arquivo obrigatorio ausente: {rel}")
    from config.wsgi import run  # noqa: F401  -- confirma imports dinamicos do Vela
    print(f"DFD Studio Linux PyQt6 / QtWebEngine OK; renderer={RENDER_MODE}")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
    else:
        print(f"DFD Studio: renderer={RENDER_MODE} (DFD_HARDWARE_ACCELERATION=1 libera aceleracao)", flush=True)
        from config.wsgi import run
        run()
