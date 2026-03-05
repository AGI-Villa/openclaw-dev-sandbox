"""命令行入口：bg-remove <input> <output>"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from bg_removal.core import (
    SUPPORTED_INPUT_FORMATS,
    UnsupportedFormatError,
    remove_background,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bg-remove",
        description="移除图片背景，输出带透明通道的 PNG。",
    )
    parser.add_argument("input", type=Path, help="输入图片路径 (PNG/JPG/WebP)")
    parser.add_argument("output", type=Path, help="输出 PNG 路径")
    parser.add_argument(
        "--model",
        default="u2net",
        help="rembg 模型名称 (默认: u2net)",
    )
    parser.add_argument(
        "--alpha-matting",
        action="store_true",
        help="启用 alpha matting 精细化边缘",
    )
    parser.add_argument(
        "--post-process-mask",
        action="store_true",
        help="对 mask 进行后处理",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    print(f"输入: {args.input}")
    print(f"输出: {args.output}")
    print(f"模型: {args.model}")

    start = time.perf_counter()
    try:
        out = remove_background(
            args.input,
            args.output,
            model_name=args.model,
            alpha_matting=args.alpha_matting,
            post_process_mask=args.post_process_mask,
        )
    except (FileNotFoundError, UnsupportedFormatError) as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1

    elapsed = time.perf_counter() - start
    print(f"完成! 耗时 {elapsed:.2f}s → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
