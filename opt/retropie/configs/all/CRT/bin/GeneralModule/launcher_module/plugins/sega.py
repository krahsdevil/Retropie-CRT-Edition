#!/usr/bin/python3
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
import os, logging
from launcher_module.plugins.selector import selector
from launcher_module.file_helpers import ini_set

VDATA = { "megadrive": {
            "default": {"width": 1920, "height": 240, "x": -4, "y": 0},
            "picodrive": {"width": 1920, "height": 240, "x": -3,  "y": 0},
          },
          "megadrive50": {
            "default": {"width": 1920, "height": 288, "x": 7, "y": 3},
            "picodrive": {"width": 1920, "height": 240, "x": 9,  "y": 27},
          },
          "mastersystem": {
            "default": {"width": 1900, "height": 240, "x": 8, "y": 0},
            "picodrive": {"width": 1920, "height": 240, "x": 0,  "y": -1},
          },
          "mastersystem50": {
            "default": {"width": 1872, "height": 288, "x": 34, "y": 3},
            "picodrive": {"width": 1880, "height": 240, "x": 29, "y": 27},
          }
        }

class sega(selector):
    m_sSegaTmpPath = ""
    m_sViewPortType = ""
    m_sRndCore  = ""  # previous core selection

    @staticmethod
    def get_system_list():
        return ["megadrive", "mastersystem"]

    # get ready sega retroarch video settings
    def prepare(self):
        current_cmd = super(sega, self).prepare()
        self.segacfg_generate()

    def segacfg_generate(self):
        try:
            logging.info("INFO: Customizing SEGA retroarch video core configuration")
            dCFG = VDATA[self.m_sSystemFreq]
            # genesis-plus and other genesis cores by default
            self.m_sViewPortType = "default"
            if "picodrive" in self.m_sSelCore:
                self.m_sViewPortType = "picodrive"
            self.segacfg_write(dCFG[self.m_sViewPortType])
            self.m_sRndCore = self.m_sSelCore
        except:
            logging.info("WARNING: missed - cfg data not found!")

    # second check - emulator could be changed before is launched
    def emulatorcfg_check_or_die(self):
        if not self.m_bFastBoot:
            super(sega, self).emulatorcfg_check_or_die()
            self.segacfg_generate()

    def segacfg_write(self, p_dData):
        if self.m_sRndCore != self.m_sSelCore:
            logging.info("INFO: system: %s core: %s" % (self.m_sSystemFreq, self.m_sSelCore))
            ini_set(self.m_sCustomRACFG, "custom_viewport_width", p_dData["width"])
            ini_set(self.m_sCustomRACFG, "custom_viewport_height", p_dData["height"])
            ini_set(self.m_sCustomRACFG, "custom_viewport_x", p_dData["x"])
            ini_set(self.m_sCustomRACFG, "custom_viewport_y", p_dData["y"])
            logging.info("INFO: Changes type %s => %s" % (self.m_sViewPortType, str(p_dData)))
        else:
            logging.info("INFO: same SEGA core, changes already applied")

        
