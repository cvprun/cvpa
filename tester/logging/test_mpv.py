# -*- coding: utf-8 -*-

from unittest import TestCase, main

from cvpa.logging.mpv import MpvLogLevel


class MpvLogLevelTestCase(TestCase):
    def test_all_members(self):
        expected = ("no", "fatal", "error", "warn", "info", "v", "debug", "trace")
        members = [m.value for m in MpvLogLevel]
        self.assertEqual(tuple(members), expected)

    def test_is_str(self):
        self.assertIsInstance(MpvLogLevel.no, str)
        self.assertEqual(MpvLogLevel.no, "no")

    def test_count(self):
        self.assertEqual(len(MpvLogLevel), 8)


if __name__ == "__main__":
    main()
