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
import filecmp, time, threading

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(SCRIPT_DIR + "/../"))
from main_paths import MODULES_PATH
sys.path.append(MODULES_PATH)

from launcher_module.core_paths import *
from es_rotation import frontend_rotation
from launcher_module.file_helpers import modify_line, ini_get
from launcher_module.utils import get_screen_resolution, something_is_bad
from launcher_module.core_controls import joystick, CRT_UP, CRT_DOWN, \
                                          CRT_LEFT, CRT_RIGHT, CRT_BUTTON

FONT_FILE = os.path.join(CRT_FONTS_PATH, "PetMe64.ttf")
CURSOR_SOUND_FILE = os.path.join(CRT_SOUNDS_PATH, "sys_cursor_01.ogg")
CLICK_SOUND_FILE = os.path.join(CRT_SOUNDS_PATH, "sys_click_01.ogg")


SCREEN_MNG_PATH = os.path.join(CRT_MODULES_PATH, "module_screen_tools_manager")
SCREEN_MNG_FILE = os.path.join(SCREEN_MNG_PATH, "screen_tools_manager.py")

ES_LAUNCHER_DST_FILE = os.path.join(RETROPIE_PATH,
                       "supplementary/emulationstation/emulationstation.sh")
ES_LAUNCHER_SRC_FILE = os.path.join(CRT_ES_RES_PATH,
                       "configs/default_emulationstation.sh")
ES_LAUNCHER_BCK_FILE = os.path.join(RETROPIE_PATH,
                       "supplementary/emulationstation/backup.emulationstation.sh")

BGM_PATH = os.path.join(CRT_BIN_PATH, "BGMService")
BGM_SERVICE_NAME = "BackGroundMusic.service"
BGM_SERVICE_CORE_NAME = "BGM.py"
BGM_SERVICE_FILE_SRC = os.path.join(BGM_PATH, BGM_SERVICE_NAME)
BGM_SERVICE_FILE_DST = os.path.join(RASP_SERVICES_PATH, BGM_SERVICE_NAME)
BGM_SERVICE_CORE_FILE = os.path.join(BGM_PATH, BGM_SERVICE_CORE_NAME)
BGM_INFO_TXT = os.path.join(RETROPIE_MUSIC_PATH,
                            "place your background music here.txt")

# screen resolution
iRES_X = 0
iRES_Y = 0

# menu positions
iMARGIN_TOP = 0
iMARGIN_RIGHT = 0
iMARGIN_LEFT = 0
iCurOption = 0
iIntLine = 0
iLineAdj = 0

# background music checking
bBGMServWch = True
bBGMServRun = False
bBGMServIns = False

bRotateES = False

# pygame configurations
PGoJoyHandler = None
PGoScreen = None
PGoFont = None
PGoSndCursor = None
PGoSndClick = None
PGbScroll = False
PGoScroll = None
BLUELIGHT = pygame.Color(165, 165, 255)
BLUEDARK = pygame.Color(66, 66, 231)
BLUEUNS = pygame.Color(110, 110, 255)
YELLOW = pygame.Color(255, 255, 0)
RED = pygame.Color(255, 0, 0)

# loading data from su.cfg
opt = [["1.GAMES ROTATION" , 
        "Rotate ONLY vertical games to play them in horizontal mode. " + \
        "NOT PixelPerfect but playable." , 0],
      ["2.FRONTEND ROTATION" ,
       "Rotate frontend EmulationStation. This option requires rotate " + \
       "your monitor." , 0, 0],
      ["3.HANDHELD BEZELS" , 
       "CAUTION!!! Long use can damage the screen." , 0],
      ["4.FREQUENCY SELECTOR" , 
       "Set frequency at 50/60hz, Auto or Manual." , 0],
      ["5.VIDEO CONFIG>" , 
       "Access to Advanced Video Configuration."],
      ["6.BACKGROUND MUSIC" , 
       "Play your music with EmulationStation.", 0],
      ["7.INTEGER SCALE" , 
       "ONLY applies to LibRetro Arcade and NEOGEO Games.", 0],
      ["8.SCUMMVM ARC" , 
       "Aspect Ratio Correction: vertical stretch but NOT PixelPerfect.", 0],
      ["<EXIT" , 
       "Save and Exit"]]

