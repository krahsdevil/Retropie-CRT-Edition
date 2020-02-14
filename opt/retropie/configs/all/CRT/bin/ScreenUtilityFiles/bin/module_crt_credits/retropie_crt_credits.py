#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Credits for Retropie CRT Edition

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
import os, sys, subprocess
import pygame

CRT_PATH = "/opt/retropie/configs/all/CRT"
RESOURCES_PATH = os.path.join(CRT_PATH, "bin/GeneralModule")
sys.path.append(RESOURCES_PATH)

from launcher_module.core_paths import *
from launcher_module.utils import ra_check_version, get_xy_screen, HideScreen
from launcher_module.screen import CRT

ROM_FILE = os.path.join(CRTADDONS_PATH, "addon_credits/flappybird.gba")
RA_GBA_CFG_FILE1 = os.path.join(RETROPIECFG_PATH, "gba/retroarch.cfg")
RA_GBA_CFG_FILE2 = os.path.join(CRTROOT_PATH, "Retroarch/configs/credits.cfg")
RA_GBA_CORE_FILE = os.path.join(CRTADDONS_PATH,
                  "addon_credits/mgba_libretro.so")

# Screen CRT Class
oCRT = None
oBlackScreen = None
sSystem = 'gba'

def launch_credits():
    global oCRT
    global oBlackScreen
    ra_check_version(RA_GBA_CFG_FILE2)
    oCRT = CRT(sSystem)
    oBlackScreen = HideScreen()
    oBlackScreen.fill()
    oCRT.screen_calculated(CFG_TIMINGS_FILE)
    commandline = "%s -L %s " % (RETROARCHBIN_FILE, RA_GBA_CORE_FILE)
    commandline += "--config %s " % RA_GBA_CFG_FILE1
    commandline += "--appendconfig %s " % RA_GBA_CFG_FILE2
    commandline += "\"%s\" " % ROM_FILE
    commandline += "> /dev/null 2>&1"
    oRunProcess = subprocess.Popen(commandline, shell=True)
    iExitCode = oRunProcess.wait()
    oCRT.screen_restore()

launch_credits()
sys.exit(iExitCode)
