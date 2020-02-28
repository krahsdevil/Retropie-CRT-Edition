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
from launcher_module.es_rotation import frontend_rotation
from launcher_module.core_choices_dynamic import choices
from launcher_module.file_helpers import modify_line, ini_get
from launcher_module.utils import get_xy_screen, something_is_bad
from launcher_module.core_controls import joystick, CRT_UP, CRT_DOWN, CRT_LEFT, \
                                          CRT_RIGHT, CRT_BUTTON

FONT_FILE = os.path.join(CRTFONTS_PATH, "PetMe64.ttf")
SCREEN_MNG_PATH = os.path.join(CRTMODULES_PATH, "module_screen_tools_manager")
SCREEN_MNG_FILE = os.path.join(SCREEN_MNG_PATH, "screen_tools_manager.py")

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

iCurSide = ""
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
      ["6.BACKGROUND MUSIC" , "Play your music with emulationstation", 0],
      ["7.INTEGER SCALE" , "ONLY for LibRetro Arcade and NEOGEO Games", 0],
      ["8.SCUMMVM ARC" , "Aspect Ratio Correction: Stretch but NO PixelPerfect", 0],
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
    PGoFont = pygame.font.Font(FONT_FILE, 8)
    PGoScreen = pygame.display.set_mode((x_screen,y_screen), pygame.FULLSCREEN)
    
def pygame_unload():
    pygame.display.quit()
    pygame.quit()

def script_initialization():
    os.system('clear')
    check_es_launcher()        # fix ES script launcher if needed
    get_screen_size_adjust()
    pygame_initialization()
    background_music_check()
    get_config()

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
        something_is_bad(infos, infos2)
        os.system('sudo reboot')
   
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

def draw_arrow_left(p_sLabel = 0):
    PGoScreen.blit((PGoFont.render('<<', 1, YELLOW)), (data_x - (len(p_sLabel) * 8) - 18,
                   (30 + y_margin + LineMov) + iCurOption * Interline))

def draw_arrow_right():
    PGoScreen.blit((PGoFont.render('>>', 1, (YELLOW))), (data_x + 2, 
                   (30 + y_margin+LineMov) + iCurOption * Interline))

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

def quit_utility():
    pygame_unload()
    save_configuration()
    if bRotateES == True:
        frontend_rotation(opt[1][2], True)
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
    global iCurSide

    # create configuration file if not exists
    if not os.path.exists(CFG_VIDEOUTILITY_FILE):
        os.system('echo %s > %s' % (DEFAULT_CONFIG, CFG_VIDEOUTILITY_FILE))

    # get configuration values
    opt[0][2] = int(ini_get(CFG_VIDEOUTILITY_FILE, "game_rotation"))
    opt[2][2] = int(ini_get(CFG_VIDEOUTILITY_FILE, "handheld_bezel"))
    opt[3][2] = int(ini_get(CFG_VIDEOUTILITY_FILE, "freq_selector"))
    opt[6][2] = int(ini_get(CFG_VIDEOUTILITY_FILE, "integer_scale"))
    opt[7][2] = int(ini_get(CFG_VIDEOUTILITY_FILE, "scummvm_arc"))

    # get current emulationstation side
    if os.path.exists(ROTMODES_TATE1_FILE):
        opt[1][2] = 90
        opt[1][3] = 90
        opt[0][2] = 0
    elif os.path.exists(ROTMODES_TATE3_FILE):
        opt[1][2] = -90
        opt[1][3] = -90
        opt[0][2] = 0
    else:
        opt[1][2] = 0
        opt[1][3] = 0

def check_rotation_mode(p_iOption = None):
    global bRotateES
    global opt
    bRotateES = False
    p_lDisOpt = []
    
    if opt[1][2] != opt[1][3]:
        bRotateES = True
        p_lDisOpt = [0, 2, 3, 4, 5, 6, 7, 9]

    if p_iOption != None:
        if p_iOption in p_lDisOpt and bRotateES:
            return False
        return True

    if bRotateES:
        opt[8][0] = '<RESTART'
        opt[8][1] = 'Restart FrontEnd for TATE Mode'
        text_print('EMULATIONSTATION NEEDS TO RESTART', 0, y_margin-13, RED, True)
        if opt[1][2] != 0:
            opt[0][2] = 0
    else:
        opt[8][0] = '<EXIT'
        opt[8][1] = 'Save and Exit'