DEFAULT_CONFIG = "\"default system60\n"
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
DEFAULT_CONFIG += "240p_theme_vertical V240P-CRT-Uniflyered\n"
DEFAULT_CONFIG += "270p_theme_vertical V270P-CRT-BASE\n"
DEFAULT_CONFIG += "240p_theme_horizontal 240P-CRT-UniFlyered\n"
DEFAULT_CONFIG += "270p_theme_horizontal 270P-CRT-SNES-MINI\n\""

def get_screen_size_adjust():
    global iMARGIN_TOP
    global iIntLine
    global iLineAdj
    global iMARGIN_RIGHT
    global iMARGIN_LEFT
    global iRES_X
    global iRES_Y

    # Get current x,y resolution
    iRES_X, iRES_Y = get_screen_resolution()

    if iRES_Y > 270:
        Multiplier = int((iRES_Y-270)/8)
        iIntLine = 20-Multiplier
        iLineAdj = int(Multiplier/2)
        iMARGIN_TOP = 20-((iRES_Y-270)-(Multiplier*9))
    elif iRES_Y < 270:
        Multiplier = int((270-iRES_Y)/8)
        iIntLine = 20-Multiplier
        iLineAdj = int(-1*(Multiplier/2))
        iMARGIN_TOP = 20-((270-iRES_Y)-(Multiplier*9))

    elif iRES_Y == 270:
        iMARGIN_TOP = 20
        iIntLine = 20

    if iRES_X < 340:
        iMARGIN_RIGHT = 269
        iMARGIN_LEFT = 50
    else:
        iMARGIN_RIGHT = 340
        iMARGIN_LEFT = 100

def pygame_initialization():
    global PGoScreen
    global PGoFont
    global PGoJoyHandler
    global PGoSndCursor
    global PGoSndClick
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.init()
    pygame.mouse.set_visible(0)
    PGoJoyHandler = joystick()
    PGoFont = pygame.font.Font(FONT_FILE, 8)
    PGoScreen = pygame.display.set_mode((iRES_X, iRES_Y), pygame.FULLSCREEN)
    PGoSndCursor = pygame.mixer.Sound(CURSOR_SOUND_FILE)
    PGoSndClick = pygame.mixer.Sound(CLICK_SOUND_FILE)

def clean():
    global bBGMServWch
    global PGbScroll
    bBGMServWch = False
    PGbScroll = False
    PGoJoyHandler.quit()
    while pygame.mixer.get_busy():
        pass
    pygame.quit()

def script_initialization():
    os.system('clear')
    check_es_launcher()        # fix ES script launcher if needed
    get_screen_size_adjust()
    pygame_initialization()
    music_service_watcher()
    get_config()

def check_es_launcher():
    p_bFixed = False
    if not os.path.exists(ES_LAUNCHER_DST_FILE):
        os.system('sudo cp %s %s >> /dev/null 2>&1' % \
                 (ES_LAUNCHER_SRC_FILE, ES_LAUNCHER_DST_FILE))
        p_bFixed = True
    else:
        if not filecmp.cmp(ES_LAUNCHER_SRC_FILE, ES_LAUNCHER_DST_FILE):
            os.system('sudo cp %s %s >> /dev/null 2>&1' % \
                     (ES_LAUNCHER_DST_FILE, ES_LAUNCHER_BCK_FILE))
            os.system('sudo cp %s %s >> /dev/null 2>&1' % \
                     (ES_LAUNCHER_SRC_FILE, ES_LAUNCHER_DST_FILE))
            p_bFixed = True
    if p_bFixed:
        os.system('sudo chmod +x %s >> /dev/null 2>&1' % \
                  ES_LAUNCHER_DST_FILE)
        infos = "System needs to reboot, please wait..."
        infos2 = ""
        something_is_bad(infos, infos2)
        os.system('sudo reboot')

