#!/bin/sh
# Jalankan dengan perangkat X689B terhubung (adb root disarankan):
#   sh check_partitions.sh
# Output dipakai untuk memverifikasi nilai dynamic partition di BoardConfig.mk.

echo "=== root ==="
adb root >/dev/null 2>&1 || true
adb remount >/dev/null 2>&1 || true

echo "=== slot aktif ==="
adb shell getprop ro.boot.slot_suffix

echo "=== partisi by-name (potongan) ==="
adb shell ls -l /dev/block/by-name/ 2>/dev/null | grep -E 'super|system|vendor|product|vbmeta|boot|dtbo|userdata|metadata' | head -30

echo "=== super layout (lpdump) ==="
adb shell lpdump /dev/block/by-name/super 2>/dev/null | head -60 || \
adb shell lpdump /dev/block/bootdevice/by-name/super 2>/dev/null | head -60 || \
echo "lpdump tidak tersedia di perangkat"

echo "=== fstab aktif ==="
adb shell cat /vendor/etc/fstab.mt6768 2>/dev/null | grep -v '^#' | grep -v '^$' | head -15

echo "=== partisi ter-mount ==="
adb shell df -h 2>/dev/null | grep -E '/system|/vendor|/product|/system_ext|/data|/metadata' | head -15
