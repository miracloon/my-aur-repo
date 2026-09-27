# Bootstrap State

> Status: active
> 本文件是当前工作快照，不是执行日志，也不能替代代码、Actions 或客户端证据。

## 已确认

- 项目定位、长期边界、单仓库公开交付、x86_64 范围和 AI 直接发布规则已经由用户确认。
- 包定义、版本语义、失败隔离、依赖来源、版本保留、每日监控和失败 Issue 方向已经确认。
- `mrrss-bin` 作为首个实例，选择稳定 GitHub Release 的普通 Linux amd64 tar.gz，不使用 AppImage。
- 公共自动化使用 Python + uv；Shell 仅调用 Arch 系统工具，workflow YAML 不承载业务逻辑。
- 控制面文档栏目结构已经用户确认并锁定。

## 已验证完成

- 工作区初始为空，未发现需要迁移的旧代码、旧配置或旧控制文档。
- 上游 MrRSS 仓库存在稳定 Release 流程，并声明提供 Linux amd64 tar.gz 与 AppImage。
- 上游 Release 工作流可见当前资产命名规则及 x86_64 构建路径。
- 工作区已重命名为 `my-aur-repo` 并初始化 `main` 分支。
- registry、schema、Python 自动化、测试、工作流和 `mrrss-bin` 标准 PKGBUILD 已落地。
- 本地仅执行文本与自动化验证：Ruff 通过、13 项 pytest 通过、真实上游发现输出 `mrrss-bin 1.3.38-1`。
- 上游 tar.gz SHA-256 与 Release digest 一致；二进制直接依赖已调查为 GTK4、WebKitGTK 6.0、libsoup3、GLib、X11 和 glibc。

以上不证明远端打包、Release 发布或客户端安装已经成功。

## 当前进行中

- 部署公开 GitHub 仓库并运行正式 Actions。

## 尚未实现或验证

- 远程 GitHub Actions 的 Arch 构建与安装验证；
- 固定 Release、pacman 数据库、版本保留与失败 Issue 的运行验证；
- 客户端 pacman/yay 端到端检索、安装与升级；
- 定时保活的实际运行验证；
- GPG 签名。

## 开放问题

- 无设计待裁决项；等待首次正式运行证据。

## 当前下一步

1. 创建 `miracloon/my-aur-repo` 公开仓库并推送 `main`；
2. 观察并修复正式 Actions，直至 Release 可由 pacman 消费；
3. 配置本机源并完成 `mrrss-bin` 检索和安装；
4. 每获得新的运行证据后更新本 State。

## 长期治理状态

- `AGENTS.md`、`docs/INTENT.md`、`docs/WORKFLOW.md`、`docs/SPEC.md` 和三个模块文档的栏目结构已经用户确认并锁定；后续增删或合并 `##` 须先提出结构变更申请。
- bootstrap 完成前，任何“已支持”判断必须回到代码、Actions、Release 和客户端证据核验。
