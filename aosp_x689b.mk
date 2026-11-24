#
# SPDX-License-Identifier: Apache-2.0
#
# ROM-agnostic product for Infinix X689B.
# No ROM-specific dependency -- works with any AOSP-based ROM.
#

$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/full_base_telephony.mk)
$(call inherit-product, device/infinix/x689b/device.mk)

PRODUCT_DEVICE := x689b
PRODUCT_NAME := aosp_x689b
PRODUCT_BRAND := Infinix
PRODUCT_MANUFACTURER := Infinix

PRODUCT_BUILD_PROP_OVERRIDES += \
    PRIVATE_BUILD_DESC="X689B-H696JKM-R-GL-230606V270 release-keys"

BUILD_FINGERPRINT := Infinix/X689B-GL/Infinix-X689B:11/RP1A.200720.011/230606V270:user/release-keys
