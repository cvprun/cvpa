# -*- coding: utf-8 -*-

import os
from unittest import TestCase, main

from cvpa.system.environ import (
    environ_dict,
    exchange_env,
    exchange_env_context,
    get_typed_environ_value,
)


class GetTypedEnvironValueTestCase(TestCase):
    def test_default_none_missing(self):
        result = get_typed_environ_value("_CVPA_TEST_NONEXISTENT_KEY_")
        self.assertIsNone(result)

    def test_default_none_present(self):
        os.environ["_CVPA_TEST_KEY_"] = "hello"
        try:
            result = get_typed_environ_value("_CVPA_TEST_KEY_")
            self.assertEqual(result, "hello")
        finally:
            os.environ.pop("_CVPA_TEST_KEY_")

    def test_default_str(self):
        result = get_typed_environ_value("_CVPA_TEST_NONEXISTENT_", "fallback")
        self.assertEqual(result, "fallback")

    def test_default_bool(self):
        os.environ["_CVPA_TEST_BOOL_"] = "true"
        try:
            result = get_typed_environ_value("_CVPA_TEST_BOOL_", False)
            self.assertTrue(result)
        finally:
            os.environ.pop("_CVPA_TEST_BOOL_")

    def test_default_int(self):
        os.environ["_CVPA_TEST_INT_"] = "42"
        try:
            result = get_typed_environ_value("_CVPA_TEST_INT_", 0)
            self.assertEqual(result, 42)
        finally:
            os.environ.pop("_CVPA_TEST_INT_")

    def test_default_float(self):
        os.environ["_CVPA_TEST_FLOAT_"] = "3.14"
        try:
            result = get_typed_environ_value("_CVPA_TEST_FLOAT_", 0.0)
            self.assertAlmostEqual(result, 3.14)
        finally:
            os.environ.pop("_CVPA_TEST_FLOAT_")

    def test_unsupported_type_raises(self):
        with self.assertRaises(TypeError):
            get_typed_environ_value("_CVPA_TEST_", [])  # type: ignore[call-overload]


class EnvironDictTestCase(TestCase):
    def test_returns_dict(self):
        result = environ_dict()
        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 0)


class ExchangeEnvTestCase(TestCase):
    def test_exchange_existing(self):
        os.environ["_CVPA_EXCHANGE_"] = "old"
        result = exchange_env("_CVPA_EXCHANGE_", "new")
        self.assertEqual(result, "old")
        self.assertEqual(os.environ["_CVPA_EXCHANGE_"], "new")
        os.environ.pop("_CVPA_EXCHANGE_")

    def test_exchange_missing(self):
        os.environ.pop("_CVPA_EXCHANGE_", None)
        result = exchange_env("_CVPA_EXCHANGE_", "new")
        self.assertIsNone(result)
        self.assertEqual(os.environ["_CVPA_EXCHANGE_"], "new")
        os.environ.pop("_CVPA_EXCHANGE_")

    def test_exchange_with_none(self):
        os.environ["_CVPA_EXCHANGE_"] = "old"
        result = exchange_env("_CVPA_EXCHANGE_", None)
        self.assertEqual(result, "old")
        self.assertNotIn("_CVPA_EXCHANGE_", os.environ)

    def test_exchange_missing_with_none(self):
        os.environ.pop("_CVPA_EXCHANGE_", None)
        result = exchange_env("_CVPA_EXCHANGE_", None)
        self.assertIsNone(result)
        self.assertNotIn("_CVPA_EXCHANGE_", os.environ)


class ExchangeEnvContextTestCase(TestCase):
    def test_restores_original(self):
        os.environ["_CVPA_CTX_"] = "original"
        with exchange_env_context("_CVPA_CTX_", "temporary"):
            self.assertEqual(os.environ["_CVPA_CTX_"], "temporary")
        self.assertEqual(os.environ["_CVPA_CTX_"], "original")
        os.environ.pop("_CVPA_CTX_")

    def test_restores_missing(self):
        os.environ.pop("_CVPA_CTX_", None)
        with exchange_env_context("_CVPA_CTX_", "temporary"):
            self.assertEqual(os.environ["_CVPA_CTX_"], "temporary")
        self.assertNotIn("_CVPA_CTX_", os.environ)


if __name__ == "__main__":
    main()
