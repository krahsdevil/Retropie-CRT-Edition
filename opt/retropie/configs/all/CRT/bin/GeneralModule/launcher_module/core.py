#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
launcher core.py.

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


import os, sys
import subprocess, commands
import logging

from .screen_helpers import crt_open_screen_from_timings_cfg, es_restore_screen
from .utils import something_is_bad, splash_info
from .file_helpers import *

__VERSION__ = '0.1'
__DEBUG__ = logging.INFO # logging.ERROR
CLEAN_LOG_ONSTART = True

TMP_LAUNCHER_PATH = "/tmp/crt"
TMP_SPEEPER_NAME = "lchtmp"
TMP_SLEEPER_FILE = os.path.join(TMP_LAUNCHER_PATH, TMP_SPEEPER_NAME)
LEGACY_SLEEPER_FILE = "/tmp/lchtmp"

LOG_PATH = os.path.join(TMP_LAUNCHER_PATH, "CRT_Launcher.log")

# retropie path setup
__RETROPIE_PATH = "/opt/retropie"
RETROPIECFG_PATH = os.path.join(__RETROPIE_PATH, "configs")
__CRTROOT_PATH = os.path.join(RETROPIECFG_PATH, "all/CRT")
__CRTBIN_PATH = os.path.join(__CRTROOT_PATH, "bin")

CRT_RUNCOMMAND_FORMAT = "touch %s && sleep 1 && "
RUNCOMMAND_FILE = os.path.join(__RETROPIE_PATH, "supplementary/runcommand/runcommand.sh")

CFG_VIDEOMODES_FILE = os.path.join(RETROPIECFG_PATH, "all/videomodes.cfg")
CFG_CUSTOMEMU_FILE = os.path.join(RETROPIECFG_PATH, "all/emulators.cfg")

CFG_FIXMODES_FILE = os.path.join(__CRTBIN_PATH, "ScreenUtilityFiles/modes.cfg")
CFG_VIDEOUTILITY_FILE = os.path.join(__CRTBIN_PATH,"ScreenUtilityFiles/utility.cfg")
CFG_NETPLAY_FILE = os.path.join(__CRTROOT_PATH, "netplay.cfg")
CFG_TIMINGS_FILE = os.path.join(__CRTROOT_PATH, "Resolutions/base_systems.cfg")
RACFG_PATH = os.path.join(__CRTROOT_PATH, "Retroarch/configs")



# FIXME: arcade
RC_ADVANCEDMAME_FILE = os.path.join(__RETROPIE_PATH, "mame-advmame/advmame.rc")
__ARCADE_PATH = TMP_LAUNCHER_PATH
__ARCADE_FILE = "retroarcharcade"
CFG_ARCADE_FILE = "%s%s.cfg" % (__ARCADE_PATH, __ARCADE_FILE)


