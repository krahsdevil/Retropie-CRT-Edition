#!/usr/bin/python
# coding: utf-8
#
# Coded by -krahS- (2019)
# Retropie Integration Port by -krahS-
#
# unlicense.org
#
# This script can be heavily optimized.

import struct
import os
import os.path
import sys
import shutil
import pygame
import time
import filecmp
import subprocess
from math import *
sys.path.append('/opt/retropie/configs/all/CRT/bin/SelectorsModule/')
sys.path.append('/opt/retropie/configs/all/CRT/bin/GeneralModule/')
sys.path.append('/opt/retropie/configs/all/CRT/')
from selector_module_functions import get_retropie_joy_map
from selector_module_functions import check_joy_event
from pygame.locals import *

os.system('clear')

try:
    argument = sys.argv[1]
except (IndexError):
    argument = 'none'

# VARIABLES
state_up = 0
state_down = 0
state_left = 0
state_right = 0
threshold = 1000 # Analogic middle to debounce
joystick = 0 # 0 is the 1sf joystick

x_screen = 0
x_screen_ui = 0
y_screen = 0
y_screen_ui = 0

y = 0

offsetX = 0
offsetY = 0
ConfOpt = 0
width = 0
height = 0
MAXWidth = 0
MAXHeight = 0
MAXoffsetX = 0
MAXoffsetY = 0
DefSystemRes = "none"
srchsystem = "none"
srchoffsetx = "none"
srchoffsety = "none"
srchwidth = "none"
srchheight = "none"
GameMask = []
GameMaskFound = False


VideoUtilityCFG = "/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/utility.cfg"
RaspbianCFG = "/boot/config.txt"
CompModesCFG = '/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/modes.cfg'

