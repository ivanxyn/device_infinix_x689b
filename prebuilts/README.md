# Kernel prebuilt — Infinix X689B

## Status: SUDAH COCOK ✅

| Item | Nilai |
|---|---|
| Sumber | `boot_1.img` (6 Jun 2023) dari `/run/media/ivan/linux/home/ivan/platform-tools/` |
| Build kernel | `#1 SMP PREEMPT Tue Jun 6 19:34:48 CST 2023` |
| Versi | `Linux version 4.14.186-g60a1e758fd6b-dirty` |
| Vermagic modul vendor | `vermagic=4.14.186-g60a1e758fd6b-dirty SMP preempt mod_unload modversions aarch64` |
| SHA-256 (gzip) | `dd95663f2d991189c08d3a556ab40ad5189f7cc130fd5a59db2718780f54b1fe` |
| Toolchain | AOSP clang 11.0.1 (r383902), LLD 11.0.1 |
| Config | `CONFIG_MODULES=y`, `CONFIG_MODVERSIONS=y`, `CONFIG_IKCONFIG=y`, `CONFIG_BUILD_ARM64_APPENDED_DTB_IMAGE=y` |

Kernel ini dibangun **19:34:48**, berdampingan dengan vendor image yang
dibangun **19:21:32** pada tanggal yang sama (6 Jun 2023, build
`X689B-H696JKM-R-GL-230606V270`). Jadi ini pasangan yang tepat.

## Riwayat investigasi

Ada tiga kernel yang sempat ditemukan, semuanya **tidak** cocok dengan modul:

| Sumber | Versi |
|---|---|
| `prebuilts/kernel` lama (TWRP X689) | `4.14.186-gcb189c894182-dirty` (24 Feb 2023) |
| `boot.img` di `Documents/Backup` | `4.14.186-00953-g112ef0acd83d-dirty` (16 Apr 2023) |
| `boot_a` yang di-dump dari perangkat | `4.14.186-gcb189c894182-dirty` (sama dengan TWRP) |

Ketiganya sama sekali tidak cocok dengan 10 modul `.ko` vendor yang dipakai
lewat init rc (`wlan_drv_gen4m.ko`, `wmt_drv.ko`, `bt_drv.ko`, `gps_drv.ko`,
`fmradio_drv.ko`, `fpsgo.ko`, dll.).

Kandidat benar ditemukan di drive eksternal: `boot_1.img`, `boot_mod.img`, dan
`boot_pro.img` — ketiganya berisi kernel yang **byte-identik** (SHA-256 sama).
`boot_1.img` dipilih karena merupakan stock image bertanggal 6 Jun 2023.

## DTB

File `prebuilts/dtb.img` ternyata **bukan DTB**, melainkan salinan kernel Image
yang sama (hash gzip `dd95663f…` identik). Karena kernel sudah dibangun dengan
`CONFIG_BUILD_ARM64_APPENDED_DTB_IMAGE=y` dan stock `boot.img` memakai header v2
(tanpa field DTB terpisah), `BoardConfig.mk` **sengaja tidak memakai `--dtb`**.
DTBO tetap memakai `prebuilts/dtbo.img` sebagai partisi terpisah.

## Verifikasi

```sh
gzip -dc prebuilts/kernel | strings | grep -m1 'Linux version'
# Linux version 4.14.186-g60a1e758fd6b-dirty ... Tue Jun 6 19:34:48 CST 2023
```

Setelah boot, cek modul berhasil dimuat:

```sh
adb shell lsmod | grep -E 'wlan|wmt|bt_drv|gps|fmradio|fpsgo'
```