def get_menu_options_value_label(p_sOption):
    p_sLabel = None
    p_bLArrow = False
    p_bRArrow = False

    try:
        p_iCurValue = int(opt[p_sOption][2])
    except:
        return None, None, None

    if p_sOption == 0:
        if p_iCurValue == 0:
            p_sLabel = "OFF"
            p_bLArrow = True
        else:
            p_sLabel = str(p_iCurValue)
            p_bRArrow = True
    elif p_sOption == 1:
        if p_iCurValue == 0:
            p_sLabel = "OFF"
            p_bRArrow = True
            p_bLArrow = True
        else:
            p_sLabel = str(p_iCurValue)
            if p_iCurValue > 0:
                p_bLArrow = True
            elif p_iCurValue < 0:
                p_bRArrow = True
    elif p_sOption == 2:
        if p_iCurValue == 0:
            p_sLabel = "OFF"
            p_bRArrow = True
        elif p_iCurValue == 1:
            p_sLabel = "YES"
            p_bLArrow = True
    elif p_sOption == 3:
        if p_iCurValue == 0:
            p_sLabel = "MAN"
            p_bRArrow = True
        elif p_iCurValue == 100:
            p_sLabel = "AUT"
            p_bLArrow = True
        else:
            p_sLabel = str(p_iCurValue)
            p_bRArrow = True
            p_bLArrow = True
    elif p_sOption == 4:
        pass
    elif p_sOption == 5:
        if p_iCurValue == 0:
            p_sLabel = "OFF"
            p_bRArrow = True
        elif p_iCurValue == 1:
            p_sLabel = "YES"
            p_bLArrow = True
    elif p_sOption == 6:
        if p_iCurValue == 0:
            p_sLabel = "OFF"
            p_bRArrow = True
        elif p_iCurValue == 1:
            p_sLabel = "YES"
            p_bLArrow = True
    elif p_sOption == 7:
        if p_iCurValue == 0:
            p_sLabel = "OFF"
            p_bRArrow = True
        elif p_iCurValue == 1:
            p_sLabel = "YES"
            p_bRArrow = True
            p_bLArrow = True
        elif p_iCurValue == 2:
            p_sLabel = "MAN"
            p_bLArrow = True
    
    return p_sLabel, p_bLArrow, p_bRArrow

def draw_menu_options_value(p_oColor, p_iOption):
    p_sLabel, p_bLArrow, p_bRArrow = get_menu_options_value_label(p_iOption)
    
    if p_sLabel:
        sLabelLen = int(len(p_sLabel))
        listrndr = PGoFont.render(p_sLabel, 1, p_oColor)
        PGoScreen.blit(listrndr, ((data_x - (sLabelLen) * 8),
                      (30 + y_margin + LineMov) + p_iOption * Interline))
        if p_iOption == iCurOption:
            if p_bRArrow:
                draw_arrow_right()
            if p_bLArrow:
                draw_arrow_left(p_sLabel)

def draw_menu_options_description(p_oColor, p_iOption):
    try:
        p_sLabel = str(opt[p_iOption][0])
    except:
        return

    if p_sLabel:
        PGoScreen.blit((PGoFont.render(p_sLabel, 1, p_oColor)),
                       (list_x, (30 + y_margin+LineMov) + p_iOption * Interline))

def draw_menu_options_info(p_iOption, p_oColor = YELLOW):
    try:
        p_sLabel = str(opt[p_iOption][1])
    except:
        return

    if x_screen <= 340:
        p_sLabel = p_sLabel[0:28]
        if len(p_sLabel) >= 28 :
            p_sLabel += '...'
    else:
        p_sLabel = p_sLabel[0:44]
        if len(p_sLabel) >= 44 :
            p_sLabel += '...'

    if p_sLabel:
        PGoScreen.blit((PGoFont.render(p_sLabel, 1, p_oColor)),
                        (38, ((y_margin + 23) + Interline * 9) + 4))
                    
def draw_menu_options_selection_bar():
    # draw current selection frame color
    pygame.draw.rect(PGoScreen, BLUELIGHT,
                    (32,(24 + y_margin) + iCurOption * Interline, x_screen \
                    - 62, Interline))
    PGoScreen.blit((PGoFont.render(opt[iCurOption][0], 1, BLUEDARK)),
                    (list_x, (30 + y_margin + LineMov) + iCurOption * Interline))

def draw_menu_options():
    p_iOption = 0
    p_oColor = None
    p_iCount = 0
    for p_iOption in opt:
        p_oColor = BLUELIGHT
        if p_iCount == iCurOption:
            draw_menu_options_selection_bar()
            draw_menu_options_info(p_iCount)
            p_oColor = BLUEDARK
        else:
            if not check_rotation_mode(p_iCount):
                p_oColor = BLUEUNS
        draw_menu_options_value(p_oColor, p_iCount)
        draw_menu_options_description(p_oColor, p_iCount)
        p_iCount += 1

def draw_menu_base_framework():
    # draw background color and main frame
    PGoScreen.fill(BLUELIGHT) 
    pygame.draw.rect(PGoScreen, BLUEDARK,
                    (20,y_margin,x_screen-40,(20+(Interline*9)+3+16+10)), 0)
    # draw options list frame
    pygame.draw.rect(PGoScreen, BLUELIGHT, 
                    (32, y_margin + 24, x_screen-62, Interline * 9), 1)
    # draw info list frame
    pygame.draw.rect(PGoScreen, BLUELIGHT, 
                    (32,(y_margin + 23) + Interline * 9,x_screen - 62, 16), 1)

def draw_menu_title():
    # draw title and version
    sTitle = PGoFont.render("Configuration Utility", 1, BLUELIGHT)
    PGoScreen.blit(sTitle, (32, y_margin+8))
    text_print("v3.5", x_screen-62, y_margin+8, BLUEUNS, False)


def draw_menu():
    check_rotation_mode()    
    draw_menu_base_framework()
    draw_menu_title()
    draw_menu_options()
    pygame.display.flip()

# MAIN PROGRAM
script_initialization()

while True:
    draw_menu()
    event = PGoJoyHandler.event_wait()
    #button
    if event & CRT_BUTTON:
        if iCurOption < 4:
            opt[iCurOption][2] = 0
        elif iCurOption == 4:
            launch_screen_tool_manager()
        elif iCurOption == 5:
            background_music_remove()
        elif iCurOption < 8:
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