def text_print(txt, xcoord, ycoord, color, center):
    if iRES_X <= 340:
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
        textPos.center = (iRES_X/2, ycoord+6)
        PGoScreen.blit(text,textPos)
    else:
        PGoScreen.blit(PGoFont.render(txt, 1, color), (xcoord, ycoord))

def draw_arrow_left(p_sLabel = 0):
    PGoScreen.blit((PGoFont.render('<<', 1, YELLOW)),
                   (iMARGIN_RIGHT - (len(p_sLabel) * 8) - 18,
                   (30 + iMARGIN_TOP + iLineAdj) + iCurOption * iIntLine))

def draw_arrow_right():
    PGoScreen.blit((PGoFont.render('>>', 1, (YELLOW))), (iMARGIN_RIGHT + 2,
                   (30 + iMARGIN_TOP+iLineAdj) + iCurOption * iIntLine))

def save_configuration():
    modify_line(CRT_UTILITY_FILE,'game_rotation',
                'game_rotation %s' % opt[0][2])
    modify_line(CRT_UTILITY_FILE,'frontend_rotation',
                'frontend_rotation %s' % opt[1][2])
    modify_line(CRT_UTILITY_FILE,'handheld_bezel',
                'handheld_bezel %s' % opt[2][2])
    modify_line(CRT_UTILITY_FILE,'freq_selector',
                'freq_selector %s' % opt[3][2])
    modify_line(CRT_UTILITY_FILE,'integer_scale',
                'integer_scale %s' % opt[6][2])
    modify_line(CRT_UTILITY_FILE,'scummvm_arc',
                'scummvm_arc %s' % opt[7][2])

def background_music_check():
    global opt
    global bBGMServRun
    global bBGMServIns
    if not os.path.exists(RETROPIE_MUSIC_PATH):
        os.makedirs(RETROPIE_MUSIC_PATH)
        os.system('touch "%s"' % BGM_INFO_TXT)
    while bBGMServWch:
        commandline = "systemctl list-units --all "
        commandline += "| grep \"%s\"" % (BGM_SERVICE_NAME)
        CheckService = commands.getoutput(commandline)
        p_bChange = False
        bBGMServIns = False
        bBGMServRun = False
        if BGM_SERVICE_NAME in CheckService:
            bBGMServIns = True
        if 'running' in CheckService:
            bBGMServRun = True
            if opt[5][2] != 1:
                opt[5][2] = 1
                p_bChange = True
        else:
            if opt[5][2] != 0:
                opt[5][2] = 0
                p_bChange = True
        if p_bChange:
            draw_menu()
        time.sleep(1)

def music_service_watcher():
    global bBGMServWch
    bBGMServWch = True
    oDaemon = threading.Thread(target=background_music_check)
    oDaemon.setDaemon(True)
    oDaemon.start()

def background_music_install():
    global bBGMServRun
    global bBGMServIns
    if not os.path.exists(BGM_SERVICE_FILE_SRC) or \
       not os.path.exists(BGM_SERVICE_CORE_FILE):
        return False
    if not bBGMServIns:
        os.system('sudo cp "%s" "%s" > /dev/null 2>&1' % \
                 (BGM_SERVICE_FILE_SRC, BGM_SERVICE_FILE_DST))
        os.system('sudo systemctl enable %s > /dev/null 2>&1' % \
                  BGM_SERVICE_NAME)
    os.system('sudo systemctl start %s > /dev/null 2>&1' % \
                  BGM_SERVICE_NAME)

def background_music_remove():
    if bBGMServIns:
        os.system('sudo systemctl stop %s > /dev/null 2>&1' % \
                  BGM_SERVICE_NAME)
        os.system('sudo systemctl disable %s > /dev/null 2>&1' % \
                  BGM_SERVICE_NAME)
        os.system('sudo rm %s > /dev/null 2>&1' % \
                  BGM_SERVICE_FILE_DST)

