# -*- coding: utf-8 -*-

import os
import sys
from unittest import TestCase, main

from cvpa.asserts import get_assets_dir


class GetAssetsDirTestCase(TestCase):
    def test_without_meipass(self):
        get_assets_dir.cache_clear()
        result = get_assets_dir()
        self.assertTrue(os.path.isabs(result))
        get_assets_dir.cache_clear()

    def test_with_meipass(self):
        get_assets_dir.cache_clear()
        sys._MEIPASS = "/fake/path"  # type: ignore[attr-defined]
        try:
            result = get_assets_dir()
            self.assertEqual(result, os.path.join("/fake/path", "assets"))
        finally:
            del sys._MEIPASS  # type: ignore[attr-defined]
            get_assets_dir.cache_clear()


if __name__ == "__main__":
    main()
