# Bootstrap Design

> Status: active design
> Scope: 建立 my-aur-repo 最小完整链路，并以 `mrrss-bin` 作为首个验证实例。

## 背景

工作区目前只有已确认的长期控制面设计，尚无包声明、自动化代码、Actions、Release 或客户端验证。首次建设需要证明长期结构能够承载一个真实的上游 Release 二进制包，但不能让 MrRSS 的局部特征反向成为项目全局假设。

## 阶段目标

- 建立配置驱动的单包注册和 GitHub Release 监控能力。
- 在远端 Arch `x86_64` 环境中生成、验证并发布标准 pacman 包。
- 在同一公开 GitHub 仓库的固定 Release 中建立 `[my-aur]` 数据库。
- 让客户端通过正常 pacman/yay 路径安装和升级 `mrrss-bin`。
- 为后续包保留稳定扩展边界，不提前实现未出现的监控与打包类型。

## 阶段边界

### 包含

- `github_release` 稳定版监控；
- 标准 PKGBUILD 自动版本与校验和更新；
- 单一 `x86_64` 构建；
- 公共验证门禁的首个可运行集合；
- 固定 Release 发布和当前/上一版本保留；
- 包级失败 Issue；
- 每日、手工和 Push 触发；
- MrRSS 普通 Linux amd64 tar.gz 重打包。

### 不包含

- AUR 发布；
- arm64 或其他架构；
- tag、commit、网页和手工版本监控实现；
- deb、AppImage 或源码构建的专用公共适配器；
- GPG 强制签名；
- 私有软件源；
- AI 服务自动读取 Issue 并编写修复代码。

## MrRSS 实例决定

| 项目 | 决定 |
|---|---|
| 包名 | `mrrss-bin` |
| 上游 | `DevXDojo/MrRSS` |
| 监控 | 最新稳定 GitHub Release，忽略预发布 |
| 架构 | `x86_64`，映射上游 `linux-amd64` |
| 输入 | `MrRSS-{version}-linux-amd64.tar.gz`，不使用 AppImage |
| 安装 | 原生 Arch 路径，不要求运行时 FUSE |
| 包关系 | 提供并冲突 `mrrss` |
| 验证 | 动态依赖完整、桌面文件有效、干净环境安装/卸载；不在 CI 启动 GUI |

图标、desktop 文件、精确运行依赖和可再分发材料的具体处理必须在实施调查中核验，不能仅从 README 推断。

## 实现取舍

### 自动化语言

公共逻辑使用 Python 并由 uv 管理环境，负责 TOML/schema、GitHub API、版本状态、Issue 状态和可测试的数据变换。Shell 只调用 makepkg、updpkgsums、namcap、repo-add 等系统工具；workflow YAML 只负责编排。

### 标准工具

优先复用 makepkg、updpkgsums、namcap、repo-add、vercmp 和 GitHub CLI/API。若 Arch 官方工具已经覆盖需求，不增加等价自研实现。

### 发布一致性

Git 提交是期望状态，固定 Release 数据库是实际状态。首次实现必须验证提交成功而发布失败后的重试路径，以及新包先于数据库上传的顺序。

## 完成证据

本阶段只有在以下证据齐全后才能归档：

1. 正式 Actions 从清单发现 `mrrss-bin`；
2. 上游版本检测与稳定版过滤有自动化测试；
3. Actions 生成并安装验证 `.pkg.tar.zst`；
4. 固定 Release 可同时下载包与 `my-aur.db`；
5. 一台目标 Arch `x86_64` 客户端通过配置的软件源安装成功；
6. 人为制造的无更新、版本倒退和单包失败路径符合设计；
7. 当前 State、README 和长期文档与实际实现完成一致性收束。
