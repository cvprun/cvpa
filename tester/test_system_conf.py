# -*- coding: utf-8 -*-

from unittest import TestCase, main
from unittest.mock import patch

from cvpa.system.conf import get_page_size, get_page_size_with_unix


class GetPageSizeWithUnixTestCase(TestCase):
    def test_returns_positive(self):
        result = get_page_size_with_unix()
        self.assertGreater(result, 0)


class GetPageSizeTestCase(TestCase):
    def test_unix_path(self):
        with patch("cvpa.system.conf.sys.platform", "linux"):
            result = get_page_size()
            self.assertGreater(result, 0)

    def test_win32_path(self):
        with patch("cvpa.system.conf.sys.platform", "win32"):
            with patch("cvpa.system.conf.get_page_size_with_win32", return_value=4096):
                result = get_page_size()
                self.assertEqual(result, 4096)


if __name__ == "__main__":
    main()
