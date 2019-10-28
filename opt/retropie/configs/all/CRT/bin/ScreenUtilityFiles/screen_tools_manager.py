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
import time
import pygame
import sys
import os
import commands
import subprocess
import math
import filecmp

#sys.path.insert(0, '/opt/retropie/configs/all/CRT/')
sys.path.append('/opt/retropie/configs/all/CRT/bin/GeneralModule/')
sys.path.append('/opt/retropie/configs/all/CRT/')
from selector_module_functions import get_retropie_joy_map
from selector_module_functions import check_joy_event
from pygame.locals import *
from general_functions import *

os.system('clear')

x_screen = 0
y_screen = 0
x_margin = 0
y_margin = 0
MarginNorm = 0.1482
Interline = 0
LineMov = 0

#positions and arrows color
data_x = 0
list_x = 0
arrow_c = [255,255,0]

SaveConfig = False
SaveModes = False
OutputModeChange = False
ResModeChange = False


def get_xy_screen():
    global x_screen
    global y_screen
    global x_margin
    global y_margin
    global Interline
    global LineMov
    global list_x
    global data_x
    process = subprocess.Popen("fbset", stdout=subprocess.PIPE)
    output = process.stdout.read()
    for line in output.splitlines():
        if 'x' in line and 'mode' in line:
            ResMode = line
            ResMode = ResMode.replace('"','').replace('x',' ').split(' ')
            x_screen = int(ResMode[1])
            y_screen = int(ResMode[2])
    if y_screen > 270:
        Multiplier = int((y_screen-270)/8)
        Interline = 20+Multiplier
        LineMov = int(Multiplier/2)
        y_margin = 20+((y_screen-270)-(Multiplier*9))
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
        list_x = 40
    else:
        data_x = 350
        list_x = 100

# INITS
get_xy_screen()
pygame.init()
pygame.mouse.set_visible(0)
get_retropie_joy_map()

# VARIABLES
ES_Res_50hz = 'system50'
ES_Res_60hz = 'system60'
CurTheme = "none"
HorTheme240p = "none"
HorTheme270p = "none"
VerTheme240p = "none"
VerTheme270p = "none"
state_up = 0
state_down = 0
state_left = 0
state_right = 0
threshold = 1000 # Analogic middle to debounce
joystick = 0 # 0 is the 1sf joystick

opt = 0
x = 0
y = 0
y_slide = 0

#########################################################
# ALL FINDED MODES                                      #
# modes[0][x] Mode name                                 #
# modes[x][0] Mode description                          #
#########################################################
modes = []
MaxModes = 0
MaxModesCounter = 0
########################################################
# CURRECT SELECTED MODE                                #
# SelectedMode[0][x] Mode name                         #
# SelectedMode[x][0] Mode description                  #
########################################################
SelectedMode = (['DEFAULT', "Timings presets for better compatibility"])

#files
sucfg = '/opt/retropie/configs/all/CRT/su.cfg'
VideoUtilityCFG = "/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/config_files/utility.cfg"
EsSystemcfg = "/opt/retropie/configs/all/emulationstation/es_settings.cfg"
CompModesCFG = '/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/config_files/modes.cfg'
MainConfPath = '/opt/retropie/configs'
LaunchImgPath = '/opt/retropie/configs/all/CRT/bin/emulationstation/CRTResources/launch_images_modes'
IconsImgPathSrc = '/opt/retropie/configs/all/CRT/bin/emulationstation/CRTResources/crt_icons'
IconsImgPathDst = '/opt/retropie/configs/all/CRT/config/icons'
RaspbianCFG = "/boot/config.txt"

# FUNCTIONS
def text_print(txt, xcoord, ycoord, r, g, b, center):
    if x_screen <= 340:
        txt = txt[0:28]
        if len(txt) >= 28 :
            txt = txt + '...'
    else:
        txt = txt[0:44]
        if len(txt) >= 44 :
            txt = txt + '...'

    if center == True:
        text = myfont.render(txt, True, (r,g,b))
        textPos = text.get_rect()
        textPos.center = (x_screen/2, ycoord+6)
        fullscreen.blit(text,textPos)
    else:
        fullscreen.blit(myfont.render(txt, 1, (r,g,b)), (xcoord, ycoord))

