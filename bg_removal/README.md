# 背景移除工具 (Background Removal Tool)

基于 [rembg](https://github.com/danielgatis/rembg) 的图片背景移除工具，支持命令行和 Web 界面两种使用方式。

## 功能特性

- **输入格式**: PNG, JPG, WebP
- **输出格式**: 带透明通道的 PNG
- **使用方式**: 
  - 命令行工具 (CLI)
  - Web 界面 (浏览器上传/下载)
- **容器化**: 支持 Docker 部署

## 安装

### 使用 Docker (推荐)

```bash
# 拉取镜像
docker pull agi-villa/bg-removal:latest

# 运行 CLI 工具
docker run --rm -v $(pwd):/work agi-villa/bg-removal:latest bg-remove input.jpg output.png

# 运行 Web 服务
docker run --rm -p 8080:8080 agi-villa/bg-removal:latest
```

### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/AGI-Villa/openclaw-dev-sandbox.git
cd openclaw-dev-sandbox/bg_removal

# 安装依赖 (需要 Poetry)
poetry install

# 构建 Docker 镜像
docker build -t bg-removal .
```

## 使用方法

### CLI 命令行

```bash
# 基本用法
bg-remove input.jpg output.png

# 批量处理
bg-remove *.jpg ./output/

# 查看帮助
bg-remove --help
```

### Web 界面

1. 启动 Web 服务:
   ```bash
   # 使用 Docker
   docker run --rm -p 8080:8080 bg-removal
   
   # 或使用 Python
   python -m uvicorn bg_removal.web:app --host 0.0.0.0 --port 8080
   ```

2. 访问 `http://localhost:8080` 在浏览器中使用

3. 功能特性:
   - 拖拽或点击上传图片
   - 实时预览处理结果
   - 下载处理后的 PNG 图片
   - 响应式设计，支持移动设备

## API 接口

Web 服务提供 REST API:

- **POST `/api/remove-bg`**: 上传图片文件，返回处理后的 PNG

请求示例:
```bash
curl -X POST -F "file=@input.jpg" http://localhost:8080/api/remove-bg -o output.png
```

## 安全限制

- 文件大小限制: 10MB
- 支持的文件类型: PNG, JPG, JPEG, WebP
- 临时文件自动清理

## 开发

### 目录结构

```
bg_removal/
├── bg_removal/          # 核心模块
│   ├── __init__.py
│   ├── cli.py          # CLI 接口
│   ├── core.py         # 核心功能
│   └── web.py          # Web 服务
├── web/                # Web 界面
│   ├── index.html
│   ├── style.css
│   └── script.js
├── tests/              # 测试文件
├── Dockerfile          # Docker 配置
├── pyproject.toml      # 依赖管理
└── README.md           # 说明文档
```

### 测试

```bash
# 运行测试
poetry run pytest
```

## 许可证

MIT License