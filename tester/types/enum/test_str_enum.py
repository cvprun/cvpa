# -*- coding: utf-8 -*-

from enum import auto, unique
from unittest import TestCase, main

from cvpa.types.enum.str_enum import _StrEnum


class MyEnum(_StrEnum):
    FOO = "foo"
    BAR = "bar"


class StrEnumTestCase(TestCase):
    def test_value(self):
        self.assertEqual(MyEnum.FOO, "foo")
        self.assertEqual(MyEnum.BAR, "bar")

    def test_is_str(self):
        self.assertIsInstance(MyEnum.FOO, str)

    def test_generate_next_value(self):
        result = _StrEnum._generate_next_value_("HELLO", 0, 0, [])
        self.assertEqual(result, "hello")

    def test_non_string_value_raises(self):
        with self.assertRaises(TypeError):

            class BadEnum(_StrEnum):
                X = 123  # type: ignore

    def test_too_many_args_raises(self):
        with self.assertRaises(TypeError):

            class BadEnum(_StrEnum):
                X = ("a", "b", "c", "d")

    def test_two_args_valid(self):
        class TwoArgEnum(_StrEnum):
            X = b"hello", "utf-8"

        self.assertEqual(TwoArgEnum.X, "hello")

    def test_two_args_bad_encoding_raises(self):
        with self.assertRaises(TypeError):

            class BadEnum(_StrEnum):
                X = b"hello", 123  # type: ignore

    def test_three_args_valid(self):
        class ThreeArgEnum(_StrEnum):
            X = b"hello", "utf-8", "strict"

        self.assertEqual(ThreeArgEnum.X, "hello")

    def test_three_args_bad_errors_raises(self):
        with self.assertRaises(TypeError):

            class BadEnum(_StrEnum):
                X = b"hello", "utf-8", 123  # type: ignore

    def test_auto_generates_lowercase(self):
        @unique
        class AutoEnum(_StrEnum):
            A = auto()
            B = auto()
            CamelCase = auto()

        self.assertEqual("a", AutoEnum.A)
        self.assertEqual("b", AutoEnum.B)
        self.assertEqual("camelcase", AutoEnum.CamelCase)

    def test_unique_rejects_duplicate(self):
        with self.assertRaises(ValueError):

            @unique
            class DupEnum(_StrEnum):
                a = auto()
                b = "a"


if __name__ == "__main__":
    main()
