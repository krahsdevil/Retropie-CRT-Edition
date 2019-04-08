#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
crt_launcher.py.

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

import os, sys, optparse
from launcher_module.libretro import libretro
from launcher_module.bezel import bezel
from launcher_module.utils import something_is_bad

# FIXME: need work!
if __name__ == '__main__':
    try:
        sSystem = sys.argv[2]
        if sSystem in libretro.get_system_list():
            libretro(sys.argv[1], sys.argv[2], sys.argv[3])
        elif sSystem in bezel.get_system_list():
            bezel(sys.argv[1], sys.argv[2], sys.argv[3])
        else:
            something_is_bad("ERROR - no emulator available for this system!", "")
    except (IndexError):
        something_is_bad("ERROR - No game to launch or no emulator!", "")
