# Bootstrap State

> Status: completed and archived (2026-09-28)
> 本文件记录 Bootstrap 收束时的证据快照；归档后不再作为当前实现事实源。

## 已确认

- 项目定位为个人自用、公开读取的 Arch Linux `x86_64` 二进制包仓库。
- Git 保存文本事实，固定 GitHub Release 保存包文件与 pacman 数据库。
- 包使用标准 PKGBUILD；公共自动化使用 Python + uv，Shell 只调用 Arch 工具。
- AI 可以直接提交和发布，但不能绕过 schema、测试、构建、版本与产物门禁。
- `mrrss-bin` 使用稳定 GitHub Release 的普通 Linux amd64 tar.gz，不使用 AppImage。

## 已验证完成

- 已建立公开仓库 `miracloon/my-aur-repo`，默认分支为 `main`。
- registry、schema、Python 自动化、13 项 pytest、Ruff、GitHub Actions 和 `mrrss-bin` 配方均已落地。
- Actions 运行 `36329163001` 在干净 Arch 环境中完成构建、动态依赖检查、安装与卸载验证，并发布 `mrrss-bin 1.3.38-1`。
- 固定 Release `repository-x86_64` 已提供包文件、`my-aur.db` 与 `my-aur.files`；数据库只索引当前版本。
- 首次构建失败创建包级 Issue `#1`，修复后的成功运行自动关闭该 Issue，验证了故障交接与恢复路径。
- 手工无更新运行 `36329440625` 和最终 Push 运行 `36332738771` 均成功，且正确跳过构建与发布。
- 目标客户端已配置 `[my-aur]`，pacman 与 yay 均能检索已发布包并安装 `mrrss-bin 1.3.38-1`。
- 客户端 `pacman -Qkk mrrss-bin` 报告 17 个文件、0 个变化；`/usr/bin/mrrss` 的动态库全部可解析。

## 当前进行中

- 无。Bootstrap 已完成。

## 尚未实现或验证

- 每日 schedule 与月度保活尚未等待到自然触发时间；其配置已由 Push 工作流解析，但运行证据留待日常运营积累。
- 真实第二个上游版本的升级和“当前版加上一版”资产保留尚无自然样本；算法由测试覆盖，首次真实升级后应复核 Release。
- GPG 签名按既定边界未实现，客户端当前使用 `SigLevel = Optional TrustAll`。

## 开放问题

- 无阻塞问题。

## 当前下一步

1. 由每日 Actions 持续检查上游稳定版本；
2. 首次自然升级后复核旧版本保留与客户端升级结果；
3. 新增包或引入签名时创建独立 initiative，不重新打开 Bootstrap。

## 长期治理状态

- README、长期控制文档和模块文档与已实现架构一致，无需改变已锁定的 `##` 栏目结构。
- `mrrss-bin` 的持续维护知识已经写入 `packages/mrrss-bin/README.md`。
- Bootstrap 材料整体移入 `docs/development/history/bootstrap/`，仅用于追溯。
