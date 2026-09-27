# my-aur-repo

个人自用的 Arch Linux 软件包监控、远端打包与 pacman 仓库发布工程。完整定位见 [`docs/INTENT.md`](docs/INTENT.md)。

---

## AI 启动规则

- 先读本文件，再按文档导航进入主链。
- 本文件只提供入口级约束、最小识别信息和导航，不替代核心文档。
- 理解项目为什么存在、边界和取舍时，读取 [`docs/INTENT.md`](docs/INTENT.md)。
- 理解监控、构建、发布和客户端消费链路时，读取 [`docs/WORKFLOW.md`](docs/WORKFLOW.md)。
- 理解目录、配置、命名和维护规范时，读取 [`docs/SPEC.md`](docs/SPEC.md)。
- 处理阶段性建设任务时，再读取 [`docs/development/DEV_WORKFLOW.md`](docs/development/DEV_WORKFLOW.md) 与对应的 `active/` 材料。
- 单个包不能反向定义项目架构；实例经验只有经过验证并具有长期普遍性时才能晋升为治理规则。

---

## 硬性约束

1. 始终使用简体中文工作。
2. 禁止使用系统 Python；需要 Python 时使用项目内由 uv 管理的虚拟环境。
3. 软件包的正式打包、编译和安装验证只在 GitHub Actions 中执行，不在维护者客户端执行。
4. 项目全局只面向 Arch Linux `x86_64`；不得因上游提供其他架构而自行扩展构建矩阵。
5. Git 只保存文本配方、配置、自动化和必要的小型辅助文件；禁止提交上游下载物、构建缓存、pacman 包和仓库数据库。
6. 公开发布前必须确认资产允许再分发；密钥、令牌、私有地址和受限资产不得进入仓库或公开 Release。
7. AI 可以直接提交和发布，但不得绕过 schema、构建、版本及产物验证。
8. 包依赖只允许来自 Arch 官方仓库或本项目已经发布的包；不得隐式拉取和构建 AUR 依赖。
9. 配方内容变化但 `pkgver` 未变化时必须增加 `pkgrel`；禁止覆盖已发布的同版本包。
10. 项目偏好破坏式演进，不为内部旧结构保留兼容层；Git 负责历史追溯。

---

## 快速环境摘要

```text
registry/                    # 启用包的唯一清单
packages/<pkgname>/          # 单包声明、PKGBUILD 与小型辅助文件
automation/                  # 监控、构建编排、验证和发布实现
docs/modules/                # 长期模块级控制文档
docs/development/active/     # 当前阶段材料，不是长期事实源
.github/workflows/           # GitHub Actions 入口
GitHub Releases              # pacman 数据库和 .pkg.tar.zst，不进入 Git
```

`automation/`、`schemas/`、`tests/` 等路径是规范中的职责位置，只在首次出现真实内容时创建，不使用空目录占位。

---

## 文档导航

| 文档 | 定位 | 什么时候读 |
|---|---|---|
| [`docs/INTENT.md`](docs/INTENT.md) | 意图与取舍 | 判断项目目标、边界和长期方向时 |
| [`docs/WORKFLOW.md`](docs/WORKFLOW.md) | 运转拓扑 | 判断修改处于哪个环节、影响什么上下游时 |
| [`docs/SPEC.md`](docs/SPEC.md) | 结构与规范 | 新增包、配置、目录或公共能力时 |
| [`docs/modules/package-model.md`](docs/modules/package-model.md) | 包定义模型 | 处理清单、监控声明、PKGBUILD、版本和依赖时 |
| [`docs/modules/automation.md`](docs/modules/automation.md) | 自动化模块 | 处理触发、构建、验证、失败和直接发布时 |
| [`docs/modules/repository.md`](docs/modules/repository.md) | pacman 仓库模块 | 处理 Release、数据库、保留和客户端契约时 |
| [`docs/development/DEV_WORKFLOW.md`](docs/development/DEV_WORKFLOW.md) | 阶段材料治理 | 开始或结束中大型建设、迁移和实验时 |
| [`docs/development/active/bootstrap/state.md`](docs/development/active/bootstrap/state.md) | 当前建设状态 | 继续首次建设与 `mrrss-bin` 接入时 |
