BRCM_SAI = libsaibcm_4.3.5.1-6_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm_4.3.5.1-6_amd64.deb?sv=2015-04-05&sr=b&sig=F%2BWXIA%2B1BCf1lfB6X%2B3WDmfrd57TQbRIf448ry%2F0G2M%3D&se=2035-07-13T03%3A22%3A23Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_4.3.5.1-6_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm-dev_4.3.5.1-6_amd64.deb?sv=2015-04-05&sr=b&sig=sxqBQ99A6FUh5fTgCTss%2FlOYXXymGOTjcMF7uofW%2FyI%3D&se=2035-07-13T03%3A23%3A37Z&sp=r"

BRCM_SAI_DBG = libsaibcm-dbg_3.5.2.3_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DBG)))
$(BRCM_SAI_DBG)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/libsaibcm-dbg_3.5.2.3_amd64.deb?sv=2015-04-05&sr=b&sig=02XfkVdPH4RF85%2B0LG%2BFA5g22tUgEXKIlF2IpZLflIk%3D&se=2033-04-16T16%3A32%3A54Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))
$(BRCM_SAI_DBG)_DEPENDS += $(BRCM_SAI)
