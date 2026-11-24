#
# Copyright (C) 2024 The LineageOS Project
#
# SPDX-License-Identifier: Apache-2.0
#

# Inherit from those products. Most specific first.
$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/full_base_telephony.mk)

# Inherit some common Lineage stuff.
$(call inherit-product, vendor/lineage/config/common_full_phone.mk)

# Inherit from x689b device
$(call inherit-product, device/infinix/x689b/device.mk)

PRODUCT_DEVICE := x689b
PRODUCT_NAME := lineage_x689b
PRODUCT_BRAND := Infinix
PRODUCT_MANUFACTURER := infinix

PRODUCT_GMS_CLIENTID_BASE := android-transsion

PRODUCT_BUILD_PROP_OVERRIDES += \
    PRIVATE_BUILD_DESC="X689B-H696JKM-R-GL-230606V270 release-keys"

BUILD_FINGERPRINT := Infinix/X689B-GL/Infinix-X689B:11/RP1A.200720.011/230606V270:user/release-keys