def draw_arrow_left():
    fullscreen.blit((myfont.render('<<', 1, (arrow_c))), (data_x-(len(str(str(opt[option][2])))*8)-18, (30+y_margin+LineMov)+y*Interline))

def draw_arrow_right():
    fullscreen.blit((myfont.render('>>', 1, (arrow_c))), (data_x+2, (30+y_margin+LineMov)+y*Interline))

def replace_launch_image(image):
    image_cur = MainConfPath+"/"+image
    image_240p = LaunchImgPath+"/"+image[:-4]+"_240p.png"
    image_270p = LaunchImgPath+"/"+image[:-4]+"_270p.png"
    if "240" in opt[0][2]:
        try:
            if filecmp.cmp(image_cur, image_270p):
                os.system('cp "%s" "%s" >> /dev/null 2>&1'%(image_240p, image_cur))
        except:
            pass
    elif "270" in opt[0][2]:
        try:
            if filecmp.cmp(image_cur, image_240p):
                os.system('cp "%s" "%s" >> /dev/null 2>&1'%(image_270p, image_cur))
        except:
            pass

def replace_icons_image():
    for file in os.listdir(IconsImgPathDst):
        IconImg = IconsImgPathDst+"/"+file
        IconImgMode = IconsImgPathSrc+"/"+file[:-4]+"_"+opt[0][2]+".png"
        if not os.path.isdir(IconImg):
            os.system('cp "%s" "%s" >> /dev/null 2>&1'%(IconImgMode, IconImg))

def search_launch_image():
    for Level1 in os.listdir(MainConfPath):
        if os.path.isdir(MainConfPath+"/"+Level1):
            for Level2 in os.listdir(MainConfPath+"/"+Level1):
                if os.path.isdir(MainConfPath+"/"+Level1+"/"+Level2):
                    for Level3 in os.listdir(MainConfPath+"/"+Level1+"/"+Level2):
                        if os.path.isdir(MainConfPath+"/"+Level1+"/"+Level2+"/"+Level3):
                            for Level4 in os.listdir(MainConfPath+"/"+Level1+"/"+Level2+"/"+Level3):
                                if os.path.isfile(MainConfPath+"/"+Level1+"/"+Level2+"/"+Level3+"/"+Level4):
                                    replace_launch_image(Level1+"/"+Level2+"/"+Level3+"/"+Level4)
                        else:
                            replace_launch_image(Level1+"/"+Level2+"/"+Level3)
                else:
                    replace_launch_image(Level1+"/"+Level2)

def save():
    if SaveConfig == True:
        modificarLinea(VideoUtilityCFG, '%s_theme_horizontal '%opt[0][3], '%s_theme_horizontal %s'%(opt[0][3], CurTheme))
        if opt[0][2] == '240p':
            modificarLinea(VideoUtilityCFG,'default','default %s'%ES_Res_60hz)
            modificarLinea(EsSystemcfg, '"ThemeSet"', '<string name="ThemeSet" value="%s" />'%HorTheme240p)
        elif opt[0][2] == '270p':
            modificarLinea(VideoUtilityCFG,'default','default %s'%ES_Res_50hz)
            modificarLinea(EsSystemcfg, '"ThemeSet"', '<string name="ThemeSet" value="%s" />'%HorTheme270p)
        search_launch_image()
        replace_icons_image()
    if SaveModes == True:
        modificarLinea(CompModesCFG,'mode_default','mode_default %s'%SelectedMode[0])

