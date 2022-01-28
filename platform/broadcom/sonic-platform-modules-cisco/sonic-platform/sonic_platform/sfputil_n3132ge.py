# sfputil.py
#
# Platform-specific SFP transceiver interface for SONiC
#

try:
    import time
    import fcntl
    import errno
    import re
    import abc
    from sonic_platform_base.sonic_sfp.sfputilbase import SfpUtilBase
    from sonic_platform_base.sonic_sfp.sff8436 import sff8436InterfaceId  
    from sonic_platform_base.sonic_sfp.bcmshell import bcmshell
    from sonic_platform_base.sonic_sfp.sff8436 import sff8436Dom    
except ImportError as e:
    raise ImportError("%s - required module not found" % str(e))

# definitions of the offset and width for values in XCVR info eeprom
XCVR_INTFACE_BULK_OFFSET = 0
XCVR_INTFACE_BULK_WIDTH_QSFP = 20
XCVR_INTFACE_BULK_WIDTH_SFP = 21
XCVR_TYPE_OFFSET = 0
XCVR_TYPE_WIDTH = 1
XCVR_EXT_TYPE_OFFSET = 1
XCVR_EXT_TYPE_WIDTH = 1
XCVR_CONNECTOR_OFFSET = 2
XCVR_CONNECTOR_WIDTH = 1
XCVR_COMPLIANCE_CODE_OFFSET = 3
XCVR_COMPLIANCE_CODE_WIDTH = 8
XCVR_ENCODING_OFFSET = 11
XCVR_ENCODING_WIDTH = 1
XCVR_NBR_OFFSET = 12
XCVR_NBR_WIDTH = 1
XCVR_EXT_RATE_SEL_OFFSET = 13
XCVR_EXT_RATE_SEL_WIDTH = 1
XCVR_CABLE_LENGTH_OFFSET = 14
XCVR_CABLE_LENGTH_WIDTH_QSFP = 5
XCVR_CABLE_LENGTH_WIDTH_SFP = 6
XCVR_VENDOR_NAME_OFFSET = 20
XCVR_VENDOR_NAME_WIDTH = 16
XCVR_VENDOR_OUI_OFFSET = 37
XCVR_VENDOR_OUI_WIDTH = 3
XCVR_VENDOR_PN_OFFSET = 40
XCVR_VENDOR_PN_WIDTH = 16
XCVR_HW_REV_OFFSET = 56
XCVR_HW_REV_WIDTH_OSFP = 2
XCVR_HW_REV_WIDTH_QSFP = 2
XCVR_HW_REV_WIDTH_SFP = 4
XCVR_VENDOR_SN_OFFSET = 68
XCVR_VENDOR_SN_WIDTH = 16
XCVR_VENDOR_DATE_OFFSET = 84
XCVR_VENDOR_DATE_WIDTH = 8
XCVR_DOM_CAPABILITY_OFFSET = 92
XCVR_DOM_CAPABILITY_WIDTH = 1

#definitions of the offset and width for values in DOM info eeprom
QSFP_DOM_REV_OFFSET = 1
QSFP_DOM_REV_WIDTH = 1
QSFP_TEMPE_OFFSET = 22
QSFP_TEMPE_WIDTH = 2
QSFP_VLOT_OFFSET = 26
QSFP_VOLT_WIDTH = 2
QSFP_CHANNL_MON_OFFSET = 34
QSFP_CHANNL_MON_WIDTH = 16
QSFP_CHANNL_MON_WITH_TX_POWER_WIDTH = 24
QSFP_MODULE_THRESHOLD_OFFSET = 128
QSFP_MODULE_THRESHOLD_WIDTH = 24
QSFP_CHANNL_THRESHOLD_OFFSET = 176
QSFP_CHANNL_THRESHOLD_WIDTH = 24

SFP_TEMPE_OFFSET = 96
SFP_TEMPE_WIDTH = 2
SFP_VLOT_OFFSET = 98
SFP_VOLT_WIDTH = 2
SFP_CHANNL_MON_OFFSET = 100
SFP_CHANNL_MON_WIDTH = 6

qsfp_cable_length_tup = ('Length(km)', 'Length OM3(2m)', 
                         'Length OM2(m)', 'Length OM1(m)',
                         'Length Cable Assembly(m)')

sfp_cable_length_tup = ('LengthSMFkm-UnitsOfKm', 'LengthSMF(UnitsOf100m)',
                        'Length50um(UnitsOf10m)', 'Length62.5um(UnitsOfm)',
                        'LengthCable(UnitsOfm)', 'LengthOM3(UnitsOf10m)')

sfp_compliance_code_tup = ('10GEthernetComplianceCode', 'InfinibandComplianceCode', 
                            'ESCONComplianceCodes', 'SONETComplianceCodes',
                            'EthernetComplianceCodes','FibreChannelLinkLength',
                            'FibreChannelTechnology', 'SFP+CableTechnology',
                            'FibreChannelTransmissionMedia','FibreChannelSpeed')

qsfp_compliance_code_tup = ('10/40G Ethernet Compliance Code', 'SONET Compliance codes',
                            'SAS/SATA compliance codes', 'Gigabit Ethernet Compliant codes',
                            'Fibre Channel link length/Transmitter Technology',
                            'Fibre Channel transmission media', 'Fibre Channel Speed')


