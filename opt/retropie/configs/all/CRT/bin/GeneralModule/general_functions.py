# Original idea/coded by Ironic/aTg (2017) for RGB-Pi recalbox
# Retropie code/integration by -krahs- (2018)

# unlicense.org


import os
import os.path
import sys
import shutil
import time
import re
import hashlib
import commands
import subprocess
import logging
import xml.etree.ElementTree as ET

from math import *

import os, struct, array
from fcntl import ioctl

sys.path.append('/opt/retropie/configs/all/CRT/bin/SelectorsModule/')
sys.path.append('/opt/retropie/configs/all/CRT/bin/GeneralModule/')
sys.path.append('/opt/retropie/configs/all/CRT/')

CompModesCFG = '/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/modes.cfg'
VideoUtilityCFG = "/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/utility.cfg"

#logging.basicConfig(filename="/tmp/CRT_Launcher.log", level=logging.INFO, format='%(asctime)s %(message)s')

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
	#os.system('fbset -xres %s -yres %s'%(H_Res,V_Res))

def es_restore_screen():

	#with open('/boot/config.txt', 'r') as f:
	#	hdmitimings = f.readline()
	#hdmitimings = hdmitimings[:12] + ' ' + hdmitimings[13:]
	#hdmitimings = hdmitimings.strip()
	#hdmitimings = "vcgencmd " + hdmitimings + " > /dev/null"
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
	os.system("fbset -depth 8 && fbset -depth 24")
	#os.system('fbset -xres %s -yres %s'%(t1,t6))

def launch_joy2key(left, right, up, down, a, b, x, y, start, select):
    # get the first joystick device (if not already set)
	JOY2KEY_DEV = "none"
	JOY2KEY_PATH = "/opt/retropie/configs/all/CRT/bin/VideoPlayer/joy2key.py"
	JOY2KEY_VAR = commands.getoutput('$__joy2key_dev')
	if os.path.exists (JOY2KEY_VAR):
		JOY2KEY_DEV = JOY2KEY_VAR
	else:
		JOY2KEY_DEV = "/dev/input/jsX"
	output = commands.getoutput('ps -A')
	if os.path.exists (JOY2KEY_PATH) and JOY2KEY_DEV != "none" and not 'joy2key.py' in output:
		joy2key_command = "\"%s\" \"%s\" %s %s %s %s %s %s %s %s %s %s" % (JOY2KEY_PATH,JOY2KEY_DEV,left, right,up,down,a,b,x,y,start,select)
		process = subprocess.Popen(joy2key_command, shell=True)
		return process

def splash():

	if 'vga666' in open('/boot/config.txt').read():
		os.system("/opt/retropie/configs/all/CRT/Datas/splash.sh & sleep 23")

	elif not 'dpi_output_format=6' in open('/boot/config.txt').read():
		os.system("/opt/retropie/configs/all/CRT/Datas/splash.sh & sleep 23")

def something_is_bad(infos,infos2):

#	infos = "It's a try !!!"
	time.sleep(2)
	problem = "/opt/retropie/configs/all/CRT/Datas/problem.sh \"%s\" \"%s\"" % (infos, infos2)
	os.system(problem)
	#sys.exit()

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

			
	# Exit if no emulator timings found in 'timings.cfg'
	if timings == "none":
		infos = "[%s] isn't in 'timings.cfg'" % emulator
		infos2 = ""
		something_is_bad(infos,infos2)
		sys.exit()

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
	#os.system('fbset -xres %s -yres %s'%(t1,t6))
	# Exit if no emulator timings found in 'timings.cfg'
	if timings == "none":
		infos = "[%s] isn't in 'timings.cfg'" % emulator
		infos2 = ""
		something_is_bad(infos,infos2)
		sys.exit()

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
	if timings == "none":
		infos = "[%s] isn't in 'timings.cfg'" % emulator
		infos2 = ""
		something_is_bad(infos,infos2)
		sys.exit()

def joystick_button_check():

	# Released by rdb under the Unlicense (unlicense.org)
	# Based on information from:
	# https://www.kernel.org/doc/Documentation/input/joystick-api.txt

	# We'll store the states here.
	axis_states = {}
	button_states = {}

	# These constants were borrowed from linux/input.h
	axis_names = {
	    0x00 : 'x',
	    0x01 : 'y',
	    0x02 : 'z',
	    0x03 : 'rx',
	    0x04 : 'ry',
	    0x05 : 'rz',
	    0x06 : 'trottle',
	    0x07 : 'rudder',
	    0x08 : 'wheel',
	    0x09 : 'gas',
	    0x0a : 'brake',
	    0x10 : 'hat0x',
	    0x11 : 'hat0y',
	    0x12 : 'hat1x',
	    0x13 : 'hat1y',
	    0x14 : 'hat2x',
	    0x15 : 'hat2y',
	    0x16 : 'hat3x',
	    0x17 : 'hat3y',
	    0x18 : 'pressure',
	    0x19 : 'distance',
	    0x1a : 'tilt_x',
	    0x1b : 'tilt_y',
	    0x1c : 'tool_width',
	    0x20 : 'volume',
	    0x28 : 'misc',
	}

	button_names = {
	    0x120 : 'trigger',
	    0x121 : 'thumb',
	    0x122 : 'thumb2',
	    0x123 : 'top',
	    0x124 : 'top2',
	    0x125 : 'pinkie',
	    0x126 : 'base',
	    0x127 : 'base2',
	    0x128 : 'base3',
	    0x129 : 'base4',
	    0x12a : 'base5',
	    0x12b : 'base6',
	    0x12f : 'dead',
	    0x130 : 'a',
	    0x131 : 'b',
	    0x132 : 'c',
	    0x133 : 'x',
	    0x134 : 'y',
	    0x135 : 'z',
	    0x136 : 'tl',
	    0x137 : 'tr',
	    0x138 : 'tl2',
	    0x139 : 'tr2',
	    0x13a : 'select',
	    0x13b : 'start',
	    0x13c : 'mode',
	    0x13d : 'thumbl',
	    0x13e : 'thumbr',

	    0x220 : 'dpad_up',
	    0x221 : 'dpad_down',
	    0x222 : 'dpad_left',
	    0x223 : 'dpad_right',

	    # XBox 360 controller uses these codes.
	    0x2c0 : 'dpad_left',
	    0x2c1 : 'dpad_right',
	    0x2c2 : 'dpad_up',
	    0x2c3 : 'dpad_down',
	}

	axis_map = []
	button_map = []

	# Open the joystick device.
	fn = '/dev/input/js0'
	print('Opening %s...' % fn)
	jsdev = open(fn, 'rb')



	# Get number of axes and buttons.
	buf = array.array('B', [0])
	ioctl(jsdev, 0x80016a11, buf) # JSIOCGAXES
	num_axes = buf[0]

	buf = array.array('B', [0])
	ioctl(jsdev, 0x80016a12, buf) # JSIOCGBUTTONS
	num_buttons = buf[0]

	# Get the axis map.
	buf = array.array('B', [0] * 0x40)
	ioctl(jsdev, 0x80406a32, buf) # JSIOCGAXMAP

	for axis in buf[:num_axes]:
	    axis_name = axis_names.get(axis, 'unknown(0x%02x)' % axis)
	    axis_map.append(axis_name)
	    axis_states[axis_name] = 0.0

	# Get the button map.
	buf = array.array('H', [0] * 200)
	ioctl(jsdev, 0x80406a34, buf) # JSIOCGBTNMAP

	for btn in buf[:num_buttons]:
	    btn_name = button_names.get(btn, 'unknown(0x%03x)' % btn)
	    button_map.append(btn_name)
	    button_states[btn_name] = 0

	print '%d axes found: %s' % (num_axes, ', '.join(axis_map))
	print '%d buttons found: %s' % (num_buttons, ', '.join(button_map))

	# Main event loop
	#while True:
	evbuf = jsdev.read(8)
	if evbuf:
	    time, value, type, number = struct.unpack('IhBB', evbuf)


	    if type & 0x01:
	        button = button_map[number]
	        if button:
	            button_states[button] = value
	            if value:
	                print "%s pressed" % (button)
	                return 1
	            else:
	                print "%s released" % (button)
	                return 0



