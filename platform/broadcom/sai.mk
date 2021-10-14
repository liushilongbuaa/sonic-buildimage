BRCM_SAI = libsaibcm_4.3.5.1-4_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm_4.3.5.1-4_amd64.deb?sv=2015-04-05&sr=b&sig=LfRmvdkpfDcRBIW0R%2BHvD9zdc%2Br5KP%2BRY9aGK9gk1IE%3D&se=2035-06-22T06%3A50%3A41Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_4.3.5.1-4_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm-dev_4.3.5.1-4_amd64.deb?sv=2015-04-05&sr=b&sig=2WoIZ2gpylyuL6XEKTGka0zqXLNpLr407Qfyp6YFqvI%3D&se=2035-06-22T06%3A51%3A34Z&sp=r"

BRCM_SAI_DBG = libsaibcm-dbg_3.5.2.3_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DBG)))
$(BRCM_SAI_DBG)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/libsaibcm-dbg_3.5.2.3_amd64.deb?sv=2015-04-05&sr=b&sig=02XfkVdPH4RF85%2B0LG%2BFA5g22tUgEXKIlF2IpZLflIk%3D&se=2033-04-16T16%3A32%3A54Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))
$(BRCM_SAI_DBG)_DEPENDS += $(BRCM_SAI)
