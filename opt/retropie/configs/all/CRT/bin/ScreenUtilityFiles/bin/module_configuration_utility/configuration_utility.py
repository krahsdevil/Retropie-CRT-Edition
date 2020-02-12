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

import pygame
import sys, os, commands, subprocess
import filecmp, time

CRT_PATH = "/opt/retropie/configs/all/CRT"
RESOURCES_PATH = os.path.join(CRT_PATH, "bin/GeneralModule")
sys.path.append(RESOURCES_PATH)

from launcher_module.core_paths import *
from launcher_module.core_choices_dynamic import choices
from launcher_module.file_helpers import modify_line
from launcher_module.utils import get_xy_screen, something_is_bad
from launcher_module.core_controls import joystick, CRT_UP, CRT_DOWN, CRT_LEFT, \
                                          CRT_RIGHT, CRT_BUTTON

FONT_FILE = os.path.join(CRTFONTS_PATH, "PetMe64.ttf")
SCREEN_MNG_PATH = os.path.join(CRTMODULES_PATH, "module_screen_tools_manager")
SCREEN_MNG_FILE = os.path.join(SCREEN_MNG_PATH, "screen_tools_manager.py")

# menu centering and screen adjusters
x_screen = 0
y_screen = 0
y_margin = 0
MarginNorm = 0.1482
Interline = 0
LineMov = 0

# menu positions
data_x = 0
list_x = 0
x = 0
y = 0
iCurOption = 0

SystemRes = ""
ES_Res_50hz = 'system50'
ES_Res_60hz = 'system60'
CurTheme = "none"
VerTheme = "V270P-CRT-BASE"
HorTheme = "270P-CRT-SNES-MINI"
ServiceRunning = False
ServiceExist = False
ES_Restart = False
bRotateES = False

# pygame configurations
PGoJoyHandler = None
PGoScreen = None
PGoFont = None
BLUELIGHT = pygame.Color(165, 165, 255)
BLUEDARK = pygame.Color(66, 66, 231)
BLUEUNS = pygame.Color(110, 110, 255)
YELLOW = pygame.Color(255, 255, 0)
RED = pygame.Color(255, 0, 0)

# loading data from su.cfg
opt = [["1.GAMES ROTATION" , "Not PixelPerfect but playable on AdvMAME" , 0],
      ["2.FRONTEND ROTATION" , "This option requires rotate your monitor" , 0, 0],
      ["3.HANDHELD BEZELS" , "CAUTION!!! Long use can damage the screen" , 0],
      ["4.FREQUENCY SELECTOR" , "Set Frequency at 50/60hz, Auto or Manual" , 0],
      ["5.VIDEO CONFIG>" , "Advanced Video Configuration"],
      ['6.BACKGROUND MUSIC' , 'Play your music with emulationstation', 0],
      ['7.INTEGER SCALE' , 'ONLY for LibRetro Arcade and NEOGEO Games', 0],
      ['8.SCUMMVM ARC' , 'Aspect Ratio Correction: Stretch but NO PixelPerfect', 0],
      ["<EXIT" , "Save and Exit"]]
      
DEFAULT_CONFIG = "\"default system50\n"
DEFAULT_CONFIG += "system60_timings 320 1 10 30 40 240 1 6 5 12 0 0 0 60 0 6400000 1\n"
DEFAULT_CONFIG += "system60_offsetX 0\n"
DEFAULT_CONFIG += "system60_offsetY 0\n"
DEFAULT_CONFIG += "system60_width 0\n"
DEFAULT_CONFIG += "system60_height 0\n"
DEFAULT_CONFIG += "system50_timings 450 1 50 32 94 270 1 12 5 26 0 0 0 50 0 9600000 1\n"
DEFAULT_CONFIG += "system50_offsetX 0\n"
DEFAULT_CONFIG += "system50_offsetY 0\n"
DEFAULT_CONFIG += "system50_width 0\n"
DEFAULT_CONFIG += "system50_height 0\n"
DEFAULT_CONFIG += "test60_timings 1920 240 60.00 -4 -10 3 48 192 240 5 15734\n"
DEFAULT_CONFIG += "test60_offsetX 0\n"
DEFAULT_CONFIG += "test60_offsetY 0\n"
DEFAULT_CONFIG += "test60_width 0\n"
DEFAULT_CONFIG += "test60_height 0\n"
DEFAULT_CONFIG += "game_rotation 0\n"
DEFAULT_CONFIG += "frontend_rotation 0\n"
DEFAULT_CONFIG += "handheld_bezel 0\n"
DEFAULT_CONFIG += "freq_selector 0\n"
DEFAULT_CONFIG += "integer_scale 0\n"
DEFAULT_CONFIG += "scummvm_arc 0\n"
DEFAULT_CONFIG += "240p_theme_vertical V270P-CRT-BASE\n"
DEFAULT_CONFIG += "270p_theme_vertical V270P-CRT-BASE\n"
DEFAULT_CONFIG += "240p_theme_horizontal 240P-CRT-BUBBLEGUM\n"
DEFAULT_CONFIG += "270p_theme_horizontal 270P-CRT-SNES-MINI\n\""

