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
import sys, os, commands, subprocess
import filecmp

CRT_PATH = "/opt/retropie/configs/all/CRT"
RESOURCES_PATH = os.path.join(CRT_PATH, "bin/GeneralModule")
sys.path.append(RESOURCES_PATH)

from launcher_module.core_paths import *
from launcher_module.core_choices_dynamic import choices
from launcher_module.file_helpers import modify_line
from launcher_module.screen import CRT
from launcher_module.utils import ra_check_version, get_xy_screen
from launcher_module.core_controls import joystick, CRT_UP, CRT_DOWN, CRT_LEFT, \
                                          CRT_RIGHT, CRT_BUTTON

CRTICONS_PATH = os.path.join(CRTROOT_PATH, "config/icons")
FONT_FILE = os.path.join(CRTFONTS_PATH, "PetMe64.ttf")

PATTERN_LAUNCHER_FILE = os.path.join(CRTMODULES_PATH,
                        "module_screen_center_utility/pattern_launcher.py")

TEST_SUITE_FILE = os.path.join(CRTADDONS_PATH, "addon_240p_suite/240pSuite.bin")
RA_MD_CFG_FILE1 = os.path.join(RETROPIECFG_PATH, "megadrive/retroarch.cfg")
RA_MD_CFG_FILE2 = os.path.join(CRTROOT_PATH, "Retroarch/configs/megadrive.cfg")
RA_MD_CORE_FILE = os.path.join(CRTADDONS_PATH,
                  "addon_240p_suite/genesis_plus_gx_libretro.so")

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
iCurOption = 0

bChangeMode = False
bChangeRes = False
bESReload = False

sESResLabel50 = 'system50'
sESResLabel60 = 'system60'

CurTheme = "none"
HorTheme240p = "none"
HorTheme270p = "none"
VerTheme240p = "none"
VerTheme270p = "none"

# modes[0][x] Mode name; modes[x][0] Mode description
modes = []
MaxModes = 0
MaxModesCounter = 0
SelectedMode = (['DEFAULT', "Timings presets for better compatibility"])

# pygame configurations
PGoJoyHandler = None
PGoScreen = None
PGoFont = None
BLUELIGHT = pygame.Color(165, 165, 255)
BLUEDARK = pygame.Color(66, 66, 231)
BLUEUNS = pygame.Color(110, 110, 255)
YELLOW = pygame.Color(255, 255, 0)
RED = pygame.Color(255, 0, 0)

# Screen CRT Class
oCRT = None

# menu options
opt = [["1.SYSTEM RESOLUTION" ,
        "Changes don't have effect inside the games", 0, 0],
       ["2.TV COMPATIBILITY" , 
        "Timings presets for better compatibility", "DEFAULT", "DEFAULT"],
       ["3.FRONTEND CENTERING>" ,
        "Affects only to Emulation Station"],
       ["4.IN-GAME CENTERING>" ,
        "Affects to all games"],
       ["5.240P TEST SUITE>" ,
        "Tool suite for TV/Monitor calibration"],
       ["empty" ,
        "empty"],
       ["empty" ,
        "empty"],
       ["empty" ,
        "empty"],
       ["<BACK" ,
        "Save and back to main menu"]]

def show_info(p_sMessage, p_iTime = 2000, p_sTitle = None):
    ch = choices()
    if p_sTitle:
        ch.set_title(p_sTitle)
    ch.load_choices([(p_sMessage, "OK")])
    ch.show(p_iTime)

def get_screen_size_adjust():
    global x_screen
    global y_screen
    global y_margin
    global Interline
    global LineMov
    global list_x
    global data_x

    # Get current x,y resolution
    x_screen, y_screen = get_xy_screen()

    if y_screen > 270:
        Multiplier = int((y_screen - 270) / 8)
        Interline = 20 + Multiplier
        LineMov = int(Multiplier / 2)
        y_margin = 20 + ((y_screen - 270) - (Multiplier * 9))
    elif y_screen < 270:
        Multiplier = int((270 - y_screen) / 8)
        Interline = 20 - Multiplier
        LineMov = int(-1 * (Multiplier / 2))
        y_margin = 20 - ((270 - y_screen) - (Multiplier * 9))
    elif y_screen == 270:
        y_margin = 20
        Interline = 20

    if x_screen < 340:
        data_x = 269
        list_x = 40
    else:
        data_x = 350
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
        text = PGoFont.render(txt, True, (color))
        textPos = text.get_rect()
        textPos.center = (x_screen/2, ycoord+6)
        PGoScreen.blit(text,textPos)
    else:
        PGoScreen.blit(PGoFont.render(txt, 1, (color)), (xcoord, ycoord))

