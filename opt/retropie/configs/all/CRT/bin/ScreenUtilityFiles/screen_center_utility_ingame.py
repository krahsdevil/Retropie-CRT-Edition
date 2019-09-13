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

VTextResizer = 9
HTextResizer = 27
HInfoCenter = 0

VideoUtilityCFG = "/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/utility.cfg"
BaseSystemsTimings = "/opt/retropie/configs/all/CRT/Resolutions/base_systems.cfg"
CompModesCFG = '/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/modes.cfg'
RaspbianCFG = "/boot/config.txt"

def draw_move_pattern(offsetX,offsetY,width):
    fullscreen.fill(black)
    patternPath = pygame.image.load('/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/media/screen_center_utility_su_crosshatch.png')
    patternPath = pygame.transform.smoothscale(patternPath,((x_screen_ui+width+width)+(2*(width*2)),(y_screen_ui+(2*height))))
    patternPathPos = patternPath.get_rect()
    patternPathPos.center = (((x_screen/2)+(offsetX*4)-int(8-(width/2))), ((y_screen/2)+offsetY))
    fullscreen.blit(patternPath, patternPathPos)

    myfont = pygame.font.Font("/opt/retropie/configs/all/CRT/config/PetMe64.ttf", 8)
    
    pygame.draw.rect(fullscreen, Blue, (((x_screen/2)-500),(y_screen-75-7-MAXoffsetY),1000,57), 0)
    pygame.draw.rect(fullscreen, white, (((x_screen/2)-500),(y_screen-75-7-MAXoffsetY),1000,57), 1)
    pygame.draw.rect(fullscreen, white, (((x_screen/2)-500),(y_screen-75-7-MAXoffsetY),1000,17), 1)


    
    if abs(offsetX) == MAXoffsetX:
        text = "Offset X:%s"%offsetX
        myfontText = myfont.render(text, True, red)
    else:
        text = "Offset X:%s"%offsetX
        myfontText = myfont.render(text, True, white)
    textsize = len(text)
    textsize = int(textsize*HTextResizer)
    myfontText = pygame.transform.smoothscale(myfontText,(textsize,VTextResizer))
    myfontPos = myfontText.get_rect()
    myfontPos.midleft = ((x_screen/2)-450, (y_screen-88-7-MAXoffsetY)+22)
    fullscreen.blit(myfontText,myfontPos)

    if abs(offsetY) == MAXoffsetY:
        text = "Offset Y:%s"%offsetY
        myfontText = myfont.render(text, True, red)
    else:
        text = "Offset Y:%s"%offsetY
        myfontText = myfont.render(text, True, white)
    textsize = len(text)
    textsize = int(textsize*HTextResizer)
    myfontText = pygame.transform.smoothscale(myfontText,(textsize,VTextResizer))
    myfontPos = myfontText.get_rect()
    myfontPos.midleft = ((x_screen/2)-100, (y_screen-88-7-MAXoffsetY)+22)
    fullscreen.blit(myfontText,myfontPos)
    
    if ConfOpt == 1:
        if abs(width) == MAXWidth:
            text = "Width:%s"%width
            myfontText = myfont.render(text, True, red)
        else:
            text = "Width:%s"%width
            myfontText = myfont.render(text, True, white)
    elif ConfOpt == 2:
        if abs(width) == MAXHeight:
            text = "Blocked:%s"%height
            myfontText = myfont.render(text, True, red)
        else:
            text = "Blocked:%s"%height
            myfontText = myfont.render(text, True, white)
    else:
        text = "H:%s|V:%s"%(width,height)
        myfontText = myfont.render(text, True, white)
    textsize = len(text)
    textsize = int(textsize*HTextResizer)
    myfontText = pygame.transform.smoothscale(myfontText,(textsize,VTextResizer))
    myfontPos = myfontText.get_rect()
    myfontPos.midleft = ((x_screen/2)+230, (y_screen-88-7-MAXoffsetY)+22)
    fullscreen.blit(myfontText,myfontPos)
    
    if ConfOpt == 0:
        text = "PRESS ANY DIRECTION"
        myfontText = myfont.render(text, True, white)
    elif ConfOpt == 1:
        text = "PRESS LEFTH/RIGHT"
        myfontText = myfont.render(text, True, white)
    elif ConfOpt == 2:
        text = "PRESS UP/DOWN"
        myfontText = myfont.render(text, True, white)
    elif ConfOpt == 3 and y == 0:
        text = ">TRY AGAIN"
        myfontText = myfont.render(text, True, white)
    elif ConfOpt == 3 and y == 1:
        text = " TRY AGAIN"
        myfontText = myfont.render(text, True, white)
    textsize = len(text)
    textsize = int(textsize*HTextResizer)
    myfontText = pygame.transform.smoothscale(myfontText,(textsize,VTextResizer))
    myfontPos = myfontText.get_rect()
    myfontPos.center = ((x_screen/2), (y_screen-88-7-MAXoffsetY)+40)
    fullscreen.blit(myfontText,myfontPos)
    
    if ConfOpt == 0:
        text = "TO CENTER THE SCREEN"
        myfontText = myfont.render(text, True, white)
    elif ConfOpt == 1:
        text = "TO CHANGE HORIZONTAL WIDTH"
        myfontText = myfont.render(text, True, white)
    elif ConfOpt == 2:
        text = "TO CHANGE VERTICAL HEIGHT"
        myfontText = myfont.render(text, True, white)
    elif ConfOpt == 3 and y == 0:
        text = " BACK     "
        myfontText = myfont.render(text, True, white)
    elif ConfOpt == 3 and y == 1:
        text = ">BACK     "
        myfontText = myfont.render(text, True, white)
    textsize = len(text)
    textsize = int(textsize*HTextResizer)
    myfontText = pygame.transform.smoothscale(myfontText,(textsize,VTextResizer))
    myfontPos = myfontText.get_rect()
    myfontPos.center = ((x_screen/2), (y_screen-88-7-MAXoffsetY)+50)
    fullscreen.blit(myfontText,myfontPos)

    if ConfOpt == 0:
        text = "<Press any button to set>"
        myfontText = myfont.render(text, True, yellow)
    if ConfOpt == 1:
        text = "<Press any button to set>"
        myfontText = myfont.render(text, True, yellow)
    if ConfOpt == 2:
        text = "<Press any button to set>"
        myfontText = myfont.render(text, True, yellow)
    if ConfOpt == 3:
        text = "<Select your option>"
        myfontText = myfont.render(text, True, yellow)
    textsize = len(text)
    textsize = int(textsize*HTextResizer)
    myfontText = pygame.transform.smoothscale(myfontText,(textsize,VTextResizer))
    myfontPos = myfontText.get_rect()
    myfontPos.center = ((x_screen/2), (y_screen-88-7-MAXoffsetY)+61)
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
    apply_system_resolution(RaspbianCFG,"hdmi_timings",True)
    pygame.display.quit()
    pygame.quit()
    sys.exit()


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

