#!/usr/bin/env bash
set -euo pipefail

test -x /usr/bin/mrrss
test -f /usr/share/applications/mrrss.desktop
test -f /usr/share/icons/hicolor/512x512/apps/mrrss.png
test -f /usr/share/licenses/mrrss-bin/LICENSE

desktop-file-validate /usr/share/applications/mrrss.desktop
if ldd /usr/bin/mrrss | grep -F 'not found'; then
  echo 'mrrss has unresolved dynamic libraries' >&2
  exit 1
fi
