# -*- coding: utf-8 -*-

from unittest import TestCase, main
from unittest.mock import patch

from cvpa.system.shell import get_default_shell_path


class ShellWindowsTestCase(TestCase):
    @patch("cvpa.system.shell.platform.system", return_value="Windows")
    @patch.dict("os.environ", {"COMSPEC": r"C:\cmd.exe"})
    def test_comspec(self, _):
        self.assertEqual(get_default_shell_path(), r"C:\cmd.exe")

    @patch("cvpa.system.shell.platform.system", return_value="Windows")
    @patch.dict("os.environ", {}, clear=True)
    @patch(
        "cvpa.system.shell.shutil.which",
        side_effect=lambda x: {
            "powershell.exe": r"C:\powershell.exe",
        }.get(x),
    )
    def test_powershell(self, _w, _p):
        self.assertEqual(get_default_shell_path(), r"C:\powershell.exe")

    @patch("cvpa.system.shell.platform.system", return_value="Windows")
    @patch.dict("os.environ", {}, clear=True)
    @patch(
        "cvpa.system.shell.shutil.which",
        side_effect=lambda x: {
            "pwsh.exe": r"C:\pwsh.exe",
        }.get(x),
    )
    def test_pwsh(self, _w, _p):
        self.assertEqual(get_default_shell_path(), r"C:\pwsh.exe")

    @patch("cvpa.system.shell.platform.system", return_value="Windows")
    @patch.dict("os.environ", {}, clear=True)
    @patch(
        "cvpa.system.shell.shutil.which",
        side_effect=lambda x: {
            "cmd.exe": r"C:\cmd.exe",
        }.get(x),
    )
    def test_cmd(self, _w, _p):
        self.assertEqual(get_default_shell_path(), r"C:\cmd.exe")

    @patch("cvpa.system.shell.platform.system", return_value="Windows")
    @patch.dict("os.environ", {}, clear=True)
    @patch("cvpa.system.shell.shutil.which", return_value=None)
    def test_fallback(self, _w, _p):
        self.assertEqual(get_default_shell_path(), r"C:\Windows\System32\cmd.exe")


class ShellLinuxTestCase(TestCase):
    @patch("cvpa.system.shell.platform.system", return_value="Linux")
    @patch("pwd.getpwuid")
    def test_getpwuid(self, mock_pw, _):
        mock_pw.return_value.pw_shell = "/bin/zsh"
        self.assertEqual(get_default_shell_path(), "/bin/zsh")

    @patch("cvpa.system.shell.platform.system", return_value="Linux")
    @patch.dict("os.environ", {"SHELL": "/bin/fish"})
    @patch("pwd.getpwuid", side_effect=Exception)
    def test_shell_env(self, _pw, _p):
        self.assertEqual(get_default_shell_path(), "/bin/fish")

    @patch("cvpa.system.shell.platform.system", return_value="Linux")
    @patch.dict("os.environ", {}, clear=True)
    @patch(
        "cvpa.system.shell.shutil.which",
        side_effect=lambda x: {
            "bash": "/bin/bash",
        }.get(x),
    )
    @patch("pwd.getpwuid", side_effect=Exception)
    def test_bash_fallback(self, _pw, _w, _p):
        self.assertEqual(get_default_shell_path(), "/bin/bash")

    @patch("cvpa.system.shell.platform.system", return_value="Linux")
    @patch.dict("os.environ", {}, clear=True)
    @patch(
        "cvpa.system.shell.shutil.which",
        side_effect=lambda x: {
            "sh": "/bin/sh",
        }.get(x),
    )
    @patch("pwd.getpwuid", side_effect=Exception)
    def test_sh_fallback(self, _pw, _w, _p):
        self.assertEqual(get_default_shell_path(), "/bin/sh")

    @patch("cvpa.system.shell.platform.system", return_value="Linux")
    @patch.dict("os.environ", {}, clear=True)
    @patch("cvpa.system.shell.shutil.which", return_value=None)
    @patch("pwd.getpwuid", side_effect=Exception)
    def test_final_fallback(self, _pw, _w, _p):
        self.assertEqual(get_default_shell_path(), "/bin/sh")


class ShellDarwinTestCase(TestCase):
    @patch("cvpa.system.shell.platform.system", return_value="Darwin")
    @patch.dict("os.environ", {}, clear=True)
    @patch(
        "cvpa.system.shell.shutil.which",
        side_effect=lambda x: {
            "zsh": "/bin/zsh",
        }.get(x),
    )
    @patch("pwd.getpwuid", side_effect=Exception)
    def test_zsh_preferred(self, _pw, _w, _p):
        self.assertEqual(get_default_shell_path(), "/bin/zsh")


class ShellUnsupportedTestCase(TestCase):
    @patch("cvpa.system.shell.platform.system", return_value="FreeBSD")
    def test_raises(self, _):
        with self.assertRaises(NotImplementedError):
            get_default_shell_path()


if __name__ == "__main__":
    main()
