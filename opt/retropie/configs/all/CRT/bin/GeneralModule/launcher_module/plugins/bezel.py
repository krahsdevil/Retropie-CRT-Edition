#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
launcher bezel.py.

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

import os, sys, logging
from launcher_module.core import CFG_VIDEOUTILITY_FILE
from launcher_module.file_helpers import ini_get
from launcher_module.plugins.libretro import libretro, RETROARCH_CONFIGS_PATH

class bezel(libretro):
    # FIXME: aun no se muy bien como haré esto...
    @staticmethod
    def get_system_list():
        return ["atarilynx", "gbc", "gb", "gba", "ngpc", "ngp",
                "wonderswan", "wonderswancolor", "gamegear"]

    def system_setup(self):
        super(bezel, self).system_setup()
        if ini_get(CFG_VIDEOUTILITY_FILE, "handheld_bezel") == "1":
            self.m_sSystemCfg = self.m_sSystemFreq + "_s.cfg"
            self.m_sSystemCfgPath = os.path.join(RETROARCH_CONFIGS_PATH, self.m_sSystemCfg)
            logging.info("enabled bezel cfg: %s" % self.m_sSystemCfgPath)
