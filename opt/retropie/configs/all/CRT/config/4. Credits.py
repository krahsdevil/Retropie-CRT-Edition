#!/usr/bin/python
# coding: utf-8
# Retropie code/integration by -krahs- (2019)
#
# unlicense.org
#
# This script can be heavily optimized.
#
import struct
import os
import os.path
import sys
import shutil
import pygame
import time
import subprocess
sys.path.append('/opt/retropie/configs/all/CRT/')
sys.path.append('/opt/retropie/configs/all/CRT/bin/GeneralModule/')

from pygame.locals import *
from general_functions import *
from math import *

os.system('clear')

x_screen = 0
y_screen = 0

def get_xy_screen():
    global x_screen
    global y_screen
    process = subprocess.Popen("fbset", stdout=subprocess.PIPE)
    output = process.stdout.read()
    for line in output.splitlines():
        if 'x' in line and 'mode' in line:
            ResMode = line
            ResMode = ResMode.replace('"','').replace('x',' ').split(' ')
            x_screen = int(ResMode[1])
            y_screen = int(ResMode[2])

get_xy_screen()
pygame.init()
pygame.display.init()
pygame.mouse.set_visible(0)

pygame.display.set_mode((x_screen,y_screen), FULLSCREEN)
sucfg = '/opt/retropie/configs/all/CRT/su.cfg'
timings_full_path = "/opt/retropie/configs/all/CRT/Resolutions/base_systems.cfg"
libretro_core_path = "/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/addons/addon_credits/mgba_libretro.so"
game_path = "/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/addons/addon_credits/flappybird.gba"
ra_cfg_path = "/opt/retropie/configs/all/CRT/Retroarch/configs/credits.cfg"
configgen_retroarchcustom = "/opt/retropie/configs/all/retroarch.cfg"
retroarcharcade = "/tmp/retroarcharcade.cfg"

Check_RetroArch_Version(ra_cfg_path)

crt_open_screen_from_timings_cfg('test',timings_full_path)
commandline = "/opt/retropie/emulators/retroarch/bin/retroarch -L \"%s\" --config %s --appendconfig %s \"%s\"" % (libretro_core_path, configgen_retroarchcustom, ra_cfg_path, game_path)
os.system(commandline)
es_restore_screen()
pygame.quit()
sys.exit()
