#!/usr/bin/python3
# -*- coding: utf-8 -*-


"""
bgm.py.

Background music script by -krahs- for emulationstation in raspberry pi
based on original idea of BGM script version 1.03 by Livewire.

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

import os, sys, time, random, subprocess, re
import logging, traceback
import rpyc
from threading import Thread
from rpyc.utils.server import ThreadedServer

from pygame import mixer

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(SCRIPT_DIR + "/../"))
from main_paths import MODULES_PATH
sys.path.append(MODULES_PATH)

from launcher_module.core_paths import *
from launcher_module.file_helpers import ini_get, ini_set, ini_getlist
from launcher_module.utils import check_process, wait_process, set_procname

LOG_PATH = os.path.join(TMP_LAUNCHER_PATH,"CRT_Background_Music.log")
EXCEPTION_LOG = os.path.join(TMP_LAUNCHER_PATH, "backtrace.log")

__VERSION__ = '0.1'
__DEBUG__ = logging.INFO # logging.ERROR
CLEAN_LOG_ONSTART = True

set_procname(PNAME_BGM)

class BGM(object):
    m_lProcesses = []
    m_iStartDelay = 0           # Value (in seconds) to delay audio start.  If
                                # you have a splash screen with audio and the 
                                # script is playing music over the top of it, 
                                # increase this value to delay the script from
                                # starting.

    m_iVolume    = 0.70         # Music Volume
    m_iVolStep   = 0            # Store this for later use to handle fading out.
    m_iFadeHop   = 0.02
    m_iFadeSpeed = 0.05
    m_iSongPos   = 0            # Position in miliseconds of song
    m_iTraks     = 0            # Number of songs found in folder

    m_bStop       = False       # Force script to finish
    
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
        self.m_lProcesses.append(PNAME_LAUNCHER)
        self.m_lProcesses.append("omxplayer.bin")        
        logging.info("INFO: Initializating BGM service")

    def prepare(self):
        random.seed() #Initialize random function
        self.load_volume()
        self._init_pygame()
        self._check_paths
        self._get_playlist()

    def run(self):
        self.prepare()
        self._loop()
        self.cleanup()

    def _init_pygame(self):
        logging.info("INFO: loading pygame mixer")
        mixer.pre_init(44100, -16, 2, 4096)
        mixer.init()

    def _quit_pygame(self):
        logging.info("INFO: unloading pygame")
        mixer.quit()

    def _check_paths(self):
        """if ~ is used, change it to home directory
        (EXAMPLE: "~/BGM" to "/home/pi/BGM")"""
        global CRT_BGM_MUS_PATH
        if "~/" in CRT_BGM_MUS_PATH:
            CRT_BGM_MUS_PATH = os.path.expanduser(CRT_BGM_MUS_PATH)

    def _get_playlist(self):
        """ This will find everything that's .mp3 or .ogg """
        # clean counters
        self.m_iTrackCurr = -1
        self.m_lTrackList = []
        self.m_lTrackCtrl = []
        self.m_iTraks     = 0

        p_sMusicFolder = (" ".join(ini_getlist(CRT_UTILITY_FILE, "music_folder"))).strip()
        p_lMusicFolders = []
        self.m_sMusicFolder = None
        if p_sMusicFolder and p_sMusicFolder.lower() != "root": 
            if os.path.exists(os.path.join(CRT_BGM_MUS_PATH, p_sMusicFolder)):
                p_lMusicFolders.append(os.path.join(CRT_BGM_MUS_PATH, p_sMusicFolder))
            else: logging.info("ERROR: NO music folder [%s] found" % p_sMusicFolder)
        p_lMusicFolders.append(CRT_BGM_MUS_PATH)
        
        for path in p_lMusicFolders:
            self.m_lTrackList = 0
            self.m_lTrackList = [track for track in os.listdir(path) \
                                if track[-4:] == ".mp3" or track[-4:] == ".ogg"]
            if not self.m_lTrackList:
                logging.info("ERROR: NO music found in %s" % path)
            else:
                logging.info("INFO: found %s songs in %s" %
                         (len(self.m_lTrackList), path))
                self.m_iTraks = len(self.m_lTrackList)
                self.m_sMusicFolder = path
                break
        if not self.m_lTrackList: sys.exit(1)
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
        self.m_lTrackCtrl = list(range(len(self.m_lTrackList)))
        random.shuffle(self.m_lTrackCtrl)        

    def music_start(self):
        if not mixer.get_init():
            self._init_pygame()
        if not mixer.music.get_busy():
            if self.m_sMusicState == 'play':
                self.m_iSongPos = 0
            self._seek_track()
            mixer.music.set_volume(self.m_iVolStep)
            mixer.music.play(0, int(self.m_iSongPos))
            logging.info("INFO: resuming music time at {%ss}" % self.m_iSongPos)
            self._fade_in()
        self.m_sMusicState = 'play'

    def music_stop(self, p_bRestart = m_bPauseMusic, p_bRealStop = True):
        """
        You can change stop mode in function, by default will take
        value from m_bPauseMusic, but you can change for stop
        instead of pause on ES exiting.

        """
        try:
            if mixer.music.get_busy():
                if p_bRealStop: self._fade_out()
                #we aren't going to resume the audio, so stop it outright.
                mixer.music.stop()
                if p_bRestart:
                    self.m_sMusicState = 'pause'
                    self.m_iSongPos += mixer.music.get_pos()/1000
                    logging.info("INFO: pausing music time at {%ss}" % self.m_iSongPos)
                else:
                    self.m_sMusicState = 'stop'
                    self.m_iSongPos = 0
                logging.info("INFO: halted music as {%s}" % self.m_sMusicState)
        except:
            self.m_iSongPos = 0
            self.m_sMusicState = 'stop'
        if p_bRealStop: self._quit_pygame()

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
        while True:
            p_lTrack = os.path.join(self.m_sMusicFolder, self.m_lTrackList[self.m_iTrackCurr])
            try:
                mixer.music.load(p_lTrack)
                mixer.music.rewind()
                break
            except Exception as e:
                logging.info("ERROR: %s" % e)
                if len(self.m_lTrackList) == 1:
                    ini_set(CRT_UTILITY_FILE, "music_folder", "root")
                self.m_iTrackCurr = self._next_song()
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
        while self.m_iVolStep > 0:
            self.m_iVolStep -= self.m_iFadeHop
            if self.m_iVolStep < 0:
                self.m_iVolStep = 0
            mixer.music.set_volume(self.m_iVolStep);
            time.sleep(self.m_iFadeSpeed)

    def _fade_in(self):
        if self.m_iVolStep < self.m_iVolume:
            logging.info("INFO: fading in music")
            while self.m_iVolStep < self.m_iVolume:
                self.m_iVolStep += self.m_iFadeHop;
                if self.m_iVolStep > self.m_iVolume:
                    self.m_iVolStep = self.m_iVolume
                mixer.music.set_volume(self.m_iVolStep);
                time.sleep(self.m_iFadeSpeed)

    def change_volume(self, p_iVol):
        try:
            if mixer.music.get_busy():
                mixer.music.set_volume(p_iVol)
                logging.info("INFO: remote volume to %s" % p_iVol)
        except:
            logging.info("INFO: can't change volume %s" % p_iVol)
            pass
        self.m_iVolume = p_iVol
        self.save_volume()

    def get_volume(self):
        return self.m_iVolume

    def load_volume(self):
        if os.path.exists(CRT_UTILITY_FILE):
            vol = int(ini_get(CRT_UTILITY_FILE, "music_volume"))
            if vol: self.m_iVolume = (1.00 * vol) / 100
            
    def save_volume(self):
        ini_set(CRT_UTILITY_FILE, "music_volume", int(self.m_iVolume * 100))

    def _loop(self):
        """ Main program loop of BGM service"""
        while True:
            if self.m_bStop: break
            if not check_process("emulationstatio"):
                logging.info("INFO: ES is not running, stopping music")
                self.music_stop(True)
                wait_process("emulationstatio", 'start')
            if check_process(self.m_lProcesses):
                logging.info("INFO: emulator or omxplayer found!")
                self.music_stop()
                wait_process(self.m_lProcesses, 'stop')
            self.music_start()
            time.sleep(0.5)

    def cleanup(self):
        os.system('clear')
        pygame.quit()
        self.__clean()
        sys.exit(1)

    # clean system
    def __clean(self):
        pass

    def __temp(self):
        if CLEAN_LOG_ONSTART:
            if os.path.exists (LOG_PATH):
                os.system('rm %s' % LOG_PATH)
        logging.basicConfig(filename=LOG_PATH, level=__DEBUG__,
        format='[%(asctime)s] %(levelname)s - %(filename)s:%(funcName)s - %(message)s')

class VolBGMService(rpyc.Service):
    def on_connect(self, conn):
        pass

    def on_disconnect(self, conn):
        pass

    def exposed_load_music(self):
        oBGM._get_playlist()
        oBGM.music_stop(False, False)
        #oBGM.music_start()
        return True

    def exposed_status(self):
        return True

    def exposed_stop(self):
        oBGM.m_bStop = True

    def exposed_get_vol(self):
        return int(round(oBGM.get_volume() * 100))
        
    def exposed_get_tracks(self):
        return int(oBGM.m_iTraks)

    def exposed_change_vol(self, p_iVol):
        vol = p_iVol / 100.0
        oBGM.change_volume(vol)
        vol = int(round(oBGM.get_volume() * 100))
        return vol

""" Load and launch BGM class for background music"""
if __name__ == '__main__':
    try:
        oBGM = BGM()
        server = ThreadedServer(VolBGMService, port = CRT_BGM_PORT)
        t = Thread(target = server.start)
        t.daemon = True
        t.start()
        oBGM.run()
    except Exception as e:
        with open(EXCEPTION_LOG, 'a') as f:
            f.write(str(e))
            f.write(traceback.format_exc())