def show_info(p_sMessage, p_iTime = 2000, p_sTitle = None):
    ch = choices()
    if p_sTitle:
        ch.set_title(p_sTitle)
    ch.load_choices([(p_sMessage, "OK")])
    ch.show(p_iTime)

def get_screen_size_adjust():
    global y_margin
    global Interline
    global LineMov
    global data_x
    global list_x
    global x_screen
    global y_screen
    
    # Get current x,y resolution
    x_screen, y_screen = get_xy_screen()
    
    if y_screen > 270:
        Multiplier = int((y_screen-270)/8)
        Interline = 20-Multiplier
        LineMov = int(Multiplier/2)
        y_margin = 20-((y_screen-270)-(Multiplier*9))
    elif y_screen < 270:
        Multiplier = int((270-y_screen)/8)
        Interline = 20-Multiplier
        LineMov = int(-1*(Multiplier/2))
        y_margin = 20-((270-y_screen)-(Multiplier*9))
        
    elif y_screen == 270:
        y_margin = 20
        Interline = 20
        
    if x_screen < 340:
        data_x = 269
        list_x = 50
    else:
        data_x = 340
        list_x = 100

def pygame_initialization():
    global PGoScreen
    global PGoFont
    global PGoJoyHandler
    pygame.init()
    pygame.mouse.set_visible(0)
    PGoJoyHandler = joystick()
    PGoJoyHandler.find_joy()
    PGoFont = pygame.font.Font(FONT_FILE, 8)
    PGoScreen = pygame.display.set_mode((x_screen,y_screen), pygame.FULLSCREEN)
    
def pygame_unload():
    pygame.display.quit()
    pygame.quit()

def script_initialization():
    os.system('clear')
    get_screen_size_adjust()
    get_config()
    pygame_initialization()
   
def text_print(txt, xcoord, ycoord, color, center):
    if x_screen <= 340:
        txt = txt[0:28]
        if len(txt) >= 28 :
            txt = txt + '...'
    else:
        txt = txt[0:44]
        if len(txt) >= 44 :
            txt = txt + '...'

    if center == True:
        text = PGoFont.render(txt, True, color)
        textPos = text.get_rect()
        textPos.center = (x_screen/2, ycoord+6)
        PGoScreen.blit(text,textPos)
    else:
        PGoScreen.blit(PGoFont.render(txt, 1, color), (xcoord, ycoord))

def draw_arrow_left(add_space=0):
    PGoScreen.blit((PGoFont.render('<<', 1, (YELLOW))), (data_x-(len(str(opt[iCurOption][2]))*8)-18-(8*add_space), (30+y_margin+LineMov) + iCurOption * Interline))

def draw_arrow_right():
    PGoScreen.blit((PGoFont.render('>>', 1, (YELLOW))), (data_x+2, (30+y_margin+LineMov)+ iCurOption *Interline))

def save_configuration():
    modify_line(CFG_VIDEOUTILITY_FILE,'game_rotation','game_rotation %s'%opt[0][2])
    modify_line(CFG_VIDEOUTILITY_FILE,'frontend_rotation','frontend_rotation %s'%opt[1][2])
    modify_line(CFG_VIDEOUTILITY_FILE,'handheld_bezel','handheld_bezel %s'%opt[2][2])
    modify_line(CFG_VIDEOUTILITY_FILE,'freq_selector','freq_selector %s'%opt[3][2])
    modify_line(CFG_VIDEOUTILITY_FILE,'integer_scale','integer_scale %s'%opt[6][2])
    modify_line(CFG_VIDEOUTILITY_FILE,'scummvm_arc','scummvm_arc %s'%opt[7][2])

