#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
USB Automount module only for TATE mode

Module to check and load/unload USB Automount service for Retropie by -krahs-

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

# IMPORTS
import os, sys, commands, filecmp, time
import pygame

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(SCRIPT_DIR + "/../"))
from main_paths import MODULES_PATH
sys.path.append(MODULES_PATH)

from launcher_module.core_paths import *
from launcher_module.utils import get_screen_resolution
from launcher_module.core_controls import joystick, CRT_UP, CRT_DOWN, \
                                          CRT_LEFT, CRT_RIGHT, CRT_BUTTON

os.system('clear')

SKIN_THEME_PATH = os.path.join(CRT_RSC_PATH, "media/skin_automount_rotated")
CURSOR_SOUND_FILE = os.path.join(CRT_SOUNDS_PATH, "sys_cursor_01.ogg")
CLICK_SOUND_FILE = os.path.join(CRT_SOUNDS_PATH, "sys_click_01.ogg")

CRT_ES_CONFIGS_PATH = os.path.join(CRT_ES_RES_PATH, "configs")
ROTMODES_TATE1_FILE = os.path.join(CRT_ES_CONFIGS_PATH, "es-select-tate1")
ROTMODES_TATE3_FILE = os.path.join(CRT_ES_CONFIGS_PATH, "es-select-tate3")
ROTMODES_YOKO_FILE = os.path.join(CRT_ES_CONFIGS_PATH, "es-select-yoko")

USBAUTO_PATH = os.path.join(CRT_BIN_PATH, "AutomountService")
SERVICE_FILE_NAME = "CRT-Automount.service"
SERVICE_FILE = os.path.join(USBAUTO_PATH, SERVICE_FILE_NAME)
SCRIPT_FILE_NAME = "CRT-Automount.py"
SCRIPT_FILE = os.path.join(USBAUTO_PATH, SCRIPT_FILE_NAME)
TRG_MNT_FILE = os.path.join(USBAUTO_PATH, "mounted.cfg") #Trigger USB is mounted
TRG_UMNT_FILE = os.path.join(USBAUTO_PATH, "umounted.cfg") #Trigger USB is NOT mounted

bServiceExist = False
bServiceRun = False
bUSBMounted = False

y = 0

IOptMax = 1
Frame = None
option1 = None
option1_ENA = None
option2 = None
option2_ENA = None
option3 = None
option3Pos = None
option3_ENA = None
option3_ENAPos = None

PGoJoyHandler = None

sMountedPath = ""
RES_X = 0
RES_Y = 0
iCurSide = 0

def get_config():
    global iCurSide

    if os.path.exists(ROTMODES_TATE1_FILE):
        iCurSide = 1
    elif os.path.exists(ROTMODES_TATE3_FILE):
        iCurSide = 3
    else:
        sys.exit()

def check_service_files():
    """ Check if needed service files exists """
    bCheck01 = os.path.exists(SERVICE_FILE)
    bCheck02 = os.path.exists(SCRIPT_FILE)
    if bCheck01 and bCheck02:
        return True
    return False

def check_service_run():
    global bServiceExist
    global bServiceRun
    global bUSBMounted
    global sMountedPath
    global Frame
    global IOptMax
    global option1
    global option1_ENA
    global option2
    global option2_ENA
    global option3
    global option3Pos
    global option3_ENA
    global option3_ENAPos
    
    bServiceExist = False
    bServiceRun = False
    sCommand = 'systemctl list-units --all | grep \"%s\"' % SERVICE_FILE_NAME
    sCheckService = commands.getoutput(sCommand)

    if SERVICE_FILE_NAME in sCheckService:
        bServiceExist = True
    if 'running' in sCheckService:
        bServiceRun = True

    #If service exists and it's running check if usb is mounted
    if bServiceExist and bServiceRun:
        if os.path.exists(TRG_MNT_FILE):
            file = open(TRG_MNT_FILE, 'r')
            sMountedPath = file.readlines()
            file.close()
            bUSBMounted = True
            Frame = enabled_wej
            option1 = yes_wej
            option1_ENA = yesenabled_wej
            option2 = cancel_wej
            option2_ENA = cancelenabled_wej
            option3 = eject_wej
            option3_ENA = ejectenabled_wej
            option3Pos = option3.get_rect()
            option3Pos.center = ((RES_X/2), (RES_Y/2))
            option3_ENAPos = option3_ENA.get_rect()
            option3_ENAPos.center = ((RES_X/2), (RES_Y/2))
            IOptMax = 2
        else:
            bUSBMounted = False
            Frame = enabled
            option1 = yes
            option1_ENA = yesenabled
            option2 = cancel
            option2_ENA = cancelenabled
    elif not bServiceRun:
        Frame = disabled
        option1 = yes
        option1_ENA = yesenabled
        option2 = cancel
        option2_ENA = cancelenabled

