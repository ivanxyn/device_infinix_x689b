# Build ROM AOSP-based untuk Infinix X689B (varian ROM-agnostik)

Cabang `aosp-generic` ini **tidak bergantung pada LineageOS**. Satu-satunya
yang masih tertulis "LineageOS" adalah header copyright asli (Apache-2.0,
wajib dipertahankan) dan dokumen historis di `sepolicy/README.md`.

## Yang dipakai apa adanya

- Vendor blobs dari `vendor_a.img` (Android 11 / SDK 30 / VINTF target-level 5)
- Kernel `4.14.186-g60a1e758fd6b-dirty` dari `boot_1.img`
- Fstab, partisi dynamic (super 6,42 GiB), VINTF, SEPolicy, prop hardware
- `x689b-vendor.mk` + `proprietary-files.txt` (standar `PRODUCT_COPY_FILES`)

## Yang perlu Anda ubah untuk ROM tertentu

1. `aosp_x689b.mk` — ganti `PRODUCT_NAME` dan inheritance product ke ROM Anda
   (mis. `vendor/crdroid/config/common_full_phone.mk`).
2. `AndroidProducts.mk` — sesuaikan nama lunch.
3. `local_manifest.xml` — ganti URL/branch manifest ke ROM Anda.
4. `device.mk` — hapus/tambah package khas ROM bila perlu.

Bagian hardware (board, kernel, fstab, VINTF, prop) **jangan** diubah.

## Contoh: AOSP 11 vanilla

```bash
mkdir -p ~/android/aosp && cd ~/android/aosp
repo init -u https://android.googlesource.com/platform/manifest \
  -b android-11.0.0_r48 --depth=1
mkdir -p .repo/local_manifests
cp device/infinix/x689b/local_manifest.xml .repo/local_manifests/x689b.xml
# repo sync butuh kredensial karena repo vendor bersifat private
repo sync -c -j2
source build/envsetup.sh
lunch aosp_x689b-userdebug
mka bacon -j2
```

Output: `out/target/product/x689b/aosp_x689b-*.zip`.

## Catatan Android 12+

Vendor Android 11 memakai HIDL + VINTF `target-level=5`. ROM Android 12/13
masih bisa memakainya lewat compatibility mapping, tetapi:
- `ro.vendor.build.version.sdk=30` tetap, jangan dipaksa 31/33;
- VINTF & SEPolicy perlu diaudit ulang bila ada kegagalan `vintf_object`;
- ROM A14+ umumnya sudah menghapus banyak HIDL — tidak disarankan.

## Verifikasi setelah boot

```sh
adb shell getprop ro.vendor.mediatek.platform     # MT6768
adb shell lsmod | grep -E 'wlan|wmt|bt_drv|gps'  # modul harus termuat
adb shell dumpsys hwservicemanager -l | grep -E 'camera|audio|radio'
```
