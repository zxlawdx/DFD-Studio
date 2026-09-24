"""Regressoes do configurador grafico sem dependencias PyQt em CI."""
import unittest

from linux_graphics import configure_linux_graphics


class TestLinuxGraphics(unittest.TestCase):
    def test_software_mode_is_default(self):
        env = {}
        self.assertEqual(configure_linux_graphics(env), "software")
        self.assertEqual(env["QT_XCB_GL_INTEGRATION"], "none")
        self.assertEqual(env["LIBGL_ALWAYS_SOFTWARE"], "1")
        self.assertEqual(env["QT_QUICK_BACKEND"], "software")
        self.assertEqual(env["QTWEBENGINE_CHROMIUM_FLAGS"], "--disable-gpu")

    def test_hardware_mode_opt_in(self):
        env = {"DFD_HARDWARE_ACCELERATION": "1"}
        self.assertEqual(configure_linux_graphics(env), "hardware")
        self.assertNotIn("QT_XCB_GL_INTEGRATION", env)
        self.assertNotIn("QTWEBENGINE_CHROMIUM_FLAGS", env)

    def test_preserves_custom_flags(self):
        env = {"QTWEBENGINE_CHROMIUM_FLAGS": "--enable-logging"}
        configure_linux_graphics(env)
        self.assertEqual(env["QTWEBENGINE_CHROMIUM_FLAGS"],
                         "--enable-logging --disable-gpu")
        configure_linux_graphics(env)
        self.assertEqual(env["QTWEBENGINE_CHROMIUM_FLAGS"].count("--disable-gpu"), 1)

    def test_preserves_explicit_render_configuration(self):
        env = {"QT_QUICK_BACKEND": "other", "QT_XCB_GL_INTEGRATION": "xcb_egl"}
        configure_linux_graphics(env)
        self.assertEqual(env["QT_QUICK_BACKEND"], "other")
        self.assertEqual(env["QT_XCB_GL_INTEGRATION"], "xcb_egl")


if __name__ == "__main__":
    unittest.main()
