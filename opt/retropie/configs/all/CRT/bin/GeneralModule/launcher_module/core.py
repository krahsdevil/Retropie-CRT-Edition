#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
launcher core.py.

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


import os, sys
import subprocess, commands, time
import logging

from .screen import CRT
from .utils import HideScreen, check_process, show_info
from .core_paths import *
from .file_helpers import *

__VERSION__ = '0.1'
__DEBUG__ = logging.INFO # logging.ERROR
CLEAN_LOG_ONSTART = True

LOG_PATH = os.path.join(TMP_LAUNCHER_PATH, "CRT_Launcher.log")

CRT_RUNCOMMAND_FORMAT = "touch %s && sleep 1.5 && "

class launcher(object):
    """ virtual class for crt launcher """
    m_sFileName = ""
    m_sFileNameVar = "%ROM%"
    m_sCfgSystemPath = ""
    m_sSystemFreq = ""
    m_sSelCore = ""
    m_sNextValidBinary = ""
    m_lBinaryMasks = []
    m_lBinaryUntouchable = []
    m_lBinaries = []
    m_lProcesses = PROCESSES
    m_oBlackScreen = None
    m_oRunProcess = None
    m_oCRT = None

    def __init__(self, p_sFilePath, p_sSystem, p_sCustom):
        self.m_sSystem = p_sSystem
        self.m_sCustom = p_sCustom
        self.m_sFilePath = p_sFilePath
        self.m_sFileName = os.path.basename(self.m_sFilePath)
        self.m_sFileDir = os.path.dirname(self.m_sFilePath)
        self.m_sGameName = os.path.splitext(self.m_sFileName)[0]
        self.m_oBlackScreen = HideScreen()

        self.__temp()
        self.__clean()
        logging.info("INFO: arg 1 (rom_path) = %s, (system) = %s, (sin uso) = %s"
            % (self.m_sFilePath, self.m_sSystem, self.m_sCustom))

        self.pre_configure() # user virtual method get init values
        self.configure() # rom name work
        self.post_configure() # user virtual method for post configure
        self.prepare() # check runcommand and screen
        self.run() # launch, wait and cleanup

    # called children pre_configure at start, called by __init__()
    def pre_configure(self):
        self.m_sCfgSystemPath = os.path.join(RETROPIE_CFG_PATH, self.m_sSystem, "emulators.cfg")

    # setup paths - called by __init__()
    def configure(self):
        self.m_sSystemFreq = self.m_sSystem

    # called children post_configure at start, called by __init__()
    def post_configure(self):
        pass

    def prepare(self):
        self.runcommand_prepare()
        self.screen_prepare()

    def run(self):
        self.start()
        self.wait()
        self.cleanup()

    def start(self):
        self.runcommand_start()
        self.screen_set()

    def wait(self):
        time_start = time.time()
        self.m_oRunProcess.wait()
        time_elapsed = int(time.time() - time_start)
        self.statistics(time_elapsed)
        logging.info("INFO: game time: %s" % time_elapsed)
        logging.info("INFO: process end")

    # generate command string
    # just called if need rebuild the CMD
    def runcommand_generate(self, p_sCMD):
        p_sCMD = p_sCMD.replace('"','').strip()
        new_cmd = self.m_sNextValidBinary + " = \""
        new_cmd += CRT_RUNCOMMAND_FORMAT % TMP_SLEEPER_FILE
        new_cmd += p_sCMD + "\""
        return new_cmd
        # --apendconfig must be added on each plugin if needed
        # usually for retroarch.

    def runcommand_clean(self, p_sCMD):
        # first remove quotes
        p_sCMD = p_sCMD.replace('"', '')
        # check if %BASENAME% is used instead of %ROM%
        if '%BASENAME%' in p_sCMD:
            self.m_sFileNameVar = "%BASENAME%"
        elif '%ROM%' in p_sCMD:
            self.m_sFileNameVar = "%ROM%"

        # "touch /path/lchtmp && sleep 1 && /path/retroarch ...
        # "/path/retroarch ...
        if "&&" in p_sCMD:
            p_sCMD = p_sCMD.split("&&")[-1]
        # ... --appendconfig /path/system.cfg %ROM%"'
        # ... %ROM%"'
        if "--appendconfig" in p_sCMD:
            p_sCMD = p_sCMD.split("--appendconfig")[0]
        # add at the end
        if self.m_sFileNameVar not in p_sCMD:
            p_sCMD += self.m_sFileNameVar
        # finally add quotes
        p_sCMD = '"' + p_sCMD.strip() + '"'
        return p_sCMD

    # check if runcommand has correct behaivor:
    #   FROM emulator-binary-name = "command-to-launch-the-game"
    #   TO   emulator-binary-name = "crt-command && command-to-launch-the-game"
    def runcommand_prepare(self):
        f = open(self.m_sCfgSystemPath, "r")
        new_file = f.readlines()
        f.close()
        # only change file if is need it
        for Binary in self.m_lBinaries:
            for line in new_file:
                lValues = line.strip().split('=')
                sCMD = lValues[1].strip()
                if len(lValues) > 2:
                    sCMD = "=".join(lValues[1:]).strip()
                lValues = map(lambda s: s.strip(), lValues)
                if lValues[0] == Binary:
                    self.m_sNextValidBinary = lValues[0]
                    cmd_cleaned = self.runcommand_clean(sCMD)
                    cmd_current = self.runcommand_generate(cmd_cleaned)
                    if cmd_current != line.strip(): # atm just force our cmd
                        logging.info("changed command (%s)" % cmd_current)
                        modify_line(self.m_sCfgSystemPath, line, cmd_current)


    # wait_runcommand: wait for user launcher menu
    #   @only_runcommand: off, just check current process.
    #   return: True, if user wants close emulation directly.
    def runcommand_wait(self, only_runcommand = True):
        timer = 0 # security timer
        if not self.m_lProcesses:
            self.panic("processes not available")
        if only_runcommand:
            logging.info("INFO: waiting runcommand ends and start")
        else:
            logging.info("INFO: waiting one emulator process on this list: %s " % \
                        str(self.m_lProcesses))
        # TODO: better use a symple socket daemon
        while True:
            if only_runcommand:
                if os.path.exists(TMP_SLEEPER_FILE):
                    logging.info("INFO: detected trigger file %s, wait finished..." % TMP_SLEEPER_FILE)
                    return False
                # try to detect if user exits from runcommand
                poll = self.m_oRunProcess.poll()
                if poll != None:
                    logging.info("INFO: runcommand closed by user (poll = %s)" % poll)
                    RuncommandClosed = True
                    return True
            if check_process(self.m_lProcesses):
                logging.info("INFO: detected emulator active process, wait finished...")
                return False
            elif not only_runcommand:
                time.sleep(0.01)
                timer += 0.01
                if timer > 1.5:
                    logging.info("INFO: Process not found, exiting by security timer.")
                    return None

    def runcommand_start(self):
        """ launch_core: run emulator!"""
        commandline = "%s 0 _SYS_ %s \"%s\"" % (RETROPIE_RUNCOMMAND_FILE, self.m_sSystem, self.m_sFilePath)
        self.m_oRunProcess = subprocess.Popen(commandline, shell=True)
        logging.info("INFO: Subprocess running: %s", commandline)
        self.runcommand_wait()

    def runcommand_kill(self):
        self.runcommand_wait(False)
        logging.error("INFO: trying to close emulator process")
        for proc in self.m_lProcesses:
            if check_process(proc):
                logging.info("INFO: killing process: %s", proc)
                os.system('killall %s > /dev/null 2>&1' % proc)
                while True:
                    if not check_process(proc): break

    def screen_prepare(self):
        pass

    def screen_set(self):
        self.m_oCRT = CRT(self.m_sSystemFreq)
        self.m_oCRT.screen_calculated(CRT_DB_SYSTEMS_FILE)
        self.m_oBlackScreen.fill()
        logging.info("INFO: clean: %s", TMP_SLEEPER_FILE)
        remove_file(TMP_SLEEPER_FILE)

    def panic(self, p_sErrorLine1, p_sErrorLine2 = None, p_bForceQuit = True):
        """ stop the program and show error to the user """
        sTitPanic = "SYSTEM LAUNCHING ERROR"
        lOptPanic = [(str(p_sErrorLine1).upper(), "OK")]
        if p_sErrorLine2:
            lOptPanic.append((str(p_sErrorLine2).upper(), "OK"))
        logging.error("PANIC: %s" % p_sErrorLine1)
        CRT().screen_restore()
        show_info(lOptPanic, sTitPanic, 7000)
        if p_bForceQuit:
            logging.error("EXIT: crt_launcher forced")
            self.__clean()
            sys.exit(1)

    def statistics(self, p_iTime):
        if not os.path.exists(CRT_STATS_FILE):
            touch_file(CRT_STATS_FILE)
            add_line(CRT_STATS_FILE, 'timer = "0"')
            
        value = ini_get(CRT_STATS_FILE, 'timer')
        if value:
            value = int(value) + p_iTime
            ini_set(CRT_STATS_FILE, 'timer', value)
        else: 
            add_line(CRT_STATS_FILE, 'timer = "0"')

        value = ini_get(CRT_STATS_FILE, 'played_%s' % self.m_sSystem)
        if value:
            value = int(value) + 1
            ini_set(CRT_STATS_FILE, "played_%s" % self.m_sSystem, value)
        else: 
            add_line(CRT_STATS_FILE, 'played_%s = "1"' % self.m_sSystem)

        value = ini_get(CRT_STATS_FILE, 'timer_%s' % self.m_sSystem)
        if value:
            value = int(value) + p_iTime
            ini_set(CRT_STATS_FILE, "timer_%s" % self.m_sSystem, value)
        else: 
            add_line(CRT_STATS_FILE, 'timer_%s = "%s"' % (self.m_sSystem, p_iTime))

    # cleanup code
    def cleanup(self):
        self.m_oCRT.screen_restore()
        self.m_oBlackScreen.fill()
        logging.info("INFO: ES mode recover")
        os.system('clear')
        self.__clean()
        sys.exit()

    # clean system
    def __clean(self):
        self.clean_videomodes()
        remove_file(TMP_SLEEPER_FILE)

    def clean_videomodes(self):
        try:
            os.remove(RETROPIE_VIDEOMODES_FILE)
        except OSError:
            return False
        return True

    def __temp(self):
        if CLEAN_LOG_ONSTART:
            remove_file(LOG_PATH)
        logging.basicConfig(filename=LOG_PATH, level=__DEBUG__, format='[%(asctime)s] %(levelname)s - %(filename)s:%(funcName)s - %(message)s')
