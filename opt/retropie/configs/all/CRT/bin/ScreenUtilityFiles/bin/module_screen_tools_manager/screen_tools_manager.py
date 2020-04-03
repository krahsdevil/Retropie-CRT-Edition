#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Screen Tool Manager

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
import pygame, time
import sys, os, commands, subprocess, threading
import filecmp

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(SCRIPT_DIR + "/../"))
from main_paths import MODULES_PATH
sys.path.append(MODULES_PATH)

from module_screen_center_utility.pattern_launcher import center
from module_configuration_utility.sys_resolution import resolution_change
from launcher_module.core_paths import *
from launcher_module.file_helpers import modify_line, set_xml_value_esconfig, \
                                         get_xml_value_esconfig, ini_get, \
                                         ini_getlist
from launcher_module.screen import CRT
from launcher_module.utils import ra_version_fixes, get_screen_resolution, show_info
from launcher_module.core_controls import joystick, CRT_UP, CRT_DOWN, CRT_LEFT, \
                                          CRT_RIGHT, CRT_BUTTON

CRTICONS_PATH = os.path.join(CRT_ROOT_PATH, "config/icons")
FONT_FILE = os.path.join(CRT_FONTS_PATH, "PetMe64.ttf")
CURSOR_SOUND_FILE = os.path.join(CRT_SOUNDS_PATH, "sys_cursor_01.ogg")
CLICK_SOUND_FILE = os.path.join(CRT_SOUNDS_PATH, "sys_click_01.ogg")

PATTERN_LAUNCHER_FILE = os.path.join(CRT_MODULES_PATH,
                        "module_screen_center_utility/pattern_launcher.py")

TEST_SUITE_FILE = os.path.join(CRT_ADDN_PATH, "addon_240p_suite/240pSuite.bin")
RA_MD_CFG_FILE1 = os.path.join(RETROPIE_CFG_PATH, "megadrive/retroarch.cfg")
RA_MD_CFG_FILE2 = os.path.join(CRT_ROOT_PATH, "Retroarch/configs/megadrive.cfg")
RA_MD_CORE_FILE = os.path.join(CRT_ADDN_PATH,
                  "addon_240p_suite/genesis_plus_gx_libretro.so")

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

bChangeMode = False
bChangeRes = False
bESReload = False

# theme changing for resolution change
sSystem50 = "system50"
sSystem60 = "system60"

# modes[0][x] Mode name; modes[x][0] Mode description
lModeAll = []
lModeSel = []
iModeCur = 0

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

# Screen CRT Class
oCRT = None

# menu options
opt = [["1.SYSTEM RESOLUTION" ,
        "Change EmulationStation and system resolution. " + \
        "This don't have effect inside the games.", 0, 0],
       ["2.TV COMPATIBILITY" ,
        "WARNING!!! Timings presets for better compatibility. " + \
        "Affects directly to main system resolution so could " + \
        "make Retropie CRT Edition unusable, apply only if you " + \
        "are experiencing issues during emulation or showing " + \
        "EmulationStation user interface.", "DEFAULT", "DEFAULT"],
       ["3.FRONTEND CENTERING>" ,
        "Affects only to system and EmulationStation. Both " + \
        "tests 240p and 270p are launched in a row."],
       ["4.IN-GAME CENTERING>" ,
        "Affects to all games."],
       ["5.240P TEST SUITE>" ,
        "Artemio Urbina's tools suite for TV/Monitor calibration. " + \
        "Useful for hardware adjustements like convergence or geometry."],
       ["" , ""],
       ["" , ""],
       ["" , ""],
       ["<BACK" ,
        "Save and back to main menu"]]

