# -*- coding: utf-8 -*-

from sys import exit as sys_exit
from typing import List, Optional

from cvpa.apps import run_app
from cvpa.arguments import get_default_arguments


def main(cmdline: Optional[List[str]] = None) -> int:
    args = get_default_arguments(cmdline)
    return run_app(args.cmd, args)


if __name__ == "__main__":
    sys_exit(main())
