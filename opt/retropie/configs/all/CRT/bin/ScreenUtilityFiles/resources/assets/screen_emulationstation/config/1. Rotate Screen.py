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

sys.path.append('/opt/retropie/configs/all/CRT/bin/GeneralModule/')
sys.path.append('/opt/retropie/configs/all/CRT/')

from selector_module_functions import get_retropie_joy_map
from selector_module_functions import check_joy_event
from general_functions import modificarLinea
from general_functions import something_is_bad

os.system('clear')

x_screen = 0
y_screen = 0
RotationCurrentMode = 0
SystemRes = '240p'
ES_Res_50hz = 'system50'
ES_Res_60hz = 'system60'
CurTheme = "none"
VerTheme = "V270P-CRT-BASE"
HorTheme = "270P-CRT-BASE"
VideoUtilityCFG = "/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/config_files/utility.cfg"
EsSystemcfg = "/opt/retropie/configs/all/emulationstation/es_settings.cfg"

def get_config():
    global RotationCurrentMode
    global CurTheme
    global HorTheme
    global VerTheme
    global SystemRes
    HorTheme240p = "none"
    HorTheme270p = "none"
    VerTheme240p = "none"
    VerTheme270p = "none"
    
    with open(VideoUtilityCFG, 'r') as file:
        for line in file:
            line = line.strip().replace('=',' ').split(' ')
            if line[0] == '240p_theme_horizontal':
                HorTheme240p = line[1]
            elif line[0] == '270p_theme_horizontal':
                HorTheme270p = line[1]
            elif line[0] == '240p_theme_vertical':
                VerTheme240p = line[1]
            elif line[0] == '270p_theme_vertical':
                VerTheme270p = line[1]
            elif line[0] == 'default':
                if line[1] == ES_Res_50hz:
                    SystemRes = '270p'
                elif line[1] == ES_Res_60hz:
                    SystemRes = '240p'
    if SystemRes == '240p':
        HorTheme = HorTheme240p
        VerTheme = VerTheme240p
    elif SystemRes == '270p':
        HorTheme = HorTheme270p
        VerTheme = VerTheme270p
    if os.path.exists(EsSystemcfg):
        with open(EsSystemcfg, 'r') as file:
            for line in file:
                line = line.strip().replace('"','').replace(' ','').replace('/','').replace('>','').split('=')
                if 'ThemeSet' in line[1]:
                    CurTheme = line[2]
    if not os.path.exists('/opt/retropie/supplementary/emulationstation/emulationstation.sh'):
        os.system('sudo cp /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/configs/default_emulationstation.sh /opt/retropie/supplementary/emulationstation/emulationstation.sh >> /dev/null 2>&1')
    ESLauncher = filecmp.cmp('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/configs/default_emulationstation.sh', '/opt/retropie/supplementary/emulationstation/emulationstation.sh')
    if ESLauncher == False:
        os.system('sudo cp /opt/retropie/supplementary/emulationstation/emulationstation.sh /opt/retropie/supplementary/emulationstation/backup.emulationstation.sh >> /dev/null 2>&1')
        os.system('sudo cp /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/configs/default_emulationstation.sh /opt/retropie/supplementary/emulationstation/emulationstation.sh >> /dev/null 2>&1')
        os.system('sudo chmod +x /opt/retropie/supplementary/emulationstation/emulationstation.sh >> /dev/null 2>&1')
        infos = "System needs to reboot, please wait..."
        infos2 = ""
        something_is_bad(infos,infos2)
        os.system('sudo reboot')
    if os.path.exists('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/configs/es-select-tate1'):
        RotationCurrentMode = 1
        modificarLinea(VideoUtilityCFG, '%s_theme_vertical '%SystemRes, '%s_theme_vertical %s'%(SystemRes, CurTheme))
    elif os.path.exists('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/configs/es-select-tate3'):
        RotationCurrentMode = 3
        modificarLinea(VideoUtilityCFG, '%s_theme_vertical '%SystemRes, '%s_theme_vertical %s'%(SystemRes, CurTheme))
    elif os.path.exists('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/configs/es-select-yoko'):
        RotationCurrentMode = 0
        modificarLinea(VideoUtilityCFG, '%s_theme_horizontal '%SystemRes, '%s_theme_horizontal %s'%(SystemRes, CurTheme))
    else:
        RotationCurrentMode = 0
        modificarLinea(VideoUtilityCFG, '%s_theme_horizontal '%SystemRes, '%s_theme_horizontal %s'%(SystemRes, CurTheme))
    if RotationCurrentMode == 0:
        sys.exit()