def background_music_check():
    global opt
    global ServiceRunning
    global ServiceExist
    if not os.path.exists(RETROPIEMUS_PATH):
        os.makedirs(RETROPIEMUS_PATH)
        os.system('touch \"%s/place your background music here.txt\"' % RETROPIEMUS_PATH)
    CheckService = commands.getoutput('systemctl list-units --all | grep \"BackGroundMusic.service\"')
    if 'BackGroundMusic.service' in CheckService:
        ServiceExist = True
        if 'running' in CheckService:
            ServiceRunning = True
            opt[5][2] = 1
        else:
            ServiceRunning = False
            opt[5][2] = 0
    else:
        ServiceExist = False
        ServiceRunning = False
        opt[5][2] = 0

def background_music_install():
    global ServiceRunning
    global ServiceExist
    if ServiceExist == False:
        if os.path.exists('/opt/retropie/configs/all/CRT/bin/BackGroundMusic/BackGroundMusic.service') and os.path.exists('/opt/retropie/configs/all/CRT/bin/BackGroundMusic/BGM.py'):
            os.system('sudo cp /opt/retropie/configs/all/CRT/bin/BackGroundMusic/BackGroundMusic.service /etc/systemd/system/ > /dev/null 2>&1')
    os.system('sudo systemctl enable BackGroundMusic.service > /dev/null 2>&1')
    os.system('sudo systemctl start BackGroundMusic.service > /dev/null 2>&1')
    background_music_check()

def background_music_remove():
    if os.path.exists('/opt/retropie/configs/all/CRT/bin/BackGroundMusic/BackGroundMusic.service') and os.path.exists('/opt/retropie/configs/all/CRT/bin/BackGroundMusic/BGM.py'):
        os.system('sudo systemctl stop BackGroundMusic.service > /dev/null 2>&1')
        os.system('sudo systemctl disable BackGroundMusic.service > /dev/null 2>&1')
    background_music_check()

def rotate_frontend():
    show_info ("WAIT, PREPARING ROTATION...")
    if bRotateES == True:
        os.system('rm /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/configs/es-select-tate1 >> /dev/null 2>&1')
        os.system('rm /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/configs/es-select-tate3 >> /dev/null 2>&1')
        os.system('rm /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/configs/es-select-yoko >> /dev/null 2>&1')
        if opt[1][2] == 0:
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
            modify_line(ESCFG_FILE, '"ThemeSet"', '<string name="ThemeSet" value="%s" />'%HorTheme)
        if opt[1][2] == 90:
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
            modify_line(ESCFG_FILE, '"ThemeSet"', '<string name="ThemeSet" value="%s" />'%VerTheme)
        if opt[1][2] == -90:
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
            modify_line(ESCFG_FILE, '"ThemeSet"', '<string name="ThemeSet" value="%s" />'%VerTheme)

def quit_utility():
    pygame_unload()
    save_configuration()
    if bRotateES == True:
        rotate_frontend()
        # Restart ES if it is running
        output = commands.getoutput('ps -A')
        if 'emulationstatio' in output:
            commandline = "touch /tmp/es-restart "
            commandline += "&& pkill -f \"/opt/retropie"
            commandline += "/supplementary/.*/emulationstation([^.]|$)\""
            show_info ("EMULATIONSTATION WILL RESTART NOW")
            os.system(commandline)
    time.sleep(1)
    sys.exit(0)

def launch_application(sCommandline, bShell = False):
    pygame_unload()
    save_configuration()
    oRunProcess = subprocess.Popen(sCommandline, shell=bShell)
    iExitCode = oRunProcess.wait()
    if iExitCode:
        time.sleep(1)
        sys.exit()
    os.execl(sys.executable, sys.executable, *sys.argv)

def launch_screen_tool_manager():
    commandline = "/usr/bin/python \"%s\"" % SCREEN_MNG_FILE
    launch_application(commandline, True)

