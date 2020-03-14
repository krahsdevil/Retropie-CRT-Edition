#!/usr/bin/python
# coding: utf-8
#
# Retropie code/integration by -krahs- (2019)
#
# unlicense.org
#
# This script can be heavily optimized.

# IMPORTS
import struct
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

from launcher_module.core_controls import joystick, CRT_UP, CRT_DOWN, \
                                          CRT_LEFT, CRT_RIGHT, CRT_BUTTON

os.system('clear')

x_screen = 0
y_screen = 0
RotationCurrentMode = 0
def get_config():
    global RotationCurrentMode
    ESLauncher = filecmp.cmp('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/configs/default_emulationstation.sh', '/opt/retropie/supplementary/emulationstation/emulationstation.sh')
    if not os.path.exists('/opt/retropie/supplementary/emulationstation/emulationstation.sh') or ESLauncher == False:
        os.system('sudo cp /opt/retropie/supplementary/emulationstation/emulationstation.sh /opt/retropie/supplementary/emulationstation/backup.emulationstation.sh >> /dev/null 2>&1')
        os.system('sudo cp /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/configs/default_emulationstation.sh /opt/retropie/supplementary/emulationstation/emulationstation.sh >> /dev/null 2>&1')
        os.system('sudo chmod +x /opt/retropie/supplementary/emulationstation/emulationstation.sh >> /dev/null 2>&1')

    if os.path.exists('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/configs/es-select-tate1'):
        RotationCurrentMode = 1
    elif os.path.exists('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/configs/es-select-tate3'):
        RotationCurrentMode = 3
    elif os.path.exists('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/configs/es-select-yoko'):
        RotationCurrentMode = 0
    else:
        RotationCurrentMode = 0
    
    if RotationCurrentMode == 0:
        sys.exit()

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
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
pygame.display.init()
pygame.mouse.set_visible(0)
PGoJoyHandler = joystick()
get_config()

# VARIABLES
state_up = 0
state_down = 0
state_left = 0
state_right = 0
threshold = 1000 # Analogic middle to debounce
joystick = 0 # 0 is the 1sf joystick

# FF files
wait = pygame.image.load('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/media/skin_automount_rotated/wait_%s.png'%RotationCurrentMode)
waitPos = wait.get_rect()
waitPos.center = ((x_screen/2), (y_screen/2))

extract = pygame.image.load('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/media/skin_automount_rotated/extract_%s.png'%RotationCurrentMode)
extractPos = extract.get_rect()
extractPos.center = ((x_screen/2), (y_screen/2))

enabled = pygame.image.load('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/media/skin_automount_rotated/enabled_%s.png'%RotationCurrentMode)
enabledPos = enabled.get_rect()
enabledPos.center = ((x_screen/2), (y_screen/2))

disabled = pygame.image.load('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/media/skin_automount_rotated/disabled_%s.png'%RotationCurrentMode)
disabledPos = disabled.get_rect()
disabledPos.center = ((x_screen/2), (y_screen/2))

cancel = pygame.image.load('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/media/skin_automount_rotated/cancel_%s.png'%RotationCurrentMode)
cancelPos = cancel.get_rect()
cancelPos.center = ((x_screen/2), (y_screen/2))

yes = pygame.image.load('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/media/skin_automount_rotated/yes_%s.png'%RotationCurrentMode)
yesPos = yes.get_rect()
yesPos.center = ((x_screen/2), (y_screen/2))

cancelenabled = pygame.image.load('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/media/skin_automount_rotated/cancelenabled_%s.png'%RotationCurrentMode)
cancelenabledPos = cancelenabled.get_rect()
cancelenabledPos.center = ((x_screen/2), (y_screen/2))

yesenabled = pygame.image.load('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/media/skin_automount_rotated/yesenabled_%s.png'%RotationCurrentMode)
yesenabledPos = yesenabled.get_rect()
yesenabledPos.center = ((x_screen/2), (y_screen/2))

enabled_wej = pygame.image.load('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/media/skin_automount_rotated/enabled_wej_%s.png'%RotationCurrentMode)
enabled_wejPos = enabled_wej.get_rect()
enabled_wejPos.center = ((x_screen/2), (y_screen/2))