def rotate_frontend(ToMode):
    os.system('rm /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/configs/es-select-tate1 >> /dev/null 2>&1')
    os.system('rm /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/configs/es-select-tate3 >> /dev/null 2>&1')
    os.system('rm /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/configs/es-select-yoko >> /dev/null 2>&1')
    if ToMode == 0:
        os.system('touch /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/configs/es-select-yoko')
        os.system('sudo rm /opt/retropie/configs/all/emulationstation/es_systems.cfg >> /dev/null 2>&1')
        os.system('sudo mv /etc/emulationstation/disabled.themes /etc/emulationstation/themes >> /dev/null 2>&1')
        os.system('sudo rm -R /opt/retropie/configs/all/emulationstation/themes/V270P-CRT-BASE/ >> /dev/null 2>&1')
        if os.path.exists('/opt/retropie/configs/fba/launching.png'):
            os.system('cp /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/launch_images/fbah_launching_%s.png /opt/retropie/configs/fba/launching.png >> /dev/null 2>&1'%SystemRes)
        if os.path.exists('/opt/retropie/configs/mame-advmame/launching.png'):
            os.system('cp /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/launch_images/advmameh_launching_%s.png /opt/retropie/configs/mame-advmame/launching.png >> /dev/null 2>&1'%SystemRes)
        if os.path.exists('/opt/retropie/configs/mame-libretro/launching.png'):
            os.system('cp /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/launch_images/mameh_launching_%s.png /opt/retropie/configs/mame-libretro/launching.png >> /dev/null 2>&1'%SystemRes)
        if os.path.exists('/opt/retropie/configs/psx/launching.png'):
            os.system('cp /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/launch_images/psxh_launching_%s.png /opt/retropie/configs/psx/launching.png >> /dev/null 2>&1'%SystemRes)
        os.system('sudo cp /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/splash_screen/CRT-Retropie-Load_H.mp4 /opt/retropie/supplementary/splashscreen/CRT-Retropie-Load.mp4 >> /dev/null 2>&1')
        modificarLinea(EsSystemcfg, '"ThemeSet"', '<string name="ThemeSet" value="%s" />'%HorTheme)
        modificarLinea(VideoUtilityCFG, 'frontend_rotation', 'frontend_rotation 0')
    if ToMode == 3:
        os.system('touch /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/configs/es-select-tate3')
        os.system('cp /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/configs/vertical_es_systems.cfg /opt/retropie/configs/all/emulationstation/es_systems.cfg >> /dev/null 2>&1')
        os.system('sudo mv /etc/emulationstation/themes /etc/emulationstation/disabled.themes >> /dev/null 2>&1')
        if not os.path.exists('/opt/retropie/configs/all/emulationstation/themes'):
            os.system('mkdir /opt/retropie/configs/all/emulationstation/themes >> /dev/null 2>&1')
        os.system('cp -R /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/themes/V270P-CRT-BASE/ /opt/retropie/configs/all/emulationstation/themes/ >> /dev/null 2>&1')
        if os.path.exists('/opt/retropie/configs/fba/launching.png'):
            os.system('cp /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/launch_images/fbav3_launching_%s.png /opt/retropie/configs/fba/launching.png >> /dev/null 2>&1'%SystemRes)
        if os.path.exists('/opt/retropie/configs/mame-advmame/launching.png'):
            os.system('cp /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/launch_images/advmamev3_launching_%s.png /opt/retropie/configs/mame-advmame/launching.png >> /dev/null 2>&1'%SystemRes)
        if os.path.exists('/opt/retropie/configs/mame-libretro/launching.png'):
            os.system('cp /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/launch_images/mamev3_launching_%s.png /opt/retropie/configs/mame-libretro/launching.png >> /dev/null 2>&1'%SystemRes)
        if os.path.exists('/opt/retropie/configs/psx/launching.png'):
            os.system('cp /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/launch_images/psxv3_launching_%s.png /opt/retropie/configs/psx/launching.png >> /dev/null 2>&1'%SystemRes)
        os.system('sudo cp /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/splash_screen/CRT-Retropie-Load_V3.mp4 /opt/retropie/supplementary/splashscreen/CRT-Retropie-Load.mp4 >> /dev/null 2>&1')
        modificarLinea(EsSystemcfg, '"ThemeSet"', '<string name="ThemeSet" value="%s" />'%VerTheme)
        modificarLinea(VideoUtilityCFG, 'frontend_rotation', 'frontend_rotation -90')
    if ToMode == 1:
        os.system('touch /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/configs/es-select-tate1')
        os.system('cp /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/configs/vertical_es_systems.cfg /opt/retropie/configs/all/emulationstation/es_systems.cfg >> /dev/null 2>&1')
        os.system('sudo mv /etc/emulationstation/themes /etc/emulationstation/disabled.themes >> /dev/null 2>&1')
        if not os.path.exists('/opt/retropie/configs/all/emulationstation/themes'):
            os.system('mkdir /opt/retropie/configs/all/emulationstation/themes >> /dev/null 2>&1')
        os.system('cp -R /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/themes/V270P-CRT-BASE/ /opt/retropie/configs/all/emulationstation/themes/ >> /dev/null 2>&1')
        if os.path.exists('/opt/retropie/configs/fba/launching.png'):
            os.system('cp /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/launch_images/fbav1_launching_%s.png /opt/retropie/configs/fba/launching.png >> /dev/null 2>&1'%SystemRes)
        if os.path.exists('/opt/retropie/configs/mame-advmame/launching.png'):
            os.system('cp /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/launch_images/advmamev1_launching_%s.png /opt/retropie/configs/mame-advmame/launching.png >> /dev/null 2>&1'%SystemRes)
        if os.path.exists('/opt/retropie/configs/mame-libretro/launching.png'):
            os.system('cp /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/launch_images/mamev1_launching_%s.png /opt/retropie/configs/mame-libretro/launching.png >> /dev/null 2>&1'%SystemRes)
        if os.path.exists('/opt/retropie/configs/psx/launching.png'):
            os.system('cp /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/launch_images/psxv1_launching_%s.png /opt/retropie/configs/psx/launching.png >> /dev/null 2>&1'%SystemRes)
        os.system('sudo cp /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/splash_screen/CRT-Retropie-Load_V1.mp4 /opt/retropie/supplementary/splashscreen/CRT-Retropie-Load.mp4 >> /dev/null 2>&1')
        modificarLinea(EsSystemcfg, '"ThemeSet"', '<string name="ThemeSet" value="%s" />'%VerTheme)
        modificarLinea(VideoUtilityCFG, 'frontend_rotation', 'frontend_rotation 90')

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
get_config()
get_retropie_joy_map()