def get_config():
    global opt
    global CurTheme
    global HorTheme
    global VerTheme
    global SystemRes
    HorTheme240p = "none"
    HorTheme270p = "none"
    VerTheme240p = "none"
    VerTheme270p = "none"
    if not os.path.exists(CFG_VIDEOUTILITY_FILE):
        os.system('echo %s > %s'%(DEFAULT_CONFIG,CFG_VIDEOUTILITY_FILE))
    with open(CFG_VIDEOUTILITY_FILE, 'r') as file:
        for line in file:
            line = line.strip().replace('=',' ').split(' ')
            if line[0] == 'game_rotation':
                opt[0][2] = int(line[1])
            elif line[0] == 'handheld_bezel':
                opt[2][2] = int(line[1])
            elif line[0] == 'freq_selector':
                opt[3][2] = int(line[1])
            elif line[0] == 'integer_scale':
                opt[6][2] = int(line[1])
            elif line[0] == 'scummvm_arc':
                opt[7][2] = int(line[1])
            elif line[0] == '240p_theme_horizontal':
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

    if os.path.exists(ESCFG_FILE):
        with open(ESCFG_FILE, 'r') as file:
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
        opt[1][2] = 90
        opt[1][3] = 90
        opt[0][2] = 0
        modify_line(CFG_VIDEOUTILITY_FILE, '%s_theme_vertical '%SystemRes, '%s_theme_vertical %s'%(SystemRes, CurTheme))
    elif os.path.exists('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/configs/es-select-tate3'):
        opt[1][2] = -90
        opt[1][3] = -90
        opt[0][2] = 0
        modify_line(CFG_VIDEOUTILITY_FILE, '%s_theme_vertical '%SystemRes, '%s_theme_vertical %s'%(SystemRes, CurTheme))
    elif os.path.exists('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/configs/es-select-yoko'):
        opt[1][2] = 0
        opt[1][3] = 0
        modify_line(CFG_VIDEOUTILITY_FILE, '%s_theme_horizontal '%SystemRes, '%s_theme_horizontal %s'%(SystemRes, CurTheme))
    else:
        opt[1][2] = 0
        opt[1][3] = 0
        modify_line(CFG_VIDEOUTILITY_FILE, '%s_theme_horizontal '%SystemRes, '%s_theme_horizontal %s'%(SystemRes, CurTheme))
    background_music_check()

