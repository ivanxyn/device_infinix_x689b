#!/usr/bin/env python3
"""
Workaround SEMENTARA: samakan string vermagic kernel prebuilt dengan modul .ko
vendor X689B. Panjang string identik (28 byte), jadi layout biner tidak berubah.

PERINGATAN: kernel ini punya CONFIG_MODVERSIONS=y. Kalau CRC simbol berbeda
antara build kernel `cb189c894182` dan `g60a1e758fd6b`, modul masih akan ditolak
dengan "disagrees about version of symbol ...". Solusi benar ada di
prebuilts/README.md: pakai kernel dari boot.img stock build 230606V270.

Usage:
    python3 patch_vermagic.py kernel.gz output_kernel.gz
"""
import gzip, sys

OLD = b"4.14.186-gcb189c894182-dirty"
NEW = b"4.14.186-g60a1e758fd6b-dirty"

src = sys.argv[1] if len(sys.argv) > 1 else "prebuilts/kernel"
dst = sys.argv[2] if len(sys.argv) > 2 else "kernel-patched.gz"

with gzip.open(src, "rb") as f:
    img = f.read()

n = img.count(OLD)
if n == 0:
    print("old version string not found; kernel may already be patched")
    raise SystemExit(1)
if len(OLD) != len(NEW):
    print("length mismatch, refusing")
    raise SystemExit(1)

img = img.replace(OLD, NEW)
with open(dst, "wb") as f:
    gz = gzip.GzipFile(fileobj=f, mode="wb", compresslevel=9, mtime=0)
    gz.write(img)
    gz.close()
print("patched %d occurrences -> %s" % (n, dst))
