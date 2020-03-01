#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
launcher libretro.py.

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

import os, re, logging, commands
from distutils.version import LooseVersion
from launcher_module.core import CRT_ROOT_PATH, RETROPIE_EMULATORS_PATH, RETROPIE_CFG_PATH
from launcher_module.emulator import emulator
from launcher_module.utils import ra_check_version

RETROARCH_CONFIGS_PATH = os.path.join(CRT_ROOT_PATH, "Retroarch/configs")
RETROARCH_DB_FILE = os.path.join(CRT_ROOT_PATH, "bin/ScreenUtilityFiles/config_files/retroarchdb.txt")
RETROARCH_BINARY_FILE = os.path.join(RETROPIE_EMULATORS_PATH, "retroarch/bin/retroarch")

class libretro(emulator):
    m_sSystemCfg = ""
    m_sCustomRACFG = ""

    @staticmethod
    def get_system_list():
        return ["sg-1000", "fds", "pcengine", "coleco", "atari7800",
                "vectrex", "pcenginecd", "zxspectrum", "amstradcpc", "neogeocd"]

    # system configure vars
    def configure(self):
        if self.m_sSystem == "zxspectrum":
            self.m_sSystemFreq = "zxspectrum50"
        else:
            self.m_sSystemFreq = self.m_sSystem
        self.m_sSystemCfg = self.m_sSystemFreq + ".cfg"

    # final configure binary/process values and prepare emulatorcfg
    def post_configure(self):
        self.m_lBinaryMasks = ["lr-"]
        self.m_lProcesses = ["retroarch"] # default emulator process is retroarch

        self.m_sCustomRACFG = os.path.join(RETROARCH_CONFIGS_PATH, self.m_sSystemCfg)
        # if not exists report it
        if not os.path.exists(self.m_sCustomRACFG):
            logging.error("not found cfg: %s" % self.m_sCustomRACFG)
            return
        logging.info("CRT Custom Retroarch cfg: %s" % self.m_sCustomRACFG)
        ra_check_version(self.m_sCustomRACFG)

    # just called if need rebuild the CMD
    def runcommand_generate(self, p_sCMD):
        current_cmd = super(libretro, self).runcommand_generate(p_sCMD)
        if not self.m_sCustomRACFG:
            return current_cmd
        # update system_custom_cfg, used in ra_check_version
        append_cmd = "--appendconfig %s" % self.m_sCustomRACFG
        append_cmd += " " + self.m_sFileNameVar
        return current_cmd.replace(self.m_sFileNameVar, append_cmd)

