"""Entrada da distribuição Windows; Qt deve ser importado antes do Vela."""
import os
import sys
from pathlib import Path
os.environ['PYWEBVIEW_GUI'] = 'qt'
from PyQt5.QtWidgets import QApplication  # noqa
from PyQt5.QtWebEngineWidgets import QWebEngineView  # noqa
import webview
import webview.platforms.qt  # noqa
webview.settings['OPEN_DEVTOOLS_IN_DEBUG'] = False
_start = webview.start

def start_qt(*args, **kwargs):
    kwargs.pop('gui', None)
    kwargs['debug'] = False
    return _start(*args, gui='qt', **kwargs)

webview.start = start_qt
BASE_DIR = Path(sys.executable).resolve().parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent
# ApiServer do Vela serve staticfiles a partir do diretório de trabalho.
os.chdir(BASE_DIR)
sys.path.insert(0, str(BASE_DIR))
if __name__ == '__main__':
    from config.wsgi import run
    run()