def calculate_RAW_Resolution(H_Res, V_Res, R_Rate, H_Pos, H_Zoom, V_Pos, H_FP, H_Sync, H_BP, V_Sync, H_Freq):


    # H_Res   - Horizontal resolution (1600 to 1920)
    # V_Res   - (50Hz : 192 to 288) - (60Hz : 192 a 256)
    # R_Rate  - (47 a 62) MUST BE floating point.
    # H_Pos   - Horizontal position of the screen (-10 to 10)
    # H_Zoom  - Horizontal size of the screen (-40 to 10)
    # V_Pos   - Vertical position of the screen (-10 to 10) 
    # H_FP    - Horizontal Front Porch. Set to 48 if you don't know what you do.
    # H_Sync  - Horizontal Sync. Set to 192 if you don't know what you do.
    # H_BP    - Horizontal Back Porch. Set to 240 if you don't know what you do.
    # V_Sync  - Vertical Sync. (3 to 10 or more...)
    # H_Freq  - Horizontal frequency of the screen. (15500 to 16000)

    # WARNING, all these values are intrinsically linked. If your screen is desynchronized, quickly reboot the RPI.
    # Some values will be limited due to other values.

    
    # Scaling Front and back porch horizontals according to horizontal position and horizontal zoom settings.
    # H_Zoom*4 - H_Pos*4 MUST BE < to H_FP to not use negative value.
    # H_Zoom*4 + H_Pos*4 MUST BE < to H_BP to not use negative value.
    H_FP=H_FP-(H_Zoom*4)-(H_Pos*4)
    H_BP=H_BP-(H_Zoom*4)+(H_Pos*4)

    # Do not use negative values for H_FP and H_BP.
    if H_FP < 0 :
      H_FP = 0
    if H_BP < 0 :
      H_BP = 0

    # Total number of horizontal, visible and invisible pixels.
    H_Total=(H_Res+H_FP+H_Sync+H_BP)

    # Calculate the number of lines.
    V_Total=H_Freq/R_Rate
    # Round (up) the number of lines, if floating point.
    V_Total=int(ceil(V_Total))

    # Calculate of the horizontal frequency.
    Horizontal=V_Total*R_Rate
    # Round (up) the horizontal frequency.
    Horizontal=int(ceil(Horizontal))

    # Calculate of the pixel clock
    Pixel_Clock=Horizontal*H_Total

    # Calculate of the Vertical Front Porch.
    V_FP=V_Total-V_Res
    V_FP=V_FP-V_Sync
    V_FP=V_FP/2
    # Round (down) the Vertical Front Porch.
    V_FP=int(floor(V_FP))
    

    # Vertical Position MUSTN'T be bigger than Vertical Front Porch.
    if V_Pos > V_FP :
      V_Pos = V_FP
  
    # Calculate Vertical Front Porch.
    V_FP=V_FP-V_Pos

    # Calculate Vertical Back Porch.
    V_BP=V_Total-V_Res
    V_BP=V_BP-V_Sync
    V_BP=int(V_BP-V_FP)

    # Generate vcgencmd command line in a string.
    hdmi_timings = "raw %s 1 %s %s %s %s 1 %s %s %s 0 0 0 %s 0 %s 1" % (H_Res,H_FP,H_Sync,H_BP,V_Res,V_FP,V_Sync,V_BP,R_Rate,Pixel_Clock)
    return hdmi_timings

