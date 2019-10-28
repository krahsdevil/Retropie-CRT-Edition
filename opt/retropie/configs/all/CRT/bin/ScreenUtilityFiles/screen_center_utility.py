#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
centering pattern.py.

Centering Pattern Utility for CRT image adjusting by Krahs

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


import os, sys
import subprocess, commands
import logging

CRT_PATH = "/opt/retropie/configs/all/CRT"
RESOURCES_PATH = os.path.join(CRT_PATH,"bin/GeneralModule")
sys.path.append(RESOURCES_PATH)

from launcher_module.screen import CRT
from launcher_module.utils import splash_info
from launcher_module.core_paths import *
from launcher_module.file_helpers import *
from pattern_generator import *

__VERSION__ = '0.1'
__DEBUG__ = logging.INFO # logging.ERROR
CLEAN_LOG_ONSTART = True

LOG_PATH = os.path.join(TMP_LAUNCHER_PATH, "CRT_Launcher.log")
CENTER_CFG_FILE = os.path.join(CRT_PATH,"bin/ScreenUtilityFiles/config_files/utility.cfg")

tests = ["system", "test60", "force"]

class center(object):
    """ virtual class for centering pattern """
    m_dVideo = {}
    m_oCRT = None
    m_oPatternHandle = None
    m_sEnv = ""

    m_dPatternAdj = {}

    def __init__(self):
        self.__temp()
        self.__clean()
        logging.info("INFO: arg 1 (test) = %s" %sys.argv[1])

        self.configure() # rom name work
        self.prepare() # screen and pattern generator
        self.run() # launch, wait and cleanup

    # called at start, called by __init__()
    def configure(self):
        self.m_sEnv = sys.argv[1]

        """Get from utility.cfg system resolution"""
        if self.m_sEnv == "system":
            self.m_sEnv = ini_get(CENTER_CFG_FILE, "default")
        elif self.m_sEnv == "force":
            logging.info("INFO: Force mode, only apply sys resolution")
            self._force_system_res()

    def prepare(self):
        self.screen_prepare()
        self.m_oPatternHandle = generate(self.m_sEnv, self.m_dVideo)

    def run(self):
        self.start()
        self.cleanup()

    def start(self):
        self.apply_diff_timings()
        self.screen_set()
        self.m_oPatternHandle.run()

    def apply_diff_timings(self):
        DiffTimings = self.m_oPatternHandle.get_diff_timings()
        logging.info("INFO: timing_data_set CALCULATED Pre Diff - %s" %
                     self.m_dVideo)
        for timing in DiffTimings:
            self.m_oCRT.timing_add(timing, int(DiffTimings[timing]))
        logging.info("INFO: timing_data_set CALCULATED Post Diff - %s" %
                      self.m_dVideo)

    def _force_system_res(self):
        p_oSaveBoot = saveboot()
        p_oSaveBoot.save()
        self.m_oCRT = CRT()
        self.cleanup()

    def screen_prepare(self):
        self.m_oCRT = CRT(self.m_sEnv+"_timings")
        self.m_dVideo = self.m_oCRT.pattern_data(CENTER_CFG_FILE)

    def screen_set(self):
        self.m_oCRT.resolution_set()

    def panic(self, p_sErrorLine1, p_sErrorLine2 = "-", p_bForceQuit = True):
        """ stop the program and show error to the user """
        logging.error("PANIC: %s" % p_sErrorLine1)
        CRT().screen_restore()
        something_is_bad(p_sErrorLine1, p_sErrorLine2)
        if p_bForceQuit:
            logging.error("EXIT: crt_launcher forced")
            self.__clean()
            sys.exit(1)

    # cleanup code
    def cleanup(self):
        self.m_oCRT.screen_restore()
        logging.info("ES mode recover")
        os.system('clear')
        self.__clean()
        sys.exit()

    # clean system
    def __clean(self):
        pass

    def __temp(self):
        if CLEAN_LOG_ONSTART:
            remove_file(LOG_PATH)
        logging.basicConfig(filename=LOG_PATH, level=__DEBUG__,
        format='[%(asctime)s] %(levelname)s - %(filename)s:%(funcName)s - %(message)s')

try:
    argument = sys.argv[1]
except:
    print("No argument found for Screen Center Utility launching")
    sys.exit()
    
if argument in tests:
    oLaunch = center()
else:
    print("No valid argument, expecting %s"%tests)
    sys.exit()
