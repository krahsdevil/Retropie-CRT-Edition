#!/usr/bin/python
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
import os, sys, smbus, hashlib, random
import subprocess, commands, filecmp
import logging, traceback
import time

RETROPIE_PATH = "/opt/retropie"
RETROPIECFG_PATH = os.path.join(RETROPIE_PATH, "configs")
CRTROOT_PATH = os.path.join(RETROPIECFG_PATH, "all/CRT")
CRTBIN_PATH = os.path.join(CRTROOT_PATH, "bin")
CRTASSETS_PATH = os.path.join(CRTBIN_PATH, "ScreenUtilityFiles/resources/assets")

CRTCONFIGS_PATH = os.path.join(CRTBIN_PATH, "ScreenUtilityFiles/config_files")
CRTMODES_FILE = os.path.join(CRTCONFIGS_PATH, "modes.cfg")


PI2JAMMA_PATH = os.path.join(CRTASSETS_PATH, 'driver_pi2jamma')
PI2JAMMA_BIN = 'pikeyd165'
PI2JAMMA_BIN_FILE_SRC = os.path.join(PI2JAMMA_PATH, PI2JAMMA_BIN)
PI2JAMMA_BIN_FILE_DST = os.path.join('/usr/local/bin/', PI2JAMMA_BIN)

PI2JAMMA_CFG = 'pikeyd165.conf'
PI2JAMMA_CFG_FILE_SRC = os.path.join(PI2JAMMA_PATH, PI2JAMMA_CFG)
PI2JAMMA_CFG_FILE_DST = os.path.join('/etc', PI2JAMMA_CFG)

JAMMARGBPI_MODULE = 'mk_arcade_joystick_rpi'

ES_PATH = "/opt/retropie/configs/all/emulationstation"
TMP_LAUNCHER_PATH = '/dev/shm'
BOOTCFG_FILE = "/boot/config.txt"

LOG_PATH = os.path.join(TMP_LAUNCHER_PATH,"CRT_Daemon.log")
EXCEPTION_LOG = os.path.join(TMP_LAUNCHER_PATH, "backtrace.log")

__VERSION__ = '0.1'
__DEBUG__ = logging.INFO # logging.ERROR
CLEAN_LOG_ONSTART = True

