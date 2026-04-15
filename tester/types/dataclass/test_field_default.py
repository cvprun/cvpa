# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from unittest import TestCase, main

from cvpa.types.dataclass.field_default import get_field_default
from cvpa.types.dataclass.field_name import get_field_name


@dataclass
class Sample:
    name: str = "hello"
    age: int = 10
    tags: list = field(default_factory=list)
    required: str = field(default=str())


class GetFieldDefaultTestCase(TestCase):
    def test_plain_default(self):
        keys = get_field_name(Sample)
        self.assertEqual(get_field_default(Sample, keys.name), "hello")
        self.assertEqual(get_field_default(Sample, keys.age), 10)

    def test_default_factory(self):
        keys = get_field_name(Sample)
        result = get_field_default(Sample, keys.tags)
        self.assertEqual(result, [])

    def test_non_dataclass_raises(self):
        with self.assertRaises(TypeError):
            get_field_default(int, "x")  # type: ignore[arg-type]

    def test_no_default_raises(self):
        @dataclass
        class NoDefault:
            value: str

        keys = get_field_name(NoDefault)
        with self.assertRaises(ValueError):
            get_field_default(NoDefault, keys.value)

    def test_with_instance(self):
        instance = Sample()
        keys = get_field_name(instance)
        self.assertEqual(get_field_default(instance, keys.name), "hello")


if __name__ == "__main__":
    main()
