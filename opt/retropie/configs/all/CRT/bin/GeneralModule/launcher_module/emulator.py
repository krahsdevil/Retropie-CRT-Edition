#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
launcher emulator.py.

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

import os, re, logging
from launcher_module.core import launcher
from launcher_module.core_paths import RETROPIE_CUSTEMU_FILE
from launcher_module.file_helpers import remove_line, touch_file

class emulator(launcher):
    """
    Used in emulators installed by retropie, we check here emulators.cfg file
    """
    def prepare(self):
        """
        after configure we need set netplay data and get current emulator
        """
        self.netplay_setup()
        self.emulatorcfg_prepare()
        super(emulator, self).prepare() # core command prepare

    def start(self):
        """
        We need check if retropie-menu changed something after command start
        """
        super(emulator, self).start() # command start (and set videomode)
        self.emulatorcfg_check_or_die()

    # TODO: Read data from EasyNetplay
    def netplay_setup(self):
        self.m_sNetIP = ""

    def emulatorcfg_prepare(self):
        """
        Prepare emulator to launch

        Panic
        -----
            if not valid default emulator is found
            if not cores are installed
        """
        try:
            self.emulatorcfg_add_systems()
            if self.emulatorcfg_default_check() == False:
                 self.panic("No valid emulator selected", "Please, try again!")
            self.emulatorcfg_per_game()
            
        except IOError as e:
            infos = "Emulators.cfg [%s] not found" % self.m_sSystem
            infos2 = "Please, install one emulator or core"
            self.panic(infos, infos2)
        except Exception as e:
            infos = "Error in emulators.cfg [%s]" % self.m_sSystem
            self.panic(infos, str(e))

    def emulatorcfg_per_game(self):
        """
        Retropie allows to choice per game an specific emulator from available
        we check if emulator is valid or clean emulators.cfg

        Returns
        -------
        False
            If emulator is wrong and it was cleaned
        True
            Emulator is ok or not specific emulator for this game was selected
        """
        p_bNeedClean = False
        if not os.path.exists(RETROPIE_CUSTEMU_FILE):
            #create emulators.cfg if doesn't exists
            touch_file(RETROPIE_CUSTEMU_FILE)
            logging.info("Created emulators.cfg")
        sCleanName = re.sub('[^a-zA-Z0-9-_]+','', self.m_sGameName ).replace(" ", "")
        sGameSystemName = "%s_%s" % (self.m_sSystem, sCleanName)

        with open(RETROPIE_CUSTEMU_FILE, 'r') as oFile:
            for line in oFile:
                lValues = line.strip().split(' ')
                if lValues[0] == sGameSystemName:
                    sBinaryName = lValues[2].replace('"', '')
                    if self.set_binary(sBinaryName):
                        logging.info("(%s) is " % self.m_sSelCore + \
                                     "selected for this game, will " + \
                                     "be the chosen core to launch")
                        return True
                    else: # not valid is just ignored
                        p_bNeedClean = True
        # clean emulators.cfg if have an invalid binary
        if p_bNeedClean:
            logging.info("cleaning line %s from %s" % (sGameSystemName, RETROPIE_CUSTEMU_FILE))
            remove_line(RETROPIE_CUSTEMU_FILE, sGameSystemName)
            return False
        return True

    #
    # p_oFile: file ready to seek
    # return: default emu or die
    def emulatorcfg_default_check(self):
        """
        We try to found this line: default = "emulator-binary-name"

        Returns
        -------
        True
            Emulator is ok!
        False
            If default emulator selected is invalid and it was cleaned
        None
            If not found default line (then Retropie launch a selector)
        """
        with open(self.m_sCfgSystemPath, "r") as oFile:
            for line in oFile:
                lValues = line.strip().split(' ')
                if lValues[0] == 'default':
                    sBinaryName = lValues[2].replace('"', '')
                    if not self.set_binary(sBinaryName):
                        remove_line(self.m_sCfgSystemPath, "default =")
                        return False
                    else:
                        logging.info("(%s) is selected as default" % self.m_sSelCore)
                        return True
                    #return self.set_binary(sBinaryName)
            return None

    def emulatorcfg_add_systems(self):
        """
        We try to found a valid emulator-binary-name = "command-to-launch-game"

        Panic
        -----
            if not valid emulators are found, then die!
        """
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
                self.panic("NOT VALID emulators bin/masks found [%s]" % str(self.m_lBinaryMasks))

    def emulatorcfg_check_or_die(self):
        """
        After runcommand-config is closed we check if emulator still be valid or die!

        Panic
        -----
            if not valid default emulator is found.
            if user change screen resolution config.
        """
        if not self.emulatorcfg_default_check():
            self.runcommand_kill()
            self.panic("No valid emulator selected", "Please, try again!")
        if not self.emulatorcfg_per_game():
            self.runcommand_kill()
            self.panic("No valid emulator for this game", "Please, try again!")
        if self.clean_videomodes():
            self.runcommand_kill()
            self.panic("Don't change emulator resolution", "Please, try again!")

    def is_valid_binary(self, p_sCore):
        """
        We check if core is valid using our list of m_lBinaryMasks

        Parameters
        ----------
        p_sCore : str
            Current core name

        Returns
        -------
        True
            Emulator is valid
        False
            Emulator is invalid
        """
        # filter returns an array with valid values, we just check if has any value
        if not self.m_lBinaryMasks:
            logging.info("Not emulator masks defined, any binary/emulator allowed")
            return True
        elif filter(lambda mask: mask in p_sCore, self.m_lBinaryMasks):
            return True
        else:
            return False

    def set_binary(self, p_sCore):
        """
        If core is valid the set value in our m_sSelCore

        Parameters
        ----------
        p_sCore : str
            Current core name

        Returns
        -------
        True
            Emulator is valid.
        False
            If emulator is invalid and default value is cleaned.
        """
        if self.is_valid_binary(p_sCore):
            self.m_sSelCore = p_sCore
            logging.info("active core: {%s}" % self.m_sSelCore)
            return True
        else:
            logging.error("INVALID - binary (%s) - mask [%s]" %
                (self.m_sSelCore, str(self.m_lBinaryMasks)) )
            return False
