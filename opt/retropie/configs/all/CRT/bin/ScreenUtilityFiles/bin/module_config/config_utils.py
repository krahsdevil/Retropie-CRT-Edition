#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Configuration Utility

https://github.com/krahsdevil/crt-for-retropie/

Copyright (C)  2018/2020 -krahs- - https://github.com/krahsdevil/

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

import sys, os, imp, math, re, time, shlex
import logging, subprocess, commands
import xml.etree.ElementTree as ET
import socket, fcntl, struct
import pygame

sys.dont_write_bytecode = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(SCRIPT_DIR + "/../"))
from main_paths import MODULES_PATH
sys.path.append(MODULES_PATH)

from launcher_module.screen import CRT
from launcher_module.core_paths import CRT_FIXMODES_FILE, CRT_UTILITY_FILE, \
                                       CRT_EXTSTRG_SRV_PATH, CRT_EXTSTRG_CORE_PATH, \
                                       CRT_EXTSTRG_SRV_FILE, CRT_BGM_SRV_FILE, \
                                       CRT_EXTSTRG_TRIG_MNT_PATH, CRT_EXTSTRG_TRIG_UMNT_PATH, \
                                       CRT_BGM_SRV_PATH, CRT_BGM_CORE_PATH, TMP_LAUNCHER_PATH, \
                                       ES_SYSTEMS_PRI_FILE, RETROPIE_MENU, RETROPIE_HOME_PATH, \
                                       RASP_BOOTCFG_FILE, RETROPIE_CFG_PATH, \
                                       ES_THEMES_PRI_PATH, ES_THEMES_SEC_PATH, CRT_DB_SYSTEMS_FILE
from launcher_module.utils import check_process, touch_file, get_side
from launcher_module.file_helpers import ini_get, ini_getlist, modify_line, \
                                         ini_set, remove_line
from launcher_module.core_controls import joystick, CRT_UP, CRT_DOWN, \
                                          CRT_LEFT, CRT_RIGHT, CRT_OK, \
                                          CRT_CANCEL

SYSTEMSDB =    {
                "amiga": "AMIGA", "amstradcpc": "AMSTRAD CPC", "arcade": "ARCADE",
                "atari800": "ATARI 800", "atari2600": "ATARI 2600",
                "atari7800": "ATARI 7800", "atarilynx": "ATARI Lynx",
                "atarist": "ATARI ST", "c64": "COMMODORE 64", "coleco": "ColecoVision",
                "daphne": "Daphne", "fba": "FinalBurn Neo", "fds": "FDS",
                "gamegear": "SEGA GameGear", "gb": "Gameboy", "gba": "Gameboy Advance",
                "gbc": "Gameboy Color", "mame-advmame": "Advance MAME",
                "mame-libretro": "MAME", "mastersystem": "Master System",
                "megadrive": "Megadrive", "msx": "MSX", "n64": "Nintendo 64",
                "neogeo": "NEOGEO", "neogeocd": "NEOGEO CD", "nes": "NES",
                "ngp": "NEOGEO Pocket", "ngpc": "NEOGEO Pocket C.",
                "pcengine": "PC Engine", "pcenginecd": "PC Engine CD",
                "psx": "Play Station", "sega32x": "SEGA 32X", "segacd": "SEGA CD",
                "sg-1000": "SEGA SG-1000", "snes": "Super Nintendo",
                "vectrex": "Vectrex", "videopac": "Videopac",
                "wonderswan": "WonderSwan", "wonderswancolor": "WonderSwan C.",
                "zx81": "SINCLAIR ZX81", "zxspectrum": "ZX Expectrum",
               }

def run(sCommandline, sDBSys = None):
    oCRT = None
    if sDBSys:
        oCRT = CRT(sDBSys)
        oCRT.screen_calculated(CRT_DB_SYSTEMS_FILE)
    oRunProcess = subprocess.Popen(shlex.split(sCommandline), shell=False)
    iExitCode = oRunProcess.wait()
    if oCRT:
        oCRT.screen_restore()

def find_submenus(p_sPath, p_sMask):
    submenus = []
    possiblesubs = os.listdir(p_sPath)
    possiblesubs.sort()
    for sub in possiblesubs:
        location = os.path.join(p_sPath, sub)
        cname = re.sub(r'\d+$', "", str(sub.split(".")[0]))
        if p_sMask == cname and sub.endswith(".py"):
            logging.info("loaded: %s " % sub)
            sClass = sub[:-3]
            info = imp.find_module(sClass, [p_sPath])
            submenus.append({"name": sClass, "info": info})
    return submenus

def load_submenu(p_oPlugin):
    _module = imp.load_module(p_oPlugin["name"], *p_oPlugin["info"])
    return getattr(_module, p_oPlugin["name"])

