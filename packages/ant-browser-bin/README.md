# ant-browser-bin

将 [black-ant/Ant-Browser](https://github.com/black-ant/Ant-Browser) 的 Linux amd64 发布资产重打包为原生 Arch 包。

## 持续维护知识

- 监控资产为上游 `ant-browser_<version>_amd64.deb`：1.9.0 起上游不再发布旧的 `ant-browser-linux-amd64.zip`，deb 自身已含 `/opt/ant-browser/` 应用主体、desktop、图标与 AppStream 元数据，所以只需这一个资产。
- 下载地址由 `_source_url` 提供（`my-aur prepare` 按上游真实 tag 写入），配方不推导 tag 前缀与资产名；本地文件名固定为 `ant-browser-<pkgver>.deb`。
- 应用二进制为 `ant-chrome`（Wails v2），安装到只读的 `/opt/ant-browser/`，命令入口为 `/usr/bin/ant-browser` 符号链接。
- 安装目录对普通用户只读，应用会自动把可写状态（`data/`、`config.yaml`、`chrome/` 内核）外置到 `~/.local/share/ant-browser/`。
- desktop 用本仓维护的 `ant-browser.desktop`（上游 deb 内的 `Exec`/`TryExec` 写死绝对路径）；图标（8 个 hicolor 尺寸 + pixmaps）与 AppStream 元数据取自上游 deb。
- 封装边界：装进包的 `/opt/ant-browser/` 与 `usr/share/` 下文件就是上游 deb 里的同一份文件，不改内容、不裁剪、不 strip；唯一改动是安装位置，所以指纹、代理池、备份这些功能随上游二进制原样保留。
- 运行依赖：`glib2`、`glibc`、`gtk3`、`libsoup3`、`webkit2gtk-4.1`。
- Linux 包不内置浏览器内核；内核由应用在 `~/.local/share/ant-browser/chrome/` 或外部路径维护。