def draw_arrow_left():
    PGoScreen.blit((PGoFont.render('<<', 1, (YELLOW))),
                                  (data_x-(len(str(str(opt[iCurOption][2])))*8)-18,
                                  (30+y_margin+LineMov)+iCurOption*Interline))

def draw_arrow_right():
    PGoScreen.blit((PGoFont.render('>>', 1, (YELLOW))),
                    (data_x+2, (30+y_margin+LineMov)+iCurOption*Interline))

def fix_icons_image():
    for file in os.listdir(CRTICONS_PATH):
        IconImg = CRTICONS_PATH + "/" + file
        IconImgMode = CRTICONS_SET_PATH + "/" + file[:-4] + "_" + opt[0][2] + ".png"
        if not os.path.isdir(IconImg):
            os.system('cp "%s" "%s" >> /dev/null 2>&1' % (IconImgMode, IconImg))

def replace_launching_image(p_sImage):
    p_lMask = (".png", ".jpg")
    if not p_sImage[-4:] in p_lMask:
        return
    image_cur = RETROPIECFG_PATH + "/" + p_sImage
    sImageSetA = CRTLAUNCHIMAGES_SET_PATH + "/" + p_sImage[:-4] + "_240p.png"
    sImageSetB = CRTLAUNCHIMAGES_SET_PATH + "/" + p_sImage[:-4] + "_270p.png"
    # if 240p is the chosen resolution, images are changed
    if "240" in opt[0][2]:
        sImageSetA = sImageSetA[:-9] + "_270p.png"
        sImageSetB = sImageSetB[:-9] + "_240p.png"
    try:
        if filecmp.cmp(image_cur, sImageSetA):
            os.system('cp "%s" "%s"' % (sImageSetB, image_cur))
    except:
        pass

def fix_launching_image():
    for Level1 in os.listdir(RETROPIECFG_PATH):
        LEVEL1 = os.path.join(RETROPIECFG_PATH, Level1)
        if os.path.isdir(LEVEL1):
            for Level2 in os.listdir(LEVEL1):
                LEVEL2 = os.path.join(LEVEL1, Level2)
                sFile2 = os.path.join(Level1, Level2)
                if os.path.isdir(LEVEL2):
                    for Level3 in os.listdir(LEVEL2):
                        LEVEL3 = os.path.join(LEVEL2, Level3)
                        sFile3 = os.path.join(Level1, Level2, Level3)
                        if os.path.isdir(LEVEL3):
                            for Level4 in os.listdir(LEVEL3):
                                LEVEL4 = os.path.join(LEVEL3, Level4)
                                sFile4 = os.path.join(Level1, Level2, Level3, Level4)
                                if os.path.isfile(LEVEL4):
                                    replace_launching_image(sFile4)
                        else:
                            replace_launching_image(sFile3)
                else:
                    replace_launching_image(sFile2)

def fix_aspect_ratio_images():
    show_info("WAIT, PREPARING RESOLUTION CHANGE")
    fix_launching_image()
    fix_icons_image() 

def save_configuration():
    # save resolution change parameters
    if bChangeRes == True:
        # replace with rigth aspect ratio images
        fix_aspect_ratio_images()
        modify_line(CFG_VIDEOUTILITY_FILE, '%s_theme_horizontal ' % opt[0][3],
                       '%s_theme_horizontal %s' % (opt[0][3], CurTheme))
        if opt[0][2] == '240p':
            modify_line(CFG_VIDEOUTILITY_FILE, 'default', 'default %s' % sESResLabel60)
            modify_line(ESCFG_FILE, '"ThemeSet"',
                           '<string name="ThemeSet" value="%s" />' % HorTheme240p)
        elif opt[0][2] == '270p':
            modify_line(CFG_VIDEOUTILITY_FILE,'default', 'default %s' % sESResLabel50)
            modify_line(ESCFG_FILE, '"ThemeSet"',
                           '<string name="ThemeSet" value="%s" />' % HorTheme270p)
    # save mode change parameters
    if bChangeMode == True:
        modify_line(CFG_FIXMODES_FILE,'mode_default',
                       'mode_default %s' % SelectedMode[0])
def quit_manager():
    iExitCode = 0
    pygame_unload()
    save_configuration()
    if bESReload:
        commandline = "/usr/bin/python %s force" % PATTERN_LAUNCHER_FILE
        output = commands.getoutput('ps -A')
        # Restart ES if it is running
        if 'emulationstatio' in output:
            commandline += " && "
            commandline += "touch /tmp/es-restart "
            commandline += "&& pkill -f \"/opt/retropie"
            commandline += "/supplementary/.*/emulationstation([^.]|$)\""
            show_info("EMULATIONSTATION WILL RESTART NOW")
            iExitCode = 1
        os.system(commandline)
    time.sleep(1)
    sys.exit(iExitCode)