def explore_list(p_iJoy, p_sValue, p_lList = None):
    value = p_sValue
    list = []
    new = None
    if p_lList: list = p_lList

    if type(value) == type(True):
        if p_iJoy & CRT_OK:
            new = not value
    else:
        if value in list:
            pos = list.index(value)
            leng = len(list)
            if p_iJoy & CRT_RIGHT:
                if  leng > 1 and (pos + 1) < leng:
                    new = list[pos + 1]
            if p_iJoy & CRT_LEFT:
                if  leng > 1 and (pos - 1) >= 0:
                    new = list[pos - 1]
    logging.info("new value is: %s" % new)
    return new

def get_ip_address(p_sIFname):
    if p_sIFname == "public":
        addr = os.popen('wget -qO- http://ipecho.net/plain --timeout=0.8 --tries=1 ; echo').readlines(-1)[0].strip()
        if addr: return addr
        else: return "Not Available"
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        addr = socket.inet_ntoa(fcntl.ioctl(s.fileno(),
              0x8915,  # SIOCGIFADDR
              struct.pack('256s', p_sIFname[:15]))[20:24])
    except: addr = "Disconnected"

    if p_sIFname == "wlan0" and addr == "Disconnected":
        command = "iwgetid -r"
        output = commands.getoutput(command).strip()
        if output: addr = "Connected"

    if p_sIFname == "eth0":
        command = "sudo ethtool %s | grep \"Link detected\"" % p_sIFname
        output = commands.getoutput(command).strip()
        if addr != "Disconnected":
            if "no" in output.lower(): addr = "Disconnected"
        elif addr == "Disconnected":
            if "yes" in output.lower(): addr = "Trying to get IP..."
    return addr

def get_modes():
    p_lList = []
    p_lList.append("Default")
    with open(CRT_FIXMODES_FILE, 'r') as f:
        for line in f:
            line = re.sub(r' +', " ", line)
            line = line.strip().replace('=',' ').split(' ')
            if line[0].lower() == "mode":
                p_lList.append(line[1])
    return p_lList

def get_themes():
    p_lList = []
    path = ES_THEMES_PRI_PATH
    if get_side() != 0: path = ES_THEMES_SEC_PATH
    try:
        content = os.listdir(path)
        for item in content:
            if os.path.isdir(os.path.join(path, item)):
                p_lList.append(item)
    except: pass
    if p_lList: p_lList.sort()
    return p_lList

def hide_retropie_menu(p_bEnable = True):
    p_bCheck = False
    TMP = os.path.join(TMP_LAUNCHER_PATH, "myfile.cfg")
    os.system('cp %s %s > /dev/null 2>&1' % (ES_SYSTEMS_PRI_FILE, TMP))
    if p_bEnable: p_sPath = os.path.join(RETROPIE_HOME_PATH, "disabled.retropiemenu")
    else: p_sPath = RETROPIE_MENU
    oTree = ET.parse(TMP)
    oRoot = oTree.getroot()
    try:
        for sys in oRoot.iter('system'):
            if sys.find('name').text == "retropie":
                sys.find('path').text = p_sPath
                p_bCheck = True
                break
        if p_bCheck: oTree.write(TMP)
        os.system('sudo cp %s %s > /dev/null 2>&1' %(TMP, ES_SYSTEMS_PRI_FILE))
        os.system("sudo rm %s > /dev/null 2>&1" % TMP)
    except: return False
    return p_bCheck

def check_retropie_menu():
    oTree = ET.parse(ES_SYSTEMS_PRI_FILE)
    oRoot = oTree.getroot()
    try:
        for sys in oRoot.iter('system'):
            if sys.find('name').text == "retropie":
                if sys.find('path').text == RETROPIE_MENU:
                    return True
                break
        return False
    except: return False

def check_es_restart(p_lList, p_lCtrl):
    p_bCheck = False
    count = 0
    for opt in p_lCtrl:
        try:
            # if 'es_restart' is present and True, implies
            # emulationstation needs restart if value change
            if opt['es_restart']:
                if opt['value'] != p_lList[count]['value']: p_bCheck = True
        except:
            pass
        count += 1
    return p_bCheck

def check_sys_reboot(p_lList, p_lCtrl):
    p_bCheck = False
    count = 0
    for opt in p_lCtrl:
        try:
            # if 'es_restart' is present and True, implies
            # emulationstation needs restart if value change
            if opt['sys_reboot']:
                if opt['value'] != p_lList[count]['value']: p_bCheck = True
        except:
            pass
        count += 1
    return p_bCheck

def launching_images(p_bShow):
    for (root,dirs,files) in os.walk(RETROPIE_CFG_PATH, topdown=True):
            for f in files:
                if not "/all" in root:
                    if f[-4:] in (".png", ".jpg"):
                        p_sFile = os.path.join(root, f)
                        rename_image(p_sFile, p_bShow)

