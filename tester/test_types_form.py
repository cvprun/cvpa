# -*- coding: utf-8 -*-

from typing import Optional
from unittest import TestCase, main

from cvpa.types.form import SpecialForm


class SpecialFormTestCase(TestCase):
    def test_is_type_of_optional(self):
        self.assertIs(SpecialForm, type(Optional))


if __name__ == "__main__":
    main()
