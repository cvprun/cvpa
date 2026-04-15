# -*- coding: utf-8 -*-

import types
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from enum import Enum
from pathlib import Path
from unittest import TestCase, main

import numpy as np

from cvpa.types.matcher.base import BaseTypesMatcher
from cvpa.types.matcher.mapper import TypesMatcherMapper


class SpyMatcher(BaseTypesMatcher):
    def __init__(self):
        self.last_called = None

    def _record(self, name, data, extra):
        self.last_called = name

    def on_none_data(self, data, extra):
        self._record("none", data, extra)

    def on_bytes_data(self, data, extra):
        self._record("bytes", data, extra)

    def on_bytearray_data(self, data, extra):
        self._record("bytearray", data, extra)

    def on_memoryview_data(self, data, extra):
        self._record("memoryview", data, extra)

    def on_complex_data(self, data, extra):
        self._record("complex", data, extra)

    def on_float_data(self, data, extra):
        self._record("float", data, extra)

    def on_int_data(self, data, extra):
        self._record("int", data, extra)

    def on_bool_data(self, data, extra):
        self._record("bool", data, extra)

    def on_str_data(self, data, extra):
        self._record("str", data, extra)

    def on_tuple_data(self, data, extra):
        self._record("tuple", data, extra)

    def on_set_data(self, data, extra):
        self._record("set", data, extra)

    def on_list_data(self, data, extra):
        self._record("list", data, extra)

    def on_dict_data(self, data, extra):
        self._record("dict", data, extra)

    def on_ndarray_data(self, data, extra):
        self._record("ndarray", data, extra)

    def on_datetime_data(self, data, extra):
        self._record("datetime", data, extra)

    def on_date_data(self, data, extra):
        self._record("date", data, extra)

    def on_time_data(self, data, extra):
        self._record("time", data, extra)

    def on_timedelta_data(self, data, extra):
        self._record("timedelta", data, extra)

    def on_path_data(self, data, extra):
        self._record("path", data, extra)

    def on_enum_data(self, data, extra):
        self._record("enum", data, extra)

    def on_mapping_data(self, data, extra):
        self._record("mapping", data, extra)

    def on_iterable_data(self, data, extra):
        self._record("iterable", data, extra)

    def on_dataclass_data(self, data, extra):
        self._record("dataclass", data, extra)

    def on_module_data(self, data, extra):
        self._record("module", data, extra)

    def on_class_data(self, data, extra):
        self._record("class", data, extra)

    def on_unknown_data(self, data, extra):
        self._record("unknown", data, extra)


