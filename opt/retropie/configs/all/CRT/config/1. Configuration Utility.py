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
import filecmp
import sys
import os
import commands
import subprocess
sys.path.append('/opt/retropie/configs/all/CRT/bin/GeneralModule/')
sys.path.append('/opt/retropie/configs/all/CRT/')
from pygame.locals import *
from general_functions import *
from selector_module_functions import get_retropie_joy_map
from selector_module_functions import check_joy_event

os.system('clear')

ServiceRunning = False
ServiceExist = False
x_screen = 0
y_screen = 0
x_margin = 0
y_margin = 0
MarginNorm = 0.1482
Interline = 0
LineMov = 0
SystemRes = '240p'
ES_Res_50hz = 'system50'
ES_Res_60hz = 'system60'
CurTheme = "none"
VerTheme = "V270P-CRT-BASE"
HorTheme = "270P-CRT-BASE"
#positions and arrows color
data_x = 0
list_x = 0
arrow_c = [255,255,0]


ES_Restart = False
RotateFrontEnd = False

def get_xy_screen():
    global x_screen
    global y_screen
    global x_margin
    global y_margin
    global Interline
    global LineMov
    global data_x
    global list_x
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

# INITS
get_xy_screen()
pygame.init()
pygame.mouse.set_visible(0)
get_retropie_joy_map()

# VARIABLES
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


#files
JoyAutoconfigPath = "/opt/retropie/configs/all/retroarch/autoconfig/"
VideoUtilityCFG = "/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/config_files/utility.cfg"
EsSystemcfg = "/opt/retropie/configs/all/emulationstation/es_settings.cfg"
MusicPath = "/opt/retropie/configs/music"

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

def draw_arrow_left(add_space=0):
    fullscreen.blit((myfont.render('<<', 1, (arrow_c))), (data_x-(len(str(opt[option][2]))*8)-18-(8*add_space), (30+y_margin+LineMov)+y*Interline))

def draw_arrow_right():
    fullscreen.blit((myfont.render('>>', 1, (arrow_c))), (data_x+2, (30+y_margin+LineMov)+y*Interline))

def save():
#definition of the output format: h size, h pos, v pos, rotate games, rotate system, last state of rotate system, stretch portables, emulationstation resolution, last emulationtstation resolution state.

    modificarLinea(VideoUtilityCFG,'game_rotation','game_rotation %s'%opt[0][2])
    modificarLinea(VideoUtilityCFG,'frontend_rotation','frontend_rotation %s'%opt[1][2])
    modificarLinea(VideoUtilityCFG,'handheld_bezel','handheld_bezel %s'%opt[2][2])
    modificarLinea(VideoUtilityCFG,'freq_selector','freq_selector %s'%opt[3][2])
    modificarLinea(VideoUtilityCFG,'integer_scale','integer_scale %s'%opt[6][2])
def Check_BackGround_Music():
    global opt
    global ServiceRunning
    global ServiceExist
    if not os.path.exists(MusicPath):
        os.makedirs(MusicPath)
        os.system('touch \"%s/place your background music here.txt\"' % MusicPath)
    CheckService = commands.getoutput('systemctl list-units --all | grep \"BackGroundMusic.service\"')
    if 'BackGroundMusic.service' in CheckService:
        ServiceExist = True
        if 'running' in CheckService:
            ServiceRunning = True
            opt[5][2] = "YES"
        else:
            ServiceRunning = False
            opt[5][2] = "OFF"
    else:
        ServiceExist = False
        ServiceRunning = False
        opt[5][2] = "OFF"
def InstallServiceBackGroundMusic():
    global ServiceRunning
    global ServiceExist
    if ServiceExist == False:
        if os.path.exists('/opt/retropie/configs/all/CRT/bin/BackGroundMusic/BackGroundMusic.service') and os.path.exists('/opt/retropie/configs/all/CRT/bin/BackGroundMusic/BGM.py'):
            os.system('sudo cp /opt/retropie/configs/all/CRT/bin/BackGroundMusic/BackGroundMusic.service /etc/systemd/system/ > /dev/null 2>&1')
    os.system('sudo systemctl enable BackGroundMusic.service > /dev/null 2>&1')
    os.system('sudo systemctl start BackGroundMusic.service > /dev/null 2>&1')
    Check_BackGround_Music()

