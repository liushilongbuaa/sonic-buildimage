BRCM_SAI = libsaibcm_5.0.0.6-1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/5.0/master/libsaibcm_5.0.0.6-1_amd64.deb?sv=2015-04-05&sr=b&sig=HA%2FwgMr%2BHnb6zzFCQDfO1WF%2Bf6PBSmIzH13728LTNz4%3D&se=2035-03-31T20%3A45%3A36Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_5.0.0.6-1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/5.0/master/libsaibcm-dev_5.0.0.6-1_amd64.deb?sv=2015-04-05&sr=b&sig=z634%2BUk14EY5VjEE4tjhvDSP2hiK8s1EJAxjvidl44I%3D&se=2035-03-31T20%3A46%3A17Z&sp=r"
BRCM_SAI_DBG = libsaibcm-dbg_5.0.0.6-1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DBG)))
$(BRCM_SAI_DBG)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/5.0/master/libsaibcm-dbg_5.0.0.6-1_amd64.deb?sv=2015-04-05&sr=b&sig=JYMp4O2vhrEEfd0sDOlCrmQq7HDnI0vTecMDTt184JM%3D&se=2035-04-19T21%3A33%3A35Z&sp=r"

# SAI module for DNX Asic family
BRCM_DNX_SAI = libsaibcm_dnx_5.0.0.6-1_amd64.deb
$(BRCM_DNX_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/5.0/master/libsaibcm_dnx_5.0.0.6-1_amd64.deb?sv=2015-04-05&sr=b&sig=mDcpzWUcTSzNBM6vPPYNuMQ6D%2BTKQAC9k%2Fv0%2Bnz3L%2BM%3D&se=2035-03-31T20%3A46%3A44Z&sp=r"
BRCM_DNX_SAI_DBG = libsaibcm-dbg_dnx_5.0.0.6-1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_DNX_SAI),$(BRCM_DNX_SAI_DBG)))
$(BRCM_DNX_SAI_DBG)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/5.0/master/libsaibcm-dbg_dnx_5.0.0.6-1_amd64.deb?sv=2015-04-05&sr=b&sig=79RNypsZZZV2be%2FcU6AiSeqY%2FaQBI98MIQrf7oKgvkY%3D&se=2158-07-03T21%3A32%3A59Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
SONIC_ONLINE_DEBS += $(BRCM_DNX_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))
$(BRCM_SAI_DBG)_DEPENDS += $(BRCM_SAI)
$(BRCM_DNX_SAI_DBG)_DEPENDS += $(BRCM_DNX_SAI)