# VARIABLES

# FF files
wait = pygame.image.load('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/media/skin_rotate_screen/wait_%s.png'%RotationCurrentMode)
waitPos = wait.get_rect()
waitPos.center = ((x_screen/2), (y_screen/2))

option1 = pygame.image.load('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/media/skin_rotate_screen/rotate_yes_%s.png'%RotationCurrentMode)
option1Pos = option1.get_rect()
option1Pos.center = ((x_screen/2), (y_screen/2))
option1_ENA = pygame.image.load('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/media/skin_rotate_screen/rotate_yes_ena_%s.png'%RotationCurrentMode)
option1_ENAPos = option1_ENA.get_rect()
option1_ENAPos.center = ((x_screen/2), (y_screen/2))

option2 = pygame.image.load('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/media/skin_rotate_screen/rotate_180_%s.png'%RotationCurrentMode)
option2Pos = option2.get_rect()
option2Pos.center = ((x_screen/2), (y_screen/2))
option2_ENA = pygame.image.load('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/media/skin_rotate_screen/rotate_180_ena_%s.png'%RotationCurrentMode)
option2_ENAPos = option2_ENA.get_rect()
option2_ENAPos.center = ((x_screen/2), (y_screen/2))

option3 = pygame.image.load('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/media/skin_rotate_screen/rotate_cancel_%s.png'%RotationCurrentMode)
option3Pos = option3.get_rect()
option3Pos.center = ((x_screen/2), (y_screen/2))
option3_ENA = pygame.image.load('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/media/skin_rotate_screen/rotate_cancel_ena_%s.png'%RotationCurrentMode)
option3_ENAPos = option3_ENA.get_rect()
option3_ENAPos.center = ((x_screen/2), (y_screen/2))