def DesInstallServiceBackGroundMusic():
    if os.path.exists('/opt/retropie/configs/all/CRT/bin/BackGroundMusic/BackGroundMusic.service') and os.path.exists('/opt/retropie/configs/all/CRT/bin/BackGroundMusic/BGM.py'):
        os.system('sudo systemctl stop BackGroundMusic.service > /dev/null 2>&1')
        os.system('sudo systemctl disable BackGroundMusic.service > /dev/null 2>&1')
    Check_BackGround_Music()
def rotate_frontend():
    if RotateFrontEnd == True:
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
            modificarLinea(EsSystemcfg, '"ThemeSet"', '<string name="ThemeSet" value="%s" />'%HorTheme)
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
            modificarLinea(EsSystemcfg, '"ThemeSet"', '<string name="ThemeSet" value="%s" />'%VerTheme)
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
            modificarLinea(EsSystemcfg, '"ThemeSet"', '<string name="ThemeSet" value="%s" />'%VerTheme)

def quit_utility():
    pygame.quit()
    save()
    if RotateFrontEnd == True:
        rotate_frontend()
        # Restart ES if it is running
        output = commands.getoutput('ps -A')
        if 'emulationstatio' in output:
            os.system('touch /tmp/es-restart && pkill -f \"/opt/retropie/supplementary/.*/emulationstation([^.]|$)\"')
            sys.exit()
    sys.exit()

def video_config():
    save()
    #crt_open_screen_raw('test',timings_full_path)
    pygame.quit()
    commandline = "/usr/bin/python /opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/bin/module_screen_tools_manager/screen_tools_manager.py"
    os.system(commandline)
    #es_restore_screen()
    get_xy_screen()
    get_config()
    os.execl(sys.executable, sys.executable, *sys.argv)


# SET SCREEN
fullscreen = pygame.display.set_mode((x_screen,y_screen), FULLSCREEN)
fullscreen.fill((165,165,255))    

# FONT
myfont = pygame.font.Font("/opt/retropie/configs/all/CRT/config/PetMe64.ttf", 8)

# loading data from su.cfg
opt = [["1.GAMES ROTATION" , "Not PixelPerfect but playable on AdvMAME" , 0],
    ["2.FRONTEND ROTATION" , "This option requires rotate your monitor" , 0, 0],
    ["3.HANDHELD BEZELS" , "CAUTION!!! Long use can damage the screen" , 0],
    ["4.FREQUENCY SELECTOR" , "Set Frequency at 50/60hz, Auto or Manual" , 0],
    ["5.VIDEO CONFIG>" , "Advanced Video Configuration"],
    ['6.BACKGROUND MUSIC' , 'Play your music with emulationstation', 0],
    ['7.INTEGER SCALE' , 'ONLY for LibRetro Arcade and NEOGEO Games', 0],
    ['none' , 'none'],
    ["<EXIT" , "Save and Exit"]]

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
    if not os.path.exists(VideoUtilityCFG):
        DefVideoUtilityCFG = "default system50\nsystem60_timings 450 1 44 26 100 270 1 16 5 22 0 0 0 50 0 9600000 1\nsystem60_offsetX 0\nsystem60_offsetY 0\nsystem60_width 0\nsystem60_height 0\nsystem50_timings 450 1 50 32 94 270 1 12 5 26 0 0 0 50 0 9600000 1\nsystem50_offsetX 0\nsystem50_offsetY 0\nsystem50_width 0\nsystem50_height 0\ntest60_timings 1920 240 60.00 -4 -27 3 48 192 240 5 15734\ntest60_offsetX 0\ntest60_offsetY 0\ntest60_width 0\ntest60_height 0\ngame_rotation 0\nfrontend_rotation 0\nhandheld_bezel 0\nfreq_selector 0\n240p_theme_vertical V270P-CRT-BASE\n270p_theme_vertical V270P-CRT-BASE\n240p_theme_horizontal 240P-CRT-BUBBLEGUM\n270p_theme_horizontal 270P-CRT-BASE"
        os.system('echo %s > %s'%(DefVideoUtilityCFG,VideoUtilityCFG))
    with open(VideoUtilityCFG, 'r') as file:
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
        opt[1][2] = 90
        opt[1][3] = 90
        opt[0][2] = 0
        modificarLinea(VideoUtilityCFG, '%s_theme_vertical '%SystemRes, '%s_theme_vertical %s'%(SystemRes, CurTheme))
    elif os.path.exists('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/configs/es-select-tate3'):
        opt[1][2] = -90
        opt[1][3] = -90
        opt[0][2] = 0
        modificarLinea(VideoUtilityCFG, '%s_theme_vertical '%SystemRes, '%s_theme_vertical %s'%(SystemRes, CurTheme))
    elif os.path.exists('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/configs/es-select-yoko'):
        opt[1][2] = 0
        opt[1][3] = 0
        modificarLinea(VideoUtilityCFG, '%s_theme_horizontal '%SystemRes, '%s_theme_horizontal %s'%(SystemRes, CurTheme))
    else:
        opt[1][2] = 0
        opt[1][3] = 0
        modificarLinea(VideoUtilityCFG, '%s_theme_horizontal '%SystemRes, '%s_theme_horizontal %s'%(SystemRes, CurTheme))
    Check_BackGround_Music()



