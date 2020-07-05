#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
videoplayer.py

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

import os, sys, logging, commands, subprocess
import time, re, glob
from launcher_module.utils import menu_options, wait_process
from launcher_module.core import launcher
from launcher_module.core_paths import *

CRTASSETS_VIDEO_PATH = os.path.join(CRT_ASST_PATH, "screen_videoplayer")
JOY2KEY_NAME = "joy2key.py"
JOY2KEY_FILE = os.path.join(CRTASSETS_VIDEO_PATH, JOY2KEY_NAME)
FONT_FILE = os.path.join(CRT_FONTS_PATH, "UbuntuWIDE.ttf")

class videoplayer(launcher):
    m_nVideoPOS = 0
    m_nVideoNUM = 0
    m_lVideoEXT = ['avi', 'mkv', 'mp4', 'mpg', 'AVI', 'MKV', 'MP4', 'MPG']
    m_lVideoLST = []

    m_sPlayAll = "False"

    m_sTitVideo = "VIDEO PLAYER"
    m_lOptVideo = [("PLAY VIDEO", "False"),
                   ("PLAY ALL FROM THIS", "True")]

    """ OMX Player command string """
    m_sOMXPart01 = 'omxplayer -b --align center --layer 10000 '
    m_sOMXPart02 = '--font-size 72 --font="%s" ' % (FONT_FILE)
    m_sOMXPart03 = '"%s" > /dev/null 2>&1' % ("%s")
    m_sOMXPCommand = m_sOMXPart01 + m_sOMXPart02 + m_sOMXPart03

    @staticmethod
    def get_system_list():
        return ["videoplayer"]

    def pre_configure(self):
        if not os.path.isfile(JOY2KEY_FILE):
            logging.info("closing videoplayer: can't find file: %s" % \
                         JOY2KEY_FILE)
            self.panic("Sorry, can't find joy2key", "Please, try again!")

    def configure(self):
        if self.m_sSystem == "videoplayer":
            self.m_sSystemFreq = "videoplayer50"
        os.system('sudo killall %s > /dev/null 2>&1' % JOY2KEY_NAME)

    def prepare(self):
        #if more than one video and selected is not the last
        if self._find_videos() and \
           (self.m_nVideoNUM != self.m_nVideoPOS+1):
            self.m_sPlayAll = menu_options(self.m_lOptVideo, self.m_sTitVideo)

    def runcommand_start(self):
        """ launch_videoplayer!"""
        logging.info("Launching Joy2Key")
        self._launch_joy2key('kcub1', 'kcuf1', 'kcuu1', 'kcud1', '0x20', '0x71',
                            '0x6b', '0x6a', '0x6d', '0x6e')
        logging.info("Playing video: %s" % \
                     self.m_lVideoLST[self.m_nVideoPOS])

    def wait(self):
        commandline = self.m_sOMXPCommand % \
                      self.m_lVideoLST[self.m_nVideoPOS]
        self.m_oRunProcess = os.system(commandline)
        logging.info("Subprocess running: %s" % commandline)
        logging.info("wait omxplayer to finish")
        while True:
            wait_process('omxplayer.bin')
            exit_code = os.WEXITSTATUS(self.m_oRunProcess)
            if exit_code == 3:
                break
            else:
                if self.m_sPlayAll == "True":
                    self.m_nVideoPOS += 1
                    try:
                        self.m_lVideoLST[self.m_nVideoPOS]
                        logging.info("Playing video: %s" % \
                                     self.m_lVideoLST[self.m_nVideoPOS])
                        commandline = self.m_sOMXPCommand % \
                                      self.m_lVideoLST[self.m_nVideoPOS]
                        self.m_oRunProcess = os.system(commandline)
                        logging.info("Subprocess running: %s", commandline)
                    except:
                        break
                else:
                    break
            time.sleep(0.5)
        logging.info("process end")

    def cleanup(self):
        #os.system('echo %s >> /tmp/proces' % returncoded)
        os.system('sudo killall %s > /dev/null 2>&1' % JOY2KEY_NAME)
        self.m_oCRT.screen_restore()
        logging.info("ES mode recover")
        os.system('clear')
        sys.exit()

    def _launch_joy2key(self, left, right, up, down, a, b, x, y, start, select):
        if not os.path.exists (JOY2KEY_FILE):
            return False
        # get the first joystick device (if not already set)
        JOY2KEY_VAR = commands.getoutput('$__joy2key_dev')
        JOY2KEY_DEV = "/dev/input/jsX"
        if os.path.exists (JOY2KEY_VAR): JOY2KEY_DEV = JOY2KEY_VAR
        # launch joy2key if not running
        p_sOutput = commands.getoutput('ps -A')
        if not JOY2KEY_NAME in p_sOutput:
            p_sJ2KCommand = '"%s" "%s" %s %s %s %s %s %s %s %s %s %s' % \
                               (JOY2KEY_FILE, JOY2KEY_DEV, left, right, up, \
                               down, a, b, x, y, start, select)
            process = subprocess.Popen(p_sJ2KCommand, shell=True)
            return process

    def _find_videos(self):
        self.m_sFileDir
        for extension in self.m_lVideoEXT:
            self.m_lVideoLST = self.m_lVideoLST + glob.glob(("%s/*.%s") % \
                                                    (self.m_sFileDir,extension))
        self.m_lVideoLST = sorted(self.m_lVideoLST)
        self.m_nVideoNUM = len(self.m_lVideoLST)
        self.m_nVideoPOS = self.m_lVideoLST.index(self.m_sFilePath)
        logging.info("Detected %s videos, selected in position number %s" % \
                    (self.m_nVideoNUM, self.m_nVideoPOS))
        if self.m_nVideoNUM >= 1:
            return True
        return False
