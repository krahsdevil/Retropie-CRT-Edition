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
import socket, fcntl, struct
import pygame

sys.dont_write_bytecode = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(SCRIPT_DIR + "/../"))
from main_paths import MODULES_PATH
sys.path.append(MODULES_PATH)

from launcher_module.screen import CRT
from launcher_module.core_paths import *
from launcher_module.utils import get_side, check_process
from launcher_module.file_helpers import ini_get, ini_getlist, modify_line, \
                                         ini_set
from launcher_module.core_controls import joystick, CRT_UP, CRT_DOWN, \
                                          CRT_LEFT, CRT_RIGHT, CRT_OK, \
                                          CRT_CANCEL

SYSTEMSDB =    {"amiga": "AMIGA",
                "amstradcpc": "AMSTRAD CPC",
                "arcade": "ARCADE",
                "atari800": "ATARI 800",
                "atari2600": "ATARI 2600",
                "atari7800": "ATARI 7800",
                "atarilynx": "ATARI Lynx",
                "atarist": "ATARI ST",
                "c64": "COMMODORE 64",
                "coleco": "ColecoVision",
                "daphne": "Daphne",
                "fba": "FinalBurn Neo",
                "fds": "Nintendo FDS",
                "gamegear": "SEGA GameGear",
                "gb": "Gameboy",
                "gba": "Gameboy Advance",
                "gbc": "Gameboy Color",
                "mame-advmame": "Advance MAME",
                "mame-libretro": "MAME",
                "mastersystem": "Master System",
                "megadrive": "Megadrive",
                "msx": "MSX",
                "n64": "Nintendo 64",
                "neogeo": "NEOGEO",
                "neogeocd": "NEOGEO CD",
                "nes": "NES",
                "ngp": "NEOGEO Pocket",
                "ngpc": "NEOGEO Pocket C.",
                "pcengine": "PC Engine",
                "pcenginecd": "PC Engine CD",
                "psx": "Play Station",
                "sega32x": "SEGA 32X",
                "segacd": "SEGA CD",
                "sg-1000": "SEGA SG-1000",
                "snes": "Super Nintendo",
                "vectrex": "Vectrex",
                "videopac": "Videopac",
                "wonderswan": "WonderSwan",
                "wonderswancolor": "WonderSwan C.",
                "zx81": "SINCLAIR ZX81",
                "zxspectrum": "ZX Expectrum",
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
    except: addr = "Getting IP"
    command = "sudo ethtool %s | grep \"Link detected\"" % p_sIFname
    output = commands.getoutput(command).strip()
    if not output or "no" in output.lower(): addr = "Disconnected"
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

class watcher(object):
    p_lList1 = []
    p_lList2 = []
    p_iLine1 = 0
    p_iMaxLines = 0
    
    def __init__(self, p_VarList, p_VarLine, p_MaxLines):
        self.p_lList1 = self._get_values(p_VarList)
        self.p_iLine1 = p_VarLine
        self.p_iMaxLines = p_MaxLines

    def check(self, p_VarList, p_VarLine):
        p_bCheck01 = True
        p_bCheck02 = True
        self.p_lList2 = self._get_values(p_VarList)
        if len(self.p_lList1) != len(self.p_lList2):
            self.p_lList1 = self._get_values(p_VarList)
            return True

        for a, b in zip(self.p_lList1, self.p_lList2):
            if a != b:
                if self._is_same_page(self.p_lList1.index(a), self.p_iLine1):
                    p_bCheck01 = False
                self.p_lList1 = self._get_values(p_VarList)
                break

        if p_VarLine != self.p_iLine1:
                self.p_iLine1 = p_VarLine
                p_bCheck02 = False
        if p_bCheck01 and p_bCheck02: return False
        return True
        
    def _get_values(self, p_VarList):
        val = []
        for value in p_VarList:
            try:
                val.append(value['value'])
            except:
                val.append(None)
        return val
        
    def _is_same_page(self, p_iPos, p_iCurLine):
        p_iPageCur = int(math.ceil((p_iCurLine + 1) \
                          * 1.0 / self.p_iMaxLines * 1.0))
        p_iPagePos = int(math.ceil((p_iPos + 1) \
                          * 1.0 / self.p_iMaxLines * 1.0))
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