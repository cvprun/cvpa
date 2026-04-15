# -*- coding: utf-8 -*-

from dataclasses import dataclass
from unittest import TestCase, main

from cvpa.types.dataclass.field_name import get_field_name


@dataclass
class User:
    name: str = ""
    age: int = 0


class GetFieldNameTestCase(TestCase):
    def test_with_class(self):
        keys = get_field_name(User)
        self.assertEqual(keys.name, "name")
        self.assertEqual(keys.age, "age")

    def test_with_instance(self):
        instance = User()
        keys = get_field_name(instance)
        self.assertEqual(keys.name, "name")
        self.assertEqual(keys.age, "age")

    def test_non_dataclass_raises(self):
        with self.assertRaises(TypeError):
            get_field_name(int)  # type: ignore[arg-type]


if __name__ == "__main__":
    main()
