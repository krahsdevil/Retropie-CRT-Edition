#!/usr/bin/python3
# -*- coding: utf-8 -*-


"""
crt_launcher.py.

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

import os, sys, traceback
from launcher_module.core_paths import TMP_LAUNCHER_PATH, PNAME_LAUNCHER
from launcher_module.utils import something_is_bad, plugin_list, plugin_load, \
                                  show_info, set_procname

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODULES_PATH = os.path.join(BASE_DIR, "launcher_module/plugins")

EXCEPTION_LOG = os.path.join(TMP_LAUNCHER_PATH, "backtrace.log")

set_procname(PNAME_LAUNCHER)

if __name__ == '__main__':
    try:
        sSystem = sys.argv[2]
        bSystemFound = False
        for pl in plugin_list(MODULES_PATH):
            # print("Loading plugin " + pl["name"])
            launcher = plugin_load(pl)
            if sSystem in launcher.get_system_list():
                bSystemFound = True
                launcher(sys.argv[1], sys.argv[2], sys.argv[3])
        if not bSystemFound:
            #something_is_bad("ERROR - System not supported!", sSystem)
            show_info("SYSTEM [%s] NOT SUPPORTED!" % sSystem, "", 7000)
    # TODO: kill emulator ?
    except (IndexError):
        show_info("NO GAME TO LAUNCH OR NO EMULATOR!", "", 7000)
        #something_is_bad("ERROR - No game to launch or no emulator!", "")
    except Exception as e:
        with open(EXCEPTION_LOG, 'a') as f:
            f.write(str(e))
            f.write(traceback.format_exc())
