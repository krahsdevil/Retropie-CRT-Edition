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

import os, re, logging
from distutils.version import LooseVersion
from launcher_module.core import CRTROOT_PATH, RETROPIEEMU_PATH, RETROPIECFG_PATH
from launcher_module.emulator import emulator
from launcher_module.file_helpers import md5_file, add_line, modify_line, ini_get

RETROARCH_CONFIGS_PATH = os.path.join(CRTROOT_PATH, "Retroarch/configs")
RETROARCH_DB_FILE = os.path.join(CRTROOT_PATH, "HashRetroarchVersionDB.txt")
RETROARCH_BINARY_FILE = os.path.join(RETROPIEEMU_PATH, "retroarch/bin/retroarch")

class libretro(emulator):
    m_sSystemCfg = ""
    m_sSystemCfgPath = ""

    @staticmethod
    def get_system_list():
        return ["sg-1000", "fds", "pcengine", "neogeo", "coleco", "atari7800",
                "vectrex", "pcenginecd", "zxspectrum", "amstradcpc"]

    # system configure vars
    def configure(self):
        if self.m_sSystem == "zxspectrum":
            self.m_sSystemFreq = "zxspectrum50"
        elif self.m_sSystem == "pcenginecd":
            self.m_sSystemFreq = "pcengine"
        else:
            super(libretro, self).configure()
        self.m_sSystemCfg = self.m_sSystemFreq + ".cfg"
        system_path = os.path.join(RETROARCH_CONFIGS_PATH, self.m_sSystemCfg)
        # if not exists report it
        if not os.path.exists(system_path):
            logging.error("not found cfg: %s" % system_path)
            return
        self.m_sSystemCfgPath = system_path

    # final configure binary/process values and prepare emulatorcfg
    def post_configure(self):
        self.m_lBinaryMasks = ["lr-"]
        self.m_lProcesses = ["retroarch"] # default emulator process is retroarch
        self.ra_check_version() # need the correct m_sSystemCfgPath

    # just called if need rebuild the CMD
    def runcommand_generate(self, p_sCMD):
        current_cmd = super(libretro, self).runcommand_generate(p_sCMD)
        if not self.m_sSystemCfgPath:
            return current_cmd
        # update system_custom_cfg, used in ra_check_version
        append_cmd = "--appendconfig %s" % self.m_sSystemCfgPath
        append_cmd += " %ROM%"
        return current_cmd.replace("%ROM%", append_cmd)

    #  check if retroarch is lower than v1.7.5 because a change in aspect_ratio_index value
    def ra_check_version(self):
        if not self.m_sSystemCfgPath:
            return
        ra_hash = md5_file(RETROARCH_BINARY_FILE)
        f = open(RETROARCH_DB_FILE, "r")
        full_lines = f.readlines()
        f.close()
        ra_version = None
        for line in full_lines:
            lValues = line.strip().split(' ')
            if ra_hash == lValues[1]:
                ra_version = lValues[2]
                break
        # update file if not found
        if not ra_version:
            ra_output = commands.getoutput("%s --version" % RETROARCH_BINARY_FILE)
            for line in ra_output.splitlines():
                lValues = line.strip().split(' ')
                if 'RetroArch' in lValues[0]:
                    ra_version = lValues[5]
                    add_line(RETROARCH_DB_FILE, "RetroArch %s %s" % (ra_hash,ra_version))

        ratio = "23" # default 1.7.5 value
        if LooseVersion(ra_version) < LooseVersion("v1.7.5"):
            ratio = "22"
        ratio_value = ini_get(self.m_sSystemCfgPath, "aspect_ratio_index")
        if ratio != ratio_value.replace('"', ''):
            modify_line(self.m_sSystemCfgPath, "aspect_ratio_index", "aspect_ratio_index = \"%s\"" % ratio)
            logging.info("fixed: %s version: %s ratio: %s (%s)" % (self.m_sSystemCfgPath, ra_version, ratio, ratio_value))
