# -*- coding: utf-8 -*-

from unittest import TestCase, main

from cvpa.system.shortcut.xdg import _CONTENT


class XdgContentTestCase(TestCase):
    def test_is_string(self):
        self.assertIsInstance(_CONTENT, str)

    def test_contains_desktop_entry(self):
        self.assertIn("[Desktop Entry]", _CONTENT)


if __name__ == "__main__":
    main()