def rename_image(p_sImage, p_bShow):
    img_dis = "dis_launching"
    img_ena = "launching"
    img_src = img_ena
    img_dst = img_dis
    if p_bShow:
        img_src = img_dis
        img_dst = img_ena

    file = os.path.basename(p_sImage)
    ext = file[-4:]
    path = os.path.dirname(os.path.abspath(p_sImage))
    logging.info("filename: %s" % file[:-4])
    if file[:-4] != img_src: return

    filepath_dst = os.path.join(path, img_dst)
    filepath_dst += ext
    os.system('mv -f "%s" "%s" > /dev/null 2>&1' % \
             (p_sImage, filepath_dst))

def press_back():
    m_oJoyHandler = joystick()
    while True:
        event = m_oJoyHandler.event_wait()
        if event & CRT_CANCEL:
            m_oJoyHandler.quit()
            break

def render_image(p_sImg):
    if not os.path.exists(p_sImg):
        logging.info("INFO: image not found")
        return None
    try:
        img = pygame.image.load(p_sImg).convert_alpha()
        rect = img.get_rect()
        rect.bottomleft = (0, rect.height)
        sf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        sf.blit(img, rect)
        return sf
    except:
        raise
        #return None

def restart_ES():
    """ Restart ES if it's running """
    if check_process("emulationstatio"):
        logging.info("INFO: Restarting EmulationStation...")
        commandline = "touch /tmp/es-restart "
        commandline += "&& pkill -f \"/opt/retropie"
        commandline += "/supplementary/.*/emulationstation([^.]|$)\""
        os.system(commandline)
        #os.system('clear')