def draw_move_pattern(offsetX,offsetY,width):
    fullscreen.fill(black)
    patternPath = pygame.image.load('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/media/screen_center_utility_su_pattern.png')
    if x_screen_ui == 320:
        voverscan = 18
        boxoverscan = 7
    else:
        voverscan = 0
        boxoverscan = 0
    if y_screen_ui == 240:
        yoverscan = 16
    else:
        yoverscan = 0
    
    patternPath = pygame.transform.smoothscale(patternPath,(x_screen_ui-voverscan+(2*width),(y_screen_ui-yoverscan+(2*height))))
    patternPathPos = patternPath.get_rect()
    patternPathPos.center = (((x_screen/2)+offsetX), ((y_screen/2)+offsetY))
    fullscreen.blit(patternPath, patternPathPos)

    myfont = pygame.font.Font("/opt/retropie/configs/all/CRT/config/PetMe64.ttf", 8)
    
    
    pygame.draw.rect(fullscreen, Blue, (((x_screen/2)-150+boxoverscan),(y_screen-70-7-MAXoffsetY),(300-(boxoverscan*2)),57), 0)
    pygame.draw.rect(fullscreen, white, (((x_screen/2)-150+boxoverscan),(y_screen-70-7-MAXoffsetY),(300-(boxoverscan*2)),57), 1)
    pygame.draw.rect(fullscreen, white, (((x_screen/2)-150+boxoverscan),(y_screen-70-7-MAXoffsetY),(300-(boxoverscan*2)),17), 1)


    
    if abs(offsetX) == MAXoffsetX:
        myfontText = myfont.render(("Offset X:%s"%offsetX), True, red)
    else:
        myfontText = myfont.render(("Offset X:%s"%offsetX), True, white)
    myfontPos = myfontText.get_rect()
    myfontPos.midleft = ((x_screen/2)-135, (y_screen-83-7-MAXoffsetY)+22)
    fullscreen.blit(myfontText,myfontPos)

    if abs(offsetY) == MAXoffsetY:
        myfontText = myfont.render(("Offset Y:%s"%offsetY), True, red)
    else:
        myfontText = myfont.render(("Offset Y:%s"%offsetY), True, white)
    myfontPos = myfontText.get_rect()
    myfontPos.midleft = ((x_screen/2)-31, (y_screen-83-7-MAXoffsetY)+22)
    fullscreen.blit(myfontText,myfontPos)
    
    if ConfOpt == 1:
        if abs(width) == MAXWidth:
            myfontText = myfont.render(("Width:%s"%width), True, red)
        else:
            myfontText = myfont.render(("Width:%s"%width), True, white)
    elif ConfOpt == 2:
        if abs(width) == MAXHeight:
            myfontText = myfont.render(("Height:%s"%height), True, red)
        else:
            myfontText = myfont.render(("Height:%s"%height), True, white)
    else:
        myfontText = myfont.render(("H:%s|V:%s"%(width,height)), True, white)
            
    myfontPos = myfontText.get_rect()
    myfontPos.midleft = ((x_screen/2)+71, (y_screen-83-7-MAXoffsetY)+22)
    fullscreen.blit(myfontText,myfontPos)
    
    if ConfOpt == 0:
        myfontText = myfont.render(("PRESS ANY DIRECTION"), True, white)
    elif ConfOpt == 1:
        myfontText = myfont.render(("PRESS LEFTH/RIGHT"), True, white)
    elif ConfOpt == 2:
        myfontText = myfont.render(("PRESS UP/DOWN"), True, white)

    elif ConfOpt == 3 and y == 0:
        myfontText = myfont.render((">TRY AGAIN"), True, white)
    elif ConfOpt == 3 and y == 1:
        myfontText = myfont.render((" TRY AGAIN"), True, white)
    myfontPos = myfontText.get_rect()
    myfontPos.center = ((x_screen/2), (y_screen-83-7-MAXoffsetY)+40)
    fullscreen.blit(myfontText,myfontPos)
    
    if ConfOpt == 0:
        myfontText = myfont.render(("TO CENTER THE SCREEN"), True, white)
    elif ConfOpt == 1:
        myfontText = myfont.render(("TO CHANGE HORIZONTAL WIDTH"), True, white)
    elif ConfOpt == 2:
        myfontText = myfont.render(("TO CHANGE VERTICAL HEIGHT"), True, white)
        
    elif ConfOpt == 3 and y == 0:
        myfontText = myfont.render((" BACK     "), True, white)
    elif ConfOpt == 3 and y == 1:
        myfontText = myfont.render((">BACK     "), True, white)
    myfontPos = myfontText.get_rect()
    myfontPos.center = ((x_screen/2), (y_screen-83-7-MAXoffsetY)+50)
    fullscreen.blit(myfontText,myfontPos)

    if ConfOpt == 0:
        myfontText = myfont.render(("<Press any button to set>"), True, yellow)
    if ConfOpt == 1:
        myfontText = myfont.render(("<Press any button to set>"), True, yellow)
    if ConfOpt == 2:
        myfontText = myfont.render(("<Press any button to set>"), True, yellow)
    if ConfOpt == 3:
        myfontText = myfont.render(("<Select your option>"), True, yellow)
    myfontPos = myfontText.get_rect()
    myfontPos.center = ((x_screen/2), (y_screen-83-7-MAXoffsetY)+61)
    fullscreen.blit(myfontText,myfontPos)
    

    
    pygame.display.flip()

def modificarLinea(archivo,buscar,reemplazar):
    
    #Esta simple funcion cambia una linea entera de un archivo
    # Tiene que recibir el nombre del archivo, la cadena de la linea entera a
    # buscar, y la cadena a reemplazar si la linea coincide con buscar
    
    # This part remove a line
    if reemplazar == "":
        all_lines_moded = "none"
        with open(archivo, 'r') as file:
            for line in file:
                line = line.strip()
                if not buscar in line:
                    if all_lines_moded == "none":
                        all_lines_moded = "%s\n" %line
                    else:
                        all_lines_moded = "%s%s\n" % (all_lines_moded,line)
        with open(archivo, 'w') as file:
            file.write(all_lines_moded)
    else:
        # This one replace a line
        with open(archivo, "r") as f:
            # obtenemos las lineas del archivo en una lista
            lines = (line.rstrip() for line in f)
            # busca en cada linea si existe la cadena a buscar, y si la encuentra
            # la reemplaza
            altered_lines = [reemplazar if line.find(buscar) >= 0 else line for line in lines]
        with open(archivo, "w") as f:
            # guarda nuevamente todas las lineas en el archivo
            f.write('\n'.join(altered_lines) + '\n')

