import fnmatch
import os

try:
    from sonic_psu.psu_base import PsuBase
except ImportError as e:
    raise ImportError (str(e) + "- required module not found")

class PsuUtil(PsuBase):
    """Platform-specific PSUutil class"""

    def __init__(self):
        PsuBase.__init__(self)

        self.psu_num = 2
        self.psu_buses = [7, 8]
        self.psu_path = "/sys/bus/i2c/devices/{}-005b/hwmon/"
        self.psu_oper_status = "in1_input"
        self.psu_presence = "/sys/class/gpio/gpio{}/value"
        self.psu_gpios = [494, 495]
        self.psu_input_threshold = 80000


    def get_num_psus(self):
        return self.psu_num

    def get_psu_status(self, index):
        if index is None:
            return False

        #index from 1
        if index < 1 :
            return False
        if index > self.psu_num :
            return False

        status = 0
        bus = self.psu_buses[index-1]
        filename = None
        for dirname in os.listdir(self.psu_path.format(bus)):
            if fnmatch.fnmatch(dirname, 'hwmon?'):
                filename = self.psu_path.format(bus) + dirname + '/' + self.psu_oper_status
                break
        if filename is None:
            return False

        try:
            with open(filename, 'r') as power_status:
                if int(power_status.read()) <= self.psu_input_threshold :
                    return False
                else:
                    status = 1
        except IOError:
            return False
        return status == 1

    def get_psu_presence(self, index):
        if index is None:
            return False

        #index from 1
        if index < 1 :
            return False
        if index > self.psu_num :
            return False

        status = 0
        gpio = self.psu_gpios[index-1]
        try:
            with open(self.psu_presence.format(gpio), 'r') as power_presence:
                if int(power_presence.read()) == 0 :
                    return False
                else:
                    status = 1
        except IOError:
            return False
        return status == 1
