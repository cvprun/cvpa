# -*- coding: utf-8 -*-

from unittest import TestCase, main

from cvpa.types.matcher.base import BaseTypesMatcher
from cvpa.types.matcher.interface import TypesMatcherInterface


class TypesMatcherInterfaceTestCase(TestCase):
    def test_cannot_instantiate(self):
        with self.assertRaises(TypeError):
            TypesMatcherInterface()  # type: ignore[abstract]

    def test_abstract_methods_raise(self):
        """Directly call abstract methods via __dict__
        to cover raise NotImplementedError."""
        from datetime import date, datetime, time, timedelta
        from enum import Enum
        from pathlib import Path
        from types import ModuleType

        import numpy as np

        # Create a minimal concrete subclass to get an instance
        m = BaseTypesMatcher()

        # Call the interface methods directly from the ABC
        methods_data = [
            ("on_none_data", None),
            ("on_bytes_data", b""),
            ("on_bytearray_data", bytearray()),
            ("on_memoryview_data", memoryview(b"")),
            ("on_complex_data", 1j),
            ("on_float_data", 1.0),
            ("on_int_data", 1),
            ("on_bool_data", True),
            ("on_str_data", ""),
            ("on_tuple_data", ()),
            ("on_set_data", set()),
            ("on_list_data", []),
            ("on_dict_data", {}),
            ("on_ndarray_data", np.array([])),
            ("on_datetime_data", datetime.now()),
            ("on_date_data", date.today()),
            ("on_time_data", time()),
            ("on_timedelta_data", timedelta()),
            ("on_path_data", Path(".")),
            ("on_enum_data", Enum("E", "A").A),
            ("on_mapping_data", {}),
            ("on_iterable_data", []),
            ("on_dataclass_data", None),
            ("on_module_data", ModuleType("x")),
            ("on_class_data", int),
            ("on_unknown_data", object()),
        ]
        for method_name, data in methods_data:
            with self.assertRaises(NotImplementedError):
                TypesMatcherInterface.__dict__[method_name](m, data, None)


class BaseTypesMatcherTestCase(TestCase):
    def test_instantiable(self):
        m = BaseTypesMatcher()
        self.assertIsInstance(m, TypesMatcherInterface)

    def test_all_methods_return_none(self):
        from datetime import date, datetime, time, timedelta
        from enum import Enum
        from pathlib import Path
        from types import ModuleType

        import numpy as np

        m = BaseTypesMatcher()
        methods = [
            ("on_none_data", None),
            ("on_bytes_data", b""),
            ("on_bytearray_data", bytearray()),
            ("on_memoryview_data", memoryview(b"")),
            ("on_complex_data", 1 + 2j),
            ("on_float_data", 1.0),
            ("on_int_data", 1),
            ("on_bool_data", True),
            ("on_str_data", ""),
            ("on_tuple_data", ()),
            ("on_set_data", set()),
            ("on_list_data", []),
            ("on_dict_data", {}),
            ("on_ndarray_data", np.array([])),
            ("on_datetime_data", datetime.now()),
            ("on_date_data", date.today()),
            ("on_time_data", time()),
            ("on_timedelta_data", timedelta()),
            ("on_path_data", Path(".")),
            ("on_enum_data", Enum("E", "A").A),
            ("on_mapping_data", {}),
            ("on_iterable_data", []),
            ("on_dataclass_data", None),
            ("on_module_data", ModuleType("test")),
            ("on_class_data", int),
            ("on_unknown_data", object()),
        ]
        for method_name, data in methods:
            result = getattr(m, method_name)(data, None)
            self.assertIsNone(result, f"{method_name} should return None")


if __name__ == "__main__":
    main()
