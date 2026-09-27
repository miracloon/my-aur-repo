# ant-browser-bin

将 [black-ant/Ant-Browser](https://github.com/black-ant/Ant-Browser) 的 Linux amd64 发布资产重打包为原生 Arch 包。

## 再分发与许可

上游仓库当前未附带独立的 `LICENSE` 文件。本包通过公开 Release 再分发，依据是上游作者对本项目的明确授权（由维护者确认，项目为个人自用）。上游后续补充正式许可证时，应据此更新本说明与 PKGBUILD 的 `license` 字段。

## 持续维护知识

- 上游稳定 Release 资产为 `ant-browser-linux-amd64.zip`，内含 `AntBrowser-<version>-linux-amd64.tar.gz` 与 `ant-browser_<version>_amd64.deb`。
- 上游 tag 使用大写 `V` 前缀（如 `V1.8.0`），PKGBUILD 的下载 URL 固定写为 `V${pkgver}`。
- 应用二进制为 `ant-chrome`（Wails v2），安装到只读的 `/opt/ant-browser/`，命令入口为 `/usr/bin/ant-browser` 符号链接。
- 安装目录对普通用户只读，应用会自动把可写状态（`data/`、`config.yaml`、`chrome/` 内核）外置到 `~/.local/share/ant-browser/`。
- 图标（8 个 hicolor 尺寸 + pixmaps）、desktop 与 AppStream 元数据取自上游 deb。
- 运行依赖：`glib2`、`glibc`、`gtk3`、`libsoup3`、`webkit2gtk-4.1`。
- Linux 包不内置浏览器内核；内核由应用在 `~/.local/share/ant-browser/chrome/` 或外部路径维护。
