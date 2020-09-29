#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Retropie code integration by -krahs-. 

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

import os, sys, re, time, logging
import filecmp, subprocess
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(SCRIPT_DIR + "/../"))
from main_paths import MODULES_PATH
sys.path.append(MODULES_PATH)

from launcher_module.core_paths import CRT_RGB_SRV_FILE, CRT_RGB_SRV_PATH, \
                                       CRT_RGB_CORE_PATH, CRT_RGB_CORE_FILE

def clean_line(p_sLine):
    lValues = p_sLine.strip()
    lValues = lValues.replace('"', '')
    lValues = re.sub(r' +', " ", lValues).split('=')
    return lValues

def ini_sect_clean_file(p_sFile):
    if not os.path.isfile(p_sFile): return None
    with open(p_sFile, "r+") as f:
        p_bInSection = False
        new_file = f.readlines()
        f.seek(0) # rewind
        for line in new_file:
            lValues = clean_line(line)
            if lValues[0].startswith('[') and lValues[0].endswith(']'):
                    f.write('\n')
            if line.strip(): f.write(line)
        f.truncate() # remove everything after the last write

def ini_sect_get_key(p_sFile, p_sSection, p_sKeyMask):
    if not os.path.isfile(p_sFile): return None
    with open(p_sFile, "r") as f:
        p_bInSection = False
        for line in f:
            lValues = clean_line(line)
            if lValues[0].startswith('[') and lValues[0].endswith(']'):
                if p_bInSection: return None # value not found
                section = lValues[0].strip('[]')
                if p_sSection == section: p_bInSection = True
            if p_bInSection:
                if lValues[0] == p_sKeyMask:
                    value = "=".join(lValues[1:])
                    return value
    return False # section not found

def ini_sect_set_key(p_sFile, p_sSection, p_sKeyMask, p_sNewValue):
    if not os.path.isfile(p_sFile): return None
    with open(p_sFile, "r+") as f:
        p_bInSection = False
        p_bFound = False
        new_file = f.readlines()
        f.seek(0) # rewind
        for line in new_file:
            lValues = clean_line(line)
            if lValues[0].startswith('[') and lValues[0].endswith(']'):
                if p_bInSection: p_bInSection = False
                section = lValues[0].strip('[]')
                if p_sSection == section: p_bInSection = True
            if p_bInSection:
                if str(p_sKeyMask) == lValues[0].strip():
                    line = '%s=%s\n' % (str(p_sKeyMask), str(p_sNewValue))
                    p_bFound = True
            f.write(line) # new line
        f.truncate() # remove everything after the last write
    ini_sect_clean_file(p_sFile)
    return p_bFound

def ini_sect_empty_section(p_sFile, p_sSection, p_bRemove = False):
    if not os.path.isfile(p_sFile): return None
    with open(p_sFile, "r+") as f:
        p_bInSection = False
        p_bFound = False
        new_file = f.readlines()
        f.seek(0) # rewind
        for line in new_file:
            lValues = clean_line(line)
            if lValues[0].startswith('[') and lValues[0].endswith(']'):
                if p_bInSection: p_bInSection = False
                section = lValues[0].strip('[]')
                if p_sSection == section: 
                    if not p_bRemove:
                        f.write(line + '\n')
                    p_bFound = True
                    p_bInSection = True
            if p_bInSection: pass
            else: f.write(line) # new line
        f.truncate() # remove everything after the last write
    ini_sect_clean_file(p_sFile)
    return p_bFound

def ini_sect_add_key(p_sFile, p_sSection, p_sNewKey, p_sNewValue):
    if not os.path.isfile(p_sFile): return None
    ini_sect_create_section(p_sFile, p_sSection)
    p_sNewKeyLine = str(p_sNewKey) + "=" + str(p_sNewValue)
    with open(p_sFile, "r+") as f:
        p_bInSection = False
        p_bFound = False
        new_file = f.readlines()
        f.seek(0) # rewind
        for line in new_file:
            lValues = clean_line(line)
            if lValues[0].startswith('[') and lValues[0].endswith(']'):
                if p_bInSection: 
                    f.write(p_sNewKeyLine + '\n')
                    f.write('\n')
                    p_bInSection = False
                section = lValues[0].strip('[]')
                if p_sSection == section: 
                    p_bFound = True
                    p_bInSection = True
            if p_bInSection:
                if lValues[0]: f.write(line)
            else: f.write(line) # new line
        if p_bInSection:
            f.write(p_sNewKeyLine + '\n')
            f.write('\n')
        f.truncate() # remove everything after the last write
    ini_sect_clean_file(p_sFile)
    return p_bFound

def ini_set_check_section(p_sFile, p_sSection):
    if not os.path.isfile(p_sFile): return None
    with open(p_sFile, "r") as f:
        p_bFound = False
        for line in f:
            lValues = clean_line(line)
            if lValues[0].startswith('[') and lValues[0].endswith(']'):
                section = lValues[0].strip('[]')
                if p_sSection == section: 
                    p_bFound = True
                    break
    return p_bFound

def ini_sect_create_section(p_sFile, p_sSection):
    if not os.path.isfile(p_sFile):
        return None
    if not ini_set_check_section(p_sFile, p_sSection):
        with open(p_sFile, "a") as f:
            line = '\n\n[' + p_sSection + ']\n'
            f.write(line)
        ini_sect_clean_file(p_sFile)