cancel_wej = pygame.image.load('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/media/skin_automount_rotated/cancel_wej_%s.png'%RotationCurrentMode)
cancel_wejPos = cancel_wej.get_rect()
cancel_wejPos.center = ((x_screen/2), (y_screen/2))

yes_wej = pygame.image.load('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/media/skin_automount_rotated/yes_wej_%s.png'%RotationCurrentMode)
yes_wejPos = yes_wej.get_rect()
yes_wejPos.center = ((x_screen/2), (y_screen/2))

cancelenabled_wej = pygame.image.load('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/media/skin_automount_rotated/cancelenabled_wej_%s.png'%RotationCurrentMode)
cancelenabled_wejPos = cancelenabled_wej.get_rect()
cancelenabled_wejPos.center = ((x_screen/2), (y_screen/2))

yesenabled_wej = pygame.image.load('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/media/skin_automount_rotated/yesenabled_wej_%s.png'%RotationCurrentMode)
yesenabled_wejPos = yesenabled_wej.get_rect()
yesenabled_wejPos.center = ((x_screen/2), (y_screen/2))

eject_wej = pygame.image.load('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/media/skin_automount_rotated/eject_wej_%s.png'%RotationCurrentMode)
eject_wejPos = eject_wej.get_rect()
eject_wejPos.center = ((x_screen/2), (y_screen/2))

ejectenabled_wej = pygame.image.load('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/media/skin_automount_rotated/ejectenabled_wej_%s.png'%RotationCurrentMode)
ejectenabled_wejPos = ejectenabled_wej.get_rect()
ejectenabled_wejPos.center = ((x_screen/2), (y_screen/2))

cursor = pygame.mixer.Sound("/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/media/skin_automount_rotated/cursor.wav")
load = pygame.mixer.Sound("/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/media/skin_automount_rotated/load.wav")
os.system('clear')
def InstallServiceAutomount():
    if os.path.exists('/opt/retropie/configs/all/CRT/bin/AutomountService/CRT-Automount.service') and os.path.exists('/opt/retropie/configs/all/CRT/bin/AutomountService/CRT-Automount.py'):
        os.system('sudo cp /opt/retropie/configs/all/CRT/bin/AutomountService/CRT-Automount.service /etc/systemd/system/CRT-Automount.service > /dev/null 2>&1')
        os.system('sudo systemctl enable CRT-Automount.service > /dev/null 2>&1')
        os.system('sudo systemctl start CRT-Automount.service > /dev/null 2>&1')
    else:
        pygame.display.quit()
        pygame.quit()
        sys.exit()

def DesInstallServiceAutomount():
    if os.path.exists('/opt/retropie/configs/all/CRT/bin/AutomountService/CRT-Automount.service') and os.path.exists('/opt/retropie/configs/all/CRT/bin/AutomountService/CRT-Automount.py'):
        os.system('sudo systemctl disable CRT-Automount.service > /dev/null 2>&1')
        os.system('sudo systemctl stop CRT-Automount.service > /dev/null 2>&1')
        os.system('sudo rm /etc/systemd/system/CRT-Automount.service > /dev/null 2>&1')
        os.system("sudo umount -l /home/pi/RetroPie/roms > /dev/null 2>&1")
        os.system("sudo umount -l /home/pi/RetroPie/BIOS > /dev/null 2>&1")
        os.system("sudo umount -l /opt/retropie/configs/all/emulationstation/gamelists > /dev/null 2>&1")
        output = commands.getoutput('ps -A')
        if 'emulationstatio' in output:
            commandline = "touch /tmp/es-restart "
            commandline += "&& pkill -f \"/opt/retropie"
            commandline += "/supplementary/.*/emulationstation([^.]|$)\""
            os.system(commandline)
            time.sleep(1)
            sys.exit()
    else:
        pygame.display.quit()
        pygame.quit()
        sys.exit()