def draw_menu():
    global iCurOption
    global opt
    global bRotateES
    
    # draw background color and main frame
    PGoScreen.fill(BLUELIGHT) 
    pygame.draw.rect(PGoScreen, BLUEDARK,
                    (20,y_margin,x_screen-40,(20+(Interline*9)+3+16+10)), 0)

    # draw title and version
    title = PGoFont.render("Configuration Utility", 1, BLUELIGHT)
    PGoScreen.blit(title, (32, y_margin+8))
    text_print("v3.5", x_screen-62, y_margin+8, BLUEUNS, False)

    # draw options list frame
    pygame.draw.rect(PGoScreen, BLUELIGHT, (32, y_margin + 24,
                                              x_screen-62, Interline * 9), 1)

    # clear any previous warning top red message
    text_print('EMULATIONSTATION NEEDS TO RESTART', 0,
                y_margin-13, BLUELIGHT, True)

    # draw if apply warning message on top 
    bRotateES = False
    
    if opt[1][2] != opt[1][3]:
        bRotateES = True
        text_print('EMULATIONSTATION NEEDS TO RESTART', 0, y_margin-13, RED, True)
        if opt[1][2] != 0:
            opt[0][2] = 0

    # draw whole list of options in base color
    for i in range(0,9):
        if bRotateES == False:
            opt[8][0] = '<EXIT'
            opt[8][1] = 'Save and Exit'
            PGoScreen.blit((PGoFont.render(opt[i][0], 1, BLUELIGHT)), (list_x, (30+y_margin+LineMov)+i*Interline))
        elif bRotateES == True:
            opt[8][0] = '<RESTART'
            opt[8][1] = 'Restart FrontEnd for TATE Mode'
            if i == 1 or i == 8:
                PGoScreen.blit((PGoFont.render(opt[i][0], 1, BLUELIGHT)), (list_x, (30+y_margin+LineMov)+i*Interline))
            else:
                PGoScreen.blit((PGoFont.render(opt[i][0], 1, BLUEUNS)), (list_x, (30+y_margin+LineMov)+i*Interline))

    # draw all selectables values in base color    
    for i in range(0,9):
        if not bRotateES:
            if i == 0:
                if opt[0][2] == 0:
                    select = PGoFont.render("OFF", 1, BLUELIGHT)
                    PGoScreen.blit(select, (data_x-(len("OFF")*8), (30+y_margin+LineMov)+i*Interline))
                else:
                    select = PGoFont.render(str(opt[i][2]), 1, BLUELIGHT)
                    PGoScreen.blit(select, (data_x-(len(str(opt[i][2]))*8), (30+y_margin+LineMov)+i*Interline))
            elif i == 1:
                if opt[1][2] == 0:
                    select = PGoFont.render("OFF", 1, BLUELIGHT)
                    PGoScreen.blit(select, (data_x-(len("OFF")*8), (30+y_margin+LineMov)+i*Interline))
            elif i == 2:
                if opt[2][2] == 0:
                    select = PGoFont.render("OFF", 1, BLUELIGHT)
                    PGoScreen.blit(select, (data_x-(len("OFF")*8), (30+y_margin+LineMov)+i*Interline))
                elif opt[2][2] == 1:
                    select = PGoFont.render("YES", 1, BLUELIGHT)
                    PGoScreen.blit(select, (data_x-(len("YES")*8), (30+y_margin+LineMov)+i*Interline))
            elif i == 3:
                if opt[3][2] == 0:
                    select = PGoFont.render("MAN", 1, BLUELIGHT)
                    PGoScreen.blit(select, (data_x-(len("MAN")*8), (30+y_margin+LineMov)+i*Interline))
                elif opt[3][2] == 100:
                    select = PGoFont.render("AUT", 1, BLUELIGHT)
                    PGoScreen.blit(select, (data_x-(len("AUT")*8), (30+y_margin+LineMov)+i*Interline))
                else:
                    select = PGoFont.render(str(opt[3][2]), 1, BLUELIGHT)
                    PGoScreen.blit(select, (data_x-(len(str(opt[3][2]))*8), (30+y_margin+LineMov)+i*Interline))
            elif i == 5:
                if opt[5][2] == 0:
                    select = PGoFont.render("OFF", 1, BLUELIGHT)
                    PGoScreen.blit(select, (data_x-(len("OFF")*8), (30+y_margin+LineMov)+i*Interline))
                elif opt[5][2] == 1:
                    select = PGoFont.render("YES", 1, BLUELIGHT)
                    PGoScreen.blit(select, (data_x-(len("YES")*8), (30+y_margin+LineMov)+i*Interline))
            elif i == 6:
                if opt[6][2] == 0:
                    select = PGoFont.render("OFF", 1, BLUELIGHT)
                    PGoScreen.blit(select, (data_x-(len("OFF")*8), (30+y_margin+LineMov)+i*Interline))
                elif opt[6][2] == 1:
                    select = PGoFont.render("YES", 1, BLUELIGHT)
                    PGoScreen.blit(select, (data_x-(len("YES")*8), (30+y_margin+LineMov)+i*Interline))
            elif i == 7:
                if opt[7][2] == 0:
                    select = PGoFont.render("OFF", 1, BLUELIGHT)
                    PGoScreen.blit(select, (data_x-(len("OFF")*8), (30+y_margin+LineMov)+i*Interline))
                elif opt[7][2] == 1:
                    select = PGoFont.render("YES", 1, BLUELIGHT)
                    PGoScreen.blit(select, (data_x-(len("YES")*8), (30+y_margin+LineMov)+i*Interline))
                elif opt[7][2] == 2:
                    select = PGoFont.render("MAN", 1, BLUELIGHT)
                    PGoScreen.blit(select, (data_x-(len("MAN")*8), (30+y_margin+LineMov)+i*Interline))

        else:
            if i == 0:
                if opt[0][2] == 0:
                    select = PGoFont.render("OFF", 1, BLUEUNS)
                    PGoScreen.blit(select, (data_x-(len("OFF")*8), (30+y_margin+LineMov)+i*Interline))
            elif i == 1:
                strpor = PGoFont.render(str(opt[i][2]), 1, BLUELIGHT)
                PGoScreen.blit(strpor, (data_x-(len(str(opt[i][2]))*8), (30+y_margin+LineMov)+i*Interline))
            elif i == 2:
                if opt[2][2] == 0:
                    select = PGoFont.render("OFF", 1, BLUEUNS)
                    PGoScreen.blit(select, (data_x-(len("OFF")*8), (30+y_margin+LineMov)+i*Interline))
                elif opt[2][2] == 1:
                    select = PGoFont.render("YES", 1, BLUEUNS)
                    PGoScreen.blit(select, (data_x-(len("YES")*8), (30+y_margin+LineMov)+i*Interline))
            elif i == 3:
                if opt[3][2] == 0:
                    select = PGoFont.render("MAN", 1, BLUEUNS)
                    PGoScreen.blit(select, (data_x-(len("MAN")*8), (30+y_margin+LineMov)+i*Interline))
                elif opt[3][2] == 100:
                    select = PGoFont.render("AUT", 1, BLUEUNS)
                    PGoScreen.blit(select, (data_x-(len("AUT")*8), (30+y_margin+LineMov)+i*Interline))
                else:
                    select = PGoFont.render(str(opt[3][2]), 1, BLUEUNS)
                    PGoScreen.blit(select, (data_x-(len(str(opt[3][2]))*8), (30+y_margin+LineMov)+i*Interline))
            elif i == 5:
                if opt[5][2] == 0:
                    select = PGoFont.render("OFF", 1, BLUEUNS)
                    PGoScreen.blit(select, (data_x-(len("OFF")*8), (30+y_margin+LineMov)+i*Interline))
                elif opt[5][2] == 1:
                    select = PGoFont.render("YES", 1, BLUEUNS)
                    PGoScreen.blit(select, (data_x-(len("YES")*8), (30+y_margin+LineMov)+i*Interline))
            elif i == 6:
                if opt[6][2] == 0:
                    select = PGoFont.render("OFF", 1, BLUEUNS)
                    PGoScreen.blit(select, (data_x-(len("OFF")*8), (30+y_margin+LineMov)+i*Interline))
                elif opt[6][2] == 1:
                    select = PGoFont.render("YES", 1, BLUEUNS)
                    PGoScreen.blit(select, (data_x-(len("YES")*8), (30+y_margin+LineMov)+i*Interline))
            elif i == 7:
                if opt[7][2] == 0:
                    select = PGoFont.render("OFF", 1, BLUEUNS)
                    PGoScreen.blit(select, (data_x-(len("OFF")*8), (30+y_margin+LineMov)+i*Interline))
                elif opt[7][2] == 1:
                    select = PGoFont.render("YES", 1, BLUEUNS)
                    PGoScreen.blit(select, (data_x-(len("YES")*8), (30+y_margin+LineMov)+i*Interline))
                elif opt[7][2] == 2:
                    select = PGoFont.render("MAN", 1, BLUEUNS)
                    PGoScreen.blit(select, (data_x-(len("MAN")*8), (30+y_margin+LineMov)+i*Interline))

    # draw current selection frame color
    pygame.draw.rect(PGoScreen, BLUELIGHT,
                    (32,(24 + y_margin) + iCurOption * Interline, x_screen \
                    - 62, Interline))
    PGoScreen.blit((PGoFont.render(opt[iCurOption][0], 1, BLUEDARK)),
                    (list_x, (30 + y_margin + LineMov) + iCurOption * Interline))

    # draw active option in dark color
    if iCurOption in (0, 1, 2, 3, 5, 6, 7):
        if opt[0][2] == 0 and iCurOption == 0:
            listrndr = PGoFont.render("OFF", 1, BLUEDARK)
            PGoScreen.blit(listrndr, (data_x-(len("OFF")*8), (30+y_margin+LineMov)+ iCurOption *Interline))
        elif opt[1][2] == 0 and iCurOption == 1:
            listrndr = PGoFont.render("OFF", 1, BLUEDARK)
            PGoScreen.blit(listrndr, (data_x-(len("OFF")*8), (30+y_margin+LineMov)+ iCurOption *Interline))
        elif opt[2][2] == 0 and iCurOption == 2:
            listrndr = PGoFont.render("OFF", 1, BLUEDARK)
            PGoScreen.blit(listrndr, (data_x-(len("OFF")*8), (30+y_margin+LineMov)+ iCurOption *Interline))
        elif opt[2][2] == 1 and iCurOption == 2:
            listrndr = PGoFont.render("YES", 1, BLUEDARK)
            PGoScreen.blit(listrndr, (data_x-(len("YES")*8), (30+y_margin+LineMov)+ iCurOption *Interline))
        elif opt[3][2] == 0 and iCurOption == 3:
            listrndr = PGoFont.render("MAN", 1, BLUEDARK)
            PGoScreen.blit(listrndr, (data_x-(len("MAN")*8), (30+y_margin+LineMov)+ iCurOption *Interline))
        elif opt[3][2] == 100 and iCurOption == 3:
            listrndr = PGoFont.render("AUT", 1, BLUEDARK)
            PGoScreen.blit(listrndr, (data_x-(len("AUT")*8), (30+y_margin+LineMov)+ iCurOption *Interline))
        elif opt[5][2] == 0 and iCurOption == 5:
            listrndr = PGoFont.render("OFF", 1, BLUEDARK)
            PGoScreen.blit(listrndr, (data_x-(len("OFF")*8), (30+y_margin+LineMov)+ iCurOption *Interline))
        elif opt[5][2] == 1 and iCurOption == 5:
            listrndr = PGoFont.render("YES", 1, BLUEDARK)
            PGoScreen.blit(listrndr, (data_x-(len("YES")*8), (30+y_margin+LineMov)+ iCurOption *Interline))
        elif opt[6][2] == 0 and iCurOption == 6:
            listrndr = PGoFont.render("OFF", 1, BLUEDARK)
            PGoScreen.blit(listrndr, (data_x-(len("OFF")*8), (30+y_margin+LineMov)+ iCurOption *Interline))
        elif opt[6][2] == 1 and iCurOption == 6:
            listrndr = PGoFont.render("YES", 1, BLUEDARK)
            PGoScreen.blit(listrndr, (data_x-(len("YES")*8), (30+y_margin+LineMov)+ iCurOption *Interline))
        elif opt[7][2] == 0 and iCurOption == 7:
            listrndr = PGoFont.render("OFF", 1, BLUEDARK)
            PGoScreen.blit(listrndr, (data_x-(len("OFF")*8), (30+y_margin+LineMov)+ iCurOption *Interline))
        elif opt[7][2] == 1 and iCurOption == 7:
            listrndr = PGoFont.render("YES", 1, BLUEDARK)
            PGoScreen.blit(listrndr, (data_x-(len("YES")*8), (30+y_margin+LineMov)+ iCurOption *Interline))
        elif opt[7][2] == 2 and iCurOption == 7:
            listrndr = PGoFont.render("MAN", 1, BLUEDARK)
            PGoScreen.blit(listrndr, (data_x-(len("MAN")*8), (30+y_margin+LineMov)+ iCurOption *Interline))
        else:
            listrndr = PGoFont.render(str(opt[iCurOption][2]), 1, BLUEDARK)
            PGoScreen.blit(listrndr, (data_x-(len(str(opt[iCurOption][2]))*8), (30+y_margin+LineMov)+ iCurOption *Interline))

    # draw arrows per option
    # arrows for option 1
    if iCurOption == 0 and opt[0][2] < 0:
        draw_arrow_right()
    elif iCurOption == 0 and opt[0][2] == 0 and opt[1][2] == 0:
        draw_arrow_left(2)

    # arrows for option 2
    if iCurOption == 1 and opt[1][2] < 0:
        draw_arrow_right()
    elif iCurOption == 1 and opt[1][2] == 0:
        draw_arrow_right()
        draw_arrow_left(2)
    elif iCurOption == 1 and opt[1][2] > 0:
        draw_arrow_left()

    # arrows for option 3
    if iCurOption == 2:
        if opt[2][2] == 1:
            draw_arrow_left(2)
        else:
            draw_arrow_right()

    # arrows for option 4
    if iCurOption == 3:
        if opt[3][2] == 0:
            draw_arrow_right()
        if opt[3][2] == 50:
            draw_arrow_right()
            draw_arrow_left()
        if opt[3][2] == 60:
            draw_arrow_right()
            draw_arrow_left()
        if opt[3][2] == 100:
            draw_arrow_left()

    # arrows for option 6
    if iCurOption == 5:
        if opt[5][2] == 1:
            draw_arrow_left(2)
        elif opt[5][2] == 0:
            draw_arrow_right()

    # arrows for option 7
    if iCurOption == 6:
        if opt[6][2] == 1:
            draw_arrow_left(2)
        elif opt[6][2] == 0:
            draw_arrow_right()

    # arrows for option 8
    if iCurOption == 7:
        if opt[7][2] == 0:
            draw_arrow_right()
        if opt[7][2] == 1:
            draw_arrow_right()
            draw_arrow_left(2)
        if opt[7][2] == 2:
            draw_arrow_right()
            draw_arrow_left(2)

    
    if iCurOption == 7 and opt[1][2] != opt[1][3]:
        PGoScreen.blit((PGoFont.render(opt[iCurOption][0], 1, (136, 136, 255))), (110, (30+y_margin+LineMov)+ iCurOption *Interline))

    # draw info message on bottom
    info = str(opt[iCurOption][1])
    if x_screen <= 340:
        info = info[0:28]
        if len(info) >= 28 :
            info = info + '...'
    else:
        info = info[0:44]
        if len(info) >= 44 :
            info = info + '...'
    PGoScreen.blit((PGoFont.render(info, 1, (YELLOW))),
                    (38, ((y_margin + 23) + Interline * 9) + 4))
    pygame.draw.rect(PGoScreen, BLUELIGHT, 
                    (32,(y_margin + 23) + Interline * 9,x_screen - 62, 16), 1)
    pygame.display.flip()