def ini_sect_get_keys(p_sFile, p_sSection):
    if not os.path.isfile(p_sFile): return None
    p_lList = []
    with open(p_sFile, "r") as f:
        p_bInSection = False
        p_bFound = False
        for line in f:
            lValues = clean_line(line)
            if lValues[0].startswith('[') and lValues[0].endswith(']'):
                if p_bInSection: p_bInSection = False
                section = lValues[0].strip('[]')
                if p_sSection == section: 
                    p_bFound = True
                    p_bInSection = True
            if p_bInSection:
                if not line.startswith(('#', '[')) and line.strip() and '=' in line: 
                    key = lValues[0]
                    value = value = "=".join(lValues[1:])
                    p_lList.append([key, value])
    p_lList.sort()
    return p_lList

def compare_section(p_sFile, p_sSection, p_lList1):
    p_lList1.sort()
    p_lList2 = ini_sect_get_keys(p_sFile, p_sSection)
    p_lList2.sort()
    if len(p_lList1) != len(p_lList2): 
        logging.info("WARNING: number of keys in [%s] doesn't match" % p_sSection)
        return False
    p_bCheck = True
    for a, b in zip(p_lList1, p_lList2):
        if a[0] != b[0] or a[1] != b[1]: 
            logging.info("WARNING: [%s] | OK:%s=%s | WRONG:%s=%s" % \
                        (p_sSection, a[0], a[1], b[0], b[1]))
            p_bCheck = False
    if p_bCheck: logging.info("Configuration is OK for %s" % p_sSection)
    return p_bCheck

def sync_files(p_sFile1, p_sFile2, p_schmod = None):
    # p_sFile1 = source file
    # p_sFile2 = destination file
    # p_schmod = file rigths
    p_bSync = False
    try: 
        if not filecmp.cmp(p_sFile1, p_sFile2): p_bSync = True
    except:
        p_bSync = True
    if p_bSync:
        logging.info("WARNING: synchronizing %s " % p_sFile2)
        os.system('sudo cp \"%s\" \"%s\"' % (p_sFile1, p_sFile2))
        if p_schmod:
            logging.info("INFO: changing permissions to file")
            os.system('chmod +%s \"%s\"' % (p_schmod, p_sFile2))

class CRTdaemon(object):
    def __init__(self):
        self.install()
        
    def install(self):
        if not self.check():
            logging.info("WARNING: CRTDaemon is being reinstalled")
            self._remove_crtdaemon()
            self._install_crtdaemon()
    
    def check(self):
        if not self._check_service(CRT_RGB_SRV_FILE, 'load'):
            logging.info("WARNING: CRTDaemon is not loaded")
            return False
        elif not self._check_service(CRT_RGB_SRV_FILE, 'run'):
            return False
        logging.info("INFO: CRTDaemon is loaded")
        return True

    def _check_crtdaemon_files(self):
        """ Check if needed service files exists """
        bCheck01 = os.path.exists(CRT_RGB_SRV_PATH)
        bCheck02 = os.path.exists(CRT_RGB_CORE_PATH)
        if bCheck01 and bCheck02:
            logging.info("INFO: Found daemon files %s and %s" \
                         % (CRT_RGB_SRV_FILE, CRT_RGB_CORE_FILE))
            return True
        logging.info("ERROR: NOT found daemon files %s and %s" \
                     % (CRT_RGB_SRV_FILE, CRT_RGB_CORE_FILE))
        return False

    def _install_crtdaemon(self):
        if self._check_crtdaemon_files:
            os.system('sudo cp %s /etc/systemd/system/%s > /dev/null 2>&1' \
                      % (CRT_RGB_SRV_PATH, CRT_RGB_SRV_FILE))
            os.system('sudo chmod +x /etc/systemd/system/%s > /dev/null 2>&1' \
                      % CRT_RGB_SRV_FILE)
            os.system('sudo systemctl enable %s > /dev/null 2>&1' \
                      % CRT_RGB_SRV_FILE)
            logging.info("INFO: CRTDaemon reinstalled on system")

    def _remove_crtdaemon(self):
        if self._check_crtdaemon_files:
            os.system('sudo systemctl disable %s > /dev/null 2>&1' \
                      % CRT_RGB_SRV_FILE)
            os.system('sudo systemctl stop %s > /dev/null 2>&1' \
                      % CRT_RGB_SRV_FILE)
            os.system('sudo rm /etc/systemd/system/%s > /dev/null 2>&1' \
                      % CRT_RGB_SRV_FILE)
            logging.info("INFO: CRTDaemon cleaned on system")

    def _check_service(self, p_sService, p_sState):
        """
        This function will return true or false for this options:
        p_sState = 'load' return True if service is loaded
        p_sState = 'run'  return True if service is loaded
        """
        p_bLoaded = False
        p_bRunning = False
        p_sCommand = 'systemctl list-units --all | grep \"%s\"' % p_sService
        try: p_sOutput = subprocess.check_output(p_sCommand, shell=True).decode("utf-8")
        except: p_sOutput = ""
        if p_sService in p_sOutput:
            p_bLoaded = True
            if 'running' in p_sOutput:
                p_bRunning = True
        if p_sState == 'load': return p_bLoaded
        elif p_sState == 'run': return p_bRunning