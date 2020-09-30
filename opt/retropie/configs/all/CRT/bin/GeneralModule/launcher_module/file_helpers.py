#!/usr/bin/python3
# -*- coding: utf-8 -*-


"""
file_helpers.py.

https://github.com/krahsdevil/crt-for-retropie/

Copyright (C)  2018/2020 -krahs- - https://github.com/krahsdevil/
Copyright (C)  2019 dskywalk - http://david.dantoine.org

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

import os, logging
import hashlib, shutil, random, re
import xml.etree.ElementTree as ET

from launcher_module.core_paths import TMP_LAUNCHER_PATH, CRT_ROOT_PATH, ES_CFG_FILE

def remove_line(p_sFile, p_sRemoveMask):
    p_bCheck = False
    if not os.path.isfile(p_sFile):
        return None
    with open(p_sFile,"r+") as f:
        new_file = f.readlines()
        f.seek(0) # rewind
        for line in new_file:
            if p_sRemoveMask not in line:
                f.write(line) # valid line
            else: p_bCheck = True
        f.truncate() # remove everything after the last write
        return p_bCheck

def find_string(p_sFile, p_sString):
    p_bCheck = False
    if not os.path.isfile(p_sFile):
        return None
    with open(p_sFile,"r") as f:
        new_file = f.readlines()
        f.seek(0) # rewind
        for line in new_file:
            if p_sString in line:
                p_bCheck = True # found string
        return p_bCheck

def modify_line(p_sFile, p_sLineToFind, p_sNewLine, p_bEndLine = True):
    if not os.path.isfile(p_sFile):
        return None
    with open(p_sFile, "r+") as f:
        new_file = f.readlines()
        f.seek(0) # rewind
        for line in new_file:
            if p_sLineToFind in line:
                line = p_sNewLine
                if p_bEndLine:
                    line += "\n"
            f.write(line) # new line
        f.truncate() # remove everything after the last write
        return True

def add_line(p_sFile, p_sNewLine, p_bEndLine = True):
    if not os.path.isfile(p_sFile):
        return None
    with open(p_sFile, "a") as f:
        line = p_sNewLine
        if p_bEndLine:
            line += "\n"
        f.write(line)

def ini_get(p_sFile, p_sFindMask, p_bFullData = False):
    if not os.path.isfile(p_sFile):
        return None
    with open(p_sFile, "r") as f:
        for line in f:
            lValues = line.strip()
            lValues = lValues.replace('"', '')
            lValues = lValues.replace('=',' ')
            lValues = re.sub(r' +', " ", lValues).split(' ')
            if p_sFindMask == lValues[0].strip():
                if p_bFullData:
                    return lValues
                else:
                    return lValues[-1].strip()
    return False

def ini_set(p_sFile, p_sKeyMask, p_sNewValue):
    if not os.path.isfile(p_sFile):
        return None
    with open(p_sFile, "r+") as f:
        new_file = f.readlines()
        f.seek(0) # rewind
        for line in new_file:
            lValues = line.strip()
            lValues = lValues.replace('"', '')
            lValues = lValues.replace('=',' ')
            lValues = re.sub(r' +', " ", lValues).split(' ')
            if p_sKeyMask == lValues[0].strip():
                line = '%s = "%s"\n' % (p_sKeyMask, p_sNewValue)
            f.write(line) # new line
        f.truncate() # remove everything after the last write
        return True

def ini_getlist(p_sFile, p_sFindMask):
    lValues = ini_get(p_sFile, p_sFindMask, True)
    if lValues:
        return lValues[1:]
    else:
        return []

def get_xml_value_esconfig(p_sFindMask, p_sFile = ES_CFG_FILE):
    """ 
    Find value for element in es_settings.cfg of Emulationstation
    by default. This file must have a <root> to be parsed. This
    function will try to read as it is, if not, create root of xml
    and look for the element.
    """
    p_bParsed = False
    p_sValue = None
    if not os.path.isfile(p_sFile):
        return None
    try:
        tree = ET.parse(p_sFile)
        root = tree.getroot()
        p_bParsed = True
    except:
        pass
    # create root to parse as regular xml
    if not p_bParsed:
        file = list(filter(None, open(p_sFile, "r").read().splitlines()))
        for line in file:        
            if "xml" in line and "version" in line:
                file.remove(line)
        file.insert(0, "<root>\n")
        file[-1] = file[-1].strip()+"\n"
        file.append("</root>\n")
        root = ET.fromstringlist(file)    
    # search the element
    for child in root:
        try:
            if child.attrib["name"] == p_sFindMask:
                p_sValue = child.attrib["value"]
                return p_sValue
        except:
            pass
    return False
                
def set_xml_value_esconfig(p_sFindMask, p_sValue, p_sFile = ES_CFG_FILE):
    """ 
    Find element and set a value in es_settings.cfg of Emulationstation
    by default. This file must have a <root> to be parsed. This function
    will try to read as it is, if not, create root of this xml file, and
    look for the element and change its value with modify_line function.
    """
    p_bParsed = False
    p_sLineToFind = None
    p_sNewLine = None
    p_sValueToChange = None
    if not os.path.isfile(p_sFile):
        return None
    try:
        tree = ET.parse(p_sFile)
        root = tree.getroot()
        p_bParsed = True
    except:
        pass
    # create root to parse as regular xml
    if not p_bParsed:
        file = list(filter(None, open(p_sFile, "r").read().splitlines()))
        for line in file:        
            if "xml" in line and "version" in line:
                file.remove(line)
        file.insert(0, "<root>\n")
        file[-1] = file[-1].strip()+"\n"
        file.append("</root>\n")
        root = ET.fromstringlist(file)    
    # search the element and save value and line
    for child in root:
        try:
            if child.attrib["name"] == p_sFindMask:
                p_sValueToChange = child.attrib["value"]
                p_sLineToFind = ET.tostring(child).decode("utf-8").strip()
                break
        except:
            pass
    # if found replace line with the new value
    if p_sLineToFind:
        p_sNewLine = p_sLineToFind.replace(p_sValueToChange, p_sValue)
        return modify_line(p_sFile, p_sLineToFind, p_sNewLine)
    return False

def md5_file(p_sFile):
    hasher = hashlib.md5()
    with open(p_sFile, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
    return hasher.hexdigest()
    
def generate_random_temp_filename(p_sFile):
    p_sRandom = str(md5_file(p_sFile))
    p_sRandom += "_" + str(random.randrange(1000, 9999))
    p_sTMPPath = os.path.join(TMP_LAUNCHER_PATH, p_sRandom)
    return p_sTMPPath

def remove_file(p_sFile):
    try:
        os.remove(p_sFile)
    except OSError:
        pass

def touch_file(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)
