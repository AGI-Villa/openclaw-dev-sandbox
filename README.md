# openclaw-dev-sandbox

OpenClaw 多 Agent 自动化开发沙盒。

由 AI Agent 团队自主开发，人类负责方向和 Review。

## 工作流

1. Darren 在 Discord 发布需求
2. 扫地僧（CTO Agent）拆解任务 → 创建 GitHub Issues
3. Dev Sub-Agents 各自认领 Issue → 用 Cursor CLI 开发 → 提交 PR
4. Review Agent 审查代码 → approve 后合并
5. 进度每日汇报到 Discord

## 每日天气查询 CLI

使用 [wttr.in](https://wttr.in) 免费 API 查询全球城市天气，无需注册。

### 使用方法

```bash
python weather.py <城市名>
```

### 示例

```bash
$ python weather.py Beijing

📍 Beijing, China
🌡  温度: 12°C (体感 10°C)
☁  天气: Partly cloudy
💧 湿度: 45%
```

支持中文和英文城市名：

```bash
python weather.py Tokyo
python weather.py "New York"
python weather.py London
```

### 依赖

仅使用 Python 标准库（`urllib`、`json`），无需安装额外依赖。要求 Python 3.6+。

## 分支规范

- `main` — 受保护，只接受 PR 合并
- `feat/issue-<N>-<desc>` — 功能开发分支
- `fix/issue-<N>-<desc>` — Bug 修复分支
# trigger test 3 Thu Mar  5 00:14:52 CST 2026
