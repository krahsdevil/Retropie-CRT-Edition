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

from launcher_module.core_paths import CRTROOT_PATH, RETROPIEEMU_PATH, \
                                       RETROARCHBIN_FILE, CFG_RAHASHDB
from launcher_module.file_helpers import md5_file, ini_get, touch_file, \
                                         add_line, modify_line
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
            
def get_screen_resolution():
    commandline = "cat /sys/class/graphics/fb0/virtual_size"
    output = commands.getoutput(commandline)
    VirtRes = output.replace(',',' ').split(' ')
    RES_X = int(VirtRes[0])
    RES_Y = int(VirtRes[1])
    return (RES_X, RES_Y)
  
def ra_check_version(p_sSystemCfgPath = None):
    """
    This function will check version of current retroarch.
    From some or in particular version actions will be taken
    like if it's is lower than v1.7.5 aspect_ratio_index value
    must be change.
    """
    logging.info("checking retroarch version")
    if not p_sSystemCfgPath:
        return
    if not os.path.isfile(CFG_RAHASHDB):
        touch_file(CFG_RAHASHDB)
        logging.info("Created retroarch database")
        
    ra_hash = md5_file(RETROARCHBIN_FILE)
    f = open(CFG_RAHASHDB, "r")
    full_lines = f.readlines()
    f.close()
    ra_version = None
    for line in full_lines:
        if line != "\n":
            lValues = line.strip().split(' ')
            if ra_hash == lValues[1]:
                ra_version = lValues[2]
                break
    # update file if not found
    if not ra_version:
        ra_output = commands.getoutput("%s --version" % RETROARCHBIN_FILE)
        for line in ra_output.splitlines():
            lValues = line.strip().split(' ')
            if 'RetroArch' in lValues[0]:
                ra_version = lValues[5]
                add_line(CFG_RAHASHDB, "RetroArch %s %s" % (ra_hash,ra_version))

    ratio = "23" # default 1.7.5 value
    if LooseVersion(ra_version) < LooseVersion("v1.7.5"):
        logging.info("early retroarch version, fixing ratio number - %s"%LooseVersion(ra_version))
        ratio = "22"
    ratio_value = ini_get(p_sSystemCfgPath, "aspect_ratio_index")
    if ratio != ratio_value.replace('"', ''):
        modify_line(p_sSystemCfgPath, "aspect_ratio_index", "aspect_ratio_index = \"%s\"" % ratio)
        logging.info("fixed: %s version: %s ratio: %s (%s)" % (p_sSystemCfgPath, ra_version, ratio, ratio_value))

def compact_rom_name(p_sRomName):
    sPreCleanedGame = re.sub('[^a-zA-Z0-9-_]+','', p_sRomName )
    sCleanedGame = re.sub(' ','', sPreCleanedGame)
    return sCleanedGame
    
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