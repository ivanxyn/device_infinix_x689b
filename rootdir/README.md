# rootdir

`etc/*.rc` di folder ini adalah **salinan referensi** dari device tree X689F.
Mereka sengaja **TIDAK di-install** oleh `Android.bp` / `device.mk`, karena
`vendor_a.img` sudah menyediakan versi X689B yang benar di
`/vendor/etc/init/hw/` dan ikut ter-copy oleh `x689b-vendor.mk`.

Versi X689F memuat service yang tidak ada di X689B
(`spm_loader`, `remosaic_daemon`, modprobe `helloworld.ko`,
`swapon_all .../memfusion2/fstab.enableswap`) sehingga tidak dipakai.

Yang tetap di-install dari sini:

- `init.recovery.mt6768.rc` -> `/` (recovery ramdisk)
- `fstab.enableswap` dan `fstab.mt6768` -> `first_stage_ramdisk/`
  (lewat `PRODUCT_COPY_FILES` di `device.mk`)
