# -*- coding: utf-8 -*-

from unittest import TestCase, main

from cvpa.system import environ_keys


class EnvironKeysTestCase(TestCase):
    def test_all_are_strings(self):
        keys = [
            k
            for k in dir(environ_keys)
            if k.startswith("CVPA_") and not k.startswith("__")
        ]
        for key in keys:
            value = getattr(environ_keys, key)
            self.assertIsInstance(value, str, f"{key} is not a string")

    def test_cvpa_home(self):
        self.assertEqual(environ_keys.CVPA_HOME, "CVPA_HOME")


if __name__ == "__main__":
    main()