class wifi(object):
    COUNTRY = {
               'Austria': 'AT', 'Australia': 'AU', 'Belgium': 'BE', 'Brazil': 'BR',
               'Canada': 'CA', 'Switzerland': 'CH', 'China': 'CN',
               'Cyprus': 'CY', 'Czech Republic': 'CZ', 'Germany': 'DE', 'Denmark': 'DK',
               'Estonia': 'EE', 'Spain': 'ES', 'Finland': 'FI', 'France': 'FR',
               'United Kingdom': 'GB', 'Greece': 'GR', 'Hong Kong': 'HK', 'Hungary': 'HU',
               'Indonesia': 'ID', 'Ireland': 'IE', 'Israel': 'IL', 'India': 'IN',
               'Iceland': 'IS', 'Italy': 'IT', 'Japan': 'JP', 'Korea': 'KR',
               'Lithuania': 'LT', 'Luxembourg': 'LU', 'Latvia': 'LV', 'Malaysia': 'MY',
               'Netherlands': 'NL', 'Norway': 'NO', 'New Zealand': 'NZ', 'Philippines': 'PH',
               'Poland': 'PL', 'Portugal': 'PT', 'Sweden': 'SE', 'Singapore': 'SG',
               'Slovenia': 'SI', 'Slovak Republic': 'SK', 'Thailand': 'TH', 'Taiwan': 'TW',
               'USA': 'US', 'South Africa': 'ZA'
              }
    m_sMode = "Manual"
    m_lModes = ["Manual", "Detect"]
    m_lSSIDs = ["[A:SCAN]"]
    m_sSSIDSel01 = "[Your SSID]" # manual selected ssid
    m_sSSIDSel02 = m_lSSIDs[0] # scaned selected ssid
    m_sPwd = ""
    m_sCountry = ""
    WPA_FILE = '/etc/wpa_supplicant/wpa_supplicant.conf'
    TMP_FILE = os.path.join(TMP_LAUNCHER_PATH, "wpa_supplicant.conf")

    def __init__(self):
        pass

    def detect(self, p_sValue):
        if p_sValue != "[A:SCAN]": return
        commandline = "sudo iw wlan0 scan | egrep 'SSID:|signal:'"
        output = commands.getoutput(commandline).split('\n')
        if "command failed: Network is down (-100)" in output:
            os.system('sudo rfkill unblock wifi; sudo rfkill unblock all')
            output = commands.getoutput(commandline).split('\n')
        # clean output command
        p_dSSIDs = {}
        for line in output:
            sig = line.replace('dBm', '').strip().split(': ')
            if 'signal' in sig[0]:
                idx = output.index(line) + 1
                ssid = output[idx].strip().split(': ')
                try:
                    if 'SSID' in ssid[0] and not '\\x00' in ssid[1]:
                        name = ssid[1]
                        if name in p_dSSIDs:
                            if float(p_dSSIDs[name]) < float(sig[1]):
                                p_dSSIDs[name] = sig[1]
                        else: p_dSSIDs[name] = sig[1]
                except: pass
        #clean list
        p_lSSIDs = []
        for ssid in p_dSSIDs:
            p_lSSIDs.append(ssid)
        p_lSSIDs.append("[A:SCAN]")
        self.m_lSSIDs = p_lSSIDs
        self.ssid(self.m_lSSIDs[0])
        return self.m_lSSIDs

    def country(self, p_sCountry):
        ini_set(CRT_UTILITY_FILE, "wifi_country", self.COUNTRY[p_sCountry])
        self.m_sCountry = p_sCountry

    def get_country(self):
        if not self.m_sCountry:
            os.system('cp %s %s > /dev/null 2>&1' % (self.WPA_FILE, self.TMP_FILE))
            ctry = ini_get(self.TMP_FILE, "country")
            os.system("sudo rm %s > /dev/null 2>&1" % self.TMP_FILE)
            if not ctry:
                ctry = ini_get(CRT_UTILITY_FILE, "wifi_country")
                if not ctry: ctry = "ES"
            for item in self.COUNTRY:
                if self.COUNTRY[item] == ctry:
                    self.m_sCountry = item
                    break
            if not self.m_sCountry:
                self.m_sCountry = "Spain"
            self.country(self.m_sCountry)
        return self.m_sCountry

    def get_country_list(self):
        if not self.status():
            list = []
            for item in self.COUNTRY:
                list.append(item)
            list.sort()
            return list
        return None

    def connect(self):
        if self.get_ssid() == "[A:SCAN]" or self.get_pwd == "": return False
        touch_file(self.TMP_FILE)
        p_sLine1 = 'country=%s' % self.COUNTRY[self.get_country()]
        p_sLine2 = 'ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev'
        p_sLine3 = 'update_config=1'
        p_sSSIDFix = self.get_ssid()
        p_sSSIDFix = p_sSSIDFix.replace(' ', '\\ ')
        p_sSSIDFix = p_sSSIDFix.replace("'", '\xe2\x80\x99')
        p_sPWDFix = self.get_pwd()
        p_sPWDFix = p_sPWDFix.replace(' ', '\\ ')
        p_sPWDFix = p_sPWDFix.replace("'", '\xe2\x80\x99')
        p = subprocess.Popen('wpa_passphrase ' + p_sSSIDFix + ' ' + p_sPWDFix, stdout=subprocess.PIPE, shell=True)
        output, err = p.communicate()
        p.wait()
        if 'network={' in output:
            with open(self.TMP_FILE, 'w') as f:
                f.write(p_sLine1 + '\n')
                f.write(p_sLine2 + '\n')
                f.write(p_sLine3 + '\n')
                f.write(output)
        else:
            with open(self.TMP_FILE, 'w') as f:
                f.write(p_sLine1 + '\n')
                f.write(p_sLine2 + '\n')
                f.write(p_sLine3 + '\n')
        remove_line(self.TMP_FILE, '#psk="')
        os.system('sudo cp %s %s > /dev/null 2>&1' %(self.TMP_FILE, self.WPA_FILE))
        os.system("sudo rm %s > /dev/null 2>&1" % self.TMP_FILE)
        p = subprocess.Popen('wpa_cli -i wlan0 reconfigure', stdout=subprocess.PIPE, shell=True)
        output, err = p.communicate()
        p.wait()
        p_iTime = time.time()
        p_bCheck = False
        while True:
            if time.time() - p_iTime > 60: return p_bCheck
            if self.status():
                p_bCheck = True
                return p_bCheck
            time.sleep(0.2)

    def clear(self):
        self.m_sMode = "Manual"
        self.m_sPwd = ""
        self.m_sCountry = ""
        self.m_lSSIDs = ["[A:SCAN]"]
        self.m_sSSIDSel01 = "[Your SSID]"    # manual selected ssid
        self.m_sSSIDSel02 = self.m_lSSIDs[0] # scaned selected ssid

        p_sLine2 = 'ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev'
        p_sLine3 = 'update_config=1'
        touch_file(self.TMP_FILE)
        with open(self.TMP_FILE, 'w') as f:
            f.write(p_sLine2 + '\n')
            f.write(p_sLine3 + '\n')
        os.system('sudo cp %s %s > /dev/null 2>&1' %(self.TMP_FILE, self.WPA_FILE))
        os.system("sudo rm %s > /dev/null 2>&1" % self.TMP_FILE)
        p = subprocess.Popen('wpa_cli -i wlan0 reconfigure', stdout=subprocess.PIPE, shell=True)
        output, err = p.communicate()
        p.wait()

    def status(self):
        commandline = "iwgetid -r"
        output = commands.getoutput(commandline).strip()
        if output: return output
        return False

    def get_mode_list(self):
        return self.m_lModes

    def get_mode(self):
        return self.m_sMode

    def mode(self, p_sMode):
        self.m_sMode = p_sMode

    def ssid(self, p_sSSID):
        if self.m_sMode.lower() == "manual":
            self.m_sSSIDSel01 = p_sSSID
        elif self.m_sMode.lower() == "detect":
            self.m_sSSIDSel02 = p_sSSID

    def get_ssid(self):
        if self.m_sMode.lower() == "manual":
            return self.m_sSSIDSel01
        elif self.m_sMode.lower() == "detect":
            return self.m_sSSIDSel02

    def get_ssid_list(self):
        return self.m_lSSIDs

    def get_pwd(self):
        if len(self.m_sPwd) < 8: return ""
        return self.m_sPwd

    def pwd(self, p_sPWD):
        if len(p_sPWD) < 8: return False
        self.m_sPwd = p_sPWD
        return True

