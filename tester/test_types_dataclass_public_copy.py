# -*- coding: utf-8 -*-

from copy import copy, deepcopy
from dataclasses import dataclass, field
from unittest import TestCase, main

from cvpa.types.dataclass.public_copy import public_copy, public_deepcopy


@public_copy
@dataclass
class CopySample:
    name: str = "hello"
    _private: str = "secret"


@public_deepcopy
@dataclass
class DeepCopySample:
    name: str = "world"
    _private: str = "secret"


class PublicCopyTestCase(TestCase):
    def test_copy_copies_public_from_class_default(self):
        obj = CopySample(name="test", _private="hidden")
        result = copy(obj)
        self.assertEqual(result.name, "hello")

    def test_copy_skips_private(self):
        obj = CopySample(name="test", _private="hidden")
        result = copy(obj)
        self.assertNotEqual(result._private, "hidden")


class PublicDeepCopyTestCase(TestCase):
    def test_deepcopy_copies_public_from_class_default(self):
        obj = DeepCopySample(name="test", _private="hidden")
        result = deepcopy(obj)
        self.assertEqual(result.name, "world")

    def test_deepcopy_with_memo(self):
        obj = DeepCopySample(name="test")
        memo = {}
        result = obj.__deepcopy__(memo)
        self.assertIn(id(obj), memo)

    def test_deepcopy_without_memo(self):
        obj = DeepCopySample(name="test")
        result = obj.__deepcopy__(None)
        self.assertEqual(result.name, "world")


if __name__ == "__main__":
    main()