def replace_line(file_name, line_num, text):
	lines = open(file_name, 'r').readlines()
	lines[line_num-1] = text # Line start at '1' array ta '0'
	out = open(file_name, 'w')
	out.writelines(lines)
	out.close()



def make_retroarcharcade_configfile(datas1,datas2,offsetx,offsety,datas3,datas13):

					
	#Copy retroarcharcade.cfg to /tmp
	shutil.copy2('/opt/retropie/configs/all/CRT/Retroarch/configs/retroarcharcade.cfg', '/tmp')
	# Add parameters to retroarcharcade.cfg
	with open('/tmp/retroarcharcade.cfg', 'a') as file:
		param = "custom_viewport_width = \"%s\"\n" % (datas1)
		file.writelines(param)
		param = "custom_viewport_height = \"%s\"\n" % (datas2)
		file.writelines(param)
		param = "custom_viewport_x = \"%s\"\n" % (offsetx)
		file.writelines(param)
		param = "custom_viewport_y = \"%s\"\n" % (offsety)
		file.writelines(param)
		param = "video_refresh_rate = \"%s\"\n" % (datas3)
		file.writelines(param)
		# Check game orientation

		if datas13 == "H":
			param = "video_rotation = \"%s\"\n" % ("0")
			file.writelines(param)
		elif datas13 == "V3":
			param = "video_rotation = \"%s\"\n" % ("3")
			file.writelines(param)
		elif datas13 == "V1":
			param = "video_rotation = \"%s\"\n" % ("1")
			file.writelines(param)

			#param = "input_player1_up_axis = \"%s\"\n" % ("+0")
			#file.writelines(param)
			#param = "input_player1_down_axis = \"%s\"\n" % ("-0")
			#file.writelines(param)
			#param = "input_player1_left_axis = \"%s\"\n" % ("-1")
			#file.writelines(param)
			#param = "input_player1_right_axis = \"%s\"\n" % ("+1")
			#file.writelines(param)
			#param = "input_player2_up_axis = \"%s\"\n" % ("+0")
			#file.writelines(param)
			#param = "input_player2_down_axis = \"%s\"\n" % ("-0")
			#file.writelines(param)
			#param = "input_player2_left_axis = \"%s\"\n" % ("-1")
			#file.writelines(param)
			#param = "input_player2_right_axis = \"%s\"\n" % ("+1")
			#file.writelines(param)

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
			if all_lines_moded == "none":
				file.write('')
			else:
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

def check_custom_emulator_per_game(emulator,game_name,custom_emulator_file):
	##############################################################################
	# RETROPIE allows to choice per game an specific emulator from available.    #
	# By default emulator per game is saved at:                                  #
	# /opt/retropie/configs/all/emulators.cfg                                    #
	# This function will return (if exist) information of a custom emulator for  #
	# an especific game in order to check if it's compatible                     #
	##############################################################################
	game_name = re.sub('[^a-zA-Z0-9-_]+','', game_name )
	CleanedGame = re.sub(' ','', game_name )
	EmGam_mix = "%s_%s" % (emulator,CleanedGame)
	Pref_Core = "none"
	if os.path.exists(custom_emulator_file):
		with open(custom_emulator_file, 'r') as file:
			for line in file:
				linecheck = line.strip().split(' ')
				line = line.strip()
				if linecheck[0] == EmGam_mix:
					Pref_Core = linecheck[2]
					break
	CustEmuGame = [EmGam_mix,Pref_Core]
	return CustEmuGame

def Check_SystemCore_SpecialConfig(system,core,customconfigfile):
	core = core.strip('"')
	ConfigFileName = os.path.basename(customconfigfile)
	ConfigFileName = ConfigFileName[:-4]
	if system == "megadrive":
		if "genesis" in core and "plus" in core and not "50" in ConfigFileName:
			modificarLinea(customconfigfile,"custom_viewport_width","custom_viewport_width = \"2088\"")
			modificarLinea(customconfigfile,"custom_viewport_height","custom_viewport_height = \"240\"")
			modificarLinea(customconfigfile,"custom_viewport_x","custom_viewport_x = \"-67\"")
			modificarLinea(customconfigfile,"custom_viewport_y","custom_viewport_y = \"0\"")
		elif "genesis" in core and "plus" in core and "50" in ConfigFileName:
			modificarLinea(customconfigfile,"custom_viewport_width","custom_viewport_width = \"2088\"")
			modificarLinea(customconfigfile,"custom_viewport_height","custom_viewport_height = \"288\"")
			modificarLinea(customconfigfile,"custom_viewport_x","custom_viewport_x = \"-68\"")
			modificarLinea(customconfigfile,"custom_viewport_y","custom_viewport_y = \"2\"")
		elif "picodrive" in core and not "50" in ConfigFileName:
			modificarLinea(customconfigfile,"custom_viewport_width","custom_viewport_width = \"1920\"")
			modificarLinea(customconfigfile,"custom_viewport_height","custom_viewport_height = \"224\"")
			modificarLinea(customconfigfile,"custom_viewport_x","custom_viewport_x = \"-3\"")
			modificarLinea(customconfigfile,"custom_viewport_y","custom_viewport_y = \"7\"")
		elif "picodrive" in core and "50" in ConfigFileName:
			modificarLinea(customconfigfile,"custom_viewport_width","custom_viewport_width = \"1920\"")
			modificarLinea(customconfigfile,"custom_viewport_height","custom_viewport_height = \"224\"")
			modificarLinea(customconfigfile,"custom_viewport_x","custom_viewport_x = \"15\"")
			modificarLinea(customconfigfile,"custom_viewport_y","custom_viewport_y = \"33\"")
		else:
			if not "50" in ConfigFileName:
				modificarLinea(customconfigfile,"custom_viewport_width","custom_viewport_width = \"2088\"")
				modificarLinea(customconfigfile,"custom_viewport_height","custom_viewport_height = \"240\"")
				modificarLinea(customconfigfile,"custom_viewport_x","custom_viewport_x = \"-67\"")
				modificarLinea(customconfigfile,"custom_viewport_y","custom_viewport_y = \"0\"")
			if "50" in ConfigFileName:
				modificarLinea(customconfigfile,"custom_viewport_width","custom_viewport_width = \"2088\"")
				modificarLinea(customconfigfile,"custom_viewport_height","custom_viewport_height = \"288\"")
				modificarLinea(customconfigfile,"custom_viewport_x","custom_viewport_x = \"-68\"")
				modificarLinea(customconfigfile,"custom_viewport_y","custom_viewport_y = \"2\"")
	if system == "mastersystem":
		if "genesis" in core and "plus" in core and not "50" in ConfigFileName:
			modificarLinea(customconfigfile,"custom_viewport_width","custom_viewport_width = \"1988\"")
			modificarLinea(customconfigfile,"custom_viewport_height","custom_viewport_height = \"240\"")
			modificarLinea(customconfigfile,"custom_viewport_x","custom_viewport_x = \"-37\"")
			modificarLinea(customconfigfile,"custom_viewport_y","custom_viewport_y = \"0\"")
		elif "genesis" in core and "plus" in core and "50" in ConfigFileName:
			modificarLinea(customconfigfile,"custom_viewport_width","custom_viewport_width = \"1988\"")
			modificarLinea(customconfigfile,"custom_viewport_height","custom_viewport_height = \"288\"")
			modificarLinea(customconfigfile,"custom_viewport_x","custom_viewport_x = \"-29\"")
			modificarLinea(customconfigfile,"custom_viewport_y","custom_viewport_y = \"2\"")
		elif "picodrive" in core and not "50" in ConfigFileName:
			modificarLinea(customconfigfile,"custom_viewport_width","custom_viewport_width = \"1792\"")
			modificarLinea(customconfigfile,"custom_viewport_height","custom_viewport_height = \"192\"")
			modificarLinea(customconfigfile,"custom_viewport_x","custom_viewport_x = \"60\"")
			modificarLinea(customconfigfile,"custom_viewport_y","custom_viewport_y = \"24\"")
		elif "picodrive" in core and "50" in ConfigFileName:
			modificarLinea(customconfigfile,"custom_viewport_width","custom_viewport_width = \"1536\"")
			modificarLinea(customconfigfile,"custom_viewport_height","custom_viewport_height = \"192\"")
			modificarLinea(customconfigfile,"custom_viewport_x","custom_viewport_x = \"192\"")
			modificarLinea(customconfigfile,"custom_viewport_y","custom_viewport_y = \"50\"")
		else:
			if not "50" in ConfigFileName:
				modificarLinea(customconfigfile,"custom_viewport_width","custom_viewport_width = \"1988\"")
				modificarLinea(customconfigfile,"custom_viewport_height","custom_viewport_height = \"240\"")
				modificarLinea(customconfigfile,"custom_viewport_x","custom_viewport_x = \"-37\"")
				modificarLinea(customconfigfile,"custom_viewport_y","custom_viewport_y = \"0\"")
			if "50" in ConfigFileName:
				modificarLinea(customconfigfile,"custom_viewport_width","custom_viewport_width = \"1988\"")
				modificarLinea(customconfigfile,"custom_viewport_height","custom_viewport_height = \"288\"")
				modificarLinea(customconfigfile,"custom_viewport_x","custom_viewport_x = \"-29\"")
				modificarLinea(customconfigfile,"custom_viewport_y","custom_viewport_y = \"2\"")
