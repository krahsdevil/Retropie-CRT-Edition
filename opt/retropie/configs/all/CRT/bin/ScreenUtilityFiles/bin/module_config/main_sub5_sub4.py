#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Configuration Utility

https://github.com/krahsdevil/crt-for-retropie/

Copyright (C)  2018/2020 -krahs- - https://github.com/krahsdevil/

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

import sys, os, threading, time, subprocess
import logging, re, pygame

sys.dont_write_bytecode = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(SCRIPT_DIR + "/../"))
from main_paths import MODULES_PATH
sys.path.append(MODULES_PATH)

from config_utils import explore_list, find_submenus, load_submenu, \
                         check_es_restart, check_sys_reboot, render_image, \
                         press_back
from keyb.keyboard import keyboard
from launcher_module.core_paths import TMP_LAUNCHER_PATH
from launcher_module.core_controls import CRT_UP, CRT_DOWN, \
                                          CRT_LEFT, CRT_RIGHT, CRT_OK, \
                                          CRT_CANCEL

from module_cable.oc_manager import OCMNGR

LOG_PATH = os.path.join(TMP_LAUNCHER_PATH, "CRT_Configuration_Utility.log")
EXCEPTION_LOG = os.path.join(TMP_LAUNCHER_PATH, "backtrace.log")

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
OPT_MASK = FILE_NAME + "_sub"

