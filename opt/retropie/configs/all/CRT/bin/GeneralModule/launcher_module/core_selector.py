#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
core_selector.py.

50/60hz selector library for modules

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

import os, logging
from launcher_module.core_paths import CRT_AUTOFREQ_FILE, CRT_UTILITY_FILE
from launcher_module.file_helpers import ini_get, add_line, remove_line, touch_file
from launcher_module.utils import compact_rom_name, show_info, menu_options

LABELS50HZ = ["pal","nl","e","s","sw","fn","g","uk","gr","i","h","eu",
                "europe","europa","spain","germany","france","italy"]
LABELS60HZ = ["ntsc","1","4","a","j","b","k","c","u","hk","world","usa",
                "us","ue","jue","jap","jp","japan","japon","asia","usa,europe",
                "europe,usa","japan,usa","usa,japan"]
ALLOWED_FREQS = ["50", "60"]

class FrequencySelector(object):
    m_bFastBoot = False
    m_sFileName = ""
    m_sSelectFreq = ""
    m_sCompactedName = ""
    m_oFreqDB = None
    m_lOptFreq = [("60Hz / NTSC", "60"),
                  ("50Hz / PAL", "50")]

    def __init__(self, p_sFileName = ""):
        if not p_sFileName:
            logging.info("WARNING: NO filename passed, setting " % \
                         "60Hz by default")
            return "60"
        self.m_sFileName = p_sFileName
        self.m_sCompactedName = compact_rom_name(p_sFileName)
        self.m_oFreqDB = dbfreq()
        if ini_get(CRT_UTILITY_FILE, "fast_boot").lower() == "true":
            self.m_bFastBoot = True

    def get_frequency(self):
        # first i try to find an allowed freq
        self.m_sSelectFreq = ini_get(CRT_UTILITY_FILE, "freq_selector")
        if self.m_sSelectFreq in ALLOWED_FREQS:
            logging.info("Frequency selector always %sHz" % self.m_sSelectFreq)
            if self.m_sSelectFreq == "50":
                AutoSelection = "FORCED TO 50Hz / PAL"
            elif self.m_sSelectFreq == "60":
                AutoSelection = "FORCED TO 60Hz / NTSC"
            if ini_get(CRT_UTILITY_FILE, "autosel_info").lower() != "false":
                if not self.m_bFastBoot: show_info(AutoSelection)
        elif self.m_sSelectFreq == "auto":
            logging.info("Frequency selector mode auto")
            self.m_sSelectFreq = self.frecuency_auto()
        else:
            logging.info("Frequency selector mode manual")
            self.m_sSelectFreq = self.frequency_manual()
        return self.m_sSelectFreq

    def frecuency_auto(self):
        bFreqFound = False
        sFrequency = self.m_oFreqDB.find(self.m_sCompactedName)
        if sFrequency:
            bFreqFound = True
        else:
            sFrequency = self.frequency_by_name()
            if not sFrequency:
                sFrequency = self.frequency_manual()
            else:
                bFreqFound = True
        if bFreqFound:
            if sFrequency == "50":
                AutoSelection = "AUTO: 50Hz / PAL"
            elif sFrequency == "60":
                AutoSelection = "AUTO: 60Hz / NTSC"
            if ini_get(CRT_UTILITY_FILE, "autosel_info").lower() != "false":
                if not self.m_bFastBoot: show_info(AutoSelection)
        return sFrequency

    def frequency_manual(self):
        result = menu_options(self.m_lOptFreq)
        sFrequency = self.m_oFreqDB.find(self.m_sCompactedName)
        if not sFrequency:
            self.m_oFreqDB.add(self.m_sCompactedName, result)
        else:
            if sFrequency != result:
                self.m_oFreqDB.clean(self.m_sCompactedName)
                self.m_oFreqDB.add(self.m_sCompactedName, result)
        return result

    # TODO: optimize!
    def frequency_by_name(self):
        for CountryCODE in LABELS60HZ:
            if "(%s)"%CountryCODE in self.m_sFileName.lower() or "[%s]"%CountryCODE in self.m_sFileName.lower():
                self.m_oFreqDB.add(self.m_sCompactedName, "60")
                logging.info("60Hz Frequency label identified for: %s" % self.m_sFileName)
                return "60"
        for CountryCODE in LABELS50HZ:
            if "(%s)"%CountryCODE in self.m_sFileName.lower() or "[%s]"%CountryCODE in self.m_sFileName.lower():
                self.m_oFreqDB.add(self.m_sCompactedName, "50")
                logging.info("60Hz Frequency label identified for: %s" % self.m_sFileName)
                return "50"
        logging.info("Frequency label not identified for: %s" % self.m_sFileName)
        return ""

class dbfreq(object):
    """ frequency database handler """
    def __init__(self):
        if not os.path.isfile(CRT_AUTOFREQ_FILE):
            touch_file(CRT_AUTOFREQ_FILE)
            logging.info("Created frequency database")

    def find(self, p_sName):
        sFreqValue = ini_get(CRT_AUTOFREQ_FILE, p_sName)
        if sFreqValue in ALLOWED_FREQS:
            logging.info("Game found in current frequency database at %sHz" % sFreqValue)
            return sFreqValue
        elif not sFreqValue:
            logging.info("\"%s\" not found in current frequency database" % p_sName)
            return ""
        else:
            logging.info("\"%s\" found in current database with wrong Frequency" % p_sName)
            self.clean(p_sName)
            return ""

    def clean(self, p_sName):
        if remove_line(CRT_AUTOFREQ_FILE, p_sName):
            logging.info("Game was cleaned")
        else:
            logging.error("Game could not be cleaned")

    def add(self, p_sName, p_sFreq):
        if not p_sName or not p_sFreq:
            return
        add_line(CRT_AUTOFREQ_FILE, "%s %s" % (p_sName, p_sFreq))