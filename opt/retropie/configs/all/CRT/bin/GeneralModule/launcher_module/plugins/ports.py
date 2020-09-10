#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
launcher ports.py.

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

import os, logging, re, subprocess, shlex
from launcher_module.screen import CRT
from launcher_module.core_paths import *
from launcher_module.utils import show_info
from launcher_module.emulator import emulator
from launcher_module.file_helpers import ini_get, modify_line, \
                                         touch_file, add_line, \
                                         remove_file

DB_PORTS = os.path.join(CRT_DB_PATH, "ports.txt")

class ports(emulator):
    @staticmethod
    def get_system_list():
        return ["ports"]

    def pre_configure(self):
        self.p_sPort = None
        logging.info("INFO: Script for port: {%s}" % self.m_sFilePath)
        with open(self.m_sFilePath, "r") as f:
            for line in f:
                if "_PORT_" in line:
                    self.p_sPort = line.split("_PORT_")[1].strip()
                    self.p_sPort = re.sub(r' +', " ", self.p_sPort).split(' ')[0].strip()
                    self.p_sPort = self.p_sPort.replace('"', '')
                    self.p_sPort = self.p_sPort.replace('=',' ')
                    logging.info("INFO: Port ID: {%s}" % self.p_sPort)
                    break
        if not self.p_sPort: self.panic("Don't valid port game")
        p_sPortPath = os.path.join(self.m_sSystem, self.p_sPort, "emulators.cfg")
        self.m_sCfgSystemPath = os.path.join(RETROPIE_CFG_PATH, p_sPortPath)
        logging.info("INFO: emulators.cfg for this port: {%s}" % self.m_sCfgSystemPath)

    def screen_set(self):
        self.m_oCRT = CRT(self.p_sPort)
        self.m_oCRT.screen_calculated(DB_PORTS)
        self.m_oBlackScreen.fill()
        logging.info("INFO: clean: %s", TMP_SLEEPER_FILE)
        remove_file(TMP_SLEEPER_FILE)

    def runcommand_start(self):
        """ launch_core: run emulator!"""
        commandline = "bash \"%s\"" % self.m_sFilePath
        self.m_oRunProcess = subprocess.Popen(shlex.split(commandline), shell=False)
        logging.info("INFO: Subprocess running: %s", commandline)
        self.runcommand_wait()
