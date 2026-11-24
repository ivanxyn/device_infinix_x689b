# Porting LineageOS 18.1 ke Infinix X689B (Hot 10S)

Scaffold ini dibuat dari:

- **Device tree:** turunan `LazyCat2/device_infinix_x689f` (LineageOS, MT6768/MT6765 keluarga yang sama), disesuaikan untuk X689B.
- **Kernel:** prebuilt `kernel` + `dtb.img` dari `Nomercy992/device_infinix_X689` (TWRP tree X689), diambil dari boot image stock.
- **Vendor blob:** 1.874 file hasil ekstraksi `vendor_a.img` (SHA-256 `a7004095…eaa63`), build `X689B-H696JKM-R-GL-230606V270`, Android 11, patch 2023-06-05.

## Kenapa LineageOS 18.1

Vendor Anda adalah **Android 11 / SDK 30** dengan VINTF `target-level="5"`. Itu cocok persis dengan LineageOS 18.1. LineageOS 19+ (Android 12) butuh target-level 6 dan adaptasi HIDL→AIDL yang jauh lebih berat.

## Keterbatasan mesin ini

| Kebutuhan | Rekomendasi | Mesin Anda |
|---|---|---|
| RAM | 16 GB | 5,6 GB (+ swap 10 GB) |
| CPU | 8+ core | 4 core |
| Disk | 250 GB | 240 GB free |

Build masih mungkin dengan ` -j2 ` dan swap, tapi **lama (berjam-jam)**. Pertimbangkan memakai mesin/build server yang lebih besar atau GitHub Actions/self-hosted runner.

## Langkah 1 — Inisialisasi source LineageOS 18.1

```bash
mkdir -p ~/android/lineage && cd ~/android/lineage
repo init -u https://github.com/LineageOS/android.git -b lineage-18.1 --depth=1
mkdir -p .repo/local_manifests
cp /tmp/opencode/port/x689b-port/local_manifest.xml .repo/local_manifests/x689b.xml
repo sync -c -j2 --fail-fast --force-sync
```

`local_manifest.xml` di scaffold ini masih mengarah ke nama repo GitHub placeholder. Kalau belum di-push, lebih mudah pakai symlink (langkah 2 alternatif).

## Langkah 2 — Pasang device tree + vendor

**Opsi A — symlink (disarankan untuk percobaan lokal):**

```bash
cd ~/android/lineage
mkdir -p device/infinix vendor/infinix
ln -s /tmp/opencode/port/x689b-port/device/infinix/x689b device/infinix/x689b
ln -s /tmp/opencode/port/x689b-port/vendor/infinix/x689b vendor/infinix/x689b
```

**Opsi B — push ke GitHub dulu**, lalu ubah `name=` di `local_manifest.xml` sesuai repo Anda, dan `repo sync` ulang.

## Langkah 3 — Build

```bash
cd ~/android/lineage
source build/envsetup.sh
export USE_CCACHE=1
ccache -M 30G
lunch lineage_x689b-userdebug
mka bacon -j2
```

Output: `out/target/product/x689b/lineage-18.1-*-UNOFFICIAL-x689b.zip`

## Langkah 4 — Flash

Butuh recovery (TWRP untuk X689 sudah ada di `Nomercy992/device_infinix_X689`).

```
adb sideload lineage-18.1-...-x689b.zip
```

Atau via fastboot/flashing tool sesuai partisi dynamic (super) X689B.

## yang sudah disesuaikan untuk X689B

- `PRODUCT_DEVICE := x689b`, `PRODUCT_NAME := lineage_x689b`
- `BUILD_FINGERPRINT` dan `PRIVATE_BUILD_DESC` diambil dari `vendor_a.img`
- `VENDOR_SECURITY_PATCH := 2023-06-05`
- `TARGET_BOOTLOADER_BOARD_NAME := CY-X689-H696-G` (dari BoardConfig TWRP X689)
- `include vendor/infinix/x689b/BoardConfigVendor.mk`
- `PRODUCT_COPY_FILES` untuk 1.874 blob langsung dari `vendor_a.img` (file `x689b-vendor.mk`)
- 2 symlink absolut (`vulkan.mt6768.so` -> `/vendor/lib*/egl/libGLES_mali.so`)
  diubah jadi symlink relatif, supaya tidak gagal saat build di host
- Kernel + DTB prebuilt disalin ke `device/infinix/x689b/prebuilts/`

## Perbaikan VINTF yang SUDAH dilakukan

Manifest X689F awalnya **menimpa** `vendor/etc/vintf/manifest.xml` dari blob saat build
(karena `DEVICE_MANIFEST_FILE`). Sekarang sudah diganti dengan salinan verbatim dari
`vendor_a.img`, dan `DEVICE_MATRIX_FILE` juga ditambahkan.

| X689F (lama) | X689B (aktual) |
|---|---|
| `vendor.trustonic.tee` + `tee.tui` (`@1.1::ITee`, `@1.0::ITui`) | **tidak ada** — X689B pakai MicroTrust/beanpod |
| `IMtkRadioEx @2.2` (16 instance) | `IMtkRadioEx @2.0` (16 instance) |
| – | `ISecureElement/SIM1`, `/SIM2` (@1.2) |
| – | `IFpsPolicyService`, `IISPModule`, `INwkOpt` |
| – | `android.hardware.renderscript @1.0::IDevice` |

Ikutan diperbaiki supaya tidak bertentangan dengan manifest:

- `manifest.xml` <- `vendor_a.img:/etc/vintf/manifest.xml` (46 HAL, 104 fqname)
- `compatibility_matrix.xml` <- `vendor_a.img:/etc/vintf/compatibility_matrix.xml`
- init rc: `init.mt6765*.rc` -> `init.mt6768*.rc`; `fstab.mt6765` -> `fstab.mt6768`
- hapus import service Trustonic/Trustkernel dan `start vendor.keymaster-*-trustonic*`
  (X689B hanya punya `vendor.keymaster-4-0-beanpod`)