get_config()
# starting the main loop

def draw_menu():
    global option
    global opt
    global RotateFrontEnd
    # SHOW BACKGROUND
    pygame.draw.rect(fullscreen, (66,66,231), (20,y_margin,x_screen-40,(20+(Interline*9)+3+16+10)), 0)

    #title and credits
    title = myfont.render("Configuration Utility", 1, (165,165,255))
    fullscreen.blit(title, (32, y_margin+8))
    text_print("v3.1", x_screen-62, y_margin+8, 110, 110, 255, False)

    #last options
    #text_print('last rotation = ' + str(opt[4][3]), 0, 0, 255, 0, 0)
    #text_print('last ES resolution = ' + str(opt[6][3] ), 0, 8, 255, 0, 0)    
    
    #list square
    pygame.draw.rect(fullscreen, (165,165,255), (32,y_margin+24,x_screen-62,Interline*9), 1)

    #list
    for i in range(0,9):
        option = y+y_slide
        if (i+y_slide <= 6 or i+y_slide == 8) and RotateFrontEnd == False:
            opt[8][0] = '<EXIT'
            opt[8][1] = 'Save and Exit'
            fullscreen.blit((myfont.render(opt[i+y_slide][0], 1, (165,165,255))), (list_x, (30+y_margin+LineMov)+i*Interline))
        elif (i+y_slide <= 6 or i+y_slide == 8) and RotateFrontEnd == True:
            opt[8][0] = '<RESTART'
            opt[8][1] = 'Restart FrontEnd for TATE Mode'
            if i+y_slide == 1 or i+y_slide == 8:
                fullscreen.blit((myfont.render(opt[i+y_slide][0], 1, (165,165,255))), (list_x, (30+y_margin+LineMov)+i*Interline))
            else:
                fullscreen.blit((myfont.render(opt[i+y_slide][0], 1, (110,110,255))), (list_x, (30+y_margin+LineMov)+i*Interline))
    

    # data values
    
    for i in range(0,9):
        option = y+y_slide
        if RotateFrontEnd == False:
            if i == 0:
                if opt[0][2] == 0:
                    select = myfont.render("OFF", 1, (165,165,255))
                    fullscreen.blit(select, (data_x-(len("OFF")*8), (30+y_margin+LineMov)+i*Interline))
                else:
                    select = myfont.render(str(opt[i][2]), 1, (165,165,255))
                    fullscreen.blit(select, (data_x-(len(str(opt[i][2]))*8), (30+y_margin+LineMov)+i*Interline))
            elif i == 1:
                if opt[1][2] == 0:
                    select = myfont.render("OFF", 1, (165,165,255))
                    fullscreen.blit(select, (data_x-(len("OFF")*8), (30+y_margin+LineMov)+i*Interline))
            elif i == 2:
                if opt[2][2] == 0:
                    select = myfont.render("OFF", 1, (165,165,255))
                    fullscreen.blit(select, (data_x-(len("OFF")*8), (30+y_margin+LineMov)+i*Interline))
                elif opt[2][2] == 1:
                    select = myfont.render("YES", 1, (165,165,255))
                    fullscreen.blit(select, (data_x-(len("YES")*8), (30+y_margin+LineMov)+i*Interline))
            elif i == 3:
                if opt[3][2] == 0:
                    select = myfont.render("MAN", 1, (165,165,255))
                    fullscreen.blit(select, (data_x-(len("MAN")*8), (30+y_margin+LineMov)+i*Interline))
                elif opt[3][2] == 100:
                    select = myfont.render("AUT", 1, (165,165,255))
                    fullscreen.blit(select, (data_x-(len("AUT")*8), (30+y_margin+LineMov)+i*Interline))
                else:
                    select = myfont.render(str(opt[3][2]), 1, (165,165,255))
                    fullscreen.blit(select, (data_x-(len(str(opt[3][2]))*8), (30+y_margin+LineMov)+i*Interline))
            elif i == 6:
                if opt[6][2] == 0:
                    select = myfont.render("OFF", 1, (165,165,255))
                    fullscreen.blit(select, (data_x-(len("OFF")*8), (30+y_margin+LineMov)+i*Interline))
                elif opt[6][2] == 1:
                    select = myfont.render("YES", 1, (165,165,255))
                    fullscreen.blit(select, (data_x-(len("YES")*8), (30+y_margin+LineMov)+i*Interline))
            elif i < 3 or i == 5:
                strpor = myfont.render(str(opt[i][2]), 1, (165,165,255))
                fullscreen.blit(strpor, (data_x-(len(str(opt[i][2]))*8), (30+y_margin+LineMov)+i*Interline))

        else:
            if i == 0:
                if opt[0][2] == 0:
                    select = myfont.render("OFF", 1, (110,110,255))
                    fullscreen.blit(select, (data_x-(len("OFF")*8), (30+y_margin+LineMov)+i*Interline))
            elif i == 1:
                strpor = myfont.render(str(opt[i][2]), 1, (165,165,255))
                fullscreen.blit(strpor, (data_x-(len(str(opt[i][2]))*8), (30+y_margin+LineMov)+i*Interline))
            elif i == 2:
                if opt[2][2] == 0:
                    select = myfont.render("OFF", 1, (110,110,255))
                    fullscreen.blit(select, (data_x-(len("OFF")*8), (30+y_margin+LineMov)+i*Interline))
                elif opt[2][2] == 1:
                    select = myfont.render("YES", 1, (110,110,255))
                    fullscreen.blit(select, (data_x-(len("YES")*8), (30+y_margin+LineMov)+i*Interline))
            elif i == 3:
                if opt[3][2] == 0:
                    select = myfont.render("MAN", 1, (110,110,255))
                    fullscreen.blit(select, (data_x-(len("MAN")*8), (30+y_margin+LineMov)+i*Interline))
                elif opt[3][2] == 100:
                    select = myfont.render("AUT", 1, (110,110,255))
                    fullscreen.blit(select, (data_x-(len("AUT")*8), (30+y_margin+LineMov)+i*Interline))
                else:
                    select = myfont.render(str(opt[3][2]), 1, (110,110,255))
                    fullscreen.blit(select, (data_x-(len(str(opt[3][2]))*8), (30+y_margin+LineMov)+i*Interline))
            elif i == 6:
                if opt[6][2] == 0:
                    select = myfont.render("OFF", 1, (110,110,255))
                    fullscreen.blit(select, (data_x-(len("OFF")*8), (30+y_margin+LineMov)+i*Interline))
                elif opt[6][2] == 1:
                    select = myfont.render("YES", 1, (110,110,255))
                    fullscreen.blit(select, (data_x-(len("YES")*8), (30+y_margin+LineMov)+i*Interline))
            elif i < 3 or i == 5:
                strpor = myfont.render(str(opt[i][2]), 1, (110,110,255))
                fullscreen.blit(strpor, (data_x-(len(str(opt[i][2]))*8), (30+y_margin+LineMov)+i*Interline))

    # message if reboot is needed and deactivated options in red
    text_print('EMULATIONSTATION NEEDS TO RESTART NOW', 0, y_margin-13, 165, 165, 255, True)
    RotateFrontEnd = False
    if opt[1][2] != opt[1][3]:
        RotateFrontEnd = True
        text_print('EMULATIONSTATION NEEDS TO RESTART NOW', 0, y_margin-13, 255, 0, 0, True)
        if opt[1][2] != 0:
            opt[0][2] = 0