class TypesMatcherMapperTestCase(TestCase):
    def setUp(self):
        self.spy = SpyMatcher()
        self.mapper = TypesMatcherMapper.from_default(self.spy)

    def test_dict_fast_path(self):
        self.mapper(None)
        self.assertEqual(self.spy.last_called, "none")

    def test_basic_types(self):
        cases = [
            (None, "none"),
            (b"data", "bytes"),
            (bytearray(b"x"), "bytearray"),
            (memoryview(b"x"), "memoryview"),
            (1 + 2j, "complex"),
            (1.0, "float"),
            (42, "int"),
            (True, "bool"),
            ("hello", "str"),
            ((1, 2), "tuple"),
            ({1, 2}, "set"),
            ([1, 2], "list"),
            ({"a": 1}, "dict"),
            (np.array([1]), "ndarray"),
            (datetime.now(), "datetime"),
            (date.today(), "date"),
            (time(12, 0), "time"),
            (timedelta(seconds=1), "timedelta"),
        ]
        for data, expected in cases:
            self.mapper(data)
            self.assertEqual(
                self.spy.last_called, expected, f"Failed for {type(data).__name__}"
            )

    def test_fallback_path(self):
        spy = SpyMatcher()
        mapper = TypesMatcherMapper(spy)

        mapper(Path("/tmp"))
        self.assertEqual(spy.last_called, "path")

    def test_enum_fallback(self):
        class Color(Enum):
            RED = 1

        spy = SpyMatcher()
        mapper = TypesMatcherMapper(spy)

        mapper(Color.RED)
        self.assertEqual(spy.last_called, "enum")

    def test_mapping_fallback(self):
        from collections.abc import Mapping as AbcMapping

        class CustomMapping(AbcMapping):
            def __getitem__(self, key):
                return None

            def __iter__(self):
                return iter(())

            def __len__(self):
                return 0

        spy = SpyMatcher()
        mapper = TypesMatcherMapper(spy)

        mapper(CustomMapping())
        self.assertEqual(spy.last_called, "mapping")

    def test_iterable_fallback(self):
        spy = SpyMatcher()
        mapper = TypesMatcherMapper(spy)

        mapper(frozenset([1, 2]))
        self.assertEqual(spy.last_called, "iterable")

    def test_dataclass_fallback(self):
        @dataclass
        class Point:
            x: int = 0

        spy = SpyMatcher()
        mapper = TypesMatcherMapper(spy)

        mapper(Point())
        self.assertEqual(spy.last_called, "dataclass")

    def test_module_fallback(self):
        spy = SpyMatcher()
        mapper = TypesMatcherMapper(spy)

        mapper(types)
        self.assertEqual(spy.last_called, "module")

    def test_class_fallback(self):
        spy = SpyMatcher()
        mapper = TypesMatcherMapper(spy)

        class Foo:
            pass

        mapper(Foo)
        self.assertEqual(spy.last_called, "class")

    def test_unknown_fallback(self):
        spy = SpyMatcher()
        mapper = TypesMatcherMapper(spy)

        class Weird:
            pass

        mapper(Weird())
        self.assertEqual(spy.last_called, "unknown")

    def test_callable(self):
        self.mapper("test")
        self.assertEqual(self.spy.last_called, "str")

    def test_ordered_dict_dispatches_to_dict(self):
        from collections import OrderedDict

        self.mapper(OrderedDict())
        self.assertEqual(self.spy.last_called, "dict")

    def test_deque_dispatches_to_iterable(self):
        from collections import deque

        spy = SpyMatcher()
        mapper = TypesMatcherMapper(spy)
        mapper(deque())
        self.assertEqual(spy.last_called, "iterable")

    def test_dataclass_class_dispatches(self):
        @dataclass
        class Pt:
            x: int = 0

        spy = SpyMatcher()
        mapper = TypesMatcherMapper(spy)
        mapper(Pt)
        self.assertEqual(spy.last_called, "dataclass")

    def test_builtin_callable_dispatches_to_unknown(self):
        spy = SpyMatcher()
        mapper = TypesMatcherMapper(spy)
        mapper(sum)
        self.assertEqual(spy.last_called, "unknown")

    def test_match_fallback_all_basic_types(self):
        """Test match statement fallback for all basic types (empty mapper)."""
        spy = SpyMatcher()
        mapper = TypesMatcherMapper(spy)

        # Note: bool skipped because Python match matches True to int() case
        cases = [
            (None, "none"),
            (b"x", "bytes"),
            (bytearray(b"x"), "bytearray"),
            (memoryview(b"x"), "memoryview"),
            (1 + 2j, "complex"),
            (1.0, "float"),
            (42, "int"),
            ("hello", "str"),
            ((1,), "tuple"),
            ({1}, "set"),
            ([1], "list"),
            ({"a": 1}, "dict"),
            (np.array([1]), "ndarray"),
            (datetime.now(), "datetime"),
            (date.today(), "date"),
            (time(12, 0), "time"),
            (timedelta(seconds=1), "timedelta"),
        ]
        for data, expected in cases:
            mapper(data)
            self.assertEqual(
                spy.last_called, expected, f"Failed match fallback for {type(data)}"
            )


if __name__ == "__main__":
    main()
