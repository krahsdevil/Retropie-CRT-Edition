#!/usr/bin/python3
# -*- coding: utf-8 -*-


"""
CRT Daemon main service code
CRT Daemon for jamma controls (third party software activator) by -krahs-

https://github.com/krahsdevil/crt-for-retropie/

Copyright (C)  2018/2020 -krahs- - https://github.com/krahsdevil/
Copyright (C)  2020 dskywalk - http://david.dantoine.org

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
import subprocess
import logging, traceback
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(SCRIPT_DIR + "/../"))
from main_paths import MODULES_PATH
sys.path.append(MODULES_PATH)

from cable_utils import *
from launcher_module.core_paths import *
from launcher_module.utils import set_procname, check_process, \
                                  wait_process, module_exists, \
                                  module_loaded
from launcher_module.file_helpers import md5_file, ini_set, ini_get, \
                                         generate_random_temp_filename
from module_config.config_utils import saveboot

LOG_PATH = os.path.join(TMP_LAUNCHER_PATH,"CRT_RGB_Cable.log")
EXCEPTION_LOG = os.path.join(TMP_LAUNCHER_PATH, "backtrace.log")

__VERSION__ = '0.1'
__DEBUG__ = logging.INFO # logging.ERROR
CLEAN_LOG_ONSTART = True

set_procname(PNAME_RGBCABLE)

class CRTDaemon(object):
    m_sHashConfig     = ""
    m_iCableType      = None
    m_iCableType_Prev = -1
    m_bCableLoaded    = False
    m_bRecovery       = False
    m_bRecovMode      = "DEFAULT"
    m_bDaemonEna      = True
    
    m_sTempFile = ""
    
    def __init__(self):
        self.__temp()
        logging.info("INFO: Initializating CRT Daemon")
        self.m_oPI2JAMMA = pi2jammaMNGR()
        self.m_oJRGBPI = jammargbpiMNGR()
        
    def run(self):
        self._loop()

    def _loop(self, p_iTime = 20, p_iLoops = 4):
        """ 
        MAIN PROGRAM.
        Will be checking during x loops and y seconds per loop if any
        jamma cable is selected and apply its needed sofware.
        After cycle if no one jamma cable is detected on config.txt 
        daemon will be closed.
        """
        logging.info('INFO: starting main search cycle of ' + \
                     '{%s loops}x{%s seconds}' % (p_iLoops, p_iTime))
        iCounter = 0
        while iCounter < p_iLoops:
            if check_process(PNAME_CONFIG):
                wait_process(PNAME_CONFIG)
            self._get_config()
            self._halt_daemon()
            self._recovery_mode()
            self._load_cable()
            time.sleep(p_iTime)          # Wait until next cycle
            iCounter += 1
            if self.m_bCableLoaded: # Keep daemon if any jamma cable
                logging.info('INFO: JAMMA CABLE FOUND; ' + \
                             'clearing search cycle')
                iCounter = 0
            else:
                logging.info('INFO: starting checking round: %s' % iCounter)
        logging.info('INFO: NO JAMMA CABLE FOUND after search cycle ' + \
                     'of {%s loops}x{%s seconds}' \
                     % (p_iLoops, p_iTime))
        self._quit()
    
    def _get_config(self):
        """ get configuration from boot.txt """
        p_sHashTemp = md5_file(RASP_BOOTCFG_FILE)
        if p_sHashTemp != self.m_sHashConfig:
            self.m_iCableType  = int(ini_sect_get_key(RASP_BOOTCFG_FILE, 
                                     'CRT-CABLE', 'crt_cable_type'))
            self.m_bRecovery   = int(ini_sect_get_key(RASP_BOOTCFG_FILE, 
                                     'CRT-RECOVERY', 'crt_recovery_enabled'))
            self.m_bDaemonEna  = int(ini_sect_get_key(RASP_BOOTCFG_FILE, 
                                     'CRT-RECOVERY', 'crt_daemon_enabled'))

            if self.m_bRecovery:
                value =  ini_sect_get_key(RASP_BOOTCFG_FILE, 
                                          'CRT-RECOVERY', 'crt_recovery_mode')
                if value: self.m_bRecovMode = value
        self.m_sHashConfig = p_sHashTemp

    def _load_cable(self):
        if self.m_iCableType != self.m_iCableType_Prev:
            if self.m_iCableType_Prev != -1:
                logging.info("WARNING: cable selection changed in boot.txt")
            if self.m_oJRGBPI.check():
                logging.info("INFO: forcing JAMMA RGB-PI unload")
                self.m_oJRGBPI.kill()
            if self.m_oPI2JAMMA.check():
                logging.info("INFO: forcing PI2JAMMA unload")
                self.m_oPI2JAMMA.kill()
            self.m_iCableType_Prev = self.m_iCableType
        
        if self.m_iCableType == 1:
            logging.info("INFO: looking for JAMMA PICRT/RGB-PI versions")
            self.m_bCableLoaded = self.m_oJRGBPI.load()
        elif self.m_iCableType == 2:
            logging.info("INFO: PI2JAMMA is configured on boot.txt")
            self.m_bCableLoaded = self.m_oPI2JAMMA.load()
        else: self.m_bCableLoaded = False

    def _recovery_mode(self):
        """
        If recovery mode is enabled in /boot/config.txt this function will
        apply the selected MODE in crt_recovery_mode. This mode must be
        profiled in ~/CRT/bin/ScreenUtilityFiles/config_files/modes.cfg
        These MODES is a way to give compatibility to some TV or monitors.
        Basically are diffs to apply to the base timings to fit with with
        resolution. By default are three but is possible to create more
        following the scheme of current ones.
        """
        if self.m_bRecovery:
            p_lCheck = ini_set(CRT_FIXMODES_FILE, 'mode_default', self.m_bRecovMode.upper())
            logging.info("INFO: changed recovery mode to {%s} " % self.m_bRecovMode)
            self._clone_boot_cfg()

            ini_sect_set_key(self.m_sTempFile, 'CRT-RECOVERY', 'crt_recovery_enabled', 0)
            ini_sect_set_key(self.m_sTempFile, 'CRT-RECOVERY', 'crt_recovery_mode', 'DEFAULT')
            self._upload_boot_cfg()

            # Create timings with MODE for system/ES in /boot/config.txt
            p_oRESClass = saveboot()
            p_oRESClass.save()
            p_oRESClass.apply()
            self._restart_system()

    def _halt_daemon(self):
        """
        Will wait or close daemon if one of next conditions happen
        If daemon is disabled it will do nothing, only exit.
        """
        if not self.m_bDaemonEna:
            logging.info("WARNING: daemon disabled in /boot/config.txt")
            self._quit()
        if check_process('resize2fs'):
            logging.info("WARNING: Wait until resize2fs finish")
            wait_process('resize2fs')

    def _clone_boot_cfg(self):
        self.m_sTempFile = generate_random_temp_filename(RASP_BOOTCFG_FILE)
        os.system('cp %s %s' % (RASP_BOOTCFG_FILE, self.m_sTempFile))
        logging.info('INFO: taking a temp copy of config.txt ' + \
                     ' at %s' % self.m_sTempFile)

    def _upload_boot_cfg(self):
        os.system('sudo cp %s %s' %(self.m_sTempFile, RASP_BOOTCFG_FILE))
        logging.info('INFO: uploading modified config.txt to /boot')
        self.__clean()

    def _restart_system(self):
        """ Restart system and close ES if it's running """
        if check_process("emulationstatio"):
            commandline = 'sudo killall emulationstation && clear'
            os.system(commandline)
        os.system('sudo reboot now')

    def __clean(self):
        if os.path.exists (self.m_sTempFile):
            os.system('rm "%s"' % self.m_sTempFile)
            self.m_sTempFile = ""

    def _quit(self):
        logging.info('Exiting from daemon')
        self.__clean()
        sys.exit(0)
        
    def __temp(self):
        if CLEAN_LOG_ONSTART:
            if os.path.exists (LOG_PATH):
                os.system('rm "%s"' % LOG_PATH)
        logging.basicConfig(filename=LOG_PATH, level=__DEBUG__,
        format='[%(asctime)s] %(levelname)s - %(filename)s:%(funcName)s - %(message)s')

