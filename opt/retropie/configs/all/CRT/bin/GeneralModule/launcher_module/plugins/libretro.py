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

import os, sys, re
from distutils.version import LooseVersion
from launcher_module.core import launcher, logging, CRTROOT_PATH, RETROPIEEMU_PATH, RETROPIECFG_PATH
from launcher_module.file_helpers import md5_file, add_line, modify_line, ini_get

RETROARCH_CONFIGS_PATH = os.path.join(CRTROOT_PATH, "Retroarch/configs")
RETROARCH_DB_FILE = os.path.join(CRTROOT_PATH, "HashRetroarchVersionDB.txt")
RETROARCH_BINARY_FILE = os.path.join(RETROPIEEMU_PATH, "retroarch/bin/retroarch")
AUTOFREQ_DATABASE = os.path.join(CRTROOT_PATH, "AutoFreqDB.cfg")

CFG_CUSTOMEMU_FILE = os.path.join(RETROPIECFG_PATH, "all/emulators.cfg")

class libretro(launcher):
    m_sSystemCfg = ""
    m_sSystemCfgPath = ""

    @staticmethod
    def get_system_list():
        return ["sg-1000", "fds", "pcengine", "neogeo", "coleco", "atari7800",
                "vectrex", "pcenginecd", "zxspectrum", "amstradcpc"]

    # system configure vars
    def system_setup(self):
        if self.m_sSystem == "zxspectrum":
            self.m_sSystemFreq = "zxspectrum50"
        elif self.m_sSystem == "pcenginecd":
            self.m_sSystemFreq = "pcengine"
        else:
            super(libretro, self).system_setup()
        self.m_sSystemCfg = self.m_sSystemFreq + ".cfg"
        system_path = os.path.join(RETROARCH_CONFIGS_PATH, self.m_sSystemCfg)
        # if not exists report it
        if not os.path.exists(system_path):
            logging.error("not found cfg: %s" % system_path)
            return
        self.m_sSystemCfgPath = system_path

    # final configure binary/process values and prepare emulatorcfg
    def configure(self):
        self.m_lBinaryMasks = ["lr-"]
        self.m_lProcesses = ["retroarch"] # default emulator process is retroarch
        self.emulatorcfg_setup()
        self.ra_check_version() # need the correct m_sSystemCfgPath

    # we need check if retropie-menu changed something after command start
    def start(self):
        super(libretro, self).start() # command start (and set videomode)
        self.emulatorcfg_check_or_die()

    # just called if need rebuild the CMD
    def runcommand_generate(self, p_sCMD):
        current_cmd = super(libretro, self).runcommand_generate(p_sCMD)
        if not self.m_sSystemCfgPath:
            return current_cmd
        # update system_custom_cfg, used in ra_check_version
        append_cmd = "--appendconfig %s" % self.m_sSystemCfgPath
        append_cmd += " %ROM%"
        return current_cmd.replace("%ROM%", append_cmd)

    #  check if retroarch is lower than v1.7.5 because a change in aspect_ratio_index value
    def ra_check_version(self):
        if not self.m_sSystemCfgPath:
            return
        ra_hash = md5_file(RETROARCH_BINARY_FILE)
        f = open(RETROARCH_DB_FILE, "r")
        full_lines = f.readlines()
        f.close()
        ra_version = None
        for line in full_lines:
            lValues = line.strip().split(' ')
            if ra_hash == lValues[1]:
                ra_version = lValues[2]
                break
        # update file if not found
        if not ra_version:
            ra_output = commands.getoutput("%s --version" % RETROARCH_BINARY_FILE)
            for line in ra_output.splitlines():
                lValues = line.strip().split(' ')
                if 'RetroArch' in lValues[0]:
                    ra_version = lValues[5]
                    add_line(RETROARCH_DB_FILE, "RetroArch %s %s" % (ra_hash,ra_version))

        ratio = "23" # default 1.7.5 value
        if LooseVersion(ra_version) < LooseVersion("v1.7.5"):
            ratio = "22"
        ratio_value = ini_get(self.m_sSystemCfgPath, "aspect_ratio_index")
        if ratio != ratio_value.replace('"', ''):
            modify_line(self.m_sSystemCfgPath, "aspect_ratio_index", "aspect_ratio_index = \"%s\"" % ratio)
            logging.info("fixed: %s version: %s ratio: %s (%s)" % (self.m_sSystemCfgPath, ra_version, ratio, ratio_value))

    # emulatorcfg handlers

    def emulatorcfg_setup(self):
        """ prepare emulator to launch """
        try:
            self.emulatorcfg_add_systems()
            if not self.emulatorcfg_per_game():
                self.emulatorcfg_default(True)
        except IOError as e:
            infos = "File error at emulators.cfg [%s]" % self.m_sSystem
            infos2 = "Please, install at least one emulator or core"
            self.panic(infos, infos2)
        except Exception as e:
            infos = "Error in emulators.cfg [%s]" % self.m_sSystem
            self.panic(infos, str(e))

    # RETROPIE allows to choice per game an specific emulator from available
    # we check if emulator is valid or clean emulators.cfg
    def emulatorcfg_per_game(self):
        if not os.path.exists(CFG_CUSTOMEMU_FILE):
            return False
        sCleanName = re.sub('[^a-zA-Z0-9-_]+','', self.m_sGameName ).replace(" ", "")
        sGameSystemName = "%s_%s" % (self.m_sSystem, sCleanName)
        need_clean = False
        with open(CFG_CUSTOMEMU_FILE, 'r') as oFile:
            for line in oFile:
                lValues = line.strip().split(' ')
                if lValues[0] == sGameSystemName:
                    if self.is_valid_binary(lValues[2]):
                        self.m_sBinarySelected = lValues[2]
                        return True
                    else: # not valid is just ignored
                        need_clean = True
        # clean emulators.cfg if have an invalid binary
        if need_clean:
            logging.info("cleaning line %s from %s" % (sGameSystemName, CFG_CUSTOMEMU_FILE))
            remove_line(CFG_CUSTOMEMU_FILE, sGameSystemName)
        return False

    # we try to found this line: default = "emulator-binary-name"
    # p_oFile: file ready to seek
    # return: default emu or die
    def emulatorcfg_default(self, p_bSetCore):
        with open(self.m_sCfgSystemPath, "r") as oFile:
            for line in oFile:
                lValues = line.strip().split(' ')
                if lValues[0] == 'default':
                    sBinaryName = lValues[2].replace('"', '')
                    if p_bSetCore:
                        self.set_binary(sBinaryName)
                    else:
                        return self.is_valid_binary(sBinaryName)

    # we try to found emulator-binary-name = "command-to-launch-the-game"
    #   valid with our masks, if not found then die
    def emulatorcfg_add_systems(self):
        with open(self.m_sCfgSystemPath, "r") as oFile:
            self.m_lBinaries = []
            for line in oFile:
                lValues = line.strip().split(' ')
                if lValues[0] == 'default': # ignore default line
                    continue
                if self.is_valid_binary(lValues[0]):
                    self.m_lBinaries.append(lValues[0])
            if len(self.m_lBinaries):
                logging.info("VALID - emulators: %s" % str(self.m_lBinaries))
            else:
                self.panic("NOT FOUND any emulators mask [%s]" % str(self.m_lBinaryMasks))

    def emulatorcfg_check_or_die(self):
        bValidCore = self.emulatorcfg_default(False)
        if not bValidCore:
            self.emulatorcfg_kill()
            remove_line(self.m_sCfgSystemPath, "default =")
            self.panic("selected invalid emulator", "try again!")

    def emulatorcfg_kill(self):
        self.runcommand_wait(False)
        logging.error("closing %s processes" % str(self.m_lProcesses))
        for proc in self.m_lProcesses:
            os.system('killall %s > /dev/null 2>&1' % proc)

    # filter returns an array with valid values, we just check if has any value :)
    def is_valid_binary(self, p_sCore):
        if filter(lambda mask: mask in p_sCore, self.m_lBinaryMasks):
            return True
        else:
            return False

    def set_binary(self, p_sCore):
        if self.is_valid_binary(p_sCore):
            self.m_sBinarySelected = p_sCore
            logging.info("Selected binary (%s)" % self.m_sBinarySelected)
        else:
            raise NameError("INVALID - binary (%s) - mask [%s]" %
                (self.m_sBinarySelected, str(self.m_lBinaryMasks)) )
