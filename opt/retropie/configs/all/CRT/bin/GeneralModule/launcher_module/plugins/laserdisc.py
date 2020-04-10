#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
laserdisc.py.

launcher library for laserdisc (daphne) retropie by -krahs-.
This will fix joystick controls and adjust resolution based on multifrequency
and superresolutions. 

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

import os, logging, pygame
from launcher_module.core_selector import FrequencySelector
from launcher_module.emulator import emulator
from launcher_module.core_paths import *
from launcher_module.file_helpers import ini_get, add_line, touch_file, \
                                         ini_getlist, modify_line
from launcher_module.utils import show_info

JOYCONFIG_PATH = os.path.join(RETROPIE_CFG_PATH, "all/retroarch/autoconfig")

class laserdisc(emulator):
    m_sV_Res = ""
    m_lDaphneInfo = [("BETTER WITH KEYBOARD", "OK")]

    @staticmethod
    def get_system_list():
        return ["daphne"]

    # getting correct frequency for FileName loaded
    def configure(self):
        if self.m_sSystem == "daphne":
            self.m_lBinaryMasks = ["daphne"]
            self.m_lBinaryUntouchable = ["daphne"]
            FixDaphneControls(self.m_sSystem).fix()
        p_sSelectFreq = FrequencySelector(self.m_sFileName).get_frequency()
        self.m_sSystemFreq = self.m_sSystem
        if p_sSelectFreq == "50":
            self.m_sSystemFreq = self.m_sSystem + "50"
        show_info(self.m_lDaphneInfo)
        
    def create_daphne_config(self):
        """ custom commands for resolution """
        COMMAND_FILE = os.path.join(self.m_sFilePath,
                       "%s.commands" % self.m_sGameName)
        sOptions = ""
        # first value is flag, second if has any value
        lOptions = (["-ignore_aspect_ratio", False],
                    ["-x", str(self.m_oCRT.m_dData["H_Res"])],
                    ["-y", str(self.m_oCRT.m_dData["V_Res"])])
        # create full command string
        for option in lOptions:
            sOptions += option[0] + " "
            if option[1]:
                sOptions += option[1] + " "
                
        if os.path.exists(COMMAND_FILE):
            with open(COMMAND_FILE,"r+") as f:
                new_file = f.readlines()
                if not new_file:
                    new_file.append("")
                f.seek(0) # rewind
                bSaveFile = False
                for line in new_file:
                    bSaveLine = False
                    lValues = line.strip().replace('=',' ').split(' ')
                    for option in lOptions:
                        if not option[0] in lValues:
                            lValues.append(option[0])
                            if option[1]:
                                lValues.append(option[1])
                            bSaveLine = True
                        else:
                            if option[1]:
                                pos = lValues.index(option[0]) + 1
                                if lValues[pos] != option[1]:
                                    lValues[pos] = option[1]
                                    bSaveLine = True
                    line = " ".join(lValues) + "\n"
                    if bSaveLine:
                        f.write(line) # new line
                        bSaveFile = True
                if bSaveFile:
                    f.truncate() # remove everything after the last write
        else:        
            logging.info("INFO: creating daphne commandline " + \
                         "file: %s" % COMMAND_FILE)
            touch_file(COMMAND_FILE)
            add_line(COMMAND_FILE, sOptions)
            logging.info("INFO: daphne launch parameters " + \
                         "{%s}" % sOptions)

    def screen_set(self):
        super(laserdisc, self).screen_set()
        self.create_daphne_config()

    def runcommand_generate(self, p_sCMD):
        current_cmd = super(laserdisc, self).runcommand_generate(p_sCMD)
        if self.m_sNextValidBinary in self.m_lBinaryUntouchable:
            return current_cmd
        # update system_custom_cfg, used in ra_version_fixes
        append_cmd = "--appendconfig %s" % self.m_sCustomRACFG
        append_cmd += " " + self.m_sFileNameVar
        return current_cmd.replace(self.m_sFileNameVar, append_cmd)

