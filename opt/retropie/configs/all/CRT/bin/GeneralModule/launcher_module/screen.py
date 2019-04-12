#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
screen_lib.py.

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
from math import ceil, floor
from launcher_module.file_helpers import ini_get, ini_getlist

CFG_VIDEOUTILITY_FILE = "/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/utility.cfg"
CFG_COMPMODES_FILE = '/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/modes.cfg'

class CRT(object):
    """CRT handler"""

    p_sTimingPath = ""

    m_dData = { "H_Res": 0,     # H_Res   - Horizontal resolution (1600 to 1920)
                "H_FP": 0,      # H_FP    - Horizontal Front Porch. Set to 48 if you don't know what you do
                "H_Sync": 0,    # H_Sync  - Horizontal Sync. Set to 192 if you don't know what you do
                "H_BP": 0,      # H_BP    - Horizontal Back Porch. Set to 240 if you don't know what you do
                "V_Res": 0,     # V_Res   - (50Hz : 192 to 288) - (60Hz : 192 a 256)
                "V_FP": 0,      # V_FP    - Vertical Front Porch
                "V_Sync": 0,    # V_Sync  - Vertical Sync. (3 to 10 or more...)
                "V_BP": 0,      # V_BP    - Vertical Back Porch
                "R_Rate": 0.0,  # R_Rate  - (47 a 62) MUST BE floating point
                "P_Clock": 0,   # P_Clock - Pixel_Clock
                # ------------------------------------- unknown values
                "H_Unk": 0, "V_Unk": 0,
                "Unk_0": 0, "Unk_1": 0, "Unk_2": 0,
                "Unk_R": 0, "Unk_P": 0,
                # ------------------------------------- use for calcs
                "H_Pos": 0,     # H_Pos   - Horizontal position of the screen (-10 to 10)
                "H_Zoom": 0,    # H_Zoom  - Horizontal size of the screen (-40 to 10)
                "V_Pos": 0,     # V_Pos   - Vertical position of the screen (-10 to 10)
                "H_Freq": 0     # H_Freq  - Horizontal frequency of the screen. (15500 to 16000)

                # WARNING, all these values are intrinsically linked. If your screen is desynchronized, quickly reboot the RPI.
                # Some values will be limited due to other values.
    }

    m_iSide_Game = 0
    m_iR_Sys = 0
    m_iR_Game = 0

    def __init__(self, p_sSystem):
        self.m_sSystem = p_sSystem

    # vcgencmd hdmi_timings 1920 1 160 192 320 288 1 6 5 14 0 0 0 50.0 0 40564800 1
    def screen_calculated(self, p_sTimingCfgPath):
        self.p_sTimingPath = p_sTimingCfgPath
        lValues = self.get_values()
        if not lValues:
            logging.error("%s not calculated Timing: %s" % (self.m_sSystem, self.p_sTimingPath))
            return False
        self.timing_parse_calculated(lValues)
        lValues = self.get_fix_tv('%s_game_mask')
        if lValues:
            self.timing_parse_calculated(lValues)
        self.set_timing_unk()
        self.get_fix_user()
        self._calculated_adjustement()
        self.resolution_set(**self.m_dData)

    def screen_raw(self, p_sTimingCfgPath):
        self.p_sTimingPath = p_sTimingCfgPath
        self._raw_data()
        lValues = self.get_fix_tv('%s_game_mask_raw') # FIXME: not used in adjustement ??
        if lValues:
            self.timing_parse_raw(lValues)
        self.resolution_set(**self.m_dData)

    def screen_raw_adjustement(self, p_sTimingCfgPath):
        self.p_sTimingPath = p_sTimingCfgPath
        self._raw_data()
        self._raw_adjustement(
            H_Mov = ini_get(CFG_VIDEOUTILITY_FILE, "test60_offsetX"),
            V_Mov = ini_get(CFG_VIDEOUTILITY_FILE, "test60_offsetY"),
            H_Zoom = ini_get(CFG_VIDEOUTILITY_FILE, "test60_width"),
            )
        self.resolution_set(**self.m_dData)

    # vcgencmd hdmi_timings 2376 2 206 224 412 560 2 19 10 37 0 0 0 100.0 0 50164800 2
    def screen_restore(self):
        lValues = ini_getlist('/boot/config.txt', 'hdmi_timings')
        if not lValues:
            logging.error("Not found restore timing in boot/config.txt")
            return False
        self.timing_reset()
        self.timing_parse_raw(lValues)
        self.resolution_set(**self.m_dData)

    def _raw_data(self):
        lValues = self.get_values()
        if not lValues:
            logging.error("%s not raw Timing: %s" % (self.m_sSystem, self.p_sTimingPath))
            return False
        self.timing_parse_raw(lValues)

    def get_fix_tv(self, p_sFindMask):
        sSelected = ini_get(CFG_COMPMODES_FILE, "mode_default")
        #lValues = ini_get(CFG_COMPMODES_FILE, "mode_default", True)
        if not sSelected or sSelected.lower() == "default":
            return False
        return ini_getlist(CFG_COMPMODES_FILE, p_sFindMask % sSelected)

    def get_fix_user(self):
        self.timing_set("H_Pos", ini_get(CFG_VIDEOUTILITY_FILE, "test60_offsetX"))
        self.timing_set("V_Pos", ini_get(CFG_VIDEOUTILITY_FILE, "test60_offsetY"))
        self.timing_set("H_Zoom", ini_get(CFG_VIDEOUTILITY_FILE, "test60_width"))

    def timing_reset(self):
        for key in self.m_dData:
            self.m_dData[key] = 0

    def timing_set(self, p_sDataType, p_sValue):
        if p_sValue:
            self.m_dData[p_sDataType] += int(p_sValue)

    def timing_parse_calculated(self, p_lTimings):
        self.set_timing_data(H_Res  = int(p_lTimings[0]),
                         V_Res  = int(p_lTimings[1]),
                         R_Rate = float(p_lTimings[2]),
                         H_Pos  = int(p_lTimings[3]),
                         H_Zoom = int(p_lTimings[4]),
                         V_Pos  = int(p_lTimings[5]),
                         H_FP   = int(p_lTimings[6]),
                         H_Sync = int(p_lTimings[7]),
                         H_BP   = int(p_lTimings[8]),
                         V_Sync = int(p_lTimings[9]),
                         H_Freq = int(p_lTimings[10]),
                         V_FP   = 0,
                         V_BP   = 0,
                         P_Clock = 0
                         )

    def timing_parse_raw(self, p_lTimings):
        self.set_timing_data(H_Res  = int(p_lTimings[0]),
                         H_Unk  = int(p_lTimings[1]),
                         H_FP   = int(p_lTimings[2]),
                         H_Sync = int(p_lTimings[3]),
                         H_BP   = int(p_lTimings[4]),
                         V_Res  = int(p_lTimings[5]),
                         V_Unk  = int(p_lTimings[6]),
                         V_FP   = int(p_lTimings[7]),
                         V_Sync = int(p_lTimings[8]),
                         V_BP   = int(p_lTimings[9]),
                         Unk_0  = int(p_lTimings[10]),
                         Unk_1  = int(p_lTimings[11]),
                         Unk_2  = int(p_lTimings[12]),
                         R_Rate = float(p_lTimings[13]),
                         Unk_R  = int(p_lTimings[14]),
                         P_Clock = int(p_lTimings[15]),
                         Unk_P   = int(p_lTimings[16])
                         )

    def set_timing_data(self, H_Res, H_FP, H_Sync, H_BP,
                              V_Res, V_FP, V_Sync, V_BP,
                              P_Clock, R_Rate,
                              H_Pos = 0, H_Zoom = 0, V_Pos = 0, H_Freq = 0,
                              V_Unk = 0, H_Unk = 0,
                              Unk_0 = 0, Unk_1 = 0, Unk_2 = 0,
                              Unk_R = 0, Unk_P = 0
                              ):
        self.m_dData["H_Res"]   += H_Res
        self.m_dData["H_Unk"]   += H_Unk
        self.m_dData["H_FP"]    += H_FP
        self.m_dData["H_Sync"]  += H_Sync
        self.m_dData["H_BP"]    += H_BP
        self.m_dData["V_Res"]   += V_Res
        self.m_dData["V_Unk"]   += V_Unk
        self.m_dData["V_FP"]    += V_FP
        self.m_dData["V_Sync"]  += V_Sync
        self.m_dData["V_BP"]    += V_BP
        self.m_dData["Unk_0"]   += Unk_0
        self.m_dData["Unk_1"]   += Unk_1
        self.m_dData["Unk_2"]   += Unk_2
        self.m_dData["R_Rate"]  += R_Rate
        self.m_dData["Unk_R"]   += Unk_R
        self.m_dData["P_Clock"] += P_Clock
        self.m_dData["Unk_P"]   += Unk_P
        # --- calc
        self.m_dData["H_Pos"]   += H_Pos
        self.m_dData["H_Zoom"]  += H_Zoom
        self.m_dData["V_Pos"]   += V_Pos
        self.m_dData["H_Freq"]  += H_Freq


        # "Side_Game": video_data[12],
        #logging.info("CRT Timing: %s" % str(self.m_dData))

    # set unknown default values
    def set_timing_unk(self):
        self.m_dData["H_Unk"] = 1
        self.m_dData["V_Unk"] = 1
        self.m_dData["Unk_0"] = 0
        self.m_dData["Unk_1"] = 0
        self.m_dData["Unk_2"] = 0
        self.m_dData["Unk_R"] = 0
        self.m_dData["Unk_P"] = 1

    def get_values(self):
        with open(self.p_sTimingPath) as f:
            for line in f:
                lValues = line.strip().split(' ')
                if self.m_sSystem == lValues[0]:
                    return lValues[1:] # ignore first value
        return []

    def _raw_adjustement(self, H_Zoom, H_Mov, V_Mov):
        if H_Zoom:
            VMAX = (self.m_dData["V_Res"] + self.m_dData["V_FP"] + self.m_dData["V_BP"])
            HMAX = (self.m_dData["H_Res"] + self.m_dData["H_FP"] + self.m_dData["H_BP"]) - 2
            HZOOM_Normalized = int(round(H_Zoom, 0))
            RectHZOOMT3 = 0
            if HZOOM_Normalized > (self.m_dData["H_FP"] - 1):
                RectHZOOMT3 = self.m_dData["H_FP"] - 1
            RectHZOOMT5 = 0
            if HZOOM_Normalized > (self.m_dData["H_BP"] - 1):
                RectHZOOMT5 = self.m_dData["H_BP"] - 1
            if RectHZOOMT3:
                HZOOM_Normalized = RectHZOOMT3
                if RectHZOOMT5 and RectHZOOMT3 >= RectHZOOMT5:
                    HZOOM_Normalized = RectHZOOMT5
            elif RectHZOOMT5:
                HZOOM_Normalized = RectHZOOMT5
            self.m_dData["H_Res"] += HZOOM_Normalized * 2
            Reverse_HZOOM = HZOOM_Normalized * -1
            self.m_dData["H_FP"] += Reverse_HZOOM
            self.m_dData["H_BP"] += Reverse_HZOOM

        # HORIZONTAL MOVEMENT
        if H_Mov:
            H_Mov = int(round(H_Mov, 0))
            if H_Mov > 0 and (self.m_dData["H_FP"] - H_Mov) < 1:
                H_Mov = self.m_dData["H_FP"] - 1
            if H_Mov < 0 and (self.m_dData["H_BP"] + H_Mov) < 1:
                H_Mov = (self.m_dData["H_BP"] - 1) * -1
            self.m_dData["H_FP"] -= H_Mov
            self.m_dData["H_BP"] += H_Mov

        # VERTICAL MOVEMENT
        if V_Mov:
            V_Mov = int(round(V_Mov, 0))
            if V_Mov < 0 and (self.m_dData["V_BP"] + V_Mov) < 1:
                V_Mov = (self.m_dData["V_BP"] - 1) * -1
            if V_Mov > 0 and (self.m_dData["V_FP"] - V_Mov) < 1:
                V_Mov = self.m_dData["V_FP"] - 1
            self.m_dData["V_FP"] -= V_Mov
            self.m_dData["V_BP"] += V_Mov


    def _calculated_adjustement(self):
        # Scaling Front and back porch horizontals according to horizontal position and horizontal zoom settings.
        # H_Zoom*4 - H_Pos*4 MUST BE < to H_FP to not use negative value.
        # H_Zoom*4 + H_Pos*4 MUST BE < to H_BP to not use negative value.
        self.m_dData["H_FP"] -= self.m_dData["H_Zoom"] * 4
        self.m_dData["H_FP"] -= self.m_dData["H_Pos"] * 4
        # Do not use negative values for H_FP
        if self.m_dData["H_FP"] < 0:
            self.m_dData["H_FP"] = 0
        self.m_dData["H_BP"] -= self.m_dData["H_Zoom"] * 4
        self.m_dData["H_BP"] += self.m_dData["H_Pos"] * 4
        # Do not use negative values for H_BP
        if self.m_dData["H_BP"] < 0:
            self.m_dData["H_BP"] = 0

        # Total number of horizontal, visible and invisible pixels.
        H_Total = self.m_dData["H_Res"] + self.m_dData["H_FP"] + \
                self.m_dData["H_Sync"] + self.m_dData["H_BP"]

        # Calculate the number of lines and round (up)
        V_Total = int(ceil(self.m_dData["H_Freq"] / self.m_dData["R_Rate"]))
        # Calculate of the horizontal frequency and round (up)
        Horizontal = int(ceil(V_Total * self.m_dData["R_Rate"]))
        # Calculate of the pixel clock
        self.m_dData["P_Clock"] = Horizontal * H_Total

        # Calculate of the Vertical Front Porch.
        self.m_dData["V_FP"] = V_Total - self.m_dData["V_Res"]
        self.m_dData["V_FP"] -= self.m_dData["V_Sync"]
        self.m_dData["V_FP"] = self.m_dData["V_FP"] / 2.0
        # Round (down) the Vertical Front Porch.
        self.m_dData["V_FP"] = int(floor(self.m_dData["V_FP"]))
        # Check vertical position bigger than Vertical Front Porch
        if self.m_dData["V_Pos"] > self.m_dData["V_FP"]:
            self.m_dData["V_Pos"] = self.m_dData["V_FP"]
        # Final Calculation
        self.m_dData["V_FP"] -= self.m_dData["V_Pos"]

        # Calculate Vertical Back Porch.
        self.m_dData["V_BP"] = V_Total - self.m_dData["V_Res"]
        self.m_dData["V_BP"] -= self.m_dData["V_Sync"]
        self.m_dData["V_BP"] = int(self.m_dData["V_BP"] - self.m_dData["V_FP"])


    # FIXME: use internal data?
    def resolution_set(self, H_Res, H_FP, H_Sync, H_BP, H_Unk,
                             V_Res, V_FP, V_Sync, V_BP, V_Unk,
                             Unk_0, Unk_1, Unk_2,
                             R_Rate, Unk_R, P_Clock, Unk_P,
                             **_unused):
        # Generate vcgencmd command line in a string.
        cmd = "vcgencmd hdmi_timings "
        cmd += "%s %s %s %s %s " % ( H_Res, H_Unk, H_FP, H_Sync, H_BP )
        cmd += "%s %s %s %s %s " % ( V_Res, V_Unk, V_FP, V_Sync, V_BP )
        cmd += "%s %s %s " % ( Unk_0, Unk_1, Unk_2 )
        cmd += "%s %s %s %s > /dev/null" % ( R_Rate, Unk_R, P_Clock, Unk_P )
        self._resolution_call(cmd)

    def _resolution_call(self, p_sCMD):
        logging.info("CMD: %s" % p_sCMD)
        os.system(p_sCMD)
        os.system("fbset -depth 8 && fbset -depth 24")