cursor = pygame.mixer.Sound("/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/media/skin_rotate_screen/cursor.wav")
load = pygame.mixer.Sound("/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/media/skin_rotate_screen/load.wav")
os.system('clear')


# SET SCREEN
fullscreen = pygame.display.set_mode((x_screen,y_screen), FULLSCREEN)
fullscreen.fill((0,0,0))
# PASTE PICTURE ON FULLSCREEN
fullscreen.blit(wait, waitPos)
pygame.display.flip()
time.sleep(1)
MAXoptions = 2

def quit_module(RebootSys):
    pygame.display.quit()
    pygame.quit()
    if RebootSys == True:
        output = commands.getoutput('ps -A')
        if 'emulationstatio' in output:
            commandline = "touch /tmp/es-restart "
            commandline += "&& pkill -f \"/opt/retropie"
            commandline += "/supplementary/.*/emulationstation([^.]|$)\""
            os.system(commandline)
            sys.exit()
    sys.exit()

#fullscreen.blit(Frame, (119,80))
fullscreen.blit(option1, option1Pos)
pygame.display.flip()

y = 0


while True:
    pygame.event.clear()
    event = pygame.event.wait()
    action = check_joy_event(event)
    #button
    if action == 'KEYBOARD' or action == 'JOYBUTTONB' or action == 'JOYBUTTONA':
        if y < 1:
            load.play()
            fullscreen.blit(option1_ENA, option1_ENAPos)
            pygame.display.flip()
            rotate_frontend(0)
            time.sleep(1)
            quit_module(True)

        if y == 1:
            load.play()
            fullscreen.blit(option2_ENA, option2_ENAPos)
            pygame.display.flip()
            time.sleep(1)
            if RotationCurrentMode == 1:
                rotate_frontend(3)
            elif RotationCurrentMode == 3:
                rotate_frontend(1)
            quit_module(True)

        if y == 2:
            load.play()
            fullscreen.blit(option3_ENA, option3_ENAPos)
            pygame.display.flip()
            time.sleep(1)
            quit_module(False)

    #down
    elif action == 'DOWNKEYBOARD' or action == 'JOYHATDOWN' or action == 'AXISDOWN':
        if y < MAXoptions:
            y = y + 1
            cursor.play()
            if y == 1:
                fullscreen.blit(option2, option2Pos)
            elif y == 2:
                fullscreen.blit(option3, option3Pos)
            pygame.display.flip()

    #up
    elif action == 'UPKEYBOARD' or action == 'JOYHATUP' or action == 'AXISUP':
        if y > 0:
            y = y - 1
            cursor.play()
            if y == 1:
                fullscreen.blit(option2, option2Pos)
            elif y == 0:
                fullscreen.blit(option1, option1Pos)
            pygame.display.flip()
quit_module()