DEFAULT_MODES = "\"mode_default DEFAULT\n\n"
DEFAULT_MODES += "mode MODE1\n"
DEFAULT_MODES += "MODE1_desc TRINITRON RED CLASSIC FIX\n"
DEFAULT_MODES += "MODE1_game_mask 0 0 0 0 -10 0 0 -92 0 0 0\n"
DEFAULT_MODES += "MODE1_game_mask_raw 0 0 0 -9 0 0 0 0 0 0 0 0 0 0 0 0 0\n"
DEFAULT_MODES += "MODE1_system50 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n"
DEFAULT_MODES += "MODE1_system60 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n\n"
DEFAULT_MODES += "mode MODE2\n"
DEFAULT_MODES += "MODE2_desc COMPATIBILITY MODE2\n"
DEFAULT_MODES += "MODE2_game_mask 0 0 0 0 0 0 0 -50 0 -4 0\n"
DEFAULT_MODES += "MODE2_game_mask_raw 0 0 0 -9 0 0 0 0 -4 0 0 0 0 0 0 0 0\n"
DEFAULT_MODES += "MODE2_system50 0 0 -6 -6 6 0 0 3 -4 4 0 0 0 0 0 0 0\n"
DEFAULT_MODES += "MODE2_system60 0 0 0 -9 0 0 0 0 -4 0 0 0 0 0 0 0 0\n\n"
DEFAULT_MODES += "mode MODE3\n"
DEFAULT_MODES += "MODE3_desc COMPATIBILITY MODE3\n"
DEFAULT_MODES += "MODE3_game_mask 0 0 0 0 0 0 0 -110 0 -4 0\n"
DEFAULT_MODES += "MODE3_game_mask_raw 0 0 10 -17 0 0 0 0 -4 0 0 0 0 0 0 0 0\n"
DEFAULT_MODES += "MODE3_system50 0 0 -6 -10 6 0 0 3 -4 4 0 0 0 0 0 0 0\n"
DEFAULT_MODES += "MODE3_system60 0 0 10 -17 0 0 0 0 -4 0 0 0 0 0 0 0 0\n\n\""

def get_screen_size_adjust():
    global iRES_X
    global iRES_Y
    global iMARGIN_TOP
    global iIntLine
    global iLineAdj
    global iMARGIN_LEFT
    global iMARGIN_RIGHT

    # Get current x,y resolution
    iRES_X, iRES_Y = get_screen_resolution()

    if iRES_Y > 270:
        Multiplier = int((iRES_Y - 270) / 8)
        iIntLine = 20 + Multiplier
        iLineAdj = int(Multiplier / 2)
        iMARGIN_TOP = 20 + ((iRES_Y - 270) - (Multiplier * 9))
    elif iRES_Y < 270:
        Multiplier = int((270 - iRES_Y) / 8)
        iIntLine = 20 - Multiplier
        iLineAdj = int(-1 * (Multiplier / 2))
        iMARGIN_TOP = 20 - ((270 - iRES_Y) - (Multiplier * 9))
    elif iRES_Y == 270:
        iMARGIN_TOP = 20
        iIntLine = 20

    if iRES_X < 340:
        iMARGIN_RIGHT = 269
        iMARGIN_LEFT = 40
    else:
        iMARGIN_RIGHT = 350
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
    PGoScreen = pygame.display.set_mode((iRES_X,iRES_Y), pygame.FULLSCREEN)
    PGoSndCursor = pygame.mixer.Sound(CURSOR_SOUND_FILE)
    PGoSndClick = pygame.mixer.Sound(CLICK_SOUND_FILE)

def clean():
    global PGbScroll
    PGbScroll = False
    PGoJoyHandler.quit()
    while pygame.mixer.get_busy():
        pass
    pygame.quit()

def script_initialization():
    os.system('clear')
    get_screen_size_adjust()
    get_config()
    pygame_initialization()

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
        text = PGoFont.render(txt, True, (color))
        textPos = text.get_rect()
        textPos.center = (iRES_X/2, ycoord+6)
        PGoScreen.blit(text,textPos)
    else:
        PGoScreen.blit(PGoFont.render(txt, 1, (color)), (xcoord, ycoord))

def draw_arrow_left(p_sLabel = 0):
    PGoScreen.blit((PGoFont.render('<<', 1, YELLOW)),
                   (iMARGIN_RIGHT - (len(p_sLabel) * 8) - 18,
                   (30 + iMARGIN_TOP + iLineAdj) + iCurOption * iIntLine))

