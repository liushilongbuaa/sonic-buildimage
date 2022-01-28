#!/usr/bin/env python                                                                                                                               
#
# sfputil.py
#
# SFP utility functions
#

try:
    import fnmatch, subprocess, time , os.path
    from sonic_platform.globals import PlatformGlobalData
    from sonic_platform.sfputil import SfpUtil

except ImportError as e:
    raise ImportError (str(e) + "- required module not found")


class SfpUtilN3132gx(SfpUtil):
    """Platform-specific SfpUtil class"""


    
    def __init__(self, port_start, num_ports, platform_global_data, sfps_data):
        self.EEPROM_OFFSET = 20
        self.GPIO_QSFP_RESET_START = 400
        self.GPIO_QSFP_PRESENCE_START = 432
        super(SfpUtilN3132gx, self).__init__(port_start, num_ports, platform_global_data, sfps_data)

    def get_presence(self , port_num):
        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.port_end:
            return False

        qsfp_presence_direction_device_file_path="/sys/class/gpio/gpio{0}/direction".format(self.GPIO_QSFP_PRESENCE_START+port_num)

        try:
            direction_file = open(qsfp_presence_direction_device_file_path, "w")
        except IOError as e:
            print ("Error: unable to open file: %s" % str(e))
            return False

        # First, set the direction to "in" to enable reading value
        direction_file.write("in")
        direction_file.close()

        qsfp_presence_value_device_file_path = "/sys/class/gpio/gpio{}/value".format(self.GPIO_QSFP_PRESENCE_START+port_num)

        try:
            value_file = open(qsfp_presence_value_device_file_path, "r")
        except IOError as e:
            print ("Error: unable to open file: %s" % str(e))
            return False

        content = value_file.readline().rstrip()
        value_file.close()

        if content == "1":
            return True

        return False


    def get_low_power_mode(self, port_num):
        #raise NotImplementedError
        return False

    def set_low_power_mode(self, port_num, lpmode):
        raise NotImplementedError
    
    def reset(self,port_num):
        if port_num < self.port_start or port_num > self.port_end:
            return False

        qsfp_reset_direction_device_file_path = "/sys/class/gpio/gpio{0}/direction".format(self.GPIO_QSFP_RESET_START+port_num)

        try:
            direction_file = open(qsfp_reset_direction_device_file_path, "w")
        except IOError as e:
            print ("Error: unable to open file: %s" % str(e))
            return False

        # First, set the direction to "out" to enable writing value
        direction_file.write("out")
        direction_file.close()

        qsfp_reset_value_device_file_path = "/sys/class/gpio/gpio{}/value".format(self.GPIO_QSFP_RESET_START +port_num)

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


    def work_around(self,port_num):        
        file_path = self._port_to_eeprom_mapping[port_num]
        try:
            sysfsfile_eeprom = open(file_path, mode="rb", buffering=0)
        except IOError:
            print("Error: reading sysfs file %s" % file_path)
            return None

        if port_num in self.qsfp_ports:
            byte127 = self._read_eeprom_specific_bytes(sysfsfile_eeprom, 127, 1)[0]

        sysfsfile_eeprom.close()
        return True


    def get_transceiver_change_event(self, timeout=0):
        end_time = time.time() + timeout
        p_pres_dict = {}
        while True:
            xcvrs = [ 1 if ((self.get_presence(port)) == True) else 0 for port in range(self.port_start, self.NUM_PORTS) ]

            if self._xcvr_presence is not None:
                # Previous state present. Check any change from previous state
                for p in range(self.port_start, self.NUM_PORTS):
                    if self._xcvr_presence[p] != xcvrs[p]:
                        # Add the change to dict
                        d = {str(p) : str(xcvrs[p])}
                        p_pres_dict.update(d)
                        #Reset the XCVR if it is inserted
                        if xcvrs[p] == 1 :
                            self.reset(p)

                if len(p_pres_dict) != 0 :
                    time.sleep(2)
                    for p in range(self.port_start, self.NUM_PORTS):
                        if self._xcvr_presence[p] != xcvrs[p]:
                            if xcvrs[p] == 1 :
                                self.work_around(p)

            else:
                for p in range(self.port_start, self.NUM_PORTS):
                    # Add the change to dict
                    if xcvrs[p] == 1:
                        d = {str(p) : str(xcvrs[p])}
                        p_pres_dict.update(d)
                        self.reset(p)
                if len(p_pres_dict) != 0 :
                    time.sleep(2)
                    for p in range(self.port_start, self.NUM_PORTS):
                        if xcvrs[p] == 1:    
                            self.work_around(p)


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