class change_watcher(object):
    m_iPrevLine = 0
    m_iMaxLines = 0

    m_lPrevIconList = []
    m_lPrevTextList = []
    m_lPrevValueList = []
    m_lCurIconList = []
    m_lCurTextList = []
    m_lCurValueList = []

    def __init__(self, p_lInitList, p_iInitLine):
        self._get_values(p_lInitList)
        self.m_lPrevIconList = self.m_lCurIconList[:]
        self.m_lPrevTextList = self.m_lCurTextList[:]
        self.m_lPrevValueList = self.m_lCurValueList[:]
        self.m_iPrevLine = p_iInitLine

    def check(self, p_lCurList, p_iCurLine, p_MaxLines):
        p_bCheck = False
        self.m_iMaxLines = p_MaxLines
        self._get_values(p_lCurList)

        # if there is a line change
        if self.m_iPrevLine != p_iCurLine:
            p_bCheck = True
        # if not same number of lines
        elif len(self.m_lPrevTextList) != len(self.m_lCurTextList):
            p_bCheck = True
        # if any icon, value, text change
        elif not self._comp_list(p_iCurLine):
            p_bCheck = True

        self.m_iPrevLine = p_iCurLine
        self.m_lPrevIconList = self.m_lCurIconList[:]
        self.m_lPrevTextList = self.m_lCurTextList[:]
        self.m_lPrevValueList = self.m_lCurValueList[:]
        return p_bCheck

    def _get_values(self, p_lList):
        self.m_lCurIconList = []
        self.m_lCurTextList = []
        self.m_lCurValueList = []
        for item in p_lList:
            try: self.m_lCurIconList.append(item['icon'])
            except: self.m_lCurIconList.append(None)
            try: self.m_lCurTextList.append(item['text'])
            except: self.m_lCurTextList.append(None)
            try: self.m_lCurValueList.append(item['value'])
            except: self.m_lCurValueList.append(None)

    def _comp_list(self, p_iCurLine):
        """
        Compare icons, values and texts from previous and current lists
        Return True if are equal, False if are different
        """
        for a, b in zip(self.m_lPrevValueList, self.m_lCurValueList):
            if a != b:
                # only set as a change if changed value is in the current page
                if self._is_same_page(self.m_lCurValueList.index(b), p_iCurLine):
                    return False

        for a, b in zip(self.m_lPrevTextList, self.m_lCurTextList):
            if a != b:
                # only set as a change if changed text is in the current page
                if self._is_same_page(self.m_lCurTextList.index(b), p_iCurLine):
                    return False

        for a, b in zip(self.m_lPrevIconList, self.m_lCurIconList):
            if a != b:
                # only set as a change if changed icon is in the current page
                if self._is_same_page(self.m_lCurIconList.index(b), p_iCurLine):
                    return False

        return True

    def _is_same_page(self, p_iChangedLine, p_iCurLine):
        p_iPageCur = int(math.ceil((p_iCurLine + 1) \
                          * 1.0 / self.m_iMaxLines * 1.0))
        p_iPagePos = int(math.ceil((p_iChangedLine + 1) \
                          * 1.0 / self.m_iMaxLines * 1.0))
        if p_iPageCur == p_iPagePos: return True
        return False

class sys_volume(object):
    m_iSysVol = 0
    m_lFreqs = ('00. 31 Hz', '01. 63 Hz', '02. 125 Hz',
                '03. 250 Hz', '04. 500 Hz', '05. 1 kHz',
                '06. 2 kHz', '07. 4 kHz', '08. 8 kHz',
                '09. 16 kHz')
    m_lPresets = {'flat': (66, 66, 66, 66, 66, 66, 66, 66, 66, 66),
                  'live': (66, 66, 66, 66, 70, 70, 70, 85, 80, 75),
                  'clean': (66, 66, 66, 70, 70, 70, 70, 85, 90, 85)}
    def __init__(self):
        self.get_vol()

    def preset(self, p_sPreset):
        if p_sPreset.lower() in self.m_lPresets:
            command = 'amixer -q -D equal sset'
            p_lValues = self.m_lPresets[p_sPreset.lower()]
            for i in range(0, 10):
                string = ' "' + str(self.m_lFreqs[i]) + '" '
                string += str(p_lValues[i]) + '%'
                string += " > /dev/null 2>&1"
                os.system(command + string)
            ini_set(CRT_UTILITY_FILE, "audio_presets", p_sPreset.lower())
            return p_sPreset

    def get_presets(self):
        p_lValues = []
        for preset in self.m_lPresets:
            p_lValues.append(preset)
        logging.info("presets %s" % p_lValues)
        return p_lValues

    def get_vol(self):
        line = commands.getoutput('amixer -M sget PCM | grep %')
        line = line.strip().replace('[', ''). replace(']', '')
        line = re.sub(r' +', " ", line)
        line = line.split(' ')
        for item in line:
            if '%' in item: self.m_iSysVol = int(item.replace('%', ''))
        #if self.m_iSysVol > 86: self.set_vol(86)
        return self.m_iSysVol

    def set_vol(self, p_iNewVol):
        vol = int(p_iNewVol)
        if vol <= 100:
            vol = str(vol) + '%'
            os.system('amixer -q -M sset PCM %s' % vol)
            return self.get_vol()