class SfpUtilBcmMdio(SfpUtilBase):
    """Provides SFP+/QSFP EEPROM access via BCM MDIO methods"""

    __metaclass__ = abc.ABCMeta

    IDENTITY_EEPROM_ADDR = 0xa000
    DOM_EEPROM_ADDR = 0xa200

    # Register Offsets and Constants
    EEPROM_ADDR = 0x8007
    TWOWIRE_CONTROL_REG = 0x8000
    TWOWIRE_CONTROL_ENABLE_MASK = 0x8000
    TWOWIRE_CONTROL_READ_CMD_MASK = 0x0002
    TWOWIRE_CONTROL_CMD_STATUS_MASK = 0xc
    TWOWIRE_CONTROL_CMD_STATUS_IDLE = 0x0
    TWOWIRE_CONTROL_CMD_STATUS_SUCCESS = 0x4
    TWOWIRE_CONTROL_CMD_STATUS_BUSY = 0x8
    TWOWIRE_CONTROL_CMD_STATUS_FAILED = 0xc

    TWOWIRE_INTERNAL_ADDR_REG = 0x8004
    TWOWIRE_INTERNAL_ADDR_REGVAL = EEPROM_ADDR

    TWOWIRE_TRANSFER_SIZE_REG = 0x8002

    TWOWIRE_TRANSFER_SLAVEID_ADDR_REG = 0x8005

    # bcmcmd handle
    bcm = None
    # Retry value of 6 would provide approx. 60 seconds of timeout
    # assuming default bcmshell socket timeout value of 10 seconds
    BCMSHELL_RETRY_MAX = 6

    #File-lock based synchronized bcmsh socket access
    BCMSHELL_LOCK_FILE = "/etc/sonic/bcmsh_lock"
    BCMSHELL_LOCK_RETRY_MAX = 30

    # With BCM MDIO, we do not use port_to_eeprom_mapping
    @property
    def port_to_eeprom_mapping(self):
        return None

    def __init__(self):
        self.bcm = None
        SfpUtilBase.__init__(self)

    def _init_bcmshell(self): 
        try:
            self.bcm = bcmshell()
        except:
            raise RuntimeError("unable to obtain exclusive access to hardware")

    def _get_bcm_port(self,port_num):
        bcm_port = "xe%d" % (port_num)
        return bcm_port

    def _read_eeprom_devid(self, port_num, devid, offset , num_bytes=256):
        if port_num in self.qsfp_ports:
            # Get QSFP page 0 and page 1 eeprom
            # XXX: Need to have a way to select page 2,3,4 for dom eeprom
            eeprom_raw_1 = self._read_eeprom_devid_page_size(port_num, devid, 0, 128, offset)
            eeprom_raw_2 = self._read_eeprom_devid_page_size(port_num, devid, 1, 128, offset)
            if eeprom_raw_1 is None or eeprom_raw_2 is None:
                return None
            return eeprom_raw_1 + eeprom_raw_2
        else:
            # Read 256 bytes of data from specified devid
            return self._read_eeprom_devid_page_size(port_num, devid, 0, 256, offset)

    def _read_eeprom_devid_dom(self, port_num, devid, offset):
        if port_num in self.qsfp_ports:
            eeprom_raw_1 = self._read_eeprom_devid_page_size(port_num, devid, 3, 128, offset)
            if eeprom_raw_1 is None:
                return None
            return eeprom_raw_1  
        else:
            return None


    def _read_eeprom_devid_page_size(self, port_num, devid, page, size, offset):
        """
        Read data from specified devid using the bcmshell's 'phy' command..

        Use port_num to identify which EEPROM to read.
        """

        TWOWIRE_TRANSFER_SLAVEID_ADDR = 0x0001 | devid | page << 8

        eeprom_raw = None
        num_bytes = size
        phy_addr = None
        bcm_port = None

        ganged_40_by_4 = self.is_physical_port_ganged_40_by_4(port_num)
        if ganged_40_by_4 == 1:
            # In 40G/4 gang mode, the port is by default configured in
            # single mode. To read the individual sfp details, the port
            # needs to be in quad mode. Set the port mode to quad mode
            # for the duration of this function. Switch it back to
            # original state after we are done
            logical_port = self.get_physical_to_logical(port_num)
            gang_phyid = self.get_40_by_4_gangport_phyid(logical_port[0])

            # Set the gang port to quad mode
            chip_mode_reg = 0xc805
            chip_mode_mask = 0x1

            # bcmcmd phy raw c45 <phyid> <device> <mode_reg_addr> <mode_mask>
            # Ex: bcmcmd phy raw c45 0x4 1 0xc805 0x0070
            gang_chip_mode_orig = self._phy_reg_get(gang_phyid, None, chip_mode_reg)
            if gang_chip_mode_orig is None:
                return None
            quad_mode_mask = gang_chip_mode_orig & ~(chip_mode_mask)
            cmd_status = self._phy_reg_set(gang_phyid, None, chip_mode_reg, quad_mode_mask)
            if cmd_status is False:
                return None

            phy_addr = self.get_physical_port_phyid(port_num)[0]

        if phy_addr is None:
            bcm_port = self._get_bcm_port(port_num)

        # Enable 2 wire master
        regval = self._phy_reg_get(phy_addr, bcm_port, self.TWOWIRE_CONTROL_REG)
        if regval is None:
            return None
        regval = regval | self.TWOWIRE_CONTROL_ENABLE_MASK
        cmd_status = self._phy_reg_set(phy_addr, bcm_port, self.TWOWIRE_CONTROL_REG, regval)
        if cmd_status is False:
            return None

        # Set 2wire internal addr reg
        cmd_status = self._phy_reg_set(phy_addr, bcm_port,
                          self.TWOWIRE_INTERNAL_ADDR_REG,
                          self.TWOWIRE_INTERNAL_ADDR_REGVAL)
        if cmd_status is False:
            return None

        # Set transfer count
        cmd_status = self._phy_reg_set(phy_addr, bcm_port,
                          self.TWOWIRE_TRANSFER_SIZE_REG, size)
        if cmd_status is False:
            return None

        # Set eeprom dev id
        cmd_status = self._phy_reg_set(phy_addr, bcm_port,
                          self.TWOWIRE_TRANSFER_SLAVEID_ADDR_REG,
                          TWOWIRE_TRANSFER_SLAVEID_ADDR)
        if cmd_status is False:
            return None

        # Initiate read
        regval = self._phy_reg_get(phy_addr, bcm_port, self.TWOWIRE_CONTROL_REG)
        if regval is None:
            return None
        regval = regval | self.TWOWIRE_CONTROL_READ_CMD_MASK
        cmd_status = self._phy_reg_set(phy_addr, bcm_port, self.TWOWIRE_CONTROL_REG, regval)
        if cmd_status is False:
            return None

        # Read command status
        regval = self._phy_reg_get(phy_addr, bcm_port, self.TWOWIRE_CONTROL_REG)
        if regval is None:
            return None
        cmd_status = regval & self.TWOWIRE_CONTROL_CMD_STATUS_MASK

        # poll while command busy
        poll_count = 0
        while cmd_status == self.TWOWIRE_CONTROL_CMD_STATUS_BUSY:
            regval = self._phy_reg_get(phy_addr, bcm_port, self.TWOWIRE_CONTROL_REG)
            if regval is None:
                regval = 0
            cmd_status = regval & self.TWOWIRE_CONTROL_CMD_STATUS_MASK
            poll_count += 1
            if poll_count > 500:
                raise RuntimeError("Timeout waiting for two-wire transaction completion")

        if cmd_status == self.TWOWIRE_CONTROL_CMD_STATUS_SUCCESS:
            # Initialize return buffer
            eeprom_raw = []
            for i in range(0, num_bytes):
                eeprom_raw.append("0x00")

            # Read into return buffer
            for i in range(0, num_bytes):
                addr = self.EEPROM_ADDR + i
                out = self._phy_reg_get(phy_addr, bcm_port, addr)
                if out is None:
                    continue #fill it with zero and skip when there is error in read
                eeprom_raw[i] = hex(out)[2:].zfill(2)

        if ganged_40_by_4 == 1:
            # Restore original ganging mode
            self._phy_reg_set(gang_phyid, bcm_port,
                              chip_mode_reg, gang_chip_mode_orig)

        return eeprom_raw

    #Processes accessing bcmsh in this way are assumed to hold this lock briefly
    def _bcmsh_lock(self, retry_max=BCMSHELL_LOCK_RETRY_MAX):
        retry = 0

        try:
            fd = open(self.BCMSHELL_LOCK_FILE, "r")
        except OSError as e:
            print("Error: unable to open file: %s" % str(e))
            return None

        while (retry < retry_max):
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except (OSError,IOError) as e:
                if ((e.errno == errno.EAGAIN) or
                        (e.errno == errno.EPERM) or
                        (e.errno == errno.EBUSY) or
                        (e.errno == errno.EWOULDBLOCK) or
                        (e.errno == errno.ETIMEDOUT) or
                        (e.errno == errno.EACCES)):
                    retry += 1
                    time.sleep(1)
                    continue
                else:
                    print("Error: unable to lock file: %s" % str(e))
                    fd.close()
                    return None

        if (retry == retry_max):
            fd.close()
            return None

        return fd

    def _bcmsh_unlock(self, fd):
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
            fd.close()
        except OSError as e:
            print("Error: unable to close/unlock file: %s" % str(e))
            return False

        return True


    def _phy_reg_get(self, phy_addr, bcm_port, regaddr, retry_max=BCMSHELL_RETRY_MAX):
        retry = 0

        if self.bcm is None:
            self._init_bcmshell()

        if phy_addr is not None:
            cmd = "phy raw c45 %s 1 0x%x" % (phy_addr, regaddr)
        else:
            cmd = "phy %s 0x%x 1" % (bcm_port, regaddr)

        fd = self._bcmsh_lock()
        if fd is None:
            return None

        while (retry < retry_max):
            try:
                out = self.bcm.run(cmd)
                break
            except:
                retry += 1
                continue

        self._bcmsh_unlock(fd)

        if (retry == retry_max):
            return None

        return int(out.split().pop(), 16)

    def _phy_reg_set(self, phy_addr, bcm_port, regaddr, regval, retry_max=BCMSHELL_RETRY_MAX):
        retry = 0

        if self.bcm is None:
            self._init_bcmshell()

        if phy_addr is not None:
            cmd = "phy raw c45 %s 1 0x%x 0x%x" % (phy_addr, regaddr, regval)
        else:
            cmd = "phy %s 0x%x 1 0x%x" % (bcm_port, regaddr, regval)

        fd = self._bcmsh_lock()
        if fd is None:
            return None

        while (retry < retry_max):
            try:
                self.bcm.run(cmd)
                break
            except:
                retry += 1
                continue

        self._bcmsh_unlock(fd)

        if (retry == retry_max):
            return False

        return True