- `vendor.prop`: `kmsetkey`/`gatekeeper` -> `beanpod`, `paytrigger` -> `microtrust`,
  `mtk_trustonic_tee_support` -> `mtk_microtrust_tee_support`

Cadangan manifest lama: `manifest.xml.x689f.bak`.

## Yang PALING MUNGKIN perlu diperbaiki saat bring-up

1. **VINTF fragments.** 21 file `vendor/etc/vintf/manifest/*.xml` dari blob sudah ikut
   ter-copy lewat `PRODUCT_COPY_FILES`. Cek setelah boot dengan
   `adb shell dumpsys hwservicemanager -l`.
2. **`TARGET_BOARD_PLATFORM`.** Sengaja **dibiarkan `mt6765`** supaya memakai common tree
   `device/mediatek/mt6765` yang tersedia di LOS 18.1. Nama file init rc sudah diganti
   ke `mt6768` sesuai vendor. Kalau init gagal, coba ganti platform ke `mt6768` dan
   sesuaikan common tree.
3. **SEPolicy.** Sudah ditangani: vendor X689B membawa policy lengkap
   (`vendor_sepolicy.cil`, 1.412 tipe; `vendor_file_contexts`, 983 aturan; versi 30.0),
   dan device tree tidak punya aturan X689F yang bentrok. Lihat
   `device/infinix/x689b/sepolicy/README.md`. `precompiled_sepolicy` + 3 file `.sha256`
   sengaja tidak ikut di-build supaya init selalu kompilasi ulang dengan platform
   policy LineageOS. Tempat aturan tambahan: `sepolicy/vendor/` (sudah terdaftar di
   `BOARD_SEPOLICY_DIRS`). Kalau masih ada `avc: denied` setelah boot, tambahkan
   aturan di situ lalu build ulang.
4. **Fstab / dynamic partitions.** Sudah disamakan dengan `vendor_a.img` dan
   **diverifikasi dari `super329.img`** (LP metadata v10.2):
   - `rootdir/etc/fstab.mt6768` = salinan verbatim fstab stock (system,
     system_ext, vendor, product sebagai partisi logical/ext4; /data f2fs;
     /metadata, /tranfs, protect1/2, nvdata, nvcfg, persist).
   - `fstab.enableswap` diganti ke `zramsize=55%` sesuai stock.
   - `TARGET_RECOVERY_FSTAB` sekarang menunjuk ke fstab lengkap.
   - Ukuran `super` **6.895.214.592** (6,42 GiB) dan group **6.893.117.440**,
     dari metadata asli — nilai TWRP lama (9,1 GB) ternyata ~2,2 GiB terlalu
     besar. Partisi: system 1,03 GiB, system_ext 1,47 GiB, product 2,89 GiB,
     vendor 0,79 GiB (di `super329.img`; `vendor_a.img` Anda 1,25 GB, jadi
     berasal dari build sedikit beda).
   - Skrip parser: `scripts/parse_super_sparse.py`.
5. **Audio / kamera / IMS.** Sudah disamakan: config audio (audio_policy,
   audio_param, A2DP/USB/BT), HAL kamera 2.6 + bgservice/isphal, dan IMS/VoLTE
   semuanya berasal dari `vendor_a.img` dan ikut ter-copy. Device tree tidak
   punya `configs/` X689F. 21 nilai prop yang ditimpa dari X689F sudah
   dikembalikan ke nilai stock X689B (termasuk `MT6768`, `dsds`, versi build
   `X689B-H696JKM-R-GL-230606V270`, dan `camera3.zsl.default=140`).
   Lihat `device/infinix/x689b/CONFIGS.md`. Init rc X689F yang memanggil binary
   tidak ada (`remosaic_daemon`, `spm_loader`, `helloworld.ko`) sudah tidak
   di-install — vendor blobs yang jadi sumber tunggal.
6. **Kernel prebuilt — SELESAI.** Kernel dari `boot_1.img` (6 Jun 2023) sudah
   dipasang. Vermagic `4.14.186-g60a1e758fd6b-dirty` cocok persis dengan ke-10
   modul `.ko` vendor (dibangun 19:34, vendor 19:21 pada hari yang sama). DTB
   sudah termasuk di dalam Image (`CONFIG_BUILD_ARM64_APPENDED_DTB_IMAGE=y`),
   jadi `--dtb` sengaja tidak dipakai. Detail di
   `device/infinix/x689b/prebuilts/README.md`.
   `4.14.186-gcb189c894182-dirty` (Feb 2023), sedangkan 10 modul `.ko` di
   `vendor_a.img` adalah `4.14.186-g60a1e758fd6b-dirty` (Jun 2023). Karena
   `CONFIG_MODULES=y` + `CONFIG_MODVERSIONS=y`, modul Wi-Fi/BT/GPS/FM/fingerprint
   akan ditolak. **Wajib** ganti `prebuilts/kernel` + `dtb.img` dengan kernel dari
   `boot.img` stock build `230606V270`. Lihat `device/infinix/x689b/prebuilts/README.md`
   dan `scripts/extract_kernel_from_boot.sh`. `scripts/patch_vermagic.py` only a
   provisional workaround (CRC symbol masih bisa gagal).

## Catatan legal

Blob proprietary tetap milik Infinix/MediaTek. Kernel source resmi X689 **belum pernah dirilis** — isu permintaan source code masih terbuka di `OpenSource-Infinix/android#2` sejak 2021. Karena itu porting ini memakai kernel prebuilt dari firmware, bukan source yang bisa dikompilasi ulang.
