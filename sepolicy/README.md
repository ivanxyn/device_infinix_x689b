# SEPolicy — Infinix X689B

## Kebijakan yang dipakai

SELinux policy untuk partisi vendor **sudah lengkap di dalam blob** `vendor_a.img`
dan ikut ter-copy oleh `x689b-vendor.mk`:

```
vendor/etc/selinux/
├── vendor_sepolicy.cil              # 13.238 baris, 1.412 tipe
├── plat_pub_versioned.cil           # 12.084 baris (public platform, versi 30)
├── plat_sepolicy_vers.txt           # 30.0
├── vendor_file_contexts             # 983 aturan
├── vendor_property_contexts
├── vendor_hwservice_contexts
├── vendor_service_contexts
├── vndservice_contexts
├── vendor_seapp_contexts
└── vendor_mac_permissions.xml
```

Karena itu **device tree ini sengaja tidak mendefinisikan aturan sepolicy sendiri**.
Tidak ada `device/*/sepolicy` dari X689F yang dipakai (repo X689F memang tidak
memilikinya), sehingga tidak ada duplikasi tipe dengan vendor policy.

Versi sepolicy vendor = **30.0**, sama dengan Board API LineageOS 18.1 (Android 11).

## Kenapa `precompiled_sepolicy` tidak ikut di-build

File `precompiled_sepolicy` beserta 3 file `*.sha256` sengaja **dikeluarkan** dari
`proprietary-files.txt` dan `x689b-vendor.mk`. File itu dikompilasi untuk system
policy stock Infinix, sehingga checksum-nya pasti tidak cocok dengan system policy
LineageOS. Android init akan tetap melakukan kompilasi ulang jika checksum beda,
tetapi dengan tidak menyertakannya kita menghindari satu sumber kegagalan dan
memaksa init selalu memakai CIL sumber yang sesuai.

CIL sumber (`vendor_sepolicy.cil` + `plat_pub_versioned.cil`) tetap dipakai.

## Catatan Trustonic

`vendor_file_contexts`, `vendor_property_contexts`, dan `vendor_hwservice_contexts`
masih memuat beberapa entri `trustonic` / `tee.tui`. Itu **bawaan BSP MediaTek stock**
dan tidak berbahaya: tidak ada file executable ataupun service Trustonic di
`vendor_a.img`, dan import/start service Trustonic sudah dihapus dari init rc.
Konteks `microtrust` dan `beanpod` juga sudah tersedia di `vendor_file_contexts`.

## Menambah aturan

Taruh aturan `.te` baru di `sepolicy/vendor/` (sudah terdaftar lewat
`BOARD_SEPOLICY_DIRS`). Contohnya jika suatu saat ada denials untuk HAL baru:

```bash
# sepolicy/vendor/hal_foo.te
allow hal_foo_default vendor_foo_data_file:dir search;
```
