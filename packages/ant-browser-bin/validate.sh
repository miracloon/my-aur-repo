#!/usr/bin/env bash
set -euo pipefail

test -L /usr/bin/ant-browser
test -x /opt/ant-browser/ant-chrome
test -x /opt/ant-browser/bin/xray
test -x /opt/ant-browser/bin/sing-box
test -f /opt/ant-browser/config.yaml
test -f /usr/share/applications/ant-browser.desktop
test -f /usr/share/icons/hicolor/512x512/apps/ant-browser.png
test -f /usr/share/pixmaps/ant-browser.png
test -f /usr/share/metainfo/ant-browser.metainfo.xml

desktop-file-validate /usr/share/applications/ant-browser.desktop
if ldd /opt/ant-browser/ant-chrome | grep -F 'not found'; then
  echo 'ant-browser has unresolved dynamic libraries' >&2
  exit 1
fi
