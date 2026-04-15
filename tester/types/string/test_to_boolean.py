# -*- coding: utf-8 -*-

from unittest import TestCase, main

from cvpa.types.string.to_boolean import FALSE_LOWERS, TRUE_LOWERS, string_to_boolean


class StringToBooleanTestCase(TestCase):
    def test_true_values(self):
        for v in TRUE_LOWERS:
            self.assertTrue(string_to_boolean(v))

    def test_false_values(self):
        for v in FALSE_LOWERS:
            self.assertFalse(string_to_boolean(v))

    def test_case_insensitive_true(self):
        self.assertTrue(string_to_boolean("YES"))
        self.assertTrue(string_to_boolean("True"))
        self.assertTrue(string_to_boolean("ON"))

    def test_case_insensitive_false(self):
        self.assertFalse(string_to_boolean("NO"))
        self.assertFalse(string_to_boolean("False"))
        self.assertFalse(string_to_boolean("OFF"))

    def test_invalid_raises(self):
        with self.assertRaises(ValueError):
            string_to_boolean("maybe")

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            string_to_boolean("")


if __name__ == "__main__":
    main()
