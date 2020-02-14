#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
launcher amiga.py.

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
import xml.etree.ElementTree as ET
from launcher_module.core import RETROPIE_PATH, TMP_LAUNCHER_PATH, TMP_SLEEPER_FILE, CRTROOT_PATH
from launcher_module.emulator import emulator
from launcher_module.file_helpers import add_line, modify_line, remove_file
from launcher_module.core_choices_dynamic import choices
from launcher_module.utils import something_is_bad
from launcher_module.screen import CRT

DB_AMIGA = os.path.join(CRTROOT_PATH, "Resolutions/amiga_games.txt")
AMIBERRY_BASE_PATH = "/opt/retropie/configs/amiga/amiberry/whdboot"
AMIBERRY_HOSTPREFS_FILE = "%s/hostprefs.conf" % AMIBERRY_BASE_PATH
AMIBERRY_WHDLOADDB_FILE = "%s/game-data/whdload_db.xml" % AMIBERRY_BASE_PATH

class amiga(emulator):
    m_nAmiberryVertRes = 0
    m_bAmiberriWHDLoadDBGameFound = False
    m_sAmigaResolution = ""

    def config_generate(self):
        pass

    def screen_prepare(self):
        if "+Start Amiberry" in self.m_sGameName:
            self.amiberry_pre_config_generator()
            self.m_sSystemFreq = self.m_sAmigaResolution
        elif "amiberry" in self.m_sBinarySelected:
            self.amiberry_pre_config_generator()
            self.amiberry_config_generator()
            self.m_sSystemFreq = self.m_sAmigaResolution
        elif "lr-puae" in self.m_sBinarySelected:
            self.m_sSystemFreq = "amiga_lr-puae"
        logging.info("binary: %s" % self.m_sBinarySelected)

    def screen_set(self):
        self.m_oCRT = CRT(self.m_sSystemFreq)
        if "+Start Amiberry" in self.m_sGameName:
            self.m_oCRT.screen_calculated(DB_AMIGA)
        elif "amiberry" in self.m_sBinarySelected:
            self.m_oCRT.screen_calculated(DB_AMIGA)
        elif "lr-puae" in self.m_sBinarySelected:
            self.m_oCRT.screen_calculated(DB_AMIGA)
        self.m_oBlackScreen.fill()
        logging.info("clean: %s", TMP_SLEEPER_FILE)
        remove_file(TMP_SLEEPER_FILE)

    def amiberry_files_check(self):
        m_bFileMiss = False
        if not os.path.exists(AMIBERRY_HOSTPREFS_FILE):
            logging.error("not found amiberry cfg file: %s" % AMIBERRY_HOSTPREFS_FILE)
            m_bFileMiss = True
        if not os.path.exists(AMIBERRY_WHDLOADDB_FILE):
            logging.error("not found amiberry cfg file: %s" % AMIBERRY_WHDLOADDB_FILE)
            m_bFileMiss = True
        
        if m_bFileMiss:
            self.panic("amiberry warning:", "can't find one o more cfg files")

    def amiberry_pre_config_generator(self):
        self.amiberry_files_check()
        self.m_sAmigaResolution = "amiga_amiberry_default" 
        modify_line(AMIBERRY_HOSTPREFS_FILE, "ASPECT_RATIO_FIX=", "ASPECT_RATIO_FIX=FALSE")
        
    def amiberry_config_generator(self):
        self.show_info("Loading AMIBERRY WHDLoad Database...")
        logging.info("preparing amiberry configuration")
        if self.amiberry_database_search():
            if self.amiberry_stretch_selector():
                self.m_sAmigaResolution = "amiga_amiberry_" + self.m_nAmiberryVertRes
        else:
            if self.m_bAmiberriWHDLoadDBGameFound == False:
                self.show_info("Game not found in WHDLoad Database!", "AMIBERRY INFORMATION")
            else:
                self.show_info("Applying default vertical resolution!", "AMIBERRY INFORMATION")

    def amiberry_database_search(self):
        """
        This function will check amiberry WHDLoad Database in search of vertical 
        resolution of selected game.

        Returns
        -------
        False
            If not vertical resolution was found even game exist in database
        True
            Game and vertical resolution was found on WHDLoad Database
        """
        self.m_nAmiberryVertRes = 0
        tree = ET.parse(AMIBERRY_WHDLOADDB_FILE)
        root = tree.getroot()
        self.m_bAmiberriWHDLoadDBGameFound = False
        m_sAttribute = 'SCREEN_HEIGHT='
        for game in root.findall('game'):
            if game.get('filename') == self.m_sGameName:
                self.m_bAmiberriWHDLoadDBGameFound = True
                n = game.find('hardware').text
                p = n.find(m_sAttribute)
                if p > 0:
                    self.m_nAmiberryVertRes = n[p + len(m_sAttribute) : p + len(m_sAttribute) + 3]
                break
        if self.m_bAmiberriWHDLoadDBGameFound and self.m_nAmiberryVertRes > 0:
            logging.error("amiberry game and vertical resolution found: %s %s" % (self.m_sGameName, self.m_nAmiberryVertRes))
            return True
        else:
            logging.error("amiberry game or vertical resolution NOT found: %s %s" % (self.m_sGameName, self.m_nAmiberryVertRes))
            return False

    def amiberry_stretch_selector(self):
        ch = choices()
        ch.set_title("VERTICAL RESOLUTION")
        ch.load_choices([
                ("Force 1:1 (Original)", "0"),
                ("Try to stretch", "1"),
            ])
        result = ch.run()
        ch.cleanup()
        if result == "0":
            return True
        return False
        
    def show_info(self, m_sMessage, m_sTitle = None):
        ch = choices()
        if m_sTitle:
            ch.set_title(m_sTitle)
        ch.load_choices([(m_sMessage, "OK")])
        ch.show(3000)
        ch.cleanup()
        
    def emulatorcfg_check_or_die(self):
        """
        After runcommand-config is closed we check if emulator still be valid or die!

        Panic
        -----
            if not valid default emulator is found.
            if user change screen resolution config.
        """
        super(amiga, self).emulatorcfg_check_or_die()

        if self.m_sAmigaFirstBinary != self.m_sBinarySelected:
            self._emulatorcfg_die()
            self.panic("you change initial emulator", "restart for %s emulation" % self.m_sBinarySelected)