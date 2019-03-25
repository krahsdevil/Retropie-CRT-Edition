#!/usr/bin/python
# coding: utf-8
#
# Original idea/coded by Ironic/aTg (2017) for RGB-Pi recalbox
# Retropie code/integration by -krahs- (2019)
#
# unlicense.org
#
# This script can be heavily optimized.

import struct
import sys
import os
import os.path
import pygame
import shutil
import time
import subprocess
import commands
import re

sys.path.append('/opt/retropie/configs/all/CRT/')

from math import *
from pygame.locals import *
from general_functions import modificarLinea

x_screen = 0
y_screen = 0
l_axis_x = 0
l_axis_y = 1
button_b = 0
button_a = 1
state_up = 0
state_down = 0
state_left = 0
state_right = 0
threshold = 0.1
last_axis_motion = time.time()


#game_name = 'asdfas'

h = {
	(0,0):  'c',
	(1,0):  'E', (1,1):   'NE', (0,1):  'N', (-1,1): 'NW',
	(-1,0): 'W', (-1,-1): 'SW', (0,-1): 'S', (1,-1): 'SE'
}

VideoUtilityCFG = "/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/utility.cfg"
JoyAutoconfigPath = "/opt/retropie/configs/all/retroarch/autoconfig/"
AutoFreqDB = '/opt/retropie/configs/all/CRT/AutoFreqDB.cfg'

black = pygame.Color(0, 0, 0)
white = pygame.Color(255,255,255)

def get_retropie_joy_map():
	global l_axis_x
	global l_axis_y
	global button_b
	global button_a
	
	try:
		pygame.joystick.Joystick(0).init()
	except:
		pass
	try:
		if pygame.joystick.Joystick(0):
			JoyName = pygame.joystick.Joystick(0).get_name()
			JoyConfigFile = JoyAutoconfigPath + JoyName + '.cfg'
			if os.path.exists(JoyConfigFile):
				with open(JoyConfigFile, 'r') as file:
					for line in file:
						line = line.strip().replace(' = ',' ').replace('=',' ').replace('"','').split(' ')
						if line[0] == 'input_l_x_minus_axis':
							l_axis_x = int(line[1])
						if line[0] == 'input_l_y_minus_axis':
							l_axis_y = int(line[1])
						if line[0] == 'input_a_btn':
							button_a = int(line[1])
						if line[0] == 'input_b_btn':
							button_b = int(line[1])
	except:
		pass

def check_joy_event(event):
	global last_axis_motion
	global state_up
	global state_down
	global state_left
	global state_right
	movement = 'none'
	if event.type == pygame.KEYDOWN:
		if event.key == pygame.K_UP:
			movement = 'UPKEYBOARD'
		elif event.key == pygame.K_DOWN:
			movement = 'DOWNKEYBOARD'
		elif event.key == pygame.K_LEFT:
			movement = 'LEFTKEYBOARD'
		elif event.key == pygame.K_RIGHT:
			movement = 'RIGTHKEYBOARD'
		else:
			movement = 'KEYBOARD'
	elif event.type == pygame.JOYBUTTONDOWN:
		if event.button == int(button_b):
			movement = 'JOYBUTTONB'
		elif event.button == int(button_a):
			movement = 'JOYBUTTONA'
		else:
			movement = 'JOYBUTTON'
	elif event.type == pygame.JOYHATMOTION:
		direction = h[event.value]
		if direction == 'N':
			movement = 'JOYHATUP'
		elif direction == 'S':
			movement = 'JOYHATDOWN'
		elif direction == 'E':
			movement = 'JOYHATRIGTH'
		elif direction == 'W':
			movement = 'JOYHATLEFT'
		else:
			movement = 'JOYHAT'
	elif event.type == pygame.JOYAXISMOTION:
		AxisMov = round(event.value, 2)
		if event.axis == abs(l_axis_x):
			if AxisMov > 0.7:
				if state_right == 0:
					state_right = AxisMov
					movement = 'AXISRIGTH'
			elif AxisMov < -0.7:
				if state_left == 0:
					state_left = AxisMov
					movement = 'AXISLEFT'
			elif AxisMov < threshold:
				state_left = 0
				state_right = 0
		elif event.axis == abs(l_axis_y):
			if AxisMov > 0.7:
				if state_down == 0:
					state_down = AxisMov
					movement = 'AXISDOWN'
			elif AxisMov < -0.7:
				if state_up == 0:
					state_up = AxisMov
					movement = 'AXISUP'
			elif AxisMov < threshold:
				state_down = 0
				state_up = 0
	return movement