def Find_Apply_Amplied_Res_RAW(CFGFile,CFGFile2,ApplyRes):
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
    MaxXFact = 100
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
                # Get values from 'timings'
                H_Res = int(timings[1])
                V_Res = int(timings[2])
                R_Rate = float(timings[3])
                H_Pos = int(timings[4])
                H_Zoom = int(timings[5])
                V_Pos = int(timings[6])
                H_FP = int(timings[7])
                H_Sync = int(timings[8])
                H_BP = int(timings[9])
                V_Sync = int(timings[10])
                H_Freq = int(timings[11])
                
    if os.path.exists(CFGFile2):
        with open(CFGFile2, 'r') as file:
            for line in file:
                line = line.strip().replace('=',' ').split(' ')
                if line[0] == 'mode_default':
                    SelectedMode = line[1]
        if SelectedMode.lower() != 'default':
            with open(CFGFile2, 'r') as file:
                for line in file:
                    mask = line.strip().replace('=',' ').split(' ')
                    if mask[0] == '%s_game_mask'%SelectedMode:
                        GameMask = line.replace('%s_game_mask'%SelectedMode,'').strip().split(' ')
            GameMask[0] = int((int(H_Res)-(int(MaxXFact)*2)*int(GameMask[0]))/int(H_Res))
            GameMask[6] = int(ceil(((int(H_FP)-8)*int(GameMask[6]))/int(H_FP)))
            GameMask[7] = int(ceil(((int(H_Sync)-24)*int(GameMask[7]))/int(H_Sync)))+1
            GameMask[8] = int(ceil(((int(H_BP)-32)*int(GameMask[8]))/int(H_BP)))
            H_Res = int(H_Res)+int(GameMask[0])
            V_Res = int(V_Res)+int(GameMask[1])
            R_Rate = float(R_Rate)+float(GameMask[2])
            H_Pos = int(H_Pos)+int(GameMask[3])
            H_Zoom = int(H_Zoom)+int(GameMask[4])
            V_Pos = int(V_Pos)+int(GameMask[5])
            H_FP = int(H_FP)+int(GameMask[6])
            H_Sync = int(H_Sync)+int(GameMask[7])
            H_BP = int(H_BP)+int(GameMask[8])
            V_Sync = int(V_Sync)+int(GameMask[9])
            H_Freq = int(H_Freq)+int(GameMask[10])
    #os.system('echo %s %s %s %s %s %s %s %s %s %s %s >> /tmp/prob.txt'%(H_Res,V_Res,R_Rate,H_Pos,H_Zoom,V_Pos,H_FP,H_Sync,H_BP,V_Sync,H_Freq))

    x_screen = H_Res
    y_screen = V_Res
    x_screen_ui = 1820
    y_screen_ui = int(V_Res)

    os.system('echo %s %s %s %s %s %s %s %s %s %s %s >> /tmp/prob.txt'%(H_Res,V_Res,R_Rate,H_Pos,H_Zoom,V_Pos,H_FP,H_Sync,H_BP,V_Sync,H_Freq))

    # Open Screen Function
    RAW_hdmi_timings = calculate_RAW_Resolution(H_Res, V_Res, R_Rate, H_Pos, H_Zoom, V_Pos, H_FP, H_Sync, H_BP, V_Sync, H_Freq)
    timings = RAW_hdmi_timings.split(' ')
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
    
    if t10 > t8:
        MaxYFact = int(t8-1)
    else:
        MaxYFact = int(t10-1)
    
    MAXWidth = int(MaxXFact/4)
    MAXoffsetX = int(MaxXFact/4)
    MAXHeight = 0
    MAXoffsetY = int(MaxYFact)
    
    t6 = int(t6+2*MaxYFact)
    t8 = int(t8-MaxYFact)
    t10 =int(t10-MaxYFact)

    hdmi_timings = "vcgencmd hdmi_timings %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s > /dev/null" % (t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12,t13,t14,t15,t16,t17)
    os.system('echo %s >> /tmp/prob.txt' % hdmi_timings)
    os.system(hdmi_timings)
    os.system('fbset -depth 8 && fbset -depth 24')
    os.system('fbset -xres %s -yres %s'%(t1,t6))

####################################################################
#                        MAIN PROGRAM                              #
####################################################################

DefSystemRes = 'test'
srchsystem = 'test60_timings'
srchoffsetx = 'test60_offsetX'
srchoffsety = 'test60_offsetY'
srchwidth = 'test60_width'
srchheight = 'test60_height'

Find_Apply_Amplied_Res_RAW(VideoUtilityCFG,CompModesCFG,True)
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

