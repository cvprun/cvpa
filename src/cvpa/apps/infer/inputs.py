# -*- coding: utf-8 -*-

from os import scandir
from os.path import isdir, isfile, splitext
from typing import Final, FrozenSet, Iterator

IMAGE_EXTS: Final[FrozenSet[str]] = frozenset(
    {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tiff"}
)


def iter_image_paths(path: str) -> Iterator[str]:
    if isfile(path):
        yield path
        return

    if isdir(path):
        with scandir(path) as it:
            entries = sorted(it, key=lambda e: e.name)
        for entry in entries:
            if not entry.is_file():
                continue
            if splitext(entry.name)[1].lower() in IMAGE_EXTS:
                yield entry.path
        return

    raise FileNotFoundError(path)
