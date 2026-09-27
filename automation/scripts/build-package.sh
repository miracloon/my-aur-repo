#!/usr/bin/env bash
set -euo pipefail

package=${1:?package name is required}
expected=${2:?expected package filename is required}
root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)

rm -rf "${root}/dist/${package}"
mkdir -p "${root}/dist/${package}"

docker run --rm \
  -e PACKAGE="${package}" \
  -e EXPECTED="${expected}" \
  -v "${root}:/workspace" \
  archlinux:base-devel \
  bash -euo pipefail -c '
    pacman -Syu --noconfirm --needed pacman-contrib namcap git sudo
    useradd --create-home builder
    printf "builder ALL=(ALL:ALL) NOPASSWD: ALL\n" >/etc/sudoers.d/builder
    install -d -o builder -g builder "/build/${PACKAGE}"
    cp -a "/workspace/packages/${PACKAGE}/." "/build/${PACKAGE}/"
    chown -R builder:builder "/build/${PACKAGE}"

    su builder -c "cd /build/${PACKAGE} && updpkgsums"
    su builder -c "cd /build/${PACKAGE} && makepkg --syncdeps --noconfirm --cleanbuild --clean"

    package_file=$(find "/build/${PACKAGE}" -maxdepth 1 -type f -name "${EXPECTED}" -print -quit)
    if [[ -z "${package_file}" ]]; then
      echo "Expected package was not produced: ${EXPECTED}" >&2
      find "/build/${PACKAGE}" -maxdepth 1 -type f -name "*.pkg.tar.*" -print >&2
      exit 1
    fi

    namcap "/build/${PACKAGE}/PKGBUILD" | tee "/workspace/dist/${PACKAGE}/namcap-pkgbuild.txt"
    namcap "${package_file}" | tee "/workspace/dist/${PACKAGE}/namcap-package.txt"
    cp "/build/${PACKAGE}/PKGBUILD" "/workspace/packages/${PACKAGE}/PKGBUILD"
    cp "${package_file}" "/workspace/dist/${PACKAGE}/${EXPECTED}"
  '

docker run --rm \
  -e PACKAGE="${package}" \
  -e EXPECTED="${expected}" \
  -v "${root}/dist/${package}:/dist:ro" \
  -v "${root}/packages/${package}:/package:ro" \
  archlinux:base-devel \
  bash -euo pipefail -c '
    pacman -Syu --noconfirm --needed desktop-file-utils
    pacman -U --noconfirm "/dist/${EXPECTED}"
    if [[ -x /package/validate.sh ]]; then
      /package/validate.sh
    fi
    pacman -Rns --noconfirm "${PACKAGE}"
  '

printf 'Built and validated %s\n' "${expected}"