# list selection and square and arrows
    pygame.draw.rect(fullscreen, (165,165,255), (32,(24+y_margin)+y*Interline,x_screen-62,Interline))
    fullscreen.blit((myfont.render(opt[option][0], 1, (66,66,231))), (list_x, (30+y_margin+LineMov)+y*Interline))

    # data redraw
    if y < 4 or y == 5 or y == 6:
        if opt[0][2] == 0 and y == 0:
            listrndr = myfont.render("OFF", 1, (66,66,231))
            fullscreen.blit(listrndr, (data_x-(len("OFF")*8), (30+y_margin+LineMov)+y*Interline))
        elif opt[1][2] == 0 and y == 1:
            listrndr = myfont.render("OFF", 1, (66,66,231))
            fullscreen.blit(listrndr, (data_x-(len("OFF")*8), (30+y_margin+LineMov)+y*Interline))
        elif opt[2][2] == 0 and y == 2:
            listrndr = myfont.render("OFF", 1, (66,66,231))
            fullscreen.blit(listrndr, (data_x-(len("OFF")*8), (30+y_margin+LineMov)+y*Interline))
        elif opt[2][2] == 1 and y == 2:
            listrndr = myfont.render("YES", 1, (66,66,231))
            fullscreen.blit(listrndr, (data_x-(len("YES")*8), (30+y_margin+LineMov)+y*Interline))
        elif opt[3][2] == 0 and y == 3:
            listrndr = myfont.render("MAN", 1, (66,66,231))
            fullscreen.blit(listrndr, (data_x-(len("MAN")*8), (30+y_margin+LineMov)+y*Interline))
        elif opt[3][2] == 100 and y == 3:
            listrndr = myfont.render("AUT", 1, (66,66,231))
            fullscreen.blit(listrndr, (data_x-(len("AUT")*8), (30+y_margin+LineMov)+y*Interline))
        elif opt[6][2] == 0 and y == 6:
            listrndr = myfont.render("OFF", 1, (66,66,231))
            fullscreen.blit(listrndr, (data_x-(len("OFF")*8), (30+y_margin+LineMov)+y*Interline))
        elif opt[6][2] == 1 and y == 6:
            listrndr = myfont.render("YES", 1, (66,66,231))
            fullscreen.blit(listrndr, (data_x-(len("YES")*8), (30+y_margin+LineMov)+y*Interline))
        else:
            listrndr = myfont.render(str(opt[option][2]), 1, (66,66,231))
            fullscreen.blit(listrndr, (data_x-(len(str(opt[option][2]))*8), (30+y_margin+LineMov)+y*Interline))

    #option 1
    if y == 0 and opt[0][2] < 0:
        draw_arrow_right()
    elif y == 0 and opt[0][2] == 0 and opt[1][2] == 0:
        draw_arrow_left(2)
    #elif y == 0 and opt[1][2] != 0:
    #    fullscreen.blit((myfont.render(opt[option][0], 1, (136,136,255))), (list_x, (30+y_margin+LineMov)+y*Interline))

    #option 2
    if y == 1 and opt[1][2] < 0:
        draw_arrow_right()
    elif y == 1 and opt[1][2] == 0:
        draw_arrow_right()
        draw_arrow_left(2)
    elif y == 1 and opt[1][2] > 0:
        draw_arrow_left()

    #option 3
    if y == 2:
        if opt[2][2] == 1:
            draw_arrow_left(2)
        else:
            draw_arrow_right()

    #option 4
    if y == 3:
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
    #option 6
    if y == 5:
        if opt[5][2] == "YES":
            draw_arrow_left()
        elif opt[5][2] == "OFF":
            draw_arrow_right()

    #option 7
    if y == 6:
        if opt[6][2] == 1:
            draw_arrow_left(2)
        elif opt[6][2] == 0:
            draw_arrow_right()

    #option 8
    if y == 7 and opt[1][2] != opt[1][3]:
        fullscreen.blit((myfont.render(opt[option][0], 1, (136,136,255))), (110, (30+y_margin+LineMov)+y*Interline))

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
    pygame.draw.rect(fullscreen, (165,165,255), (32,(y_margin+23)+Interline*9,x_screen-62,16), 1)
    pygame.display.flip()


