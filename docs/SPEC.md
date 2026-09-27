# my-aur-repo - 结构与规范

> 本文档回答“项目如何被组织”——文档边界、目录结构、模块边界、命名与维护规范。

## 栏目索引

| 栏目 | 回答什么 | 不放什么 |
|---|---|---|
| 文档层级与维护 | 有哪些长期与阶段文档、各自管什么 | 具体开发历史 |
| 项目目录结构 | 目录怎么划分、关键位置在哪 | 每个文件的实现说明 |
| 模块边界与组织方式 | 模块怎么划分、边界在哪 | 模块为何存在——归 INTENT |
| 命名、约定与维护规范 | 包、配置和文件的约定 | 代码风格偏好 |
| 版本管理与兼容性规范 | 包版本和内部 schema 规则 | 版本检测流程 |
| AI 易踩坑的结构性边界 | 结构上反直觉的事实 | 意图或流程层面的坑 |

---

## 文档层级与维护

| 文档 | 写什么 | 不写什么 |
|---|---|---|
| `AGENTS.md` | 入口约束和导航 | 完整项目说明 |
| `docs/INTENT.md` | 项目意图、边界和取舍 | 操作步骤、目录细目 |
| `docs/WORKFLOW.md` | 运转拓扑、环节和运行环境 | 命令教程、结构规范 |
| `docs/SPEC.md` | 目录、模块、命名和维护规则 | 设计初心、运转流程 |
| `docs/modules/*.md` | 单个逻辑模块的意图、结构与运转 | 项目级规则、单包实例 |
| `docs/development/active/*` | 当前 Design、Plan、State 和开放问题 | 冒充长期或已实现事实 |
| `docs/development/history/*` | 已结束阶段的追溯记录 | 日常启动上下文 |
| `README.md` | 面向维护者的配置和操作手册 | AI 控制面规则 |

长期治理与阶段材料的晋升、归档规则见 [`development/DEV_WORKFLOW.md`](development/DEV_WORKFLOW.md)。

---

## 项目目录结构

```text
my-aur-repo/
├── AGENTS.md
├── CLAUDE.md
├── README.md                         # 面向维护者的操作手册
├── registry/
│   └── packages.toml                 # 启用包的唯一清单
├── packages/
│   └── <pkgname>/
│       ├── package.toml              # 自动化无法从 PKGBUILD 得知的声明
│       ├── PKGBUILD                  # Arch 打包事实源
│       ├── files/                    # 必要的小型自有辅助文件（可选）
│       └── README.md                 # 单包特殊知识（可选）
├── automation/                       # 公共监控、编排、验证和发布实现
├── schemas/                          # 结构化声明的 schema
├── tests/                            # 公共自动化逻辑测试
├── docs/
│   ├── INTENT.md
│   ├── WORKFLOW.md
│   ├── SPEC.md
│   ├── modules/
│   └── development/
│       ├── DEV_WORKFLOW.md
│       ├── active/<initiative>/
│       └── history/<initiative>/
└── .github/workflows/                # GitHub Actions 入口
```

路径在结构上保留不等于立即创建。`automation/`、`schemas/`、`tests/`、`packages/` 和工作流目录只在出现真实内容时落盘，不以 `.gitkeep` 或空壳实现宣称能力。

GitHub Release Assets 不属于 Git 目录树。pacman 数据库、包和上游下载物只存在于临时构建环境或 Release。

---

## 模块边界与组织方式

| 模块 | 结构边界 | 详细规范 |
|---|---|---|
| 包定义 | `registry/` 与 `packages/<pkgname>/`；每个目录对应一个稳定 pacman 包身份 | [`modules/package-model.md`](modules/package-model.md) |
| 自动化 | `automation/` 与 `.github/workflows/`；前者承载可测试逻辑，后者只负责编排入口 | [`modules/automation.md`](modules/automation.md) |
| 仓库发布 | 自动化中的发布职责与 GitHub Release；不在 Git 中建立二进制目录 | [`modules/repository.md`](modules/repository.md) |
| 声明验证 | `schemas/` 与相应测试；未知字段和未注册类型必须失败 | 包定义与自动化模块 |

跨模块规则：工作流不得复制公共业务逻辑；包目录不得实现仓库发布；公共自动化不得硬编码单个包名或资产布局。

---

## 命名、约定与维护规范

### 包身份

- `packages/<pkgname>/` 的目录名必须等于 PKGBUILD 的 `pkgname`。
- 使用上游预编译产物时采用 `<name>-bin`；稳定源码发布采用 `<name>`；直接跟踪版本控制 HEAD 时采用 `<name>-git`。
- 名称不编码监控方式、资产格式或当前上游发布习惯。
- 项目不因同名 AUR 包存在与否改变自身包身份；新增前仍应检查官方仓库和现有 AUR 是否已满足需求。

### 清单与单包声明

- `registry/packages.toml` 是启用状态的唯一事实源；未登记目录不进入正式流水线。
- `package.toml` 只保存监控位置、监控类型及确有必要的资产选择信息，不复制 PKGBUILD 已有字段。
- 包名和全局 `x86_64` 目标不在 `package.toml` 中重复声明。
- 所有声明必须带 schema 版本；未知字段、未知监控类型和无效组合直接失败。

### PKGBUILD 与辅助文件

- PKGBUILD 必须是完整、标准的 Arch 配方，不能依赖未提交的运行时模板才能表达版本和来源。
- `.SRCINFO`、下载源、`src/`、`pkg/`、日志、包文件和仓库数据库均为生成物，不提交。
- `files/` 只放项目必须自行维护的小型文件；能够从固定上游版本可靠取得的内容不重复保存。
- 单包 README 只记录持续影响该包维护的特殊知识，不记录一次构建日志或当前故障。

### 能力命名空间

公共实现按职责允许形成监控、构建编排、验证和仓库发布等内部命名空间。新类型只有同时具有 schema、实现和测试后才算受支持；不得只添加名称或空类占位。

---

## 版本管理与兼容性规范

### 软件包版本

- 新上游版本更新 `pkgver` 并将 `pkgrel` 重置为 `1`。
- 上游版本不变而打包内容变化时增加 `pkgrel`。
- 完整包版本必须严格高于 pacman 数据库中的现有版本。
- 已发布的相同完整版本不可覆盖；需要重发时必须产生更高版本。
- 同一上游版本的资产默认不可变，不自动根据资产替换产生新 `pkgrel`。

### 内部配置

- schema 变化采用显式版本号并同步迁移所有现有声明。
- 项目为个人自用，不维持废弃字段或双格式读取；迁移在同一变更中完成。
- Git 是内部结构历史的唯一兼容追溯来源。

---

## AI 易踩坑的结构性边界

- `mrrss-bin` 等实例目录不是项目模板本身；不得把首个案例字段提升为所有包必填项。
- `-bin` 是包来源语义，不是 AUR 发布标记，也不是顶层分类目录。
- GitHub Releases 与 Git 仓库属于同一个 GitHub 项目，但存储角色不同；二进制不在 Git 历史中。
- 根清单只管启用状态，`package.toml` 只管自动化声明，PKGBUILD 管 Arch 打包事实；禁止建立第二份完整包元数据。
- `active/` 中的内容可以包含未实现结构和开放问题，不能覆盖长期文档或代码现实。
- 规范中预留的职责位置不要求对应目录当前存在；判断实现状态应读取代码、工作流和当前 State。