def get_xy_screen():
	global x_screen
	global y_screen
	process = subprocess.Popen("fbset", stdout=subprocess.PIPE)
	output = process.stdout.read()
	for line in output.splitlines():
		if 'x' in line and 'mode' in line:
			ResMode = line
			ResMode = ResMode.replace('"','').replace('x',' ').split(' ')
			x_screen = int(ResMode[1])
			y_screen = int(ResMode[2])

def splash_info(SplashImagePath):
	get_xy_screen()
	black = pygame.Color(0, 0, 0)
	white = pygame.Color(255,255,255)

	if SplashImagePath != "black":
		pygame.init()
	pygame.display.init()
	pygame.mouse.set_visible(0)

	fullscreen = pygame.display.set_mode([x_screen,y_screen], FULLSCREEN)
	fullscreen.fill(black)

	if SplashImagePath != "black":
		SplashImagePath = pygame.image.load(SplashImagePath)
		SplashImagePathPos = SplashImagePath.get_rect()
		SplashImagePathPos.center = ((x_screen/2), (y_screen/2))
		fullscreen.blit(SplashImagePath, SplashImagePathPos)
		pygame.display.flip()
		time.sleep(5)
		pygame.quit()

def selector_frequency(game_name):
	get_xy_screen()
	NTSCDetect = False
	PALDetect = False
	Labels_50hz = ["pal","nl","e","s","sw","fn","g","uk","gr","i","h","eu","europe","europa","spain","germany","france","italy"]
	Labels_60hz = ["ntsc","1","4","a","j","b","k","c","u","hk","world","usa","us","ue","jue","jap","jp","japan","japon","asia","usa,europe","europe,usa","japan,usa","usa,japan"]
	PreCleanedGame = re.sub('[^a-zA-Z0-9-_]+','', game_name )
	CleanedGame = re.sub(' ','', PreCleanedGame )
	Gamedb = [False, '0']
	if not os.path.exists(AutoFreqDB):
		os.system('touch %s > /dev/null 2>&1'%AutoFreqDB)
	else:
		with open(AutoFreqDB, 'r') as file:
			for line in file:
				line = line.strip().split(' ')
				if line[0] == CleanedGame:
					if line[1] == '50':
						Gamedb[0] = True
						Gamedb[1] = '50'
					elif line[1] == '60':
						Gamedb[0] = True
						Gamedb[1] = '60'
					else:
						modificarLinea(AutoFreqDB,CleanedGame,"")
						Gamedb[0] = False
						Gamedb[1] = '0'
	with open(VideoUtilityCFG, 'r') as file:
		for line in file:
			line = line.strip().replace('=',' ').split(' ')
			if line[0] == 'freq_selector':
				if line[1] == "50":
					return 50
				elif line[1] == "60":
					return 60
				elif line[1] == "100":
					if Gamedb[0] == True:
						return Gamedb[1]
					else:
						for CountryCODE in Labels_60hz:
							BracketCountryCODE = "(%s)"%CountryCODE
							if BracketCountryCODE in game_name.lower():
								os.system('echo \"%s 60\" >> %s' % (CleanedGame,AutoFreqDB))
								NTSCDetect = True
								return 60
							BracketCountryCODE = "[%s]"%CountryCODE
							if BracketCountryCODE in game_name.lower():
								os.system('echo \"%s 60\" >> %s' % (CleanedGame,AutoFreqDB))
								NTSCDetect = True
								return 60
						for CountryCODE in Labels_50hz:
							BracketCountryCODE = "(%s)"%CountryCODE
							if BracketCountryCODE in game_name.lower():
								os.system('echo \"%s 50\" >> %s' % (CleanedGame,AutoFreqDB))
								PALDetect = True
								return 50
							BracketCountryCODE = "[%s]"%CountryCODE
							if BracketCountryCODE in game_name.lower():
								os.system('echo \"%s 50\" >> %s' % (CleanedGame,AutoFreqDB))
								PALDetect = True
								return 50

	pygame.mixer.pre_init(44100, -16, 1, 512)
	pygame.init()
	pygame.display.init()
	pygame.mouse.set_visible(0)
	
	get_retropie_joy_map()
	
	# FF files
	nojoy = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/style_default/nojoy.png')
	nojoyPos = nojoy.get_rect()
	nojoyPos.center = ((x_screen/2), (y_screen/2))
	ff60 = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/style_default/ff60.png')
	ff60Pos = ff60.get_rect()
	ff60Pos.center = ((x_screen/2), (y_screen/2))
	ff50 = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/style_default/ff50.png')
	ff50Pos = ff50.get_rect()
	ff50Pos.center = ((x_screen/2), (y_screen/2))
	load60 = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/style_default/load60.png')
	load60Pos = load60.get_rect()
	load60Pos.center = ((x_screen/2), (y_screen/2))
	load50 = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/style_default/load50.png')
	load50Pos = load50.get_rect()
	load50Pos.center = ((x_screen/2), (y_screen/2))
	cursor = pygame.mixer.Sound('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/style_default/cursor.wav')
	load = pygame.mixer.Sound('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/style_default/load.wav')

	# SET SCREEN
	fullscreen = pygame.display.set_mode((x_screen,y_screen), FULLSCREEN)
	fullscreen.fill(black)

	# PASTE PICTURE ON FULLSCREEN
	fullscreen.blit(ff60, ff60Pos)
	pygame.display.flip()
	y = 0
	y_slide = 0

	while True:
		for event in pygame.event.get():
			action = check_joy_event(event)
			#button
			if action == 'KEYBOARD' or action == 'JOYBUTTONB' or action == 'JOYBUTTONA':
				if y < 1:
					load.play()
					fullscreen.blit(load60, load60Pos)
					pygame.display.flip()
					time.sleep(1)
					pygame.display.quit()
					pygame.quit()
					if Gamedb[0] == False:
						os.system('echo \"%s 60\" >> %s' % (CleanedGame,AutoFreqDB))
					else:
						if Gamedb[1] != '60':
							modificarLinea(AutoFreqDB,CleanedGame,'%s 60'%CleanedGame)
					return 60

				if y == 1:
					load.play()
					fullscreen.blit(load50, load50Pos)
					pygame.display.flip()
					time.sleep(1)
					pygame.display.quit()
					pygame.quit()
					if Gamedb[0] == False:
						os.system('echo \"%s 50\" >> %s' % (CleanedGame,AutoFreqDB))
					else:
						if Gamedb[1] != '50':
							modificarLinea(AutoFreqDB,CleanedGame,'%s 50'%CleanedGame)
					return 50
			#down
			elif action == 'DOWNKEYBOARD' or action == 'JOYHATDOWN' or action == 'AXISDOWN':
				if y < 1:
					y = y + 1
					cursor.play()
					fullscreen.blit(ff50, ff50Pos)
					pygame.display.flip()

			#up
			elif action == 'UPKEYBOARD' or action == 'JOYHATUP' or action == 'AXISUP':
				if y > 0:
					y = y - 1
					cursor.play()
					fullscreen.blit(ff60, ff60Pos)
					pygame.display.flip()