def install_service():
    if check_service_files():
        os.system('sudo cp %s /etc/systemd/system/%s > /dev/null 2>&1'%(SERVICE_FILE, SERVICE_FILE_NAME))
        os.system('sudo chmod +x /etc/systemd/system/%s > /dev/null 2>&1'%SERVICE_FILE_NAME)
        os.system('sudo systemctl enable %s > /dev/null 2>&1'%SERVICE_FILE_NAME)
        os.system('sudo systemctl start %s > /dev/null 2>&1'%SERVICE_FILE_NAME)

def remove_service():
    if check_service_files() and bServiceRun:
        os.system('sudo systemctl disable %s > /dev/null 2>&1'%SERVICE_FILE_NAME)
        os.system('sudo systemctl stop %s > /dev/null 2>&1'%SERVICE_FILE_NAME)
        os.system('sudo rm /etc/systemd/system/%s > /dev/null 2>&1'%SERVICE_FILE_NAME)
        os.system('sudo umount -l /home/pi/RetroPie/roms > /dev/null 2>&1')
        os.system('sudo umount -l /home/pi/RetroPie/BIOS > /dev/null 2>&1')
        os.system('sudo umount -l /opt/retropie/configs/all/emulationstation/gamelists > /dev/null 2>&1')
        clean() # clean trigger files
        if bUSBMounted:
            restart_ES()

def eject_usb():
    os.system('sudo umount %s > /dev/null 2>&1' % sMountedPath[0])
    while not os.path.exists(TRG_UMNT_FILE):
        pass

def clean():
    if os.path.exists(TRG_MNT_FILE):
        os.system("rm %s > /dev/null 2>&1" % TRG_MNT_FILE)
    if os.path.exists(TRG_UMNT_FILE):
        os.system("rm %s > /dev/null 2>&1" % TRG_UMNT_FILE)

def restart_ES():
    """ Restart ES if it's running """
    sOutput = commands.getoutput('ps -A')
    if 'emulationstatio' in sOutput:
        commandline = "touch /tmp/es-restart "
        commandline += "&& pkill -f \"/opt/retropie"
        commandline += "/supplementary/.*/emulationstation([^.]|$)\""
        os.system(commandline)
        os.system('clear')
        time.sleep(1.5)

def pygame_initialization():
    global RES_X
    global RES_Y
    global PGoJoyHandler
    RES_X, RES_Y = get_screen_resolution()
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.init()
    pygame.display.init()
    pygame.mouse.set_visible(0)
    PGoJoyHandler = joystick()

def quit_module():
    PGoJoyHandler.quit()
    pygame.quit()
    sys.exit(0)

os.system('clear')
pygame_initialization()
get_config()

# FF files

PGoCursor = pygame.mixer.Sound(CURSOR_SOUND_FILE)
PGoLoad = pygame.mixer.Sound(CLICK_SOUND_FILE)

wait = pygame.image.load(os.path.join(SKIN_THEME_PATH, "wait_%s.png" % iCurSide))
waitPos = wait.get_rect()
waitPos.center = ((RES_X/2), (RES_Y/2))

extract = pygame.image.load(os.path.join(SKIN_THEME_PATH, "extract_%s.png" % iCurSide))
extractPos = extract.get_rect()
extractPos.center = ((RES_X/2), (RES_Y/2))

enabled = pygame.image.load(os.path.join(SKIN_THEME_PATH, "enabled_%s.png" % iCurSide))
enabledPos = enabled.get_rect()
enabledPos.center = ((RES_X/2), (RES_Y/2))

disabled = pygame.image.load(os.path.join(SKIN_THEME_PATH, "disabled_%s.png" % iCurSide))
disabledPos = disabled.get_rect()
disabledPos.center = ((RES_X/2), (RES_Y/2))

cancel = pygame.image.load(os.path.join(SKIN_THEME_PATH, "cancel_%s.png" % iCurSide))
cancelPos = cancel.get_rect()
cancelPos.center = ((RES_X/2), (RES_Y/2))

yes = pygame.image.load(os.path.join(SKIN_THEME_PATH, "yes_%s.png" % iCurSide))
yesPos = yes.get_rect()
yesPos.center = ((RES_X/2), (RES_Y/2))

cancelenabled = pygame.image.load(os.path.join(SKIN_THEME_PATH, "cancelenabled_%s.png" % iCurSide))
cancelenabledPos = cancelenabled.get_rect()
cancelenabledPos.center = ((RES_X/2), (RES_Y/2))

