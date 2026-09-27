# my-aur-repo

个人自用的 Arch Linux `x86_64` 二进制包仓库。Git 保存包配方与自动化；同仓库 GitHub Releases 保存 pacman 数据库和构建后的包。

项目意图、边界和内部结构分别见：

- [`docs/INTENT.md`](docs/INTENT.md)
- [`docs/WORKFLOW.md`](docs/WORKFLOW.md)
- [`docs/SPEC.md`](docs/SPEC.md)

## 客户端配置

在 `/etc/pacman.conf` 中、官方仓库之后加入：

```ini
[my-aur]
SigLevel = Optional TrustAll
Server = https://github.com/miracloon/my-aur-repo/releases/download/repository-x86_64
```

刷新数据库后即可通过 pacman 或 yay 安装：

```bash
sudo pacman -Syu
sudo pacman -S mrrss-bin
# 或 yay -S mrrss-bin
```

当前仓库暂未启用 GPG 包签名，因此自定义源显式允许未签名包。

## 管理的包

| 包 | 上游 | 监控 | 输入 |
|---|---|---|---|
| `mrrss-bin` | [DevXDojo/MrRSS](https://github.com/DevXDojo/MrRSS) | 稳定 GitHub Release | Linux amd64 tar.gz |

## 自动化入口

- 每日检查全部启用包；
- Actions 可手工检查全部包或指定包；
- 配方和自动化 Push 后检查尚未发布的目标版本；
- 正式打包、安装验证和发布只在 GitHub Actions 中进行。

新增包时，在 `packages/<pkgname>/` 写入标准 PKGBUILD 和 `package.toml`，并在 `registry/packages.toml` 显式启用。详细约束见 [`docs/modules/package-model.md`](docs/modules/package-model.md)。

## 本地开发

Python 环境由 uv 管理：

```bash
uv sync
uv run ruff check .
uv run pytest
uv run my-aur validate
```

这些命令只验证自动化逻辑和文本配置，不在本机打包软件。
