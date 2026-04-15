# -*- coding: utf-8 -*-

from dataclasses import dataclass
from unittest import TestCase, main

from cvpa.types.dataclass.public_eq import public_eq


@public_eq
@dataclass
class EqSample:
    name: str = "hello"
    _private: str = "secret"


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


if __name__ == "__main__":
    main()
