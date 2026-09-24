"""Configuracao do renderizador Linux antes de carregar o Qt.

O PyInstaller inclui Qt6/QtWebEngine, mas nao inclui driver GLX do host.
Para maximizar compatibilidade, o aplicativo inicia com renderizacao por
software; quem possui drivers GL adequados pode optar por hardware via
DFD_HARDWARE_ACCELERATION=1.
"""
import os


def configure_linux_graphics(environ=None):
    """Configura o ambiente sem importar o Qt; retorna o modo escolhido."""
    env = os.environ if environ is None else environ
    if env.get("DFD_HARDWARE_ACCELERATION", "").strip().lower() in ("1", "true", "yes"):
        return "hardware"

    # Primeiro evita o caminho GLX que abortava antes de abrir a janela.
    # Em GPUs/servidores X11 onde GLX nao esta funcional, Qt WebEngine pode
    # funcionar pelo renderizador em software (no entanto nao e garantido).
    env.setdefault("QT_XCB_GL_INTEGRATION", "none")
    env.setdefault("QT_QUICK_BACKEND", "software")
    env.setdefault("LIBGL_ALWAYS_SOFTWARE", "1")

    flags = env.get("QTWEBENGINE_CHROMIUM_FLAGS", "").strip()
    if "--disable-gpu" not in flags.split():
        env["QTWEBENGINE_CHROMIUM_FLAGS"] = (flags + " --disable-gpu").strip()
    return "software"
