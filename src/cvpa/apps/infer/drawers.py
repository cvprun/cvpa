# -*- coding: utf-8 -*-

from typing import Any, Callable, Dict, Final, List, Mapping, Sequence, Tuple, Union

from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont
from PIL.ImageFont import ImageFont as BitmapFont

from cvpa.apps.infer.formatters import (
    TASK_IMAGE_CLASSIFICATION,
    TASK_IMAGE_SEGMENTATION,
    TASK_OBJECT_DETECTION,
    TASK_ZERO_SHOT_IMAGE_CLASSIFICATION,
)

AnyFont = Union[FreeTypeFont, BitmapFont]

_PALETTE: Final[Sequence[Tuple[int, int, int]]] = (
    (230, 25, 75),
    (60, 180, 75),
    (255, 225, 25),
    (0, 130, 200),
    (245, 130, 48),
    (145, 30, 180),
    (70, 240, 240),
    (240, 50, 230),
    (210, 245, 60),
    (250, 190, 212),
    (0, 128, 128),
    (220, 190, 255),
    (170, 110, 40),
    (255, 250, 200),
    (128, 0, 0),
    (170, 255, 195),
)


def _font(size: int = 16) -> AnyFont:
    return ImageFont.load_default(size=size)


def _color_for(index: int) -> Tuple[int, int, int]:
    return _PALETTE[index % len(_PALETTE)]


def _draw_label_box(
    draw: ImageDraw.ImageDraw,
    xy: Tuple[float, float],
    text: str,
    font: AnyFont,
    fill: Tuple[int, int, int, int],
) -> None:
    bbox = draw.textbbox(xy, text, font=font)
    draw.rectangle(bbox, fill=fill)
    draw.text(xy, text, fill=(255, 255, 255), font=font)


def _draw_classification(
    image: Image.Image, result: List[Mapping[str, Any]]
) -> Image.Image:
    canvas = image.convert("RGBA")
    draw = ImageDraw.Draw(canvas, "RGBA")
    font = _font(size=max(14, canvas.width // 40))

    lines = [f"{i + 1}. {r['label']}  {r['score']:.3f}" for i, r in enumerate(result)]
    text = "\n".join(lines)

    bbox = draw.multiline_textbbox((10, 10), text, font=font, spacing=4)
    x1, y1, x2, y2 = bbox
    draw.rectangle([x1 - 6, y1 - 6, x2 + 6, y2 + 6], fill=(0, 0, 0, 180))
    draw.multiline_text((10, 10), text, fill=(255, 255, 255), font=font, spacing=4)

    return canvas


def _draw_detection(image: Image.Image, result: List[Mapping[str, Any]]) -> Image.Image:
    canvas = image.convert("RGBA")
    draw = ImageDraw.Draw(canvas, "RGBA")
    font = _font(size=max(14, canvas.width // 60))

    for i, r in enumerate(result):
        box = r["box"]
        x1, y1, x2, y2 = box["xmin"], box["ymin"], box["xmax"], box["ymax"]
        rgb = _color_for(i)

        draw.rectangle([x1, y1, x2, y2], outline=rgb + (255,), width=3)
        label = f"{r['label']} {r['score']:.2f}"
        _draw_label_box(draw, (x1, y1), label, font, rgb + (220,))

    return canvas


def _draw_segmentation(
    image: Image.Image, result: List[Mapping[str, Any]]
) -> Image.Image:
    base = image.convert("RGBA")
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))

    for i, r in enumerate(result):
        mask = r["mask"]
        rgba = _color_for(i) + (128,)
        tinted = Image.new("RGBA", base.size, rgba)
        overlay.paste(tinted, (0, 0), mask)

    composed = Image.alpha_composite(base, overlay)

    draw = ImageDraw.Draw(composed, "RGBA")
    font_size = max(14, composed.width // 60)
    font = _font(size=font_size)
    cursor_y = 10
    for i, r in enumerate(result):
        rgb = _color_for(i)
        label = r["label"]
        _draw_label_box(draw, (10, cursor_y), label, font, rgb + (220,))
        cursor_y += font_size + 6

    return composed


_DRAWERS: Dict[str, Callable[[Image.Image, List[Mapping[str, Any]]], Image.Image]] = {
    TASK_IMAGE_CLASSIFICATION: _draw_classification,
    TASK_ZERO_SHOT_IMAGE_CLASSIFICATION: _draw_classification,
    TASK_OBJECT_DETECTION: _draw_detection,
    TASK_IMAGE_SEGMENTATION: _draw_segmentation,
}


def draw_result(task: str, image: Image.Image, result: Any) -> Image.Image:
    fn = _DRAWERS.get(task)
    if fn is None or not isinstance(result, list):
        return image.convert("RGBA")
    return fn(image, result)