def quit_utility():
#Save and apply new resolution
    adjusted_timings = calculate_system_resolution_RAW(VideoUtilityCFG,srchsystem)
    save_boot_video_config(adjusted_timings)
    apply_system_resolution(RaspbianCFG,"hdmi_timings",True)
    pygame.display.quit()
    pygame.quit()
    sys.exit()

def get_mode():
    global GameMask
    global GameMaskFound
    if os.path.exists(CompModesCFG):
        with open(CompModesCFG, 'r') as file:
            for line in file:
                line = line.strip().replace('=',' ').split(' ')
                if line[0] == 'mode_default':
                    SelectedMode = line[1]
        if SelectedMode.lower() != 'default':
            with open(CompModesCFG, 'r') as file:
                for line in file:
                    mask = line.strip().replace('=',' ').split(' ')
                    if mask[0] == '%s_%s'%(SelectedMode,DefSystemRes):
                        GameMask.append (line.replace('%s_%s'%(SelectedMode,DefSystemRes),'').strip().split(' '))
                        GameMaskFound = True

def save_boot_video_config(adjusted_timings):
    os.system('cp %s /tmp/config.txt' % RaspbianCFG)
    modificarLinea("/tmp/config.txt","hdmi_timings=", adjusted_timings)
    os.system('sudo cp /tmp/config.txt %s' % RaspbianCFG)
    os.remove('/tmp/config.txt')
    #os.system('sudo reboot')
            
