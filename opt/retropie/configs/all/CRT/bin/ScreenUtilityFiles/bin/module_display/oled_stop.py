#!/usr/bin/python3
# -*- coding: utf-8 -*-


"""
I2C OLED Manager for piCRT addon

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

import os, sys, rpyc, time

sys.dont_write_bytecode = True

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(SCRIPT_DIR + "/../"))
from main_paths import MODULES_PATH
sys.path.append(MODULES_PATH)

from launcher_module.core_paths import CRT_OLED_PORT

def service_connection():
    global OledCon
    try: 
        if OledCon.root.status(): return True
    except: 
        try: 
            OledCon = rpyc.connect('localhost', CRT_OLED_PORT)
            if OledCon.root.status(): return True
        except: return False
    return False

if __name__ == '__main__':
    if service_connection(): 
        OledCon.root.quit()
        while service_connection():
            time.sleep(0.2)