class SfpUtilN3132ge(SfpUtilBcmMdio):
    """Platform-specific SfpUtil class"""
    SUPPORTED_SFP_PORT_TYPES = ['SFP', 'SFP+']
    SUPPORTED_QSFP_PORT_TYPES = ['QSFP', 'QSFP+', 'QSFP28']
    SUPPORTED_OSFP_QSFPDD_PORT_TYPES = ['QSFP-DD', 'OSFP']

    def __init__(self, port_start, num_ports, platform_global_data, sfps_data):
        SfpUtilBcmMdio.__init__(self)
        self._xcvr_presence = None
        self.XCVR_CHANGE_WAIT_TIME = .2
        self.platform_global_data = platform_global_data
        self.sfps_data = sfps_data
        self.PORT_START = port_start - 1
        self.PORT_END = num_ports - 1
        self.NUM_PORTS = num_ports

        self.SFP_PORTS_IN_BLOCK = set()
        self.QSFP_PORTS_IN_BLOCK = set()
        self.OSFP_QSFPDD_PORTS_IN_BLOCK = set()

        if 'sfp' in sfps_data:
            sfp_data = sfps_data['sfp']
            for sfp_block in sfp_data:
                if 'type' not in sfp_block:
                    continue
                sfp_type = sfp_block['type']
                if sfp_type not in self.SUPPORTED_SFP_PORT_TYPES and sfp_type not in self.SUPPORTED_QSFP_PORT_TYPES and sfp_type not in self.SUPPORTED_OSFP_QSFPDD_PORT_TYPES:
                    continue

                if 'start_index' not in sfp_block:
                    continue

                sfp_start = int(sfp_block['start_index'])
                if sfp_start < 1:
                    continue

                if 'sfp_num' not in sfp_block:
                    continue

                sfp_num_block = int(sfp_block['sfp_num'])
                if sfp_num_block < 1:
                    continue

                if sfp_type in self.SUPPORTED_QSFP_PORT_TYPES:
                    for port_index in range(sfp_start - 1,sfp_num_block):
                        self.QSFP_PORTS_IN_BLOCK.add(port_index)
                elif sfp_type in self.SUPPORTED_SFP_PORT_TYPES:
                    for port_index in range(sfp_start - 1,sfp_num_block):
                        self.SFP_PORTS_IN_BLOCK.add(port_index)
                elif sfp_type in self.SUPPORTED_OSFP_QSFPDD_PORT_TYPES:
                    for port_index in range(sfp_start - 1,sfp_num_block):
                        self.OSFP_QSFPDD_PORTS_IN_BLOCK.add(port_index)
    @property
    def port_start(self):
        """ Starting index of physical port range """
        return self.PORT_START

    @property
    def port_end(self):
        """ Ending index of physical port range """
        return self.PORT_END

    @property
    def sfp_ports(self):
        """ SFP Ports """
        return self.SFP_PORTS_IN_BLOCK
    
    @property
    def qsfp_ports(self):
        """ QSFP Ports """
        return self.QSFP_PORTS_IN_BLOCK
    
    @property
    def osfp_ports(self):
        """ OSFP/QSFP-DD  Ports """
        return self.OSFP_QSFPDD_PORTS_IN_BLOCK                    

    def get_transceiver_change_event(self, timeout=0):
        end_time = time.time() + timeout
        p_pres_dict = {}
        while True:
            xcvrs = []
            try:
                for port in range(self.PORT_START, self.NUM_PORTS):
                    xcvr_status = int(self.get_presence(port))
                    xcvrs.append(xcvr_status)
            except:
                print ( "Failed to get_presence")
                return False, {}

            if self._xcvr_presence is not None:
                # Previous state present. Check any change from previous state
                for p in range(self.PORT_START, self.NUM_PORTS):
                    if self._xcvr_presence[p] != xcvrs[p]:
                        # Add the change to dict
                        d = {str(p) : str(xcvrs[p])}
                        p_pres_dict.update(d)
                        #Reset the XCVR if it is inserted
                        if xcvrs[p] == 1 :
                            self.reset(p)

                if len(p_pres_dict) != 0 :
                    time.sleep(2)
            else:
                for p in range(self.PORT_START, self.NUM_PORTS):
                    # Add the change to dict
                    if xcvrs[p] == 1:
                        d = {str(p) : str(xcvrs[p])}
                        p_pres_dict.update(d)
                        self.reset(p)

                if len(p_pres_dict) != 0 :
                    time.sleep(2)

            self._xcvr_presence = xcvrs

            if len(p_pres_dict) != 0 :
                return True, p_pres_dict

            cur_time = time.time()
            if cur_time >= end_time and timeout != 0:
                break
            elif (cur_time + self.XCVR_CHANGE_WAIT_TIME) >= end_time and timeout != 0:
                time.sleep(end_time - cur_time)
            else:
                time.sleep(self.XCVR_CHANGE_WAIT_TIME)

        return True, {} #we reach here when timeout expire

    def get_presence(self, port_num):
        BCM_USD_PHY_MOD_ABS_INPUT_REG = 0x1c82f
        PRESENCE_MASK = (1 << 6)

        phy_addr = None
        bcm_port = None

        ganged_40_by_4 = self.is_physical_port_ganged_40_by_4(port_num)
        if ganged_40_by_4 == 1:
            # In 40G/4 gang mode, the port is by default configured in
            # single mode. To read the individual sfp details, the port
            # needs to be in quad mode. Set the port mode to quad mode
            # for the duration of this function. Switch it back to
            # original state after we are done
            logical_port = self.get_physical_to_logical(port_num)
            gang_phyid = self.get_40_by_4_gangport_phyid(logical_port[0])

            # Set the gang port to quad mode
            chip_mode_reg = 0xc805
            chip_mode_mask = 0x1

            # bcmcmd phy raw c45 <phyid> 1 <mode_reg_addr> <mode_mask>
            # Ex: bcmcmd phy raw c45 0x4 1 0xc805 0x0070
            gang_chip_mode_orig = self._phy_reg_get(gang_phyid, None, chip_mode_reg)
            if gang_chip_mode_orig is None:
                return False
            quad_mode_mask = gang_chip_mode_orig & ~(chip_mode_mask)
            cmd_status = self._phy_reg_set(gang_phyid, None, chip_mode_reg, quad_mode_mask)
            if cmd_status is False:
                return False

            phy_addr = self.get_physical_port_phyid(port_num)[0]

        if phy_addr is None:
            bcm_port = self._get_bcm_port(port_num)

        regval = self._phy_reg_get(phy_addr, bcm_port, BCM_USD_PHY_MOD_ABS_INPUT_REG)
        if regval is None:
            return False

        if ganged_40_by_4 == 1:
            # Restore original ganging mode
            cmd_status = self._phy_reg_set(gang_phyid, bcm_port,
                              chip_mode_reg, gang_chip_mode_orig)

        if (regval & PRESENCE_MASK) == 0:
            return True

        return False

    def get_low_power_mode(self, port_num):
        #print ("Low-power mode currently not supported for this platform")
        return False

    def set_low_power_mode(self, port_num, lpmode):
        #print ("Low-power mode currently not supported for this platform")
        raise NotImplementedError


    def reset(self, port_num):
        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.port_end:
            print ("Error: Invalid port")
            return False

        qsfp_reset_direction_device_file_path = "/sys/class/gpio/gpio%d/direction" % (416+port_num)

        try:
            direction_file = open(qsfp_reset_direction_device_file_path, "w")
        except IOError as e:
            print ("Error: unable to open file: %s" % str(e))
            return False

        # First, set the direction to 'out' to enable writing value
        direction_file.write("out")
        direction_file.close()

        qsfp_reset_value_device_file_path = "/sys/class/gpio/gpio%d/value" % (416+port_num)

        try:
            value_file = open(qsfp_reset_value_device_file_path, "w")
        except IOError as e:
            print ("Error: unable to open file: %s" % str(e))
            return False

        # Write "1" to put the transceiver into reset mode
        value_file.write("1")
        value_file.close()

        # Sleep 1 second to allow it to settle
        time.sleep(1)

        try:
            value_file = open(qsfp_reset_value_device_file_path, "w")
        except IOError as e:
            print ("Error: unable to open file: %s" % str(e))
            return False

        # Write "0" to take the transceiver out of reset mode
        value_file.write("0")
        value_file.close()

        return True

    def _read_eeprom_specific_bytes(self, eeprom_raw_data, offset, nbytes):
        if eeprom_raw_data is None:
            return None

        #check out-of-bound access and truncating it
        if offset + nbytes > len(eeprom_raw_data):
            nbytes = len(eeprom_raw_data) - offset
        
        return eeprom_raw_data[offset:offset+nbytes]


    # Read out SFP type, vendor name, PN, REV, SN from eeprom.
    def get_transceiver_info_dict(self, port_num):
        transceiver_info_dict = {}
        compliance_code_dict = {}

        if port_num in self.qsfp_ports:
            offset = 128
            vendor_rev_width = XCVR_HW_REV_WIDTH_QSFP
            cable_length_width = XCVR_CABLE_LENGTH_WIDTH_QSFP
            interface_info_bulk_width = XCVR_INTFACE_BULK_WIDTH_QSFP
            sfp_type = 'QSFP'

            sfpi_obj = sff8436InterfaceId()
            if sfpi_obj is None:
                print("Error: sfp_object open failed")
                return None


            #Read 256 bytes of data from specified devid
            eeprom_raw = self._read_eeprom_devid(port_num, self.IDENTITY_EEPROM_ADDR, 0)
            if eeprom_raw is None:
                print("eeprom raw data is None")
                return None

            sfp_interface_bulk_raw = self._read_eeprom_specific_bytes(eeprom_raw, (offset + XCVR_INTFACE_BULK_OFFSET), interface_info_bulk_width)
            if sfp_interface_bulk_raw is not None:
                sfp_interface_bulk_data = sfpi_obj.parse_sfp_info_bulk(sfp_interface_bulk_raw, 0)
            else:
                return None

            sfp_vendor_name_raw = self._read_eeprom_specific_bytes(eeprom_raw, (offset + XCVR_VENDOR_NAME_OFFSET), XCVR_VENDOR_NAME_WIDTH)
            if sfp_vendor_name_raw is not None:
                sfp_vendor_name_data = sfpi_obj.parse_vendor_name(sfp_vendor_name_raw, 0)
            else:
                return None

            sfp_vendor_pn_raw = self._read_eeprom_specific_bytes(eeprom_raw, (offset + XCVR_VENDOR_PN_OFFSET), XCVR_VENDOR_PN_WIDTH)
            if sfp_vendor_pn_raw is not None:
                sfp_vendor_pn_data = sfpi_obj.parse_vendor_pn(sfp_vendor_pn_raw, 0)
            else:
                return None

            sfp_vendor_rev_raw = self._read_eeprom_specific_bytes(eeprom_raw, (offset + XCVR_HW_REV_OFFSET), vendor_rev_width)
            if sfp_vendor_rev_raw is not None:
                sfp_vendor_rev_data = sfpi_obj.parse_vendor_rev(sfp_vendor_rev_raw, 0)
            else:
                return None

            sfp_vendor_sn_raw = self._read_eeprom_specific_bytes(eeprom_raw, (offset + XCVR_VENDOR_SN_OFFSET), XCVR_VENDOR_SN_WIDTH)
            if sfp_vendor_sn_raw is not None:
                sfp_vendor_sn_data = sfpi_obj.parse_vendor_sn(sfp_vendor_sn_raw, 0)
            else:
                return None

            sfp_vendor_oui_raw = self._read_eeprom_specific_bytes(eeprom_raw, (offset + XCVR_VENDOR_OUI_OFFSET), XCVR_VENDOR_OUI_WIDTH)
            if sfp_vendor_oui_raw is not None:
                sfp_vendor_oui_data = sfpi_obj.parse_vendor_oui(sfp_vendor_oui_raw, 0)
            else:
                return None

            sfp_vendor_date_raw = self._read_eeprom_specific_bytes(eeprom_raw, (offset + XCVR_VENDOR_DATE_OFFSET), XCVR_VENDOR_DATE_WIDTH)
            if sfp_vendor_date_raw is not None:
                sfp_vendor_date_data = sfpi_obj.parse_vendor_date(sfp_vendor_date_raw, 0)
            else:
                return None

            transceiver_info_dict['type'] = sfp_interface_bulk_data['data']['type']['value']
            transceiver_info_dict['manufacturer'] = sfp_vendor_name_data['data']['Vendor Name']['value']
            transceiver_info_dict['model'] = sfp_vendor_pn_data['data']['Vendor PN']['value']
            transceiver_info_dict['hardware_rev'] = sfp_vendor_rev_data['data']['Vendor Rev']['value']
            transceiver_info_dict['serial'] = sfp_vendor_sn_data['data']['Vendor SN']['value']
            transceiver_info_dict['vendor_oui'] = sfp_vendor_oui_data['data']['Vendor OUI']['value']
            transceiver_info_dict['vendor_date'] = sfp_vendor_date_data['data']['VendorDataCode(YYYY-MM-DD Lot)']['value']
            transceiver_info_dict['connector'] = sfp_interface_bulk_data['data']['Connector']['value']
            transceiver_info_dict['encoding'] = sfp_interface_bulk_data['data']['EncodingCodes']['value']
            transceiver_info_dict['ext_identifier'] = sfp_interface_bulk_data['data']['Extended Identifier']['value']
            transceiver_info_dict['ext_rateselect_compliance'] = sfp_interface_bulk_data['data']['RateIdentifier']['value']
            for key in qsfp_cable_length_tup:
                if key in sfp_interface_bulk_data['data']:
                    transceiver_info_dict['cable_type'] = key
                    transceiver_info_dict['cable_length'] = str(sfp_interface_bulk_data['data'][key]['value'])

            for key in qsfp_compliance_code_tup:
                if key in sfp_interface_bulk_data['data']['Specification compliance']['value']:
                    compliance_code_dict[key] = sfp_interface_bulk_data['data']['Specification compliance']['value'][key]['value']
            transceiver_info_dict['specification_compliance'] = str(compliance_code_dict)
            
            transceiver_info_dict['nominal_bit_rate'] = str(sfp_interface_bulk_data['data']['Nominal Bit Rate(100Mbs)']['value'])

        return transceiver_info_dict

    def get_transceiver_dom_info_dict(self, port_num):
        transceiver_dom_info_dict = {}

        if port_num in self.qsfp_ports:
            offset = 0
            offset_xcvr = 128

            sfpd_obj = sff8436Dom()
            if sfpd_obj is None:
                return None

            sfpi_obj = sff8436InterfaceId()
            if sfpi_obj is None:
                return None

            #Read 256 bytes of data from specified devid
            eeprom_raw = self._read_eeprom_devid(port_num, self.IDENTITY_EEPROM_ADDR, 0)
            if eeprom_raw is None:
                print("eeprom raw data is None")
                return None

            # QSFP capability byte parse, through this byte can know whether it support tx_power or not.
            # TODO: in the future when decided to migrate to support SFF-8636 instead of SFF-8436,
            # need to add more code for determining the capability and version compliance
            # in SFF-8636 dom capability definitions evolving with the versions.
            qsfp_dom_capability_raw = self._read_eeprom_specific_bytes(eeprom_raw, (offset_xcvr + XCVR_DOM_CAPABILITY_OFFSET), XCVR_DOM_CAPABILITY_WIDTH)
            if qsfp_dom_capability_raw is not None:
                qspf_dom_capability_data = sfpi_obj.parse_dom_capability(qsfp_dom_capability_raw, 0)
            else:
                return None

            dom_temperature_raw = self._read_eeprom_specific_bytes(eeprom_raw, (offset + QSFP_TEMPE_OFFSET), QSFP_TEMPE_WIDTH)
            if dom_temperature_raw is not None:
                dom_temperature_data = sfpd_obj.parse_temperature(dom_temperature_raw, 0)
            else:
                return None

            dom_voltage_raw = self._read_eeprom_specific_bytes(eeprom_raw, (offset + QSFP_VLOT_OFFSET), QSFP_VOLT_WIDTH)
            if dom_voltage_raw is not None:
                dom_voltage_data = sfpd_obj.parse_voltage(dom_voltage_raw, 0)
            else:
                return None

            qsfp_dom_rev_raw = self._read_eeprom_specific_bytes(eeprom_raw, (offset + QSFP_DOM_REV_OFFSET), QSFP_DOM_REV_WIDTH)
            if qsfp_dom_rev_raw is not None:
                qsfp_dom_rev_data = sfpd_obj.parse_sfp_dom_rev(qsfp_dom_rev_raw, 0)
            else:
                return None

            transceiver_dom_info_dict['temperature'] = dom_temperature_data['data']['Temperature']['value']
            transceiver_dom_info_dict['voltage'] = dom_voltage_data['data']['Vcc']['value']

            # The tx_power monitoring is only available on QSFP which compliant with SFF-8636
            # and claimed that it support tx_power with one indicator bit.
            dom_channel_monitor_data = {}
            qsfp_dom_rev = qsfp_dom_rev_data['data']['dom_rev']['value']
            qsfp_tx_power_support = qspf_dom_capability_data['data']['Tx_power_support']['value']
            if (qsfp_dom_rev[0:8] != 'SFF-8636' or (qsfp_dom_rev[0:8] == 'SFF-8636' and qsfp_tx_power_support != 'on')):
                dom_channel_monitor_raw = self._read_eeprom_specific_bytes(eeprom_raw, (offset + QSFP_CHANNL_MON_OFFSET), QSFP_CHANNL_MON_WIDTH)
                if dom_channel_monitor_raw is not None:
                    dom_channel_monitor_data = sfpd_obj.parse_channel_monitor_params(dom_channel_monitor_raw, 0)
                else:
                    return None

                transceiver_dom_info_dict['tx1power'] = 'N/A'
                transceiver_dom_info_dict['tx2power'] = 'N/A'
                transceiver_dom_info_dict['tx3power'] = 'N/A'
                transceiver_dom_info_dict['tx4power'] = 'N/A'
            else:
                dom_channel_monitor_raw = self._read_eeprom_specific_bytes(eeprom_raw, (offset + QSFP_CHANNL_MON_OFFSET), QSFP_CHANNL_MON_WITH_TX_POWER_WIDTH)
                if dom_channel_monitor_raw is not None:
                    dom_channel_monitor_data = sfpd_obj.parse_channel_monitor_params_with_tx_power(dom_channel_monitor_raw, 0)
                else:
                    return None

                transceiver_dom_info_dict['tx1power'] = dom_channel_monitor_data['data']['TX1Power']['value']
                transceiver_dom_info_dict['tx2power'] = dom_channel_monitor_data['data']['TX2Power']['value']
                transceiver_dom_info_dict['tx3power'] = dom_channel_monitor_data['data']['TX3Power']['value']
                transceiver_dom_info_dict['tx4power'] = dom_channel_monitor_data['data']['TX4Power']['value']


            transceiver_dom_info_dict['temperature'] = dom_temperature_data['data']['Temperature']['value']
            transceiver_dom_info_dict['voltage'] = dom_voltage_data['data']['Vcc']['value']
            transceiver_dom_info_dict['rx1power'] = dom_channel_monitor_data['data']['RX1Power']['value']
            transceiver_dom_info_dict['rx2power'] = dom_channel_monitor_data['data']['RX2Power']['value']
            transceiver_dom_info_dict['rx3power'] = dom_channel_monitor_data['data']['RX3Power']['value']
            transceiver_dom_info_dict['rx4power'] = dom_channel_monitor_data['data']['RX4Power']['value']
            transceiver_dom_info_dict['tx1bias'] = dom_channel_monitor_data['data']['TX1Bias']['value']
            transceiver_dom_info_dict['tx2bias'] = dom_channel_monitor_data['data']['TX2Bias']['value']
            transceiver_dom_info_dict['tx3bias'] = dom_channel_monitor_data['data']['TX3Bias']['value']
            transceiver_dom_info_dict['tx4bias'] = dom_channel_monitor_data['data']['TX4Bias']['value']

        return transceiver_dom_info_dict

    def get_temperature(self, port_num):
        temperature_value = 0
        if self._is_valid_port(port_num) :
            transceiver_dom_info_dict = self.get_transceiver_dom_info_dict(port_num)
            if transceiver_dom_info_dict is not None :
                temperature_value = transceiver_dom_info_dict['temperature']
        return temperature_value

    def get_voltage(self, port_num):
        voltage_value = 0
        if self._is_valid_port(port_num) :
            transceiver_dom_info_dict = self.get_transceiver_dom_info_dict(port_num)
            if transceiver_dom_info_dict is not None :
                voltage_value = transceiver_dom_info_dict['voltage']
        return voltage_value 

    def get_tx_bias(self, port_num):
        tx_bias_dict_keys = [ 'tx1bias', 'tx2bias', 'tx3bias', 'tx4bias',]
        tx_bias_dict = dict.fromkeys(tx_bias_dict_keys, 'N/A')

        transceiver_dom_info_dict = self.get_transceiver_dom_info_dict(port_num)
        if transceiver_dom_info_dict is not None :
            tx_bias_dict['tx1bias']= transceiver_dom_info_dict['tx1bias']
            tx_bias_dict['tx2bias']= transceiver_dom_info_dict['tx2bias']
            tx_bias_dict['tx3bias']= transceiver_dom_info_dict['tx3bias']
            tx_bias_dict['tx4bias']= transceiver_dom_info_dict['tx4bias']
        return tx_bias_dict

    def get_rx_power(self, port_num):
        rx_power_dict_keys = ['rx1power', 'rx2power',    'rx3power', 'rx4power',]
        rx_power_dict = dict.fromkeys(rx_power_dict_keys, 'N/A')

        transceiver_dom_info_dict = self.get_transceiver_dom_info_dict(port_num)
        if transceiver_dom_info_dict is not None :
            rx_power_dict['rx1power'] =transceiver_dom_info_dict['rx1power']
            rx_power_dict['rx2power'] =transceiver_dom_info_dict['rx2power']
            rx_power_dict['rx3power'] =transceiver_dom_info_dict['rx3power']
            rx_power_dict['rx4power'] =transceiver_dom_info_dict['rx4power']
        return rx_power_dict

    def get_tx_power(self, port_num):
        tx_power_dict_keys = ['tx1power', 'tx2power',    'tx3power', 'tx4power',]
        tx_power_dict = dict.fromkeys(tx_power_dict_keys, 'N/A')

        transceiver_dom_info_dict = self.get_transceiver_dom_info_dict(port_num)
        if transceiver_dom_info_dict is not None :
            tx_power_dict['tx1power'] =transceiver_dom_info_dict['tx1power']
            tx_power_dict['tx2power'] =transceiver_dom_info_dict['tx2power']
            tx_power_dict['tx3power'] =transceiver_dom_info_dict['tx3power']
            tx_power_dict['tx4power'] =transceiver_dom_info_dict['tx4power']
        return tx_power_dict

    def get_rx_los(self, port_num):
        rx_los_state = []
        return rx_los_state
    def get_tx_fault(self, port_num):
        tx_fault_state = []
        return tx_fault_state
    def get_tx_disable(self, port_num):
        tx_disable_state = []
        return tx_disable_state
    def get_tx_disable_channel(self, port_num):
        tx_disable_state = []
        tx_disable_channel = 0
        return tx_disable_channel
    def get_power_override(self, port_num):
        power_override_state = False
        return power_override_state

    def get_transceiver_dom_threshold_info_dict(self, port_num):
        transceiver_dom_threshold_info_dict = {}

        dom_info_dict_keys = ['temphighalarm',    'temphighwarning',
                              'templowalarm',     'templowwarning',
                              'vcchighalarm',     'vcchighwarning',
                              'vcclowalarm',      'vcclowwarning',
                              'rxpowerhighalarm', 'rxpowerhighwarning',
                              'rxpowerlowalarm',  'rxpowerlowwarning',
                              'txpowerhighalarm', 'txpowerhighwarning',
                              'txpowerlowalarm',  'txpowerlowwarning',
                              'txbiashighalarm',  'txbiashighwarning',
                              'txbiaslowalarm',   'txbiaslowwarning'
                             ]
        transceiver_dom_threshold_info_dict = dict.fromkeys(dom_info_dict_keys, 'N/A')

        if port_num in self.osfp_ports:
            # Below part is added to avoid fail xcvrd, shall be implemented later
            return transceiver_dom_threshold_info_dict

        elif port_num in self.qsfp_ports:

            
            eeprom_raw = self._read_eeprom_devid_dom(port_num, self.IDENTITY_EEPROM_ADDR, 0)
            if eeprom_raw is None:
                return transceiver_dom_threshold_info_dict
            sfpd_obj = sff8436Dom()
            if sfpd_obj is None:
                return None

            # Dom Threshold data starts from offset 384
            # Revert offset back to 0 once data is retrieved
            #offset = 384
            offset = 0
            dom_module_threshold_raw = self._read_eeprom_specific_bytes(
                                     eeprom_raw,
                                     (offset + QSFP_MODULE_THRESHOLD_OFFSET),
                                     QSFP_MODULE_THRESHOLD_WIDTH)
            if dom_module_threshold_raw is not None:
                dom_module_threshold_data = sfpd_obj.parse_module_threshold_values(dom_module_threshold_raw, 0)
            else:
                return None

            dom_channel_threshold_raw = self._read_eeprom_specific_bytes(
                                      eeprom_raw,
                                      (offset + QSFP_CHANNL_THRESHOLD_OFFSET),
                                      QSFP_CHANNL_THRESHOLD_WIDTH)
            if dom_channel_threshold_raw is not None:
                dom_channel_threshold_data = sfpd_obj.parse_channel_threshold_values(dom_channel_threshold_raw, 0)
            else:
                return None


            # Threshold Data
            transceiver_dom_threshold_info_dict['temphighalarm'] = dom_module_threshold_data['data']['TempHighAlarm']['value']
            transceiver_dom_threshold_info_dict['temphighwarning'] = dom_module_threshold_data['data']['TempHighWarning']['value']
            transceiver_dom_threshold_info_dict['templowalarm'] = dom_module_threshold_data['data']['TempLowAlarm']['value']
            transceiver_dom_threshold_info_dict['templowwarning'] = dom_module_threshold_data['data']['TempLowWarning']['value']
            transceiver_dom_threshold_info_dict['vcchighalarm'] = dom_module_threshold_data['data']['VccHighAlarm']['value']
            transceiver_dom_threshold_info_dict['vcchighwarning'] = dom_module_threshold_data['data']['VccHighWarning']['value']
            transceiver_dom_threshold_info_dict['vcclowalarm'] = dom_module_threshold_data['data']['VccLowAlarm']['value']
            transceiver_dom_threshold_info_dict['vcclowwarning'] = dom_module_threshold_data['data']['VccLowWarning']['value']
            transceiver_dom_threshold_info_dict['rxpowerhighalarm'] = dom_channel_threshold_data['data']['RxPowerHighAlarm']['value']
            transceiver_dom_threshold_info_dict['rxpowerhighwarning'] = dom_channel_threshold_data['data']['RxPowerHighWarning']['value']
            transceiver_dom_threshold_info_dict['rxpowerlowalarm'] = dom_channel_threshold_data['data']['RxPowerLowAlarm']['value']
            transceiver_dom_threshold_info_dict['rxpowerlowwarning'] = dom_channel_threshold_data['data']['RxPowerLowWarning']['value']
            transceiver_dom_threshold_info_dict['txbiashighalarm'] = dom_channel_threshold_data['data']['TxBiasHighAlarm']['value']
            transceiver_dom_threshold_info_dict['txbiashighwarning'] = dom_channel_threshold_data['data']['TxBiasHighWarning']['value']
            transceiver_dom_threshold_info_dict['txbiaslowalarm'] = dom_channel_threshold_data['data']['TxBiasLowAlarm']['value']
            transceiver_dom_threshold_info_dict['txbiaslowwarning'] = dom_channel_threshold_data['data']['TxBiasLowWarning']['value']

        return transceiver_dom_threshold_info_dict
