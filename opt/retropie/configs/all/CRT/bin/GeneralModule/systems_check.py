#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Retropie code integration by -krahs-. Check if execution string and others
in es_systems.cfg are right if not, system will reboot.

https://github.com/krahsdevil/crt-for-retropie/

Copyright (C)  2018/2020 -krahs- - https://github.com/krahsdevil/

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation, either version 2 of the License, or (at your option) any
later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import os, sys
import xml.etree.ElementTree as ET

CRT_PATH = "/opt/retropie/configs/all/CRT"
RESOURCES_PATH = os.path.join(CRT_PATH, "bin/GeneralModule")
sys.path.append(RESOURCES_PATH)

sys.dont_write_bytecode = True

from launcher_module.core_paths import CRT_LAUNCHER_FILE, \
                                       ES_SYSTEMS_PRI_FILE, \
                                       CRT_ES_SYSTEMDB_FILE
from launcher_module.file_helpers import md5_file, modify_line
from systems_check_db import SYSTEMS, LAST_HASH
from launcher_module.utils import show_info

oTree = None
oRoot = None
bReboot = False
lSysInfo = [("EMULATIONSTATION ES_SYSTEMS.CFG FIXED:", "OK")]
lSysTit = "SYSTEM WILL REBOOT NOW, PLEASE WAIT"

def check_xml_file(p_sFile):
    """
    Analize es_systems.cfg a check if execution string is correct in
    order to have CRT Edition integration. Also checks if any special 
    system is missing (non default system on retropie).
    sCore will be empty if the system don't require any change in 
    execution string. By default sCore will be the system but special
    systems like retropie o CRT menu has a different format of
    launching.
    """
    global oTree
    global oRoot
    global bReboot
    global lSysInfo
    bCheck = False
    oTree = ET.parse(p_sFile)
    oRoot = oTree.getroot()
    for sys in oRoot.iter('system'):
        sSystem = sys.find('name').text
        sCore = sSystem
        sFullName = sys.find('fullname').text
        sCommand = sys.find('command').text
        sTheme = sys.find('theme').text
        for item in SYSTEMS:
            if sSystem == item:
                # set checked
                SYSTEMS[sSystem]["check"] = True
                # set core name, empty if is 1CRT or Retropie
                sCore = SYSTEMS[sSystem]["core"]
                if sTheme != SYSTEMS[sSystem]["theme"]:
                    sys.find('theme').text = SYSTEMS[sSystem]["theme"]
                    lSysInfo.append(("-- CHANGED theme for %s" % \
                             sSystem, "OK"))
                    bCheck = True
        if sCore:
            sExecLine = "python %s " % CRT_LAUNCHER_FILE
            sExecLine += "%%ROM%% %s " % sCore
            sExecLine += "dummy"
            if sExecLine != sCommand and not "force" in sCommand :
                lSysInfo.append(("-- CHANGED exec line for %s" % \
                                 sSystem, "OK"))
                sys.find('command').text = sExecLine
                bCheck = True
    if bCheck:
        oTree.write(p_sFile)
        bReboot = True

def check_miss_systems(p_sFile):
    """ Add special systems missing on es_system.cfg """
    global bReboot
    global lSysInfo
    bCheck = False
    lCheckedSys = [val['check'] for key, val in SYSTEMS.iteritems()]
    sNewFile = ""
    if False in lCheckedSys:
        with open(p_sFile, "r+") as file:
            sFile = file.readlines()
            file.seek(0)
            for line in sFile:
                if "</systemList>" in line:  # ending tag in CFG
                    for key, val in SYSTEMS.iteritems():
                        if not val['check'] and val['xml']:
                            sNewFile += val['xml']
                            lSysInfo.append(("-- APPEND config for %s" % \
                                             key, "OK"))
                            bCheck = True
                sNewFile += line
            if bCheck:
                file.write(sNewFile)
                file.truncate()
                bReboot = True

def hash_check(p_sFile):
    """ 
    Compare saved hash of last es_system.cfg changes and 
    compare with current.
    """
    sHashLast = LAST_HASH
    sHashFile = md5_file(p_sFile)
    if sHashLast != sHashFile:
        return False
    return True

def update_last_hash(p_sFile):
    """ Update last hash if any change """
    sHashFile = md5_file(p_sFile)
    modify_line(CRT_ES_SYSTEMDB_FILE, "LAST_HASH", 
                "LAST_HASH = \"%s\"" % sHashFile)

""" main program """
# only analize or change file if hash is different
if not hash_check(ES_SYSTEMS_PRI_FILE):
    check_xml_file(ES_SYSTEMS_PRI_FILE)
    check_miss_systems(ES_SYSTEMS_PRI_FILE)
    update_last_hash(ES_SYSTEMS_PRI_FILE)

# force a reboot if any change is detected
if bReboot:
    show_info(lSysInfo, lSysTit, 13000)
    os.system('reboot')