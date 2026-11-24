#
# Copyright (C) 2024 The LineageOS Project
#
# SPDX-License-Identifier: Apache-2.0
#

DEVICE_PATH := device/infinix/x689b

# A/B
AB_OTA_UPDATER := true
AB_OTA_PARTITIONS +=
BOARD_USES_RECOVERY_AS_BOOT := true

# Architecture
TARGET_ARCH := arm64
TARGET_ARCH_VARIANT := armv8-a
TARGET_CPU_ABI := arm64-v8a
TARGET_CPU_ABI2 := 
TARGET_CPU_VARIANT := generic
TARGET_CPU_VARIANT_RUNTIME := cortex-a53

TARGET_2ND_ARCH := arm
TARGET_2ND_ARCH_VARIANT := armv7-a-neon
TARGET_2ND_CPU_ABI := armeabi-v7a
TARGET_2ND_CPU_ABI2 := armeabi
TARGET_2ND_CPU_VARIANT := generic
TARGET_2ND_CPU_VARIANT_RUNTIME := cortex-a53

# Bootloader
TARGET_BOOTLOADER_BOARD_NAME := CY-X689-H696-G
TARGET_NO_BOOTLOADER := true

# Display
TARGET_SCREEN_DENSITY := 320

# Kernel
BOARD_BOOTIMG_HEADER_VERSION := 2
BOARD_KERNEL_BASE := 0x40078000
BOARD_KERNEL_CMDLINE := bootopt=64S3,32N2,64N2 buildvariant=user
BOARD_KERNEL_PAGESIZE := 2048
BOARD_MKBOOTIMG_ARGS += --header_version $(BOARD_BOOTIMG_HEADER_VERSION)
BOARD_KERNEL_IMAGE_NAME := Image
BOARD_INCLUDE_DTB_IN_BOOTIMG := true
BOARD_KERNEL_SEPARATED_DTBO := true
TARGET_KERNEL_CONFIG := x689b_defconfig
TARGET_KERNEL_SOURCE := kernel/infinix/x689b

# Kernel - prebuilt
# Source: boot_1.img (6 Jun 2023, X689B-H696JKM-R-GL-230606V270).
# Vermagic 4.14.186-g60a1e758fd6b-dirty == the 10 vendor .ko modules.
# The stock boot.img (header v2) has no separate DTB field; the appended DTB is
# already inside the kernel Image (CONFIG_BUILD_ARM64_APPENDED_DTB_IMAGE=y), so
# do NOT pass --dtb here -- prebuilts/dtb.img is a copy of the same kernel Image,
# not a DTB blob. DTBO remains a separate partition.
TARGET_FORCE_PREBUILT_KERNEL := true
ifeq ($(TARGET_FORCE_PREBUILT_KERNEL),true)
TARGET_PREBUILT_KERNEL := $(DEVICE_PATH)/prebuilts/kernel
BOARD_INCLUDE_DTB_IN_BOOTIMG :=
BOARD_PREBUILT_DTBOIMAGE := $(DEVICE_PATH)/prebuilts/dtbo.img
BOARD_KERNEL_SEPARATED_DTBO :=
endif

# Partitions
BOARD_FLASH_BLOCK_SIZE := 131072 # (BOARD_KERNEL_PAGESIZE * 64)
BOARD_BOOTIMAGE_PARTITION_SIZE := 33554432
BOARD_DTBOIMG_PARTITION_SIZE := 8388608
# Dynamic partitions — verified from super329.img LP metadata (Android sparse,
# geometry@4096, metadata v10.2, groups main_a/main_b):
#   super block device : 6895214592 bytes (6.42 GiB)
#   group maximum_size : 6893117440 bytes (super - 2 MiB metadata)
#   logical partitions : system_ext_a 1581281280, product_a 3103428608,
#                        vendor_a 846757888, system_a 1107660800
# The old X689/TWRP values (9126805504 / 9122611200) were ~2.2 GiB too large.
BOARD_SUPER_PARTITION_SIZE := 6895214592
BOARD_SUPER_PARTITION_GROUPS := infinix_dynamic_partitions
BOARD_INFINIX_DYNAMIC_PARTITIONS_PARTITION_LIST := system system_ext product vendor
BOARD_INFINIX_DYNAMIC_PARTITIONS_SIZE := 6893117440

# Platform
TARGET_BOARD_PLATFORM := mt6765

# Properties
TARGET_SYSTEM_PROP += $(DEVICE_PATH)/system.prop
TARGET_VENDOR_PROP += $(DEVICE_PATH)/vendor.prop
TARGET_PRODUCT_PROP += $(DEVICE_PATH)/product.prop
TARGET_SYSTEM_EXT_PROP += $(DEVICE_PATH)/system_ext.prop
TARGET_ODM_PROP += $(DEVICE_PATH)/odm.prop

# Recovery
TARGET_RECOVERY_FSTAB := $(DEVICE_PATH)/rootdir/etc/fstab.mt6768
TARGET_USERIMAGES_USE_EXT4 := true
TARGET_USERIMAGES_USE_F2FS := true

# Security patch level
VENDOR_SECURITY_PATCH := 2023-06-05

# Verified Boot
BOARD_AVB_ENABLE := true
BOARD_AVB_MAKE_VBMETA_IMAGE_ARGS += --flags 3

# SEPolicy
# Vendor sepolicy already ships inside vendor_a.img; this dir is only for
# future device-specific rules (see sepolicy/README.md).
BOARD_SEPOLICY_DIRS += $(DEVICE_PATH)/sepolicy/vendor

# VINTF
# Both files below are verbatim copies of the X689B stock vendor partition
# (vendor_a.img: etc/vintf/manifest.xml and etc/vintf/compatibility_matrix.xml).
# The X689F versions declared vendor.trustonic.tee and omitted several
# Transsion/MediaTek HALs, which caused VINTF mismatches on X689B.
DEVICE_MANIFEST_FILE += $(DEVICE_PATH)/manifest.xml
DEVICE_MATRIX_FILE += $(DEVICE_PATH)/compatibility_matrix.xml

# Inherit the proprietary files
include vendor/infinix/x689b/BoardConfigVendor.mk
