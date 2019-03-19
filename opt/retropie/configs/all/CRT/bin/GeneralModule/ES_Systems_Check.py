#!/usr/bin/python
# coding: utf-8
# Retropie code/integration by -krahs- (2018)

import struct
import os
import os.path
import sys
import shutil
import pygame
import time
import subprocess
import commands

from math import *
from pygame.locals import *

sys.path.append('/opt/retropie/configs/all/CRT/')
sys.path.append('/opt/retropie/configs/all/CRT/bin/GeneralModule/')
from general_functions import *

import xml.etree.ElementTree as ET


all_lines_moded = "none"
pcenginecd_check = False
mame_tate_check = False
advmame_tate_check = False
fba_tate_check = False
crt_check = False
retropie_check = False

XMLChanged = False
EsSystemcfg = "/etc/emulationstation/es_systems.cfg"
tree = ET.parse(EsSystemcfg)
root = tree.getroot()

for system in root.iter('system'):
	name = system.find('name').text
	fullname = system.find('fullname').text
	command = system.find('command').text
	if name == "pcenginecd":
		fullcommand = "python /opt/retropie/configs/all/CRT/bin/GeneralModule/emulator_launcher.py %s pcenginecd dummy" % '%ROM%'
		if fullcommand != command:
			system.find('command').text = fullcommand
			XMLChanged = True
		pcenginecd_check = True
		
	elif name == "mame-libretro-tate":
		fullcommand = "python /opt/retropie/configs/all/CRT/bin/GeneralModule/emulator_launcher.py %s mame-libretro dummy" % '%ROM%'
		if fullcommand != command:
			system.find('command').text = fullcommand
			XMLChanged = True
		mame_tate_check = True
	elif name == "mame-advmame":
		FoundTheme = system.find('theme').text
		if FoundTheme != "mame-advmame":
			system.find('theme').text = "mame-advmame"
			XMLChanged = True
		fullcommand = "python /opt/retropie/configs/all/CRT/bin/GeneralModule/emulator_launcher.py %s mame-advmame dummy" % '%ROM%'
		if fullcommand != command:
			system.find('command').text = fullcommand
			XMLChanged = True
	elif name == "mame-advmame-tate":
		fullcommand = "python /opt/retropie/configs/all/CRT/bin/GeneralModule/emulator_launcher.py %s mame-advmame dummy" % '%ROM%'
		if fullcommand != command:
			system.find('command').text = fullcommand
			XMLChanged = True
		advmame_tate_check = True
	elif name == "fba-tate":
		fullcommand = "python /opt/retropie/configs/all/CRT/bin/GeneralModule/emulator_launcher.py %s fba dummy" % '%ROM%'
		if fullcommand != command:
			system.find('command').text = fullcommand
			XMLChanged = True
		fba_tate_check = True
	elif name == "1CRT":
		crt_check = True
	elif name == "retropie":
		retropie_check = True
	else:
		fullcommand = "python /opt/retropie/configs/all/CRT/bin/GeneralModule/emulator_launcher.py %s %s dummy" % ("%ROM%",name)
		if fullcommand != command:
			system.find('command').text = fullcommand
			XMLChanged = True

if XMLChanged == True:
	tree.write(EsSystemcfg)

if pcenginecd_check == False or mame_tate_check == False or advmame_tate_check == False or fba_tate_check == False or crt_check == False:
	XMLStringPCEnginceCD = "  <system>\n    <name>pcenginecd</name>\n    <fullname>PC Engine CD</fullname>\n    <path>/home/pi/RetroPie/roms/pcenginecd</path>\n    <extension>.cue .CUE .ccd .CCD</extension>\n    <command>python /opt/retropie/configs/all/CRT/bin/GeneralModule/emulator_launcher.py %ROM% pcenginecd dummy</command>\n    <platform>pcenginecd</platform>\n    <theme>pcenginecd</theme>\n  </system>\n"

	XMLStringMAMETate = "  <system>\n    <name>mame-libretro-tate</name>\n    <fullname>mame-libretro TATE</fullname>\n    <path>/home/pi/RetroPie/roms/mame_tate</path>\n    <extension>.zip .ZIP</extension>\n    <command>python /opt/retropie/configs/all/CRT/bin/GeneralModule/emulator_launcher.py %ROM% mame-libretro dummy</command>\n    <platform>arcade</platform>\n    <theme>mame_tate</theme>\n  </system>\n"

	XMLStringAdvMAMETate = "  <system>\n    <name>mame-advmame-tate</name>\n    <fullname>advmame TATE</fullname>\n    <path>/home/pi/RetroPie/roms/advmame_tate</path>\n    <extension>.zip .ZIP</extension>\n    <command>python /opt/retropie/configs/all/CRT/bin/GeneralModule/emulator_launcher.py %ROM% mame-advmame dummy</command>\n    <platform>arcade</platform>\n    <theme>advmame_tate</theme>\n  </system>\n"

	XMLStringFBATate = "  <system>\n    <name>fba-tate</name>\n    <fullname>Final Burn Alpha-TATE</fullname>\n    <path>/home/pi/RetroPie/roms/fba_libretro_tate</path>\n    <extension>.zip .ZIP</extension>\n    <command>python /opt/retropie/configs/all/CRT/bin/GeneralModule/emulator_launcher.py %ROM% fba dummy</command>\n    <platform>arcade</platform>\n    <theme>fba_libretro_tate</theme>\n  </system>\n"

	XMLStringCRT = "  <system>\n    <name>1CRT</name>\n    <fullname>CRT Utilities</fullname>\n    <path>/opt/retropie/configs/all/CRT/config</path>\n    <extension>.py</extension>\n    <command>python %ROM%</command>\n    <platform />\n    <theme>crt</theme>\n  </system>\n"

	with open(EsSystemcfg, "r") as file:
		for line in file:
			if "</systemList>" in line:
				if pcenginecd_check == False:
					all_lines_moded = "%s%s" % (all_lines_moded,XMLStringPCEnginceCD)
				if mame_tate_check == False:
					all_lines_moded = "%s%s" % (all_lines_moded,XMLStringMAMETate)
				if advmame_tate_check == False:
					all_lines_moded = "%s%s" % (all_lines_moded,XMLStringAdvMAMETate)
				if fba_tate_check == False:
					all_lines_moded = "%s%s" % (all_lines_moded,XMLStringFBATate)
				if crt_check == False:
					all_lines_moded = "%s%s" % (all_lines_moded,XMLStringCRT)
				all_lines_moded = "%s%s" % (all_lines_moded,line)
			else:
				if all_lines_moded == "none":
					all_lines_moded = line
				else:
					all_lines_moded = "%s%s" % (all_lines_moded,line)
	with open(EsSystemcfg, "w") as file:
		file.write(all_lines_moded)

if XMLChanged == True:
	infos = "System needs to reboot, please wait..."
	infos2 = ""
	something_is_bad(infos,infos2)
	os.system('reboot')