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
from launcher_module.core import CRTROOT_PATH, RETROPIEEMU_PATH, RETROPIECFG_PATH, CFG_TIMINGS_FILE, TMP_SLEEPER_FILE, CRT_RUNCOMMAND_FORMAT, RUNCOMMAND_FILE
from launcher_module.core_choices_dynamic import choices
from launcher_module.emulator import emulator
from launcher_module.screen import CRT
from launcher_module.file_helpers import remove_file

RETROARCH_CONFIGS_PATH = os.path.join(CRTROOT_PATH, "Retroarch/configs")
RETROARCH_DB_FILE = os.path.join(CRTROOT_PATH, "HashRetroarchVersionDB.txt")
RETROARCH_BINARY_FILE = os.path.join(RETROPIEEMU_PATH, "retroarch/bin/retroarch")

class abandonware(emulator):
    m_sSleeper = CRT_RUNCOMMAND_FORMAT % TMP_SLEEPER_FILE

    @staticmethod
    def get_system_list():
        return ["scummvm", "pc"]

    def pre_configure(self):
        if self.m_sSystem == "scummvm":
            self.m_lBinaryMasks = ["scummvm"]
            self.m_lProcesses = ["scummvm", "retroarch"] # default emulator process is retroarch
        elif self.m_sSystem == "pc":
            self.m_lBinaryMasks = ["dosbox"]
            self.m_lProcesses = ["dosbox", "retroarch"] # default emulator process is retroarch

    def configure(self):
        super(abandonware, self).configure()
        self.key_mouse_advise()
        
    def screen_set(self):
        self.m_oCRT = CRT(self.m_sSystemFreq)
        self.m_oCRT.screen_raw(CFG_TIMINGS_FILE)
        try:
            splash_info("black") # clean screen
        except Exception as e:
            logging.error("splash failed: %s" % e)
        logging.info("clean: %s", TMP_SLEEPER_FILE)
        remove_file(TMP_SLEEPER_FILE)
        
    def key_mouse_advise(self):
        ch = choices()
        #ch.set_title("KEYBOARD/MOUSE")
        ch.load_choices([
                ("BETTER WITH KEYBOARD AND MOUSE", "OK"),
            ])
        ch.run()
    
    def runcommand_start(self):
        """ launch_core: run emulator!"""
        if "+Start " in self.m_sGameName:
            commandline = "%s bash \"%s\" > /dev/null 2>&1" % (self.m_sSleeper, self.m_sFilePath)
            self.m_oRunProcess = subprocess.Popen(commandline, shell=True)
            logging.info("Subprocess running: %s", commandline)
            self.runcommand_wait()
        else:
            super(abandonware, self).runcommand_start()

    