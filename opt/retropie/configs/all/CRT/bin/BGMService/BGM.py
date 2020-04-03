#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
bgm.py.

Background music script by -krahs- for emulationstation in raspberry pi
based on original idea of BGM script version 1.03 by Livewire.

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

import os, sys, time, random, commands, subprocess, re
import logging, traceback
from pygame import mixer

MUSIC_PATH = '/opt/retropie/configs/music'
TMP_LAUNCHER_PATH = '/dev/shm'
LOG_PATH = os.path.join(TMP_LAUNCHER_PATH,"BGM.log")
EXCEPTION_LOG = os.path.join(TMP_LAUNCHER_PATH, "backtrace.log")

__VERSION__ = '0.1'
__DEBUG__ = logging.INFO # logging.ERROR
CLEAN_LOG_ONSTART = True

class BGM(object):
    m_dEmulatorsName = ["retroarch", "ags", "uae4all2", "uae4arm", "capricerpi",
                        "linapple", "hatari", "stella", "atari800", "xroar",
                        "vice", "daphne", "reicast", "pifba", "osmose", "gpsp",
                        "jzintv", "basiliskll", "mame", "advmame", "dgen",
                        "openmsx", "mupen64plus", "gngeo", "dosbox", "ppsspp",
                        "simcoupe", "scummvm", "snes9x", "pisnes", "frotz",
                        "fbzx", "fuse", "gemrb", "cgenesis", "zdoom", "eduke32",
                        "lincity", "love", "kodi", "alephone", "micropolis",
                        "openbor", "openttd", "opentyrian", "cannonball",
                        "tyrquake", "ioquake3", "residualvm", "xrick", "sdlpop",
                        "uqm", "stratagus", "wolf4sdl", "solarus", "drastic",
                        "coolcv", "PPSSPPSDL", "moonlight", "Xorg", "smw",
                        "omxplayer.bin", "wolf4sdl-3dr-v14", "wolf4sdl-gt-v14",
                        "wolf4sdl-spear", "wolf4sdl-sw-v14", "xvic",
                        "xvic cart", "xplus4", "xpet", "x128", "x64sc", "x64",
                        "prince", "fba2x", "steamlink", "pcsx-rearmed",
                        "limelight", "sdltrs", "ti99sm", "dosbox-sdl2",
                        "minivmac", "quasi88", "xm7", "yabause", "abuse",
                        "cdogs-sdl", "cgenius", "digger", "gemrb", "hcl",
                        "love", "love-0.10.2", "openblok", "openfodder", "srb2",
                        "yquake2", "amiberry", "zesarux", "dxx-rebirth",
                        "zesarux", "daphne.bin"]

    m_dCRTLaunchProcess = ["crt_launcher.py", "emulator_launcher.py",
                           "emulator_launcher_legacy.py"]

    m_sCRTProcessFound = ""

    m_iStartDelay = 0           # Value (in seconds) to delay audio start.  If
                                # you have a splash screen with audio and the 
                                # script is playing music over the top of it, 
                                # increase this value to delay the script from
                                # starting.

    m_iMaxVolume = 0.50
    m_iVolume    = 0            # Store this for later use to handle fading out.
    m_iFadeHop = 0.02
    m_iFadeSpeed = 0.05
    m_iSongPos = 0              # Position in miliseconds of song

    m_bPauseMusic = True        # If true, this will cause the script to fade 
                                # the music out and -stop- the song rather 
                                # than pause it.

    m_sMusicState = 'stop'      # Can be 'stop', 'pause' or 'play'
    m_sTrackInit = ""           # If this is not blank, this is the EXACT,
                                # CaSeSeNsAtIvE filename of the song you 
                                # always want to play first on boot.

    m_iTrackCurr = -1
    m_lTrackList = []           # List of all found songs
    m_lTrackCtrl = []           # Random sequence for playing without repeat
    m_bTrackRept = True         # If True will play all songs randomly 
                                # withouth repeat.

    def __init__(self):
        self.__temp()
        self.__clean()
        logging.info("INFO: Initializating BGM service")

        self.prepare()
        self.run() # launch, wait and cleanup

    def prepare(self):
        random.seed() #Initialize random function
        self._init_pygame()
        self._check_paths
        self._get_playlist()

    def run(self):
        self.start()
        self.cleanup()

    def start(self):
        self._loop()

    def _init_pygame(self):
        logging.info("INFO: loading pygame mixer")
        mixer.pre_init(44100, -16, 2, 1024)
        mixer.init()

    def _quit_pygame(self):
        logging.info("INFO: unloading pygame")
        mixer.quit()

    def _check_paths(self):
        """if ~ is used, change it to home directory
        (EXAMPLE: "~/BGM" to "/home/pi/BGM")"""
        global MUSIC_PATH
        if "~/" in MUSIC_PATH:
            MUSIC_PATH = os.path.expanduser(MUSIC_PATH)

    def _get_playlist(self):
        """ This will find everything that's .mp3 or .ogg """
        self.m_lTrackList = 0
        self.m_lTrackList = [track for track in os.listdir(MUSIC_PATH) \
                            if track[-4:] == ".mp3" or track[-4:] == ".ogg"]
        if not self.m_lTrackList:
            logging.info("ERROR: NO music found in /config/music")
            sys.exit(1)
        logging.info("INFO: found %s songs in music path" %
                     len(self.m_lTrackList))
        self._get_random_sequence()
        # Try to configure if exist the starting song
        if self.m_sTrackInit:
            try:
                self.m_iTrackCurr = self.m_lTrackList.index(self.m_sTrackInit)
                self.m_lTrackCtrl.append(self.m_iTrackCurr)
                logging.info("INFO: found starting song \"%s\" in list" %
                             self.m_sTrackInit)
            except:
                logging.info("INFO: can't locate found starting song \"%s\" in list" \
                             % self.m_sTrackInit)

    def _get_random_sequence(self):
        # Create random order for reproduction
        logging.info("INFO: generating random track sequence db")
        self.m_lTrackCtrl = range(len(self.m_lTrackList))
        random.shuffle(self.m_lTrackCtrl)        

    def music_start(self):
        if not mixer.get_init():
            self._init_pygame()
        if not mixer.music.get_busy():
            if self.m_sMusicState == 'play':
                self.m_iSongPos = 0
            self._seek_track()
            mixer.music.play(0, int(self.m_iSongPos))
            logging.info("INFO: resuming music time at {%ss}" % self.m_iSongPos)
            self._fade_in()
        self.m_sMusicState = 'play'

    def music_stop(self, p_bRestart = m_bPauseMusic):
        """
        You can change stop mode in function, by default will take
        value from m_bPauseMusic, but you can change for stop
        instead of pause on ES exiting.

        """
        if mixer.music.get_busy():
            self._fade_out()
            #we aren't going to resume the audio, so stop it outright.
            mixer.music.stop()
            if p_bRestart:
                self.m_sMusicState = 'pause'
                self.m_iSongPos += mixer.music.get_pos()/1000
                logging.info("INFO: pausing music time at {%ss}" % self.m_iSongPos)
            else:
                self.m_sMusicState = 'stop'
                self.m_iSongPos = 0
            self._quit_pygame()
            logging.info("INFO: halted music as {%s}" % self.m_sMusicState)
        else:
            self.m_iSongPos = 0
            self.m_sMusicState = 'stop'

    def _seek_track(self):
        """ If music is stopped will seek for the next song """
        # If we have more than one song, choose a new one until we get one that
        # isn't what we just played.
        if len(self.m_lTrackList) > 1:
            if self.m_iSongPos == 0:
                logging.info("INFO: taking next song in sequence")
                self.m_iTrackCurr = self._next_song()
        logging.info("INFO: next song: file [%s] - seq [%s]" \
                     % (self.m_lTrackList[self.m_iTrackCurr], self.m_iTrackCurr))
        p_lTrack = os.path.join(MUSIC_PATH, self.m_lTrackList[self.m_iTrackCurr])
        mixer.music.load(p_lTrack)
        mixer.music.rewind()
        logging.info("INFO: song loaded on mixer, ready to play")
        self.m_iTrackLast = self.m_iTrackCurr

    def _next_song(self):
        """
        This function will create a database with the position number of the songs
        to check and avoid to repeat until to play all of them.
        It's possible to disable this feature changing m_bTrackRept to False.
        
        """
        if os.path.getsize(LOG_PATH) > 524288:
            open(LOG_PATH, "w").close()
            logging.info("WARNING: previous log events were cleared")
    
        if self.m_bTrackRept == False:
            p_Song = random.randint(0, len(self.m_lTrackCtrl)-1)
            logging.info("WARNING: no repeat control enabled")
            return p_Song
            
        while True:
            try:
                p_Song = self.m_lTrackCtrl.pop()
                return p_Song
            except:
                logging.info("INFO: END OF SEQUENCE, restarting reproduction")
                self._get_playlist()
                
    def _fade_out(self):
        logging.info("INFO: fading out music")
        while self.m_iVolume > 0:
            self.m_iVolume -= self.m_iFadeHop
            if self.m_iVolume < 0:
                self.m_iVolume = 0
            mixer.music.set_volume(self.m_iVolume);
            time.sleep(self.m_iFadeSpeed)

    def _fade_in(self):
        if self.m_iVolume < self.m_iMaxVolume:
            logging.info("INFO: fading in music")
            while self.m_iVolume < self.m_iMaxVolume:
                self.m_iVolume += self.m_iFadeHop;
                if self.m_iVolume > self.m_iMaxVolume:
                    self.m_iVolume = self.m_iMaxVolume
                mixer.music.set_volume(self.m_iVolume);
                time.sleep(self.m_iFadeSpeed)

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

    def _loop(self):
        """ Main program loop of BGM service"""
        while True:
            if not self._check_process("emulationstatio"):
                logging.info("INFO: ES is not running, stopping music")
                self.music_stop(True)
                self._wait_process("emulationstatio", 'start')
            if self._check_process(self.m_dEmulatorsName):
                logging.info("INFO: emulator or omxplayer found!")
                self.music_stop()
                self._wait_process(self.m_dEmulatorsName, 'stop')
            self.music_start()
            time.sleep(1)

    def cleanup(self):
        os.system('clear')
        pygame.quit()
        self.__clean()
        sys.exit()

    # clean system
    def __clean(self):
        pass

    def __temp(self):
        if CLEAN_LOG_ONSTART:
            if os.path.exists (LOG_PATH):
                os.system('rm %s' % LOG_PATH)
        logging.basicConfig(filename=LOG_PATH, level=__DEBUG__,
        format='[%(asctime)s] %(levelname)s - %(filename)s:%(funcName)s - %(message)s')

""" Load and launch BGM class for background music"""
try:
    oBackGrounMusic = BGM()
except Exception as e:
    with open(EXCEPTION_LOG, 'a') as f:
        f.write(str(e))
        f.write(traceback.format_exc())