def quit_manager():
    if ResModeChange == True or SaveModes == True:
        save()
        pygame.quit()
        commandline = "/usr/bin/python /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/screen_center_utility.py force"
        os.system(commandline)
        output = commands.getoutput('ps -A')
        # Restart ES if it is running
        if 'emulationstatio' in output:
            os.system('sudo pkill -9 -f \"Configuration Utility\"')
            os.system("touch /tmp/es-restart && pkill -f \"/opt/retropie/supplementary/.*/emulationstation([^.]|$)\"")
    elif OutputModeChange == True:
        CurMode = 'none'
        rgbpidto = False
        rgbpidtoformat = False
        pi2scart_audio1 = False
        pi2scart_audio2 = False
        with open(RaspbianCFG, 'r') as file:
            for line in file:
                if 'dtoverlay=rgb-pi' in line:
                    CurMode = 'RGB-Pi'
                elif 'dtoverlay=vga666' in line:
                    CurMode = 'VGA666'
                elif 'dtoverlay=pwm-2chan,pin=18,func=2,pin2=19,func2=2' in line:
                    rgbpidto = True
                elif 'dpi_output_format=6' in line:
                    rgbpidtoformat = True
                elif 'disable_audio_dither=1' in line:
                    pi2scart_audio1 = True
                elif 'dtparam=audio=on' in line:
                    pi2scart_audio2 = True
        if CurMode != 'none':
            if opt[2][2] == 'RGB-Pi':
                modificarLinea("/tmp/config.txt","dtoverlay=vga666", "dtoverlay=rgb-pi")
                if rgbpidto == True:
                    modificarLinea("/tmp/config.txt","dtoverlay=pwm-2chan,pin=18,func=2,pin2=19,func2=2", "dtoverlay=pwm-2chan,pin=18,func=2,pin2=19,func2=2")
                else:
                    os.system('echo \"dtoverlay=pwm-2chan,pin=18,func=2,pin2=19,func2=2\" >> /tmp/config.txt')
                if rgbpidtoformat == True:
                    modificarLinea("/tmp/config.txt","dpi_output_format=6", "dpi_output_format=6")
                else:
                    os.system('echo \"dpi_output_format=6\" >> /tmp/config.txt')
                if pi2scart_audio1 == True:
                    modificarLinea("/tmp/config.txt","disable_audio_dither=1", "#disable_audio_dither=1")
                else:
                    os.system('echo \"#disable_audio_dither=1\" >> /tmp/config.txt')
                if pi2scart_audio2 == True:
                    modificarLinea("/tmp/config.txt","dtparam=audio=on", "dtparam=audio=on")
                else:
                    os.system('echo \"dtparam=audio=on\" >> /tmp/config.txt')
            elif opt[2][2] == 'VGA666':
                modificarLinea("/tmp/config.txt","dtoverlay=rgb-pi", "dtoverlay=vga666")
                if rgbpidto != False:
                    modificarLinea("/tmp/config.txt","dtoverlay=pwm-2chan,pin=18,func=2,pin2=19,func2=2", "#dtoverlay=pwm-2chan,pin=18,func=2,pin2=19,func2=2")
                else:
                    os.system('echo \"#dtoverlay=pwm-2chan,pin=18,func=2,pin2=19,func2=2\" >> /tmp/config.txt')
                if rgbpidtoformat != False:
                    modificarLinea("/tmp/config.txt","dpi_output_format=6", "#dpi_output_format=6")
                else:
                    os.system('echo \"#dpi_output_format=6\" >> /tmp/config.txt')
                if pi2scart_audio1 == True:
                    modificarLinea("/tmp/config.txt","disable_audio_dither=1", "#disable_audio_dither=1")
                else:
                    os.system('echo \"#disable_audio_dither=1\" >> /tmp/config.txt')
                if pi2scart_audio2 == True:
                    modificarLinea("/tmp/config.txt","dtparam=audio=on", "dtparam=audio=on")
                else:
                    os.system('echo \"dtparam=audio=on\" >> /tmp/config.txt')
            elif opt[2][2] == 'PI2SCART':
                modificarLinea("/tmp/config.txt","dtoverlay=rgb-pi", "dtoverlay=vga666")
                if rgbpidto != False:
                    modificarLinea("/tmp/config.txt","dtoverlay=pwm-2chan,pin=18,func=2,pin2=19,func2=2", "#dtoverlay=pwm-2chan,pin=18,func=2,pin2=19,func2=2")
                else:
                    os.system('echo \"#dtoverlay=pwm-2chan,pin=18,func=2,pin2=19,func2=2\" >> /tmp/config.txt')
                if rgbpidtoformat != False:
                    modificarLinea("/tmp/config.txt","dpi_output_format=6", "#dpi_output_format=6")
                else:
                    os.system('echo \"#dpi_output_format=6\" >> /tmp/config.txt')
                if pi2scart_audio1 == True:
                    modificarLinea("/tmp/config.txt","disable_audio_dither=1", "disable_audio_dither=1")
                else:
                    os.system('echo \"disable_audio_dither=1\" >> /tmp/config.txt')
                if pi2scart_audio2 == True:
                    modificarLinea("/tmp/config.txt","dtparam=audio=on", "dtparam=audio=on")
                else:
                    os.system('echo \"dtparam=audio=on\" >> /tmp/config.txt')
            os.system('sudo cp /tmp/config.txt %s' % RaspbianCFG)
            os.remove('/tmp/config.txt')
            os.system('sudo shutdown now')
    sys.exit()

