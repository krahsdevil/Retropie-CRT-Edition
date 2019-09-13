#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
launcher sega.py.

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
import os, logging, shutil
from launcher_module.core import TMP_LAUNCHER_PATH
from launcher_module.plugins.libretro import RETROARCH_CONFIGS_PATH
from launcher_module.plugins.selector import selector
from launcher_module.file_helpers import ini_set

VDATA = { "megadrive": {
            "default": {"width": 2088, "height": 240, "x": -67, "y": 0},
            "picodrive": {"width": 1920, "height": 224, "x": -3,  "y": 7},
          },
          "megadrive50": {
            "default": {"width": 2088, "height": 288, "x": -68, "y": 2},
            "picodrive": {"width": 1920, "height": 224, "x": 15,  "y": 33},
          },
          "mastersystem": {
            "default": {"width": 1988, "height": 240, "x": -37, "y": 0},
            "picodrive": {"width": 1792, "height": 192, "x": 60,  "y": 24},
          },
          "mastersystem50": {
            "default": {"width": 1988, "height": 288, "x": -29, "y": 2},
            "picodrive": {"width": 1536, "height": 192, "x": 192, "y": 50},
          }
        }

class sega(selector):
    m_sSegaTmpPath = ""
    m_sViewPortType = ""

    @staticmethod
    def get_system_list():
        return ["none"]

    def post_configure(self):
        super(sega, self).post_configure()
        # copy cfg base
        self.m_sSegaTmpPath = os.path.join(TMP_LAUNCHER_PATH, os.path.basename(self.m_sSystemCfgPath))
        logging.info("copying: %s => %s" % (self.m_sSystemCfgPath, self.m_sSegaTmpPath) )
        shutil.copy2(self.m_sSystemCfgPath, self.m_sSegaTmpPath)
        # use tmp config
        self.m_sSystemCfgPath = self.m_sSegaTmpPath

    def segacfg_generate(self):
        try:
            logging.info("s: %s b: %s" % (self.m_sSystemFreq, self.m_sBinarySelected) )
            dCFG = VDATA[self.m_sSystemFreq]
            # genesis-plus and other genesis cores by default
            self.m_sViewPortType = "default"
            if "picodrive" in self.m_sBinarySelected:
                self.m_sViewPortType = "picodrive"
            self.segacfg_write(dCFG[self.m_sViewPortType])
        except:
            logging.info("warning: missed - cfg data not found!")

    # first check
    def runcommand_generate(self, p_sCMD):
        current_cmd = super(sega, self).runcommand_generate(p_sCMD)
        self.segacfg_generate()
        return current_cmd

    # second check - emulator could be changed before is launched
    def emulatorcfg_check_or_die(self):
        super(sega, self).emulatorcfg_check_or_die()
        self.segacfg_generate()

    def segacfg_write(self, p_dData):
        ini_set(self.m_sSegaTmpPath, "custom_viewport_width", p_dData["width"])
        ini_set(self.m_sSegaTmpPath, "custom_viewport_height", p_dData["height"])
        ini_set(self.m_sSegaTmpPath, "custom_viewport_x", p_dData["x"])
        ini_set(self.m_sSegaTmpPath, "custom_viewport_y", p_dData["y"])
        logging.info("type: %s => %s" % (self.m_sViewPortType, str(p_dData)))

        