def launch_application(sCommandline, bShell = False):
    global oCRT
    pygame_unload()
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
    ra_check_version(RA_MD_CFG_FILE2)
    oCRT = CRT("megadrive")
    oCRT.screen_calculated(CFG_TIMINGS_FILE)
    commandline = "%s -L %s " % (RETROARCHBIN_FILE, RA_MD_CORE_FILE)
    commandline += "--config %s " % RA_MD_CFG_FILE1
    commandline += "--appendconfig %s " % RA_MD_CFG_FILE2
    commandline += "\"%s\" " % TEST_SUITE_FILE
    commandline += "> /dev/null 2>&1"
    launch_application(commandline, True)

def get_available_modes():
    global modes
    global MaxModes
    global SelectedMode
    global MaxModesCounter
    if os.path.exists(CFG_FIXMODES_FILE):
        with open(CFG_FIXMODES_FILE, 'r') as file:
            counter = 0
            modes.append(['DEFAULT', "Timings presets for better compatibility"])
            for line in file:
                line = line.strip().replace('=',' ').split(' ')
                if line[0] == "mode":
                    modes.append([line[1], False])
                    counter += 1
                elif line[0] == 'mode_default':
                    SelectedMode[0] = line[1]
            MaxModes = counter
        counter = 0
        for item in modes:
            if item[0] != 'DEFAULT':
                with open(CFG_FIXMODES_FILE, 'r') as file:
                    for line in file:
                        line = line.strip().replace('=', ' ').split(' ')
                        if line[0] == '%s_desc' % item[0]:
                            modes[counter][1] = " ".join(line)\
                                                .replace('%s_desc' % item[0], '')\
                                                .strip()
            counter += 1
        counter = 0
        for item in modes:
            if item[0] == SelectedMode[0]:
                SelectedMode[1] = item[1]
                MaxModesCounter = counter
            counter += 1

    opt[1][2] = SelectedMode[0]
    opt[1][3] = SelectedMode[0]
    opt[1][1] = SelectedMode[1]

def get_config():
    global opt
    global CurTheme
    global HorTheme240p
    global HorTheme270p
    global VerTheme240p
    global VerTheme270p
    with open(CFG_VIDEOUTILITY_FILE, 'r') as file:
        for line in file:
            line = line.strip().replace('=',' ').split(' ')
            if line[0] == "default":
                if line[1] == sESResLabel50:
                    opt[0][2] = '270p'
                    if opt[0][3] == 0:
                        opt[0][3] = '270p'
                elif line[1] == sESResLabel60:
                    opt[0][2] = '240p'
                    if opt[0][3] == 0:
                        opt[0][3] = '240p'
            elif line[0] == '240p_theme_horizontal':
                HorTheme240p = line[1]
            elif line[0] == '270p_theme_horizontal':
                HorTheme270p = line[1]

    get_available_modes()

    if os.path.exists(ESCFG_FILE):
        with open(ESCFG_FILE, 'r') as file:
            for line in file:
                line = line.strip().replace('"','').replace(' ','')
                line = line.replace('/','').replace('>','').split('=')
                if 'ThemeSet' in line[1]:
                    CurTheme = line[2]

