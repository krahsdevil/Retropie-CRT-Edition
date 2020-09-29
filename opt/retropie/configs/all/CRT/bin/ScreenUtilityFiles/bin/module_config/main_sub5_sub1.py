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

import sys, os, threading, time
import logging, pygame

sys.dont_write_bytecode = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(SCRIPT_DIR + "/../"))
from main_paths import MODULES_PATH
sys.path.append(MODULES_PATH)

from config_utils import find_submenus, load_submenu, explore_list, run, \
                         check_es_restart, check_sys_reboot, render_image, \
                         press_back, get_themes, check_retropie_menu, \
                         hide_retropie_menu, launching_images
from keyb.keyboard import keyboard
from es_rotation import frontend_rotation
from launcher_module.file_helpers import get_xml_value_esconfig, \
                                         set_xml_value_esconfig, \
                                         ini_get, ini_set
from launcher_module.core_paths import TMP_LAUNCHER_PATH, RETROPIE_RUNCOMMAND_CFG_FILE, \
                                       RA_CFG_FILE, CRT_UTILITY_FILE
from launcher_module.utils import get_side
from launcher_module.core_controls import CRT_UP, CRT_DOWN, \
                                          CRT_LEFT, CRT_RIGHT, CRT_OK, \
                                          CRT_CANCEL

LOG_PATH = os.path.join(TMP_LAUNCHER_PATH, "CRT_Configuration_Utility.log")
EXCEPTION_LOG = os.path.join(TMP_LAUNCHER_PATH, "backtrace.log")

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
OPT_MASK = FILE_NAME + "_sub"

