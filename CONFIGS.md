# Audio / Kamera / IMS — Infinix X689B

Semua konfigurasi audio, kamera, dan IMS **berasal dari partisi vendor X689B**
dan ikut ter-copy oleh `vendor/infinix/x689b/x689b-vendor.mk`. Device tree ini
**tidak punya folder `configs/`**, sehingga tidak ada config X689F yang dipakai.

## Audio

- `etc/audio_policy_configuration.xml`, `audio_policy.conf`, `audio_policy_volumes.xml`
- `etc/audio_device.xml`, `audio_effects.xml`, `audio_em.xml`
- `etc/a2dp_audio_policy_configuration.xml`, `bluetooth_audio_policy_configuration.xml`,
  `usb_audio_policy_configuration.xml`, `r_submix_audio_policy_configuration.xml`
- `etc/audio_param/` dan `etc/audio_param_ce/` — ratusan file tuning MediaTek
  (Playback/Record/Speech/VoIP, DRC, DTS, VolumeGainMap, dll.)
- `lib64/hw/android.hardware.audio@6.0-impl-mediatek.so` dan `lib/hw/...`

## Kamera

- HAL: `lib64/hw/android.hardware.camera.provider@2.6-impl-mediatek.so`
- `vendor.mediatek.hardware.camera.bgservice@1.1-impl.so`
- `vendor.mediatek.hardware.camera.isphal@1.0-impl.so`
- `etc/permissions/android.hardware.camera.*.xml`
- `etc/init/camerahalserver.rc`
- Sensor: 48 MP + 2 MP + 2 MP, front 8 MP (MT6768 / X689B)

Service X689F `remosaic_daemon` dan node `/dev/MAINAF`, `/dev/SUBAF`, dll. masih
muncul di salinan referensi `rootdir/etc/init.project.rc`, tetapi **file itu tidak
lagi di-install** (lihat `rootdir/README.md`) karena binary `remosaic_daemon` dan
service `spm_loader` tidak ada di X689B.

## IMS / VoLTE

- `persist.vendor.ims_support=1`, `persist.vendor.volte_support=1`,
  `persist.vendor.mims_support=2`, `persist.vendor.mtk_dynamic_ims_switch=1`
- `etc/init/init.volte_{imcb,imsm_93,md_status,stack,ua}.rc`
- `lib64/libvolte_*.so`, `bin/volte_*`
- HAL RIL `android.hardware.radio@1.2` dengan instance `imsAospSlot1/2`,
  `mtkIms*`, dan `vendor.mediatek.hardware.mtkradioex@2.0`

## Props yang diperbaiki

Device tree X689F sebelumnya menimpa 21 nilai stock X689B lewat `TARGET_*_PROP`.
Semua sudah disamakan dengan `vendor_a.img`:

| Prop | X689F | X689B |
|---|---|---|
| `ro.vendor.mediatek.platform` | MT6765 | **MT6768** |
| `ro.vendor.tran.version.release` | X689F-…231012V857 | **X689B-H696JKM-R-GL-230606V270** |
| `ro.product.tran.version.release` | X689F-…231012V1295 | **X689B-H696JKM-R-GL-230606V270** |
| `ro.tecno.manual_guide_support` | Infinix-X689F | **Infinix-X689B** |
| `persist.radio.multisim.config` | tsts | **dsds** |
| `persist.vendor.radio.msimmode` | tsts | **dsds** |
| `ro.vendor.radio.max.multisim` | tsts | **dsds** |
| `telephony.active_modems.max_count` | 3 | **2** |
| `ro.vendor.camera3.zsl.default` | 130 | **140** |
| `persist.vendor.radio.mtk_dsbp_support` | 1 | **2** |
| `persist.vendor.swapfile_enable` | true | **false** |
| `ro.lmk.psi_complete_stall_ms` | 70 | **150** |
| `ro.surface_flinger.*phase_offset_ns` | (kosong) | **8300000** |
| `ro.vendor.midtest.*` (3 prop) | nilai X689F | nilai X689B |
| `ro.vendor.mtk_md1_support` | 12 | **9** |
| `vendor.dalvik.vm.dex2oat-threads-ext` | 3 | **2** |
| `vendor.mtk.vdec.waitkeyframeforplay` | 11 | **9** |

Hasil `cmp_props.py`: **0 konflik** tersisa.

## Verifikasi setelah boot

```sh
adb shell getprop ro.vendor.mediatek.platform      # MT6768
adb shell getprop persist.vendor.ims_support        # 1
adb shell getprop persist.vendor.volte_support      # 1
adb shell dumpsys media.camera | head -40
adb shell dumpsys audio | head -40
adb shell dumpsys hwservicemanager -l | grep -E 'camera|audio|radio|ims'
```