def change_retropie_runcommand_emulator_init(easynet,emulator,emulatorcfg,pathemulatorcfg,game_name):
	logging.info("INICIANDO FUNCION: change_retropie_runcommand_emulator_init")
	# ARCADE DATABASES
	mame037b5DB = "/opt/retropie/configs/all/CRT/Resolutions/mame037b5_games.txt"
	mame078DB = "/opt/retropie/configs/all/CRT/Resolutions/mame078_games.txt"
	mame0139DB = "/opt/retropie/configs/all/CRT/Resolutions/mame0139_games.txt"
	fbalphaDB = "/opt/retropie/configs/all/CRT/Resolutions/fbalpha_games.txt"
	advmameDB = "/opt/retropie/configs/all/CRT/Resolutions/advmame_games.txt"
	amigaDB = "/opt/retropie/configs/all/CRT/Resolutions/amiga_games.txt"
	returnedDB = ["none","none"]
	################################################################################################
	# ADVMAME PATHS AND INFO                                                                       #
	# VARIABLE CONTAINS:                                                                           #
	#   0) True or False if detected or not in emulators.cfg                                       #
	#   1) Full path to advmame's binary                                                           #
	#   2) Quoted name recognized on RETROPIE                                                      #
	#   3) Full path and file of advmame config file                                               #
	################################################################################################
	advmame = [False, "/opt/retropie/emulators/advmame/bin/advmame", "\"advmame\"", "/opt/retropie/configs/mame-advmame/advmame.rc"] 
	# advmame_valid, True or False: if finds any advmame compatible emulator instaled, "none": Emulator found
	advmame_valid = [False, "none"]
	
	################################################################################################
	# AMIGA PATHS AND INFO                                                                         #
	# VARIABLE CONTAINS:                                                                           #
	#   0) True or False if detected amiberry or not in emulators.cfg                              #
	#   1) First amiga emulator supported: amiberry (Quoted name recognized on RETROPIE)           #
	#   2) True or False if detected lr-puae or not in emulators.cfg                               #
	#   3) Second amiga emulator supported: lr-puae (Quoted name recognized on RETROPIE)           #
	################################################################################################
	amiga = [False, "amiberry", False, "lr-puae"] 
	# amiga_valid, True or False: if finds any amiga compatible emulator instaled, "none": Emulator found
	amiga_valid = [False, "none"]
	################################################################################################
	# SCUMMVM PATHS AND INFO                                                                       #
	# VARIABLE CONTAINS:                                                                           #
	#   0) True or False if detected scummvm (standard) or not in emulators.cfg                    #
	#   1) First scummvm emulator supported: scummvm (Quoted name recognized on RETROPIE)          #
	#   2) True or False if detected scummvm-sdl1 (SDL1) or not in emulators.cfg                   #
	#   3) Second scummvm emulator supported: scummvm-sdl1 (Quoted name recognized on RETROPIE)    #
	################################################################################################
	scummvm = [False, "scummvm", False, "scummvm-sdl1"] 
	# scummvm_valid, True or False: if finds any scummvm compatible emulator instaled, "none": Emulator found
	scummvm_valid = [False, "none"]
	################################################################################################
	# DOSBOX PATHS AND INFO                                                                        #
	# VARIABLE CONTAINS:                                                                           #
	#   0) True or False if detected dosbox (standard) or not in emulators.cfg                     #
	#   1) First dosbox emulator supported: dosbox                                                 #
	################################################################################################
	dosbox = [False, "dosbox"] 
	# scummvm_valid, True or False: if finds any scummvm compatible emulator instaled, "none": Emulator found
	dosbox_valid = [False, "none"]

	# default_valid, True or False: if finds any libretro core, "none": Emulator found
	default_valid = [False, "none"]	

	coreid = "none"
	corefile = "none"
	corepath = "none"
	retropiecommand = "none"
	cfgfilepath = "/opt/retropie/configs/%s/emulators.cfg" % emulator
	custom_emulator_file = "/opt/retropie/configs/all/emulators.cfg"
	addcfgpath = "%s%s.cfg" % (pathemulatorcfg,emulatorcfg)
	found_Lr_core = False

	all_lines_moded = "none"
	default_moded = "none"
	check_changes = 0
	logging.info("INFO: Buscando archivo %s en el sistema" % cfgfilepath)
	if not os.path.isfile(cfgfilepath):
		logging.info("ERROR: No se ha encontrado el archivo %s en el sistema" % cfgfilepath)
		infos = "Can't find emulators.cfg for [%s]" % emulator
		infos2 = "Please, install at least one emulator or core"
		something_is_bad(infos,infos2)
		logging.info("ERROR: Saliendo de la aplicacion")
		sys.exit()
	################################################################################################
	# Open emulators.cfg and read lines for CRT integration                                        #
	# RETROPIE use command line defined on each emulators.cfg located in emulator's config folder  #
	# These command lines are added by RETROPIE when a new emulator is installed, we can manage    #
	# changing this configuration forcing for example, default emulator/core for best CRT          #
	# experience.                                                                                  #
	# This part will get default emulator/core and available of emulators.cfg in a variable        #
	################################################################################################
	logging.info("INFO: Accediendo al archivo %s y analizando emuladores instalados" % cfgfilepath)
	with open(cfgfilepath, 'r') as file:
		for line in file:
			linecheck = line.strip().split(' ')
			line = line.strip()
			################################################################################################
			# Search for 'default' emulator/core line                                                      #
			################################################################################################
			if linecheck[0] == 'default':
				logging.info("INFO: Emulador por defecto para el sistema %s es %s" % (emulator,linecheck[2]))
				################################################################################################
				# Check if DEFAULT core version of advmame is supported                                        #
				################################################################################################
				if linecheck[2] == advmame[2]:
					logging.info("INFO: Emulador por defecto (%s) detectado como emulador valido para advmame" % linecheck[2])
					advmame_valid[0] = True
					advmame_valid[1] = linecheck[2]
				else:
					logging.info("INFO: Emulador por defecto (%s) detectado como emulador NO valido para advmame" % linecheck[2])
					advmame_valid[0] = False
					advmame_valid[1] = "none"
				if amiga[1] in linecheck[2] or amiga[3] in linecheck[2]:
					logging.info("INFO: Emulador por defecto (%s) detectado como emulador valido para amiga" % linecheck[2])
					amiga_valid[0] = True
					amiga_valid[1] = linecheck[2]
				else:
					logging.info("INFO: Emulador por defecto (%s) detectado como emulador NO valido para amiga" % linecheck[2])
					amiga_valid[0] = False
					amiga_valid[1] = "none"
				if linecheck[2].replace('"','') == scummvm[1] or linecheck[2].replace('"','') == scummvm[3]:
					logging.info("INFO: Emulador por defecto (%s) detectado como emulador valido para scummvm" % linecheck[2])
					scummvm_valid[0] = True
					scummvm_valid[1] = linecheck[2]
				else:
					logging.info("INFO: Emulador por defecto (%s) detectado como emulador NO valido para scummvm" % linecheck[2])
					scummvm_valid[0] = False
					scummvm_valid[1] = "none"
					
				if linecheck[2].replace('"','') == dosbox[1]:
					logging.info("INFO: Emulador por defecto (%s) detectado como emulador valido para dosbox" % linecheck[2])
					dosbox_valid[0] = True
					dosbox_valid[1] = linecheck[2]
				else:
					logging.info("INFO: Emulador por defecto (%s) detectado como emulador NO valido para dosbox" % linecheck[2])
					dosbox_valid[0] = False
					dosbox_valid[1] = "none"
					
				if not 'lr-' in line:
					logging.info("INFO: Emulador por defecto (%s) detectado como emulador generico libretro NO valido" % linecheck[2])
					default_valid[0] = False
					default_valid[1] = "none"
				else:
					logging.info("INFO: Emulador por defecto (%s) detectado como emulador generico libretro valido" % linecheck[2])
					default_valid[0] = True
					default_valid[1] = linecheck[2]
				default_moded = line

			################################################################################################
			# Must be specific command lines for each emulator/core installed on emulators.cfg             #
			################################################################################################
			else:
				logging.info("INFO: Encontrado emulador instalado: %s" % linecheck[0])
				coreid = linecheck[0]
				quotedcoreid = "\"%s\"" % linecheck[0]
				################################################################################################
				# Check for advmame supported versions                                                         #
				################################################################################################
				if quotedcoreid == advmame[2]:
					logging.info("INFO: Encontrado emulador instalado (%s) compatible con advmame" % linecheck[0])
					advmame[0] = True
				################################################################################################
				# Check for amiga supported emulators                                                          #
				################################################################################################
				if amiga[1] in coreid:
					logging.info("INFO: Encontrado emulador instalado (%s) compatible con amiga" % amiga[1])
					amiga[0] = True
				if amiga[3] in coreid:
					logging.info("INFO: Encontrado emulador instalado (%s) compatible con amiga" % amiga[3])
					amiga[2] = True
				################################################################################################
				# Check for scummvm supported emulators                                                        #
				################################################################################################
				if scummvm[1] == coreid:
					logging.info("INFO: Encontrado emulador instalado (%s) compatible con scummvm" % scummvm[1])
					scummvm[0] = True
				if scummvm[3] == coreid:
					logging.info("INFO: Encontrado emulador instalado (%s) compatible con scummvm" % scummvm[3])
					scummvm[2] = True
				################################################################################################
				# Check for dosbox supported emulators                                                        #
				################################################################################################
				if dosbox[1] == coreid:
					logging.info("INFO: Encontrado emulador instalado (%s) compatible con dosbox" % dosbox[1])
					dosbox[0] = True
				################################################################################################
				# Any case, if not a Libretro core leave command line as it is                                 #
				################################################################################################
				if not 'lr-' in coreid:
					logging.info("INFO: Modificando cadena de ejecucion para emulador NO libretro (%s) en %s" % (linecheck[0],cfgfilepath))
					ExecutionLine = line.strip().split('=')
					ExecutionLine[1] = ExecutionLine[1].replace('touch /tmp/lchtmp && sleep 1 && ','').replace('"','').strip()
					retropiecommand = "%s = \"touch /tmp/lchtmp && sleep 1 && %s\"" % (coreid,ExecutionLine[1])
					logging.info("INFO: Cadena calculada: \"%s\"" % retropiecommand)
				################################################################################################
				# If exist Libretro core command line, function will generate a custom command line for right  #
				# resolution config:                                                                           #
				#   1.- Generate path to core's binary and check if not, exit launcher                         #
				#   2.- Generate full command line parameters for Libretro and core:                           #
				#     a) Path to RETROPIE retroarch path                                                       #
				#     b) Config pointig to retroarch.cfg included in config folder of each libretro core.      #
				#        This config includes automatically retroarch.cfg global file in RETROPIE              #
				#     c) Append specific RGB retroarch.cfg config file.                                        #
				#                                                                                              #
				# *Retroarch config files priorities for defined options:                                      #
				#    1)CRT Retroarch -> 2)CUSTOM Retroach (in core config folder) -> 3) GLOBAL Retroarch       #
				#  As regular RETROPIE instalation, users can add their custom option is CUSTOM retroarch.cfg  #
				# *CORE options are CUSTOM files from RGB integration defined on RGB retroarch.cfg             #
				################################################################################################
				else:
					logging.info("INFO: Modificando cadena de ejecucion para emulador libretro (%s) en %s" % (linecheck[0],cfgfilepath))
					found_Lr_core = True
					count = 0
					for item in linecheck:
						if item == "-L":
							corepath = linecheck[count+1]
							logging.info("INFO: Path del emulador libretro (%s): \"%s\"" % (linecheck[0],corepath))
						count += 1
					if not os.path.isfile(corepath):
						logging.info("INFO: No se ha podido encontrar la ruta del emulador")
						infos = "Can't convert command line for [%s]" % coreid
						infos2 = "You can't do anything... sorry!"
						something_is_bad(infos,infos2)
						logging.info("Saliendo de la aplicacion")
						sys.exit()
					if easynet == "":
						logging.info("INFO: Easynet esta deshabilitado, excluido de la cadena de ejecucion")
						retropiecommand = "%s = \"touch /tmp/lchtmp && sleep 1 && /opt/retropie/emulators/retroarch/bin/retroarch -L %s --config /opt/retropie/configs/%s/retroarch.cfg --appendconfig %s %s\"" % (coreid,corepath,emulator,addcfgpath,"%ROM%")
					else:
						logging.info("INFO: Easynet = \"%s\", se incluira en la cadena de ejecucion" % easynet)
						retropiecommand = "%s = \"touch /tmp/lchtmp && sleep 1 && /opt/retropie/emulators/retroarch/bin/retroarch %s -L %s --config /opt/retropie/configs/%s/retroarch.cfg --appendconfig %s %s\"" % (coreid,easynet,corepath,emulator,addcfgpath,"%ROM%")
					logging.info("INFO: Cadena calculada: \"%s\"" % retropiecommand)
				################################################################################################
				# If generated command line is different, original emulators.cfg will modified                 #
				################################################################################################
				if retropiecommand != line:
					check_changes = 1
					logging.info("La cadena de ejecucion calculada para \"%s\" es diferente a la existente" % linecheck[0])
				else:
					logging.info("La cadena de ejecucion calculada para \"%s\" es igual a la existente" % linecheck[0])
				if all_lines_moded == "none":
					logging.info("Guardando linea de ejecucion calculada en variable")
					all_lines_moded = retropiecommand
				else:
					logging.info("Guardando linea de ejecucion calculada en variable")
					all_lines_moded = "%s\n%s" % (all_lines_moded,retropiecommand)

	#####################################################################################################################
	# SPECIFIC FOR ADVMAME                                                                                              #
	# Check current default core version of advmame after emulators.cfg review:                                         #
	#  1.- If not compatible version as default and there is any compatible, function will close later the launcher     #
	#  2.- If not compatible version as default and compatible is available, function will change for it.               #
	#      Change default with preferred: advmame (v3.9)                                                                #
	#      Return to main program the advmame database                                                                  #
	#####################################################################################################################
	if emulator == "mame-advmame":
		logging.info("Analizando emuladores para advmame")
		if advmame_valid[0] == False and advmame[0] == False:
			infos = "Install a supported version of advmame" 
			infos2 = ""
			something_is_bad(infos,infos2)
			logging.info("No hay instalado ningun emulador advmame compatible con CRT")
			logging.info("Saliendo de la aplicacion")
			sys.exit()
		else:
			if advmame_valid[1] != advmame[2]:
				logging.info("Estableciendo como predeterminada la version advmame encontrada (compatible)")
				default_moded = "default = %s" % (advmame[2])
				advmame_valid[1] = advmame[2]
				check_changes = 1

	#####################################################################################################################
	# SPECIFIC FOR AMIGA                                                                                                #
	# Check current default core version of amiga after emulators.cfg review:                                           #
	#  1.- If not compatible version as default and there is any compatible, function will close later the launcher     #
	#  2.- If not compatible version as default and compatible is available, function will change for it.               #
	#      Change default with preferred:  first amiberry then lr-puae                                                  #
	#      Return to main program the amiberry xml database                                                             #
	#####################################################################################################################
	elif emulator == "amiga":
		logging.info("Analizando emuladores para amiga")
		if amiga_valid[0] == False and amiga[0] == False and amiga[2] == False:
			infos = "Install a supported version of amiga" 
			infos2 = ""
			something_is_bad(infos,infos2)
			logging.info("No hay instalado ningun emulador amiga compatible con CRT")
			logging.info("Saliendo de la aplicacion")
			sys.exit()
		elif amiga_valid[0] == False and amiga[2] == True:
			logging.info("Emulador por defecto para amiga NO soportado por CRT")
			logging.info("Detectado (%s), estableciendo emulador como predeterminado" % amiga[1])
			default_moded = "default = %s" % amiga[3]
			logging.info("Guardando configuracion de emulador por defecto en variable:")
			logging.info(default_moded)
			amiga_valid[1] = amiga[3]
			check_changes = 1
		elif amiga_valid[0] == False and amiga[0] == True:
			default_moded = "default = %s" % amiga[1]
			amiga_valid[1] = amiga[1]
			check_changes = 1

	#####################################################################################################################
	# SPECIFIC FOR SCUMMVM                                                                                              #
	# Check current default emulator for scummvm after emulators.cfg review:                                            #
	#  1.- If not compatible version as default and there is any compatible, function will close later the launcher     #
	#####################################################################################################################
	elif emulator == "scummvm":
		logging.info("Analizando emuladores para scummvm")
		if scummvm_valid[0] == False and scummvm[0] == False and scummvm[2] == False:
			infos = "Install a supported version of scummvm" 
			infos2 = ""
			something_is_bad(infos,infos2)
			logging.info("No hay instalado ningun emulador scummvm compatible con CRT")
			logging.info("Saliendo de la aplicacion")
			sys.exit()
		if scummvm_valid[0] == False and (scummvm[0] == True or scummvm[2] == True):
			logging.info("Existe una version compatible de emulador para scummvm pero no es la seleccionada")
			default_moded = ""
			check_changes = 1
	#####################################################################################################################
	# SPECIFIC FOR DOSBOX                                                                                               #
	# Check current default emulator for dosbox after emulators.cfg review:                                             #
	#  1.- If not compatible version as default and there is any compatible, function will close later the launcher     #
	#####################################################################################################################
	elif emulator == "pc":
		logging.info("Analizando emuladores para dosbox")
		if dosbox_valid[0] == False and dosbox[0] == False and dosbox[2] == False:
			infos = "Install a supported version of dosbox" 
			infos2 = ""
			something_is_bad(infos,infos2)
			logging.info("No hay instalado ningun emulador dosbox compatible con CRT")
			logging.info("Saliendo de la aplicacion")
			sys.exit()
		if dosbox_valid[0] == False and (dosbox[0] == True or dosbox[2] == True):
			logging.info("Existe una version compatible de emulador para dosbox pero no es la seleccionada")
			default_moded = ""
			check_changes = 1
	#################################################################################################################
	# FOR ALL CONSOLES, HANDLED, MAME LIBRETRO AND FBA LIBRETRO                                                     #
	# Check if default core is Libretro after emulators.cfg review, if not:                                         #
	#   1.- If there is installed a Libretro core but no default, function will remove default line. This force     #
	#       runcommand to launch core selector. User must select a Retroarch core.                                  #
	#   2.- If there is not installed any Libretro core, function will close launcher and request install at least  #
	#       one with Retropie-config                                                                                #
	#                                                                                                               #
	# * For mame-libretro or FBA any mame/FBA libretro core is allowed.                                             #
	#   For mame-libretro function will select appropiate database:                                                 #
	#       lr-mame2000 0.37b5 Romset Database                                                                      #
	#       lr-mame2003 0.78 Romset Database                                                                        #
	#       lr-mame2010 0.139 Romset Database                                                                       #
	#       Any other lr-mame 0.78 Romset Database                                                                  #
	#   database. Any game out of this DB will be launched with default resolution mode 1920x240x60hz.              #
	#   For any version of libretro FBA only will be available 0.2.97.43 romset resolution database.                #
	#################################################################################################################
	elif emulator == "arcade":
		if default_valid[0] != True and advmame_valid[0] != True:
			if found_Lr_core == True or advmame[0] == True:
				default_moded == ""
				check_changes = 1
			if found_Lr_core == False and advmame[0] == False:
				infos = "Install a Libretro Core or advmame for [%s]" % (emulator) 
				infos2 = ""
				something_is_bad(infos,infos2)
				sys.exit()
	else:
		if default_valid[0] == False and found_Lr_core == True:
			default_moded = ""
			check_changes = 1
		if default_valid[0] == False and found_Lr_core == False:
			infos = "Install a Libretro Core for [%s]" % (emulator) 
			infos2 = ""
			something_is_bad(infos,infos2)
			sys.exit()

	# Add default core line of configuration file at the end
	all_lines_moded = "%s\n%s" % (all_lines_moded,default_moded)

	# If any change is needed function will overwrite emulators.cfg
	if check_changes != 0:
		with open(cfgfilepath, "w") as file:
			file.write(all_lines_moded)
	# If there is any compatible emulator but not as default, force exit.
	if default_moded == "":
		infos = "Please, select compatible core/emulator" 
		infos2 = ""
		something_is_bad(infos,infos2)

	CustEmuLineGame=check_custom_emulator_per_game (emulator,game_name,custom_emulator_file)

	#################################################################
	# For MAME, FBA and AMIGA is returned resolution DB             #
	# Also check if game has selected a different and compatible    #
	# emulator                                                      #
	#################################################################
	if emulator == "mame-libretro":
		if CustEmuLineGame[1] != "none":
			if not 'lr-' in CustEmuLineGame[1]:
				modificarLinea(custom_emulator_file,CustEmuLineGame[0],"")
			else:
				default_moded = CustEmuLineGame[1]
		if 'mame' in default_moded and '2000' in default_moded:
			returnedDB[0] = mame037b5DB
		if 'mame' in default_moded and '2003' in default_moded:
			returnedDB[0] = mame078DB
		if 'mame' in default_moded and '2010' in default_moded:
			returnedDB[0] = mame0139DB
		if default_moded == "":
			returnedDB[0] = mame078DB
		returnedDB[1] = "mame-libretro"
		# Check current Retroarch Version
		Check_RetroArch_Version ("/opt/retropie/configs/all/CRT/Retroarch/configs/retroarcharcade.cfg")
	elif emulator == "fba":
		returnedDB[0] = fbalphaDB
		returnedDB[1] = "fba"
		if CustEmuLineGame[1] != "none" and not 'lr-' in CustEmuLineGame[1]:
			modificarLinea(custom_emulator_file,CustEmuLineGame[0],"")
		# Check current Retroarch Version
		Check_RetroArch_Version ("/opt/retropie/configs/all/CRT/Retroarch/configs/retroarcharcade.cfg")
	elif emulator == "scummvm":
		if CustEmuLineGame[1] != "none":
			if CustEmuLineGame[1].replace('"','') != scummvm[1] and CustEmuLineGame[1].replace('"','') != scummvm[3]:
				logging.info("INFO: Emulador especifico scummvm para este juego (%s) no es ninguno de los soportados (%s o %s)" % (CustEmuLineGame[1], scummvm[1], scummvm[3]))
				logging.info("INFO: Eliminando linea en %s para juego %s" % (custom_emulator_file, CustEmuLineGame[0]))
				modificarLinea(custom_emulator_file,CustEmuLineGame[0],"")
	elif emulator == "pc":
		if CustEmuLineGame[1] != "none":
			if CustEmuLineGame[1].replace('"','') != dosbox[1]:
				logging.info("INFO: Emulador especifico dosbox para este juego (%s) no es ninguno de los soportados (%s)" % (CustEmuLineGame[1], dosbox[1]))
				logging.info("INFO: Eliminando linea en %s para juego %s" % (custom_emulator_file, CustEmuLineGame[0]))
				modificarLinea(custom_emulator_file,CustEmuLineGame[0],"")
	elif emulator == "mame-advmame":
		returnedDB[0] = advmameDB
		returnedDB[1] = "mame-advmame"
		if CustEmuLineGame[1] != "none" and CustEmuLineGame[1] != advmame[2]:
			modificarLinea(custom_emulator_file,CustEmuLineGame[0],"")
	elif emulator == "amiga":
		if CustEmuLineGame[1] != "none":
			if not amiga[1] in CustEmuLineGame[1] and not amiga[3] in CustEmuLineGame[1]:
				modificarLinea(custom_emulator_file,CustEmuLineGame[0],"")
			else:
				amiga_valid[1] = CustEmuLineGame[1]
		returnedDB[0] = amigaDB
		returnedDB[1] = amiga_valid[1]
		default_moded = amiga_valid[1]
	elif emulator == "arcade":
		if 'lr-mame' in default_moded:
			if CustEmuLineGame[1] != "none":
				if not 'lr-' in CustEmuLineGame[1]:
					modificarLinea(custom_emulator_file,CustEmuLineGame[0],"")
				else:
					default_moded = CustEmuLineGame[1]
			if 'mame' in default_moded and '2000' in default_moded:
				returnedDB[0] = mame037b5DB
			if 'mame' in default_moded and '2003' in default_moded:
				returnedDB[0] = mame078DB
			if 'mame' in default_moded and '2010' in default_moded:
				returnedDB[0] = mame0139DB
			if default_moded == "":
				returnedDB[0] = mame078DB
			returnedDB[1] = "mame-libretro"
			# Check current Retroarch Version
			Check_RetroArch_Version ("/opt/retropie/configs/all/CRT/Retroarch/configs/retroarcharcade.cfg")
		if 'lr-fba' in default_moded:
			returnedDB[0] = fbalphaDB
			returnedDB[1] = "fba"
			if CustEmuLineGame[1] != "none" and not 'lr-' in CustEmuLineGame[1]:
				modificarLinea(custom_emulator_file,CustEmuLineGame[0],"")
			# Check current Retroarch Version
			Check_RetroArch_Version ("/opt/retropie/configs/all/CRT/Retroarch/configs/retroarcharcade.cfg")
		if 'advmame' in default_moded:
			returnedDB[0] = advmameDB
			returnedDB[1] = "mame-advmame"
			if CustEmuLineGame[1] != "none" and CustEmuLineGame[1] != advmame[2]:
				modificarLinea(custom_emulator_file,CustEmuLineGame[0],"")
		if default_moded == "":
			if CustEmuLineGame[1] != "none":
				if not 'lr-' in CustEmuLineGame[1] and CustEmuLineGame[1] != advmame[2]:
					modificarLinea(custom_emulator_file,CustEmuLineGame[0],"")
					returnedDB[0] = mame078DB
					returnedDB[1] = "unknown"
				else:
					default_moded = CustEmuLineGame[1]
					if 'lr-mame' in default_moded:
						if 'mame' in default_moded and '2000' in default_moded:
							returnedDB[0] = mame037b5DB
						if 'mame' in default_moded and '2003' in default_moded:
							returnedDB[0] = mame078DB
						if 'mame' in default_moded and '2010' in default_moded:
							returnedDB[0] = mame0139DB
						if default_moded == "":
							returnedDB[0] = mame078DB
						returnedDB[1] = "mame-libretro"
					elif 'lr-fba' in default_moded:
						returnedDB[0] = fbalphaDB
						returnedDB[1] = "fba"
					elif 'advmame' in default_moded:
						returnedDB[0] = advmameDB
						returnedDB[1] = "mame-advmame"
					else:
						returnedDB[0] = mame078DB
						returnedDB[1] = "unknown"
			else:
				returnedDB[0] = mame078DB
				returnedDB[1] = "unknown"
			# Check current Retroarch Version
			Check_RetroArch_Version ("/opt/retropie/configs/all/CRT/Retroarch/configs/retroarcharcade.cfg")
	else:
		if CustEmuLineGame[1] != "none":
			if not 'lr-' in CustEmuLineGame[1]:
				modificarLinea(custom_emulator_file,CustEmuLineGame[0],"")
			else:
				default_moded = CustEmuLineGame[1]
		# Check current Retroarch Version
		Check_RetroArch_Version (addcfgpath)
	#Some systems may need some fine tunning on resolution depending on which core they use
	if default_moded != "":
		UsedCore = default_moded
		Check_SystemCore_SpecialConfig(emulator,UsedCore,addcfgpath)
	if returnedDB != ["none","none"]:
		return returnedDB
	