def quit_utility():
    clean()
    save_configuration()
    if bRotateES == True:
        frontend_rotation(opt[1][2], True)
    sys.exit(0)

def launch_application(sCommandline, bShell = False):
    clean()
    save_configuration()
    oRunProcess = subprocess.Popen(sCommandline, shell=bShell)
    iExitCode = oRunProcess.wait()
    if iExitCode:
        time.sleep(2)
        sys.exit()
    os.execl(sys.executable, sys.executable, *sys.argv)

def launch_screen_tool_manager():
    commandline = "/usr/bin/python \"%s\"" % SCREEN_MNG_FILE
    launch_application(commandline, True)

def get_config():
    global opt
    # create configuration file if not exists
    if not os.path.exists(CRT_UTILITY_FILE):
        os.system('echo %s > %s' % \
                 (DEFAULT_CONFIG, CRT_UTILITY_FILE))

    # get configuration values
    opt[0][2] = int(ini_get(CRT_UTILITY_FILE, "game_rotation"))
    opt[2][2] = int(ini_get(CRT_UTILITY_FILE, "handheld_bezel"))
    opt[3][2] = int(ini_get(CRT_UTILITY_FILE, "freq_selector"))
    opt[6][2] = int(ini_get(CRT_UTILITY_FILE, "integer_scale"))
    opt[7][2] = int(ini_get(CRT_UTILITY_FILE, "scummvm_arc"))

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

    if bRotateES:
        opt[8][0] = "[RESTART]"
        opt[8][1] = "Restart EmulationStation to switch to " + \
                    "vertical mode (TATE)."
        text_print("EMULATIONSTATION NEEDS TO RESTART",
                    0, iMARGIN_TOP-13, RED, True)
        if opt[1][2] != 0:
            opt[0][2] = 0
    else:
        opt[8][0] = '<EXIT'
        opt[8][1] = 'Save and Exit'

    if p_iOption != None:
        if p_iOption in p_lDisOpt and bRotateES:
            return False
        return True

def get_menu_options_value_label(p_sOption):
    p_sLabel = None
    p_bLArrow = False
    p_bRArrow = False

    try:
        p_iCurValue = opt[p_sOption][2]
        p_sLabel = str(p_iCurValue)
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
        PGoScreen.blit(listrndr, ((iMARGIN_RIGHT - (sLabelLen) * 8),
                      (30 + iMARGIN_TOP + iLineAdj) + p_iOption * iIntLine))
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
                       (iMARGIN_LEFT, (30 + iMARGIN_TOP+iLineAdj) + p_iOption * iIntLine))

def draw_menu_options_info(p_iOption, p_oColor = YELLOW):
    """ 
    for drawing bottom information, create scroll daemon
    if text don't fit on visible area.    
    """
    global PGbScroll
    global PGoScroll
    PGbScroll = False
    if PGoScroll:
        PGoScroll.join()
        PGoScroll = None
    
    PGbScroll = True
    PGoScroll = threading.Thread(target=draw_info_scroll, args=[p_iOption, p_oColor])
    PGoScroll.setDaemon(True)
    PGoScroll.start()

