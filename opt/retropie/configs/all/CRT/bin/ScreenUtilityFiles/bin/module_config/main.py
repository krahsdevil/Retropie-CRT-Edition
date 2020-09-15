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

import sys, os, logging

sys.dont_write_bytecode = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(SCRIPT_DIR + "/../"))
from main_paths import MODULES_PATH
sys.path.append(MODULES_PATH)

from config_utils import find_submenus, load_submenu
from launcher_module.core_paths import TMP_LAUNCHER_PATH
from launcher_module.core_controls import CRT_UP, CRT_DOWN, \
                                          CRT_LEFT, CRT_RIGHT, CRT_OK, \
                                          CRT_CANCEL

LOG_PATH = os.path.join(TMP_LAUNCHER_PATH, "utility.log")
EXCEPTION_LOG = os.path.join(TMP_LAUNCHER_PATH, "backtrace.log")

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
OPT_MASK = FILE_NAME + "_sub"

class main(object):

    m_lLines = []
    m_lSubMenus = []
    m_lIcon = {'icon': "icon_info"}
    m_sSection = "MAIN"
    m_bPause = [False]
    m_bThreadsStop = True

    m_lLayer40 = [None, None] # text & icon label

    def __init__(self):
        self._load_sub_menus()

    def load(self):
        pass

    def input(self, p_iLine, p_iJoy):
        if p_iJoy & CRT_CANCEL:
            return CRT_CANCEL # False: back to previous menu
        elif p_iJoy & CRT_OK:
            sub = self.m_lSubMenus[p_iLine]
            return sub
                    
    def _load_sub_menus(self):
        try:
            for sbm in find_submenus(SCRIPT_DIR, OPT_MASK):
                logging.info("Loading main menu option: %s " % sbm["name"])
                sub = load_submenu(sbm)
                self.m_lSubMenus.append(sub())

            if not self.m_lSubMenus: sys.exit()

            for sbm in self.m_lSubMenus:
                temp = {}
                temp.update({'text': sbm.m_sSection})
                temp.update({'icon': sbm.m_lIcon['icon']})
                temp.update({'color_txt': "type_color_2"})
                self.m_lLines.append(temp)

        except:
            raise
           