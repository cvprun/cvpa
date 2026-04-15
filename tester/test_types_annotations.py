# -*- coding: utf-8 -*-

from unittest import TestCase, main

from cvpa.types.annotations import AnnotatedAlias


class AnnotatedAliasTestCase(TestCase):
    def test_is_a_type(self):
        self.assertTrue(isinstance(AnnotatedAlias, type))

    def test_from_typing(self):
        import typing

        if hasattr(typing, "_AnnotatedAlias"):
            self.assertIs(AnnotatedAlias, typing._AnnotatedAlias)


if __name__ == "__main__":
    main()
