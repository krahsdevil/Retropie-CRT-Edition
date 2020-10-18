#!/usr/bin/python3
# -*- coding: utf-8 -*-


"""
Raspberry Pi overclock manager

Module to change configuration in config.txt for different raspberry pi
overclocking

https://github.com/krahsdevil/crt-for-retropie/

Copyright (C)  2018/2020 -krahs- - https://github.com/krahsdevil/
Copyright (C)  2020 dskywalk - http://david.dantoine.org

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation, either version 2 of the License, or (at your option) any
later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
import os, sys, traceback, re
import time, subprocess
import logging

sys.dont_write_bytecode = True

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(SCRIPT_DIR + "/../"))
from main_paths import MODULES_PATH
sys.path.append(MODULES_PATH)

from launcher_module.core_paths import TMP_LAUNCHER_PATH, RASP_BOOTCFG_FILE
from module_cable.cable_utils import ini_sect_clean_file, ini_sect_get_key, \
                                     ini_sect_set_key, ini_sect_empty_section, \
                                     ini_sect_add_key, ini_set_check_section, \
                                     ini_sect_create_section, ini_sect_get_keys, \
                                     ini_outofsect_get_key
from launcher_module.file_helpers import ini_getlist, generate_random_temp_filename, \
                                         remove_line, remove_file, touch_file, ini_get, \
                                         md5_file

LOG_PATH = os.path.join(TMP_LAUNCHER_PATH, "CRT_OCManager.log")
EXCEPTION_LOG = os.path.join(TMP_LAUNCHER_PATH, "backtrace.log")

__VERSION__ = '0.1'
__DEBUG__ = logging.INFO # logging.ERROR
CLEAN_LOG_ONSTART = True

class OCMNGR(object):
    """ virtual class for overclocking management """
    p_mProfile  = {'id'      : [],
                   'section' : 'CRT-OC',
                   'desc'    : 'Not Compatible',
                   'recval'  : {},
                   'values'  : {},
                   'config'  : {},
                  }

    m_sRPIModel  = ""
    m_dOCConfig  = {}
    m_bOCEnabled = None
    m_bRPIComp = None

    m_sMD5_Prev  = ""
    m_sTemp = ""        # temp file
    
    def __init__(self):
        self.__temp()
        logging.info("INFO: Launching overclock manager")
        self.create_rpi_config()
        self.clean_oc_options()
        
    def create_rpi_config(self):
        p_lProfiles = [self.load_profile_0, self.load_profile_1,
                       self.load_profile_2]
        p_bProfFound = False
        self.get_rpi_id()
        for pf in p_lProfiles:
            p_lList = {}
            p_lList = pf()
            hwd = self.m_sRPIModel
            if len(self.m_sRPIModel) > 6:
                hwd = self.m_sRPIModel[-6:]
            if hwd in p_lList['id']:
                p_bProfFound = True
                self.m_bRPIComp = True
                self.load_rpi_config(p_lList)
                break
        if not p_bProfFound: 
            self.m_bRPIComp = False
            self.m_dOCConfig = self.p_mProfile

    def clean_oc_options(self):
        p_lOCFullOpt = ['arm_freq', 'gpu_freq', 'core_freq', 'h264_freq',
                        'isp_freq', 'v3d_freq', 'hevc_freq', 'sdram_freq',
                        'over_voltage', 'over_voltage_sdram', 'over_voltage_sdram_c',
                        'over_voltage_sdram_i', 'over_voltage_sdram_p', 'force_turbo',
                        'initial_turbo', 'arm_freq_min', 'core_freq_min',
                        'gpu_freq_min', 'h264_freq_min', 'isp_freq_min', 
                        'v3d_freq_min', 'hevc_freq_min', 'sdram_freq_min', 
                        'over_voltage_min', 'temp_limit', 'temp_soft_limit',
                        'sdram_schmoo', 'avoid_pwm_pll',
                        ]
        p_dOptToMove = []
        p_lSection   = []
        p_bSectFound = False
        if ini_set_check_section(RASP_BOOTCFG_FILE, self.m_dOCConfig['section']):
            p_lSection = ini_sect_get_keys(RASP_BOOTCFG_FILE, self.m_dOCConfig['section'])
            p_bSectFound = True
        for opt in p_lOCFullOpt:
            value = ini_get(RASP_BOOTCFG_FILE, opt)
            if value:
                p_bFound = False
                for item in p_lSection:
                    if opt == item[0]: p_bFound = True
                if not p_bFound: 
                    try: value = int(value)
                    except: pass
                    p_dOptToMove.append([opt, value])
        valueOut = ini_outofsect_get_key(RASP_BOOTCFG_FILE, self.m_dOCConfig['section'],
                                         'dtparam=sd_overclock')
        valueIn = ini_sect_get_key(RASP_BOOTCFG_FILE, self.m_dOCConfig['section'],
                                         'dtparam=sd_overclock')
        if valueOut:
            if valueIn: 
                try: valueIn = int(valueIn)
                except: pass
                p_dOptToMove.append(['dtparam=sd_overclock', valueIn])
            else:
                try: valueOut = int(valueOut)
                except: pass            
                p_dOptToMove.append(['dtparam=sd_overclock', valueOut])

        if p_dOptToMove:
            self.__clone_cfg()
            if not p_bSectFound: 
                ini_sect_create_section(self.m_sTemp, self.m_dOCConfig['section'])
            for opt in p_dOptToMove:
                remove_line(self.m_sTemp, opt[0])
                if opt[1] not in self.m_dOCConfig['values'][opt[0]][3]:
                    opt[1] = self.m_dOCConfig['values'][opt[0]][0]
                ini_sect_add_key(self.m_sTemp, self.m_dOCConfig['section'],
                                 opt[0], opt[1])
            self.__upload_cfg()
        
    def load_profile_0(self):
        """ Create profile for Raspberry Pi 3A+/3B+ """
        p_lProfile = {'id'      : ['a020d3', '9020e0'],
                      'section' : 'CRT-OC',
                      'desc'    : 'Pi3A+/Pi3B+',
                      'values'  : {'arm_freq'            : [1400, 1600, 10, []],
                                   'gpu_freq'            : [ 400,  550, 10, []],
                                   'core_freq'           : [ 400,  550, 10, []],
                                   'sdram_freq'          : [ 500,  600, 10, []],
                                   'sdram_schmoo'        : ['none', 1,  1, 
                                                           ['none', '0x02000020']],
                                   'over_voltage'        : [   0,    6,  1, []],
                                   'over_voltage_sdram'  : [   0,    6,  1, []],
                                   'dtparam=sd_overclock': [  50,  100, 10, []],
                                  },
                      'recval'  : {},
                      'config'  : {'arm_freq'            : 0,
                                   'gpu_freq'            : 0,
                                   'core_freq'           : 0,
                                   'sdram_freq'          : 0,
                                   'sdram_schmoo'        : 0,
                                   'over_voltage'        : 0,
                                   'over_voltage_sdram'  : 0,
                                   'dtparam=sd_overclock': 0,
                                  },
                     }
        for item in p_lProfile['values']:
            if not p_lProfile['values'][item][3]:
                for i in range(p_lProfile['values'][item][0], 
                         p_lProfile['values'][item][1] + p_lProfile['values'][item][2], 
                         p_lProfile['values'][item][2]):
                    p_lProfile['values'][item][3].append(i)

        return p_lProfile

    def load_profile_1(self):
        """ Create profile for Raspberry Pi 3B """
        p_lProfile = {'id'      : ['a02082', 'a22082', 'a32082'],
                      'section' : 'CRT-OC',
                      'desc'    : 'Pi3B',
                      'values'  : {'arm_freq'            : [1200, 1400, 10, []],
                                   'gpu_freq'            : [ 400,  550, 10, []],
                                   'core_freq'           : [ 400,  550, 10, []],
                                   'sdram_freq'          : [ 450,  550, 10, []],
                                   'sdram_schmoo'        : ['none', 1,  1, 
                                                           ['none', '0x02000020']],
                                   'over_voltage'        : [   0,    6,  1, []],
                                   'over_voltage_sdram'  : [   0,    6,  1, []],
                                   'dtparam=sd_overclock': [  50,  100, 10, []],
                                  },
                      'recval'  : {},
                      'config'  : {'arm_freq'            : 0,
                                   'gpu_freq'            : 0,
                                   'core_freq'           : 0,
                                   'sdram_freq'          : 0,
                                   'sdram_schmoo'        : 0,
                                   'over_voltage'        : 0,
                                   'over_voltage_sdram'  : 0,
                                   'dtparam=sd_overclock': 0,
                                  },
                     }
        for item in p_lProfile['values']:
            if not p_lProfile['values'][item][3]:
                for i in range(p_lProfile['values'][item][0], 
                         p_lProfile['values'][item][1] + p_lProfile['values'][item][2], 
                         p_lProfile['values'][item][2]):
                    p_lProfile['values'][item][3].append(i)

        return p_lProfile

    def load_profile_2(self):
        """ Create profile for Raspberry Pi 2B """
        p_lProfile = {'id'      : ['a01040', 'a01041', 'a21041'],
                      'section' : 'CRT-OC',
                      'desc'    : 'Pi2B',
                      'values'  : {'arm_freq'            : [ 900, 1100, 10, []],
                                   'gpu_freq'            : [ 250,  350, 10, []],
                                   'core_freq'           : [ 250,  350, 10, []],
                                   'sdram_freq'          : [ 400,  500, 10, []],
                                   'sdram_schmoo'        : ['none', 1,  1, 
                                                           ['none', '0x02000020']],
                                   'over_voltage'        : [   0,    6,  1, []],
                                   'over_voltage_sdram'  : [   0,    6,  1, []],
                                   'dtparam=sd_overclock': [  50,  100, 10, []],
                                  },
                      'recval'  : {'arm_freq'            : 1000,
                                   'core_freq'           :  500,
                                   'sdram_freq'          :  500,
                                   'over_voltage'        :    2,
                                  },
                      'config'  : {'arm_freq'            : 0,
                                   'gpu_freq'            : 0,
                                   'core_freq'           : 0,
                                   'sdram_freq'          : 0,
                                   'sdram_schmoo'        : 0,
                                   'over_voltage'        : 0,
                                   'over_voltage_sdram'  : 0,
                                   'dtparam=sd_overclock': 0,
                                  },
                     }
        for item in p_lProfile['values']:
            if not p_lProfile['values'][item][3]:
                for i in range(p_lProfile['values'][item][0], 
                         p_lProfile['values'][item][1] + p_lProfile['values'][item][2], 
                         p_lProfile['values'][item][2]):
                    p_lProfile['values'][item][3].append(i)

        return p_lProfile

    def get_rpi_id(self):
        p_sCMD = 'cat /proc/cpuinfo | grep Revision'
        try: p_sOutput = subprocess.check_output(p_sCMD, shell=True).decode("utf-8")
        except: p_sOutput = ""
        if p_sOutput:
            p_sModel = re.sub(r' +', " ", p_sOutput).split(':')[1]
            p_sModel = p_sModel.replace('\00', '').strip()
            self.m_sRPIModel = p_sModel
        else: self.m_sRPIModel = "Not Found"

    def status(self):
        if not self.compatible(): return False
        return self.m_bOCEnabled

    def compatible(self):
        return self.m_bRPIComp

    def is_base_value(self, p_sINI, p_sValue):
        if self.m_dOCConfig['values'][p_sINI][0] == p_sValue:
            return True
        return False
        
    def rec_values(self):
        if self.m_dOCConfig['recval']: return True
        return False

    def apply_rec_values(self):
        for p_sINI in self.m_dOCConfig['config']:
            if p_sINI in self.m_dOCConfig['recval']:
                value = self.m_dOCConfig['recval'][p_sINI]
            else: value = self.m_dOCConfig['values'][p_sINI][3][0]
            self.set_oc_value(p_sINI, value)

    def enable(self):
        if self.m_bOCEnabled: return False
        self.__clone_cfg()
        ini_sect_empty_section(self.m_sTemp, self.m_dOCConfig['section'], True)
        ini_sect_create_section(self.m_sTemp, self.m_dOCConfig['section'])
        self.__upload_cfg()

    def disable(self):
        if not self.m_bOCEnabled: return False
        self.__clone_cfg()
        ini_sect_empty_section(self.m_sTemp, self.m_dOCConfig['section'], True)
        self.__upload_cfg()

    def load_rpi_config(self, p_dConfig):
        if self.m_sMD5_Prev != md5_file(RASP_BOOTCFG_FILE):
            if ini_set_check_section(RASP_BOOTCFG_FILE, p_dConfig['section']):
                self.m_bOCEnabled = True
                for ini in p_dConfig['config']:
                    value = ini_sect_get_key(RASP_BOOTCFG_FILE, p_dConfig['section'], ini)
                    if value != None: 
                        try: value = int(value)
                        except Exception as e: pass
                        if value not in p_dConfig['values'][ini][3]:
                            value = p_dConfig['values'][ini][0]
                        p_dConfig['config'][ini] = value
                    else: 
                        p_dConfig['config'][ini] = p_dConfig['values'][ini][0]
            else:
                self.m_bOCEnabled = False
                for ini in p_dConfig['values']:
                    p_dConfig['config'][ini] = p_dConfig['values'][ini][0]
            m_sMD5_Prev = md5_file(RASP_BOOTCFG_FILE)
        self.m_dOCConfig = p_dConfig.copy()

    def set_oc_value(self, p_sINI, p_sValue):
        if not self.m_bOCEnabled: return
        if not p_sINI in self.m_dOCConfig['config']: return False
        self.__clone_cfg()
        if p_sValue == self.m_dOCConfig['values'][p_sINI][3][0]:
            remove_line(self.m_sTemp, p_sINI)
        else:
            if not ini_sect_set_key(self.m_sTemp, self.m_dOCConfig['section'], p_sINI, p_sValue):
                ini_sect_add_key(self.m_sTemp, self.m_dOCConfig['section'], p_sINI, p_sValue)
        self.__upload_cfg()

    def get_ini_values_list(self, p_sINI):
        try: p_lList = self.m_dOCConfig['values'][p_sINI][3]
        except: p_lList = []
        return p_lList

    def get_ini(self, p_sINI):
        if not p_sINI in self.m_dOCConfig['config']: return None
        #self.load_rpi_config(self.m_dOCConfig)
        return self.m_dOCConfig['config'][p_sINI]

    def get_model_id(self):
        return self.m_sRPIModel

    def get_model(self):
        return self.m_dOCConfig['desc']

    def __clone_cfg(self):
        self.m_sTemp = generate_random_temp_filename(RASP_BOOTCFG_FILE)
        os.system('cp %s %s' % (RASP_BOOTCFG_FILE, self.m_sTemp))

    def __upload_cfg(self, p_bReload = True):
        ini_sect_clean_file(self.m_sTemp)
        os.system('sudo cp %s %s' % (self.m_sTemp, RASP_BOOTCFG_FILE))
        self.__clean()
        if p_bReload: self.load_rpi_config(self.m_dOCConfig)

    def __clean(self):
        if os.path.exists(self.m_sTemp):
            remove_file(self.m_sTemp)
        self.m_sTemp = ""
        
    def __temp(self):
        if CLEAN_LOG_ONSTART:
            remove_file(LOG_PATH)
        logging.basicConfig(filename=LOG_PATH, level=__DEBUG__,
        format='[%(asctime)s] %(levelname)s - %(filename)s:%(funcName)s - %(message)s')
