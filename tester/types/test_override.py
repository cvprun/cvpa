# -*- coding: utf-8 -*-

from unittest import TestCase, main

from cvpa.types.override import _fake_override


class FakeOverrideTestCase(TestCase):
    def test_preserves_function(self):
        @_fake_override
        def foo(x):
            return x + 1

        self.assertEqual(foo(1), 2)

    def test_preserves_name(self):
        @_fake_override
        def my_func():
            pass

        self.assertEqual(my_func.__name__, "my_func")

    def test_override_importable(self):
        from cvpa.types.override import override

        self.assertTrue(callable(override))


if __name__ == "__main__":
    main()
