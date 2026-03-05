# bg-removal — 图片背景移除工具

基于 [rembg](https://github.com/danielgatis/rembg) 的图片背景移除 CLI 工具。

- 支持输入格式：PNG / JPG / WebP
- 输出格式：PNG（带透明 Alpha 通道）
- 依赖管理：Poetry
- 开发/测试环境：Docker

## 快速开始（Docker，推荐）

### 构建镜像

```bash
# 测试镜像
docker build --target test -t bg-removal-test .

# 运行时镜像
docker build --target runtime -t bg-removal .
```

### 运行测试

```bash
docker run --rm bg-removal-test
```

### 移除背景

```bash
docker run --rm -v $(pwd)/images:/data bg-removal /data/input.jpg /data/output.png
```

## 本地开发（需要 Poetry）

```bash
cd bg_removal
poetry install --with dev
```

### CLI 用法

```bash
# 基本用法
poetry run bg-remove input.jpg output.png

# 指定模型
poetry run bg-remove input.png output.png --model u2net

# 启用 alpha matting（更精细的边缘）
poetry run bg-remove photo.webp result.png --alpha-matting

# 后处理 mask
poetry run bg-remove photo.jpg result.png --post-process-mask
```

### 作为 Python 模块使用

```python
from bg_removal.core import remove_background

output = remove_background("photo.jpg", "result.png")
print(f"已保存: {output}")
```

### 运行测试

```bash
poetry run pytest -v
```

## 项目结构

```
bg_removal/
├── pyproject.toml        # Poetry 依赖配置
├── Dockerfile            # 多阶段构建 (test / runtime)
├── .dockerignore
├── README.md
├── bg_removal/
│   ├── __init__.py
│   ├── core.py           # 核心背景移除逻辑
│   └── cli.py            # 命令行入口
└── tests/
    ├── __init__.py
    └── test_core.py      # 单元测试
```

## 支持的模型

默认使用 `u2net`，首次运行会自动下载模型文件（~170MB）。rembg 还支持 `u2netp`、`u2net_human_seg`、`isnet-general-use` 等模型，通过 `--model` 参数切换。

## 依赖

| 包 | 用途 |
|---|---|
| rembg[cpu] | 背景移除引擎（CPU 推理） |
| Pillow | 图片 I/O |
| pytest | 单元测试（dev） |
