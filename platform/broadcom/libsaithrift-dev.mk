# libsaithrift-dev package

SAI_VER = 0.9.4

LIBSAITHRIFT_DEV = libsaithrift$(SAITHRIFT_VER)-dev_$(SAI_VER)_amd64.deb
$(LIBSAITHRIFT_DEV)_SRC_PATH = $(SRC_PATH)/sonic-sairedis/SAI
#Support two different versions of thrift
ifeq ($(SAITHRIFT_V2),y)
$(LIBSAITHRIFT_DEV)_DEPENDS += $(LIBTHRIFT_0_13_0) $(LIBTHRIFT_DEV_0_13_0) $(PYTHON3_THRIFT_0_13_0) $(THRIFT_COMPILER_0_13_0)
$(LIBSAITHRIFT_DEV)_RDEPENDS += $(LIBTHRIFT_0_13_0)
$(LIBSAITHRIFT_DEV)_BUILD_ENV = SAITHRIFTV2=true SAITHRIFT_VER=v2
else
$(LIBSAITHRIFT_DEV)_DEPENDS += $(LIBTHRIFT) $(LIBTHRIFT_DEV) $(PYTHON_THRIFT) $(THRIFT_COMPILER)
$(LIBSAITHRIFT_DEV)_RDEPENDS += $(LIBTHRIFT)
endif
$(LIBSAITHRIFT_DEV)_DEPENDS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(LIBSAITHRIFT_DEV)_RDEPENDS += $(BRCM_SAI)
SONIC_DPKG_DEBS += $(LIBSAITHRIFT_DEV)

PYTHON_SAITHRIFT = python-saithrift$(SAITHRIFT_VER)_$(SAI_VER)_amd64.deb
$(eval $(call add_extra_package,$(LIBSAITHRIFT_DEV),$(PYTHON_SAITHRIFT)))

SAISERVER = saiserver$(SAITHRIFT_VER)_$(SAI_VER)_amd64.deb
$(SAISERVER)_RDEPENDS += $(LIBSAITHRIFT_DEV)
$(eval $(call add_extra_package,$(LIBSAITHRIFT_DEV),$(SAISERVER)))

SAISERVER_DBG = saiserver$(SAITHRIFT_VER)-dbg_$(SAI_VER)_amd64.deb
$(SAISERVER_DBG)_RDEPENDS += $(SAISERVER)
$(eval $(call add_extra_package,$(LIBSAITHRIFT_DEV),$(SAISERVER_DBG)))
