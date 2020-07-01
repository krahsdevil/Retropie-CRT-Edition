#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
PI2JAMMA hardware detection

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
import os, sys
import logging, traceback, keyboard
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(SCRIPT_DIR + "/../"))
from main_paths import MODULES_PATH
sys.path.append(MODULES_PATH)

from launcher_module.core_paths import TMP_LAUNCHER_PATH
from launcher_module.utils import check_process

__DEBUG__ = logging.INFO # logging.ERROR
LOG_PATH = os.path.join(TMP_LAUNCHER_PATH,"CRT_RGB_Cable.log")
logging.basicConfig(filename=LOG_PATH, level=__DEBUG__,
format='[%(asctime)s] %(levelname)s - %(filename)s:%(funcName)s - %(message)s')

def detect():
    sError = ""
    ctr = 0
    ctr_check = 0
    while True:
        try:
            if keyboard.is_pressed('&'):
                ctr += 1
        except Exception as e:
            if str(e) != sError:
                logging.info('ERROR: pi2jamma detection: %s' % str(e))
                sError = str(e)
        ctr_check += 1
        if ctr_check >= 1000:
            if ctr > 1: 
                logging.info("INFO: hardware pi2jamma found")
                logging.info("INFO: char '&' detected %s times" % ctr)
                return True
            else: 
                logging.info("WARNING: hardware pi2jamma not found")
                logging.info("WARNING: char '&' detected %s times" % ctr)
                return False
                
value = detect()
if value: sys.exit(100)
sys.exit(0)