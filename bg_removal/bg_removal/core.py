"""核心背景移除逻辑，封装 rembg。"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PIL import Image
from rembg import remove

SUPPORTED_INPUT_FORMATS = {".png", ".jpg", ".jpeg", ".webp"}


class UnsupportedFormatError(Exception):
    """输入文件格式不受支持时抛出。"""


def validate_input(path: Path) -> Path:
    """校验输入文件存在且格式受支持，返回规范化的 Path。"""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"输入文件不存在: {path}")
    if path.suffix.lower() not in SUPPORTED_INPUT_FORMATS:
        raise UnsupportedFormatError(
            f"不支持的格式 '{path.suffix}'，仅支持: {', '.join(sorted(SUPPORTED_INPUT_FORMATS))}"
        )
    return path


def remove_background(
    input_path: str | Path,
    output_path: str | Path,
    *,
    model_name: str = "u2net",
    alpha_matting: bool = False,
    alpha_matting_foreground_threshold: int = 240,
    alpha_matting_background_threshold: int = 10,
    post_process_mask: bool = False,
) -> Path:
    """移除图片背景并保存为带透明通道的 PNG。

    Parameters
    ----------
    input_path : 输入图片路径 (PNG/JPG/WebP)
    output_path : 输出 PNG 路径
    model_name : rembg 模型名称，默认 u2net
    alpha_matting : 是否启用 alpha matting 精细化边缘
    alpha_matting_foreground_threshold : 前景阈值
    alpha_matting_background_threshold : 背景阈值
    post_process_mask : 是否对 mask 后处理

    Returns
    -------
    Path : 输出文件的路径
    """
    input_path = validate_input(Path(input_path))
    output_path = Path(output_path)

    if output_path.suffix.lower() != ".png":
        output_path = output_path.with_suffix(".png")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(input_path) as img:
        img = img.convert("RGBA")

        result: Image.Image = remove(
            img,
            alpha_matting=alpha_matting,
            alpha_matting_foreground_threshold=alpha_matting_foreground_threshold,
            alpha_matting_background_threshold=alpha_matting_background_threshold,
            post_process_mask=post_process_mask,
        )
        result.save(output_path, format="PNG")

    return output_path
