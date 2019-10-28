#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
launcher amiga.py.

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

import os, logging, subprocess
from launcher_module.core import CFG_VIDEOUTILITY_FILE, RETROPIEEMU_PATH, RETROPIECFG_PATH, CRT_RUNCOMMAND_FORMAT, TMP_SLEEPER_FILE, RUNCOMMAND_FILE
from launcher_module.file_helpers import ini_get
from launcher_module.core_paths import CRTROOT_PATH
from launcher_module.amiga import amiga

RETROARCH_CONFIGS_PATH = os.path.join(CRTROOT_PATH, "Retroarch/configs")

class amiga(amiga):
    m_sSleeper = CRT_RUNCOMMAND_FORMAT % TMP_SLEEPER_FILE
    m_sSystemCfg = ""
    m_sSystemCfgPath = ""
    m_sAmigaFirstBinary = ""

    @staticmethod
    def get_system_list():
        return ["amiga"]

    def configure(self):
        """
        1) Identifies those emulators not need --append config, this only for retroarch
        2) Preconfigure amiga50.cfg for lr-puae
        """
        self.m_lBinaryUntouchable = ["amiberry", "amiberry-a500", "amiberry-a1200"]
        self.m_sSystemFreq = "amiga50"
        self.m_sCfgSystemPath = os.path.join(RETROPIECFG_PATH, self.m_sSystem, "emulators.cfg")
        self.m_sSystemCfg = self.m_sSystemFreq + ".cfg"
        system_path = os.path.join(RETROARCH_CONFIGS_PATH, self.m_sSystemCfg)
        # if not exists report it
        if not os.path.exists(system_path):
            logging.error("not found cfg: %s" % system_path)
            return
        self.m_sSystemCfgPath = system_path

    def post_configure(self):
        self.m_lBinaryMasks = ["lr-puae", "amiberry"]
        self.m_lProcesses = ["amiberry", "retroarch"] # default emulator process is retroarch        

    def runcommand_generate(self, p_sCMD):
        current_cmd = super(amiga, self).runcommand_generate(p_sCMD)
        #Check if a VALID binary of the list must be excluded of the --appendconfig flag addition:
        if (self.m_sNextValidBinary in self.m_lBinaryUntouchable) or (not self.m_sSystemCfgPath):
            return current_cmd
        # update system_custom_cfg, used in ra_check_version
        append_cmd = "--appendconfig %s" % self.m_sSystemCfgPath
        append_cmd += " " + self.m_sFileNameVar
        #Save first VALID binary selection, later will be compared if change and close
        self.m_sAmigaFirstBinary = self.m_sBinarySelected
        return current_cmd.replace(self.m_sFileNameVar, append_cmd)

    def runcommand_start(self):
        """ 
        If launching Amiberry Configurator ensure Amiberry resolution
        config even though selected emulator is lr-puae
        Else, follow standar procedure
        """
        if "+Start Amiberry" in self.m_sGameName:
            self.amiberry_show_info("Launching AMIBERRY Configurator!")
            commandline = "%s bash \"%s\"" % (self.m_sSleeper, self.m_sFilePath)
            self.m_oRunProcess = subprocess.Popen(commandline, shell=True)
            logging.info("Subprocess running: %s", commandline)
            self.runcommand_wait()
        else:
            super(amiga, self).runcommand_start()