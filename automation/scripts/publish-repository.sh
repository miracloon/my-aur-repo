#!/usr/bin/env bash
set -euo pipefail

artifacts=${1:?downloaded artifact directory is required}
root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
tag=repository-x86_64
work="${root}/repo-work"

mapfile -t package_files < <(find "${artifacts}/dist" -type f -name '*.pkg.tar.zst' -print 2>/dev/null | sort)
if (( ${#package_files[@]} == 0 )); then
  echo 'No successful package artifacts to publish.'
  exit 0
fi

mapfile -t package_names < <(find "${artifacts}/packages" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort)
for package in "${package_names[@]}"; do
  install -Dm644 "${artifacts}/packages/${package}/PKGBUILD" \
    "${root}/packages/${package}/PKGBUILD"
done

git config user.name 'github-actions[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
git add packages/*/PKGBUILD
if ! git diff --cached --quiet; then
  git commit -m 'chore(packages): update upstream versions'
  git pull --rebase origin main
  git push origin HEAD:main
fi

if ! gh release view "${tag}" >/dev/null 2>&1; then
  gh release create "${tag}" \
    --title 'my-aur x86_64 repository' \
    --notes 'pacman repository assets managed by GitHub Actions.'
fi

# Package files must exist before the database can reference them.
for file in "${package_files[@]}"; do
  gh release upload "${tag}" "${file}"
done

rm -rf "${work}"
mkdir -p "${work}/database" "${work}/publish"
if gh release download "${tag}" -p 'my-aur.db' -p 'my-aur.files' -D "${work}/database"; then
  mv "${work}/database/my-aur.db" "${work}/database/my-aur.db.tar.gz"
  mv "${work}/database/my-aur.files" "${work}/database/my-aur.files.tar.gz"
  ln -s my-aur.db.tar.gz "${work}/database/my-aur.db"
  ln -s my-aur.files.tar.gz "${work}/database/my-aur.files"
fi

for file in "${package_files[@]}"; do
  cp "${file}" "${work}/database/"
done

docker run --rm \
  -v "${work}/database:/repo" \
  archlinux:base-devel \
  bash -euo pipefail -c '
    cd /repo
    mapfile -t packages < <(find . -maxdepth 1 -type f -name "*.pkg.tar.zst" -print | sort)
    repo-add -R my-aur.db.tar.gz "${packages[@]}"
  '

cp -L "${work}/database/my-aur.db" "${work}/publish/my-aur.db"
cp -L "${work}/database/my-aur.files" "${work}/publish/my-aur.files"
gh release upload "${tag}" \
  "${work}/publish/my-aur.db" \
  "${work}/publish/my-aur.files" \
  --clobber

for package in "${package_names[@]}"; do
  uv run my-aur close-failure --package "${package}"
done
uv run my-aur prune --keep 2

echo 'Repository publication completed.'
