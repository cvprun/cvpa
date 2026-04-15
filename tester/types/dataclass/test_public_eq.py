# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import Dict, List
from unittest import TestCase, main

from cvpa.types.dataclass.public_eq import public_eq
from cvpa.types.shapes import Point


@public_eq
@dataclass
class EqSample:
    name: str = "hello"
    _private: str = "secret"


@public_eq
@dataclass
class NestedVal:
    value0: List[Point] = field(default_factory=list)
    value1: Dict[int, int] = field(default_factory=dict)
    _private_value: int = 0


@public_eq
@dataclass
class NestedTest:
    value0 = 0
    value1: int = 1
    value2: str = "2"
    value3: Point = 3, 3
    value4: NestedVal = field(default_factory=NestedVal)
    _private_value: int = 0


class PublicEqTestCase(TestCase):
    def test_equal(self):
        a = EqSample(name="test", _private="a")
        b = EqSample(name="test", _private="b")
        self.assertEqual(a, b)

    def test_not_equal(self):
        a = EqSample(name="foo")
        b = EqSample(name="bar")
        self.assertNotEqual(a, b)

    def test_lh_wrong_type(self):
        a = EqSample()
        self.assertNotEqual("not_eq_sample", a)

    def test_lh_wrong_type_direct(self):
        """Direct call to __eq__ with lh not being cls instance."""
        self.assertFalse(EqSample.__eq__("not_eq", EqSample()))

    def test_rh_wrong_type(self):
        a = EqSample()
        self.assertNotEqual(a, "not_eq_sample")


class NestedPublicEqTestCase(TestCase):
    def test_nested_equal_ignoring_private(self):
        aa = NestedVal(value0=[(1, 1), (2, 2)], value1={1: 1}, _private_value=1)
        bb = NestedVal(value0=[(1, 1), (2, 2)], value1={1: 1}, _private_value=2)
        a = NestedTest(
            value1=10,
            value2="20",
            value3=(30, 30),
            value4=aa,
            _private_value=3,
        )
        b = NestedTest(
            value1=10,
            value2="20",
            value3=(30, 30),
            value4=bb,
            _private_value=4,
        )
        self.assertEqual(aa, bb)
        self.assertEqual(a, b)

    def test_nested_cross_type_not_equal(self):
        aa = NestedVal(value0=[(1, 1)])
        a = NestedTest(value4=aa)
        self.assertNotEqual(aa, a)
        self.assertNotEqual(a, aa)

    def test_nested_list_order_matters(self):
        aa = NestedVal(value0=[(2, 2), (1, 1)])
        bb = NestedVal(value0=[(1, 1), (2, 2)])
        self.assertNotEqual(aa, bb)


if __name__ == "__main__":
    main()