class pi2jammaMNGR(object):
    m_oRunBinary = None
    PI2JAMMA_PATH = os.path.join(CRT_ASST_PATH, 'driver_pi2jamma')
    PI2JAMMA_BIN = 'pikeyd165'
    PI2JAMMA_BIN_FILE_SRC = os.path.join(PI2JAMMA_PATH, PI2JAMMA_BIN)
    PI2JAMMA_BIN_FILE_DST = os.path.join('/usr/local/bin/', PI2JAMMA_BIN)

    PI2JAMMA_CFG = 'pikeyd165.conf'
    PI2JAMMA_CFG_FILE_SRC = os.path.join(PI2JAMMA_PATH, PI2JAMMA_CFG)
    PI2JAMMA_CFG_FILE_DST = os.path.join('/etc', PI2JAMMA_CFG)

    def __init__(self):
        pass

    def load(self):
        """ will load PI2JAMMA drivers """
        if not self.check():
            logging.info("INFO: trying to load pi2jamma driver")
            if not self.check_files(): return False
            os.system('sudo chmod a+rwx /dev/uinput')
            commandline = 'sudo -s %s ' % self.PI2JAMMA_BIN
            commandline += '-smi -ndb -d &> /dev/null'
            self.m_oRunBinary = subprocess.Popen(commandline, shell=True)
            logging.info("INFO: Subproc launched: %s, " % self.PI2JAMMA_BIN + \
                         "PID: %s" % self.m_oRunBinary.pid)
            if self.check(True):
                logging.info("INFO: pi2jamma driver loaded")
                if self.detect(): return True
                else: self.kill()
        else:
            logging.info("INFO: Subprocess for pi2jamma " + \
                         "already FOUND running")
            return True
        logging.info("WARNING: couldn't load pi2jamma cable")
        return False

    def detect(self):
        # pi2jamma detection disabled
        return True
        commandline = 'sudo python3 pi2jamma_check.py'
        p = subprocess.Popen(commandline, shell=True)
        iTime = time.time()
        while p.poll() == None:
            if time.time() - iTime > 3: break
        code = p.returncode
        if code == 100: 
            logging.info("INFO: hardware pi2jamma found")
            return True
        elif code == 50: 
            logging.info("INFO: error detecting pi2jamma")
            return False
        logging.info("WARNING: hardware pi2jamma not found")
        return False

    def kill(self):
        """ This function will close pi2jamma software """
        os.system('sudo chmod a+rwx /dev/uinput')
        commandline = 'sudo -s  %s -k ' % self.PI2JAMMA_BIN
        commandline += '&> /dev/null'
        os.system(commandline)
        while self.check():
            pass
        logging.info("INFO: pi2jamma driver unloaded")
        self.m_oRunBinary = None
        return True

    def check(self, WaitStart = False):
        """ check current status of driver """
        p_iWTime = 2 # time to wait
        start = time.time()
        while True:
            value = check_process(self.PI2JAMMA_BIN)
            if not WaitStart: break
            else:
                if value or (time.time() - start) > p_iWTime: 
                    break
        return value

    def check_files(self):
        """ 
        pi2jamma asset of files.
        Will check if binary and config files are stored in assets
        folder of this Retropie CRT Edition to install in system if
        needed (pikeyd165 & pikeyd165.conf)
        """
        p_bCheck = True
        if not os.path.exists(self.PI2JAMMA_CFG_FILE_SRC):
            p_bCheck = False
            logging.info("WARNING: not found %s" % self.PI2JAMMA_CFG_FILE_SRC)
        if not os.path.exists(self.PI2JAMMA_BIN_FILE_SRC):
            p_bCheck = False
            logging.info("WARNING: not found %s" % self.PI2JAMMA_BIN_FILE_SRC)
        
        # if source files exits, check instalation
        if p_bCheck:
            sync_files(self.PI2JAMMA_BIN_FILE_SRC,
                       self.PI2JAMMA_BIN_FILE_DST, "x")
            sync_files(self.PI2JAMMA_CFG_FILE_SRC,
                       self.PI2JAMMA_CFG_FILE_DST)
        return p_bCheck