def draw_arrow_right():
    PGoScreen.blit((PGoFont.render('>>', 1, (YELLOW))), (iMARGIN_RIGHT + 2,
                   (30 + iMARGIN_TOP+iLineAdj) + iCurOption * iIntLine))

def save_configuration():
    if bChangeMode:
        modify_line(CRT_FIXMODES_FILE, "mode_default",
                    "mode_default %s" % lModeSel[0])
def quit_manager():
    clean()
    save_configuration()
    # save resolution change parameters
    if bChangeRes:
        oChangeRes = resolution_change(opt[0][2])
        oChangeRes.change()
    elif bChangeMode:
        show_info("APPLYING MODE")
        oApplyMode = center()
        oApplyMode.launch("force")
    sys.exit(0)

def launch_application(sCommandline, bShell = False):
    global oCRT
    clean()
    save_configuration()
    oRunProcess = subprocess.Popen(sCommandline, shell=bShell)
    iExitCode = oRunProcess.wait()
    if oCRT:
        oCRT.screen_restore()
        oCRT = None
    os.execl(sys.executable, sys.executable, *sys.argv)

def launch_center_utility_es():
    commandline = "/usr/bin/python %s system" % PATTERN_LAUNCHER_FILE
    launch_application(commandline, True)

def launch_center_utility_ingame():
    commandline = "/usr/bin/python %s test60" % PATTERN_LAUNCHER_FILE
    launch_application(commandline, True)

def launch_test_suite():
    global oCRT
    ra_version_fixes(RA_MD_CFG_FILE2)
    oCRT = CRT("megadrive")
    oCRT.screen_calculated(CRT_DB_SYSTEMS_FILE)
    commandline = "%s -L %s " % (RA_BIN_FILE, RA_MD_CORE_FILE)
    commandline += "--config %s " % RA_MD_CFG_FILE1
    commandline += "--appendconfig %s " % RA_MD_CFG_FILE2
    commandline += "\"%s\" " % TEST_SUITE_FILE
    commandline += "> /dev/null 2>&1"
    launch_application(commandline, True)

def get_available_modes():
    global lModeAll
    global lModeSel
    global iModeCur

    lModeAll.append([opt[1][2], opt[1][1]])
    lModeSel = ([opt[1][2], opt[1][1]])

    if not os.path.exists(CRT_FIXMODES_FILE):
        os.system('echo %s > %s' % \
                 (DEFAULT_MODES, CRT_FIXMODES_FILE))

    with open(CRT_FIXMODES_FILE, 'r') as f:
        for line in f:
            line = line.strip().replace('=',' ').split(' ')
            if line[0] == "mode":
                lModeAll.append([line[1], ""])
            elif line[0] == "mode_default":
                lModeSel[0] = line[1]

    for item in lModeAll:
        if item[0] != "DEFAULT":
            lModeDesc = ini_getlist(CRT_FIXMODES_FILE,
                                    "%s_desc" % item[0])
            item[1] = " ".join(lModeDesc)
            if item[0] == lModeSel[0]: 
                lModeSel[1] = " ".join(lModeDesc)

    iModeCur = lModeAll.index([lModeSel[0], lModeSel[1]])

    opt[1][2] = lModeSel[0]
    opt[1][3] = lModeSel[0]
    opt[1][1] = lModeSel[1]

def get_resolution_and_themes():
    global opt
    sCurRes = ""
    sCurResID = "270p"

    sCurRes = ini_get(CRT_UTILITY_FILE, "default")
    if sCurRes == sSystem50:
        sCurResID = "270p"
    elif sCurRes == sSystem60:
        sCurResID = "240p"

    # init current resolution info in options
    opt[0][2] = sCurResID
    opt[0][3] = sCurResID

def get_config():
    get_resolution_and_themes()
    get_available_modes()

