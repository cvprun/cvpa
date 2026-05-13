# -*- coding: utf-8 -*-

from sys import exit as sys_exit
from sys import stderr

try:
    import torch  # noqa: F401
    import torchvision  # noqa: F401
    import transformers  # noqa: F401
except ModuleNotFoundError as e:
    print(
        f"Missing ML dependency '{e.name}'. " "Install with: pip install 'cvpa[ml]'",
        file=stderr,
    )
    sys_exit(1)
