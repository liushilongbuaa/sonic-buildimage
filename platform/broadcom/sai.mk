BRCM_SAI = libsaibcm_5.0.0.1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/5.0/master/libsaibcm_5.0.0.1_amd64.deb?sv=2015-04-05&sr=b&sig=FXHu5ggw8zfUdvi0UScTHMAP0X3br0vTM4f2U2brQWo%3D&se=2029-08-15T01%3A20%3A19Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_5.0.0.1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/5.0/master/libsaibcm-dev_5.0.0.1_amd64.deb?sv=2015-04-05&sr=b&sig=C48%2BIViiA5KAq4ubDkXSehylTQgiIc7ZD47eo4roBYI%3D&se=2029-08-15T01%3A21%3A14Z&sp=r"

BRCM_SAI_DBG = libsaibcm-dbg_4.3.0.10-3_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DBG)))
$(BRCM_SAI_DBG)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/master/libsaibcm-dbg_4.3.0.10-3_amd64.deb?sv=2019-10-10&st=2021-02-01T18%3A50%3A19Z&se=2036-02-02T18%3A50%3A00Z&sr=b&sp=r&sig=fpeFJ0AQeViX%2Bq4XZjxryEF0au2JtilumteRsZkXR6Y%3D"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))
$(BRCM_SAI_DBG)_DEPENDS += $(BRCM_SAI)
