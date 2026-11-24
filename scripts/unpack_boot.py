#!/usr/bin/env python3
"""
Unpack Android boot.img (header v0-v4) tanpa tool eksternal.
Usage: python3 unpack_boot.py boot.img [output-dir]

Output: kernel (dekompres kalau gzip), kernel.orig, ramdisk.gz, dtb.img,
dtb_appended.img, boot_header.txt
"""
import os, sys, struct, gzip

BOOT_MAGIC = b"ANDROID!"
FDT_MAGIC = b"\xd0\x0d\xfe\xed"


def align(x, page):
    return (x + page - 1) // page * page


def dec(data):
    if data[:2] == b"\x1f\x8b":
        try:
            return gzip.decompress(data)
        except Exception:
            return data
    return data


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else None
    if not src:
        print("Usage: unpack_boot.py <boot.img> [out-dir]")
        raise SystemExit(1)
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(src)[0] + "_unpacked"
    os.makedirs(out, exist_ok=True)

    data = open(src, "rb").read()
    if data[:8] != BOOT_MAGIC:
        print("ERROR: bukan boot.img (magic:", data[:16].hex(), ")")
        raise SystemExit(1)

    (kernel_size, kernel_addr, ramdisk_size, ramdisk_addr, second_size,
     second_addr, tags_addr, page_size) = struct.unpack_from("<8I", data, 8)
    header_version = struct.unpack_from("<I", data, 40)[0]

    os_version = os_patch = header_size = dtb_size = dtb_addr = vendor_ramdisk_size = 0
    if header_version >= 1:
        os_version, os_patch = struct.unpack_from("<2I", data, 44)
    if header_version >= 2:
        header_size = struct.unpack_from("<I", data, 52)[0]
    if header_version >= 3:
        dtb_size, dtb_addr = struct.unpack_from("<2I", data, 56)
    if header_version >= 4:
        vendor_ramdisk_size = struct.unpack_from("<I", data, 76)[0]

    info = [
        "file=%s" % src,
        "size=%d" % len(data),
        "header_version=%d" % header_version,
        "page_size=%d" % page_size,
        "kernel_size=%d kernel_addr=0x%x" % (kernel_size, kernel_addr),
        "ramdisk_size=%d ramdisk_addr=0x%x" % (ramdisk_size, ramdisk_addr),
        "second_size=%d" % second_size,
        "os_version=0x%x os_patch=0x%x" % (os_version, os_patch),
        "header_size=%d dtb_size=%d dtb_addr=0x%x vendor_ramdisk=%d"
        % (header_size, dtb_size, dtb_addr, vendor_ramdisk_size),
    ]
    open(os.path.join(out, "boot_header.txt"), "w").write("\n".join(info) + "\n")
    print("\n".join(info))

    off = page_size
    kernel_raw = data[off:off + kernel_size]
    open(os.path.join(out, "kernel.orig"), "wb").write(kernel_raw)
    kernel = dec(kernel_raw)
    open(os.path.join(out, "kernel"), "wb").write(kernel)

    off += align(kernel_size, page_size)
    if ramdisk_size:
        open(os.path.join(out, "ramdisk.gz"), "wb").write(data[off:off + ramdisk_size])
        off += align(ramdisk_size, page_size)
    if second_size:
        off += align(second_size, page_size)
    if dtb_size:
        open(os.path.join(out, "dtb.img"), "wb").write(data[off:off + dtb_size])

    fdt = kernel.find(FDT_MAGIC)
    if fdt > 0:
        open(os.path.join(out, "dtb_appended.img"), "wb").write(kernel[fdt:])
        print("DTB appended to kernel at offset", fdt)

    ver = b""
    for line in kernel.split(b"\n"):
        if b"Linux version" in line:
            ver = line.strip()
            break
    print("\nKERNEL:", ver.decode("utf-8", "replace"))
    if b"g60a1e758fd6b" in kernel:
        print("MATCH: vermagic g60a1e758fd6b ditemukan -> ini kernel yang dibutuhkan!")
    else:
        print("WARNING: kernel ini TIDAK punya vermagic g60a1e758fd6b")
    print("\nOutput:", out)


if __name__ == "__main__":
    main()