def draw_info_scroll(p_iOption, p_oColor):
    """ main text scroll loop """
    Y_POS = (iMARGIN_TOP + 27) + (iIntLine * 9)
    X_POS = 38
    X_MAX = 31 if iRES_X <= 340 else 47

    text = str(opt[p_iOption][1])
    ScrollText = text
    ScrollChar = -1
    ScrollEnd = False
    ScrollWait = 0.4
    ScrollWaitFrm = 0.2
    ScrollWaitInit = 2.0
    ScrollWaitEnd = 1.0     
    ScrollTimes = 1         # number of times of text scroll

    if not wait_info_scroll(ScrollWait): return True
    while PGbScroll:
        ScrollWait = ScrollWaitFrm
        # text movement and wait timers
        if (ScrollChar + X_MAX) < len(text):
            ScrollChar += 1
            if ScrollChar == 0:
                ScrollWait = ScrollWaitInit
            if (ScrollChar + X_MAX) == len(text):
                ScrollWait = ScrollWaitEnd
        else:
            ScrollChar = 0
            ScrollWait = ScrollWaitInit

        # if text don't fit on visible area then scroll,
        # else leave it drawn and exit
        if len(text) > X_MAX:
            ScrollText = text[ScrollChar:(ScrollChar + X_MAX)]
        else:
            ScrollEnd = True

        # draw info text frame
        text_surface = PGoFont.render(ScrollText, True, p_oColor)
        PGoScreen.blit(text_surface, (X_POS, Y_POS))
        pygame.display.flip()

        # leave text drawn and exit
        if ScrollEnd or ScrollTimes <= 0:
            break

        # wait before to erase to create scroll efect
        if not wait_info_scroll(ScrollWait): return True

        # hide text for redraw
        text_surface = PGoFont.render(ScrollText, True, BLUEDARK)
        PGoScreen.blit(text_surface, (X_POS, Y_POS))
        pygame.display.flip()

        # substract one time of text scroll times
        if (ScrollChar + X_MAX) == len(text):
            if not wait_info_scroll(0.7): return True
            if ScrollTimes > 0:
                ScrollTimes -= 1
    return True

def wait_info_scroll(p_iScrollWait = 0.2):
    """ timer for text scroll function """
    p_iScrollCount = 0
    while p_iScrollCount <= p_iScrollWait:
        if not PGbScroll:
            return False
        time.sleep(0.1)
        p_iScrollCount += 0.1
    return True

def draw_menu_options_selection_bar():
    # draw current selection frame color
    pygame.draw.rect(PGoScreen, BLUELIGHT,
                    (32,(24 + iMARGIN_TOP) + iCurOption * iIntLine, iRES_X \
                    - 62, iIntLine))
    PGoScreen.blit((PGoFont.render(opt[iCurOption][0], 1, BLUEDARK)),
                    (iMARGIN_LEFT, (30 + iMARGIN_TOP + iLineAdj) + iCurOption * iIntLine))

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
                    (20,iMARGIN_TOP,iRES_X-40,(20+(iIntLine*9)+3+16+10)), 0)
    # draw options list frame
    pygame.draw.rect(PGoScreen, BLUELIGHT,
                    (32, iMARGIN_TOP + 24, iRES_X-62, iIntLine * 9), 1)
    # draw info list frame
    pygame.draw.rect(PGoScreen, BLUELIGHT,
                    (32,(iMARGIN_TOP + 23) + iIntLine * 9,iRES_X - 62, 16), 1)

def draw_menu_title():
    # draw title and version
    sTitle = PGoFont.render("Configuration Utility", 1, BLUELIGHT)
    PGoScreen.blit(sTitle, (32, iMARGIN_TOP+8))
    text_print("v4.0", iRES_X-62, iMARGIN_TOP+8, BLUEUNS, False)


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
        PGoSndClick.play()
        if iCurOption < 4:
            opt[iCurOption][2] = 0
        elif iCurOption == 4:
            launch_screen_tool_manager()
        elif iCurOption == 5:
            opt[5][2] = 0
            background_music_remove()
        elif iCurOption < 8:
            opt[iCurOption][2] = 0
        elif iCurOption == 8:
            quit_utility()
    #right
    elif event & CRT_RIGHT:
        PGoSndCursor.play()
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
        PGoSndCursor.play()
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
        PGoSndCursor.play()
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
        PGoSndCursor.play()
        if bRotateES == True:
            if iCurOption == 1:
                iCurOption = 8
        else:
            if iCurOption == 8:
                iCurOption = 0
            elif iCurOption < 8:
                iCurOption = iCurOption + 1