#################################################################################################################
#  This function will check if retroarch is lower than v1.7.5 because of there is a significative change witch  #
# 'customview' number that affects to CRT.                                                                   #
#################################################################################################################
def Check_RetroArch_Version(configfile):
	RetroarchPath = "/opt/retropie/emulators/retroarch/bin/retroarch"
	HashRetroarchVersionDB = "/opt/retropie/configs/all/CRT/HashRetroarchVersionDB.txt"
	DBUpdate = "none"
	RetroarchIDENT = "none"
	RetroarchIDENTFound = False
	RetroarchVerOutput = "none"
	RetroarchVersionFound = "none"
	hasher = hashlib.md5()
	# Get Retroarch hash
	with open(RetroarchPath, 'rb') as afile:
		buf = afile.read()
		hasher.update(buf)
	RetroarchHASH = hasher.hexdigest()

	# Look for the hash in custom retroarch database 
	with open(HashRetroarchVersionDB, 'r') as file:
		for lineS in file:
			lineS = lineS.strip()
			if DBUpdate == "none":
				DBUpdate = lineS
			else:
				DBUpdate = "%s\n%s" % (DBUpdate,lineS)
			
			lineS = lineS.strip().split(' ')
			if lineS[1] == RetroarchHASH:
				RetroarchIDENTFound = True
				RetroarchVersionFound = lineS[2]
				break

	# If the hash is not registered, a new enter in file will be created with hash and number version.
	if RetroarchIDENTFound == False:
		RetroarchVerOutput = commands.getoutput("%s --version" % RetroarchPath)
		for outputline in RetroarchVerOutput.splitlines():
			outputline = outputline.strip().split(' ')
			if 'RetroArch' in outputline[0]:
				RetroarchVersionFound = outputline[5]
				RetroarchIDENT = "RetroArch %s %s" % (RetroarchHASH,outputline[5])
				DBUpdate = "%s\n%s" % (DBUpdate,RetroarchIDENT)
		with open(HashRetroarchVersionDB, "w") as file:
			file.write(DBUpdate)
	# Make some actions if retroarch version is equal or higher than (in this case) 1.7.5
	if RetroarchVersionFound >= 'v1.7.5':
		modificarLinea (configfile,"aspect_ratio_index","aspect_ratio_index = \"23\"")
	else:
		modificarLinea (configfile,"aspect_ratio_index","aspect_ratio_index = \"22\"")
