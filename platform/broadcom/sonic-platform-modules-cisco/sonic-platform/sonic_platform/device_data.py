DEVICE_DATA = {
    'x86_64-n3164-r0': {
        'globals': {
            #frontpanel port leds related
            'fp_start_index' : 1,
            'max_fp_num' : 64,

            #Thermal thresholds
            'min_temperature_threshold' : 55.0, 
            'max_temperature_threshold' : 85.0,
            'min_blue_fans_speed' : 60,
            'min_red_fans_speed' : 60,
            'max_blue_fans_speed' : 90, 
            'max_red_fans_speed' : 90,
            'fan_speed_tolerance' : 15,
            'fan_pwm_path_format' : 1,
            'sensors_path_format' : 2,
            'F_fan_curve_slope' : 120.09,
            'R_fan_curve_slope' : 112.82,
            'psu_eeprom_data_format' : 0,
            'isN9k' : 1,
            'thermal_high_thresh_hysteresis' : 5.0,
            'thermal_crit_thresh_hysteresis' : 10.0,
            'blue_fans_inlet_temp_threshold' : 35.0,
            'red_fans_inlet_temp_threshold' : 35.0,
            'reboot_gpio' : 133,
            'shutdown_gpio' : 134,
            'transceiver_enable_high_power_class': 0,
            'max_supplied_power' : 1200.0,

            #Components and their num instances in platform
            'IOFPGA' : 1,
            'MIFPGA' : 2,
            'BIOS'   : 2  #num partitions
        },
        'fans': {
            'drawer_num': 2,
            'fan_drawer': [{'fan_num' : 2,
                            'fan':[{'bus' : 33 , 'addr' : "002e", 'gpio_presence' : 122,'gpio_direction' : 172},
                                   {'bus':33,'addr' : "002e" ,'gpio_presence' : 122,'gpio_direction' : 172}]
                           },
                           {'fan_num' : 2,
                            'fan':[{'bus': 33,'addr' : "002c",'gpio_presence' : 123,'gpio_direction' : 173},
                                   {'bus' : 33 , 'addr' : "002c", 'gpio_presence' : 123,'gpio_direction' : 173}]}]
        },
        'psus': {
            'psu_num': 2,
            'psu' : [{'bus' : 34, 'addr' : "0058", 'eeprom_addr' : "0050",'gpio' : 116, 'fan_num':1,'hot_swappable': True,'led_num' :1, 'is_fan_sw_controllable' : False },
                {'bus' : 35, 'addr' : "0058", 'eeprom_addr' : "0050",'gpio' : 117,'fan_num':1,'hot_swappable':True, 'led_num' : 1, 'is_fan_sw_controllable' : False}]

        },
        'thermals': {
            'thermal_num': 4,
            'temp' : [
                {'name' : "REAR (UPPER BOARD)", 'bus' : 40 , 'addr' : "0048", 'location': 'near Fans', 'minor': 70, 'major': 80},
                {'name' : "FRONT (UPPER BOARD)",'bus' : 40 , 'addr' : "0049", 'location': 'near front panel ports', 'minor': 42, 'major': 60},
                {'name' : "REAR (LOWER BOARD)", 'bus' : 42 , 'addr' : "0048", 'location': 'near Fans', 'minor': 70, 'major': 80},
                {'name' : "FRONT (LOWER BOARD)" , 'bus' : 42 , 'addr': "0049", 'location': 'near front panel ports', 'minor': 42, 'major': 60}
                ]
        },
        'sfps': {
            'fp_num' : 64,
            'fp_start_index' : 1,
            'sfp' : [
                {'type' : 'QSFP', 'sfp_num' : 64, 'start_index' : 1},
                {'type' : 'SFP', 'sfp_num' : 0, 'start_index' : 0}
                ]
        }
    },
    'x86_64-m3000-r1':{
        'globals': {
            #frontpanel port leds related
            'fp_start_index' : 1,
            'max_fp_num' : 32, 

            #Thermal thresholds
            'min_temperature_threshold' : 55.0, 
            'max_temperature_threshold' : 85.0,
            'min_blue_fans_speed' : 60,
            'min_red_fans_speed' : 60,
            'max_blue_fans_speed' : 90, 
            'max_red_fans_speed' : 90,
            'fan_speed_tolerance' : 20,
            'fan_pwm_path_format' : 2,
            'sensors_path_format' : 1,
            'F_fan_curve_slope' : 159,
            'R_fan_curve_slope' : 120,
            'psu_eeprom_data_format' : 1,
            'isN9k' : 0,
            'thermal_high_thresh_hysteresis' : 5.0,
            'thermal_crit_thresh_hysteresis' : 10.0,
            'blue_fans_inlet_temp_threshold' : 35.0,
            'red_fans_inlet_temp_threshold' : 35.0,
            #'reboot_gpio' : 133,
            #'shutdown_gpio' : 134,
            'transceiver_enable_high_power_class': 0,
            'max_supplied_power' : 400.0,

            #Components and their num instances in platform
            'IOFPGA' : 0,
            'MIFPGA' : 0,
            'BIOS'   : 1  #num partitions
        },
        'fans': {
            'drawer_num': 4,
            'fan_drawer': [{'fan_num' : 2,'fan':[{'bus': 1,'addr' : "0058",'gpio_presence' : 500,'gpio_direction' :496 },
                                                 {'bus': 1,'addr' : "0058",'gpio_presence' : 500,'gpio_direction' :496 }]},
                           {'fan_num' : 2,'fan':[{'bus': 1,'addr' : "0058",'gpio_presence' : 501,'gpio_direction' :497 },
                                                 {'bus': 1,'addr' : "0058",'gpio_presence' : 501,'gpio_direction' :497 }]},
                           {'fan_num' : 2,'fan':[{'bus': 1,'addr' : "0058",'gpio_presence' : 502,'gpio_direction' :498 },
                                                 {'bus': 1,'addr' : "0058",'gpio_presence' : 502,'gpio_direction' :498 }]},
                           {'fan_num' : 2,'fan':[{'bus': 1,'addr' : "0058",'gpio_presence' : 503,'gpio_direction' :499 },
                                                 {'bus': 1,'addr' : "0058",'gpio_presence' : 503,'gpio_direction' :499 }]}]
        },
        'psus': {
            'psu_num': 2,
            'psu' : [{'bus' : 8, 'addr' : "005b", 'eeprom_addr' : "0053",'gpio' : 494, 'fan_num':1,'hot_swappable': True,'led_num' :1 , 'is_fan_sw_controllable' : True},
                {'bus' : 7, 'addr' : "005b", 'eeprom_addr' : "0053",'gpio' : 495, 'fan_num':1,'hot_swappable': True,'led_num' :1, 'is_fan_sw_controllable' : True}]
        },
        'thermals': {
            'thermal_num': 4,
            'temp' : [{'name' : "Internal (D0)", 'bus' : 1 , 'addr' : "0058", 'location': 'near Fans','minor': 42,'major':70},
                {'name' : "Front-Middle (D1)", 'bus' : 1 , 'addr' :"0058",'location':'near front panel ports','minor': 56,'major':70},
                {'name' : "Front-Left (D2)", 'bus' : 1 , 'addr' : "0058",'location':'near front panel ports','minor': 44,'major':70},
                {'name' : "Back (D3)", 'bus' : 1 , 'addr' : "0058", 'location':'near Fans','minor': 42 ,'major':70}]
        },
        'sfps': {
            'fp_num' : 32,
            'fp_start_index' : 1,
            'sfp' : [
                {'type' : 'QSFP', 'sfp_num' : 32, 'start_index' : 1},
                {'type' : 'SFP', 'sfp_num' : 0, 'start_index' : 0}
                ]
        }
    },
    'x86_64-m3000-r0':{
        'globals': {
            #frontpanel port leds related
            'fp_start_index' : 1,
            'max_fp_num' : 32, 

            #Thermal thresholds
            'min_temperature_threshold' : 55.0, 
            'max_temperature_threshold' : 85.0,
            'min_blue_fans_speed' : 60,
            'min_red_fans_speed' : 60,
            'max_blue_fans_speed' : 90, 
            'max_red_fans_speed' : 90,
            'fan_speed_tolerance' : 20,
            'fan_pwm_path_format' : 2,
            'sensors_path_format' : 1,
            'F_fan_curve_slope' : 159,
            'R_fan_curve_slope' : 120,
            'psu_eeprom_data_format' : 1,
            'isN9k' : 0,
            'thermal_high_thresh_hysteresis' : 5.0,
            'thermal_crit_thresh_hysteresis' : 10.0,
            'blue_fans_inlet_temp_threshold' : 35.0,
            'red_fans_inlet_temp_threshold' : 35.0,
            #'reboot_gpio' : 133,
            #'shutdown_gpio' : 134,
            'transceiver_enable_high_power_class': 0,
            'max_supplied_power' : 400.0,

            #Components and their num instances in platform
            'IOFPGA' : 0,
            'MIFPGA' : 0,
            'BIOS'   : 1  #num partitions
        },
        'fans': {
            'drawer_num': 4,
            'fan_drawer': [{'fan_num' : 2,'fan':[{'bus': 1,'addr' : "0058",'gpio_presence' : 500,'gpio_direction' :496 },
                                                 {'bus': 1,'addr' : "0058",'gpio_presence' : 500,'gpio_direction' :496 }]},
                           {'fan_num' : 2,'fan':[{'bus': 1,'addr' : "0058",'gpio_presence' : 501,'gpio_direction' :497 },
                                                 {'bus': 1,'addr' : "0058",'gpio_presence' : 501,'gpio_direction' :497 }]},
                           {'fan_num' : 2,'fan':[{'bus': 1,'addr' : "0058",'gpio_presence' : 502,'gpio_direction' :498 },
                                                 {'bus': 1,'addr' : "0058",'gpio_presence' : 502,'gpio_direction' :498 }]},
                           {'fan_num' : 2,'fan':[{'bus': 1,'addr' : "0058",'gpio_presence' : 503,'gpio_direction' :499 },
                                                 {'bus': 1,'addr' : "0058",'gpio_presence' : 503,'gpio_direction' :499 }]}]
        },
        'psus': {
            'psu_num': 2,
            'psu' : [{'bus' : 8, 'addr' : "005b", 'eeprom_addr' : "0053",'gpio' : 494, 'fan_num':1,'hot_swappable': True,'led_num' :1 , 'is_fan_sw_controllable' : True},
                {'bus' : 7, 'addr' : "005b", 'eeprom_addr' : "0053",'gpio' : 495, 'fan_num':1,'hot_swappable': True,'led_num' :1, 'is_fan_sw_controllable' : True}]
        },
        'thermals': {
            'thermal_num': 4,
            'temp' : [{'name' : "Internal (D0)", 'bus' : 1 , 'addr' : "0058", 'location': 'near Fans','minor': 42,'major':70},
                {'name' : "Front-Middle (D1)", 'bus' : 1 , 'addr' :"0058",'location':'near front panel ports','minor': 56,'major':70},
                {'name' : "Front-Left (D2)", 'bus' : 1 , 'addr' : "0058",'location':'near front panel ports','minor': 44,'major':70},
                {'name' : "Back (D3)", 'bus' : 1 , 'addr' : "0058", 'location':'near Fans','minor': 42 ,'major':70}]
        },
        'sfps': {
            'fp_num' : 32,
            'fp_start_index' : 1,
            'sfp' : [
                {'type' : 'QSFP', 'sfp_num' : 32, 'start_index' : 1},
                {'type' : 'SFP', 'sfp_num' : 0, 'start_index' : 0}
                ]
        }
    }
}
