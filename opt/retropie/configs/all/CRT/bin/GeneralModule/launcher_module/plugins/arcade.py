#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
launcher arcade.py.

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

import os, logging
from launcher_module.core import CFG_VIDEOUTILITY_FILE
from launcher_module.file_helpers import ini_get
from launcher_module.arcade import arcade, CFG_ARCADE_FILE

class arcade(arcade):
    m_oConfigureFunc = None

    @staticmethod
    def get_system_list():
        return ["arcade", "mame-advmame", "mame-libretro", "fba"]

    def init(self):
        if self.m_sSystem == "mame-advmame":
            self.m_oConfigureFunc = self.adv_config_generate
            self.m_lBinaryMasks = ["advmame"]
            self.m_lProcesses = ["advmame"] # default emulator process is retroarch
        else:
            self.m_oConfigureFunc = self.ra_config_generate
            self.m_lBinaryMasks = ["lr-"]
            self.m_lProcesses = ["retroarch"] # default emulator process is retroarch

    def config_generate(self):
        self.m_oConfigureFunc()

    # just called if need rebuild the CMD
    def runcommand_generate(self, p_sCMD):
        current_cmd = super(arcade, self).runcommand_generate(p_sCMD)
        if self.m_sSystem == "mame-advmame": # advmame not need append any cfg
            return current_cmd
        # update system_custom_cfg, used in ra_check_version
        append_cmd = "--appendconfig %s" % CFG_ARCADE_FILE
        append_cmd += " %ROM%"
        return current_cmd.replace("%ROM%", append_cmd)