draw_menu()
while True:
    for event in pygame.event.get():
        action = check_joy_event(event)
        #button
        if action == 'KEYBOARD' or action == 'JOYBUTTONB' or action == 'JOYBUTTONA':
            if y == 4:
                video_config()
            elif y < 3:
                opt[option][2] = 0
            elif y == 8:
                quit_utility()
                sys.exit()
        #right
        elif action == 'RIGTHKEYBOARD' or action == 'JOYHATRIGTH' or action == 'AXISRIGTH':
            if y == 0 and opt[0][2] < 0 and opt[1][2] == 0:
                opt[0][2] += 90
            elif y == 1 and opt[1][2] < 90:
                opt[1][2] += 90
                opt[0][2] = 0
            elif y == 2 and opt[2][2] == 0:
                opt[2][2] = 1
            elif y == 3 and opt[3][2] == 0:
                opt[3][2] = 50
            elif y == 3 and opt[3][2] == 50:
                opt[3][2] = 60
            elif y == 3 and opt[3][2] == 60:
                opt[3][2] = 100
            elif y == 5 and opt[5][2] == "OFF":
                InstallServiceBackGroundMusic()
            elif y == 6 and opt[6][2] == 0:
                opt[6][2] = 1
        #left
        elif action == 'LEFTKEYBOARD' or action == 'JOYHATLEFT' or action == 'AXISLEFT':
            if y == 0 and opt[0][2] > -90 and opt[1][2] == 0:
                opt[0][2] -= 90
            elif y == 1 and opt[1][2] > -90:
                opt[1][2] -= 90
                opt[0][2] = 0
            elif y == 2 and opt[2][2] == 1:
                opt[2][2] = 0
            elif y == 3 and opt[3][2] == 100:
                opt[3][2] = 60
            elif y == 3 and opt[3][2] == 60:
                opt[3][2] = 50
            elif y == 3 and opt[3][2] == 50:
                opt[3][2] = 0
            elif y == 5 and opt[5][2] == "YES":
                DesInstallServiceBackGroundMusic()
            elif y == 6 and opt[6][2] == 1:
                opt[6][2] = 0
        #up            
        elif action == 'UPKEYBOARD' or action == 'JOYHATUP' or action == 'AXISUP':
            if RotateFrontEnd == True:
                if y == 8:
                    y = 1
            else:
                if y == 0:
                    y = 8
                elif y == 8:
                    y = 6
                elif y > 0:
                    y = y - 1
        #down
        elif action == 'DOWNKEYBOARD' or action == 'JOYHATDOWN' or action == 'AXISDOWN':
            if RotateFrontEnd == True:
                if y == 1:
                    y = 8
            else:
                if y == 6:
                    y = 8
                elif y == 8:
                    y = 0
                elif y < 8:
                    y = y + 1
    draw_menu()
