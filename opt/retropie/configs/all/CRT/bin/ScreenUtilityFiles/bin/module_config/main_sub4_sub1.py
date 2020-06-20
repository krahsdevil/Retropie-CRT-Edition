#!/usr/bin/python
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

import sys, os, threading, time, commands
import logging, pygame

sys.dont_write_bytecode = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(SCRIPT_DIR + "/../"))
from main_paths import MODULES_PATH
sys.path.append(MODULES_PATH)

from config_utils import explore_list, find_submenus, load_submenu, \
                         check_es_restart, check_sys_reboot, wifi
from keyb.keyboard import keyboard
from launcher_module.core_paths import *
from launcher_module.core_controls import CRT_UP, CRT_DOWN, \
                                          CRT_LEFT, CRT_RIGHT, CRT_OK, \
                                          CRT_CANCEL

LOG_PATH = os.path.join(TMP_LAUNCHER_PATH, "utility.log")
EXCEPTION_LOG = os.path.join(TMP_LAUNCHER_PATH, "backtrace.log")

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
OPT_MASK = FILE_NAME + "_sub"

class main_sub4_sub1(object):
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
    m_sSection = "WIFI Configuration"

    m_lLayer40 = [None, None] # text & icon label

    def __init__(self):
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

    def _launch_kbd(self, p_sString = ""):
        try: self.m_oKBDClass
        except: self.m_oKBDClass = keyboard()
        while True:
            value = self.m_oKBDClass.write(p_sString)
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
        p_lAutoL = [self.opt1, self.opt2, self.opt3,
                    self.opt6]
        timer = 0.5 # look for datas timer
        if p_lAutoL:
            while not self.m_bThreadsStop:
                for opt in p_lAutoL:
                    self._reload_opt_datas(opt)
                time.sleep(timer)

    def _load_options(self):
        p_lOptFn = [self.opt1, self.opt2, self.opt3,
                    self.opt4, self.opt5, self.opt6]
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
        try: self.m_oWIFIClass
        except: self.m_oWIFIClass = wifi()
        if p_iJoy == None:
            return self.opt1_datas()

    def opt1_datas(self):
        try: self.m_oWIFIClass
        except: self.m_oWIFIClass = wifi()
        p_lLines = {'color_val': "type_color_1",
                    'icon': None}
        value = self.m_oWIFIClass.status()
        if value:
            text = "Connected"
            value = "SSID:" + value
        else:
            text = "Disconnected"
            value = "SSID:N/A"
        p_lLines.update({'text': text})
        p_lLines.update({'value': value})
        return p_lLines

    def opt2(self, p_iJoy = None, p_iLine = None):
        try: self.m_oWIFIClass
        except: self.m_oWIFIClass = wifi()
        if p_iJoy == None:
            return self.opt2_datas()
        if p_iJoy & CRT_LEFT or p_iJoy & CRT_RIGHT:
            list = self.m_lLines[p_iLine]['options']
            value = self.m_lLines[p_iLine]['value']
            new = explore_list(p_iJoy, value, list)
            self.m_oWIFIClass.mode(new)
            self.m_lLines[p_iLine]['value'] = new

    def opt2_datas(self):
        try: self.m_oWIFIClass
        except: self.m_oWIFIClass = wifi()
        p_lLines = {'text': "SSID Input Mode",
                    'color_val': "type_color_1",
                    'icon': None}
        value = self.m_oWIFIClass.get_mode()
        list = self.m_oWIFIClass.get_mode_list()
        p_lLines.update({'value': value})
        p_lLines.update({'options': list})
        return p_lLines

    def opt3(self, p_iJoy = None, p_iLine = None):
        try: self.m_oWIFIClass
        except: self.m_oWIFIClass = wifi()
        if p_iJoy == None:
            return self.opt3_datas()
        if p_iJoy & CRT_LEFT or p_iJoy & CRT_RIGHT:
            if self.m_oWIFIClass.get_mode().lower() == "manual":
                return
            list = self.m_lLines[p_iLine]['options']
            value = self.m_lLines[p_iLine]['value']
            new = explore_list(p_iJoy, value, list)
            if new:
                self.m_oWIFIClass.ssid(new)
                self.m_lLines[p_iLine]['value'] = new
        elif p_iJoy & CRT_OK:
            if self.m_oWIFIClass.get_mode().lower() == "manual":
                value = self.m_lLines[p_iLine]['value']
                new = self._launch_kbd().strip()
                if new:
                    self.m_oWIFIClass.ssid(new)
                    self.m_lLines[p_iLine]['value'] = new
            elif self.m_oWIFIClass.get_mode().lower() == "detect":
                value = self.m_lLines[p_iLine]['value']
                self.info("Scanning SSIDs", "icon_clock")
                list = self.m_oWIFIClass.detect(value)
                if list:
                    self.m_lLines[p_iLine]['options'] = list
                    self.m_lLines[p_iLine]['value'] = self.m_oWIFIClass.get_ssid()
                self.info()

    def opt3_datas(self):
        try: self.m_oWIFIClass
        except: self.m_oWIFIClass = wifi()
        p_lLines = {'text': "SSID",
                    'color_val': "type_color_1"}
        if self.m_oWIFIClass.get_mode().lower() == "manual":
            value = self.m_oWIFIClass.get_ssid()
            p_lLines.update({'icon': "icon_edit"})
            p_lLines.update({'options': None})
        if self.m_oWIFIClass.get_mode().lower() == "detect":
            list = self.m_oWIFIClass.get_ssid_list()
            value = self.m_oWIFIClass.get_ssid()
            if value == "[A:SCAN]":
                p_lLines.update({'icon': "icon_bin"})
            else: p_lLines.update({'icon': None})
            p_lLines.update({'options': list})
        p_lLines.update({'value': value})
        return p_lLines

    def opt4(self, p_iJoy = None, p_iLine = None):
        try: self.m_oWIFIClass
        except: self.m_oWIFIClass = wifi()
        if p_iJoy == None:
            return self.opt4_datas()
        if p_iJoy & CRT_OK:
            new = self._launch_kbd(self.m_oWIFIClass.get_pwd())
            if new:
                if not self.m_oWIFIClass.pwd(new):
                    self.info(["Password length",
                               "must be between",
                               "8-63 characters"],
                               "icon_info")
                    time.sleep(2)
                    self.info()

    def opt4_datas(self):
        try: self.m_oWIFIClass
        except: self.m_oWIFIClass = wifi()
        p_lLines = {'text': "Password",
                    'color_val': "type_color_1",
                    'icon': "icon_edit"}
        value = '*****'
        p_lLines.update({'value': value})
        return p_lLines

    def opt5(self, p_iJoy = None, p_iLine = None):
        try: self.m_oWIFIClass
        except: self.m_oWIFIClass = wifi()
        if p_iJoy == None:
            return self.opt5_datas()
        if p_iJoy & CRT_OK:
            value = self.m_oWIFIClass.get_ssid()
            if value == "[A:SCAN]":
                if len(self.m_oWIFIClass.get_ssid_list()) > 1:
                    self.info("Select an SSID", "icon_info")
                else:
                    self.info("Scan SSIDs", "icon_info")
            elif value == "[Your SSID]":
                self.info("Write your SSID", "icon_info")
            elif value == self.m_oWIFIClass.status():
                self.info("Already connected", "icon_info")
            elif not self.m_oWIFIClass.get_pwd():
                self.info("Write a password", "icon_info")
            else:
                self.info("Connecting", "icon_clock")
                if self.m_oWIFIClass.connect():
                    self.info("Connected", "icon_info")
                else:
                    self.info("Could not connect", "icon_info")
                    self.m_oWIFIClass.clear()
            time.sleep(2)
            self.info()

    def opt5_datas(self):
        try: self.m_oWIFIClass
        except: self.m_oWIFIClass = wifi()
        p_lLines = {'text': "Connect to WIFI",
                    'color_val': "type_color_1",
                    'icon': "icon_bin"}
        return p_lLines

    def opt6(self, p_iJoy = None, p_iLine = None):
        try: self.m_oWIFIClass
        except: self.m_oWIFIClass = wifi()
        if p_iJoy == None:
            return self.opt6_datas()
        if p_iJoy & CRT_OK:
            self.info("Please Wait", "icon_clock")
            self.m_oWIFIClass.clear()
            self.info("WIFI config cleared", "icon_info")
            time.sleep(2)
            self.info()

    def opt6_datas(self):
        try: self.m_oWIFIClass
        except: self.m_oWIFIClass = wifi()
        p_lLines = {'color_val': "type_color_1",
                    'icon': "icon_bin"}
        if self.m_oWIFIClass.status():
            p_lLines.update({'text': "Disconnect from SSID"})
        else:
            p_lLines.update({'text': "Clear config"})
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