#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
launcher selector.py.

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

import os, sys
from launcher_module.plugins.libretro import libretro, logging, RETROARCH_CONFIGS_PATH

class selector(libretro):
    # FIXME: aun no se muy bien como haré esto... (pues imagina yo)
    @staticmethod
    def get_system_list():
        return ["megadrive", "segacd", "sega32x", "mastersystem", "n64", "nes", "snes", "psx", "msx", "atari2600", "odyssey2", "zx81", "atarist", "c64", "atari7800"]

    def system_setup(self):
        super(selector, self).system_setup()
        self.m_sSystemCfg = self.m_sSystemFreq + ".cfg"
        self.m_sSystemCfgPath = os.path.join(RETROARCH_CONFIGS_PATH, self.m_sSystemCfg)
        logging.info("enabled selector cfg: %s" % self.m_sSystemCfgPath)