def calculate_system_resolution_RAW(CFGFile,resolution):
    # Final calculation after centering
    timings = "none"
    offsetX = 0
    offsetY = 0
    width = 0
    height = 0
    with open(CFGFile) as file:
        for line in file:
            line = line.strip().replace('=',' ').split(' ')
            if line[0] == resolution:
                timings = line
                # Get values from 'timings'
                t1 = int(timings[1])
                t2 = int(timings[2])
                t3 = int(timings[3])
                t4 = int(timings[4])
                t5 = int(timings[5])
                t6 = int(timings[6])
                t7 = int(timings[7])
                t8 = int(timings[8])
                t9 = int(timings[9])
                t10 = int(timings[10])
                t11 = int(timings[11])
                t12 = int(timings[12])
                t13 = int(timings[13])
                t14 = int(timings[14])
                t15 = int(timings[15])
                t16 = int(timings[16])
                t17 = int(timings[17])
            elif line[0] == srchoffsetx:
                offsetX = int(line[1])
            elif line[0] == srchoffsety:
                offsetY = int(line[1])
            elif line[0] == srchwidth:
                width = int(line[1])
            elif line[0] == srchheight:
                height = int(line[1])
    if GameMaskFound == True:
        t1 = int(t1)+int(GameMask[0][0])
        t2 = int(t2)+int(GameMask[0][1])
        t3 = int(t3)+int(GameMask[0][2])
        t4 = int(t4)+int(GameMask[0][3])
        t5 = int(t5)+int(GameMask[0][4])
        t6 = int(t6)+int(GameMask[0][5])
        t7 = int(t7)+int(GameMask[0][6])
        t8 = int(t8)+int(GameMask[0][7])
        t9 = int(t9)+int(GameMask[0][8])
        t10 = int(t10)+int(GameMask[0][9])
        t11 = int(t11)+int(GameMask[0][10])
        t12 = int(t12)+int(GameMask[0][11])
        t13 = int(t13)+int(GameMask[0][12])
        t14 = int(t14)+int(GameMask[0][13])
        t15 = int(t15)+int(GameMask[0][14])
        t16 = int(t16)+int(GameMask[0][15])
        t17 = int(t17)+int(GameMask[0][16])

    # width
    if width != 0:
        VMAX = (t6+t8+t10)-2
        HMAX = (t1+t3+t5)-2
        HZOOM = int(width)
        HZOOM_Normalized = HZOOM
        HZOOM_Normalized = int(round(HZOOM_Normalized,0))
        RectHZOOMT3 = 0
        RectHZOOMT5 = 0
        if not HZOOM_Normalized <= (t3-1):
            RectHZOOMT3 = t3-1
        if not HZOOM_Normalized <= (t5-1):
            RectHZOOMT5 = t5-1
        if RectHZOOMT3 != 0 and RectHZOOMT5 != 0:
            if RectHZOOMT3 < RectHZOOMT5:
                HZOOM_Normalized = RectHZOOMT3
            else:
                HZOOM_Normalized = RectHZOOMT5
        elif RectHZOOMT3 == 0 and RectHZOOMT5 != 0:
            HZOOM_Normalized = RectHZOOMT5
        elif RectHZOOMT3 != 0 and RectHZOOMT5 == 0:
            HZOOM_Normalized = RectHZOOMT3
        t1 = t1+(HZOOM_Normalized*2)
        Reverse_HZOOM = -1*HZOOM_Normalized
        t3 = t3+Reverse_HZOOM
        t5 = t5+Reverse_HZOOM

    if height != 0:
        VMAX = (t6+t8+t10)-2
        VZOOM = int(height)
        VZOOM_Normalized = VZOOM
        VZOOM_Normalized = int(round(VZOOM_Normalized,0))
        RectVZOOMT8 = 0
        RectVZOOMT10 = 0
        if not VZOOM_Normalized <= (t8-1):
            RectVZOOMT8 = t8-1
        if not VZOOM_Normalized <= (t10-1):
            RectVZOOMT10 = t10-1
        if RectVZOOMT8 != 0 and RectVZOOMT10 != 0:
            if RectVZOOMT8 < RectVZOOMT10:
                VZOOM_Normalized = RectVZOOMT8
            else:
                VZOOM_Normalized = RectVZOOMT8
        elif RectVZOOMT8 == 0 and RectVZOOMT10 != 0:
            VZOOM_Normalized = RectVZOOMT10
        elif RectVZOOMT8 != 0 and RectVZOOMT10 == 0:
            VZOOM_Normalized = RectVZOOMT8
        t6 = t6+(VZOOM_Normalized*2)
        Reverse_VZOOM = -1*VZOOM_Normalized
        t8 = t8+Reverse_VZOOM
        t10 = t10+Reverse_VZOOM

    # HORIZONTAL MOVEMENT
    if offsetX !=0:
        HMOV = int(offsetX)
        HMOV = HMOV/1
        HMOV = int(round(HMOV,0))
        if HMOV < 0 and (t5+HMOV) < 1:
            HMOV = -1*(t5-1)
        if HMOV > 0 and (t3-HMOV) < 1:
            HMOV = t3-1
        t3 = t3 - HMOV
        t5 = t5 + HMOV
    # VERTICAL MOVEMENT
    if offsetY !=0:
        VMOV = int(offsetY)
        VMOV = VMOV/1
        VMOV = int(round(VMOV,0))
        if VMOV < 0 and (t10+VMOV) < 1:
            VMOV = -1*(t10-1)
        if VMOV > 0 and (t8-VMOV) < 1:
            VMOV = t8-1
        t8 = t8 - VMOV
        t10 = t10 + VMOV
    
    adjusted_timings = "hdmi_timings=%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s"%(t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12,t13,t14,t15,t16,t17)
    return adjusted_timings

def apply_system_resolution(CFGFile,resolution,ESRestart):
    hdmi_timings = "none"
    with open(CFGFile, 'r') as file:
        for line in file:
            if resolution in line:
                timings = line.strip().replace('=',' ').split(' ')
                t1 = int(timings[1])
                t2 = int(timings[2])
                t3 = int(timings[3])
                t4 = int(timings[4])
                t5 = int(timings[5])
                t6 = int(timings[6])
                t7 = int(timings[7])
                t8 = int(timings[8])
                t9 = int(timings[9])
                t10 = int(timings[10])
                t11 = int(timings[11])
                t12 = int(timings[12])
                t13 = int(timings[13])
                t14 = float(timings[14])
                t15 = int(timings[15])
                t16 = int(timings[16])
                t17 = int(timings[17])
                hdmi_timings = "vcgencmd hdmi_timings %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s > /dev/null" % (t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12,t13,t14,t15,t16,t17)
    os.system(hdmi_timings)
    pygame.quit()
    os.system('fbset -depth 8 && fbset -depth 24')
    os.system('fbset -xres %s -yres %s'%(t1,t6))

