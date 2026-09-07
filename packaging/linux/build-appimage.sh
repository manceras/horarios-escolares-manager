#!/usr/bin/env bash
# Build the Linux AppImage from an existing PyInstaller bundle in dist/Horarios.
#
# An AppImage rather than a .deb or an .rpm: one file, no package manager, no
# root, and it runs on any distribution recent enough to matter. That is the
# same deal the Windows installer offers, which is the point.
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
BUNDLE="$ROOT/dist/Horarios"
APPDIR="$ROOT/build/AppDir"
VERSION=${1:?usage: build-appimage.sh VERSION}

[ -d "$BUNDLE" ] || { echo "Missing $BUNDLE -- run 'make installer' first" >&2; exit 1; }

rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin" "$APPDIR/usr/share/icons/hicolor/256x256/apps"
cp -a "$BUNDLE/." "$APPDIR/usr/bin/"
cp "$ROOT/packaging/linux/AppRun" "$APPDIR/AppRun"
chmod +x "$APPDIR/AppRun"
cp "$ROOT/packaging/linux/horarios.desktop" "$APPDIR/horarios.desktop"
cp "$ROOT/packaging/horarios.png" "$APPDIR/horarios.png"
cp "$ROOT/packaging/horarios.png" "$APPDIR/.DirIcon"
cp "$ROOT/packaging/horarios.png" "$APPDIR/usr/share/icons/hicolor/256x256/apps/horarios.png"

TOOL=${APPIMAGETOOL:-appimagetool}
if ! command -v "$TOOL" >/dev/null; then
  TOOL="$ROOT/build/appimagetool"
  if [ ! -x "$TOOL" ]; then
    curl -fsSL -o "$TOOL" \
      "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x "$TOOL"
  fi
fi

mkdir -p "$ROOT/dist"
# --appimage-extract-and-run: CI containers have no FUSE to mount with.
ARCH=x86_64 "$TOOL" --appimage-extract-and-run \
  "$APPDIR" "$ROOT/dist/Horarios-$VERSION-x86_64.AppImage"