def selector_stretch():
	get_xy_screen()
	pygame.mixer.pre_init(44100, -16, 1, 512)
	pygame.init()
	pygame.display.init()
	pygame.mouse.set_visible(0)
	
	get_retropie_joy_map()
	
	# FF files
	nojoy = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/stretch/nojoy.png')
	nojoyPos = nojoy.get_rect()
	nojoyPos.center = ((x_screen/2), (y_screen/2))
	ARyes = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/stretch/yes.png')
	ARyesPos = ARyes.get_rect()
	ARyesPos.center = ((x_screen/2), (y_screen/2))
	STRETCHcancel = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/stretch/cancel.png')
	STRETCHcancelPos = STRETCHcancel.get_rect()
	STRETCHcancelPos.center = ((x_screen/2), (y_screen/2))
	ARyesenabled = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/stretch/yesenabled.png')
	ARyesenabledPos = ARyesenabled.get_rect()
	ARyesenabledPos.center = ((x_screen/2), (y_screen/2))
	STRETCHcancelenabled = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/stretch/cancelenabled.png')
	STRETCHcancelenabledPos = STRETCHcancelenabled.get_rect()
	STRETCHcancelenabledPos.center = ((x_screen/2), (y_screen/2))
	cursor = pygame.mixer.Sound("/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/stretch/cursor.wav")
	load = pygame.mixer.Sound("/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/stretch/load.wav")

	# SET SCREEN
	fullscreen = pygame.display.set_mode((x_screen,y_screen), FULLSCREEN)
	fullscreen.fill(black)

	# PASTE PICTURE ON FULLSCREEN
	fullscreen.blit(ARyes, ARyesPos)
	pygame.display.flip()
	y = 0
	y_slide = 0


	while True:
		for event in pygame.event.get():
			action = check_joy_event(event)
			#button
			if action == 'KEYBOARD' or action == 'JOYBUTTONB' or action == 'JOYBUTTONA':
				if y < 1:
					load.play()
					fullscreen.blit(ARyesenabled, ARyesenabledPos)
					pygame.display.flip()
					time.sleep(1)
					pygame.display.quit()
					pygame.quit()
					return True

				if y == 1:
					load.play()
					fullscreen.blit(STRETCHcancelenabled, STRETCHcancelenabledPos)
					pygame.display.flip()
					time.sleep(1)
					pygame.display.quit()
					pygame.quit()
					return False

			#down
			elif action == 'DOWNKEYBOARD' or action == 'JOYHATDOWN' or action == 'AXISDOWN':
				if y < 1:
					y = y + 1
					cursor.play()
					fullscreen.blit(STRETCHcancel, STRETCHcancelPos)
					pygame.display.flip()

			#up
			elif action == 'UPKEYBOARD' or action == 'JOYHATUP' or action == 'AXISUP':
				if y > 0:
					y = y - 1
					cursor.play()
					fullscreen.blit(ARyes, ARyesPos)
					pygame.display.flip()

