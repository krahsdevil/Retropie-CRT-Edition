#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
launcher arcade.py.

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

import os, logging, shutil
from launcher_module.file_helpers import ini_get
from launcher_module.arcade import arcade
from launcher_module.core_paths import CRT_UTILITY_FILE, CRT_RA_CORES_CFG_PATH, \
                                       CRT_RA_MAIN_CFG_PATH, TMP_LAUNCHER_PATH

class arcade(arcade):
    m_bIScale = False
    m_sCoreCFG = ""

    @staticmethod
    def get_system_list():
        return ["arcade", "mame-advmame", "mame-libretro", "fba", "neogeo"]

    def pre_configure(self):
        if ini_get(CRT_UTILITY_FILE, "integer_scale") == "true":
            self.m_bIScale = True
            logging.info("enabled integer scale for arcade/neogeo")

        """
        For custom core config files to apply if not, default included
        in arcade.cfg will be loaded:
        core_options_path = "/~/CRT/Retroarch/cores/arcade-core.cfg"
        """
        if self.m_sSystem == "neogeo":
            sFile = self.m_sSystem + "-core.cfg"
            self.m_sCoreCFG = os.path.join(CRT_RA_CORES_CFG_PATH, sFile)
        super(arcade, self).pre_configure()

    def configure(self):
        if self.m_sSystem == "mame-advmame":
            self.m_lBinaryMasks = ["advmame"]
        elif self.m_sSystem == "arcade":
            self.m_lBinaryMasks = ["lr-", "advmame"]
            # if BinaryMask doesn't match will try to close all these process
        else:
            self.m_lBinaryMasks = ["lr-"]
            
    def post_configure(self):
        file = os.path.join(CRT_RA_MAIN_CFG_PATH, "arcade.cfg")
        # if not exists report it
        if not os.path.exists(file):
            logging.error("not found cfg: %s" % file)
            return
        logging.info("CRT Custom Retroarch cfg: %s" % file)
        self.m_sCustomRACFG = os.path.join(TMP_LAUNCHER_PATH, "arcade.cfg")
        logging.info("INFO: copying: %s => %s" % (file, self.m_sCustomRACFG))
        shutil.copy2(file, self.m_sCustomRACFG)