yesenabled = pygame.image.load(os.path.join(SKIN_THEME_PATH, "yesenabled_%s.png" % iCurSide))
yesenabledPos = yesenabled.get_rect()
yesenabledPos.center = ((RES_X/2), (RES_Y/2))

enabled_wej = pygame.image.load(os.path.join(SKIN_THEME_PATH, "enabled_wej_%s.png" % iCurSide))
enabled_wejPos = enabled_wej.get_rect()
enabled_wejPos.center = ((RES_X/2), (RES_Y/2))

cancel_wej = pygame.image.load(os.path.join(SKIN_THEME_PATH, "cancel_wej_%s.png" % iCurSide))
cancel_wejPos = cancel_wej.get_rect()
cancel_wejPos.center = ((RES_X/2), (RES_Y/2))

yes_wej = pygame.image.load(os.path.join(SKIN_THEME_PATH, "yes_wej_%s.png" % iCurSide))
yes_wejPos = yes_wej.get_rect()
yes_wejPos.center = ((RES_X/2), (RES_Y/2))

cancelenabled_wej = pygame.image.load(os.path.join(SKIN_THEME_PATH, "cancelenabled_wej_%s.png" % iCurSide))
cancelenabled_wejPos = cancelenabled_wej.get_rect()
cancelenabled_wejPos.center = ((RES_X/2), (RES_Y/2))

yesenabled_wej = pygame.image.load(os.path.join(SKIN_THEME_PATH, "yesenabled_wej_%s.png" % iCurSide))
yesenabled_wejPos = yesenabled_wej.get_rect()
yesenabled_wejPos.center = ((RES_X/2), (RES_Y/2))

eject_wej = pygame.image.load(os.path.join(SKIN_THEME_PATH, "eject_wej_%s.png" % iCurSide))
eject_wejPos = eject_wej.get_rect()
eject_wejPos.center = ((RES_X/2), (RES_Y/2))

ejectenabled_wej = pygame.image.load(os.path.join(SKIN_THEME_PATH, "ejectenabled_wej_%s.png" % iCurSide))
ejectenabled_wejPos = ejectenabled_wej.get_rect()
ejectenabled_wejPos.center = ((RES_X/2), (RES_Y/2))

# SET SCREEN
fullscreen = pygame.display.set_mode((RES_X,RES_Y), pygame.FULLSCREEN)
fullscreen.fill((0,0,0))
fullscreen.blit(wait, waitPos)
pygame.display.flip()
time.sleep(1)
check_service_run()

FramePos = Frame.get_rect()
FramePos.center = ((RES_X/2), (RES_Y/2))
option1Pos = option1.get_rect()
option1Pos.center = ((RES_X/2), (RES_Y/2))
option2Pos = option2.get_rect()
option2Pos.center = ((RES_X/2), (RES_Y/2))

option1_ENAPos = option1_ENA.get_rect()
option1_ENAPos.center = ((RES_X/2), (RES_Y/2))
option2_ENAPos = option2_ENA.get_rect()
option2_ENAPos.center = ((RES_X/2), (RES_Y/2))

fullscreen.blit(Frame, FramePos)
fullscreen.blit(option1, option1Pos)
pygame.display.flip()

while True:
    event = PGoJoyHandler.event_wait()
    #button
    if event & CRT_BUTTON:
        if y < 1:
            PGoLoad.play()
            fullscreen.blit(option1_ENA, option1_ENAPos)
            pygame.display.flip()
            if bServiceRun:
                remove_service()
            elif not bServiceRun:
                install_service()
                time.sleep(2)

        if y == 1:
            PGoLoad.play()
            fullscreen.blit(option2_ENA, option2_ENAPos)
            pygame.display.flip()
            time.sleep(1)

        if y == 2:
            PGoLoad.play()
            fullscreen.blit(option3_ENA, option3_ENAPos)
            pygame.display.flip()
            time.sleep(1)
            fullscreen.blit(extract, extractPos)
            pygame.display.flip()
            time.sleep(3)
            eject_usb()
        quit_module()

    #down
    elif event & CRT_DOWN:
        if y < IOptMax:
            y = y + 1
            PGoCursor.play()
            if y == 1:
                fullscreen.blit(option2, option2Pos)
            elif y == 2:
                fullscreen.blit(option3, option3Pos)
            pygame.display.flip()

    #up
    elif event & CRT_UP:
        if y > 0:
            y = y - 1
            PGoCursor.play()
            if y == 1:
                fullscreen.blit(option2, option2Pos)
            elif y == 0:
                fullscreen.blit(option1, option1Pos)
            pygame.display.flip()

quit_module()