class main_sub5_sub4(object):
    m_bPause = [False]
    m_oThreads = []
    m_bThreadsStop = True

    m_lLines = []
    m_lMainOpts = []
    m_lSubMenus = []
    m_lOptFn = []

    m_lCtrl = []
    m_lRestart = [__name__, False]
    m_lReboot = [__name__, False]

    m_lIcon = {'icon': 'icon_folder'}
    m_sSection = "System Overclocking"

    m_lLayer40 = [None, None] # text & icon label

    def __init__(self):
        logging.info("INFO: Initializing %s" % __name__)
        self._load_options()
        self._load_sub_menus()

    def load(self):
        self.m_bThreadsStop = False
        self._create_threads()

    def info(self, p_sText = False, p_sIcon = False, p_bPress = False):
        self.m_lLayer40[0] = None
        self.m_lLayer40[1] = None
        if not p_sText: return
        if type(p_sText) is not list:
            if type(p_sText) == pygame.Surface:
                self.m_lLayer40[0] = p_sText
                return
            elif type(p_sText) is str:
                if os.path.exists(p_sText):
                    self.m_lLayer40[0] = render_image(p_sText)
                    if p_bPress: press_back()
                    return
        self.m_lLayer40[0] = p_sText
        self.m_lLayer40[1] = p_sIcon

    def _launch_kbd(self, p_sString = "", p_iChars = 15):
        try: self.m_oKBDClass
        except: self.m_oKBDClass = keyboard()
        while True:
            value = self.m_oKBDClass.write(p_sString, p_iChars)
            if type(value) is str:
                break
            else:
                self.info(value)
        self.info()
        return value

    def _create_threads(self):
        p_oDmns = [self._auto_load_datas]
        self.m_oThreads = []
        for dmn in p_oDmns:
            t = threading.Thread(target=dmn)
            t.start()
            self.m_oThreads.append(t)

    def _auto_load_datas(self, p_bOnce = False):
        p_lAutoL = [self.opt1, self.opt4, self.opt5,
                    self.opt6, self.opt7, self.opt8,
                    self.opt9, self.opt10, self.opt11]
        timer = 0.5 # look for datas timer
        if p_lAutoL:
            while not self.m_bThreadsStop:
                for opt in p_lAutoL:
                    self._reload_opt_datas(opt)
                if p_bOnce: break
                time.sleep(timer)

    def _load_options(self):
        p_lOptFn = [self.opt1, self.opt2, self.opt3,
                    self.opt4, self.opt5, self.opt6,
                    self.opt7, self.opt8, self.opt9,
                    self.opt10, self.opt11]
        self.m_lOptFn = p_lOptFn
        for opt in self.m_lOptFn:
            self.m_lMainOpts.append(opt)
            self.m_lLines.append(opt())
            self.m_lCtrl.append(opt())

    def _reload_opt_datas(self, opt = None):
        pos = self.m_lMainOpts.index(opt)
        if opt: self.m_lLines[pos].update(opt())

    def _launch_app(self, p_sCommand, p_sDBSys = None):
        self.m_bPause[0] = True
        self.m_bThreadsStop = True
        run(p_sCommand, p_sDBSys)
        self.m_bPause[0] = False
        self.m_bThreadsStop = False

    def _load_sub_menus(self):
        submenus = []
        try:
            for sbm in find_submenus(SCRIPT_DIR, OPT_MASK):
                logging.info("Loading main menu option: %s " % sbm["name"])
                sub = load_submenu(sbm)
                submenus.append(sub())

            if len(self.m_lLines) != 0:
                for i in range (0, len(self.m_lLines)):
                    self.m_lSubMenus.append(None)
            for sub in submenus:
                self.m_lSubMenus.append(sub)

            for sbm in self.m_lSubMenus:
                if sbm:
                    temp = {}
                    temp.update({'text': sbm.m_sSection})
                    temp.update({'icon': sbm.m_lIcon['icon']})
                    temp.update({'color_txt': "type_color_2"})
                    self.m_lLines.append(temp)
        except:
            raise

    def opt1(self, p_iJoy = None, p_iLine = None):
        try: self.m_oOCClass
        except: self.m_oOCClass = OCMNGR()
        p_lLines = {}
        if p_iJoy == None:
            return self.opt1_datas()
        if p_iJoy & CRT_OK:
            list = self.m_lLines[p_iLine]['options']
            value = self.m_lLines[p_iLine]['value']
            if not self.m_oOCClass.compatible(): return
            new = explore_list(p_iJoy, value, list)
            self.info("Please Wait", "icon_clock")
            if new == False: 
                self.m_oOCClass.disable()
                self._auto_load_datas(True)
            elif new == True: 
                self.info(["Only advanced users!",
                           " Overclock can damage",
                           "   your Raspberry Pi.",
                           "  You may experience",
                           " instability, hungs or",
                           "  system overheating."], 'icon_warn')
                time.sleep(10)
                self.info()
                self.m_oOCClass.enable()
            value = self.m_oOCClass.status()
            self.info()
            self.m_lLines[p_iLine]['value'] = value

    def opt1_datas(self):
        p_lLines = {'text': "System Overclock",
                    'sys_reboot': True,
                    'color_val': "type_color_1"}
        try: self.m_oOCClass
        except: self.m_oOCClass = OCMNGR()
        if not self.m_oOCClass.compatible():
            p_lLines.update({'color_val': "type_color_7"})
            value = "N/A"
        else:
            value = self.m_oOCClass.status()
        p_lLines.update({'value': value})
        return p_lLines

    def opt2(self, p_iJoy = None, p_iLine = None):
        try: self.m_oOCClass
        except: self.m_oOCClass = OCMNGR()
        p_lLines = {}
        if p_iJoy == None:
            return self.opt2_datas()

    def opt2_datas(self):
        p_lLines = {'text': "Raspberry Model",
                    'color_val': "type_color_7"}
        try: self.m_oOCClass
        except: self.m_oOCClass = OCMNGR()
        value = self.m_oOCClass.get_model()
        p_lLines.update({'value': value})
        return p_lLines

    def opt3(self, p_iJoy = None, p_iLine = None):
        try: self.m_oOCClass
        except: self.m_oOCClass = OCMNGR()
        p_lLines = {}
        if p_iJoy == None:
            return self.opt3_datas()

    def opt3_datas(self):
        p_lLines = {'text': "Hardware Rev.",
                    'color_val': "type_color_7"}
        try: self.m_oOCClass
        except: self.m_oOCClass = OCMNGR()
        value = self.m_oOCClass.get_model_id()
        p_lLines.update({'value': value})
        return p_lLines

    def opt4(self, p_iJoy = None, p_iLine = None):
        try: self.m_oOCClass
        except: self.m_oOCClass = OCMNGR()
        p_lLines = {}
        if p_iJoy == None:
            return self.opt4_datas()
        if p_iJoy & CRT_OK:
            if not self.m_oOCClass.status(): return
            if not self.m_oOCClass.rec_values(): 
                self.info("Only for Pi2B", "icon_info")
                time.sleep(2)
                self.info()
                return
            self.info("Please Wait", "icon_clock")
            self.m_oOCClass.apply_rec_values()
            self.info()

    def opt4_datas(self):
        p_lLines = {'text': "Apply recommended values",
                    'icon': None,
                    'value': '--',
                    'color_val': "type_color_7"}
        try: self.m_oOCClass
        except: self.m_oOCClass = OCMNGR()
        if self.m_oOCClass.status():
            if self.m_oOCClass.rec_values():
                p_lLines.update({'icon': 'icon_edit'})
                p_lLines.update({'value': None})
            else:
                p_lLines.update({'value': 'N/A'})
        return p_lLines

    def opt5(self, p_iJoy = None, p_iLine = None):
        try: self.m_oOCClass
        except: self.m_oOCClass = OCMNGR()
        p_lLines = {}
        if p_iJoy == None:
            return self.opt5_datas()
        if p_iJoy & CRT_LEFT or p_iJoy & CRT_RIGHT:
            list = self.m_lLines[p_iLine]['options']
            value = self.m_lLines[p_iLine]['value']
            if not self.m_oOCClass.status(): return
            p_sINI = 'arm_freq' # overclock value to get
            new = explore_list(p_iJoy, value, list)
            if new != None:
                self.info("Please Wait", "icon_clock")
                self.m_oOCClass.set_oc_value(p_sINI, new)
                value = self.m_oOCClass.get_ini(p_sINI)
                if self.m_oOCClass.is_base_value(p_sINI, value): 
                    p_lLines.update({'icon': None})
                    self.m_lLines[p_iLine]['color_val'] = "type_color_1"
                else:
                    p_lLines.update({'icon': "icon_warn2"})
                    self.m_lLines[p_iLine]['color_val'] = "type_color_6"
                self.m_lLines[p_iLine]['value'] = value
                self.info()

    def opt5_datas(self):
        p_sINI = 'arm_freq' # overclock value to get
        p_lLines = {'text': p_sINI.lower(),
                    'sys_reboot': True,
                    'icon': None,
                    'color_val': "type_color_1"}
        try: self.m_oOCClass
        except: self.m_oOCClass = OCMNGR()
        value = self.m_oOCClass.get_ini(p_sINI)
        if not self.m_oOCClass.status():
            p_lLines.update({'color_val': "type_color_7"})
            p_lValues = []
        else: 
            p_lValues = self.m_oOCClass.get_ini_values_list(p_sINI)
            if not self.m_oOCClass.is_base_value(p_sINI, value): 
                p_lLines.update({'icon': "icon_warn2"})
                p_lLines.update({'color_val': "type_color_6"})
        p_lLines.update({'value': value})
        p_lLines.update({'options': p_lValues})
        return p_lLines

    def opt6(self, p_iJoy = None, p_iLine = None):
        try: self.m_oOCClass
        except: self.m_oOCClass = OCMNGR()
        p_lLines = {}
        if p_iJoy == None:
            return self.opt6_datas()
        if p_iJoy & CRT_LEFT or p_iJoy & CRT_RIGHT:
            list = self.m_lLines[p_iLine]['options']
            value = self.m_lLines[p_iLine]['value']
            if not self.m_oOCClass.status(): return
            p_sINI = 'gpu_freq' # overclock value to get
            new = explore_list(p_iJoy, value, list)
            if new != None:
                self.info("Please Wait", "icon_clock")
                self.m_oOCClass.set_oc_value(p_sINI, new)
                value = self.m_oOCClass.get_ini(p_sINI)
                if self.m_oOCClass.is_base_value(p_sINI, value): 
                    p_lLines.update({'icon': None})
                    self.m_lLines[p_iLine]['color_val'] = "type_color_1"
                else:
                    p_lLines.update({'icon': "icon_warn2"})
                    self.m_lLines[p_iLine]['color_val'] = "type_color_6"
                self.m_lLines[p_iLine]['value'] = value
                self.info()

    def opt6_datas(self):
        p_sINI = 'gpu_freq' # overclock value to get
        p_lLines = {'text': p_sINI.lower(),
                    'sys_reboot': True,
                    'icon': None,
                    'color_val': "type_color_1"}
        try: self.m_oOCClass
        except: self.m_oOCClass = OCMNGR()
        value = self.m_oOCClass.get_ini(p_sINI)
        if not self.m_oOCClass.status():
            p_lLines.update({'color_val': "type_color_7"})
            p_lValues = []
        else: 
            p_lValues = self.m_oOCClass.get_ini_values_list(p_sINI)
            if not self.m_oOCClass.is_base_value(p_sINI, value): 
                p_lLines.update({'icon': "icon_warn2"})
                p_lLines.update({'color_val': "type_color_6"})
        p_lLines.update({'value': value})
        p_lLines.update({'options': p_lValues})
        return p_lLines
        
    def opt7(self, p_iJoy = None, p_iLine = None):
        try: self.m_oOCClass
        except: self.m_oOCClass = OCMNGR()
        p_lLines = {}
        if p_iJoy == None:
            return self.opt7_datas()
        if p_iJoy & CRT_LEFT or p_iJoy & CRT_RIGHT:
            list = self.m_lLines[p_iLine]['options']
            value = self.m_lLines[p_iLine]['value']
            if not self.m_oOCClass.status(): return
            p_sINI = 'core_freq' # overclock value to get
            new = explore_list(p_iJoy, value, list)
            if new != None:
                self.info("Please Wait", "icon_clock")
                self.m_oOCClass.set_oc_value(p_sINI, new)
                value = self.m_oOCClass.get_ini(p_sINI)
                if self.m_oOCClass.is_base_value(p_sINI, value): 
                    p_lLines.update({'icon': None})
                    self.m_lLines[p_iLine]['color_val'] = "type_color_1"
                else:
                    p_lLines.update({'icon': "icon_warn2"})
                    self.m_lLines[p_iLine]['color_val'] = "type_color_6"
                self.m_lLines[p_iLine]['value'] = value
                self.info()

    def opt7_datas(self):
        p_sINI = 'core_freq' # overclock value to get
        p_lLines = {'text': p_sINI.lower(),
                    'sys_reboot': True,
                    'icon': None,
                    'color_val': "type_color_1"}
        try: self.m_oOCClass
        except: self.m_oOCClass = OCMNGR()
        value = self.m_oOCClass.get_ini(p_sINI)
        if not self.m_oOCClass.status():
            p_lLines.update({'color_val': "type_color_7"})
            p_lValues = []
        else: 
            p_lValues = self.m_oOCClass.get_ini_values_list(p_sINI)
            if not self.m_oOCClass.is_base_value(p_sINI, value): 
                p_lLines.update({'icon': "icon_warn2"})
                p_lLines.update({'color_val': "type_color_6"})
        p_lLines.update({'value': value})
        p_lLines.update({'options': p_lValues})
        return p_lLines

    def opt8(self, p_iJoy = None, p_iLine = None):
        try: self.m_oOCClass
        except: self.m_oOCClass = OCMNGR()
        p_lLines = {}
        if p_iJoy == None:
            return self.opt8_datas()
        if p_iJoy & CRT_LEFT or p_iJoy & CRT_RIGHT:
            list = self.m_lLines[p_iLine]['options']
            value = self.m_lLines[p_iLine]['value']
            if not self.m_oOCClass.status(): return
            p_sINI = 'sdram_freq' # overclock value to get
            new = explore_list(p_iJoy, value, list)
            if new != None:
                self.info("Please Wait", "icon_clock")
                self.m_oOCClass.set_oc_value(p_sINI, new)
                value = self.m_oOCClass.get_ini(p_sINI)
                if self.m_oOCClass.is_base_value(p_sINI, value): 
                    p_lLines.update({'icon': None})
                    self.m_lLines[p_iLine]['color_val'] = "type_color_1"
                else:
                    p_lLines.update({'icon': "icon_warn2"})
                    self.m_lLines[p_iLine]['color_val'] = "type_color_6"
                self.m_lLines[p_iLine]['value'] = value
                self.info()

    def opt8_datas(self):
        p_sINI = 'sdram_freq' # overclock value to get
        p_lLines = {'text': p_sINI.lower(),
                    'sys_reboot': True,
                    'icon': None,
                    'color_val': "type_color_1"}
        try: self.m_oOCClass
        except: self.m_oOCClass = OCMNGR()
        value = self.m_oOCClass.get_ini(p_sINI)
        if not self.m_oOCClass.status():
            p_lLines.update({'color_val': "type_color_7"})
            p_lValues = []
        else: 
            p_lValues = self.m_oOCClass.get_ini_values_list(p_sINI)
            if not self.m_oOCClass.is_base_value(p_sINI, value): 
                p_lLines.update({'icon': "icon_warn2"})
                p_lLines.update({'color_val': "type_color_6"})
        p_lLines.update({'value': value})
        p_lLines.update({'options': p_lValues})
        return p_lLines
        
    def opt9(self, p_iJoy = None, p_iLine = None):
        try: self.m_oOCClass
        except: self.m_oOCClass = OCMNGR()
        p_lLines = {}
        if p_iJoy == None:
            return self.opt9_datas()
        if p_iJoy & CRT_LEFT or p_iJoy & CRT_RIGHT:
            list = self.m_lLines[p_iLine]['options']
            value = self.m_lLines[p_iLine]['value']
            if not self.m_oOCClass.status(): return
            p_sINI = 'sdram_schmoo' # overclock value to get
            new = explore_list(p_iJoy, value, list)
            if new != None:
                self.info("Please Wait", "icon_clock")
                self.m_oOCClass.set_oc_value(p_sINI, new)
                value = self.m_oOCClass.get_ini(p_sINI)
                if self.m_oOCClass.is_base_value(p_sINI, value): 
                    p_lLines.update({'icon': None})
                    self.m_lLines[p_iLine]['color_val'] = "type_color_1"
                else:
                    p_lLines.update({'icon': "icon_warn2"})
                    self.m_lLines[p_iLine]['color_val'] = "type_color_6"
                self.m_lLines[p_iLine]['value'] = value
                self.info()

    def opt9_datas(self):
        p_sINI = 'sdram_schmoo' # overclock value to get
        p_lLines = {'text': p_sINI.lower(),
                    'sys_reboot': True,
                    'icon': None,
                    'color_val': "type_color_1"}
        try: self.m_oOCClass
        except: self.m_oOCClass = OCMNGR()
        value = self.m_oOCClass.get_ini(p_sINI)
        if not self.m_oOCClass.status():
            p_lLines.update({'color_val': "type_color_7"})
            p_lValues = []
        else: 
            p_lValues = self.m_oOCClass.get_ini_values_list(p_sINI)
            if not self.m_oOCClass.is_base_value(p_sINI, value): 
                p_lLines.update({'icon': "icon_warn2"})
                p_lLines.update({'color_val': "type_color_6"})
        p_lLines.update({'value': value})
        p_lLines.update({'options': p_lValues})
        return p_lLines
        
    def opt10(self, p_iJoy = None, p_iLine = None):
        try: self.m_oOCClass
        except: self.m_oOCClass = OCMNGR()
        p_lLines = {}
        if p_iJoy == None:
            return self.opt10_datas()
        if p_iJoy & CRT_LEFT or p_iJoy & CRT_RIGHT:
            list = self.m_lLines[p_iLine]['options']
            value = self.m_lLines[p_iLine]['value']
            if not self.m_oOCClass.status(): return
            p_sINI = 'over_voltage' # overclock value to get
            new = explore_list(p_iJoy, value, list)
            if new != None:
                self.info("Please Wait", "icon_clock")
                self.m_oOCClass.set_oc_value(p_sINI, new)
                value = self.m_oOCClass.get_ini(p_sINI)
                if self.m_oOCClass.is_base_value(p_sINI, value): 
                    p_lLines.update({'icon': None})
                    self.m_lLines[p_iLine]['color_val'] = "type_color_1"
                else:
                    p_lLines.update({'icon': "icon_warn2"})
                    self.m_lLines[p_iLine]['color_val'] = "type_color_6"
                self.m_lLines[p_iLine]['value'] = value
                self.info()

    def opt10_datas(self):
        p_sINI = 'over_voltage' # overclock value to get
        p_lLines = {'text': p_sINI.lower(),
                    'sys_reboot': True,
                    'icon': None,
                    'color_val': "type_color_1"}
        try: self.m_oOCClass
        except: self.m_oOCClass = OCMNGR()
        value = self.m_oOCClass.get_ini(p_sINI)
        if not self.m_oOCClass.status():
            p_lLines.update({'color_val': "type_color_7"})
            p_lValues = []
        else: 
            p_lValues = self.m_oOCClass.get_ini_values_list(p_sINI)
            if not self.m_oOCClass.is_base_value(p_sINI, value): 
                p_lLines.update({'icon': "icon_warn2"})
                p_lLines.update({'color_val': "type_color_6"})
        p_lLines.update({'value': value})
        p_lLines.update({'options': p_lValues})
        return p_lLines
        
    def opt11(self, p_iJoy = None, p_iLine = None):
        try: self.m_oOCClass
        except: self.m_oOCClass = OCMNGR()
        p_lLines = {}
        if p_iJoy == None:
            return self.opt11_datas()
        if p_iJoy & CRT_LEFT or p_iJoy & CRT_RIGHT:
            list = self.m_lLines[p_iLine]['options']
            value = self.m_lLines[p_iLine]['value']
            if not self.m_oOCClass.status(): return
            p_sINI = 'over_voltage_sdram' # overclock value to get
            new = explore_list(p_iJoy, value, list)
            if new != None:
                self.info("Please Wait", "icon_clock")
                self.m_oOCClass.set_oc_value(p_sINI, new)
                value = self.m_oOCClass.get_ini(p_sINI)
                if self.m_oOCClass.is_base_value(p_sINI, value): 
                    p_lLines.update({'icon': None})
                    self.m_lLines[p_iLine]['color_val'] = "type_color_1"
                else:
                    p_lLines.update({'icon': "icon_warn2"})
                    self.m_lLines[p_iLine]['color_val'] = "type_color_6"
                self.m_lLines[p_iLine]['value'] = value
                self.info()

    def opt11_datas(self):
        p_sINI = 'over_voltage_sdram' # overclock value to get
        p_lLines = {'text': p_sINI.lower(),
                    'sys_reboot': True,
                    'icon': None,
                    'color_val': "type_color_1"}
        try: self.m_oOCClass
        except: self.m_oOCClass = OCMNGR()
        value = self.m_oOCClass.get_ini(p_sINI)
        if not self.m_oOCClass.status():
            p_lLines.update({'color_val': "type_color_7"})
            p_lValues = []
        else: 
            p_lValues = self.m_oOCClass.get_ini_values_list(p_sINI)
            if not self.m_oOCClass.is_base_value(p_sINI, value): 
                p_lLines.update({'icon': "icon_warn2"})
                p_lLines.update({'color_val': "type_color_6"})
        p_lLines.update({'value': value})
        p_lLines.update({'options': p_lValues})
        return p_lLines

    def input(self, p_iLine, p_iJoy):
        if p_iJoy & CRT_CANCEL:
            self.quit()
            return CRT_CANCEL # False: back to previous menu
        else:
            if p_iLine > (len(self.m_lOptFn) - 1):
                if p_iJoy & CRT_OK: return self.m_lSubMenus[p_iLine]
            else:
                self.m_lMainOpts[p_iLine](p_iJoy, p_iLine)
                self.m_lRestart[1] = check_es_restart(self.m_lLines, self.m_lCtrl)
                self.m_lReboot[1] = check_sys_reboot(self.m_lLines, self.m_lCtrl)

    def quit(self):
        self.m_bThreadsStop = True
        self.info()