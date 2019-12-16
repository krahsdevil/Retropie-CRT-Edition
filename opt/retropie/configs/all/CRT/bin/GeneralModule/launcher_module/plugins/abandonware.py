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
from launcher_module.core_choices_dynamic import choices
from launcher_module.emulator import emulator
from launcher_module.screen import CRT
from launcher_module.file_helpers import remove_file

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
        self.abandonware_show_info("Better with keyboard and mouse")

    def screen_set(self):
        self.m_oCRT = CRT(self.m_sSystemFreq)
        self.m_oCRT.screen_calculated(CFG_TIMINGS_FILE)
        try:
            splash_info("black") # clean screen
        except Exception as e:
            logging.error("splash failed: %s" % e)
        logging.info("clean: %s", TMP_SLEEPER_FILE)
        remove_file(TMP_SLEEPER_FILE)

    def abandonware_show_info(self, m_sMessage, m_sTitle = None):
        ch = choices()
        if m_sTitle:
            ch.set_title(m_sTitle)
        ch.load_choices([(m_sMessage, "OK")])
        ch.show()
        ch.cleanup()

    def runcommand_start(self):
        """ launch_core: run emulator!"""
        if "+Start " in self.m_sGameName:
            self.abandonware_show_info("Launching SCUMMVM Configurator!")
            commandline = "%s bash \"%s\" > /dev/null 2>&1" % \
                          (self.m_sSleeper, self.m_sFilePath)
            self.m_oRunProcess = subprocess.Popen(commandline, shell=True)
            logging.info("Subprocess running: %s", commandline)
            self.runcommand_wait()
        else:
            super(abandonware, self).runcommand_start()