def selector_encapsulate():
	get_xy_screen()
	pygame.mixer.pre_init(44100, -16, 1, 512)
	pygame.init()
	pygame.display.init()
	pygame.mouse.set_visible(0)
	get_retropie_joy_map()
	
	# FF files
	nojoy = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/encapsulator/nojoy.png')
	nojoyPos = nojoy.get_rect()
	nojoyPos.center = ((x_screen/2), (y_screen/2))
	ff60 = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/encapsulator/crop.png')
	ff60Pos = ff60.get_rect()
	ff60Pos.center = ((x_screen/2), (y_screen/2))
	ff50 = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/encapsulator/forc.png')
	ff50Pos = ff50.get_rect()
	ff50Pos.center = ((x_screen/2), (y_screen/2))
	load60 = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/encapsulator/cropload.png')
	load60Pos = load60.get_rect()
	load60Pos.center = ((x_screen/2), (y_screen/2))
	load50 = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/encapsulator/forcload.png')
	load50Pos = load50.get_rect()
	load50Pos.center = ((x_screen/2), (y_screen/2))
	cursor = pygame.mixer.Sound("/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/encapsulator/cursor.wav")
	load = pygame.mixer.Sound("/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/encapsulator/load.wav")

	# SET SCREEN
	fullscreen = pygame.display.set_mode((x_screen,y_screen), FULLSCREEN)
	fullscreen.fill(black)

	# PASTE PICTURE ON FULLSCREEN
	fullscreen.blit(ff60, ff60Pos)
	pygame.display.flip()
	y = 0
	y_slide = 0


	while True:
		for event in pygame.event.get():
			action = check_joy_event(event)
			#button
			if action == 'KEYBOARD' or action == 'JOYBUTTONB' or action == 'JOYBUTTONA':
				if y < 1:
					load.play()
					fullscreen.blit(load60, load60Pos)
					pygame.display.flip()
					time.sleep(1)
					#pygame.display.quit()
					pygame.quit()
					return 0

				if y == 1:
					load.play()
					fullscreen.blit(load50, load50Pos)
					pygame.display.flip()
					time.sleep(1)
					#pygame.display.quit()
					pygame.quit()
					return 1

			#down
			elif action == 'DOWNKEYBOARD' or action == 'JOYHATDOWN' or action == 'AXISDOWN':
				if y < 1:
					y = y + 1
					cursor.play()
					fullscreen.blit(ff50, ff50Pos)
					pygame.display.flip()

			#up
			elif action == 'UPKEYBOARD' or action == 'JOYHATUP' or action == 'AXISUP':
				if y > 0:
					y = y - 1
					cursor.play()
					fullscreen.blit(ff60, ff60Pos)
					pygame.display.flip()
