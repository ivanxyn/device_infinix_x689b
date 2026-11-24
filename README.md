# device/infinix/x689b — LineageOS 18.1

Device tree for **Infinix X689B / Hot 10S** (MT6768, Android 11 vendor,
build `X689B-H696JKM-R-GL-230606V270`).

- Vendor blobs: `ivanxyn/vendor_infinix_x689b_los`
- Original blob archive: `ivanxyn/vendor_infinix_x689b`

## Build

See [BUILD.md](BUILD.md). Quick start:

```bash
repo init -u https://github.com/LineageOS/android.git -b lineage-18.1 --depth=1
mkdir -p .repo/local_manifests
cp device/infinix/x689b/local_manifest.xml .repo/local_manifests/x689b.xml
repo sync -c -j2
source build/envsetup.sh
lunch lineage_x689b-userdebug
mka bacon -j2
```

Both repos are **private** — the PAT used for `repo sync` must have `repo` scope
(or use an SSH key).

## SPDX

SPDX-License-Identifier: Apache-2.0