##################################################################################################################
#   Second check of default emulator.                                                                            #
#   Because of is possible to change default emulator and emulator for an specific game just before launch it    #
#   with the runcommand menu (retropie native) is necessary to check for a second time if the new selected one   #
#   is compatible.                                                                                               #
##################################################################################################################
def second_check_runcommand_emulator_init(emulator,rom_full_path,emulatorcfg,pathemulatorcfg,PreselectedCore):

	addcfgpath = "%s%s.cfg" % (pathemulatorcfg,emulatorcfg)
	file_name = os.path.basename(rom_full_path)
	game_name = file_name[:-4]
	
	advmame = [False, "/opt/retropie/emulators/advmame/bin/advmame", "\"advmame\"", "/opt/retropie/configs/mame-advmame/advmame.rc"] 
	advmame_valid = [False, "none"]
	
	amiga = [False, "amiberry", False, "lr-puae"] 
	amiga_valid = [False, "none"]

	scummvm = [False, "scummvm", False, "scummvm-sdl1"] 
	scummvm_valid = [False, "none"]

	dosbox = [False, "dosbox"] 
	dosbox_valid = [False, "none"]

	
	default_valid = [False, "none"]
	KillEmulator = [False, "none"]

	coreid = "none"
	corefile = "none"
	corepath = "none"
	retropiecommand = "none"
	cfgfilepath = "/opt/retropie/configs/%s/emulators.cfg" % emulator
	custom_emulator_file = "/opt/retropie/configs/all/emulators.cfg"
	found_Lr_core = False

	all_lines_moded = "none"
	default_moded = "none"
	check_changes = 0

	if not os.path.isfile(cfgfilepath):
		infos = "Can't find emulators.cfg for [%s]" % emulator
		infos2 = "Please, install at least one emulator or core"
		something_is_bad(infos,infos2)
		sys.exit()
	with open(cfgfilepath, 'r') as file:
		for line in file:
			linecheck = line.strip().split(' ')
			line = line.strip()
			if linecheck[0] == 'default':
				if linecheck[2] == advmame[2]:
					advmame_valid[0] = True
				else:
					advmame_valid[0] = False
				if amiga[1] in linecheck[2] or amiga[3] in linecheck[2]:
					amiga_valid[0] = True
					amiga_valid[1] = linecheck[2]
				else:
					amiga_valid[0] = False
					amiga_valid[1] = "none"
				if linecheck[2].replace('"','') == scummvm[1] or linecheck[2].replace('"','') == scummvm[3]:
					scummvm_valid[0] = True
					scummvm_valid[1] = linecheck[2]
				else:
					scummvm_valid[0] = False
					scummvm_valid[1] = "none"
					
				if linecheck[2].replace('"','') == dosbox[1]:
					dosbox_valid[0] = True
					dosbox_valid[1] = linecheck[2]
				else:
					dosbox_valid[0] = False
					dosbox_valid[1] = "none"
				if not 'lr-' in line:
					default_valid[0] = False
				else:
					default_valid[0] = True
				advmame_valid[1] = linecheck[2]
				
				default_valid[1] = linecheck[2]
				default_moded = line
			else:
				coreid = linecheck[0]
				quotedcoreid = "\"%s\"" % linecheck[0]
				if quotedcoreid == advmame[2]:
					advmame[0] = True
				if amiga[1] in coreid:
					amiga[0] = True
				if amiga[3] in coreid:
					amiga[2] = True
				if scummvm[1] == coreid:
					scummvm[0] = True
				if scummvm[3] == coreid:
					scummvm[2] = True
				if dosbox[1] == coreid:
					dosbox[0] = True
				if 'lr-' in coreid:
					found_Lr_core = True
	if emulator == "mame-advmame":
		if advmame_valid[1] != advmame[2]:
			default_moded = "default = %s" % (advmame[2])
			check_changes = 1
	elif emulator == "scummvm":
		if scummvm_valid[0] == False and scummvm[0] == False and scummvm[2] == False:
			logging.info("NO Existe una version compatible de emulador para scummvm instalada")
			default_moded = ""
			check_changes = 1
		elif scummvm_valid[0] == False and (scummvm[0] == True or scummvm[2] == True):
			logging.info("Existe una version compatible de emulador para scummvm pero no es la seleccionada")
			default_moded = ""
			check_changes = 1
	elif emulator == "pc":
		if dosbox_valid[0] == False and dosbox[0] == False and dosbox[2] == False:
			default_moded = ""
			check_changes = 1
		elif dosbox_valid[0] == False and (dosbox[0] == True or dosbox[2] == True):
			default_moded = ""
			check_changes = 1
	elif emulator == "amiga":
		if amiga_valid[0] == True:
			PreselectedCore = PreselectedCore.replace('-a1200','').replace('-a500','').strip('"')
			SelectedCore = amiga_valid[1].replace('-a1200','').replace('-a500','').strip('"')
			if PreselectedCore != SelectedCore:
				KillEmulator[0] = True
				KillEmulator[1] = "core_changed"
		else:
			if amiga_valid[0] == False and amiga[0] == False and amiga[2] == False:
				infos = "Install a supported version of amiga" 
				infos2 = ""
				something_is_bad(infos,infos2)
				sys.exit()
			elif amiga_valid[0] == False and amiga[2] == True:
				default_moded == "default = %s" % (amiga[3])
				amiga_valid[1] = amiga[3]
				check_changes = 1
			elif amiga_valid[0] == False and amiga[0] == True:
				default_moded == "default = %s" % (amiga[1])
				amiga_valid[1] = amiga[1]
				check_changes = 1
	elif emulator == "arcade":
		if default_valid[0] != True and advmame_valid[0] != True:
			if found_Lr_core == True or advmame[0] == True:
				default_moded == ""
				check_changes = 1
	else:
		if default_valid[0] == False and found_Lr_core == True:
			default_moded = ""
			check_changes = 1

	if check_changes != 0:
		modificarLinea(cfgfilepath,"default",default_moded)
		KillEmulator[0] = True
		KillEmulator[1] = "core_compatible"

	CustEmuLineGame=check_custom_emulator_per_game (emulator,game_name,custom_emulator_file)
	if CustEmuLineGame[1] != "none":
		if emulator == "mame-advmame":
			if CustEmuLineGame[1] != advmame[2]:
				modificarLinea(custom_emulator_file,CustEmuLineGame[0],"")
				KillEmulator[0] = True
				KillEmulator[1] = "core_compatible_game"
			else:
				default_moded = CustEmuLineGame[1]
		elif emulator == "amiga":
			if not amiga[1] in CustEmuLineGame[1] and not amiga[3] in CustEmuLineGame[1]:
				modificarLinea(custom_emulator_file,CustEmuLineGame[0],"")
				KillEmulator[0] = True
				KillEmulator[1] = "core_compatible_game"
			else:
				default_moded = CustEmuLineGame[1].replace('"','')
				if PreselectedCore != default_moded:
					KillEmulator[0] = True
					KillEmulator[1] = "core_changed"
				else:
					KillEmulator[0] = False
					KillEmulator[1] = "none"

		elif emulator == "scummvm":
			if CustEmuLineGame[1].replace('"','') != scummvm[1] and CustEmuLineGame[1].replace('"','') != scummvm[3]:
				logging.info("INFO: Emulador especifico scummvm para este juego (%s) no es ninguno de los soportados (%s o %s)" % (CustEmuLineGame[1], scummvm[1], scummvm[3]))
				logging.info("INFO: Eliminando linea en %s para juego %s" % (custom_emulator_file, CustEmuLineGame[0]))
				modificarLinea(custom_emulator_file,CustEmuLineGame[0],"")
				KillEmulator[0] = True
				KillEmulator[1] = "core_compatible_game"
			else:
				default_moded = CustEmuLineGame[1]
		elif emulator == "pc":
			if CustEmuLineGame[1].replace('"','') != dosbox[1]:
				modificarLinea(custom_emulator_file,CustEmuLineGame[0],"")
				KillEmulator[0] = True
				KillEmulator[1] = "core_compatible_game"
			else:
				default_moded = CustEmuLineGame[1]
		elif emulator == "arcade":
			if 'lr-mame' in default_moded:
				if not 'lr-' in CustEmuLineGame[1]:
					modificarLinea(custom_emulator_file,CustEmuLineGame[0],"")
					KillEmulator[0] = True
					KillEmulator[1] = "core_compatible_game"
				else:
					default_moded = CustEmuLineGame[1]
			elif 'lr-fba' in default_moded:
				if not 'lr-' in CustEmuLineGame[1]:
					modificarLinea(custom_emulator_file,CustEmuLineGame[0],"")
					KillEmulator[0] = True
					KillEmulator[1] = "core_compatible_game"
				else:
					default_moded = CustEmuLineGame[1]
			elif 'advmame' in default_moded:
				if CustEmuLineGame[1] != advmame[2]:
					modificarLinea(custom_emulator_file,CustEmuLineGame[0],"")
					KillEmulator[0] = True
					KillEmulator[1] = "core_compatible_game"
				else:
					default_moded = CustEmuLineGame[1]
