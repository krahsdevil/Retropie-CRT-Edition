#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
USB Automount Launcher

Module to check and load/unload USB Automount service for Retropie by -krahs-

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
import os, sys, traceback
import commands, time
import logging

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(SCRIPT_DIR + "/../"))
from main_paths import MODULES_PATH
sys.path.append(MODULES_PATH)

from launcher_module.utils import show_info, menu_options
from launcher_module.core_paths import TMP_LAUNCHER_PATH, CRT_BIN_PATH
from launcher_module.file_helpers import *

LOG_PATH = os.path.join(TMP_LAUNCHER_PATH, "CRT_USBAutoMount.log")
EXCEPTION_LOG = os.path.join(TMP_LAUNCHER_PATH, "backtrace.log")

USBAUTO_PATH = os.path.join(CRT_BIN_PATH, "AutomountService")
SERVICE_FILE_NAME = "CRT-Automount.service"
SERVICE_FILE = os.path.join(USBAUTO_PATH, SERVICE_FILE_NAME)
SCRIPT_FILE_NAME = "CRT-Automount.py"
SCRIPT_FILE = os.path.join(USBAUTO_PATH, SCRIPT_FILE_NAME)
TRG_MNT_FILE = os.path.join(USBAUTO_PATH, "mounted.cfg") #Trigger USB is mounted
TRG_UMNT_FILE = os.path.join(USBAUTO_PATH, "umounted.cfg") #Trigger USB is NOT mounted

__VERSION__ = '0.1'
__DEBUG__ = logging.INFO # logging.ERROR
CLEAN_LOG_ONSTART = False

class automount(object):
    """ virtual class for USB Automount enable/disable/eject """
    m_bServiceExist = False
    m_bServiceRun = False
    m_bUSBMounted = False
    m_sMountedPath = ""

    m_sTitAuto = "" # title for selector
    m_lOptAuto = [] # options for selector

    def __init__(self):
        self.__temp()
        self._check_service_run() # Check service and usb mount status
        self._prepare_options()
        logging.info("INFO: Launching USB Automount Selector")
    
    def run(self):
        show_info('PLEASE WAIT...')
        sChoice = menu_options(self.m_lOptAuto, self.m_sTitAuto)
        self._automount_act(sChoice)
        sys.exit(0)
    
    def _check_service_files(self):
        """ Check if needed service files exists """
        bCheck01 = os.path.exists(SERVICE_FILE)
        bCheck02 = os.path.exists(SCRIPT_FILE)
        if bCheck01 and bCheck02:
            return True
        return False
        
    def _check_service_run(self):
        self.m_bServiceExist = False
        self.m_bServiceRun = False
        sCommand = 'systemctl list-units --all | grep \"%s\"' % SERVICE_FILE_NAME
        sCheckService = commands.getoutput(sCommand)

        if SERVICE_FILE_NAME in sCheckService:
            self.m_bServiceExist = True
        if 'running' in sCheckService:
            self.m_bServiceRun = True

        #If service exists and it's running check if usb is mounted
        if self.m_bServiceExist and self.m_bServiceRun:
            if os.path.exists(TRG_MNT_FILE):
                file = open(TRG_MNT_FILE, 'r')
                self.m_sMountedPath = file.readlines()
                file.close()
                self.m_bUSBMounted = True
            else:
                self.m_bUSBMounted = False
                
    def _prepare_options(self):
        """ This function will prepare the menu options """
        if self.m_bServiceRun:
            self.m_sTitAuto = "USB AUTOMOUNT"
            self.m_lOptAuto.append(("STOP AUTOMOUNT!", "stop"))
            if self.m_bUSBMounted:
                self.m_lOptAuto.append(("EJECT MY USB", "eject"))
        else:
            self.m_sTitAuto = "WARNING: SERVICE STOPPED!"
            self.m_lOptAuto.append(("START AUTOMOUNT!", "start"))
        self.m_lOptAuto.append(("CANCEL", "cancel"))

    def _automount_act(self, p_sOption):
        if p_sOption == "start":
            self._install_service()
            time.sleep(2)
        elif p_sOption == "stop":
            self._remove_service()
        elif p_sOption == "eject":
            self.eject_usb()

    def _install_service(self):
        if self._check_service_files:
            show_info('STARTING SERVICE...')
            show_info('EMULATIONSTATION MAY REBOOT...')
            os.system('sudo cp %s /etc/systemd/system/%s > /dev/null 2>&1'%(SERVICE_FILE, SERVICE_FILE_NAME))
            os.system('sudo chmod +x /etc/systemd/system/%s > /dev/null 2>&1'%SERVICE_FILE_NAME)
            os.system('sudo systemctl enable %s > /dev/null 2>&1'%SERVICE_FILE_NAME)
            os.system('sudo systemctl start %s > /dev/null 2>&1'%SERVICE_FILE_NAME)

    def _remove_service(self):
        if self._check_service_files and self.m_bServiceRun:
            show_info('STOPPING SERVICE...')
            os.system('sudo systemctl disable %s > /dev/null 2>&1'%SERVICE_FILE_NAME)
            os.system('sudo systemctl stop %s > /dev/null 2>&1'%SERVICE_FILE_NAME)
            os.system('sudo rm /etc/systemd/system/%s > /dev/null 2>&1'%SERVICE_FILE_NAME)
            os.system('sudo umount -l /home/pi/RetroPie/roms > /dev/null 2>&1')
            os.system('sudo umount -l /home/pi/RetroPie/BIOS > /dev/null 2>&1')
            os.system('sudo umount -l /opt/retropie/configs/all/emulationstation/gamelists > /dev/null 2>&1')
            self.__clean() # clean trigger files
            if self.m_bUSBMounted:
                self._restart_ES()

    def eject_usb(self):
        show_info('EJECTING USB STORAGE...')
        show_info('RESTARTING EMULATIONSTATION')
        os.system('sudo umount %s > /dev/null 2>&1' % self.m_sMountedPath[0])
        while not os.path.exists(TRG_UMNT_FILE):
            pass

    def _restart_ES(self):
        """ Restart ES if it's running """
        sOutput = commands.getoutput('ps -A')
        if 'emulationstatio' in sOutput:
            show_info('RESTARTING EMULATIONSTATION')
            commandline = "touch /tmp/es-restart "
            commandline += "&& pkill -f \"/opt/retropie"
            commandline += "/supplementary/.*/emulationstation([^.]|$)\""
            os.system(commandline)
            os.system('clear')
            time.sleep(1.5)

    # clean system
    def __clean(self):
        if os.path.exists(TRG_MNT_FILE):
            os.system("rm %s > /dev/null 2>&1" % TRG_MNT_FILE)
        if os.path.exists(TRG_UMNT_FILE):
            os.system("rm %s > /dev/null 2>&1" % TRG_UMNT_FILE)

    def __temp(self):
        if CLEAN_LOG_ONSTART:
            remove_file(LOG_PATH)
        logging.basicConfig(filename=LOG_PATH, level=__DEBUG__,
        format='[%(asctime)s] %(levelname)s - %(filename)s:%(funcName)s - %(message)s')
        
try:
    oLaunch = automount()
    oLaunch.run()
except Exception as e:
    with open(EXCEPTION_LOG, 'a') as f:
        f.write(str(e))
        f.write(traceback.format_exc())