# SET SCREEN
fullscreen = pygame.display.set_mode((x_screen,y_screen), FULLSCREEN)
fullscreen.fill((0,0,0))
# PASTE PICTURE ON FULLSCREEN
fullscreen.blit(wait, waitPos)
pygame.display.flip()
time.sleep(1)
CheckService = commands.getoutput('systemctl list-units --all | grep \"CRT-Automount.service\"')
if 'CRT-Automount.service' in CheckService:
    ServiceExist = True
    if 'running' in CheckService:
        ServiceRunning = True
        if os.path.exists('/opt/retropie/configs/all/CRT/bin/AutomountService/mounted.cfg'):
            MountedFile = open('/opt/retropie/configs/all/CRT/bin/AutomountService/mounted.cfg', 'r')
            MountedPaths = MountedFile.readlines()
            #MountedPaths = MountedPaths.split(' ')
            MountedFile.close()
            Frame = enabled_wej
            option1 = yes_wej
            option1_ENA = yesenabled_wej
            option2 = cancel_wej
            option2_ENA = cancelenabled_wej
            option3 = eject_wej
            option3_ENA = ejectenabled_wej
            option3Pos = option3.get_rect()
            option3Pos.center = ((x_screen/2), (y_screen/2))
            option3_ENAPos = option3_ENA.get_rect()
            option3_ENAPos.center = ((x_screen/2), (y_screen/2))
            MAXoptions = 2
        else:
            Frame = enabled
            option1 = yes
            option1_ENA = yesenabled
            option2 = cancel
            option2_ENA = cancelenabled
            MAXoptions = 1
    else:
        ServiceRunning = False
        Frame = disabled
        option1 = yes
        option1_ENA = yesenabled
        option2 = cancel
        option2_ENA = cancelenabled
        MAXoptions = 1
else:
    ServiceExist = False
    ServiceRunning = False
    Frame = disabled
    option1 = yes
    option1_ENA = yesenabled
    option2 = cancel
    option2_ENA = cancelenabled
    MAXoptions = 1

def quit_moudule():
    PGoJoyHandler.quit()
    pygame.display.quit()
    pygame.quit()
    sys.exit()

FramePos = Frame.get_rect()
FramePos.center = ((x_screen/2), (y_screen/2))
option1Pos = option1.get_rect()
option1Pos.center = ((x_screen/2), (y_screen/2))
option2Pos = option2.get_rect()
option2Pos.center = ((x_screen/2), (y_screen/2))

option1_ENAPos = option1_ENA.get_rect()
option1_ENAPos.center = ((x_screen/2), (y_screen/2))
option2_ENAPos = option2_ENA.get_rect()
option2_ENAPos.center = ((x_screen/2), (y_screen/2))

fullscreen.blit(Frame, FramePos)
fullscreen.blit(option1, option1Pos)
pygame.display.flip()

y = 0


while True:
    event = PGoJoyHandler.event_wait()
    #button
    if event & CRT_BUTTON:
        if y < 1:
            load.play()
            fullscreen.blit(option1_ENA, option1_ENAPos)
            pygame.display.flip()
            time.sleep(1)
            if ServiceRunning == True:
                DesInstallServiceAutomount()
            elif ServiceRunning == False:
                InstallServiceAutomount()
            quit_moudule()

        if y == 1:
            load.play()
            fullscreen.blit(option2_ENA, option2_ENAPos)
            pygame.display.flip()
            time.sleep(1)
            quit_moudule()

        if y == 2:
            load.play()
            fullscreen.blit(option3_ENA, option3_ENAPos)
            pygame.display.flip()
            time.sleep(1)
            fullscreen.blit(extract, extractPos)
            pygame.display.flip()
            time.sleep(3)
            os.system('sudo umount %s > /dev/null 2>&1' % MountedPaths[0])
            while True:
                if os.path.exists('/opt/retropie/configs/all/CRT/bin/AutomountService/umounted.cfg'):
                    break
            quit_moudule()

    #down
    elif event & CRT_DOWN:
        if y < MAXoptions:
            y = y + 1
            cursor.play()
            if y == 1:
                fullscreen.blit(option2, option2Pos)
            elif y == 2:
                fullscreen.blit(option3, option3Pos)
            pygame.display.flip()

    #up
    elif event & CRT_UP:
        if y > 0:
            y = y - 1
            cursor.play()
            if y == 1:
                fullscreen.blit(option2, option2Pos)
            elif y == 0:
                fullscreen.blit(option1, option1Pos)
            pygame.display.flip()
quit_moudule()

