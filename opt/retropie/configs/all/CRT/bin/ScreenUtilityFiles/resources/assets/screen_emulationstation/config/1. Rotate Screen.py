#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Rotate Screen

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

import os
import sys
import pygame
import time
import commands
import filecmp
import subprocess
from pygame.locals import *

CRT_PATH = "/opt/retropie/configs/all/CRT"
RESOURCES_PATH = os.path.join(CRT_PATH, "bin/GeneralModule")
sys.path.append(RESOURCES_PATH)

from launcher_module.core_paths import *
from launcher_module.es_rotation import frontend_rotation
from launcher_module.file_helpers import modify_line
from launcher_module.utils import get_screen_resolution, something_is_bad
from launcher_module.core_controls import joystick, CRT_UP, CRT_DOWN, CRT_LEFT, \
                                          CRT_RIGHT, CRT_BUTTON

SKIN_THEME_PATH = os.path.join(CRT_RSC_PATH, "media/skin_rotate_screen")

ES_LAUNCHER_DST_FILE = os.path.join(RETROPIE_PATH,
                       "supplementary/emulationstation/emulationstation.sh")
ES_LAUNCHER_SRC_FILE = os.path.join(CRT_ES_RES_PATH,
                       "configs/default_emulationstation.sh")
ES_LAUNCHER_BCK_FILE = os.path.join(RETROPIE_PATH,
                       "supplementary/emulationstation/backup.emulationstation.sh")

CRT_ES_CONFIGS_PATH = os.path.join(CRT_ES_RES_PATH, "configs")
ROTMODES_TATE1_FILE = os.path.join(CRT_ES_CONFIGS_PATH, "es-select-tate1")
ROTMODES_TATE3_FILE = os.path.join(CRT_ES_CONFIGS_PATH, "es-select-tate3")
ROTMODES_YOKO_FILE = os.path.join(CRT_ES_CONFIGS_PATH, "es-select-yoko")

CURSOR_SOUND_FILE = os.path.join(CRT_SOUNDS_PATH, "sys_cursor_01.ogg")
CLICK_SOUND_FILE = os.path.join(CRT_SOUNDS_PATH, "sys_click_01.ogg")

y = 0
RES_X = 0
RES_Y = 0
iCurSide = 0

sCurSysRes = '240p'
sSystem50 = 'system50'
sSystem60 = 'system60'

PGoLoad = None
PGoCursor = None
PGoJoyHandler = None
oOption = None
oPosition = None
fullscreen = None
MAXoptions = 2

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
    pygame.quit()
    if p_iSide != None:
        frontend_rotation(p_iSide, True)
    sys.exit(0)

def init_screen():
    global fullscreen
    fullscreen = pygame.display.set_mode((RES_X, RES_Y), pygame.FULLSCREEN)
    fullscreen.fill((0,0,0))
    fullscreen.blit(wait, waitPos)
    pygame.display.flip()
    time.sleep(1)

def pygame_initialization():
    global PGoJoyHandler
    global PGoCursor
    global PGoLoad
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.init()
    pygame.display.init()
    pygame.mouse.set_visible(0)
    PGoCursor = pygame.mixer.Sound(CURSOR_SOUND_FILE)
    PGoLoad = pygame.mixer.Sound(CLICK_SOUND_FILE)
    PGoJoyHandler = joystick()

def script_initialization():
    global RES_X
    global RES_Y
    os.system('clear')
    RES_X, RES_Y = get_screen_resolution()
    check_es_launcher()
    get_config()
    pygame_initialization()

def draw_menu():
    fullscreen.blit(oOption, oPosition)
    pygame.display.flip()

script_initialization()

# Pygame Load Images
wait = pygame.image.load(os.path.join(SKIN_THEME_PATH, "wait_%s.png" % iCurSide))
waitPos = wait.get_rect()
waitPos.center = ((RES_X/2), (RES_Y/2))

option1 = pygame.image.load(os.path.join(SKIN_THEME_PATH, "rotate_yes_%s.png" % iCurSide))
option1Pos = option1.get_rect()
option1Pos.center = ((RES_X/2), (RES_Y/2))
option1_ENA = pygame.image.load(os.path.join(SKIN_THEME_PATH, "rotate_yes_ena_%s.png" % iCurSide))
option1_ENAPos = option1_ENA.get_rect()
option1_ENAPos.center = ((RES_X/2), (RES_Y/2))

option2 = pygame.image.load(os.path.join(SKIN_THEME_PATH, "rotate_180_%s.png" % iCurSide))
option2Pos = option2.get_rect()
option2Pos.center = ((RES_X/2), (RES_Y/2))
option2_ENA = pygame.image.load(os.path.join(SKIN_THEME_PATH, "rotate_180_ena_%s.png"%iCurSide))
option2_ENAPos = option2_ENA.get_rect()
option2_ENAPos.center = ((RES_X/2), (RES_Y/2))

option3 = pygame.image.load(os.path.join(SKIN_THEME_PATH, "rotate_cancel_%s.png" % iCurSide))
option3Pos = option3.get_rect()
option3Pos.center = ((RES_X/2), (RES_Y/2))
option3_ENA = pygame.image.load(os.path.join(SKIN_THEME_PATH, "rotate_cancel_ena_%s.png" % iCurSide))
option3_ENAPos = option3_ENA.get_rect()
option3_ENAPos.center = ((RES_X/2), (RES_Y/2))

oOption = option1
oPosition = option1Pos

init_screen()

while True:
    draw_menu()
    event = PGoJoyHandler.event_wait()
    #button
    if event & CRT_BUTTON:
        if y < 1:
            PGoLoad.play()
            oOption = option1_ENA
            oPosition = option1_ENAPos
            draw_menu()
            time.sleep(1)
            quit_module(0)
        elif y == 1:
            PGoLoad.play()
            oOption = option2_ENA
            oPosition = option2_ENAPos
            draw_menu()
            time.sleep(1)
            if iCurSide == 1:
                quit_module(-90)
            elif iCurSide == 3:
                quit_module(90)
        elif y == 2:
            PGoLoad.play()
            oOption = option3_ENA
            oPosition = option3_ENAPos
            draw_menu()
            time.sleep(1)
            quit_module()
    #down
    elif event & CRT_DOWN:
        if y < MAXoptions:
            PGoCursor.play()
            y = y + 1
            if y == 1:
                oOption = option2
                oPosition = option2Pos
            elif y == 2:
                oOption = option3
                oPosition = option3Pos
    #up
    elif event & CRT_UP:
        if y > 0:
            PGoCursor.play()
            y = y - 1
            if y == 1:
                oOption = option2
                oPosition = option2Pos
            elif y == 0:
                oOption = option1
                oPosition = option1Pos
quit_module()