class jammargbpiMNGR(object):
    JAMMARGBPI_MODULE = 'mk_arcade_joystick_rpi'
    def __init__(self):
        pass

    def load(self):
        """ will load JAMMA RGB-PI drivers """
        if self.check():
            logging.info("INFO: jamma rgb-pi already loaded") 
            return True
        else: 
            logging.info("INFO: trying to load jamma-rgb-pi module")
             # Check if mk_arcade_joystick_rpi is loaded is system
            if not module_exists(self.JAMMARGBPI_MODULE):
                logging.info("WARNING: %s not installed" % self.JAMMARGBPI_MODULE)
                return False
            if not self.detect():
                return False
            os.system('sudo modprobe %s i2c0=0x20,0x21' % self.JAMMARGBPI_MODULE)
            if self.check(): 
                logging.info("INFO: jamma rgb-pi now loaded") 
                return True
            else:
                logging.info("WARNING: couldn't load module: %s" \
                             % self.JAMMARGBPI_MODULE)
        return False

    def detect(self):
        """ 
        This function try to detect in i2c bus 0 if any i2c device is 
        connected looking for addreses.
        """
        if i2c_detect([32, 33]): # 0x20/0x21 i2c address;
            logging.info("INFO: hardware jamma rgb-pi found")
            return True
        else:
            logging.info("WARNING: hardware jamma-rgb-pi NOT found")
            return False

    def kill(self):
        """ This function will close JAMMA RGB-PI software """
        while self.check():
            logging.info("INFO: Killing %s module" % self.JAMMARGBPI_MODULE)
            os.system('sudo modprobe -r %s' % self.JAMMARGBPI_MODULE)
        return True

    def check(self):
        """ check current status of driver """
        if module_loaded(self.JAMMARGBPI_MODULE): return True
        return False

try:
    oCRTDaemon = CRTDaemon()
    oCRTDaemon.run()
except Exception as e:
    with open(EXCEPTION_LOG, 'a') as f:
        f.write(str(e))
        f.write(traceback.format_exc())

