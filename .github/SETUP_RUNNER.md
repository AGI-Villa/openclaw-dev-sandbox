# GitHub Actions Self-Hosted Runner 安装指南

CTO Review 通过本机 self-hosted runner 执行，需要一次性安装配置。

## 安装步骤

### 1. 在 GitHub 获取注册 Token

前往：`https://github.com/SuperSupeng/openclaw-dev-sandbox/settings/actions/runners/new`

选择：Linux / x64，拿到注册命令里的 `--token <TOKEN>`。

### 2. 在服务器上安装 Runner

```bash
# 创建目录
mkdir -p /home/admin/actions-runner && cd /home/admin/actions-runner

# 下载最新版 runner（从 GitHub releases 获取最新版本号）
RUNNER_VERSION=$(curl -s https://api.github.com/repos/actions/runner/releases/latest | grep '"tag_name"' | sed 's/.*"v\([^"]*\)".*/\1/')
curl -o actions-runner.tar.gz -L \
  "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz"
tar xzf actions-runner.tar.gz

# 注册 runner（替换 TOKEN）
./config.sh \
  --url https://github.com/SuperSupeng/openclaw-dev-sandbox \
  --token <TOKEN> \
  --name "cto-review-runner" \
  --labels "self-hosted,linux,x64" \
  --work "/home/admin/actions-runner/_work" \
  --unattended

# 安装为 systemd 服务（开机自启）
sudo ./svc.sh install
sudo ./svc.sh start
```

### 3. 配置 GitHub Secrets

在仓库 `Settings > Secrets and variables > Actions` 里添加：

| Secret 名 | 值 |
|-----------|---|
| `CURSOR_API_KEY` | Cursor API Key（从 Cursor 账号设置获取） |

`GITHUB_TOKEN` 是 GitHub 自动注入的，无需手动配置。

### 4. 验证安装

```bash
# 查看 runner 状态
sudo /home/admin/actions-runner/svc.sh status

# 查看 runner 日志
sudo journalctl -u actions.runner.SuperSupeng-openclaw-dev-sandbox.cto-review-runner -f
```

在 GitHub 上：`Settings > Actions > Runners`，应看到 runner 状态为 **Idle**。

### 5. 测试触发

研发主管提一个测试 PR，assign reviewer `darrencto`，观察 Actions tab 是否触发。

---

## 常见问题

**Runner offline？**
```bash
sudo /home/admin/actions-runner/svc.sh start
```

**Cursor API 认证失败？**
- 检查 `CURSOR_API_KEY` secret 是否正确配置
- 本机验证：`CURSOR_API_KEY=<key> agent status`

**Runner 注册 Token 过期？**（Token 有效期 1 小时）
- 重新从 GitHub 获取新 Token，重新运行 `./config.sh`
