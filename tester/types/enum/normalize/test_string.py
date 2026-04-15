# -*- coding: utf-8 -*-

from enum import StrEnum
from types import MappingProxyType
from unittest import TestCase, main

from cvpa.types.enum.normalize.string import index2string, string2index


class Fruit(StrEnum):
    APPLE = "apple"
    BANANA = "banana"
    CHERRY = "cherry"


class String2IndexTestCase(TestCase):
    def test_mapping(self):
        result = string2index(Fruit)
        self.assertIsInstance(result, MappingProxyType)
        self.assertEqual(result["apple"], 0)
        self.assertEqual(result["banana"], 1)
        self.assertEqual(result["cherry"], 2)


class Index2StringTestCase(TestCase):
    def test_mapping(self):
        result = index2string(Fruit)
        self.assertIsInstance(result, MappingProxyType)
        self.assertEqual(result[0], "apple")
        self.assertEqual(result[1], "banana")
        self.assertEqual(result[2], "cherry")


if __name__ == "__main__":
    main()
