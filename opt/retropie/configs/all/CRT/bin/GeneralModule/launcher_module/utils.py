#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Utilities for CRT Scripts

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
import os, subprocess, commands
import time, imp, re, logging
import pygame

from launcher_module.core_paths import CRT_ROOT_PATH, RETROPIE_EMULATORS_PATH, \
                                       RA_BIN_FILE, CRT_RA_HASHDB_FILE, \
                                       ROTMODES_TATE1_FILE, ROTMODES_TATE3_FILE
from launcher_module.file_helpers import md5_file, ini_get, touch_file, \
                                         add_line, modify_line
from launcher_module.core_choices_dynamic import choices
from distutils.version import LooseVersion

#
# simple plugin system
#

# returns a list of .py files and ignores __init__.py
def plugin_list(p_sPath):
    plugins = []
    possibleplugins = os.listdir(p_sPath)
    for pl in possibleplugins:
        location = os.path.join(p_sPath, pl)
        if pl.endswith(".py") and not pl.endswith("_.py"):
            sClass = pl[:-3]
            info = imp.find_module(sClass, [p_sPath])
            plugins.append({"name": sClass, "info": info})
    return plugins

# load module dinamically and his main class (same name as .py file)
# ex: userplugin.py, userplugin()
def plugin_load(p_oPlugin):
    _module = imp.load_module(p_oPlugin["name"], *p_oPlugin["info"])
    return getattr(_module, p_oPlugin["name"])

#
# CRT Team functions
#
def something_is_bad(infos,infos2):
    time.sleep(0.5)
    problem = "/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/media/info_splash_screen/problem.sh \"%s\" \"%s\"" % (infos, infos2)
    os.system(problem)

def get_screen_resolution():
    """ main function to get screen resolution """
    commandline = "cat /sys/class/graphics/fb0/virtual_size"
    output = commands.getoutput(commandline)
    VirtRes = output.replace(',',' ').split(' ')
    RES_X = int(VirtRes[0])
    RES_Y = int(VirtRes[1])
    return (RES_X, RES_Y)
    
def get_xy_screen():
    process = subprocess.Popen("fbset", stdout=subprocess.PIPE)
    output = process.stdout.read()
    for line in output.splitlines():
        if 'x' in line and 'mode' in line:
            ResMode = line
            ResMode = ResMode.replace('"','').replace('x',' ').split(' ')
            x_screen = int(ResMode[1])
            y_screen = int(ResMode[2])
            return (x_screen, y_screen)
            
def compact_rom_name(p_sRomName):
    sPreCleanedGame = re.sub('[^a-zA-Z0-9-_]+','', p_sRomName )
    sCleanedGame = re.sub(' ','', sPreCleanedGame)
    return sCleanedGame

def show_info(p_sMessage, p_sTitle = None, p_iTime = 2000):
    ch = choices()
    if p_sTitle:
        ch.set_title(p_sTitle)
    if type(p_sMessage) is str:
            ch.load_choices([(p_sMessage, "OK")])
    else:
        ch.load_choices(p_sMessage)
    ch.show(p_iTime)
    
def menu_options(p_sMessage, p_sTitle = None):
    ch = choices()
    if p_sTitle:
        ch.set_title(p_sTitle)
    if type(p_sMessage) is str:
            ch.load_choices([(p_sMessage, "OK")])
    else:
        ch.load_choices(p_sMessage)
    result = ch.run()
    return result

def check_process(p_sProcess, p_iTimes = 1):
    """ 
    Look for a process.
    Only a name can be passed or a list of them.
    If list is passed will break as soon as one of them is found.
    For a single process is possible to pass the number of times 
    that is found to be identified as 'found'; This is interesting 
    for emulationstation because application in retropie generates
    three 'emulationstatio' processes.
    """
    p_bCheck = 0
    if p_sProcess == "emulationstatio": p_iTimes = 3
    
    pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
    for pid in pids:
        try:
            procname = open(os.path.join('/proc', pid, 'comm'), 'rb').read()
            if type(p_sProcess) is list:
                if procname[:-1] in p_sProcess:
                    p_bCheck = p_iTimes
                    break
            elif type(p_sProcess) is str:
                if procname[:-1] == p_sProcess:
                    p_bCheck += 1
        except IOError:
            pass
    # p_iTimes >= 1 process was found
    p_bCheck = True if p_bCheck >= p_iTimes else False 
    return p_bCheck

def get_side():
    """ Check current side of EmulatioStation """
    iCurSide = 0
    if os.path.exists(ROTMODES_TATE1_FILE):
        iCurSide = 1
    elif os.path.exists(ROTMODES_TATE3_FILE):
        iCurSide = 3
    return iCurSide
    
def wait_process(p_sProcess, p_sState = 'stop', p_iTimes = 1, p_iWaitScs = 1):
    """
    This function will wait to start or stop for only one process or
    a list of them like emulators. By default will wait to stop with
    'p_sState' parameter but you can change it on call to 'stop'.
    If a list is passed, function will validate that at least one of
    them started or all are stopped.
    For a single process is possible to pass the number of times 
    that is found to be identified as 'found'; This is interesting 
    for emulationstation because application in retropie generates
    three 'emulationstatio' processes.
    """
    bProcessFound = None
    bCondition = False
    logging.info("INFO: waiting to %s processes: %s"%(p_sState, p_sProcess))
    if p_sState == 'start':
        bCondition = True
    while bProcessFound != bCondition:
        bProcessFound = check_process(p_sProcess, p_iTimes)
        time.sleep(p_iWaitScs)
    logging.info("INFO: wait finished")
    