def get_output_video_mode():
    global opt
    os.system('cp %s /tmp/config.txt' % RaspbianCFG)
    OutputMode = 'none'
    pi2scart_audio1 = False
    pi2scart_audio2 = False
    with open(RaspbianCFG, 'r') as file:
        for line in file:
            line = line.strip()
            if 'dtoverlay=rgb-pi' in line:
                OutputMode = 'RGB-Pi'
            elif 'dtoverlay=vga666' in line:
                OutputMode = 'VGA666'
            elif 'disable_audio_dither=1' == line:
                pi2scart_audio1 = True
            elif 'dtparam=audio=on' == line:
                pi2scart_audio2 = True
    if OutputMode == 'VGA666'and pi2scart_audio1 == True and pi2scart_audio2 == True:
        OutputMode = 'PI2SCART'
    opt[2][2] = OutputMode
    if opt[2][3] == 'unknown':
        opt[2][3] = OutputMode

def screen_center_utility_es():
    save()
    pygame.quit()
    commandline = "/usr/bin/python /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/screen_center_utility.py system"
    os.system(commandline)
    get_xy_screen()
    os.execl(sys.executable, sys.executable, *sys.argv)

def screen_center_utility_ingame():
    save()
    pygame.quit()
    commandline = "/usr/bin/python /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/screen_center_utility.py test60"
    os.system(commandline)
    get_xy_screen()
    os.execl(sys.executable, sys.executable, *sys.argv)

def test_suite():
    save()
    TestSuiteRom = "/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/addons/addon_240p_suite/240pSuite.bin"
    timings_full_path = "/opt/retropie/configs/all/CRT/Resolutions/base_systems.cfg"
    ra_cfg_path = "/opt/retropie/configs/all/CRT/Retroarch/configs/megadrive.cfg"
    ra_bin_path = "/opt/retropie/emulators/retroarch/bin/retroarch"
    retroarch_core = "/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/addons/addon_240p_suite/genesis_plus_gx_libretro.so"
    Check_RetroArch_Version(ra_cfg_path)
    crt_open_screen_from_timings_cfg('megadrive',timings_full_path)
    pygame.quit()
    commandline = "%s -L %s --config /opt/retropie/configs/megadrive/retroarch.cfg --appendconfig %s \"%s\" > /dev/null 2>&1" % (ra_bin_path,retroarch_core,ra_cfg_path,TestSuiteRom)
    os.system(commandline)
    es_restore_screen()
    get_xy_screen()
    os.execl(sys.executable, sys.executable, *sys.argv)

# SET SCREEN
black = pygame.Color(0,0,0)
white = pygame.Color(255,255,255)
BlueLight = pygame.Color(165,165,255)
BlueDark = pygame.Color(66,66,231)
BlueUnselect = pygame.Color(110,110,255)

fullscreen = pygame.display.set_mode((x_screen,y_screen), FULLSCREEN)
fullscreen.fill(BlueLight)

# FONT
myfont = pygame.font.Font("/opt/retropie/configs/all/CRT/config/PetMe64.ttf", 8)

# loading data from su.cfg
opt = [["1.SYSTEM RESOLUTION" , "Changes don't have effect inside the games", 0, 0],
    ["2.TV COMPATIBILITY" , "Timings presets for better compatibility", "DEFAULT", "DEFAULT"],
    ["3.RGB OUTPUT MODE" , 'Change DPI Overlay for RGB video signal', 'unknown', 'unknown'],
    ["4.FRONTEND CENTERING>" , "Affects only to Emulation Station"],
    ["5.IN-GAME CENTERING>" , "Affects to all games"],
    ["6.240P TEST SUITE>" , "Tool suite for TV/Monitor calibration"],
    ["empty" , "empty"],
    ["empty" , "empty"],
    ["<BACK" , "Save and back to main menu"]]

