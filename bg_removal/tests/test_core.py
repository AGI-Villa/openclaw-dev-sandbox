"""bg_removal.core 单元测试。"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from bg_removal.core import (
    SUPPORTED_INPUT_FORMATS,
    UnsupportedFormatError,
    remove_background,
    validate_input,
)


@pytest.fixture()
def sample_rgb_image(tmp_path: Path) -> Path:
    """创建一张简单的 100x100 RGB PNG 测试图片。"""
    img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    path = tmp_path / "sample.png"
    img.save(path)
    return path


@pytest.fixture()
def sample_jpg_image(tmp_path: Path) -> Path:
    img = Image.new("RGB", (100, 100), color=(0, 255, 0))
    path = tmp_path / "sample.jpg"
    img.save(path)
    return path


@pytest.fixture()
def sample_webp_image(tmp_path: Path) -> Path:
    img = Image.new("RGB", (100, 100), color=(0, 0, 255))
    path = tmp_path / "sample.webp"
    img.save(path)
    return path


# ---------- validate_input ----------


class TestValidateInput:
    def test_valid_png(self, sample_rgb_image: Path) -> None:
        assert validate_input(sample_rgb_image) == sample_rgb_image

    def test_valid_jpg(self, sample_jpg_image: Path) -> None:
        assert validate_input(sample_jpg_image) == sample_jpg_image

    def test_valid_webp(self, sample_webp_image: Path) -> None:
        assert validate_input(sample_webp_image) == sample_webp_image

    def test_file_not_found(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError, match="输入文件不存在"):
            validate_input(tmp_path / "nonexistent.png")

    def test_unsupported_format(self, tmp_path: Path) -> None:
        bmp = tmp_path / "image.bmp"
        Image.new("RGB", (10, 10)).save(bmp)
        with pytest.raises(UnsupportedFormatError, match="不支持的格式"):
            validate_input(bmp)


# ---------- remove_background ----------


class TestRemoveBackground:
    @patch("bg_removal.core.remove")
    def test_output_is_png_rgba(
        self, mock_remove: MagicMock, sample_rgb_image: Path, tmp_path: Path
    ) -> None:
        """输出应为 RGBA PNG。"""
        rgba_result = Image.new("RGBA", (100, 100), (255, 0, 0, 0))
        mock_remove.return_value = rgba_result

        out = tmp_path / "out.png"
        result_path = remove_background(sample_rgb_image, out)

        assert result_path.exists()
        with Image.open(result_path) as result_img:
            assert result_img.mode == "RGBA"
            assert result_img.format == "PNG"

    @patch("bg_removal.core.remove")
    def test_output_suffix_forced_to_png(
        self, mock_remove: MagicMock, sample_rgb_image: Path, tmp_path: Path
    ) -> None:
        """即使指定 .jpg 输出，也应自动改为 .png。"""
        mock_remove.return_value = Image.new("RGBA", (100, 100))
        result_path = remove_background(sample_rgb_image, tmp_path / "out.jpg")
        assert result_path.suffix == ".png"

    @patch("bg_removal.core.remove")
    def test_creates_output_dir(
        self, mock_remove: MagicMock, sample_rgb_image: Path, tmp_path: Path
    ) -> None:
        """输出目录不存在时应自动创建。"""
        mock_remove.return_value = Image.new("RGBA", (100, 100))
        out = tmp_path / "subdir" / "deep" / "out.png"
        result_path = remove_background(sample_rgb_image, out)
        assert result_path.exists()

    @patch("bg_removal.core.remove")
    def test_accepts_jpg_input(
        self, mock_remove: MagicMock, sample_jpg_image: Path, tmp_path: Path
    ) -> None:
        mock_remove.return_value = Image.new("RGBA", (100, 100))
        result_path = remove_background(sample_jpg_image, tmp_path / "out.png")
        assert result_path.exists()

    @patch("bg_removal.core.remove")
    def test_accepts_webp_input(
        self, mock_remove: MagicMock, sample_webp_image: Path, tmp_path: Path
    ) -> None:
        mock_remove.return_value = Image.new("RGBA", (100, 100))
        result_path = remove_background(sample_webp_image, tmp_path / "out.png")
        assert result_path.exists()

    def test_rejects_unsupported_format(self, tmp_path: Path) -> None:
        bmp = tmp_path / "img.bmp"
        Image.new("RGB", (10, 10)).save(bmp)
        with pytest.raises(UnsupportedFormatError):
            remove_background(bmp, tmp_path / "out.png")

    def test_rejects_missing_file(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            remove_background(tmp_path / "nope.png", tmp_path / "out.png")


# ---------- CLI ----------


class TestCli:
    def test_parser_defaults(self) -> None:
        from bg_removal.cli import build_parser

        parser = build_parser()
        args = parser.parse_args(["in.png", "out.png"])
        assert args.input == Path("in.png")
        assert args.output == Path("out.png")
        assert args.model == "u2net"
        assert args.alpha_matting is False

    @patch("bg_removal.cli.remove_background")
    def test_main_success(
        self, mock_rb: MagicMock, sample_rgb_image: Path, tmp_path: Path
    ) -> None:
        from bg_removal.cli import main

        out = tmp_path / "out.png"
        mock_rb.return_value = out
        code = main([str(sample_rgb_image), str(out)])
        assert code == 0
        mock_rb.assert_called_once()

    def test_main_file_not_found(self, tmp_path: Path) -> None:
        from bg_removal.cli import main

        code = main([str(tmp_path / "nope.png"), str(tmp_path / "out.png")])
        assert code == 1