class main_sub5_sub1(object):
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
    m_sSection = "User Interface"

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

    def _auto_load_datas(self):
        p_lAutoL = [self.opt4, self.opt7, self.opt9,
                    self.opt10]
        timer = 0.5 # look for datas timer
        if p_lAutoL:
            while not self.m_bThreadsStop:
                for opt in p_lAutoL:
                    self._reload_opt_datas(opt)
                time.sleep(timer)

    def _load_options(self):
        p_lOptFn = [self.opt3, self.opt4, self.opt5,
                    self.opt6, self.opt7, self.opt8,
                    self.opt9, self.opt10, self.opt11]
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

    def opt3(self, p_iJoy = None, p_iLine = None):
        p_lLines = {}
        if p_iJoy == None:
            return self.opt3_datas()
        if p_iJoy & CRT_LEFT or p_iJoy & CRT_RIGHT:
            list = self.m_lLines[p_iLine]['options']
            value = self.m_lLines[p_iLine]['value']
            new = explore_list(p_iJoy, value, list)
            if new:
                value = new.lower()
                set_xml_value_esconfig("ScreenSaverBehavior", value)
                self.m_lLines[p_iLine].update({'value': new})

    def opt3_datas(self):
        p_lLines = {'text': "ES ScreenSaver",
                    'options': ["Black", "Dim", "Random Video", "Slideshow"],
                    'color_val': "type_color_1",
                    'es_restart': True}
        value = get_xml_value_esconfig("ScreenSaverBehavior").title()
        p_lLines.update({'value': value})
        return p_lLines

    def opt4(self, p_iJoy = None, p_iLine = None):
        p_lLines = {}
        if p_iJoy == None:
            return self.opt4_datas()
        if p_iJoy & CRT_LEFT or p_iJoy & CRT_RIGHT:
            try: self.m_oROTClass
            except: self.m_oROTClass = frontend_rotation()
            list = self.m_lLines[p_iLine]['options']
            value = self.m_lLines[p_iLine]['value']
            new = explore_list(p_iJoy, value, list)
            if new:
                if new == "Horizontal":
                    value = 0
                elif new == "90 Degrees":
                    value = 90
                elif new == "-90 Degrees":
                    value = -90
                if self.m_oROTClass.rotate(value):
                    self.m_lLines[p_iLine].update({'value': new})

    def opt4_datas(self):
        p_lLines = {'text': "ES Rotation",
                    'options': ["-90 Degrees", "Horizontal", "90 Degrees"],
                    'color_val': "type_color_1",
                    'es_restart': True}
        value = get_side()

        if value == 1:
            p_lLines.update({'value': "90 Degrees"})
        elif value == 3:
            p_lLines.update({'value': "-90 Degrees"})
        else:
            p_lLines.update({'value': "Horizontal"})
        return p_lLines

    def opt5(self, p_iJoy = None, p_iLine = None):
        p_lLines = {}
        if p_iJoy == None:
            return self.opt5_datas()
        if p_iJoy & CRT_LEFT or p_iJoy & CRT_RIGHT:
            list = self.m_lLines[p_iLine]['options']
            value = self.m_lLines[p_iLine]['value']
            new = explore_list(p_iJoy, value, list)
            if new:
                value = new.replace('m', '')
                value = str(int(value) * 60000)
                set_xml_value_esconfig("ScreenSaverTime", value)
                self.m_lLines[p_iLine].update({'value': new})
                if int(value) == 0:
                    self.info(["Long exposure to a",
                               "static image could",
                               "damage your CRT"],
                               "icon_info")
                    time.sleep(2)
                    self.info()

    def opt5_datas(self):
        p_lLines = {'text': "ES ScreenSaver After",
                    'es_restart': True,
                    'color_val': "type_color_1"}
        options = []
        for i in range (0, 31):
            options.append(str(i) + "m")
        p_lLines.update({'options': options})
        value = get_xml_value_esconfig("ScreenSaverTime")
        p_lLines.update({'value': str(int(int(value) / 60000)) + "m"})
        return p_lLines

    def opt6(self, p_iJoy = None, p_iLine = None):
        p_lLines = {}
        if p_iJoy == None:
            return self.opt6_datas()
        if p_iJoy & CRT_OK:
            list = self.m_lLines[p_iLine]['options']
            value = self.m_lLines[p_iLine]['value']
            new = explore_list(p_iJoy, value, list)
            if new == False: set_xml_value_esconfig("VideoOmxPlayer", "false")
            elif new == True: set_xml_value_esconfig("VideoOmxPlayer", "true")
            self.m_lLines[p_iLine].update({'value': new})

    def opt6_datas(self):
        p_lLines = {'text': "ES Use OMX Player",
                    'color_val': "type_color_1",
                    'es_restart': True}
        value = get_xml_value_esconfig("VideoOmxPlayer")
        if value.lower() == "true": value = True
        else: value = False
        p_lLines.update({'value': value})
        return p_lLines

    def opt7(self, p_iJoy = None, p_iLine = None):
        p_lLines = {}
        if p_iJoy == None:
            return self.opt7_datas()
        if p_iJoy & CRT_LEFT or p_iJoy & CRT_RIGHT:
            list = self.m_lLines[p_iLine]['options']
            value = self.m_lLines[p_iLine]['value']
            new = explore_list(p_iJoy, value, list)
            if new: 
                self.info("Please Wait," "icon_clock")
                set_xml_value_esconfig("ThemeSet", new)
                value = get_xml_value_esconfig("ThemeSet")
                self.m_lLines[p_iLine].update({'value': value})
                self.info()

    def opt7_datas(self):
        p_lLines = {'text': "ES Theme",
                    'color_val': "type_color_1",
                    'es_restart': True}
        list = get_themes()
        if not list: 
            p_lLines.update({'options': None})
            p_lLines.update({'value': "Updating..."})
        else: 
            value = get_xml_value_esconfig("ThemeSet")
            if not value in list: list.append(value)
            set_xml_value_esconfig("ThemeSet", value)
            p_lLines.update({'options': list})
            p_lLines.update({'value': value})
        return p_lLines

    def opt8(self, p_iJoy = None, p_iLine = None):
        p_lLines = {}
        if p_iJoy == None:
            return self.opt8_datas()
        if p_iJoy & CRT_OK:
            list = self.m_lLines[p_iLine]['options']
            value = self.m_lLines[p_iLine]['value']
            new = explore_list(p_iJoy, value, list)
            if new: hide_retropie_menu(False)
            elif not new: hide_retropie_menu(True)
            value = check_retropie_menu()
            self.m_lLines[p_iLine].update({'value': new})

    def opt8_datas(self):
        p_lLines = {'text': "ES Show Retropie Menu",
                    'color_val': "type_color_1",
                    'es_restart': True}
        if check_retropie_menu(): value = True
        else: value = False
        p_lLines.update({'value': value})
        return p_lLines

    def opt9(self, p_iJoy = None, p_iLine = None):
        p_lLines = {}
        if p_iJoy == None:
            return self.opt9_datas()
        if p_iJoy & CRT_OK:
            if self.m_lLines[p_iLine]['value'] == "N/A":
                self.info("FastBoot is enabled", "icon_info")
                time.sleep(2)
                self.info()
                return
        elif p_iJoy & CRT_LEFT or p_iJoy & CRT_RIGHT:
            list = self.m_lLines[p_iLine]['options']
            value = self.m_lLines[p_iLine]['value']
            if value == "N/A": return
            new = explore_list(p_iJoy, value, list)
            if new:
                if new == "Disabled":
                    ini_set(RETROPIE_RUNCOMMAND_CFG_FILE, "image_delay", "0")
                    self.info("Please Wait", "icon_clock")
                    launching_images(False)
                    self.info()
                else:
                    ini_set(RETROPIE_RUNCOMMAND_CFG_FILE, "image_delay", new.replace('s',''))
                    if new == "1s" and value == "Disabled":
                        self.info("Please Wait", "icon_clock")
                        launching_images(True)
                        self.info()
                self.m_lLines[p_iLine].update({'value': new})

    def opt9_datas(self):
        p_lLines = {'text': "Runcommand Splash Images",
                    'color_val': "type_color_1"}
        p_lLines.update({'options': []})
        if ini_get(CRT_UTILITY_FILE, "fast_boot").lower() == "true":
            value = "N/A"
            p_lLines.update({'color_val': "type_color_7"})
        else:
            options = []
            value = ini_get(RETROPIE_RUNCOMMAND_CFG_FILE, "image_delay")
            if value == "0":
                value = "Disabled"
            else:
                value = value + "s"
            #p_lLines.update({'value': value})
            options.append("Disabled")
            for i in range (1, 11):
                options.append(str(i) + "s")
            p_lLines.update({'options': options})
        p_lLines.update({'value': value})
        return p_lLines

    def opt10(self, p_iJoy = None, p_iLine = None):
        p_lLines = {}
        if p_iJoy == None:
            return self.opt10_datas()
        if p_iJoy & CRT_OK:
            list = self.m_lLines[p_iLine]['options']
            value = self.m_lLines[p_iLine]['value']
            if value == "N/A":
                self.info("FastBoot is enabled", "icon_info")
                time.sleep(2)
                self.info()
                return
            new = explore_list(p_iJoy, value, list)
            if new == False: ini_set(RETROPIE_RUNCOMMAND_CFG_FILE, "disable_menu", "1")
            elif new == True: ini_set(RETROPIE_RUNCOMMAND_CFG_FILE, "disable_menu", "0")
            self.m_lLines[p_iLine].update({'value': new})

    def opt10_datas(self):
        p_lLines = {'text': "Runcommand Allow Config",
                    'color_val': "type_color_1"}
        if ini_get(CRT_UTILITY_FILE, "fast_boot").lower() == "true":
            value = "N/A"
            p_lLines.update({'color_val': "type_color_7"})
        else:
            value = ini_get(RETROPIE_RUNCOMMAND_CFG_FILE, "disable_menu")
            if value == "0": value = True
            else: value = False
        p_lLines.update({'value': value})
        return p_lLines

    def opt11(self, p_iJoy = None, p_iLine = None):
        p_lLines = {}
        if p_iJoy == None:
            return self.opt11_datas()
        if p_iJoy & CRT_OK:
            list = self.m_lLines[p_iLine]['options']
            value = self.m_lLines[p_iLine]['value']
            new = explore_list(p_iJoy, value, list)
            if new: ini_set(RA_CFG_FILE, "menu_driver", "rgui")
            elif not new: ini_set(RA_CFG_FILE, "menu_driver", 'Null')
            self.m_lLines[p_iLine].update({'value': new})

    def opt11_datas(self):
        p_lLines = {'text': "Retroarch Allow Config",
                    'color_val': "type_color_1"}
        value = ini_get(RA_CFG_FILE, "menu_driver")
        if value == "Null": value = False
        else: value = True
        p_lLines.update({'value': value})
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