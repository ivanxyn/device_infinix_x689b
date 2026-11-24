#!/bin/sh
# Ekstrak kernel + ramdisk dari boot.img stock X689B (build 230606V270).
# Butuh magiskboot (dari Magisk) ATAU unpack_bootimg (dari AOSP).
#
# Usage:
#   sh extract_kernel_from_boot.sh /path/ke/boot.img /path/output/
set -e
BOOT="$1"
OUT="${2:-./boot_extracted}"

if [ -z "$BOOT" ]; then
  echo "Usage: $0 <boot.img> [output-dir]"
  exit 1
fi
mkdir -p "$OUT"

if command -v magiskboot >/dev/null 2>&1; then
  cp "$BOOT" "$OUT/boot.img"
  (cd "$OUT" && magiskboot unpack boot.img)
elif command -v unpack_bootimg >/dev/null 2>&1; then
  unpack_bootimg --boot_img "$BOOT" --out "$OUT"
else
  echo "ERROR: pasang magiskboot atau unpack_bootimg dulu."
  exit 1
fi

echo "=== hasil ==="
ls -lh "$OUT" | head -20
echo
echo "=== cek versi kernel ==="
K=$(find "$OUT" -maxdepth 1 -type f \( -name 'kernel' -o -name 'kernel.gz' -o -name 'Image' \) | head -1)
if [ -n "$K" ]; then
  case "$K" in
    *.gz) gzip -dc "$K" | strings | grep -m1 'Linux version' ;;
    *) strings "$K" | grep -m1 'Linux version' ;;
  esac
  echo
  echo "Harus: 4.14.186-g60a1e758fd6b-dirty ..."
  echo "Kalau iya, copy kernel ini ke device/infinix/x689b/prebuilts/kernel"
fi
