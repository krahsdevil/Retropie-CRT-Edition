#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
launcher libretro.py.

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

import os, logging, commands
from launcher_module.core_paths import CRT_RA_MAIN_CFG_PATH
from launcher_module.emulator import emulator
from launcher_module.utils import ra_version_fixes

class libretro(emulator):
    m_sSystemCfg = ""
    m_sCustomRACFG = ""

    @staticmethod
    def get_system_list():
        return ["sg-1000", "fds", "pcengine", "coleco", "atari7800", "amiga",
                "vectrex", "pcenginecd", "zxspectrum", "amstradcpc", "neogeocd"]

    # system configure vars
    def configure(self):
        if self.m_sSystem == "zxspectrum":
            self.m_sSystemFreq = "zxspectrum50"
        elif self.m_sSystem == "amiga":
            self.m_sSystemFreq = "amiga50"
        else:
            self.m_sSystemFreq = self.m_sSystem
        self.m_sSystemCfg = self.m_sSystemFreq + ".cfg"

    # final configure binary/process values and prepare emulatorcfg
    def post_configure(self):
        self.m_lBinaryMasks = ["lr-"]

        self.m_sCustomRACFG = os.path.join(CRT_RA_MAIN_CFG_PATH, self.m_sSystemCfg)
        # if not exists report it
        if not os.path.exists(self.m_sCustomRACFG):
            logging.error("not found cfg: %s" % self.m_sCustomRACFG)
            return
        logging.info("CRT Custom Retroarch cfg: %s" % self.m_sCustomRACFG)
        ra_version_fixes(self.m_sCustomRACFG)