def get_available_modes():
    global modes
    global MaxModes
    global SelectedMode
    global MaxModesCounter
    if os.path.exists(CompModesCFG):
        with open(CompModesCFG, 'r') as file:
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
                with open(CompModesCFG, 'r') as file:
                    for line in file:
                        line = line.strip().replace('=',' ').split(' ')
                        if line[0] == '%s_desc'%item[0]:
                            modes[counter][1] = " ".join(line).replace('%s_desc'%item[0],'').strip()
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
    with open(VideoUtilityCFG, 'r') as file:
        for line in file:
            line = line.strip().replace('=',' ').split(' ')
            if line[0] == "default":
                if line[1] == ES_Res_50hz:
                    opt[0][2] = '270p'
                    if opt[0][3] == 0:
                        opt[0][3] = '270p'
                elif line[1] == ES_Res_60hz:
                    opt[0][2] = '240p'
                    if opt[0][3] == 0:
                        opt[0][3] = '240p'
            elif line[0] == '240p_theme_horizontal':
                HorTheme240p = line[1]
            elif line[0] == '270p_theme_horizontal':
                HorTheme270p = line[1]
    get_output_video_mode()
    get_available_modes()
    if os.path.exists(EsSystemcfg):
        with open(EsSystemcfg, 'r') as file:
            for line in file:
                line = line.strip().replace('"','').replace(' ','').replace('/','').replace('>','').split('=')
                if 'ThemeSet' in line[1]:
                    CurTheme = line[2]

get_config()

