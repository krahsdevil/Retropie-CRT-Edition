# Original idea/coded by Ironic/aTg (2017) for RGB-Pi recalbox
# Retropie code/integration by -krahs- (2018)

# unlicense.org

import os
from math import *

CompModesCFG = '/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/modes.cfg'
VideoUtilityCFG = "/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/utility.cfg"

def crt_open_screen(H_Res, V_Res, R_Rate, H_Pos, H_Zoom, V_Pos, H_FP, H_Sync, H_BP, V_Sync, H_Freq):
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
    hdmi_timings = "vcgencmd hdmi_timings %s 1 %s %s %s %s 1 %s %s %s 0 0 0 %s 0 %s 1 > /dev/null" % (H_Res,H_FP,H_Sync,H_BP,V_Res,V_FP,V_Sync,V_BP,R_Rate,Pixel_Clock)
    os.system(hdmi_timings)
    os.system("fbset -depth 8 && fbset -depth 24")


def crt_open_screen_from_timings_cfg(emulator,timings_full_path):
    # Read Timings Config File and get current emulator timings
    timings = "none"
    with open(timings_full_path) as file:
        for line in file:
            line = line.strip().split(' ')

            if line[0] == emulator:
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
                    if mask[0] == '%s_game_mask'%SelectedMode:
                        GameMask = line.replace('%s_game_mask'%SelectedMode,'').strip().split(' ')
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

    # Read data from Screen Utility
    srchoffsetx = 'test60_offsetX'
    srchoffsety = 'test60_offsetY'
    srchwidth = 'test60_width'
    with open(VideoUtilityCFG, 'r') as file:
        for line in file:
            line = line.strip().replace('=',' ').split(' ')
            if line[0] == srchoffsetx:
                H_Pos += int(line[1])
            elif line[0] == srchoffsety:
                V_Pos += int(line[1])
            elif line[0] == srchwidth:
                H_Zoom += int(line[1])

    # Open Screen Function
    crt_open_screen(H_Res, V_Res, R_Rate, H_Pos, H_Zoom, V_Pos, H_FP, H_Sync, H_BP, V_Sync, H_Freq)


def crt_open_screen_raw(emulator,timings_full_path):

    # Read Timings Config File and get current emulator timings
    timings = "none"
    with open(timings_full_path) as file:
        for line in file:
            line = line.strip().split(' ')

            if line[0] == emulator:
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
                t14 = float(timings[14])
                t15 = int(timings[15])
                t16 = int(timings[16])
                t17 = int(timings[17])

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
                    if mask[0] == '%s_game_mask_raw'%SelectedMode:
                        GameMask = line.replace('%s_game_mask_raw'%SelectedMode,'').strip().split(' ')
            t1 = int(t1)+int(GameMask[0])
            t2 = int(t2)+int(GameMask[1])
            t3 = int(t3)+int(GameMask[2])
            t4 = int(t4)+int(GameMask[3])
            t5 = int(t5)+int(GameMask[4])
            t6 = int(t6)+int(GameMask[5])
            t7 = int(t7)+int(GameMask[6])
            t8 = int(t8)+int(GameMask[7])
            t9 = int(t9)+int(GameMask[8])
            t10 = int(t10)+int(GameMask[9])
            t11 = int(t11)+int(GameMask[10])
            t12 = int(t12)+int(GameMask[11])
            t13 = int(t13)+int(GameMask[12])
            t14 = float(t14)+float(GameMask[13])
            t15 = int(t15)+int(GameMask[14])
            t16 = int(t16)+int(GameMask[15])
            t17 = int(t17)+int(GameMask[16])
    #os.system("echo %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s >> /tmp/br.txt" % (t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12,t13,t14,t15,t16,t17))
    hdmi_timings = "vcgencmd hdmi_timings %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s > /dev/null" % (t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12,t13,t14,t15,t16,t17)

    # Execute command lines.
    os.system(hdmi_timings)
    os.system("fbset -depth 8 && fbset -depth 24")

def crt_open_screen_raw_with_adjustement(emulator,timings_full_path):

    # Read Timings Config File and get current emulator timings
    timings = "none"
    with open(timings_full_path) as file:
        for line in file:
            line = line.strip().split(' ')

            if line[0] == emulator:
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
                t14 = float(timings[14])
                t15 = int(timings[15])
                t16 = int(timings[16])
                t17 = int(timings[17])

    # Read data from Screen Utility
    srchoffsetx = 'test60_offsetX'
    srchoffsety = 'test60_offsetY'
    srchwidth = 'test60_width'
    with open(VideoUtilityCFG, 'r') as file:
        for line in file:
            line = line.strip().replace('=',' ').split(' ')
            if line[0] == srchoffsetx:
                HMOV = int(line[1])
            elif line[0] == srchoffsety:
                VMOV = int(line[1])
            elif line[0] == srchwidth:
                HZOOM = int(line[1])

    if HZOOM != 0:
        VMAX = (t6+t8+t10)-2
        HMAX = (t1+t3+t5)-2
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
    # HORIZONTAL MOVEMENT
    if HMOV !=0:
        HMOV = HMOV/1
        HMOV = int(round(HMOV,0))
        if HMOV < 0 and (t5+HMOV) < 1:
            HMOV = -1*(t5-1)
        if HMOV > 0 and (t3-HMOV) < 1:
            HMOV = t3-1
        t3 = t3 - HMOV
        t5 = t5 + HMOV
    # VERTICAL MOVEMENT
    if VMOV !=0:
        VMOV = VMOV/1
        VMOV = int(round(VMOV,0))
        if VMOV < 0 and (t10+VMOV) < 1:
            VMOV = -1*(t10-1)
        if VMOV > 0 and (t8-VMOV) < 1:
            VMOV = t8-1
        t8 = t8 - VMOV
        t10 = t10 + VMOV


    hdmi_timings = "vcgencmd hdmi_timings %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s > /dev/null" % (t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12,t13,t14,t15,t16,t17)

    # Execute command lines.
    os.system(hdmi_timings)
    os.system("fbset -depth 8 && fbset -depth 24")
    #os.system('fbset -xres %s -yres %s'%(t1,t6))
    # Exit if no emulator timings found in 'timings.cfg'


def es_restore_screen():
    with open('/boot/config.txt', 'r') as file:
        for line in file:
            line = line.strip().replace('=',' ').split(' ')
            if line[0] == 'hdmi_timings':
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

    hdmitimings = "vcgencmd hdmi_timings %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s > /dev/null" % (t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12,t13,t14,t15,t16,t17)
    os.system(hdmitimings)
    os.system("fbset -depth 8 && fbset -depth 24") # necesario para el cambio de modo