# MAIN PROGRAM
script_initialization()

while True:
    draw_menu()
    event = PGoJoyHandler.event_wait()
    #button
    if event & CRT_BUTTON:
        if iCurOption == 4:
            launch_screen_tool_manager()
        elif iCurOption < 3:
            opt[iCurOption][2] = 0
        elif iCurOption == 8:
            quit_utility()
    #right
    elif event & CRT_RIGHT:
        if iCurOption == 0 and opt[0][2] < 0 and opt[1][2] == 0:
            opt[0][2] += 90
        elif iCurOption == 1 and opt[1][2] < 90:
            opt[1][2] += 90
            opt[0][2] = 0
        elif iCurOption == 2 and opt[2][2] == 0:
            opt[2][2] = 1
        elif iCurOption == 3 and opt[3][2] == 0:
            opt[3][2] = 50
        elif iCurOption == 3 and opt[3][2] == 50:
            opt[3][2] = 60
        elif iCurOption == 3 and opt[3][2] == 60:
            opt[3][2] = 100
        elif iCurOption == 5 and opt[5][2] == 0:
            background_music_install()
        elif iCurOption == 6 and opt[6][2] == 0:
            opt[6][2] = 1
        elif iCurOption == 7 and opt[7][2] < 2:
            opt[7][2] += 1
    #left
    elif event & CRT_LEFT:
        if iCurOption == 0 and opt[0][2] > -90 and opt[1][2] == 0:
            opt[0][2] -= 90
        elif iCurOption == 1 and opt[1][2] > -90:
            opt[1][2] -= 90
            opt[0][2] = 0
        elif iCurOption == 2 and opt[2][2] == 1:
            opt[2][2] = 0
        elif iCurOption == 3 and opt[3][2] == 100:
            opt[3][2] = 60
        elif iCurOption == 3 and opt[3][2] == 60:
            opt[3][2] = 50
        elif iCurOption == 3 and opt[3][2] == 50:
            opt[3][2] = 0
        elif iCurOption == 5 and opt[5][2] == 1:
            background_music_remove()
        elif iCurOption == 6 and opt[6][2] == 1:
            opt[6][2] = 0
        elif iCurOption == 7 and opt[7][2] > 0:
            opt[7][2] -= 1
    #up            
    elif event & CRT_UP:
        if bRotateES == True:
            if iCurOption == 8:
                iCurOption = 1
        else:
            if iCurOption == 0:
                iCurOption = 8
            elif iCurOption > 0:
                iCurOption = iCurOption - 1
    #down
    elif event & CRT_DOWN:
        if bRotateES == True:
            if iCurOption == 1:
                iCurOption = 8
        else:
            if iCurOption == 8:
                iCurOption = 0
            elif iCurOption < 8:
                iCurOption = iCurOption + 1
