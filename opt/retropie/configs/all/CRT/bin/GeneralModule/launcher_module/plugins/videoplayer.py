#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
videoplayer.py

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
from launcher_module.core_choices_dynamic import choices
from launcher_module.core import launcher
from launcher_module.core_paths import *

CRTASSETS_VIDEO_PATH = os.path.join(CRT_ASST_PATH, "screen_videoplayer")
FONT_FILE = os.path.join(CRTASSETS_VIDEO_PATH, "Ubuntu_MOD_WIDE.ttf")
JOY2KEY_FILE = os.path.join(CRTASSETS_VIDEO_PATH, "joy2key.py")

class videoplayer(launcher):
    m_nVideoPOS = 0
    m_nVideoNUM = 0
    m_lVideoEXT = ['avi', 'mkv', 'mp4', 'mpg', 'AVI', 'MKV', 'MP4', 'MPG']
    m_lVideoLST = []

    m_sPlayAll = "False"

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
            self.panic("can't find joy2key", "try again!")

    def configure(self):
        if self.m_sSystem == "videoplayer":
            self.m_sSystemFreq = "videoplayer50"

    def prepare(self):
        #if more than one video and selected is not the last
        if self._find_videos() and \
           (self.m_nVideoNUM != self.m_nVideoPOS+1):
            self.m_sPlayAll = self.video_options()

    def runcommand_start(self):
        """ launch_videoplayer!"""
        commandline = self.m_sOMXPCommand % \
                      self.m_lVideoLST[self.m_nVideoPOS]
        logging.info("Launching Joy2Key")
        self._launch_joy2key('kcub1', 'kcuf1', 'kcuu1', 'kcud1', '0x20', '0x71',
                            '0x6b', '0x6a', '0x6d', '0x6e')
        logging.info("Playing video: %s" % \
                     self.m_lVideoLST[self.m_nVideoPOS])
        self.m_oRunProcess = subprocess.Popen(commandline, shell=True)
        logging.info("Subprocess running: %s" % commandline)

    def wait(self):
        logging.info("wait omxplayer to finish")
        while True:
            poll = self.m_oRunProcess.poll()
            if poll != None:
                returncoded = self.m_oRunProcess.returncode
                if returncoded == 3:
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

    def _launch_joy2key(self, left, right, up, down, a, b, x, y, start, select):
        # get the first joystick device (if not already set)
        JOY2KEY_VAR = commands.getoutput('$__joy2key_dev')
        JOY2KEY_DEV = "/dev/input/jsX"
        if os.path.exists (JOY2KEY_VAR):
            JOY2KEY_DEV = JOY2KEY_VAR
        output = commands.getoutput('ps -A')
        if os.path.exists (JOY2KEY_FILE) and JOY2KEY_DEV != "none" and \
           not 'joy2key.py' in output:
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

    def video_options(self):
        ch = choices()
        ch.set_title("VIDEO PLAYER")
        ch.load_choices([("Just this video...", "False"),
                         ("Play ALL from this!", "True")])
        result = ch.run()
        return result