class HideScreen(object):
    """ Class for hide the screen filling with a color """
    m_iRES_X = 0
    m_iRES_Y = 0
    m_PGoScreen = None
    m_PGFILLCOLOR = None
    BLACK = pygame.Color(0, 0, 0)
    WHITE = pygame.Color(255, 255, 255)
    PYGAME_FLAGS = (pygame.FULLSCREEN | pygame.NOFRAME)
    
    def __init__(self):
        self.__clean()
        
    def _pygame_initialization(self):
        self.m_iRES_X, self.m_iRES_Y = get_screen_resolution()
        pygame.init()
        pygame.mouse.set_visible(0)
        self.m_PGoScreen = pygame.display.set_mode((self.m_iRES_X, self.m_iRES_Y),
                                                    self.PYGAME_FLAGS)
    def _pygame_unload(self):
        pygame.display.quit()
        pygame.quit()

    def _prepare_color(self, p_sColor):
        oPGBGColor = "self." + p_sColor
        try:
            self.m_PGFILLCOLOR = eval(oPGBGColor)
            logging.info("HideScreen chosen color: {%s}" % p_sColor)
        except:
            self.m_PGFILLCOLOR = self.BLACK
            logging.info("HideScreen color {%s} " % p_sColor + \
                         "NOT defined, changing to BLACK")

    def fill(self, p_sColor = "BLACK", p_iMaxTime = 0):
        os.system("clear")
        self._prepare_color(p_sColor)
        self._pygame_initialization()
        try:
            self.m_PGoScreen.fill(self.m_PGFILLCOLOR)
            logging.info("HideScreen %s x %s applied" % \
                        (self.m_iRES_X, self.m_iRES_Y))
            if p_iMaxTime:
                time.sleep(p_iMaxTime)
        except:
            raise
        self.__clean()

    def __clean(self):
        os.system("clear")
        self._pygame_unload()
        
class ra_version_fixes():
    """
    This function will check version of current retroarch and
    apply some related version fixes.
    From some or in particular version actions will be taken
    like if it's is lower than v1.7.5 aspect_ratio_index value
    must be change.
    """
    m_sSystemCfgPath = ""
    m_sRAVersion = None
    m_sRAHash = ""
    def __init__(self, p_sSystemCfgPath = None):
        if not self._check_custom_ra_cfg(p_sSystemCfgPath):
            return
        self._check_ra_db()
        self._run()

    def _run(self):
        self._get_ra_version_from_db()
        self._apply_fixes()

    def _check_custom_ra_cfg(self, p_sSystemCfgPath):
        p_bCheck = False
        if not p_sSystemCfgPath:
            p_bCheck = False
            logging.info("WARNING: need a custom retroarch file to check")
        if not os.path.isfile(p_sSystemCfgPath):
            p_bCheck = False
            logging.info("WARNING: custom retroach config NOT found")
        else:
            p_bCheck = True
            self.m_sSystemCfgPath = p_sSystemCfgPath
        return p_bCheck

    def _check_ra_db(self):
        if not os.path.isfile(CRT_RA_HASHDB_FILE):
            touch_file(CRT_RA_HASHDB_FILE)
            logging.info("INFO: Created retroarch hash database")

    def _get_ra_version_from_db(self):
        logging.info("INFO: checking retroarch version")
        self.m_sRAHash = md5_file(RA_BIN_FILE)
        f = open(CRT_RA_HASHDB_FILE, "r")
        full_lines = f.readlines()
        f.close()

        for line in full_lines:
            if line != "\n":
                lValues = line.strip().split(' ')
                if self.m_sRAHash == lValues[1]:
                    self.m_sRAVersion = lValues[2]
                    logging.info("INFO: found hash in db: {%s} {%s}" % \
                                (self.m_sRAHash, self.m_sRAVersion))
                    break
        if not self.m_sRAVersion:
            self._add_ra_version_to_db()

    def _add_ra_version_to_db(self):
        # update file if not found
        output = commands.getoutput("%s --version" % RA_BIN_FILE)
        for line in output.splitlines():
            lValues = line.strip().split(' ')
            if 'RetroArch' in lValues[0]:
                self.m_sRAVersion = lValues[5]
                add_line(CRT_RA_HASHDB_FILE, "RetroArch %s %s" % \
                        (self.m_sRAHash, self.m_sRAVersion))
                logging.info("INFO: added new retroach hash to db: " + \
                             "{%s} {%s}" % (self.m_sRAHash, self.m_sRAVersion))

    def _apply_fixes(self):
        self._ra_aspect_ratio()

    def _ra_aspect_ratio(self):
        p_sVersion = "v1.7.5"
        p_sRatioNew = "23" # default 1.7.5 value
        p_sRatioCur = ""
        if LooseVersion(self.m_sRAVersion) < LooseVersion(p_sVersion):
            p_sRatioNew = "22"
        p_sRatioCur = ini_get(self.m_sSystemCfgPath, "aspect_ratio_index")
        logging.info("INFO: Checking if aspect ratio number is %s" % p_sRatioNew)
        if p_sRatioNew != p_sRatioCur.replace('"', ''):
            modify_line(self.m_sSystemCfgPath, "aspect_ratio_index",
                        "aspect_ratio_index = \"%s\"" % p_sRatioNew)
            logging.info("INFO: fixed: %s version: %s ratio: %s (was %s)" % \
                        (self.m_sSystemCfgPath, self.m_sRAVersion,
                         p_sRatioNew, p_sRatioCur))
        else:
            logging.info("INFO: retroarch aspect ratio number no need fix")
        
