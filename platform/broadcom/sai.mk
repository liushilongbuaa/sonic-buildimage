BRCM_SAI = libsaibcm_4.3.5.1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm_4.3.5.1_amd64.deb?sv=2015-04-05&sr=b&sig=c%2BgR2UeeyjEyo%2BBwCFtcTOxOQbX38EeIiwqdfQSh76o%3D&se=2035-04-13T19%3A30%3A14Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_4.3.5.1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm-dev_4.3.5.1_amd64.deb?sv=2015-04-05&sr=b&sig=qxAl66xr1T%2B0ibG%2BSSc4xM3nfVpE5w%2Bk1z8jI%2Fihu6c%3D&se=2035-04-13T19%3A33%3A19Z&sp=r"

BRCM_SAI_DBG = libsaibcm-dbg_3.5.2.3_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DBG)))
$(BRCM_SAI_DBG)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/libsaibcm-dbg_3.5.2.3_amd64.deb?sv=2015-04-05&sr=b&sig=02XfkVdPH4RF85%2B0LG%2BFA5g22tUgEXKIlF2IpZLflIk%3D&se=2033-04-16T16%3A32%3A54Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))
$(BRCM_SAI_DBG)_DEPENDS += $(BRCM_SAI)
