BRCM_SAI = libsaibcm_4.3.5.2_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm_4.3.5.2_amd64.deb?sv=2020-10-02&st=2022-01-13T06%3A01%3A24Z&se=2037-01-14T06%3A01%3A00Z&sr=b&sp=r&sig=w6pvHKumQcToTp4ooNU3rsZpYUSVaJN5CrpTEZK%2B3Ek%3D"
BRCM_SAI_DEV = libsaibcm-dev_4.3.5.2_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm-dev_4.3.5.2_amd64.deb?sv=2020-10-02&st=2022-01-13T06%3A04%3A13Z&se=2037-01-14T06%3A04%3A00Z&sr=b&sp=r&sig=Qam0Cl%2B%2BRr8qHiFj47rtDpsswpdhrlfiJwG9EjXTBV4%3D"

BRCM_SAI_DBG = libsaibcm-dbg_3.5.2.3_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DBG)))
$(BRCM_SAI_DBG)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/libsaibcm-dbg_3.5.2.3_amd64.deb?sv=2015-04-05&sr=b&sig=02XfkVdPH4RF85%2B0LG%2BFA5g22tUgEXKIlF2IpZLflIk%3D&se=2033-04-16T16%3A32%3A54Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))
$(BRCM_SAI_DBG)_DEPENDS += $(BRCM_SAI)
