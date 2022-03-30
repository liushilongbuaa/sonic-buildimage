import filecmp
import os
import subprocess
import json
import shutil

import tests.common_utils as utils

from unittest import TestCase

class TestBgpTemplate(TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.realpath(__file__))
        self.minigraph_dir = os.path.join(self.test_dir, 'minigraph')
        self.script_file = utils.PYTHON_INTERPRETTER + ' ' + os.path.join(self.test_dir, '..', 'sonic-cfggen')
        self.t1_minigraph = os.path.join(self.minigraph_dir, 'CO4SCH04001AALF.xml')
        self.tycoon_t1_minigraph = os.path.join(self.minigraph_dir, 'SN1-0102-0201-11T1.xml')
        self.m0_minigraph = os.path.join(self.minigraph_dir, 'MWH01-0100-0202-01M0.xml')
        self.dell_s6000_port_config = os.path.join(self.test_dir, 't0-sample-port-config.ini')
        self.hlx_port_config = os.path.join(self.test_dir, 'hlx-port-config.ini')
        self.a7060_port_config = os.path.join(self.test_dir, 'a7060-port-config.ini')
        self.deployment_id_asn_map = os.path.join(self.test_dir, 'deployment_id_asn_map.yml')
        self.device_metadata = os.path.join(self.test_dir, 'device_metadata.json')
        self.output_file = os.path.join(self.test_dir, 'output')

    def run_script(self, argument):
        print('CMD: sonic-cfggen %s' % argument)
        output = subprocess.check_output(self.script_file + ' ' + argument, shell=True)

        if utils.PY3x:
            output = output.decode()

        return output

    def run_diff(self, file1, file2):
        output = subprocess.check_output('diff -u {} {} || true'.format(file1, file2), shell=True)

        if utils.PY3x:
            output = output.decode()

        return output

    def tearDown(self):
        try:
            os.remove(self.output_file)
        except OSError:
            pass
