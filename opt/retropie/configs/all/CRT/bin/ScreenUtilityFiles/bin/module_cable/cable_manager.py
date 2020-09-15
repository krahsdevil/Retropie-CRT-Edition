#!/usr/bin/python3
# -*- coding: utf-8 -*-


"""
RGB cable manager for Retropie CRT Edition

Module to change configuration in config.txt for different RGB cables by -krahs-
CRT Daemon for jamma controls (third party software activator)

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
import os, sys, traceback
import time
import logging

sys.dont_write_bytecode = True

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(SCRIPT_DIR + "/../"))
from main_paths import MODULES_PATH
sys.path.append(MODULES_PATH)

from module_cable.controls_mapping import CTRLSMgmt
from module_cable.cable_utils import *
from launcher_module.core_paths import *
from launcher_module.file_helpers import ini_getlist, generate_random_temp_filename, \
                                         add_line, remove_file, touch_file, ini_get, \
                                         md5_file
from launcher_module.utils import check_process, wait_process, \
                                  show_info, menu_options

LOG_PATH = os.path.join(TMP_LAUNCHER_PATH, "CRT_RGB_Cable_Selector.log")
EXCEPTION_LOG = os.path.join(TMP_LAUNCHER_PATH, "backtrace.log")

__VERSION__ = '0.1'
__DEBUG__ = logging.INFO # logging.ERROR
CLEAN_LOG_ONSTART = True

class CableMNGR(object):
    """ virtual class for USB Automount enable/disable/eject """
    m_lCableList = {}   # list of cables and configs
    m_lCableLab  = []   # list of cable labels, ids and descriptions
    m_iCableID = None   # current id of the cable
    m_bNeedFix = False  # wrong config for current cable
    m_sTemp = ""        # temp file
    m_lBaseCfg = {'CRT-BASE'    : [['disable_overscan', '1'],
                                   ['overscan_scale', '1'],
                                   ['framebuffer_depth', '32'],
                                   ['enable_dpi_lcd', '1'],
                                   ['display_default_lcd', '1'],
                                   ['dpi_group', '2'],
                                   ['dpi_mode', '87']],
                  'CRT-RECOVERY': [['crt_recovery_enabled', '0'],
                                   ['crt_recovery_mode', 'DEFAULT'],
                                   ['crt_daemon_enabled', '1']]}
    def __init__(self):
        self.__temp()
        logging.info("INFO: Launching CRT cable selector")
        self.create_cable_list()
        self.check_cable()
        self.m_oDaemon = CRTdaemon()
        self.m_oKeyboardMNGR = CTRLSMgmt()

    def create_cable_list(self):
        p_lProfiles = [self.load_profile_0, self.load_profile_1, 
                       self.load_profile_2]
        for pf in p_lProfiles:
            p_lList = {}
            p_lList = pf()
            self.m_lCableLab.append([p_lList['id'], p_lList['label'],
                                     p_lList['desc']])
            CableID = p_lList['id']
            self.m_lCableList.update({CableID: p_lList})

    def load_profile_0(self):
        """ Create profile for RGB-PI, JAMMA RGB-PI, PICRT and JAMMA PICRT """
        p_lProfile = {'id'    : 0,
                      'label' : 'Type 0',
                      'desc'  : 'VGA666/PI2SCART',
                      'kbd'   : False,
                      'config': {}}
        p_lCfg01   = {'CRT-SOUND'       : [['dtparam', 'audio=on'],
                                           ['audio_pwm_mode', '3'],
                                           ['disable_audio_dither', '1']]}
        p_lCfg02   = {'CRT-CABLE'       : [['crt_cable_type', '0']]}
        p_lCfg03   = {'CRT-I2C0'        : []}
        p_lCfg04   = {'CRT-VGA666-MODE' : [['dtoverlay', 'vga666']]}

        p_lProfile['config'].update(self.m_lBaseCfg)
        p_lProfile['config'].update(p_lCfg01)
        p_lProfile['config'].update(p_lCfg02)
        p_lProfile['config'].update(p_lCfg03)
        p_lProfile['config'].update(p_lCfg04)
        return p_lProfile

    def load_profile_1(self):
        """ Create profile for RGB-PI, JAMMA RGB-PI, PICRT and JAMMA PICRT """
        p_lProfile = {'id'   : 1,
                      'label': 'Type 1',
                      'desc' : 'RGB-Pi/PiCRT',
                      'kbd'   : False,
                      'config': {}}
        p_lCfg01   = {'CRT-SOUND'       : [['dtparam', 'audio=on'],
                                           ['audio_pwm_mode', '3'],
                                           ['dpi_output_format', '6'],
                                           ['dtoverlay', 'pwm-2chan,pin=18,func=2,pin2=19,func2=2']]}
        p_lCfg02   = {'CRT-CABLE'       : [['crt_cable_type', '1']]}
        p_lCfg03   = {'CRT-I2C0'        : [['dtparam', 'i2c_vc=on'],
                                           ['dtoverlay', 'i2c-gpio,i2c_gpio_sda=10,i2c_gpio_scl=11']]}
        p_lCfg04   = {'CRT-VGA666-MODE' : [['dtoverlay', 'rgb-pi']]}

        p_lProfile['config'].update(self.m_lBaseCfg)
        p_lProfile['config'].update(p_lCfg01)
        p_lProfile['config'].update(p_lCfg02)
        p_lProfile['config'].update(p_lCfg03)
        p_lProfile['config'].update(p_lCfg04)
        return p_lProfile

    def load_profile_2(self):
        """ Create profile for PI2JAMMA """
        p_lProfile = {'id'   : 2,
                      'label': 'Type 2',
                      'desc' : 'PI2JAMMA',
                      'kbd'   : True,
                      'config': {}}
        p_lCfg01   = {'CRT-SOUND'       : [['dtparam', 'audio=on'],
                                           ['audio_pwm_mode', '3'],
                                           ['disable_audio_dither', '1']]}
        p_lCfg02   = {'CRT-CABLE'       : [['crt_cable_type', '2']]}
        p_lCfg03   = {'CRT-I2C0'        : []}
        p_lCfg04   = {'CRT-VGA666-MODE' : [['dtoverlay', 'vga666']]}

        p_lProfile['config'].update(self.m_lBaseCfg)
        p_lProfile['config'].update(p_lCfg01)
        p_lProfile['config'].update(p_lCfg02)
        p_lProfile['config'].update(p_lCfg03)
        p_lProfile['config'].update(p_lCfg04)
        return p_lProfile
        
    def check_current_cableID(self):
        """ get current cable configured on the system (config.txt) """
        try:
            id = int(ini_sect_get_key(RASP_BOOTCFG_FILE, 'CRT-CABLE', 'crt_cable_type'))
            self.m_iCableID = id
            return self.m_iCableID
        except: self.m_iCableID = None
        logging.info("WARNING: crt_cable_type not found in boot.txt")
        return False

    def get_cable_list_ids(self):
        """ get list of IDs from short cable list """
        p_lList = []
        for item in self.m_lCableLab:
            p_lList.append(item[0])
        return p_lList        

    def get_cable_list_labels(self):
        """ get list of labels from short cable list """
        p_lList = []
        for item in self.m_lCableLab:
            p_lList.append(item[1])
        return p_lList 

    def get_cable_list_desc(self):
        """ get list of labels from short cable list """
        p_lList = []
        for item in self.m_lCableLab:
            p_lList.append(item[2])
        return p_lList 

    def get_cable_label(self, p_sKey):
        """ get description cable from label ir ID """
        for item in self.m_lCableLab:
            if p_sKey in item: return item[1]
        return None

    def get_cable_desc(self, p_sKey):
        """ get description cable from label ir ID """
        for item in self.m_lCableLab:
            if p_sKey in item: return item[2]
        return None

    def get_cable_id(self, p_sKey):
        """ get id cable from label or description """
        for item in self.m_lCableLab:
            if p_sKey in item: return item[0]
        return None    

    def get_current_cable_id(self):
        return self.m_iCableID
        
    def fix(self):
        return self.m_bNeedFix

    def check_cable(self):
        p_bCheck = False # false if config is wrong
        p_iCableID = self.check_current_cableID()
        if p_iCableID == None or (not p_iCableID and type(p_iCableID) == type(False)):
            logging.info("WARNING: was not possible to check")
            return False
        if not os.path.exists(RASP_BOOTCFG_FILE): return False
        for id in self.m_lCableList:
            if id == p_iCableID:
                desc = self.m_lCableList[id]['desc']
                logging.info("INFO: Comparing configs on boot.txt for %s" % desc)
                for section in self.m_lCableList[id]['config']:
                    list = self.m_lCableList[id]['config'][section]
                    comp = compare_section(RASP_BOOTCFG_FILE, section, list)
                    if not comp:
                        p_bCheck = True
                        break
        self.m_bNeedFix = p_bCheck
        return self.m_bNeedFix

    def change_cable(self, p_iCableID):
        """ change cable config on system: config.txt """
        p_bCheck = False
        p_iCableID = self.get_cable_id(p_iCableID)
        self.m_sTemp = generate_random_temp_filename(RASP_BOOTCFG_FILE)
        os.system('cp %s %s' % (RASP_BOOTCFG_FILE, self.m_sTemp))
        self.set_cable(self.m_sTemp, p_iCableID)
        os.system('sudo cp %s %s' % (self.m_sTemp, RASP_BOOTCFG_FILE))
        if md5_file(self.m_sTemp) == md5_file(RASP_BOOTCFG_FILE):
            p_bCheck = True
        self.__clean()
        value = self.m_oKeyboardMNGR.check_keyboard_enabled()
        if self.m_lCableList[p_iCableID]['kbd']:
            if not value: self.m_oKeyboardMNGR.pi2jamma_enable_controls()
        else:
            if ini_get(CRT_UTILITY_FILE, 'keyb_ipac') == 'true': ipac = True
            else: ipac = False
            if value and not ipac:
                self.m_oKeyboardMNGR.pi2jamma_disable_controls()
            if not value and ipac:
                self.m_oKeyboardMNGR.pi2jamma_enable_controls()
        self.check_cable()
        return p_bCheck

    def set_cable(self, p_sFile, p_iCableID):
        """ clean and add cable configuration to a file with cable ID """
        if p_iCableID not in self.m_lCableList:
            logging.info("WARNING: id %s is not a valid cable" % p_iCableID)
            return False
        if not os.path.exists(p_sFile): return False
        logging.info("INFO: changing to cable type %s: %s" % \
                    (p_iCableID, self.m_lCableList[p_iCableID]['desc']))
        for id in self.m_lCableList:
            if id == p_iCableID:
                for section in self.m_lCableList[id]['config']:
                    ini_sect_empty_section(p_sFile, section)
                    list = self.m_lCableList[id]['config'][section]
                    if not list:
                        ini_sect_create_section(p_sFile, section)
                    for key, value in list:
                        ini_sect_add_key(p_sFile, section, key, value)
        return True

    def reset_config(self):
        p_bCheck = False
        self.m_sTemp = generate_random_temp_filename(RASP_BOOTCFG_FILE)
        touch_file(self.m_sTemp)
        p_lBaseCfg = {'pi4': [['dtoverlay', 'vc4-fkms-v3d'],
                              ['max_framebuffers' , '2']],
                      'all': [['gpu_mem_256', '128'],
                              ['gpu_mem_512', '256'],
                              ['gpu_mem_1024', '256']]}

        timings = " ".join(ini_getlist(RASP_BOOTCFG_FILE, 'hdmi_timings'))
        if not timings:
            res = ini_get(CRT_UTILITY_FILE, 'default') + '_timings'
            timings = " ".join(ini_getlist(CRT_UTILITY_FILE, res))
        line = 'hdmi_timings=' + timings
        add_line(self.m_sTemp, line)

        section_order = ['pi4', 'all'] # pi4 section must be before of all
        for section in section_order:
            list = p_lBaseCfg[section]
            for key, value in list:
                ini_sect_add_key(self.m_sTemp, section, key, value)
        
        self.set_cable(self.m_sTemp, 0) # create cable config ID0 (default)
        ini_sect_create_section(self.m_sTemp, "CUSTOM-USER")
        
        os.system('sudo cp %s %s' % (self.m_sTemp, RASP_BOOTCFG_FILE))
        if md5_file(self.m_sTemp) == md5_file(RASP_BOOTCFG_FILE):
            p_bCheck = True
        self.__clean()
        return p_bCheck

    def __clean(self):
        if os.path.exists(self.m_sTemp):
            remove_file(self.m_sTemp)
        self.m_sTemp = ""
        
    def __temp(self):
        if CLEAN_LOG_ONSTART:
            remove_file(LOG_PATH)
        logging.basicConfig(filename=LOG_PATH, level=__DEBUG__,
        format='[%(asctime)s] %(levelname)s - %(filename)s:%(funcName)s - %(message)s')

class UI(object):
    m_lCableList = []
    m_iCableID = None
    m_bFix = False

    def __init__(self):
        self.m_oCableMNGR = CableMNGR()
        self.run()
    
    def run(self):
        self._check_if_first_boot()
        self.m_lCableList = self.m_oCableMNGR.get_cable_list_ids()
        self.m_iCableID = self.m_oCableMNGR.get_current_cable_id()
        self.m_bFix = self.m_oCableMNGR.fix()
        self._main()

    def _main(self):
        p_sOption = ""
        self._generate_cable_list()
        p_sOption = menu_options(self.m_lChoices, self.m_sTitle)
        if p_sOption != 'EXIT':
            self.m_oCableMNGR.change_cable(int(p_sOption))
            self._restart()
        sys.exit(0)
        
    def _generate_cable_list(self):
        self.m_sTitle = ""
        self.m_lChoices = []
        self.m_sTitle = "SELECT RGB CABLE"
        for cable in self.m_lCableList:
            desc = self.m_oCableMNGR.get_cable_desc(cable)
            if cable == self.m_iCableID and self.m_bFix:
                self.m_lChoices.append(('[*] ' + desc.upper() + \
                                        ' (Current, need FIX)', cable))
            elif cable == self.m_iCableID:
                self.m_lChoices.append(('[*] ' + desc.upper() + \
                                        " (Don't Change)", 'EXIT'))
            else:
                self.m_lChoices.append(('[ ] ' + desc.upper(), cable))

    def _restart(self):
        """ Restart system """
        show_info('SYSTEM WILL REBOOT NOW')
        os.system('sudo reboot now')

    def _check_if_first_boot(self):
        """ Check if resize2fs is working on expanding SD partition """
        if check_process('resize2fs'):
            logging.info("WARNING: Wait until resize2fs finish")
            wait_process('resize2fs', 'stop', 1, 5)

if __name__ == '__main__':
    try:
        oLaunch = UI()
    except Exception as e:
        with open(EXCEPTION_LOG, 'a') as f:
            f.write(str(e))
            f.write(traceback.format_exc())