def Find_Apply_Amplied_Res(CFGFile,ApplyRes):
    global x_screen_ui
    global y_screen_ui
    global x_screen
    global y_screen
    global MAXWidth
    global MAXHeight
    global MAXoffsetX
    global MAXoffsetY
    global offsetX
    global offsetY
    global width
    global height
    hdmi_timings = "none"
    with open(CFGFile, 'r') as file:
        for line in file:
            line = line.strip().replace('=',' ').split(' ')
            if line[0] == srchoffsetx:
                offsetX = int(line[1])
            elif line[0] == srchoffsety:
                offsetY = int(line[1])
            elif line[0] == srchwidth:
                width = int(line[1])
            elif line[0] == srchheight:
                height = int(line[1])
            elif line[0] == srchsystem:
                timings = line
                t1 = int(timings[1])
                t2 = int(timings[2])
                t3 = int(timings[3])
                t4 = int(timings[4])
                t5 = int(timings[5])
                t6 = int(timings[6])
                t7 = int(timings[7])
                t8 = int(timings[8])
                t9 = int(timings[9])
                t10 = int(timings[10])
                t11 = int(timings[11])
                t12 = int(timings[12])
                t13 = int(timings[13])
                t14 = float(timings[14])
                t15 = int(timings[15])
                t16 = int(timings[16])
                t17 = int(timings[17])
    if GameMaskFound == True:
        t1 = int(t1)+int(GameMask[0][0])
        t2 = int(t2)+int(GameMask[0][1])
        t3 = int(t3)+int(GameMask[0][2])
        t4 = int(t4)+int(GameMask[0][3])
        t5 = int(t5)+int(GameMask[0][4])
        t6 = int(t6)+int(GameMask[0][5])
        t7 = int(t7)+int(GameMask[0][6])
        t8 = int(t8)+int(GameMask[0][7])
        t9 = int(t9)+int(GameMask[0][8])
        t10 = int(t10)+int(GameMask[0][9])
        t11 = int(t11)+int(GameMask[0][10])
        t12 = int(t12)+int(GameMask[0][11])
        t13 = int(t13)+int(GameMask[0][12])
        t14 = float(t14)+float(GameMask[0][13])
        t15 = int(t15)+int(GameMask[0][14])
        t16 = int(t16)+int(GameMask[0][15])
        t17 = int(t17)+int(GameMask[0][16])
    x_screen_ui = int(t1)
    y_screen_ui = int(t6)
    
    if t5 > t3:
        MaxXFact = int(t3-1)
    else:
        MaxXFact = int(t5-1)
    MAXWidth = int(MaxXFact)
    MAXoffsetX = int(MaxXFact)

    if t10 > t8:
        MaxYFact = int(t8-1)
    else:
        MaxYFact = int(t10-1)
    MAXHeight = int(MaxYFact)
    MAXoffsetY = int(MaxYFact)
    
    t1 = int(t1+2*MaxXFact)
    t3 = int(t3-MaxXFact)
    t5 = int(t5-MaxXFact)
    t6 = int(t6+2*MaxYFact)
    t8 = int(t8-MaxYFact)
    t10 =int(t10-MaxYFact)
    
    x_screen = int(t1)
    y_screen = int(t6)
    
    hdmi_timings = "vcgencmd hdmi_timings %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s > /dev/null" % (t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12,t13,t14,t15,t16,t17)
    
    os.system(hdmi_timings)
    os.system('fbset -depth 8 && fbset -depth 24')
    os.system('fbset -xres %s -yres %s'%(t1,t6))

####################################################################
#                        MAIN PROGRAM                              #
####################################################################

with open(VideoUtilityCFG, 'r') as file:
    for line in file:
        line = line.strip().replace('=',' ').split(' ')
        if line[0] == 'default':
            DefSystemRes = line[1]
            srchsystem = DefSystemRes + '_timings'
            srchoffsetx = DefSystemRes + '_offsetX'
            srchoffsety = DefSystemRes + '_offsetY'
            srchwidth = DefSystemRes + '_width'
            srchheight = DefSystemRes + '_height'
get_mode()
Find_Apply_Amplied_Res(VideoUtilityCFG,True)

if argument == 'force':
    quit_utility()


pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
pygame.display.init()
pygame.mouse.set_visible(0)
get_retropie_joy_map()
red = pygame.Color(255, 0, 0)
black = pygame.Color(0, 0, 0)
white = pygame.Color(255,255,255)
yellow = pygame.Color(255,255,0)
Blue = pygame.Color(0,0,153)
BlueDark = pygame.Color(66,66,231)
BlueLight = pygame.Color(165,165,255)
BlueUnselect = pygame.Color(110,110,255)
fullscreen = pygame.display.set_mode((x_screen,y_screen), FULLSCREEN)
cursor = pygame.mixer.Sound("/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/media/screen_center_utility_cursor.wav")
load = pygame.mixer.Sound("/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/media/screen_center_utility_load.wav")
fullscreen.fill(black)

draw_move_pattern(offsetX,offsetY,width)
while True:
    for event in pygame.event.get():
        action = check_joy_event(event)
        #button
        if action == 'KEYBOARD' or action == 'JOYBUTTONB' or action == 'JOYBUTTONA':
            if ConfOpt == 0:
                load.play()
                ConfOpt += 1
                draw_move_pattern(offsetX,offsetY,width)
            elif ConfOpt == 1:
                load.play()
                ConfOpt += 1
                draw_move_pattern(offsetX,offsetY,width)
            elif ConfOpt == 2:
                load.play()
                ConfOpt += 1
                draw_move_pattern(offsetX,offsetY,width)
            elif ConfOpt == 3:
                if y == 0:
                    ConfOpt = 0
                    y = 0
                    load.play()
                    draw_move_pattern(offsetX,offsetY,width)
                elif y == 1:
                    modificarLinea(VideoUtilityCFG,srchoffsetx,"%s %s"%(srchoffsetx,offsetX))
                    modificarLinea(VideoUtilityCFG,srchoffsety,"%s %s"%(srchoffsety,offsetY))
                    modificarLinea(VideoUtilityCFG,srchwidth,"%s %s"%(srchwidth,width))
                    modificarLinea(VideoUtilityCFG,srchheight,"%s %s"%(srchheight,height))
                    quit_utility()
        #down
        elif action == 'DOWNKEYBOARD' or action == 'JOYHATDOWN' or action == 'AXISDOWN':
            if ConfOpt == 0:
                if offsetY < MAXoffsetY:
                    offsetY += 1
                    cursor.play()
                draw_move_pattern(offsetX,offsetY,width)
            if ConfOpt == 2:
                if height > -1*MAXHeight:
                    height -= 1
                    cursor.play()
                draw_move_pattern(offsetX,offsetY,width)
            if ConfOpt == 3:
                if y < 1:
                    y += 1
                    cursor.play()
                    draw_move_pattern(offsetX,offsetY,width)
        #up
        elif action == 'UPKEYBOARD' or action == 'JOYHATUP' or action == 'AXISUP':
            if ConfOpt == 0:
                if offsetY > -1*MAXoffsetY:
                    offsetY -= 1
                    cursor.play()
                draw_move_pattern(offsetX,offsetY,width)
            if ConfOpt == 2:
                if height < MAXHeight:
                    height += 1
                    cursor.play()
                draw_move_pattern(offsetX,offsetY,width)
            if ConfOpt == 3:
                if y > 0:
                    y -= 1
                    cursor.play()
                    draw_move_pattern(offsetX,offsetY,width)
        #right
        elif action == 'RIGTHKEYBOARD' or action == 'JOYHATRIGTH' or action == 'AXISRIGTH':
            if ConfOpt == 0:
                if offsetX < MAXoffsetX:
                    offsetX += 1
                    cursor.play()
                draw_move_pattern(offsetX,offsetY,width)
            if ConfOpt == 1:
                if width < MAXWidth:
                    width += 1
                    cursor.play()
                draw_move_pattern(offsetX,offsetY,width)
        #left
        elif action == 'LEFTKEYBOARD' or action == 'JOYHATLEFT' or action == 'AXISLEFT':
            if ConfOpt == 0:
                if offsetX > -1*MAXoffsetX:
                    offsetX -= 1
                    cursor.play()
                draw_move_pattern(offsetX,offsetY,width)
            if ConfOpt == 1:
                if width > -1*MAXWidth:
                    width -= 1
                    cursor.play()
                draw_move_pattern(offsetX,offsetY,width)


