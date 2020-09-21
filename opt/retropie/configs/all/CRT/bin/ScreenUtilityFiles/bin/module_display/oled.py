#!/usr/bin/python3
# -*- coding: utf-8 -*-


"""
I2C OLED Manager for piCRT addon

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

import os, sys, math, subprocess, time, re, threading, shlex
import logging, traceback
import smbus, socket, busio, rpyc
from rpyc.utils.server import ThreadedServer
from PIL import Image, ImageDraw, ImageFont
from board import D0, D1
from adafruit_ssd1306 import SSD1306_I2C

sys.dont_write_bytecode = True

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(SCRIPT_DIR + "/../"))
from main_paths import MODULES_PATH
sys.path.append(MODULES_PATH)

from launcher_module.core_paths import PNAME_OLED, TMP_LAUNCHER_PATH, \
                                       PNAME_LAUNCHER, CRT_UTILITY_FILE, \
                                       CRT_NETPLAY_FILE, RETROPIE_RUNCOMMAND_LOG, \
                                       CRT_OLED_FILE, CRT_OLED_PORT
from launcher_module.utils import check_process, set_procname
from launcher_module.file_helpers import md5_file, ini_get, ini_set, touch_file, \
                                         remove_line, add_line

__VERSION__ = '0.1'
__DEBUG__ = logging.INFO # logging.ERROR
CLEAN_LOG_ONSTART = True

LOG_PATH = os.path.join(TMP_LAUNCHER_PATH, "CRT_Display.log")
EXCEPTION_LOG = os.path.join(TMP_LAUNCHER_PATH, "backtrace.log")

FONT_PATH2 = "usr/share/fonts/truetype/dejavu"
FONT_PATH1 = "./assets/fonts"
FONT_TYPE1 = os.path.join(FONT_PATH1, "Ubuntu-BoldItalic.ttf")
FONT_TYPE2 = os.path.join(FONT_PATH2, "DejaVuSans.ttf")

class OLED_Display(object):
    m_oDisplay = None
    m_iDspWidth = 0
    m_iDspHeight = 0
    m_oOutput = None
    m_oDraw = None

    m_sHash_Prev = ""

    m_sGM_Game = ""
    m_sGM_System = ""
    m_iGM_StartTime = time.time()

    def __init__(self):
        self.__temp()
        self.__clean()
        self.m_lOLEDScrns = [{'scr_info_ingame': True, 'function': self.screen_ingame, 'time': 60},
                             {'scr_info_cpu': True, 'function': self.screen_cpu_use, 'time': 60},
                             {'scr_info_mem': True, 'function': self.screen_mem_use, 'time': 60},
                            ]
        logging.info("INFO: Initializating OLED Display service")
        self.prepare()
        self.loop()

    def prepare(self):
        set_procname(PNAME_OLED)
        if self.detect():
            i2c = busio.I2C(D1, D0) # Create the I2C interface.
            # Create the SSD1306 OLED class.
            # The first two parameters are the pixel width and pixel height.
            self.m_oDisplay = SSD1306_I2C(128, 64, i2c, addr=0x3C)
            # Create blank image for drawing.
            # Make sure to create image with mode '1' for 1-bit color.
            self.m_iDspWidth = self.m_oDisplay.width
            self.m_iDspHeight = self.m_oDisplay.height
            self.m_oOutput = Image.new("1", (self.m_iDspWidth, self.m_iDspHeight), color=0)
            self.m_oDraw = ImageDraw.Draw(self.m_oOutput)
            self.get_config()
            self.get_assets()
            self.clear_screen()
        else:
            sys.exit()

    def get_assets(self):
        self.m_oFont1 = ImageFont.truetype(FONT_TYPE1, 14)
        self.m_oFont2 = ImageFont.truetype(FONT_TYPE1, 13)
        self.m_oFont3 = ImageFont.truetype(FONT_TYPE1, 16)
        self.m_oFont4 = ImageFont.truetype(FONT_TYPE1, 20)
        
        self.m_oFont10 = ImageFont.truetype(FONT_TYPE2, 9)
        self.m_oFont11 = ImageFont.truetype(FONT_TYPE2, 10)
        self.m_oFont12 = ImageFont.truetype(FONT_TYPE2, 11)
        self.m_oFont13 = ImageFont.truetype(FONT_TYPE2, 13)
        self.m_oFont14 = ImageFont.truetype(FONT_TYPE2, 18)
        
        self.m_oImage1 = Image.open("./assets/bg/splash_crt.pbm").convert("1")
        self.m_oImage2 = Image.open("./assets/bg/info_ingame.pbm").convert("1")
        self.m_oImage3 = Image.open("./assets/bg/info_cpu.pbm").convert("1")
        self.m_oImage4 = Image.open("./assets/bg/info_mem.pbm").convert("1")
        self.m_oImage5 = Image.open("./assets/bg/gameinit.pbm").convert("1")
        self.m_oImage6 = Image.open("./assets/bg/gameover.pbm").convert("1")

    def get_config(self):
        if not os.path.exists(CRT_OLED_FILE): touch_file(CRT_OLED_FILE)
        p_sHash = md5_file(CRT_OLED_FILE)
        if p_sHash != self.m_sHash_Prev:
            for screen in self.m_lOLEDScrns:
                for item in screen:
                    if 'scr_' in item:
                        value = ini_get(CRT_OLED_FILE, item)
                        if value == False:
                            value = 0
                            remove_line(CRT_OLED_FILE, item)
                            add_line(CRT_OLED_FILE, "%s = 0" % item)
                        else: value = int(value)
                        if value > 0: 
                            screen[item] = True
                            screen['time'] = value * 60
                        elif value <= 0: 
                            screen[item] = False
                            screen['time'] = 0
            self.m_sHash_Prev = md5_file(CRT_OLED_FILE)

    def clear_screen(self):
        self.m_oDisplay.fill(0)
        self.m_oDisplay.show()

    def detect(self):
        """ OLED display detection in i2c bus 0, address 3C """
        p_bCheck = False
        try: bus = smbus.SMBus(0)
        except: 
            logging.info("WARNING: can't connect to i2c0")
            return p_bCheck
        p_lDevList = [60] # 0x3c display address; 
        for device in p_lDevList:
            try:
                bus.read_byte(device)
                p_bCheck = True
            except:
                pass
        bus.close()
        bus = None
        if not p_bCheck: logging.info("WARNING: OLED display NOT found")
        else: logging.info("INFO: OLED display found")
        return p_bCheck

    def loop(self):
        global STOP_SCREEN
        global INFO_IMG
        p_bPrevScrMain = False
        while not STOP_SERVICE:
            self.get_config()
            if not p_bPrevScrMain and not INFO_IMG:
                self.clear_screen()
                self.screen_splash_image(self.m_oImage1, 2)
                p_bPrevScrMain = True
            if INFO_IMG:
                if INFO_IMG == "game_over": self.screen_splash_image(self.m_oImage6, 2)
                if INFO_IMG == "game_init": self.screen_splash_image(self.m_oImage5, 2)
                INFO_IMG = None
                p_bPrevScrMain = False
            for screen in self.m_lOLEDScrns:
                for item in screen:
                    if 'scr_' in item and screen[item]:
                        if not STOP_SCREEN and not STOP_SERVICE:
                            logging.info("INFO: show %s screen" % item)
                            try:
                                if screen['function'](screen['time']): p_bPrevScrMain = False 
                            except Exception as e:
                                logging.info("ERROR: %s" % e)
                                self.clear_screen()
            STOP_SCREEN = False
        time.sleep(1)
        self.clear_screen()

    def draw(self):
        self.m_oDisplay.image(self.m_oOutput)
        self.m_oDisplay.show()

    def screen_splash_image(self, p_sImage, p_iTime = 3):
        p_iStart = time.time()
        self.m_oOutput.paste(p_sImage, (0, 0))
        self.draw()
        while not STOP_SCREEN and not STOP_SERVICE:
            time.sleep(0.5)
            if time.time() - p_iStart >= p_iTime: break

    def get_ip_address(self, p_sIFname):
        if p_sIFname == "public":
            addr = os.popen('wget -qO- http://ipecho.net/plain --timeout=0.8 --tries=1 ; echo').readlines(-1)[0].strip()
            if addr: return addr
            else: return None
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            addr = socket.inet_ntoa(fcntl.ioctl(s.fileno(),
                   0x8915, # SIOCGIFADDR
                   struct.pack('256s', p_sIFname[:15].encode('utf-8')))[20:24])
        except: return None

    def ingame_get_info(self):
        self.m_sNetplay = "NETPLAY: DISABLED"
        self.m_sPublic = "LOCAL PLAYING"
        self.m_sRate = ""
        p_iTime = 0
        """ Get Retroarch Netplay info if launched by CRT scripts """
        p_bNetplay = ini_get(CRT_UTILITY_FILE, "netplay")
        p_sNetMode = ini_get(CRT_NETPLAY_FILE, "__netplaymode")
        p_sNetRemo = ini_get(CRT_NETPLAY_FILE, "__netplayhostip")
        p_sNetPort = ini_get(CRT_NETPLAY_FILE, "__netplayport")
        if p_bNetplay and p_bNetplay.lower() == "true": p_bNetplay = True
        else: p_bNetplay = None

        while not STOP_SCREEN and not STOP_SERVICE:
            if p_iTime == 0 or time.time() - p_iTime >= 5:
                """ Get Retroarch Netplay info if launched by runcommand """
                if p_bNetplay == None:
                    if os.path.exists(RETROPIE_RUNCOMMAND_LOG):
                        with open(RETROPIE_RUNCOMMAND_LOG, "r") as f:
                            for line in f:
                                if "-H" in line or "-C" in line:
                                    p_bNetplay = True
                """ Get current resolution """
                cmd = "vcgencmd hdmi_timings"
                p_sOutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
                p_lTimings = p_sOutput.strip().split("=")[1].split(' ')
                self.m_sTimings = p_lTimings[0] + "x" + p_lTimings[5] + "@" + p_lTimings[13] + "hz"
                text_width = self.m_oDraw.textsize(self.m_sTimings, font=self.m_oFont10)[0]
                self.m_iTimingPosX = 81 - int(text_width / 2)
                """ Get if NTSC or PAL and its screen position """
                if int(p_lTimings[0]) == 320 and int(p_lTimings[5]) == 240: self.m_sRate = "240p"
                elif int(p_lTimings[5]) <= 240: self.m_sRate = "NTSC"
                elif int(p_lTimings[5]) > 240: self.m_sRate = "PAL"
                text_width = self.m_oDraw.textsize(self.m_sRate, font=self.m_oFont10)[0]
                self.m_iRatePosX = 15 - int(text_width / 2)            
                """ Get IP and connection for Netplay"""
                if p_bNetplay:
                    if p_sNetMode == "C" or  p_sNetMode == "c":
                        self.m_sNetplay = "NETPLAY: CLIENT MODE"
                        self.m_sPublic = chr(8594) + " " + p_sNetRemo + ":" + p_sNetPort
                    elif p_sNetMode == "H" or  p_sNetMode == "h":
                        p_sIP = self.get_ip_address("public")
                        if not p_sIP: p_sIP = self.get_ip_address("eth0")
                        if not p_sIP: p_sIP = self.get_ip_address("wlan0")
                        if not p_sIP: p_sIP = "NOT CONNECTED"
                        self.m_sNetplay = "NETPLAY: HOST MODE"
                        if p_sIP == "NOT CONNECTED": self.m_sPublic = "NO NETWORK AVAILABLE"
                        else: self.m_sPublic = p_sIP + ":" + p_sNetPort + " " + chr(8592)
                p_iTime = time.time()
            time.sleep(0.3)
        return

    def screen_ingame(self, p_iShow = 30, p_iInfoUpdate = 1):
        if not check_process(PNAME_LAUNCHER): return False
        """ Start screen refresh daemon for system & title """
        t = threading.Thread(target=self.ingame_get_info)
        t.setDaemon(True)
        t.start()

        global STOP_SCREEN
        global INFO_IMG
        X_POS = 0
        Y_POS = 0
        p_sTitle = self.m_sGM_Game
        p_iTime = time.time()
        p_iInfoGlobal = 0
        p_iInfoSGTime = 0
        p_iInfoNetTime = 0

        p_iRefreshTime = 0.2
        p_iTitleOversize = 0
        p_iTitleMove = 0
        p_iScroll = 0
        p_iScrollWait = 3
        p_iScrollWaitCtrl = time.time()
        p_sPrev_Title = None

        time.sleep(0.3)
        while not STOP_SCREEN and not STOP_SERVICE:
            if not check_process(PNAME_LAUNCHER): 
                break
            """ Get gaming time """
            p_iGameTime = time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time() - self.m_iGM_StartTime))
            """ Switch system and game file names """
            if p_iInfoSGTime == 0 or time.time() - p_iInfoSGTime >= 30: # 30 seconds per info line
                p_iInfoSGTime = time.time()
                if p_sTitle == self.m_sGM_System:
                    p_sTitle = self.m_sGM_Game
                else: p_sTitle = self.m_sGM_System
            """ Switch Netplay info """
            if p_iInfoNetTime == 0 or time.time() - p_iInfoNetTime >= 3: # 3 seconds per info line
                try: p_sNet 
                except: p_sNet = self.m_sPublic
                p_iInfoNetTime = time.time()
                if p_sNet == self.m_sNetplay:
                    p_sNet = self.m_sPublic
                else: p_sNet = self.m_sNetplay
                p_iTextWidth = self.m_oDraw.textsize(p_sNet, font=self.m_oFont10)[0]
                p_iNetInfoPosX = int(self.m_iDspWidth / 2) - int(p_iTextWidth / 2)
            """ Title scroll """
            if p_sTitle != p_sPrev_Title:
                p_sPrev_Title = p_sTitle
                p_iTextWidth = self.m_oDraw.textsize(p_sPrev_Title, font=self.m_oFont2)[0]
                p_iTitleOversize = p_iTextWidth - self.m_iDspWidth # oversize
                p_iTitleOversize += 5
                p_iTitleMove = 0
                if p_iTitleOversize >= 0: 
                    p_iScroll = -5
                    p_iTitleOversize = abs(p_iTitleOversize)
                else:
                    p_iScroll = 0
                    p_iTitleOversize = 0
                    p_iSysGamePosX = int(self.m_iDspWidth / 2) - int(p_iTextWidth / 2) - 2
            
            if p_iScroll != 0:
                if p_iTitleMove == 0 or abs(p_iTitleMove) == abs(p_iTitleOversize):
                    if time.time() - p_iScrollWaitCtrl > p_iScrollWait:
                        p_iTitleMove += p_iScroll
                else:
                    if p_iTitleMove + p_iScroll >= -p_iTitleOversize and p_iTitleMove + p_iScroll <= 0:
                        p_iTitleMove += p_iScroll
                    elif p_iTitleMove + p_iScroll <= -p_iTitleOversize:
                        p_iTitleMove = -p_iTitleOversize
                    elif p_iTitleMove + p_iScroll > 0:
                        p_iTitleMove = 0
                    if abs(p_iTitleMove) == abs(p_iTitleOversize) or p_iTitleMove == 0:
                        p_iScroll = -p_iScroll
                        p_iScrollWaitCtrl = time.time()

            """ Draw info elements on screen """
            if time.time() - p_iInfoGlobal > 3:
                p_iInfoGlobal = time.time()
                self.m_oOutput.paste(self.m_oImage2, (0, 0))
                self.m_oDraw.text((X_POS + 49, Y_POS + 28), "PLAYING TIME:", 
                                   font=self.m_oFont10, fill=255)
                self.m_oDraw.text((X_POS + self.m_iTimingPosX, Y_POS -1), self.m_sTimings, 
                                   font=self.m_oFont10, fill=1)
                self.m_oDraw.text((X_POS + self.m_iRatePosX, Y_POS -1), self.m_sRate, 
                                   font=self.m_oFont10, fill=1)
                self.m_oDraw.text((X_POS + p_iNetInfoPosX, Y_POS + 54), p_sNet, 
                                   font=self.m_oFont10, fill=1)
                if p_iScroll == 0:
                    self.m_oDraw.rectangle((0, 12, 128, 29), outline=0, fill=0)
                    self.m_oDraw.text((p_iSysGamePosX, 12), p_sPrev_Title, 
                                       font=self.m_oFont2, fill=1)
            if p_iScroll != 0:
                self.m_oDraw.rectangle((0, 12, 128, 29), outline=0, fill=0)
                self.m_oDraw.text((p_iTitleMove, 12), p_sPrev_Title, 
                                   font=self.m_oFont2, fill=1)
            self.m_oDraw.rectangle((58, 41, 128, 48), outline=0, fill=0)
            self.m_oDraw.text((X_POS + 60, Y_POS + 39), p_iGameTime, 
                               font=self.m_oFont10, fill=1)
            self.draw()
            time.sleep(p_iRefreshTime)
            if time.time() - p_iTime >= p_iShow: break
        if not STOP_SCREEN:
            STOP_SCREEN = True
            t.join()
            STOP_SCREEN = False
        else:
            t.join()
        return True

    def screen_cpu_use(self, p_iShow = 30, p_iInfoUpdate = 0.3):
        X_POS = 0
        Y_POS = 0
        p_iAngleMax = 155
        p_iAngleStr = 135
        p_iAngle = p_iAngleMax / 100
        p_iTime = time.time()

        while not STOP_SCREEN and not STOP_SERVICE:
            """ Get CPU current usage """
            p_sCMD = "top -bn1 | awk '/Cpu\(s\):/ {print 100-$8}'"
            p_sCPU = subprocess.check_output(p_sCMD, shell=True).decode("utf-8")
            p_fCPU = float(p_sCPU.strip())
            """ Get CPU Temperature """
            p_sCMD = "vcgencmd measure_temp"
            p_sCPUTemp = subprocess.check_output(p_sCMD, shell=True).decode("utf-8")
            p_sCPUTemp = p_sCPUTemp.strip().split("=")[1]
            p_sCPUTemp = p_sCPUTemp.replace("'", "\xb0")
            """ Get CPU clock speed """
            p_sCMD = "vcgencmd measure_clock arm"
            p_sCPUSpeed = subprocess.check_output(p_sCMD, shell=True).decode("utf-8")
            p_sCPUSpeed = p_sCPUSpeed.strip().split("=")[1]
            p_iCPUSpeed = int(int(p_sCPUSpeed) / 1000000.0)
            p_sCPUSpeed = str(p_iCPUSpeed) + "Mhz"
            """ Get CPU governor """
            p_sCMD = "cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"
            p_sCPUGob = subprocess.check_output(p_sCMD, shell=True).decode("utf-8")
            p_sCPUGob = p_sCPUGob.strip()[:3].upper()
            """ Get CPU core voltage """
            p_sCMD = "vcgencmd measure_volts core"
            p_sCPUVolt = subprocess.check_output(p_sCMD, shell=True).decode("utf-8")
            p_sCPUVolt = p_sCPUVolt.strip().split("=")[1]
            
            self.m_oOutput.paste(self.m_oImage3, (0, 0))
            
            """ Draw total scale for CPU usage graphics """
            for i in range(0, 108, 8):
                scale = i * 0.01
                self.m_oDraw.pieslice((X_POS + 0, Y_POS + 0, X_POS + 74, Y_POS + 74), 
                                       start=p_iAngleStr + (p_iAngleMax * scale), 
                                       end=p_iAngleStr + (p_iAngleMax * scale), 
                                       outline=1, fill=0, width=1)
            
            """ Hide part of scale for CPU usage graphics to get points """
            self.m_oDraw.pieslice((X_POS + 1, Y_POS + 1, X_POS + 73, Y_POS + 73), 
                                   start=p_iAngleStr - 5, end=p_iAngleStr + p_iAngleMax + 25, 
                                   outline=1, fill=0, width=0)

            """ Dynamic CPU usage arc from 0% to current utilization """
            self.m_oDraw.arc((X_POS + 0, Y_POS + 0, X_POS + 74, Y_POS + 74), 
                              start=p_iAngleStr, end=p_iAngleStr + (p_iAngle * p_fCPU), 
                              fill=1, width=12)

            """ Pointer line for current CPU usage at end of arc """
            self.m_oDraw.pieslice((X_POS + 0, Y_POS + 0, X_POS + 74, Y_POS + 74), 
                                   start=p_iAngleStr + (p_iAngle * p_fCPU) + 5, 
                                   end=p_iAngleStr + (p_iAngle * p_fCPU) + 5, 
                                   outline=1, fill=0, width=1)

            """ Hide part of pointer line for current CPU usage """
            self.m_oDraw.pieslice((X_POS + 14, Y_POS + 14, X_POS + 60, Y_POS + 60), 
                                   start=p_iAngleStr - 5, end=p_iAngleStr + p_iAngleMax + 5, 
                                   outline=1, fill=0, width=0)

            if p_fCPU > 99: p_fCPU = 99 # max percetange shown is 99%
            self.m_oDraw.text((X_POS + 19, Y_POS + 21), "USAGE", 
                               font=self.m_oFont11, fill=255)
            self.m_oDraw.text((X_POS + 18, Y_POS + 29), str(int(p_fCPU)).zfill(2) + "%", 
                               font=self.m_oFont14, fill=255)
            self.m_oDraw.text((X_POS + 65, Y_POS + 43), p_sCPUTemp, 
                               font=self.m_oFont4, fill=255)
            self.m_oDraw.text((X_POS + 65, Y_POS + 17), p_sCPUVolt, 
                               font=self.m_oFont12, fill=255)
            self.m_oDraw.text((X_POS + 65, Y_POS + 30), p_sCPUSpeed, 
                               font=self.m_oFont12, fill=255)
            self.m_oDraw.text((X_POS + 29, Y_POS + 54), p_sCPUGob, 
                               font=self.m_oFont11, fill=255)

            self.draw()
            time.sleep(p_iInfoUpdate)
            if time.time() - p_iTime >= p_iShow: break
        return True

    def screen_mem_use(self, p_iShow = 30, p_iInfoUpdate = 0.3):
        X_POS = 0
        Y_POS = 0
        p_iBarMax = 68
        p_lArrow = [[1, 1, 1, 1], [0, 2, 2, 2],
                    [-1, 3, 3, 3], [-2, 4, 4, 4],
                    [-3, 5, 5, 5]]
        p_iTime = time.time()

        while not STOP_SCREEN and not STOP_SERVICE:
            """ Get total available RAM """
            p_sCMD = "free -m | awk 'NR==2{printf \"%s %s\", $3,$2}'"
            p_sMemory = subprocess.check_output(p_sCMD, shell=True).decode("utf-8")
            p_sMemAvail = p_sMemory.strip().split(' ')[1].zfill(3)
            p_sMemUsed = p_sMemory.strip().split(' ')[0].zfill(3)
            """ Get GPU dedicated RAM memory """
            p_sCMD = "vcgencmd get_mem gpu"
            p_sMemGPU = subprocess.check_output(p_sCMD, shell=True).decode("utf-8")
            p_sMemGPU = p_sMemGPU.strip().split("=")[1].replace('M', '').zfill(3)
            p_sMemGPU = "GPU MEM: " + p_sMemGPU + "MB"
            """ Get free RAM out of available """
            p_sMemFreePerc = int(((int(p_sMemAvail) - int(p_sMemUsed)) * 100) / (int(p_sMemAvail)))
            p_sMemFreePerc = str(p_sMemFreePerc) + "%"
            """ Calculate percentage of used RAM of available for bar """
            p_sMemUsedBar = int((int(p_sMemUsed) * p_iBarMax) / int(p_sMemAvail))
            """ Get RAM core voltage """
            p_sCMD = "vcgencmd measure_volts sdram_c"
            VOLT = subprocess.check_output(p_sCMD, shell=True).decode("utf-8")
            VOLT = VOLT.strip().split("=")[1]
            
            self.m_oOutput.paste(self.m_oImage4, (0, 0))
            self.m_oDraw.text((X_POS + 14, Y_POS + 2), VOLT, font=self.m_oFont10, fill=255)
            self.m_oDraw.text((X_POS + 0, Y_POS + 15), p_sMemUsed, font=self.m_oFont1, fill=255)
            self.m_oDraw.text((X_POS + 0, Y_POS + 30), "MB", font=self.m_oFont10, fill=255)
            self.m_oDraw.text((X_POS + 0, Y_POS + 40), "USED", font=self.m_oFont10, fill=255)
            self.m_oDraw.text((X_POS + 103, Y_POS + 15), p_sMemAvail, font=self.m_oFont1, fill=255)
            self.m_oDraw.text((X_POS + 112, Y_POS + 30), "MB", font=self.m_oFont10, fill=255)
            self.m_oDraw.text((X_POS + 103, Y_POS + 40), "FREE", font=self.m_oFont10, fill=255)
            self.m_oDraw.text((X_POS + 2, Y_POS + 54), p_sMemGPU, font=self.m_oFont10, fill=255)
            self.m_oDraw.text((X_POS + 93, Y_POS + 49), p_sMemFreePerc, font=self.m_oFont3, fill=255)
            self.m_oDraw.rectangle((30, 22, 30 + p_sMemUsedBar, 34), outline=0, fill=1) # clean info

            """ Draw used memory bar pointer """
            for line in p_lArrow:
                X_ARROW = 29 + p_sMemUsedBar
                Y_ARROW = 41
                self.m_oDraw.line((X_ARROW + line[0], Y_ARROW + line[1],
                                   X_ARROW + line[2], Y_ARROW + line[3]),
                                   fill=1)
            self.draw()
            time.sleep(p_iInfoUpdate)
            if time.time() - p_iTime >= p_iShow: break
        return True

    def __clean(self):
        pass

    def __temp(self):
        if CLEAN_LOG_ONSTART:
            if os.path.exists (LOG_PATH):
                os.system('rm %s' % LOG_PATH)
        logging.basicConfig(filename=LOG_PATH, level=__DEBUG__,
        format='[%(asctime)s] %(levelname)s - %(filename)s:%(funcName)s - %(message)s')


class OLEDService(rpyc.Service):
    def on_connect(self, conn):
        pass

    def on_disconnect(self, conn):
        pass

    def exposed_game_mode(self, p_sGame, p_sSystem, p_iStartTime, p_sInfo = None):
        global STOP_SCREEN
        global INFO_IMG
        SYSTEMSDB =    {
                        "amiga": "AMIGA", "amstradcpc": "Amstrad CPC", "arcade": "ARCADE",
                        "atari800": "Atari 800", "atari2600": "Atari 2600",
                        "atari7800": "Atari 7800", "atarilynx": "Atari Lynx",
                        "atarist": "Atari ST", "c64": "Commodore 64", "coleco": "ColecoVision",
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
                        "wonderswan": "WonderSwan", "wonderswancolor": "WonderSwan Color",
                        "zx81": "Sinclair ZX81", "zxspectrum": "ZX Espectrum",
                       }
        p_sSystem = p_sSystem.title()
        if p_sSystem.lower() in SYSTEMSDB:
            p_sSystem = SYSTEMSDB[p_sSystem.lower()]
        oLaunch.m_sGM_Game = p_sGame
        oLaunch.m_sGM_System = p_sSystem
        oLaunch.m_iGM_StartTime = p_iStartTime
        INFO_IMG = p_sInfo
        STOP_SCREEN = True
        
    def exposed_game_mode_off(self, p_sInfo = None):
        global STOP_SCREEN
        global INFO_IMG
        STOP_SCREEN = True
        INFO_IMG = "game_over"

    def exposed_status(self):
        return True
        
    def exposed_quit(self):
        global STOP_SERVICE
        STOP_SERVICE = True

if __name__ == '__main__':
    STOP_SCREEN = False
    STOP_SERVICE = False
    INFO_IMG = None
    try:
        oLaunch = OLED_Display
        server = ThreadedServer(OLEDService, port = CRT_OLED_PORT)
        t = threading.Thread(target = server.start)
        t.daemon = True
        t.start()
        oLaunch()
    except Exception as e:
        with open(EXCEPTION_LOG, 'a') as f:
            f.write(str(e))
            f.write(traceback.format_exc())