def selector_allvideos():
	get_xy_screen()
	pygame.mixer.pre_init(44100, -16, 1, 512)
	pygame.init()
	pygame.display.init()
	pygame.mouse.set_visible(0)
	
	get_retropie_joy_map()
	
	# FF files
	option1 = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/videoplayer/allvideos/option1.png')
	option1Pos = option1.get_rect()
	option1Pos.center = ((x_screen/2), (y_screen/2))
	option2 = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/videoplayer/allvideos/option2.png')
	option2Pos = option2.get_rect()
	option2Pos.center = ((x_screen/2), (y_screen/2))
	option1_ena = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/videoplayer/allvideos/option1_ena.png')
	option1_enaPos = option1_ena.get_rect()
	option1_enaPos.center = ((x_screen/2), (y_screen/2))
	option2_ena = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/videoplayer/allvideos/option2_ena.png')
	option2_enaPos = option2_ena.get_rect()
	option2_enaPos.center = ((x_screen/2), (y_screen/2))
	cursor = pygame.mixer.Sound("/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/videoplayer/allvideos/cursor.wav")
	load = pygame.mixer.Sound("/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/videoplayer/allvideos/load.wav")

	# SET SCREEN
	fullscreen = pygame.display.set_mode((x_screen,y_screen), FULLSCREEN)
	fullscreen.fill(black)

	# PASTE PICTURE ON FULLSCREEN
	fullscreen.blit(option1, option1Pos)
	pygame.display.flip()
	y = 0
	y_slide = 0


	while True:
		for event in pygame.event.get():
			action = check_joy_event(event)
			#button
			if action == 'KEYBOARD' or action == 'JOYBUTTONB' or action == 'JOYBUTTONA':
				if y < 1:
					load.play()
					fullscreen.blit(option1_ena, option1_enaPos)
					pygame.display.flip()
					time.sleep(1)
					pygame.display.quit()
					pygame.quit()
					return False

				if y == 1:
					load.play()
					fullscreen.blit(option2_ena, option2_enaPos)
					pygame.display.flip()
					time.sleep(1)
					pygame.display.quit()
					pygame.quit()
					return True

			#down
			elif action == 'DOWNKEYBOARD' or action == 'JOYHATDOWN' or action == 'AXISDOWN':
				if y < 1:
					y = y + 1
					cursor.play()
					fullscreen.blit(option2, option2Pos)
					pygame.display.flip()

			#up
			elif action == 'UPKEYBOARD' or action == 'JOYHATUP' or action == 'AXISUP':
				if y > 0:
					y = y - 1
					cursor.play()
					fullscreen.blit(option1, option1Pos)
					pygame.display.flip()