class external_storage(object):
    """ virtual class for USB Automount enable/disable/eject """
    m_sService = ""
    m_bSrvExist = False
    m_bSrvRun = False
    m_bUSBMounted = False
    m_sMountedPath = ""

    def _check_files(self):
        """ Check if needed service files exists """
        bCheck01 = os.path.exists(CRT_EXTSTRG_SRV_PATH)
        bCheck02 = os.path.exists(CRT_EXTSTRG_CORE_PATH)
        if bCheck01 and bCheck02:
            return True
        return False

    def check(self):
        self.m_bSrvExist = False
        self.m_bSrvRun = False
        sCommand = 'systemctl list-units --all | grep \"%s\"' % CRT_EXTSTRG_SRV_FILE
        sCheckService = commands.getoutput(sCommand)

        if CRT_EXTSTRG_SRV_FILE in sCheckService:
            self.m_bSrvExist = True
        if 'running' in sCheckService:
            self.m_bSrvRun = True
        return self.m_bSrvRun

    def init(self):
        if self._check_files and not self.check():
            os.system('sudo cp %s /etc/systemd/system/%s > /dev/null 2>&1' % \
                     (CRT_EXTSTRG_SRV_PATH, CRT_EXTSTRG_SRV_FILE))
            os.system('sudo chmod +x /etc/systemd/system/%s > /dev/null 2>&1' % \
                      CRT_EXTSTRG_SRV_FILE)
            os.system('sudo systemctl enable %s > /dev/null 2>&1' % \
                      CRT_EXTSTRG_SRV_FILE)
            os.system('sudo systemctl start %s > /dev/null 2>&1' % \
                      CRT_EXTSTRG_SRV_FILE)
            self.check()

    def stop(self):
        if self._check_files and self.check():
            os.system('sudo systemctl disable %s > /dev/null 2>&1' % \
                      CRT_EXTSTRG_SRV_FILE)
            os.system('sudo systemctl stop %s > /dev/null 2>&1' % \
                      CRT_EXTSTRG_SRV_FILE)
            os.system('sudo rm /etc/systemd/system/%s > /dev/null 2>&1' % \
                      CRT_EXTSTRG_SRV_FILE)
            os.system('sudo umount -l /home/pi/RetroPie/roms > /dev/null 2>&1')
            os.system('sudo umount -l /home/pi/RetroPie/BIOS > /dev/null 2>&1')
            os.system('sudo umount -l /opt/retropie/configs/all/emulationstation/gamelists > /dev/null 2>&1')
            self.__clean() # clean trigger files
            self.check()

    def check_connected(self):
        if os.path.exists(CRT_EXTSTRG_TRIG_MNT_PATH):
            try:
                with open(CRT_EXTSTRG_TRIG_MNT_PATH, "r+") as f:
                    new_file = f.readlines()
                    line = new_file[0].strip().split(' ')
                    disk = line[1]
                    dev = line[0]
                if os.path.exists(dev):
                    return disk
            except: pass
        return False

    def eject(self):
        disk = self.check_connected()
        if disk:
            command = "sudo umount "
            command += disk
            command += " > /dev/null 2>&1"
            os.system(command)
            logging.info(command)
            return True
        return False

    def __clean(self):
        if os.path.exists(CRT_EXTSTRG_TRIG_MNT_PATH):
            os.system("rm %s > /dev/null 2>&1" % \
                      CRT_EXTSTRG_TRIG_MNT_PATH)
        if os.path.exists(CRT_EXTSTRG_TRIG_UMNT_PATH):
            os.system("rm %s > /dev/null 2>&1" % \
                      CRT_EXTSTRG_TRIG_UMNT_PATH)

