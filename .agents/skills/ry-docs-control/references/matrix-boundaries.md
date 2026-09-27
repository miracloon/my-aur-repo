# 文档矩阵定义与边界

> 纯查询手册——在需要确认"某信息应归入哪份文档"时查阅。

---

## 文档矩阵

核心矩阵是用户明确选择的统一治理格式，不按项目原有治理拓扑自由变形：`AGENTS.md`、`CLAUDE.md`、`docs/INTENT.md`、`docs/WORKFLOW.md` 和 `docs/SPEC.md` 必须建立；`docs/modules/` 按内容需要展开。`docs/ARCHITECTURE.md` 仅在全局逻辑架构形成独立职责时加入。

| 文档 | 核心职责 | 回答什么 | 不回答什么 |
|------|---------|---------|-----------|
| `AGENTS.md` | AI 入口与导航 | 先看什么、先遵循什么 | 完整项目说明、详细结构规范 |
| `CLAUDE.md` | Claude 专属补丁 | Claude 特有约束 | 项目通用规则 |
| `docs/INTENT.md` | 意图与取舍 | 为什么存在、边界在哪、为什么这样取舍 | 操作步骤、结构细目 |
| `docs/ARCHITECTURE.md`（按需） | 全局逻辑架构 | 系统由哪些逻辑组件构成，职责、依赖、接口、数据所有权和跨模块不变量是什么 | 项目目标、目录树、完整运行时序、模块内部设计 |
| `docs/WORKFLOW.md` | 运转拓扑 | 如何运转、上下游如何衔接 | 命令教程、详细结构规范 |
| `docs/SPEC.md` | 结构与规范 | 如何被组织、目录与模块边界、维护规则 | 设计初心、运转拓扑 |
| `docs/modules/{name}.md` | 模块统一文档 | 某模块的意图 + 结构 + 运转；形成独立加载或维护边界时拆出，10 行作为默认判断信号 | 项目级信息 |

### README 的定位

项目根目录的 `README.md` **不属于控制面文档矩阵**。它面向人类读者（用户、贡献者），侧重项目简介、特色、使用方式和操作说明。
- **初始化期间**：README 是高价值信息源，应主动读取并从中提取有价值的信息归入控制文档
- **初始化完成后**：AI 不主动维护 README，仅在用户明确要求时才读取或修改
- **发生冲突时**：README 不自动覆盖治理正文，治理正文也不能否认可观察的实际行为；按 [权威来源与防漂移规则](anti-drift-rules.md) 暴露并解决冲突

---

## 默认读取链路

```text
通用入口：AGENTS.md → docs/INTENT.md → docs/ARCHITECTURE.md（若存在）→ docs/WORKFLOW.md → docs/SPEC.md
Claude 环境：CLAUDE.md 自动加载 → 引用 AGENTS.md → 进入同一主链
```

---

## 归属判断速查

当你不确定某个信息应写入哪份文档时：

| 这个信息主要回答 | → 归入 |
|----------------|--------|
| "为什么做 / 为什么不做 / 为什么这样选" | INTENT.md |
| “系统由哪些逻辑组件构成 / 组件职责与依赖是什么 / 数据由谁拥有” | ARCHITECTURE.md（仅已建立时；否则分别归入 INTENT、WORKFLOW、SPEC） |
| "在整体中处于什么环节 / 影响什么上下游" | WORKFLOW.md |
| "怎么组织 / 目录规则 / 命名规范" | SPEC.md |
| "AI 进入时先做什么 / 硬性技术约束" | AGENTS.md |
| "某个模块的完整设计细节" | docs/modules/{name}.md |
| "怎么安装 / 怎么使用 / 面向用户的操作说明" | README.md（不归控制面文档管） |

---

## 边界澄清

| 容易混淆的对 | 区分方式 |
|-------------|---------|
| README vs WORKFLOW | README 面向用户写"怎么操作"；WORKFLOW 面向 AI 写"操作在整体运转中的位置" |
| README vs INTENT | README 面向用户讲"这是什么、有什么特色"；INTENT 面向 AI 讲"为什么存在、边界与取舍" |
| AGENTS vs INTENT | AGENTS 做入口导航（极简摘要）；INTENT 做完整意图解释 |
| INTENT vs WORKFLOW | INTENT 解释"为什么"；WORKFLOW 解释"如何运转" |
| INTENT vs ARCHITECTURE | INTENT 记录架构驱动和重大取舍的理由；ARCHITECTURE 记录当前成立的全局逻辑组件模型与不变量 |
| ARCHITECTURE vs SPEC | ARCHITECTURE 描述逻辑组件、职责和依赖；SPEC 描述它们在仓库中的物理组织与维护规范 |
| ARCHITECTURE vs WORKFLOW | ARCHITECTURE 描述相对稳定的组件关系；WORKFLOW 描述请求、数据和产物随时间怎样流转 |
| WORKFLOW vs SPEC | WORKFLOW 回答"如何运转"；SPEC 回答"如何组织" |
| 主文档 vs 模块文档 | 主文档放项目级 + 模块摘要索引；模块文档放单模块完整细节 |
