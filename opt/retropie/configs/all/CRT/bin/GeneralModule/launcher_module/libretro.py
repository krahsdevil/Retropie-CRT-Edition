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

import os, sys
from .core import launcher

class libretro(launcher):
    # FIXME: aun no se muy bien como haré esto...
    @staticmethod
    def get_system_list():
        return ["sg-1000", "fds", "pcengine", "neogeo", "colecovision", "atari7800",
                "vectrex", "pcenginecd", "zxspectrum", "amstradcpc"]


    def init(self):
        self.m_lBinaryMasks = ["lr-"]
        self.m_lProcesses = ["retroarch"] # default emulator process is retroarch
        self.run()

    def run(self):
        self.start()
        self.wait()
        self.cleanup()


    def system_setup(self):
        if self.m_sSystem == "zxspectrum":
            self.m_sSystemFreq = "zxspectrum50"
        elif self.m_sSystem == "pcenginecd":
            self.m_sSystemFreq = "pcengine"
        else:
            super(libretro, self).system_setup()