""" virtual class for crt launcher """
class launcher(object):

    m_sCfgSystemPath = ""
    m_sSystemFreq = ""
    m_sBinarySelected = ""
    m_lBinaryMasks = []
    m_lBinaries = []
    m_lProcesses = []

    m_oRunProcess = None

    def __init__(self, p_sRomPath, p_sSystem, p_sCustom):
        self.m_sRomPath = p_sRomPath
        self.m_sSystem = p_sSystem
        self.m_sSystemVideoName = p_sSystem
        self.m_sCustom = p_sCustom

        self.__temp()
        logging.info("INFO: arg 1 (rom_path) = %s, (system) = %s, (sin uso) = %s"
            % (self.m_sRomPath, self.m_sSystem, self.m_sCustom))

        # rom name work
        self.__clean()
        self.__setup()

        # user virtual methods
        self.init()

    def start(self):
        self.netplay_setup()
        self.system_setup()
        self.video_setup()
        self.emulator_setup()
        self.runcommand_check()
        self.runcommand_start()
        self.emulator_prepare()
        self.emulator_final_check()

    def wait(self):
        self.m_oRunProcess.wait()
        logging.info("process end")

    def cleanup(self):
        es_restore_screen()
        logging.info("ES mode recover")
        os.system('clear')
        self.__clean()
        sys.exit()

    def panic(self, p_sErrorLine1, p_sErrorLine2 = "-", p_bForceQuit = True):
        logging.error("PANIC: %s" % p_sErrorLine1)
        something_is_bad(p_sErrorLine1, p_sErrorLine2)
        if p_bForceQuit:
            logging.error("EXIT: crt_launcher forced")
            self.__clean()
            sys.exit(1)

    def clean_videomodes(self):
        try:
            os.remove(CFG_VIDEOMODES_FILE)
        except OSError:
            return False
        return True

    # called children init at start, called by __init__()
    def init(self):
        pass

    # esto quiza habria que hacerlo de forma externa, un proceso al inicio...
    def __temp(self):
        if not os.path.isdir(TMP_LAUNCHER_PATH):
            os.makedirs(TMP_LAUNCHER_PATH)
            # os.system("mount -t tmpfs -o size=8m tmpfs %s" % TMP_LAUNCHER_PATH)
        if CLEAN_LOG_ONSTART:
            remove_file(LOG_PATH)
        logging.basicConfig(filename=LOG_PATH, level=__DEBUG__, format='[%(asctime)s] %(levelname)s - %(funcName)s : %(message)s')


    # setup paths - called by __init__()
    def __setup(self):
        self.m_sCfgSystemPath = os.path.join(RETROPIECFG_PATH, self.m_sSystem, "emulators.cfg")
        self.m_sRomFile = os.path.basename(self.m_sRomPath)
        self.m_sGameName = os.path.splitext(self.m_sRomFile)[0]

    # clean system
    def __clean(self):
        self.clean_videomodes()
        remove_file(TMP_SLEEPER_FILE)

    # TODO: Read data from EasyNetplay
    def netplay_setup(self):
        self.m_sNetIP = ""

    def video_setup(self):
        pass

    def system_setup(self):
        self.m_sSystemFreq = self.m_sSystem

    # filter returns an array with valid values, we just check if has any value :)
    def is_valid_binary(self, p_sCore):
        if filter(lambda mask: mask in p_sCore, self.m_lBinaryMasks):
            return True
        else:
            return False

    def set_binary(self, p_sCore):
        if self.is_valid_binary(p_sCore):
            self.m_sBinarySelected = p_sCore
            logging.info("Selected binary (%s)" % self.m_sBinarySelected)
        else:
            raise NameError("INVALID - binary (%s) - mask [%s]" %
                (self.m_sBinarySelected, str(self.m_lBinaryMasks)) )

    # RETROPIE allows to choice per game an specific emulator from available
    # we check if emulator is valid or clean emulators.cfg
    #
    def get_emulator_per_game(self):
        if not os.path.exists(CFG_CUSTOMEMU_FILE):
            return False
        sCleanName = re.sub('[^a-zA-Z0-9-_]+','', self.m_sGameName ).replace(" ", "")
        sGameSystemName = "%s_%s" % (self.m_sSystem, sCleanName)
        need_clean = False
        with open(CFG_CUSTOMEMU_FILE, 'r') as oFile:
            for line in oFile:
                lValues = line.strip().split(' ')
                if lValues[0] == sGameSystemName:
                    if self.is_valid_binary(lValues[2]):
                        self.m_sBinarySelected = lValues[2]
                        return True
                    else: # not valid is just ignored
                        need_clean = True
        # clean emulators.cfg if have an invalid binary
        if need_clean:
            logging.info("cleaning line %s from %s" % (sGameSystemName, CFG_CUSTOMEMU_FILE))
            remove_line(CFG_CUSTOMEMU_FILE, sGameSystemName)
        return False

    # we try to found this line: default = "emulator-binary-name"
    # p_oFile: file ready to seek
    # return: default emu or die
    def default_emulator(self, p_bSetCore):
        with open(self.m_sCfgSystemPath, "r") as oFile:
            for line in oFile:
                lValues = line.strip().split(' ')
                if lValues[0] == 'default':
                    sBinaryName = lValues[2].replace('"', '')
                    if p_bSetCore:
                        self.set_binary(sBinaryName)
                    else:
                        return self.is_valid_binary(sBinaryName)

    # we try to found emulator-binary-name = "command-to-launch-the-game"
    #   valid with our masks, if not found then die
    def add_system_emulators(self):
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
                self.panic("NOT FOUND any emulators mask [%s]" % str(self.m_lBinaryMasks))

    # prepare emulator to launch
    def emulator_setup(self):
        try:
            self.add_system_emulators()
            if not self.get_emulator_per_game():
                self.default_emulator(True)
        except IOError as e:
            infos = "File error at emulators.cfg [%s]" % self.m_sSystem
            infos2 = "Please, install at least one emulator or core"
            self.panic(infos, infos2)
        except Exception as e:
            infos = "Error in emulators.cfg [%s]" % self.m_sSystem
            self.panic(infos, str(e))

    # check if runcommand has correct behaivor:
    #   FROM emulator-binary-name = "command-to-launch-the-game"
    #   TO   emulator-binary-name = "crt-command && command-to-launch-the-game"
    def runcommand_check(self):
        f = open(self.m_sCfgSystemPath, "r")
        new_file = f.readlines()
        f.close()
        # only change file if is need it
        for line in new_file:
            lValues = line.strip().split('=')
            lValues = map(lambda s: s.strip(), lValues)
            if lValues[0] == self.m_sBinarySelected:
                sEmulatorCommand = lValues[1]
                if LEGACY_SLEEPER_FILE in sEmulatorCommand:
                    sEmulatorCommand = sEmulatorCommand \
                        .replace(CRT_RUNCOMMAND_FORMAT % LEGACY_SLEEPER_FILE, '')
                if TMP_SLEEPER_FILE not in sEmulatorCommand:
                    sEmulatorCommand = sEmulatorCommand.replace('"','').strip()
                    new_line = self.m_sBinarySelected + " = \""
                    new_line += CRT_RUNCOMMAND_FORMAT % TMP_SLEEPER_FILE
                    new_line += sEmulatorCommand + "\""
                    logging.info("changed command (%s)" % new_line)
                    modify_line(self.m_sCfgSystemPath, line, new_line)

    # wait_runcommand: wait for user launcher menu
    #   @full_checks: off, just check current process.
    #   return: True, if user wants close emulation directly.
    def runcommand_wait(self, full_checks = True):
        if not self.m_lProcesses:
            self.panic("processes not available")

        logging.info("wait runcommand ends and start: %s (full_checks: %s)" % (str(self.m_lProcesses), str(full_checks)) )
        # TODO: better use a symple socket daemon
        while True:
            if full_checks:
                if os.path.exists(TMP_SLEEPER_FILE):
                    logging.info("detected trigger file %s, wait finished..." % TMP_SLEEPER_FILE)
                    return False
                # try to detect if user exits from runcommand
                poll = self.m_oRunProcess.poll()
                if poll != None:
                    logging.info("runcommand closed by user (poll = %s)" % poll)
                    RuncommandClosed = True
                    return True
            output = commands.getoutput('ps -A')
            for proc in self.m_lProcesses:
                if proc in output:
                    logging.info("detected %s in active process, wait finished...", proc)
                    return False

    # launch_core: run emulator!
    def runcommand_start(self):
        commandline = "%s 0 _SYS_ %s \"%s\"" % (RUNCOMMAND_FILE, self.m_sSystem, self.m_sRomPath)
        self.m_oRunProcess = subprocess.Popen(commandline, shell=True)
        logging.info("Subprocess running: %s", commandline)
        self.runcommand_wait()

    def emulator_prepare(self):
        crt_open_screen_from_timings_cfg(self.m_sSystemFreq, CFG_TIMINGS_FILE)
        try:
            splash_info("black") # clean screen
        except Exception as e:
            logging.error("splash failed: %s" % e)
        logging.info("clean: %s", TMP_SLEEPER_FILE)
        remove_file(TMP_SLEEPER_FILE)


    def emulator_kill(self):
        self.runcommand_wait(False)
        logging.error("closing %s processes" % str(self.m_lProcesses))
        for proc in self.m_lProcesses:
            os.system('killall %s > /dev/null 2>&1' % proc)


    def emulator_final_check(self):
        bValidCore = self.default_emulator(False)
        if not bValidCore:
            self.emulator_kill()
            remove_line(self.m_sCfgSystemPath, "default =")
            self.panic("selected invalid emulator", "try again!")