class CRTDaemon(object):
    m_iJammaCable = 0
    m_iRecoverEna = -1 # If -1 option don't exist
    m_sRecoverMod = None
    m_iDaemonCRT = -1 # If -1 option don't exist

    m_oRunBinary = None
    m_iLoadedCable = 0

    m_sBootTempFile = ""
    m_bUploadCFG = False  # If True config.txt was changed

    def __init__(self):
        self.__temp()
        logging.info("INFO: Initializating CRT Daemon")

    def run(self):
        self._loop()

    def _get_ini_base_config(self):
        self._get_boot_config_ini()
        self._create_missing_recovery_config()

    def _get_boot_config_ini(self):
        self.m_iJammaCable = 0
        self.m_iRecoverEna = -1
        self.m_sRecoverMod = None
        self.m_iDaemonCRT = -1
        p_lCheck = []
        self._clone_boot_cfg() #Copy to a temp space

        """
        Try to get jamma_cable= from config.txt
        This option will activate different drivers for pi2jamma or
        jamma-rgb-pi
        """
        p_lCheck = self._ini_get(self.m_sBootTempFile, 'jamma_cable')
        if p_lCheck[0]:
            self.m_iJammaCable = 0
            if not p_lCheck[1]: #line is not commented, getting value
                self.m_iJammaCable = int(p_lCheck[2])

        """
        Try to get crt_recovery_enabled= from config.txt
        This option will activate auto video recovery to apply MODES
        configured in ~/CRT/bin/ScreenUtilityFiles/config_files/modes.cfg
        This may help with TV video compatibility
        """
        p_lCheck = self._ini_get(self.m_sBootTempFile, 'crt_recovery_enabled')
        if p_lCheck[0]:
            self.m_iRecoverEna = 0
            if not p_lCheck[1]: #line is not commented, getting value
                self.m_iRecoverEna = int(p_lCheck[2])

        """
        Try to get crt_recovery_mode = from config.txt
        If previous option crt_recovery_enabled= is enabled, will take
        this value to change automatically in file modes.cfg.
        If not found in modes.cfg DEFAULT will be applied.
        """
        p_lCheck = self._ini_get(self.m_sBootTempFile, 'crt_recovery_mode')
        if p_lCheck[0]:
            self.m_sRecoverMod = 'DEFAULT'
            if not p_lCheck[1]:  #line is not commented, getting value
                self.m_sRecoverMod = str(p_lCheck[2].upper())

        """
        Try to get crt_daemon_enabled= from config.txt
        If found and enable, this daemon will end automatically
        """
        p_lCheck = self._ini_get(self.m_sBootTempFile, 'crt_daemon_enabled')
        if p_lCheck[0]:
            self.m_iDaemonCRT = 0
            if not p_lCheck[1]:  #line is not commented, getting value
                self.m_iDaemonCRT = int(p_lCheck[2])

    def _create_missing_recovery_config(self):
        p_bConfigs = False
        if self.m_iRecoverEna < 0:
            p_bConfigs = True
            os.system('echo \"\n# CRT Video Recovery MODES; 0=disabled; ' \
                       + '1=enabled\" >> %s' % self.m_sBootTempFile)
            os.system('echo \"crt_recovery_enabled=0\" ' + \
                      '>> %s' % self.m_sBootTempFile)
            if not self.m_sRecoverMod:
                os.system('echo \"# MODE to apply: DEFAULT/MODE1/MODE2/MODE3 ' +\
                          '(modes.cfg)\" ' +
                '>> %s' % self.m_sBootTempFile)
                os.system('echo \"crt_recovery_mode=DEFAULT\" ' + \
                          '>> %s' % self.m_sBootTempFile)

        if self.m_iDaemonCRT < 0:
            p_bConfigs = True
            os.system('echo \"\n# CRT DAEMON; 0=disabled; 1=enabled\" ' + \
                      '>> %s' % self.m_sBootTempFile)
            os.system('echo \"crt_daemon_enabled=1\" ' + \
                      '>> %s' % self.m_sBootTempFile)

        if p_bConfigs:
            #Re-check again config options in boot.txt
            logging.info("INFO: checking a second time config.txt")
            self._upload_boot_cfg()
            self._get_boot_config_ini()

    def _check_jamma_cable(self):
        if self.m_iLoadedCable != self.m_iJammaCable:
            logging.info("WARNING: Jamma config changed, killing " + \
                         "previous driver")
            self._kill_drivers()
        else:
            logging.info("INFO: Jamma cable config not changed: " + \
                         "%s" % self.m_iJammaCable)

        if self.m_iJammaCable == 1:
            self._run_pi2jamma()
        elif self.m_iJammaCable == 2:
            self._run_jamma_rgb_pi()

    def _kill_drivers(self):
        if self._kill_pi2jamma() and self._kill_jammargbpi():
            self.m_iLoadedCable = 0

    def _run_pi2jamma(self):
        """
        This function will try to launch software for
        pi2jamma cable.
        """
        if not self._check_process(PI2JAMMA_BIN):
            logging.info("INFO: Subprocess for pi2jamma NOT found, " + \
                         "try to start...")
            if not self._check_pi2jamma_files():
                return

            # Launch pi2jamma driver
            os.system('sudo chmod a+rwx /dev/uinput')
            commandline = 'sudo -s %s ' % PI2JAMMA_BIN
            commandline += '-smi -ndb -d &> /dev/null'
            self.m_oRunBinary = subprocess.Popen(commandline, shell=True)
            time.sleep(2)

            logging.info("INFO: Subproc launched: %s, " % PI2JAMMA_BIN + \
                         "PID: %s" % self.m_oRunBinary.pid)
            if self._check_process(PI2JAMMA_BIN):
                self.m_iLoadedCable = 1
                logging.info("INFO: Process %s seems " % PI2JAMMA_BIN +  \
                             "to be loaded")
        else:
            self.m_iLoadedCable = 1
            logging.info("INFO: Subprocess for pi2jamma " + \
                         "already FOUND running")

    def _check_pi2jamma_files(self):
        """ 
        pi2jamma asset of files.
        Will check if binary and config files are stored in assets
        folder of this Retropie CRT Edition to install in system if
        needed (pikeyd165 & pikeyd165.conf)
        """
        p_bCheck = True
        if not os.path.exists(PI2JAMMA_CFG_FILE_SRC):
            logging.info("WARNING: pi2jamma binary source asset " + \
                         "not found in %s" % PI2JAMMA_CFG_FILE_SRC)
            p_bCheck = False
        if not os.path.exists(PI2JAMMA_BIN_FILE_SRC):
            logging.info("WARNING: pi2jamma binary source asset " + \
                         "not found in %s" % PI2JAMMA_BIN_FILE_SRC)
            p_bCheck = False
        
        # if source files exits, check instalation
        if p_bCheck:
            self._sync_files(PI2JAMMA_BIN_FILE_SRC,
                             PI2JAMMA_BIN_FILE_DST, "x")
            self._sync_files(PI2JAMMA_CFG_FILE_SRC,
                             PI2JAMMA_CFG_FILE_DST)
        return p_bCheck

    def _sync_files(self, p_sFile1, p_sFile2, p_schmod = ""):
        # p_sFile1 = source file
        # p_sFile2 = destination file
        # p_schmod = file rigths
        p_bSync = False

        if not os.path.exists(p_sFile2): # check first if dest exists
            p_bSync = True
        else: # compare files if exists
            if not filecmp.cmp(p_sFile1, p_sFile2):
                p_bSync = True

        if p_bSync:
            logging.info("WARNING: %s don't exists " % p_sFile2 + \
                         "or was changed, synchronizing the file...")
            os.system('sudo cp \"%s\" \"%s\"' % (p_sFile1, p_sFile2))
            if p_schmod:
                logging.info("INFO: changing permissions " + \
                             "{+%s} to the file..." % p_schmod)
                os.system('chmod +%s \"%s\"' % (p_schmod, p_sFile2))
        else:
            logging.info("INFO: %s is installed" % p_sFile1)
                
    def _kill_pi2jamma(self):
        """ This function will close pi2jamma software """
        if self._check_process(PI2JAMMA_BIN):
            logging.info("INFO: Terminating subprocess with " + \
                         "PID: %s" % self.m_oRunBinary.pid)
            os.system('sudo chmod a+rwx /dev/uinput')
            commandline = 'sudo -s  %s -k ' % PI2JAMMA_BIN
            commandline += '&> /dev/null'
            os.system(commandline)
            self.m_oRunBinary = None
        return True

    def _run_jamma_rgb_pi(self):
        """ 
        This function will check the current state of neened module for
        jamma-rgb-pi.        
        """
        if self._module_loaded(JAMMARGBPI_MODULE):
            self.m_iLoadedCable = 2
            logging.info("INFO: Module driver for jamma-rgb-pi " + \
                         "already FOUND loaded")
            return
        else: # If module is not loaded
            logging.info("INFO: Module driver for jamma-rgb-pi NOT " + \
                         "found loaded, try to start...")
            # Check if mk_arcade_joystick_rpi is loaded is system
            if not self._module_exists(JAMMARGBPI_MODULE):
                logging.info("WARNING: jamma-rgb-pi module driver DON'T exists")
                return
            # Try to detect jamma-rgb-pi hardware
            if not self._i2c_check():
                logging.info("WARNING: Hardware jamma-rgb-pi NOT found")
                return
            os.system('sudo modprobe %s i2c0=0x20,0x21' % JAMMARGBPI_MODULE)
            time.sleep(2)
            if self._module_loaded(JAMMARGBPI_MODULE):
                self.m_iLoadedCable = 2
                logging.info("INFO: Module %s loaded" % JAMMARGBPI_MODULE)
            else:
                logging.info("WARNING: Can't load module: %s" \
                             % JAMMARGBPI_MODULE)

    def _kill_jammargbpi(self):
        if self._module_loaded(JAMMARGBPI_MODULE):
            logging.info("INFO: Killing %s module" % JAMMARGBPI_MODULE)
            os.system('sudo modprobe -r %s' % JAMMARGBPI_MODULE)
            if not self._module_loaded(JAMMARGBPI_MODULE):
                return True
            else:
                return False

    def _i2c_check(self):
        """ 
        This function try to detect in i2c bus 0 if any i2c device is 
        connected looking for addreses.
        """
        bus = smbus.SMBus(0)
        p_bCheck = False
        for device in range(3, 128):
            try:
                bus.read_byte(device)
                p_bCheck = True
            except:
                pass
        return p_bCheck

    def _module_exists(self, p_sModule):
        """ Return True if module exists/installed """
        sOutput = commands.getoutput('modinfo %s' % p_sModule)
        if not 'error' or not 'ERROR' in sOutput:
            return True
        return False

    def _module_loaded(self, p_sModule):
        """ Return True if module is loaded """
        sOutput = commands.getoutput('lsmod | grep %s' % p_sModule)
        if p_sModule in sOutput:
            return True
        return False

    def _modify_line(self, p_sFile, p_sLineToFind, p_sNewLine, p_bEndLine = True):
        """ This function modifies a line in a text file """
        if not os.path.isfile(p_sFile):
            return None
        with open(p_sFile, "r+") as f:
            new_file = f.readlines()
            f.seek(0) # rewind
            for line in new_file:
                if p_sLineToFind in line:
                    line = p_sNewLine
                    if p_bEndLine:
                        line += "\n"
                f.write(line) # new line
            f.truncate() # remove everything after the last write
            return True

    def _ini_get(self, p_sFile, p_sFindMask):
        """
        This function will return three values:
        p_lCheck = [value0, value1, value2]:
            value0 = True or False; True if ini value was found
            value1 = True or False; True if line is commented with '#'
            value2 = String; Value of requested ini 
        """
        p_lCheck = [False, False, None]
        if not os.path.isfile(p_sFile):
            logging.info('WARNING: %s NOT found' % p_sFile)
            return p_lCheck
        with open(p_sFile, "r") as f:
            for line in f:
                lValues = line.strip().replace(' ','').split('=')
                if p_sFindMask == lValues[0].strip('# '):
                    p_lCheck[0] = True
                    if line[:1] == '#':
                        p_lCheck[1] = True
                        logging.info('WARNING: %s is ' % p_sFindMask + \
                                     'commented or without value')
                    try:
                        p_lCheck[2] = lValues[1].strip('" ')
                        logging.info('INFO: %s=' % p_sFindMask + \
                                      '%s' % p_lCheck[2])
                    except:
                        logging.info('WARNING: %s has ' % p_sFindMask + \
                                     'not value')

        if not p_lCheck[0]:
            logging.info('WARNING: %s NOT found' % p_sFindMask)
        return p_lCheck

    def _loop(self, p_iTime = 60, p_iLoops = 5):
        """ 
        MAIN PROGRAM.
        Will be checking during 5 loops and 60 seconds per loop if any
        jamma cable is selected and apply its needed sofware.
        After cycle if no one jamma cable is detected on config.txt 
        daemon will be closed.
        """
        logging.info('INFO: starting main search cycle of ' + \
                     '{%s loops}x{%s seconds}' % (p_iLoops, p_iTime))
        iCounter = 0
        while iCounter < p_iLoops:
            self._get_ini_base_config()  # Get datas from /boot/config.txt
            self._halt_daemon()          # Check if daemon shall wait or end
            self._recovery_mode()        # If recovery is found, apply and reboot
            self._check_jamma_cable()    # Check if jamma cable is selected
            time.sleep(p_iTime)          # Wait until next cycle
            iCounter += 1
            if self.m_iLoadedCable != 0: # Keep daemon if any jamma cable
                logging.info('INFO: JAMMA CABLE FOUND; ' + \
                             'clearing search cycle')
                iCounter = 0
        logging.info('INFO: NO JAMMA CABLE FOUND after search cycle ' + \
                     'of {%s loops}x{%s seconds}; Exiting from daemon' \
                     % (p_iLoops, p_iTime))
        self._exit_daemon()

    def _halt_daemon(self):
        """
        Will wait or close daemon if one of next conditions happen
        If daemon is disabled it will do nothing, only exit.
        """
        if self.m_iDaemonCRT == 0:
            logging.info("WARNING: Closing daemon: disabled or " + \
                         "commented in /boot/config.txt")
            self._exit_daemon()
        if self._check_process('resize2fs'):
            logging.info("WARNING: Wait until resize2fs finish")
            self._wait_process('resize2fs', 'stop')

    def _recovery_mode(self):
        """
        If recovery mode is enabled in /boot/config.txt this function will
        apply the selected MODE in crt_recovery_mode. This mode must have
        profile in ~/CRT/bin/ScreenUtilityFiles/config_files/modes.cfg
        These MODES is a way to give compatibility to some TV or monitors.
        Basically are diffs to apply to the base timings to fit with with
        resolution. By default are three but is possible to create more
        following the scheme of current ones.
        """
        if self.m_iRecoverEna == 1:
            p_lCheck = self._ini_get(CRTMODES_FILE, self.m_sRecoverMod)
            if p_lCheck[0]:
                logging.info("INFO: Recovery mode {%s} " % self.m_sRecoverMod + \
                             "exist, changing in modes.cfg" )
                self._modify_line(CRTMODES_FILE, 'mode_default',
                                  'mode_default %s' % self.m_sRecoverMod.upper())
            else:
                logging.info("INFO: Recovery mode {%s} " % self.m_sRecoverMod + \
                             "NOT exist, changing to DEFAULT in modes.cfg")
                self._modify_line(CRTMODES_FILE, 'mode_default',
                                  'mode_default DEFAULT')

            # Cleaning video recovery from /boot/config.txt
            self._modify_line(self.m_sBootTempFile, 'crt_recovery_enabled',
                              'crt_recovery_enabled=0')
            self._modify_line(self.m_sBootTempFile, 'crt_recovery_mode',
                              'crt_recovery_mode=DEFAULT')

            # Upload /boot/config.txt
            self._upload_boot_cfg()

            # Create timings with MODE for system/ES in /boot/config.txt
            commandline = "/usr/bin/python /opt/retropie/configs/all/CRT"
            commandline += "/bin/ScreenUtilityFiles/bin"
            commandline += "/module_screen_center_utility"
            commandline += "/pattern_launcher.py force"
            os.system(commandline)

            self._restart_system()

    def _restart_system(self):
        """ Restart system and close ES if it's running """
        if self._check_process("emulationstatio"):
            commandline = 'sudo killall emulationstation && clear'
            os.system(commandline)
        print "CRT DAEMON WILL REBOOT THE SYSTEM NOW..."
        time.sleep(3)
        commandline = 'sudo reboot now'
        os.system(commandline)
        sys.exit()

    def _wait_process(self, p_sProcess, p_sState = 'stop',
                     p_iTimes = 1, p_iWaitScs = 1):
        """
        This function will wait to start or stop for only one process or a 
        list of them like emulators. By default will wait to start with
        p_sState parameter, but you can change it on call to 'stop'.
        If a list is passed, function will validate that at least one of
        them started or all are stopped.
        
        """
        bProcessFound = None
        bCondition = True
        logging.info("INFO: waiting to %s processes: %s"%(p_sState, p_sProcess))
        if p_sState == 'stop':
            bCondition = False
        while bProcessFound != bCondition:
            bProcessFound = self._check_process(p_sProcess, p_iTimes)
            time.sleep(p_iWaitScs)
        logging.info("INFO: wait finished")

    def _check_process(self, p_sProcess, p_iTimes = 1):
        p_bCheck = 0
        if p_sProcess == "emulationstatio": p_iTimes = 3
        
        pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
        for pid in pids:
            try:
                procname = open(os.path.join('/proc',pid,'comm'),'rb').read()
                if type(p_sProcess) is list:
                    if procname[:-1] in p_sProcess:
                        p_bCheck = p_iTimes
                        break
                elif type(p_sProcess) is str:
                    if procname[:-1] == p_sProcess:
                        p_bCheck += 1
            except IOError:
                pass
        # p_iTimes >= 1 process was found
        p_bCheck = True if p_bCheck >= p_iTimes else False 
        return p_bCheck

    def _generate_random_config_temp(self):
        self.__clean()
        p_sName = str(self._md5_file(BOOTCFG_FILE))
        p_sName += "_" + str(random.randrange(1000, 9999))
        p_sPath = os.path.join(TMP_LAUNCHER_PATH, p_sName)
        self.m_sBootTempFile = p_sPath

    def _md5_file(self, p_sFile):
        hasher = hashlib.md5()
        with open(p_sFile, 'rb') as afile:
            buf = afile.read()
            hasher.update(buf)
        return hasher.hexdigest()

    def _clone_boot_cfg(self):
        self._generate_random_config_temp()
        os.system('cp %s %s' % (BOOTCFG_FILE, self.m_sBootTempFile))
        logging.info('INFO: taking a temp copy of config.txt ' + \
                     ' at %s' % self.m_sBootTempFile)

    def _upload_boot_cfg(self):
        os.system('sudo cp %s %s' %(self.m_sBootTempFile, BOOTCFG_FILE))
        logging.info('INFO: uploading modified config.txt to /boot')

    def _exit_daemon(self):
        self.__clean()
        sys.exit()

    # clean trigger files
    def __clean(self):
        if os.path.exists (self.m_sBootTempFile):
            logging.info('INFO: deleting temp config file: ' + \
                         '%s' % self.m_sBootTempFile)
            os.system('rm "%s"' % self.m_sBootTempFile)

    def __temp(self):
        if CLEAN_LOG_ONSTART:
            if os.path.exists (LOG_PATH):
                os.system('rm "%s"' % LOG_PATH)
        logging.basicConfig(filename=LOG_PATH, level=__DEBUG__,
        format='[%(asctime)s] %(levelname)s - %(filename)s:%(funcName)s - %(message)s')

try:
    oCRTDaemon = CRTDaemon()
    oCRTDaemon.run()
except Exception as e:
    with open(EXCEPTION_LOG, 'a') as f:
        f.write(str(e))
        f.write(traceback.format_exc())