class background_music(object):
    """ virtual class for Background Music enable/disable """
    m_sService = ""
    m_bSrvExist = False
    m_bSrvRun = False
    m_bUSBMounted = False
    m_sMountedPath = ""

    def _check_files(self):
        """ Check if needed service files exists """
        bCheck01 = os.path.exists(CRT_BGM_SRV_PATH)
        bCheck02 = os.path.exists(CRT_BGM_CORE_PATH)
        if bCheck01 and bCheck02:
            return True
        return False

    def check(self):
        self.m_bSrvExist = False
        self.m_bSrvRun = False
        sCommand = 'systemctl list-units --all | grep \"%s\"' % CRT_BGM_SRV_FILE
        sCheckService = commands.getoutput(sCommand)

        if CRT_BGM_SRV_FILE in sCheckService:
            self.m_bSrvExist = True
        if 'running' in sCheckService:
            self.m_bSrvRun = True
        return self.m_bSrvRun

    def init(self):
        if self._check_files and not self.check():
            os.system('sudo cp %s /etc/systemd/system/%s > /dev/null 2>&1' % \
                     (CRT_BGM_SRV_PATH, CRT_BGM_SRV_FILE))
            os.system('sudo chmod +x /etc/systemd/system/%s > /dev/null 2>&1' % \
                      CRT_BGM_SRV_FILE)
            os.system('sudo systemctl enable %s > /dev/null 2>&1' % \
                      CRT_BGM_SRV_FILE)
            os.system('sudo systemctl start %s > /dev/null 2>&1' % \
                      CRT_BGM_SRV_FILE)
            self.check()

    def stop(self):
        if self._check_files and self.check():
            os.system('sudo systemctl disable %s > /dev/null 2>&1' % \
                      CRT_BGM_SRV_FILE)
            os.system('sudo systemctl stop %s > /dev/null 2>&1' % \
                      CRT_BGM_SRV_FILE)
            os.system('sudo rm /etc/systemd/system/%s > /dev/null 2>&1' % \
                      CRT_BGM_SRV_FILE)
            self.__clean() # clean trigger files
            self.check()

    def __clean(self):
        pass

