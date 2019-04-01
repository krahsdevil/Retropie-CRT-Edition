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
#sys.path.insert(0, '/opt/retropie/configs/all/CRT/')
sys.path.append('/opt/retropie/configs/all/CRT/bin/SelectorsModule/')
sys.path.append('/opt/retropie/configs/all/CRT/bin/GeneralModule/')
sys.path.append('/opt/retropie/configs/all/CRT/')
from selector_module_functions import get_retropie_joy_map
from selector_module_functions import check_joy_event
from selector_module_functions import get_xy_screen
from pygame.locals import *
from general_functions import *

x_screen = 0
y_screen = 0

launchlegacypath = "/opt/retropie/configs/all/CRT/bin/GeneralModule"
launchlegacyfile = "emulator_launcher_legacy.py"
launchnewpath = "/opt/retropie/configs/all/CRT/bin/GeneralModule"
launchnewfile = "crt_launcher"
curlauncher = "none"
unslauncher = "none"
launcherinfo = "none"
launcherinfo2 = "none"

simblinkfile = "/opt/retropie/configs/all/CRT/bin/GeneralModule/emulator_launcher.py"

def check_launcher():
	global curlauncher
	global unslauncher
	global launcherinfo
	global launcherinfo2
	if not os.path.exists(simblinkfile):
		try:
			os.system('ln -s %s/%s %s' % (launchlegacypath, launchlegacyfile, simblinkfile))
		except:
			sys.exit()
	output = commands.getoutput('ls -l %s' % simblinkfile)
	if not '->' in output:
		sys.exit()
	if launchnewfile in output:
		curlauncher = launchnewpath + "/" + launchnewfile
		unslauncher = launchlegacypath + "/" + launchlegacyfile
		launcherinfo = "New CRT Launcher is active."
		launcherinfo2 = "Change to legacy?"
	elif launchlegacypath in output:
		curlauncher = launchlegacypath + "/" + launchlegacyfile
		unslauncher = launchnewpath + "/" + launchnewfile
		launcherinfo = "Legacy Launcher is active."
		launcherinfo2 = "Change to developing launcher?"

def change_selector():
	os.system('sudo rm %s'% simblinkfile)
	os.system('ln -s %s %s' % (unslauncher, simblinkfile))

def draw_move_pattern():
	fullscreen.fill(black)
	if y == 0:
		option1text = ">Yes"
		option2text = " Cancel"
	elif y == 1:
		option1text = " Yes"
		option2text = ">Cancel"
	title = myfont.render(launcherinfo, True, BlueLight)
	titlePos = title.get_rect()
	titlePos.midleft = (120, 85)
	title1 = myfont.render(launcherinfo2, True, BlueLight)
	title1Pos = title1.get_rect()
	title1Pos.midleft = (120, 95)
	
	option1 = myfont.render(option1text, True, white)
	option1Pos = option1.get_rect()
	option1Pos.midleft = (130, 110)
	option2 = myfont.render(option2text, True, white)
	option2Pos = option2.get_rect()
	option2Pos.midleft = (130, 120)
	fullscreen.blit(option1,option1Pos)
	fullscreen.blit(option2,option2Pos)
	fullscreen.blit(title,titlePos)
	fullscreen.blit(title1,title1Pos)
	pygame.display.flip()

get_xy_screen()
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
pygame.display.init()
pygame.mouse.set_visible(0)
get_retropie_joy_map()
red = pygame.Color(255, 0, 0)
black = pygame.Color(0, 0, 0)
white = pygame.Color(255,255,255)
BlueLight = pygame.Color(165,165,255)
myfont = pygame.font.Font("/opt/retropie/configs/all/CRT/config/PetMe64.ttf", 8)

fullscreen = pygame.display.set_mode((x_screen,y_screen), FULLSCREEN)

# PASTE PICTURE ON FULLSCREEN
y = 0
y_slide = 0

check_launcher()
draw_move_pattern()
while True:
	for event in pygame.event.get():
		action = check_joy_event(event)
		#button
		if action == 'KEYBOARD' or action == 'JOYBUTTONB' or action == 'JOYBUTTONA':
			if y < 1:
				change_selector()
				sys.exit()
				pygame.quit()

			if y == 1:
				sys.exit()
				pygame.quit()

		#down
		elif action == 'DOWNKEYBOARD' or action == 'JOYHATDOWN' or action == 'AXISDOWN':
			if y < 1:
				y = y + 1
				draw_move_pattern()

		#up
		elif action == 'UPKEYBOARD' or action == 'JOYHATUP' or action == 'AXISUP':
			if y > 0:
				y = y - 1
				draw_move_pattern()