def draw_menu():
    global option
    global opt
    global OutputModeChange
    global ResModeChange
    global SaveConfig
    global SaveModes
    # SHOW BACKGROUND
    pygame.draw.rect(fullscreen, BlueDark, (20,y_margin,x_screen-40,(20+(Interline*9)+3+16+10)), 0)

    #title and credits
    title = myfont.render("Configuration Utility", 1, BlueLight)
    fullscreen.blit(title, (32, y_margin+8))
    text_print("v3.0", x_screen-62, y_margin+8, 110, 110, 255, False)

    #last options
    #text_print('last rotation = ' + str(opt[4][3]), 0, 0, 255, 0, 0)
    #text_print('last ES resolution = ' + str(opt[6][3] ), 0, 8, 255, 0, 0)    
    
    #list square
    pygame.draw.rect(fullscreen, BlueLight, (32,y_margin+24,x_screen-62,Interline*9), 1)

    #list
    for i in range(0,9):
        option = y+y_slide
        if (i+y_slide <= 5 or i+y_slide == 8) and OutputModeChange == False and ResModeChange == False:
            opt[8][0] = '<BACK'
            opt[8][1] = 'Save and back to main menu'
            fullscreen.blit((myfont.render(opt[i+y_slide][0], 1, BlueLight)), (list_x, (30+y_margin+LineMov)+i*Interline))
        elif (i+y_slide <= 5 or i+y_slide == 8) and OutputModeChange == True:
            opt[8][0] = '<SHUTDOWN'
            opt[8][1] = 'Shudown the system and replace RGB connector'
            if i+y_slide == 2 or i+y_slide == 8:
                fullscreen.blit((myfont.render(opt[i+y_slide][0], 1, BlueLight)), (list_x, (30+y_margin+LineMov)+i*Interline))
            else:
                fullscreen.blit((myfont.render(opt[i+y_slide][0], 1, BlueUnselect)), (list_x, (30+y_margin+LineMov)+i*Interline))
        elif (i+y_slide <= 5 or i+y_slide == 8) and ResModeChange == True:
            opt[8][0] = '<RESTART'
            opt[8][1] = 'Restart ES to apply new resolution...'
            if i+y_slide == 0 or i+y_slide == 8:
                fullscreen.blit((myfont.render(opt[i+y_slide][0], 1, BlueLight)), (list_x, (30+y_margin+LineMov)+i*Interline))
            else:
                fullscreen.blit((myfont.render(opt[i+y_slide][0], 1, BlueUnselect)), (list_x, (30+y_margin+LineMov)+i*Interline))

    # data values
    for i in range(0,9):
        option = y+y_slide
        if (i < 3) and OutputModeChange == False and ResModeChange == False:
            esres = myfont.render(str(opt[i][2]), 1, BlueLight)
            fullscreen.blit(esres, (data_x-(len(str(opt[i][2]))*8), (30+y_margin+LineMov)+i*Interline))
        elif (i < 3) and OutputModeChange == True:
            if i == 2:
                mode = myfont.render(str(opt[i][2]), 1, BlueLight)
                fullscreen.blit(mode, (data_x-(len(str(opt[i][2]))*8), (30+y_margin+LineMov)+i*Interline))
            else:
                esres = myfont.render(str(opt[i][2]), 1, BlueUnselect)
                fullscreen.blit(esres, (data_x-(len(str(opt[i][2]))*8), (30+y_margin+LineMov)+i*Interline))
        elif (i < 3) and ResModeChange == True:
            if i == 0:
                mode = myfont.render(str(opt[i][2]), 1, BlueLight)
                fullscreen.blit(mode, (data_x-(len(str(opt[i][2]))*8), (30+y_margin+LineMov)+i*Interline))
            else:
                esres = myfont.render(str(opt[i][2]), 1, BlueUnselect)
                fullscreen.blit(esres, (data_x-(len(str(opt[i][2]))*8), (30+y_margin+LineMov)+i*Interline))


    # message if reboot is needed and deactivated options in red
    OutputModeChange = False
    ResModeChange = False
    SaveModes = False
    text_print('SYSTEM NEEDS TO SHUTDOWN NOW', 0, y_margin-13, 165, 165, 255, True)
    text_print('RESOLUTION WILL APPLY ON BACK/CENTERING', 0, y_margin-13, 165, 165, 255, True)
    text_print('FIX WILL APPLY ON BACK/CENTERING', 0, y_margin-13, 165, 165, 255, True)
    if opt[2][2] != opt[2][3]:
        OutputModeChange = True
        #opt[0][2] = opt[0][3]
        #opt[1][2] = opt[1][3]
        text_print('SYSTEM NEEDS TO SHUTDOWN NOW', 0, y_margin-13, 255, 0, 0, True)
    elif opt[0][2] != opt[0][3]:
        #opt[1][2] = opt[1][3]
        ResModeChange = True
        SaveConfig = True
        text_print('RESOLUTION WILL APPLY ON BACK/CENTERING', 0, y_margin-13, 255, 0, 0, True)
    elif opt[1][2] != opt[1][3]:
        SaveModes = True
        text_print('FIX WILL APPLY ON BACK/CENTERING', 0, y_margin-13, 255, 0, 0, True)

# list selection and square and arrows
    pygame.draw.rect(fullscreen, BlueLight, (32,(24+y_margin)+y*Interline,x_screen-62,Interline))
    fullscreen.blit((myfont.render(opt[option][0], 1, BlueDark)), (list_x, (30+y_margin+LineMov)+y*Interline))

    # data redraw
    if y == 0:
        esres = myfont.render(str(opt[0][2]), 1, BlueDark)
        fullscreen.blit(esres, (data_x-(len(str(opt[0][2]))*8), (30+y_margin+LineMov)+y*Interline))
        if opt[0][2] == '240p':
            draw_arrow_right()
        elif opt[0][2] == '270p':
            draw_arrow_left()
    elif y == 1:
        modres = myfont.render(str(opt[1][2]), 1, BlueDark)
        fullscreen.blit(modres, (data_x-(len(str(opt[1][2]))*8), (30+y_margin+LineMov)+y*Interline))
        if MaxModes != 0:
            if MaxModesCounter == 0:
                draw_arrow_right()
            elif MaxModesCounter < MaxModes:
                draw_arrow_left()
                draw_arrow_right()
            elif MaxModesCounter == MaxModes:
                draw_arrow_left()
    elif y == 2:
        VideoMode = myfont.render(str(opt[2][2]), 1, BlueDark)
        fullscreen.blit(VideoMode, (data_x-(len(str(opt[2][2]))*8), (30+y_margin+LineMov)+y*Interline))
        if opt[2][2] == 'RGB-Pi':
            draw_arrow_right()
            draw_arrow_left()
        elif opt[2][2] == 'VGA666':
            draw_arrow_right()
        elif opt[2][2] == 'PI2SCART':
            draw_arrow_left()

    # SHOW description on bootom in yellow and case
    info = str(opt[y+y_slide][1])
    if x_screen <= 340:
        info = info[0:28]
        if len(info) >= 28 :
            info = info + '...'
    else:
        info = info[0:44]
        if len(info) >= 44 :
            info = info + '...'
    fullscreen.blit((myfont.render(info, 1, (255,255,0))), (38, ((y_margin+23)+Interline*9)+4))
    pygame.draw.rect(fullscreen, BlueLight, (32,(y_margin+23)+Interline*9,x_screen-62,16), 1)
    pygame.display.flip()

