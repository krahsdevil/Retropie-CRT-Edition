#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Rotate screen module only for TATE mode

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

import os, sys
import filecmp

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(SCRIPT_DIR + "/../"))
from main_paths import MODULES_PATH
sys.path.append(MODULES_PATH)

from launcher_module.core_paths import *
from launcher_module.utils import something_is_bad, menu_options
from module_configuration_utility.es_rotation import frontend_rotation

ES_LAUNCHER_DST_FILE = os.path.join(RETROPIE_PATH,
                       "supplementary/emulationstation/emulationstation.sh")
ES_LAUNCHER_SRC_FILE = os.path.join(CRT_ES_RES_PATH,
                       "configs/default_emulationstation.sh")
ES_LAUNCHER_BCK_FILE = os.path.join(RETROPIE_PATH,
                       "supplementary/emulationstation/backup.emulationstation.sh")

iCurSide = 0
sTitRot = "ROTATE SCREEN"
lOptRot = [("HORIZONTAL", "HORIZONTAL"),
           ("ROTATE 180", "VERTICAL"),
           ("CANCEL", "CANCEL")]

def get_config():
    global iCurSide
    if os.path.exists(ROTMODES_TATE1_FILE):
        iCurSide = 1
    elif os.path.exists(ROTMODES_TATE3_FILE):
        iCurSide = 3
    else:
        sys.exit()

def check_es_launcher():
    p_bFixed = False
    if not os.path.exists(ES_LAUNCHER_DST_FILE):
        os.system('sudo cp %s %s >> /dev/null 2>&1' % (ES_LAUNCHER_SRC_FILE, ES_LAUNCHER_DST_FILE))
        p_bFixed = True
    else:
        if not filecmp.cmp(ES_LAUNCHER_SRC_FILE, ES_LAUNCHER_DST_FILE):
            os.system('sudo cp %s %s >> /dev/null 2>&1' % (ES_LAUNCHER_DST_FILE, ES_LAUNCHER_BCK_FILE))
            os.system('sudo cp %s %s >> /dev/null 2>&1' % (ES_LAUNCHER_SRC_FILE, ES_LAUNCHER_DST_FILE))
            p_bFixed = True
    if p_bFixed:        
        os.system('sudo chmod +x %s >> /dev/null 2>&1' % ES_LAUNCHER_DST_FILE)
        infos = "System needs to reboot, please wait..."
        infos2 = ""
        something_is_bad(infos,infos2)
        os.system('sudo reboot')
        
def quit_module(p_iSide = None):
    if p_iSide != None:
        frontend_rotation(p_iSide, True)
    sys.exit(0)

def script_initialization():
    check_es_launcher()
    get_config()

def draw_menu():
    sOption = menu_options(lOptRot, sTitRot)
    if sOption == "VERTICAL":
        if iCurSide == 1:
            quit_module(-90)
        elif iCurSide == 3:
            quit_module(90)
    elif sOption == "HORIZONTAL":
        quit_module(0)
    else:
        quit_module()

script_initialization()
draw_menu()
