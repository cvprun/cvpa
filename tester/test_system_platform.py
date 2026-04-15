# -*- coding: utf-8 -*-

from unittest import TestCase, main

from cvpa.system.platform import (
    SysMach,
    get_normalized_machine,
    get_normalized_system,
    get_system_machine,
)


class GetNormalizedSystemTestCase(TestCase):
    def test_darwin(self):
        self.assertEqual(get_normalized_system("Darwin"), "darwin")

    def test_windows(self):
        self.assertEqual(get_normalized_system("Windows"), "windows")

    def test_linux(self):
        self.assertEqual(get_normalized_system("Linux"), "linux")

    def test_unknown_raises(self):
        with self.assertRaises(ValueError):
            get_normalized_system("FreeBSD")

    def test_default_uses_platform(self):
        result = get_normalized_system()
        self.assertIn(result, ("darwin", "windows", "linux"))


class GetNormalizedMachineTestCase(TestCase):
    def test_x86_64(self):
        self.assertEqual(get_normalized_machine("x86_64"), "x64")

    def test_i386(self):
        self.assertEqual(get_normalized_machine("i386"), "x86")

    def test_arm64(self):
        self.assertEqual(get_normalized_machine("arm64"), "arm64")

    def test_aarch64(self):
        self.assertEqual(get_normalized_machine("aarch64"), "arm64")

    def test_unknown_raises(self):
        with self.assertRaises(ValueError):
            get_normalized_machine("mips")

    def test_default_uses_platform(self):
        result = get_normalized_machine()
        self.assertIn(result, ("x64", "x86", "arm64"))


class GetSystemMachineTestCase(TestCase):
    def test_explicit_args(self):
        result = get_system_machine("linux", "x64")
        self.assertEqual(result, SysMach.linux_x64)

    def test_all_combinations(self):
        for sys in ("windows", "linux", "darwin"):
            for mach in ("x64", "x86", "arm64"):
                result = get_system_machine(sys, mach)
                self.assertEqual(result, SysMach(f"{sys}.{mach}"))

    def test_default_args(self):
        result = get_system_machine()
        self.assertIsInstance(result, SysMach)


if __name__ == "__main__":
    main()
