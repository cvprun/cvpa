# -*- coding: utf-8 -*-

from enum import IntEnum
from types import MappingProxyType
from unittest import TestCase, main

from cvpa.types.enum.normalize.number import (
    name2number,
    normalize_name2number,
    normalize_number2name,
    number2name,
)


class Color(IntEnum):
    RED = 1
    GREEN = 2
    BLUE = 3


class Name2NumberTestCase(TestCase):
    def test_mapping(self):
        result = name2number(Color)
        self.assertIsInstance(result, MappingProxyType)
        self.assertEqual(result["RED"], 1)
        self.assertEqual(result["GREEN"], 2)
        self.assertEqual(result["BLUE"], 3)


class Number2NameTestCase(TestCase):
    def test_mapping(self):
        result = number2name(Color)
        self.assertIsInstance(result, MappingProxyType)
        self.assertEqual(result[1], "RED")
        self.assertEqual(result[2], "GREEN")
        self.assertEqual(result[3], "BLUE")


class NormalizeName2NumberTestCase(TestCase):
    def setUp(self):
        self.mapping = name2number(Color)

    def test_with_enum(self):
        self.assertEqual(normalize_name2number(self.mapping, Color.RED), 1)

    def test_with_str(self):
        self.assertEqual(normalize_name2number(self.mapping, "RED"), 1)

    def test_with_int(self):
        self.assertEqual(normalize_name2number(self.mapping, 42), 42)

    def test_with_unsupported_type(self):
        with self.assertRaises(TypeError):
            normalize_name2number(self.mapping, 3.14)  # type: ignore[arg-type]


class NormalizeNumber2NameTestCase(TestCase):
    def setUp(self):
        self.mapping = number2name(Color)

    def test_with_enum(self):
        self.assertEqual(normalize_number2name(self.mapping, Color.RED), "RED")

    def test_with_str(self):
        self.assertEqual(normalize_number2name(self.mapping, "RED"), "RED")

    def test_with_int(self):
        self.assertEqual(normalize_number2name(self.mapping, 1), "RED")

    def test_with_unsupported_type(self):
        with self.assertRaises(TypeError):
            normalize_number2name(self.mapping, 3.14)  # type: ignore[arg-type]


if __name__ == "__main__":
    main()