class FixDaphneControls(object):
    """
    This class will try to get current joystick button configuration
    under Retropie/EmulationStation to apply it into daphne config.
    Daphne will autoconfigure analog joystick direction, so this 
    function only will change BUTTON1 (b), BUTTON2 (a), BUTTON3 (x),
    START1 (start), COIN1 (select).
    Will disable directions based buttons preconfigured on daphne
    because may enter in conflict with currect ones on retropie joystick
    autoconfig.
    WHEN POSSIBLE BETTER USE KEYBOARD OR JOY WITH ANALOG PAD/DIRECTIONS
    """
    DAPHNE_CFG_FILE = ""
    m_sJoyName = ""
    m_sCfgFile = ""
    m_lDaphneBTN = (["KEY_UP", "0", "clear"],
                    ["KEY_DOWN", "0", "clear"],
                    ["KEY_LEFT", "0", "clear"],
                    ["KEY_RIGHT", "0", "clear"],
                    ["KEY_BUTTON1", "1", "input_b_btn"],
                    ["KEY_BUTTON2", "2", "input_a_btn"],
                    ["KEY_BUTTON3", "3", "input_x_btn"],
                    ["KEY_SKILL1", "0", "input_y_btn"],
                    ["KEY_SKILL2", "0", "input_l_btn"],
                    ["KEY_SKILL3", "0", "input_r_btn"],
                    ["KEY_START1", "9", "input_start_btn"],
                    ["KEY_COIN1", "10", "input_select_btn"])
    
    def __init__(self, p_sSystem = "daphne"):
        self.DAPHNE_CFG_FILE = os.path.join(RETROPIE_CFG_PATH, p_sSystem,
                                            "dapinput.ini")

    def fix(self):
        if self._initialize_pygame():
            self.m_sCfgFile = os.path.join(JOYCONFIG_PATH, 
                                           self.m_sJoyName + '.cfg')
            if os.path.exists(self.m_sCfgFile) and \
               os.path.exists(self.DAPHNE_CFG_FILE):
                    self._get_joy_cfg()
                    self._fix_daphne_cfg()
                    self.__clean()
                    return True
        return False

    def _get_joy_cfg(self):
        for button in self.m_lDaphneBTN:
            btn_temp = self._joy_get_cfg(self.m_sCfgFile, button[2])
            if btn_temp: button[1] = str(int(btn_temp) + 1)

    def _fix_daphne_cfg(self):
        for control in self.m_lDaphneBTN:
            lValues = ini_getlist(self.DAPHNE_CFG_FILE, control[0])
            # clean returned empty values:
            iClearPos = []
            for idx, value in enumerate(lValues):
                if value == "": iClearPos.append(idx)
            if iClearPos:
                for pos in sorted(iClearPos, reverse=True):
                    del lValues[pos]
            # edit daphne controls config file
            if lValues[-1] != control[1]:
                lValues[-1] = control[1]
                sNewLine = control[0] + " = "
                sNewLine += " ".join(lValues)
                modify_line(self.DAPHNE_CFG_FILE, control[0], sNewLine)
    
    def _initialize_pygame(self):
        bCheck = False
        try:
            pygame.joystick.init()
            pygame.joystick.Joystick(0).init()
            self.m_sJoyName = pygame.joystick.Joystick(0).get_name()
            bCheck = True
        except:
            bCheck = False
        self.__clean()
        return bCheck

    def _joy_get_cfg(self, p_sCfgFile, p_sINI):
        temp = ini_get(p_sCfgFile, p_sINI)
        if temp:
            try:
                temp = temp.replace('"', '')
                logging.info("INFO: found %s = %s" % (p_sINI, temp))
            except:
                logging.info("WARNING: value no found for %s in %s" % (p_sINI, p_sCfgFile))
                return False
        return temp
        
    def __clean(self):
        pygame.joystick.quit() 
        