#ESTE SE PODRIA ELIMINAR
			elif default_moded == "":
				if not 'lr-' in CustEmuLineGame[1] and CustEmuLineGame[1] != advmame[2]:
					modificarLinea(custom_emulator_file,CustEmuLineGame[0],"")
					KillEmulator[0] = True
				else:
					default_moded = CustEmuLineGame[1]
		else:
			if not 'lr-' in CustEmuLineGame[1]:
				modificarLinea(custom_emulator_file,CustEmuLineGame[0],"")
				KillEmulator[0] = True
				KillEmulator[1] = "core_compatible_game"
			else:
				default_moded = CustEmuLineGame[1]
	if KillEmulator[0] != True:
		UsedCore = default_moded
		Check_SystemCore_SpecialConfig(emulator,UsedCore,addcfgpath)
	return KillEmulator
def check_videomodes():
	videomodes_path = "/opt/retropie/configs/all/videomodes.cfg"
	if os.path.exists('%s' % videomodes_path):
		os.remove ('%s' % videomodes_path)
		return True
	else:
		return False
def find_amiberry_WHDLoadDB_vertical_res(attribute,file,WHDLoadDB):
	VRES = 0
	tree = ET.parse(WHDLoadDB)
	root = tree.getroot()
	GameFound = [False,0]
	for game in root.findall('game'):
		if game.get('filename') == file:
			GameFound[0] = True
			n = game.find('hardware').text
			p = n.find(attribute)
			if p > 0:
				VRES = n[p + len(attribute) : p + len(attribute) + 3]
				GameFound[1] = VRES
			break
	return (GameFound)