#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
launcher selector.py.

For RetroArch multi-frequency system launcher library for retropie, 
based on original idea - Ironic and the retropie integration work by -krahs-

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

import os, logging
from launcher_module.plugins.libretro import libretro
from launcher_module.core_selector import FrequencySelector

class selector(libretro):
    @staticmethod
    def get_system_list():
        return ["n64", "nes", "snes", "psx", "msx", "atari2600", "videopac", "zx81",
                "atarist", "c64", "segacd", "sega32x", "atari800"]

    # getting correct frequency for FileName loaded
    def configure(self):
        super(selector, self).configure()
        p_sSelectFreq = FrequencySelector(self.m_sFileName).get_frequency()
        if p_sSelectFreq == "50":
            self.m_sSystemFreq = self.m_sSystem + "50"
            self.m_sSystemCfg = self.m_sSystemFreq + ".cfg"
