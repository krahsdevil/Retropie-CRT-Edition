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

import pygame, os, sys, logging, traceback, time
import filecmp

sys.dont_write_bytecode = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(SCRIPT_DIR + "/../"))
from main_paths import MODULES_PATH
sys.path.append(MODULES_PATH)

from launcher_module.core_paths import *
from launcher_module.file_helpers import modify_line, ini_get, remove_file
from config_render import render

LOG_PATH = os.path.join(TMP_LAUNCHER_PATH, "CRT_Configuration_Utility.log")
EXCEPTION_LOG = os.path.join(TMP_LAUNCHER_PATH, "backtrace.log")

__VERSION__ = '0.1'
__DEBUG__ = logging.INFO # logging.ERROR
CLEAN_LOG_ONSTART = True

os.system("clear")

ES_LAUNCHER_DST_FILE = os.path.join(RETROPIE_PATH,
                       "supplementary/emulationstation/emulationstation.sh")
ES_LAUNCHER_SRC_FILE = os.path.join(CRT_ES_RES_PATH,
                       "configs/default_emulationstation.sh")
ES_LAUNCHER_BCK_FILE = os.path.join(RETROPIE_PATH,
                       "supplementary/emulationstation/backup.emulationstation.sh")

class config(render):

    def __init__(self):
        self.__temp()
        self.__clean()
        super(render, self).__init__()

    def check_es_launcher(self):
        p_bFixed = False
        if not os.path.exists(ES_LAUNCHER_DST_FILE):
            os.system('sudo cp %s %s >> /dev/null 2>&1' % \
                     (ES_LAUNCHER_SRC_FILE, ES_LAUNCHER_DST_FILE))
            p_bFixed = True
        else:
            if not filecmp.cmp(ES_LAUNCHER_SRC_FILE, ES_LAUNCHER_DST_FILE):
                os.system('sudo cp %s %s >> /dev/null 2>&1' % \
                         (ES_LAUNCHER_DST_FILE, ES_LAUNCHER_BCK_FILE))
                os.system('sudo cp %s %s >> /dev/null 2>&1' % \
                         (ES_LAUNCHER_SRC_FILE, ES_LAUNCHER_DST_FILE))
                p_bFixed = True
        if p_bFixed:
            os.system('sudo chmod +x %s >> /dev/null 2>&1' % \
                      ES_LAUNCHER_DST_FILE)
            self.m_lLayer40_core = [["Please Wait", 
                                     "Fixed ES Launcher", 
                                     "System Will Reboot Now"],
                                     "icon_info"]
            time.sleep(6)
            os.system('sudo reboot')

    def __clean(self):
        pass

    def __temp(self):
        if CLEAN_LOG_ONSTART:
            remove_file(LOG_PATH)
        logging.basicConfig(filename=LOG_PATH, level=__DEBUG__,
        format='[%(asctime)s] %(levelname)s - %(filename)s:%(funcName)s - %(message)s')

if __name__ == '__main__':
    try:
        oMenu = config()
        os.system("clear")
        time.sleep(1)
    except Exception as e:
        with open(EXCEPTION_LOG, 'a') as f:
            f.write(str(e))
            f.write(traceback.format_exc())
