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

import sys, os
import logging

sys.dont_write_bytecode = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(SCRIPT_DIR + "/../"))
from main_paths import MODULES_PATH
sys.path.append(MODULES_PATH)

from main import main
from launcher_module.core_paths import *
from launcher_module.core_controls import CRT_UP, CRT_DOWN, \
                                          CRT_LEFT, CRT_RIGHT, CRT_OK, \
                                          CRT_CANCEL

LOG_PATH = os.path.join(TMP_LAUNCHER_PATH, "utility.log")
EXCEPTION_LOG = os.path.join(TMP_LAUNCHER_PATH, "backtrace.log")

class index(object):
    m_lLines = []
    m_bPause = [False]
    
    m_oCurPage = None
    m_lSubMenus = []
    m_lIcon = {}
    m_sSection = ""
    m_bNewSub = False
    
    m_lRestart = []
    m_bRestart = False

    m_lReboot = []
    m_bReboot = False

    m_lLayer40 = [None, None] # text & icon label

    def __init__(self):
        self._load_sub_menus(main())
    
    def _load_sub_menus(self, p_oSub = None):
        if p_oSub == CRT_CANCEL:
            if len(self.m_lSubMenus) == 1:
                return CRT_CANCEL # exit configuration utility
            del self.m_lSubMenus[-1]
            self._load_datas()
        elif p_oSub != None:
            try:
                if self.m_lSubMenus[-1] != p_oSub:
                    self.m_lSubMenus.append(p_oSub)
                    self._load_datas()
            except:
                self.m_lSubMenus.append(p_oSub)
                self._load_datas()

    def _load_datas(self):
        self.m_bNewSub = True
        self.m_lSubMenus[-1].load()
        self.m_bPause = self.m_lSubMenus[-1].m_bPause
        self.m_lLines = self.m_lSubMenus[-1].m_lLines
        self.m_lIcon = self.m_lSubMenus[-1].m_lIcon
        self.m_sSection = self.m_lSubMenus[-1].m_sSection
        self.m_lLayer40 = self.m_lSubMenus[-1].m_lLayer40
        self._restart_control()
        self._reboot_control()

    def check_new_sub(self):
        if self.m_bNewSub:
            self.m_bNewSub = False
            return not self.m_bNewSub
        return False

    def input(self, p_iLine, p_iJoy):
        page = self.m_lSubMenus[-1].input(p_iLine, p_iJoy)
        self._restart_control()
        self._reboot_control()
        return self._load_sub_menus(page)
        
    def _restart_control(self):
        p_bPartial = True
        if len(self.m_lSubMenus) == 1: p_bPartial = False
        # add submenu restart control to the list
        try:
            p_bCheck = False
            p_lCtrl = self.m_lSubMenus[-1].m_lRestart
            for item in self.m_lRestart:
                if p_lCtrl[0] == item[0]:
                    item[1] = p_lCtrl[1]
                    p_bCheck = True
            # add to the list if not exist
            if not p_bCheck: 
                self.m_lRestart.append(self.m_lSubMenus[-1].m_lRestart)
        except:
            pass

        # show es restart icon if needed in current submenu
        # if any submenu requires es restart, icon will appear on main page
        p_bCheck = False
        if p_bPartial:
            try:
                name = self.m_lSubMenus[-1].m_lRestart[0]
                for item in self.m_lRestart:
                    if item[0] == name:
                        if item[1] == True: p_bCheck = True
            except:
                p_bCheck = False
        else:
            for item in self.m_lRestart:
                if item[1] == True: p_bCheck = True
        self.m_bRestart = p_bCheck

    def _reboot_control(self):
        p_bPartial = True
        if len(self.m_lSubMenus) == 1: p_bPartial = False
        # add submenu reboot control to the list
        try:
            p_bCheck = False
            p_lCtrl = self.m_lSubMenus[-1].m_lReboot
            for item in self.m_lReboot:
                if p_lCtrl[0] == item[0]:
                    item[1] = p_lCtrl[1]
                    p_bCheck = True
            # add to the list if not exist
            if not p_bCheck: 
                self.m_lReboot.append(self.m_lSubMenus[-1].m_lReboot)
        except:
            pass

        # show sys reboot icon if needed in current submenu
        # if any submenu requires sys reboot, icon will appear on main page
        p_bCheck = False
        if p_bPartial:
            try:
                name = self.m_lSubMenus[-1].m_lReboot[0]
                for item in self.m_lReboot:
                    if item[0] == name:
                        if item[1] == True: p_bCheck = True
            except:
                p_bCheck = False
        else:
            for item in self.m_lReboot:
                if item[1] == True: p_bCheck = True
        self.m_bReboot = p_bCheck        