class saveboot(object):
    """ virtual class save config.txt system resolution """
    m_dConfigFile = { "offsetX": "", "offsetY": "",
                      "width": "", "height": ""}
    m_lBootTimings = [] # To calculate system resolution on boot.txt

    m_lResizeRes = [] # To forwad diffs timings for pattern testing
    m_sEnv = ""

    BOOTCFG_TEMP_FILE = os.path.join(TMP_LAUNCHER_PATH, "config.txt")

    def __init__(self):
        pass

    def _prepare(self, p_dConfigFile = None):
        self._get_boot_timing()
        self._prepare_cfg()
        logging.info("INFO: taking custom parameters from utility.cfg")

        logging.info("INFO: OffsetX: %s, OffsetY: %s, Width: %s and Height: %s"%
        (self.m_dConfigFile["offsetX"],self.m_dConfigFile["offsetY"],
         self.m_dConfigFile["width"], self.m_dConfigFile["height"]))

    def _get_boot_timing(self):
        """ Take current system base timings from utility.cfg"""
        self.m_sEnv = ini_get(CRT_UTILITY_FILE, "default")
        self.m_lBootTimings = ini_getlist(CRT_UTILITY_FILE,
                                          "%s_timings" % self.m_sEnv)
        self.m_lBootTimings = map(int, self.m_lBootTimings)
        if not self._apply_fix_tv():
            logging.info("INFO: not fix tv to apply")
        logging.info("INFO: default system resolution: %s"%self.m_sEnv)

    def _apply_fix_tv(self):
        sSelected = ini_get(CRT_FIXMODES_FILE, "mode_default")
        if not sSelected or sSelected.lower() == "default":
            return False
        DiffTimings = ini_getlist(CRT_FIXMODES_FILE,
                                  "%s_%s"%(sSelected, self.m_sEnv))
        DiffTimings = map(int, DiffTimings)
        if len(DiffTimings) != 17: #If not 17 timings, not valid
            return False
        i = 0
        for timing in DiffTimings: #SUM TV Fix to main timings
            self.m_lBootTimings[i] += DiffTimings[i]
            i += 1
        logging.info("INFO: resolution + MODE: %s"%self.m_lBootTimings)
        return True

    def _prepare_cfg(self):
        """ Take config from utility.cfg """
        self.m_dConfigFile["offsetX"] = int(ini_get(CRT_UTILITY_FILE,
                                                    self.m_sEnv+"_offsetX"))
        self.m_dConfigFile["offsetY"] = int(ini_get(CRT_UTILITY_FILE,
                                                    self.m_sEnv+"_offsetY"))
        self.m_dConfigFile["width"] = int(ini_get(CRT_UTILITY_FILE,
                                                  self.m_sEnv+"_width"))
        self.m_dConfigFile["height"] = int(ini_get(CRT_UTILITY_FILE,
                                                   self.m_sEnv+"_height"))

    def save(self):
        """ Save on boot.txt system timings """
        self._prepare()
        if self._boot_timing_calculation():
            self._write_boot_timing()
        self.cleanup()

    def _boot_timing_calculation(self):
        #This function will check if a valid timing set result of applying
        #offsetX, offsetY, width and height for config.txt system file.
        #check01 must be identical to check03 and check02 to check04.
        #If calculation is OK will return True, if not False.
        #[H_Res] = self.m_lBootTimings[0]       [V_Res] = self.m_lBootTimings[5]
        #[H_BP]  = self.m_lBootTimings[4]       [V_BP]  = self.m_lBootTimings[9]
        #[H_FP]  = self.m_lBootTimings[2]       [V_FP]  = self.m_lBootTimings[7]

        #Calculation of check01 & check02 on utility.cfg timings + MODES
        check01 = self.m_lBootTimings[0] + self.m_lBootTimings[4] + \
                  self.m_lBootTimings[2]
        check02 = self.m_lBootTimings[5] + self.m_lBootTimings[9] + \
                  self.m_lBootTimings[7]

        #Apply width to timings
        if self.m_dConfigFile["width"] < 0:
            self.m_lBootTimings[0] -= abs(2*self.m_dConfigFile["width"])
            self.m_lBootTimings[4] += abs(self.m_dConfigFile["width"])
            self.m_lBootTimings[2] += abs(self.m_dConfigFile["width"])
        else:
            self.m_lBootTimings[0] += abs(2*self.m_dConfigFile["width"])
            self.m_lBootTimings[4] -= abs(self.m_dConfigFile["width"])
            self.m_lBootTimings[2] -= abs(self.m_dConfigFile["width"])

        #Apply height to timings
        if self.m_dConfigFile["height"] < 0:
            self.m_lBootTimings[5] -= abs(2*self.m_dConfigFile["height"])
            self.m_lBootTimings[9] += abs(self.m_dConfigFile["height"])
            self.m_lBootTimings[7] += abs(self.m_dConfigFile["height"])
        else:
            self.m_lBootTimings[5] += abs(2*self.m_dConfigFile["height"])
            self.m_lBootTimings[9] -= abs(self.m_dConfigFile["height"])
            self.m_lBootTimings[7] -= abs(self.m_dConfigFile["height"])

        #Apply offsetX to timings
        if self.m_dConfigFile["offsetX"] < 0:
            self.m_lBootTimings[4] -= abs(self.m_dConfigFile["offsetX"])
            self.m_lBootTimings[2] += abs(self.m_dConfigFile["offsetX"])
        else:
            self.m_lBootTimings[4] += abs(self.m_dConfigFile["offsetX"])
            self.m_lBootTimings[2] -= abs(self.m_dConfigFile["offsetX"])

        #Apply offsetY to timings
        if self.m_dConfigFile["offsetY"] < 0:
            self.m_lBootTimings[9] -= abs(self.m_dConfigFile["offsetY"])
            self.m_lBootTimings[7] += abs(self.m_dConfigFile["offsetY"])
        else:
            self.m_lBootTimings[9] += abs(self.m_dConfigFile["offsetY"])
            self.m_lBootTimings[7] -= abs(self.m_dConfigFile["offsetY"])

        #Calculation of check03 & check04 on utility.cfg timings + MODES + CENTERING
        check03 = self.m_lBootTimings[0] + self.m_lBootTimings[4] + \
                  self.m_lBootTimings[2]
        check04 = self.m_lBootTimings[5] + self.m_lBootTimings[9] + \
                  self.m_lBootTimings[7]

        if (check01 == check03) and (check02 == check04):
            logging.info("INFO: center and size applied correctly")
            return True
        else:
            logging.error("ERROR: can't apply center and \
                           size, check utility.cfg")
            return False

    def _write_boot_timing(self):
        p_sBootTimings = self.m_lBootTimings
        p_sBootTimings = map(str, p_sBootTimings)
        p_sBootTimings = " ".join(p_sBootTimings)
        logging.info("INFO: calculated resolution to add in config.txt: %s"% \
                     p_sBootTimings)

        os.system('cp %s %s' %(RASP_BOOTCFG_FILE, self.BOOTCFG_TEMP_FILE))
        modify_line(self.BOOTCFG_TEMP_FILE, "hdmi_timings=",
                    "hdmi_timings=%s" % p_sBootTimings)
        os.system('sudo cp %s %s' %(self.BOOTCFG_TEMP_FILE, RASP_BOOTCFG_FILE))
        logging.info("INFO: boot resolution saved at %s"%RASP_BOOTCFG_FILE)

    def apply(self):
        lValues = ' '.join(ini_getlist(RASP_BOOTCFG_FILE, 'hdmi_timings'))
        cmd = 'vcgencmd hdmi_timings '
        cmd += lValues
        cmd += " > /dev/null 2>&1"
        os.system(cmd)
        os.system('fbset -depth 8 && fbset -depth 32')
        RES_X = self.m_lBootTimings[0]
        REX_Y = self.m_lBootTimings[5]
        cmd = "fbset -xres %s -yres %s" % (RES_X, REX_Y)
        cmd += " -vxres %s -vyres %s" % (RES_X, REX_Y)
        os.system(cmd)

    # cleanup code
    def cleanup(self):
        self.__clean()

    # clean system
    def __clean(self):
        os.remove(self.BOOTCFG_TEMP_FILE)