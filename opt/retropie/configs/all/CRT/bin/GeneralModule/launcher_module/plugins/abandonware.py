#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
launcher abandonware.py.

launcher library for retropie, based on original idea - Ironic
  and the retropie integration work by -krahs-

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
from launcher_module.core_paths import *
from launcher_module.utils import show_info
from launcher_module.emulator import emulator
from launcher_module.file_helpers import ini_get, modify_line, \
                                         touch_file, add_line

SCUMMVMCFG_FILE = os.path.join(RETROPIE_CFG_PATH, "scummvm/scummvm.ini")

class abandonware(emulator):
    m_lOptARC = [("ENABLE / VERTICAL STRETCH", "FIT"),
                 ("DISABLE / PIXELPERFECT", "PIXEL")]

    @staticmethod
    def get_system_list():
        return ["scummvm", "pc"]

    def configure(self):
        if self.m_sSystem == "scummvm":
            self.m_lBinaryMasks = ["scummvm"]
            self._scummvm_change_gfxmode()
            if not "+Start " in self.m_sGameName:
                self._scummvm_change_aspect()
        elif self.m_sSystem == "pc":
            self.m_lBinaryMasks = ["dosbox"]
        super(abandonware, self).configure()
        show_info("Better with keyboard and mouse")

    def _scummvm_create_cfg(self):
        """ create base ini file if not exist """
        if not os.path.isfile(SCUMMVMCFG_FILE):
            touch_file(SCUMMVMCFG_FILE)
            add_line(SCUMMVMCFG_FILE, "[scummvm]")

    def _scummvm_change_gfxmode(self):
        """ will make scummvm menu clear and crisp """
        self._scummvm_create_cfg()
        p_sGFXValue = 'opengl'
        p_sGFXKey = 'gfx_mode'
        self._scummvm_change_ini(SCUMMVMCFG_FILE, p_sGFXKey, p_sGFXValue)
        
    def _scummvm_change_aspect(self):
        """ 
        If aspect ratio correction is enabled game will fit vertically
        the screen although we lost pixel perfect.
        If disabled, most of the games are 320x200 so will show two 
        horizontal bars up and down on the screen.
        If auto will ask just before of game launching for an option
        """
        p_sARValue = 'aspect_ratio'
        
        # get aspect ratio configuration from CRT config
        sAspect = None
        p_sScummARC = ini_get(CRT_UTILITY_FILE, "scummvm_arc")
        if p_sScummARC == "false":
            self._scummvm_change_ini(SCUMMVMCFG_FILE, p_sARValue, "false")
        if p_sScummARC == "true":
            self._scummvm_change_ini(SCUMMVMCFG_FILE, p_sARValue, "true")

    def _scummvm_change_ini(self, p_sFile, p_sKey, p_sValue,
                                 p_sSection = "[scummvm]"):
        p_sINI = ini_get(p_sFile, p_sKey)
        if p_sINI:
            logging.info("INFO: Changing {%s} to '%s'" % (p_sKey, p_sValue))
            p_sStr = p_sKey + "=" + p_sValue
            if (p_sValue != p_sINI):
                modify_line(p_sFile, p_sKey, p_sStr)
        else:
            logging.info("INFO: {%s} attribute not found", p_sKey)
            p_sStr = p_sSection + "\n"
            p_sStr += p_sKey + "=" + p_sValue + "\n"
            modify_line(p_sFile, p_sSection, p_sStr)

    def runcommand_start(self):
        """ launch_core: run emulator!"""
        if "+Start " in self.m_sGameName:
            show_info("Launching %s Configurator!" % self.m_sSystem.upper())
        super(abandonware, self).runcommand_start()
