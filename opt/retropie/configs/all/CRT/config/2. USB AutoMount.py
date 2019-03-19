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
import os
import sys
import pygame
import time
import commands
import subprocess
from pygame.locals import *

sys.path.append('/opt/retropie/configs/all/CRT/bin/SelectorsModule/')
sys.path.append('/opt/retropie/configs/all/CRT/bin/GeneralModule/')
sys.path.append('/opt/retropie/configs/all/CRT/')

from selector_module_functions import get_retropie_joy_map
from selector_module_functions import check_joy_event

os.system('clear')

x_screen = 0
y_screen = 0

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
get_xy_screen()
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
pygame.display.init()
pygame.mouse.set_visible(0)
get_retropie_joy_map()


# VARIABLES
state_up = 0
state_down = 0
state_left = 0
state_right = 0
threshold = 1000 # Analogic middle to debounce
joystick = 0 # 0 is the 1sf joystick

# FF files
wait = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/automount/wait.png')
extract = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/automount/extract.png')
nojoy = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/automount/nojoy.png')

enabled = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/automount/enabled.png')
disabled = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/automount/disabled.png')
cancel = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/automount/cancel.png')
yes = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/automount/yes.png')
cancelenabled = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/automount/cancelenabled.png')
yesenabled = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/automount/yesenabled.png')

enabled_wej = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/automount/enabled_wej.png')
cancel_wej = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/automount/cancel_wej.png')
yes_wej = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/automount/yes_wej.png')
cancelenabled_wej = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/automount/cancelenabled_wej.png')
yesenabled_wej = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/automount/yesenabled_wej.png')
eject_wej = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/automount/eject_wej.png')
ejectenabled_wej = pygame.image.load('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/automount/ejectenabled_wej.png')

cursor = pygame.mixer.Sound("/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/automount/cursor.wav")
load = pygame.mixer.Sound("/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/automount/load.wav")
os.system('clear')
def InstallServiceAutomount():
	if os.path.exists('/opt/retropie/configs/all/CRT/bin/AutomountService/CRT-Automount.service') and os.path.exists('/opt/retropie/configs/all/CRT/bin/AutomountService/CRT-Automount.py'):
		os.system('sudo cp /opt/retropie/configs/all/CRT/bin/AutomountService/CRT-Automount.service /etc/systemd/system/CRT-Automount.service > /dev/null 2>&1')
		os.system('sudo systemctl enable CRT-Automount.service > /dev/null 2>&1')
		os.system('sudo systemctl start CRT-Automount.service > /dev/null 2>&1')
	else:
		pygame.display.quit()
		pygame.quit()
		sys.exit()

def DesInstallServiceAutomount():
	if os.path.exists('/opt/retropie/configs/all/CRT/bin/AutomountService/CRT-Automount.service') and os.path.exists('/opt/retropie/configs/all/CRT/bin/AutomountService/CRT-Automount.py'):
		os.system('sudo systemctl disable CRT-Automount.service > /dev/null 2>&1')
		os.system('sudo systemctl stop CRT-Automount.service > /dev/null 2>&1')
		os.system('sudo rm /etc/systemd/system/CRT-Automount.service > /dev/null 2>&1')
		os.system("sudo umount -l /home/pi/RetroPie/roms > /dev/null 2>&1")
		os.system("sudo umount -l /home/pi/RetroPie/BIOS > /dev/null 2>&1")
		os.system("sudo umount -l /opt/retropie/configs/all/emulationstation/gamelists > /dev/null 2>&1")
		output = commands.getoutput('ps -A')
		if 'emulationstatio' in output:
			os.system('touch /tmp/es-restart && pkill -f \"/opt/retropie/supplementary/.*/emulationstation([^.]|$)\"')
			os.system('clear')
	else:
		pygame.display.quit()
		pygame.quit()
		sys.exit()


# SET SCREEN
fullscreen = pygame.display.set_mode((x_screen,y_screen), FULLSCREEN)
fullscreen.fill((0,0,0))
# PASTE PICTURE ON FULLSCREEN
fullscreen.blit(wait, (119,80))
pygame.display.flip()
time.sleep(1)
CheckService = commands.getoutput('systemctl list-units --all | grep \"CRT-Automount.service\"')
if 'CRT-Automount.service' in CheckService:
	ServiceExist = True
	if 'running' in CheckService:
		ServiceRunning = True
		if os.path.exists('/opt/retropie/configs/all/CRT/bin/AutomountService/mounted.cfg'):
			MountedFile = open('/opt/retropie/configs/all/CRT/bin/AutomountService/mounted.cfg', 'r')
			MountedPaths = MountedFile.readlines()
			#MountedPaths = MountedPaths.split(' ')
			MountedFile.close()
			Frame = enabled_wej
			option1 = yes_wej
			option1_ENA = yesenabled_wej
			option2 = cancel_wej
			option2_ENA = cancelenabled_wej
			option3 = eject_wej
			option3_ENA = ejectenabled_wej
			MAXoptions = 2
		else:
			Frame = enabled
			option1 = yes
			option1_ENA = yesenabled
			option2 = cancel
			option2_ENA = cancelenabled
			MAXoptions = 1
	else:
		ServiceRunning = False
		Frame = disabled
		option1 = yes
		option1_ENA = yesenabled
		option2 = cancel
		option2_ENA = cancelenabled
		MAXoptions = 1
else:
	ServiceExist = False
	ServiceRunning = False
	Frame = disabled
	option1 = yes
	option1_ENA = yesenabled
	option2 = cancel
	option2_ENA = cancelenabled
	MAXoptions = 1

def quit_moudule():
	pygame.display.quit()
	pygame.quit()
	sys.exit()

fullscreen.blit(Frame, (119,80))
fullscreen.blit(option1, (119,116))
pygame.display.flip()

y = 0


while True:
	for event in pygame.event.get():
		action = check_joy_event(event)
		#button
		if action == 'KEYBOARD' or action == 'JOYBUTTONB' or action == 'JOYBUTTONA':
			if y < 1:
				load.play()
				fullscreen.blit(option1_ENA, (119,116))
				pygame.display.flip()
				time.sleep(1)
				if ServiceRunning == True:
					DesInstallServiceAutomount()
				elif ServiceRunning == False:
					InstallServiceAutomount()
				quit_moudule()

			if y == 1:
				load.play()
				fullscreen.blit(option2_ENA, (119,116))
				pygame.display.flip()
				time.sleep(1)
				quit_moudule()

			if y == 2:
				load.play()
				fullscreen.blit(option3_ENA, (119,116))
				pygame.display.flip()
				time.sleep(1)
				fullscreen.blit(extract, (119,80))
				pygame.display.flip()
				time.sleep(3)
				os.system('sudo umount %s > /dev/null 2>&1' % MountedPaths[0])
				while True:
					if os.path.exists('/opt/retropie/configs/all/CRT/bin/AutomountService/umounted.cfg'):
						break
				quit_moudule()

		#down
		elif action == 'DOWNKEYBOARD' or action == 'JOYHATDOWN' or action == 'AXISDOWN':
			if y < MAXoptions:
				y = y + 1
				cursor.play()
				if y == 1:
					fullscreen.blit(option2, (119,116))
				elif y == 2:
					fullscreen.blit(option3, (119,116))
				pygame.display.flip()

		#up
		elif action == 'UPKEYBOARD' or action == 'JOYHATUP' or action == 'AXISUP':
			if y > 0:
				y = y - 1
				cursor.play()
				if y == 1:
					fullscreen.blit(option2, (119,116))
				elif y == 0:
					fullscreen.blit(option1, (119,116))
				pygame.display.flip()
quit_moudule()

