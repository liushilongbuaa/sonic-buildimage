# Pensando dpu version

DPU_MODULE_VERSION = 1.0.0
DPU_MODULE = dpu_$(DPU_MODULE_VERSION)_amd64.deb
$(DPU_MODULE)_SRC_PATH = $(SRC_PATH)/dpu
$(DPU_MODULE)_MACHINE = vs
SONIC_DPKG_DEBS += $(DPU_MODULE)