draw_menu()
while True:
    for event in pygame.event.get():
        action = check_joy_event(event)
        #button
        if action == 'KEYBOARD' or action == 'JOYBUTTONB' or action == 'JOYBUTTONA':
            if y == 3 and OutputModeChange == False and ResModeChange == False:
                screen_center_utility_es()
            if y == 4 and OutputModeChange == False and ResModeChange == False:
                screen_center_utility_ingame()
            if y == 5 and OutputModeChange == False and ResModeChange == False:
                test_suite()
            if y == 8:
                pygame.quit()
                quit_manager()
                sys.exit()
        #right
        elif action == 'RIGTHKEYBOARD' or action == 'JOYHATRIGTH' or action == 'AXISRIGTH':
            if y == 0:
                if opt[0][2] == '240p':
                    opt[0][2] = '270p'
                    if opt[0][2] != opt[0][3]:
                        y = 8
            elif y == 1:
                if MaxModesCounter < MaxModes:
                    MaxModesCounter+=1
                    SelectedMode[0] = modes[MaxModesCounter][0]
                    SelectedMode[1] = modes[MaxModesCounter][1]
                    opt[1][2] = SelectedMode[0]
                    opt[1][1] = SelectedMode[1]
            elif y == 2:
                if opt[2][2] == 'VGA666':
                    opt[2][2] = 'RGB-Pi'
                elif opt[2][2] == 'RGB-Pi':
                    opt[2][2] = 'PI2SCART'
        #left
        elif action == 'LEFTKEYBOARD' or action == 'JOYHATLEFT' or action == 'AXISLEFT':
            if y == 0:
                if opt[0][2] == '270p':
                    opt[0][2] = '240p'
                    if opt[0][2] != opt[0][3]:
                        y = 8
            elif y == 1:
                if MaxModesCounter > 0:
                    MaxModesCounter-=1
                    SelectedMode[0] = modes[MaxModesCounter][0]
                    SelectedMode[1] = modes[MaxModesCounter][1]
                    opt[1][2] = SelectedMode[0]
                    opt[1][1] = SelectedMode[1]
            elif y == 2:
                if opt[2][2] == 'PI2SCART':
                    opt[2][2] = 'RGB-Pi'
                elif opt[2][2] == 'RGB-Pi':
                    opt[2][2] = 'VGA666'
        #up
        elif action == 'UPKEYBOARD' or action == 'JOYHATUP' or action == 'AXISUP':
            if OutputModeChange == True:
                if y == 8:
                    y = 2
            elif ResModeChange == True:
                if y == 8:
                    y = 0
            else:
                if y == 8:
                    y = 5
                elif y > 0:
                    y = y - 1
                elif y == 0:
                    y = 8
        #down
        elif action == 'DOWNKEYBOARD' or action == 'JOYHATDOWN' or action == 'AXISDOWN':
            if OutputModeChange == True:
                if y == 2:
                    y = 8
            elif ResModeChange == True:
                if y == 0:
                    y = 8
            else:
                if y == 5:
                    y = 8
                elif y < 8:
                    y = y + 1
                elif y == 8:
                    y = 0
    draw_menu()