def draw_menu():
    global opt
    global bChangeRes
    global bChangeMode
    global bESReload

    # draw background color and main frame
    PGoScreen.fill(BLUELIGHT)
    pygame.draw.rect(PGoScreen, BLUEDARK, 
                    (20, y_margin, x_screen - 40, (49 + (Interline * 9))), 0)

    # draw title and version
    title = PGoFont.render("Configuration Utility", 1, BLUELIGHT)
    PGoScreen.blit(title, (32, y_margin + 8))
    text_print("v3.5", x_screen - 62, y_margin + 8, BLUEUNS, False)

    # draw options list frame
    pygame.draw.rect(PGoScreen, BLUELIGHT, (32, y_margin + 24,
                                             x_screen - 62, Interline * 9), 1)

    # clear any previous warning top red message
    text_print('SYSTEM NEEDS TO SHUTDOWN NOW', 0,
               y_margin - 13, BLUELIGHT, True)
    text_print('RESOLUTION WILL APPLY ON BACK/CENTERING', 0,
               y_margin - 13, BLUELIGHT, True)
    text_print('FIX WILL APPLY ON BACK/CENTERING', 0,
               y_margin - 13, BLUELIGHT, True)

    # draw if apply warning message on top
    bESReload = False
    bChangeRes = False
    bChangeMode = False

    if opt[0][2] != opt[0][3]:
        bChangeRes = True
        bESReload = True
        text_print('RESOLUTION WILL APPLY ON BACK/CENTERING', 0,
                   y_margin - 13, RED, True)

    if opt[1][2] != opt[1][3]:
        bChangeMode = True
        bESReload = True
        text_print('FIX WILL APPLY ON BACK/CENTERING', 0,
                    y_margin - 13, RED, True)

    # draw whole list of options in base color
    for i in range(0,9):
        if (i <= 4 or i == 8) and bChangeRes == False:
            opt[8][0] = '<BACK'
            opt[8][1] = 'Save and back to main menu'
            PGoScreen.blit((PGoFont.render(opt[i][0], 1, BLUELIGHT)),
                            (list_x, (30 + y_margin + LineMov) + i * Interline))
        elif (i <= 4 or i == 8) and bChangeRes == True:
            opt[8][0] = '<RESTART'
            opt[8][1] = 'Restart ES to apply new resolution...'
            if i == 0 or i == 8:
                PGoScreen.blit((PGoFont.render(opt[i][0], 1, BLUELIGHT)),
                                (list_x, (30 + y_margin + LineMov) \
                                + i * Interline))
            else:
                PGoScreen.blit((PGoFont.render(opt[i][0], 1, BLUEUNS)),
                                (list_x, (30+y_margin+LineMov)+i*Interline))

    # draw all selectables values in base color
    for i in range(0,9):
        if (i < 2) and bChangeRes == False:
            esres = PGoFont.render(str(opt[i][2]), 1, BLUELIGHT)
            PGoScreen.blit(esres, (data_x-(len(str(opt[i][2])) * 8),
                                            (30 + y_margin + LineMov) \
                                            + i * Interline))
        elif (i < 2) and bChangeRes == True:
            if i == 0:
                mode = PGoFont.render(str(opt[i][2]), 1, BLUELIGHT)
                PGoScreen.blit(mode, (data_x-(len(str(opt[i][2])) * 8),
                                      (30 + y_margin + LineMov) + i * Interline))
            else:
                esres = PGoFont.render(str(opt[i][2]), 1, BLUEUNS)
                PGoScreen.blit(esres, (data_x-(len(str(opt[i][2])) * 8),
                                        (30 + y_margin + LineMov) \
                                        + i * Interline))

    # draw current selection frame color
    pygame.draw.rect(PGoScreen, BLUELIGHT,
                    (32, (24 + y_margin) + iCurOption * Interline, x_screen \
                    - 62, Interline))
    PGoScreen.blit((PGoFont.render(opt[iCurOption][0], 1, BLUEDARK)),
                    (list_x, (30 + y_margin + LineMov) + iCurOption * Interline))

    # draw active option in dark color
    if iCurOption == 0:
        esres = PGoFont.render(str(opt[0][2]), 1, BLUEDARK)
        PGoScreen.blit(esres, (data_x - (len(str(opt[0][2])) * 8),
                        (30 + y_margin + LineMov) + iCurOption * Interline))
        if opt[0][2] == '240p':
            draw_arrow_right()
        elif opt[0][2] == '270p':
            draw_arrow_left()
    elif iCurOption == 1:
        modres = PGoFont.render(str(opt[1][2]), 1, BLUEDARK)
        PGoScreen.blit(modres, (data_x - (len(str(opt[1][2])) * 8),
                        (30 + y_margin + LineMov) + iCurOption * Interline))
        if MaxModes != 0:
            if MaxModesCounter == 0:
                draw_arrow_right()
            elif MaxModesCounter < MaxModes:
                draw_arrow_left()
                draw_arrow_right()
            elif MaxModesCounter == MaxModes:
                draw_arrow_left()

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
                    (32, (y_margin + 23) + Interline * 9, x_screen - 62, 16), 1)
    pygame.display.flip()

# MAIN PROGRAM
script_initialization()

while True:
    draw_menu()
    event = PGoJoyHandler.event_wait()
    #button
    if event & CRT_BUTTON:
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
        if iCurOption == 0:
            if opt[0][2] == '240p':
                opt[0][2] = '270p'
                if opt[0][2] != opt[0][3]:
                    iCurOption = 8
        elif iCurOption == 1:
            if MaxModesCounter < MaxModes:
                MaxModesCounter+=1
                SelectedMode[0] = modes[MaxModesCounter][0]
                SelectedMode[1] = modes[MaxModesCounter][1]
                opt[1][2] = SelectedMode[0]
                opt[1][1] = SelectedMode[1]
    #left
    elif event & CRT_LEFT:
        if iCurOption == 0:
            if opt[0][2] == '270p':
                opt[0][2] = '240p'
                if opt[0][2] != opt[0][3]:
                    iCurOption = 8
        elif iCurOption == 1:
            if MaxModesCounter > 0:
                MaxModesCounter-=1
                SelectedMode[0] = modes[MaxModesCounter][0]
                SelectedMode[1] = modes[MaxModesCounter][1]
                opt[1][2] = SelectedMode[0]
                opt[1][1] = SelectedMode[1]
    #up
    elif event & CRT_UP:
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