def check_resolution_change(p_iOption = None):
    global bESReload
    global bChangeRes
    global bChangeMode
    bESReload = False
    bChangeRes = False
    bChangeMode = False
    p_lDisOpt = []

    if opt[0][2] != opt[0][3]:
        bChangeRes = True
        bESReload = True
        p_lDisOpt = [1, 2, 3, 4, 5, 6, 7]
    elif opt[1][2] != opt[1][3]:
        bChangeMode = True
        bESReload = True

    if bChangeRes:
        opt[8][0] = "[RESTART]"
        opt[8][1] = 'Restart EmulationStation to apply new resolution.'
        text_print('RESOLUTION WILL APPLY ON BACK/CENTERING', 0,
                   iMARGIN_TOP - 13, RED, True)
    elif bChangeMode:
        opt[8][0] = "[RESTART]"
        opt[8][1] = 'Restart EmulationStation to apply new compatibility MODE.'
        text_print('FIX WILL APPLY ON BACK/CENTERING', 0,
                    iMARGIN_TOP - 13, RED, True)
    else:
        opt[8][0] = '<BACK'
        opt[8][1] = 'Save and back to main menu'

    if p_iOption != None:
        if p_iOption in p_lDisOpt and bChangeRes:
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
        if p_iCurValue == "240p":
            p_bRArrow = True
            p_sLabel = "240p"
        elif p_iCurValue == "270p":
            p_bLArrow = True
            p_sLabel = "270p"
    elif p_sOption == 1:
        if len(lModeAll) - 1 != 0:
            if iModeCur == 0:
                p_bRArrow = True
            elif iModeCur < len(lModeAll) - 1:
                p_bLArrow = True
                p_bRArrow = True
            elif iModeCur == len(lModeAll) - 1:
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
            if not check_resolution_change(p_iCount):
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
    check_resolution_change()
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
        if iCurOption == 2 and bChangeRes == False:
            launch_center_utility_es()
        if iCurOption == 3 and bChangeRes == False:
            launch_center_utility_ingame()
        if iCurOption == 4 and bChangeRes == False:
            launch_test_suite()
        if iCurOption == 8:
            quit_manager()
    #right
    elif event & CRT_RIGHT:
        PGoSndCursor.play()
        if iCurOption == 0:
            if opt[0][2] == "240p":
                opt[0][2] = "270p"
                if opt[0][2] != opt[0][3]:
                    iCurOption = 8
        elif iCurOption == 1:
            if iModeCur < len(lModeAll) - 1:
                iModeCur+=1
                lModeSel[0] = lModeAll[iModeCur][0]
                lModeSel[1] = lModeAll[iModeCur][1]
                opt[1][2] = lModeSel[0]
                opt[1][1] = lModeSel[1]
    #left
    elif event & CRT_LEFT:
        PGoSndCursor.play()
        if iCurOption == 0:
            if opt[0][2] == "270p":
                opt[0][2] = "240p"
                if opt[0][2] != opt[0][3]:
                    iCurOption = 8
        elif iCurOption == 1:
            if iModeCur > 0:
                iModeCur-=1
                lModeSel[0] = lModeAll[iModeCur][0]
                lModeSel[1] = lModeAll[iModeCur][1]
                opt[1][2] = lModeSel[0]
                opt[1][1] = lModeSel[1]
    #up
    elif event & CRT_UP:
        PGoSndCursor.play()
        if bChangeRes == True:
            if iCurOption == 8:
                iCurOption = 0
        else:
            if iCurOption == 8:
                iCurOption = 4
            elif iCurOption > 0:
                iCurOption = iCurOption - 1
            elif iCurOption == 0:
                iCurOption = 8
    #down
    elif event & CRT_DOWN:
        PGoSndCursor.play()
        if bChangeRes == True:
            if iCurOption == 0:
                iCurOption = 8
        else:
            if iCurOption == 4:
                iCurOption = 8
            elif iCurOption < 8:
                iCurOption = iCurOption + 1
            elif iCurOption == 8:
                iCurOption = 0
