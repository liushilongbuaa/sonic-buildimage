BRCM_SAI = libsaibcm_4.3.5.1-2_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm_4.3.5.1-2_amd64.deb?sv=2020-04-08&st=2021-09-03T19%3A11%3A02Z&se=2036-01-01T20%3A11%3A00Z&sr=b&sp=r&sig=N8u96t8srU9bfs8xnVlFZ4%2Fw%2BZg6YYLLSc3j%2FaNPss0%3D"
BRCM_SAI_DEV = libsaibcm-dev_4.3.5.1-2_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm-dev_4.3.5.1-2_amd64.deb?sv=2015-04-05&sr=b&sig=RvQcM1FHKbezWN3GMHZ6VuslpR0d5TLxpuRjskjJ%2Fbw%3D&se=2035-05-13T19%3A31%3A33Z&sp=r"

BRCM_SAI_DBG = libsaibcm-dbg_3.5.2.3_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DBG)))
$(BRCM_SAI_DBG)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/libsaibcm-dbg_3.5.2.3_amd64.deb?sv=2015-04-05&sr=b&sig=02XfkVdPH4RF85%2B0LG%2BFA5g22tUgEXKIlF2IpZLflIk%3D&se=2033-04-16T16%3A32%3A54Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))
$(BRCM_SAI_DBG)_DEPENDS += $(BRCM_SAI)
