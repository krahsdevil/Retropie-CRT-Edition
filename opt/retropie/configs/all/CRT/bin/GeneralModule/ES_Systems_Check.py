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

# TODO: use external config
CRT_PATH = '/opt/retropie/configs/all/CRT'
MODULES_PATH = os.path.join(CRT_PATH, 'bin/GeneralModule')
LAUNCHER_BIN = os.path.join(MODULES_PATH, 'emulator_launcher.py')

sys.path.append(CRT_PATH)
sys.path.append(MODULES_PATH)

# TODO: add a json config to avoid this :D
XMLStringPCEnginceCD = "  <system>\n    <name>pcenginecd</name>\n    <fullname>PC Engine CD</fullname>\n    <path>/home/pi/RetroPie/roms/pcenginecd</path>\n    <extension>.cue .CUE .ccd .CCD</extension>\n    <command>python /opt/retropie/configs/all/CRT/bin/GeneralModule/emulator_launcher.py %%ROM%% pcenginecd dummy</command>\n    <platform>pcenginecd</platform>\n    <theme>pcenginecd</theme>\n  </system>\n"

XMLStringMAMETate = "  <system>\n    <name>mame-libretro-tate</name>\n    <fullname>mame-libretro TATE</fullname>\n    <path>/home/pi/RetroPie/roms/mame_tate</path>\n    <extension>.zip .ZIP</extension>\n    <command>python /opt/retropie/configs/all/CRT/bin/GeneralModule/emulator_launcher.py %%ROM%% mame-libretro dummy</command>\n    <platform>arcade</platform>\n    <theme>mame_tate</theme>\n  </system>\n"

XMLStringAdvMAMETate = "  <system>\n    <name>mame-advmame-tate</name>\n    <fullname>advmame TATE</fullname>\n    <path>/home/pi/RetroPie/roms/advmame_tate</path>\n    <extension>.zip .ZIP</extension>\n    <command>python /opt/retropie/configs/all/CRT/bin/GeneralModule/emulator_launcher.py %%ROM%% mame-advmame dummy</command>\n    <platform>arcade</platform>\n    <theme>advmame_tate</theme>\n  </system>\n"

XMLStringFBATate = "  <system>\n    <name>fba-tate</name>\n    <fullname>Final Burn Alpha-TATE</fullname>\n    <path>/home/pi/RetroPie/roms/fba_libretro_tate</path>\n    <extension>.zip .ZIP</extension>\n    <command>python /opt/retropie/configs/all/CRT/bin/GeneralModule/emulator_launcher.py %%ROM%% fba dummy</command>\n    <platform>arcade</platform>\n    <theme>fba_libretro_tate</theme>\n  </system>\n"

XMLStringCRT = "  <system>\n    <name>1CRT</name>\n    <fullname>CRT Utilities</fullname>\n    <path>/opt/retropie/configs/all/CRT/config</path>\n    <extension>.py</extension>\n    <command>python %%ROM%%</command>\n    <platform />\n    <theme>crt</theme>\n  </system>\n"


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

SYSTEMS = {
    "pcenginecd": { "core": "pcenginecd", "check": False, "xml": XMLStringPCEnginceCD },
    "mame-libretro-tate": { "core": "mame-libretro", "check": False, "xml": XMLStringMAMETate },
    "mame-advmame": { "core": "mame-advmame", "check": False, "xml": None },
    "mame-advmame-tate": { "core": "mame-advmame", "check": False, "xml": XMLStringAdvMAMETate },
    "fba-tate": { "core": "fba", "check": False, "xml": XMLStringFBATate },
    "1CRT": { "core": "", "check": False, "xml": XMLStringCRT },
    "retropie": { "core": "", "check": False, "xml": None },
}


def test_system(name, fullname, command):
    global XMLChanged
    core_name = name
    command_dummy = "dummy"
    if name in SYSTEMS:
        SYSTEMS[name]["check"] = True       # set checked
        core_name = SYSTEMS[name]["core"]   # set core name

    if core_name: # only test command if core exists
        fullcommand = "python %s %%ROM%% %s %s" % (LAUNCHER_BIN, core_name, command_dummy)
        if fullcommand != command and not "force" in command :
            print("-- CHANGED: %s" % fullcommand )
            system.find('command').text = fullcommand
            XMLChanged = True


for system in root.iter('system'):
    name = system.find('name').text
    fullname = system.find('fullname').text
    command = system.find('command').text
    test_system(name, fullname, command)

if XMLChanged == True:
    tree.write(EsSystemcfg)

lsystems_checked = [val['check'] for key, val in SYSTEMS.iteritems()]

if False in lsystems_checked:
    with open(EsSystemcfg, "r") as file:
        for line in file:
            if "</systemList>" in line:  # ending tag in CFG
                for key, val in SYSTEMS.iteritems():
                    if not val['check'] and val['xml']:
                        all_lines_moded = "%s%s" % (all_lines_moded, val['xml'])
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
    infos2 = "es_systems.cfg fixed"
    something_is_bad(infos,infos2)
    os.system('reboot')
