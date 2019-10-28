#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
launcher videoplayer.py.

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

import os, re, sys, logging, commands, glob, subprocess
from launcher_module.utils import splash_info
from launcher_module.core_choices_dynamic import choices
from launcher_module.core import launcher, CRTROOT_PATH, RETROPIEEMU_PATH, RETROPIECFG_PATH, CFG_TIMINGS_FILE
from launcher_module.screen import CRT

OMXPLAYER_FONT = '--font="/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_videoplayer/Ubuntu_MOD_WIDE.ttf'
OMXPLAYER_COMMAND = 'omxplayer -b --align center --layer 10000 --font-size 72 %s" \"%s\" > /dev/null 2>&1' % (OMXPLAYER_FONT, "%s")
JOY2KEY_DEV = "none"
JOY2KEY_PATH = "/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_videoplayer/joy2key.py"
JOY2KEY_VAR = commands.getoutput('$__joy2key_dev')

class videoplayer(launcher):
    m_sSystemCfg = ""
    m_sSystemCfgPath = ""
    m_sVideoPath = ""
    m_sMultipleVideos = False
    m_nVideoPosition = 0
    m_nVideoFoundNumber = 0
    m_lVideoEXT = ['avi', 'mkv', 'mp4', 'mpg', 'AVI', 'MKV', 'MP4', 'MPG']
    m_lVideoList = []

    @staticmethod
    def get_system_list():
        return ["videoplayer"]

    def pre_configure(self):
        if not os.path.isfile(JOY2KEY_PATH):
            logging.info("closing videoplayer: can't find file: %s" % JOY2KEY_PATH)
            self.panic("can't find joy2key", "try again!")
    # system configure vars
    def configure(self):
        if self.m_sSystem == "videoplayer":
            self.m_sSystemFreq = "videoplayer50"

     # just called if need rebuild the CMD
    def prepare(self):
        #if more than one video and selected is not the last
        if self.find_videos() and (self.m_nVideoFoundNumber != self.m_nVideoPosition):
            self.m_sMultipleVideos = self.video_options()

    def runcommand_start(self):
        """ launch_videoplayer!"""
        commandline = OMXPLAYER_COMMAND % self.m_lVideoList[self.m_nVideoPosition]
        
        logging.info("Launching Joy2Key")  
        self.launch_joy2key('kcub1', 'kcuf1', 'kcuu1', 'kcud1', '0x20', '0x71', '0x6b', '0x6a', '0x6d', '0x6e')
        logging.info("Playing video: %s", self.m_lVideoList[self.m_nVideoPosition])        
        self.m_oRunProcess = subprocess.Popen(commandline, shell=True)
        logging.info("Subprocess running: %s", commandline)

    def screen_set(self):
        self.m_oCRT = CRT(self.m_sSystemFreq)
        self.m_oCRT.screen_calculated(CFG_TIMINGS_FILE)
        try:
            splash_info("black") # clean screen
        except Exception as e:
            logging.error("splash failed: %s" % e)

    def wait(self):
        logging.info("wait omxplayer to finish")
        while True:
            poll = self.m_oRunProcess.poll()
            if poll != None:
                returncoded = self.m_oRunProcess.returncode
                if returncoded == 3:
                    break
                else:
                    if self.m_sMultipleVideos == "True":
                        self.m_nVideoPosition += 1
                        try:
                            self.m_lVideoList[self.m_nVideoPosition]
                            logging.info("Playing video: %s", self.m_lVideoList[self.m_nVideoPosition])
                            commandline = OMXPLAYER_COMMAND % self.m_lVideoList[self.m_nVideoPosition]
                            self.m_oRunProcess = subprocess.Popen(commandline, shell=True)
                            logging.info("Subprocess running: %s", commandline)
                        except:
                            break
                    else:
                        break
        logging.info("process end")
        
    def cleanup(self):
        #os.system('echo %s >> /tmp/proces' % returncoded)
        os.system('sudo killall joy2key.py')
        self.m_oCRT.screen_restore()
        logging.info("ES mode recover")
        os.system('clear')
        sys.exit()

    def launch_joy2key(self, left, right, up, down, a, b, x, y, start, select):
        # get the first joystick device (if not already set)
        if os.path.exists (JOY2KEY_VAR):
            JOY2KEY_DEV = JOY2KEY_VAR
        else:
            JOY2KEY_DEV = "/dev/input/jsX"
        output = commands.getoutput('ps -A')
        if os.path.exists (JOY2KEY_PATH) and JOY2KEY_DEV != "none" and not 'joy2key.py' in output:
            joy2key_command = "\"%s\" \"%s\" %s %s %s %s %s %s %s %s %s %s" % (JOY2KEY_PATH,JOY2KEY_DEV,left, right,up,down,a,b,x,y,start,select)
            process = subprocess.Popen(joy2key_command, shell=True)
            return process

    def find_videos(self):
        self.m_sFileDir
        for extension in self.m_lVideoEXT:
            self.m_lVideoList = self.m_lVideoList + glob.glob(("%s/*.%s")%(self.m_sFileDir,extension))
        self.m_lVideoList = sorted(self.m_lVideoList)
        
        counter = 0
        for video in self.m_lVideoList:
            if video == self.m_sFilePath:
                self.m_nVideoPosition = counter
            counter += 1
        self.m_nVideoFoundNumber = counter-1
        logging.info("Detected %s videos in the same folder", counter)
        if self.m_nVideoFoundNumber > 1:
            return True
        else:
            return False

    def video_options(self):
        ch = choices()
        ch.set_title("MULTIPLE VIDEOS FOUND")
        ch.load_choices([
                ("Play only this video.", "False"),
                ("Play ALL from this!", "True"),
            ])
        result = ch.run()
        return result

        