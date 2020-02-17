#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
launcher abandonware.py.

launcher library for retropie, based on original idea - Ironic
  and the retropie integration work by -krahs-

https://github.com/krahsdevil/crt-for-retropie/

Copyright (C)  2018/2019 -krahs- - https://github.com/krahsdevil/
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

import os, re, logging
import subprocess
from launcher_module.core import CFG_TIMINGS_FILE, TMP_SLEEPER_FILE, CRT_RUNCOMMAND_FORMAT
from launcher_module.core_paths import *
from launcher_module.core_choices_dynamic import choices
from launcher_module.emulator import emulator
from launcher_module.screen import CRT
from launcher_module.file_helpers import remove_file, ini_get, modify_line, \
                                         touch_file, add_line

SCUMMVMCFG_FILE = os.path.join(RETROPIECFG_PATH, "scummvm/scummvm.ini")

class abandonware(emulator):
    m_sSleeper = CRT_RUNCOMMAND_FORMAT % TMP_SLEEPER_FILE

    @staticmethod
    def get_system_list():
        return ["scummvm", "pc"]

    def pre_configure(self):
        if self.m_sSystem == "scummvm":
            self.m_lBinaryMasks = ["scummvm"]
            self.m_lProcesses = ["scummvm", "retroarch"]
        elif self.m_sSystem == "pc":
            self.m_lBinaryMasks = ["dosbox"]
            self.m_lProcesses = ["dosbox", "retroarch"]

    def configure(self):
        super(abandonware, self).configure()
        if self.m_sSystem == "scummvm":
            self._scummvm_change_gfxmode()
            if not "+Start " in self.m_sGameName:
                self._scummvm_change_aspect()
        self.show_info("Better with keyboard and mouse")

    def show_info(self, m_sMessage, m_sTitle = None):
        ch = choices()
        if m_sTitle:
            ch.set_title(m_sTitle)
        ch.load_choices([(m_sMessage, "OK")])
        ch.show()
        ch.cleanup()

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
        p_sScummARC = int(ini_get(CFG_VIDEOUTILITY_FILE, "scummvm_arc"))
        if p_sScummARC == 0:
            """ 
            If Aspect Ratio Correction is not enabled leave this
            config as it is, only change if forced required or asked.
            """
            pass
        if p_sScummARC == 1:
            sAspect = "FIT"
        elif p_sScummARC == 2:
            sAspect = self._selector_pixel_ferfect()

        if sAspect == "PIXEL":
            self._scummvm_change_ini(SCUMMVMCFG_FILE, p_sARValue, "false")
        elif sAspect == "FIT":
            self._scummvm_change_ini(SCUMMVMCFG_FILE, p_sARValue, "true")

    def _selector_pixel_ferfect(self):
        ch = choices()
        ch.set_title("SCUMMVM ARC")
        ch.load_choices([("ENABLE / VERTICAL STRETCH", "FIT"),
                         ("DISABLE / PIXELPERFECT", "PIXEL")])
        result = ch.run()
        return result

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
            self.show_info("Launching %s Configurator!" % self.m_sSystem.upper())
            commandline = "%s bash \"%s\" > /dev/null 2>&1" % \
                          (self.m_sSleeper, self.m_sFilePath)
            self.m_oRunProcess = subprocess.Popen(commandline, shell=True)
            logging.info("Subprocess running: %s", commandline)
            self.runcommand_wait()
        else:
            super(abandonware, self).runcommand_start()
