# mrrss-bin

将 [DevXDojo/MrRSS](https://github.com/DevXDojo/MrRSS) 发布的 Linux amd64 普通 tar.gz 重打包为原生 Arch 包。

## 持续维护知识

- 监控资产为 `MrRSS-{version}-linux-amd64.tar.gz`，不使用 AppImage 或 portable 包；下载地址由 `_source_url` 提供，配方不推导 tag 前缀与资产名。
- 图标和 LICENSE 固定到与二进制相同的上游 tag（`_tag`），由 `updpkgsums` 随版本更新校验和。
- 上游二进制直接链接 GTK4、WebKitGTK 6.0、libsoup3、GLib、X11 和 glibc。
- 命令安装为小写 `/usr/bin/mrrss`；桌面窗口类保持上游的 `MrRSS`。
- 封装边界：装进包的可执行文件就是 tar.gz 里那份，不改内容、不裁剪；唯一变换是安装路径。
- GUI 不在无桌面的 CI 中启动；验证动态链接、desktop 文件及干净环境安装/卸载。
