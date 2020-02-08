#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
pattern_generator.py.

Centering Pattern Utility for CRT image adjusting by Krahs

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


import os, sys, time, math
import subprocess, commands
import logging
import pygame

CRT_PATH = "/opt/retropie/configs/all/CRT"
RESOURCES_PATH = os.path.join(CRT_PATH,"bin/GeneralModule")
sys.path.append(RESOURCES_PATH)

from launcher_module.core_controls import joystick, CRT_UP, CRT_DOWN, CRT_LEFT, \
                                          CRT_RIGHT, CRT_BUTTON
from launcher_module.core import CFG_VIDEOUTILITY_FILE, LOG_PATH, CFG_FIXMODES_FILE
from launcher_module.core_paths import *
from launcher_module.file_helpers import *
from pattern_datas import *

__VERSION__ = '0.1'
__DEBUG__ = logging.INFO # logging.ERROR

TEST_MEDIA_PATH = os.path.join(CRT_PATH,"bin/ScreenUtilityFiles/resources/assets/screen_center_utility")
TEST_SNDCURSOR_FILE = os.path.join(TEST_MEDIA_PATH,
                      "screen_center_utility_cursor.wav")
TEST_SNDLOAD_FILE = os.path.join(TEST_MEDIA_PATH,
                    "screen_center_utility_load.wav")
FONT_FILE = os.path.join(CRTFONTS_PATH, "PetMe64.ttf")

BOOTCFG_FILE = "/boot/config.txt"
BOOTCFG_TEMP_FILE = os.path.join(TMP_LAUNCHER_PATH, "config.txt")

FPS = 0

class generate(object):
    """ virtual class for centering pattern """
    m_dConfigFile = { "offsetX": "", "offsetY": "",
                      "width": "", "height": ""}

    m_dPatternAdj = { "PatternHSize": 0, "PatternVSize": 0,
                      "ScreenHSize": 0, "ScreenVsize": 0}

    m_oPatternDatas = None

    m_lTimings = {} # To receive and storage calculated resolution to work with
    m_lResizeRes = {} # To forwad diffs timings for pattern testing

    m_sEnv = ""

    m_iMaxOffSetX = 0
    m_iMaxOffSetY = 0

    m_iVOverscan = 0
    m_iHOverscan = 0

    m_PGSndCursor = None
    m_PGSndLoad = None
    m_PGoClock = None
    m_PGoScreen = None
    m_PGpPattern = None
    m_PGoFreqIcon = None
    m_PGoFontText = None
    m_PGoFontTextSize = 0
    m_PGTextVResizer = 0
    m_PGTextHResizer = 0

    m_iCurrent = 0
    m_iCurrentSub = 0

    m_lInfoText = []
    m_lInfoBox = []
    m_lPattern = {"posx": 0, "posy": 0, "width": 0, "height": 0,
                  "rndimg": None, "rndpos": None}
    m_lFreqIcon = {"posx": 0, "posy": 0, "width": 0, "height": 0,
                  "rndimg": None, "rndpos": None}

    def __init__(self):
        self.m_oPatternDatas = datas()
        self.m_PGoJoyHandler = joystick()
        
    def initialize(self, m_sEnv, p_lTimings = {}):
        self.m_sEnv = m_sEnv
        self.m_lTimings = p_lTimings
        self.prepare()    
    
    def prepare(self):
        self.prepare_cfg()
        self.prepare_screen_timings()
        self.prepare_test_font()
        self.test_data_init()

    def launch(self):
        self._init_pygame()
        self.render_test()
        self.draw_test()
        self.loop()
        self.save()
        self.cleanup()

    def _init_pygame(self):
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()
        self.m_PGoClock = pygame.time.Clock()
        self.m_PGoJoyHandler.find_joy()
        self._init_screen()
        self._init_sounds()

    def _init_screen(self):
        pygame.display.init()
        pygame.font.init()
        pygame.mouse.set_visible(0)
        self.m_PGoFontText = pygame.font.Font(FONT_FILE,
                                              self.m_PGoFontTextSize)
        self.m_PGoScreen = pygame.display.set_mode((self.m_dPatternAdj["ScreenHSize"],
                                                    self.m_dPatternAdj["ScreenVSize"]),
                                                    pygame.FULLSCREEN)

    def prepare_test_font(self):
        """
        Default size font is 8 but need to be resized on ingame test because
        of superresolution
        """
        self.m_PGoFontTextSize = 8
        if self.m_sEnv == "test60" or self.m_sEnv == "test50":
            self.m_PGTextVResizer = 9 #Need to resize font at 1920x240@60hz
            self.m_PGTextHResizer = 27 #Need to resize font at 1920x240@60hz

    def _init_sounds(self):
        try:
            self.m_PGSndCursor = pygame.mixer.Sound(TEST_SNDCURSOR_FILE)
            self.m_PGSndLoad = pygame.mixer.Sound(TEST_SNDLOAD_FILE)
        except Exception as e:
            logging.error(e)

    def save(self):
        self._save_config()
        p_oSaveBoot = saveboot()
        p_oSaveBoot.save()

    def _save_config(self):
        """
        Save main configuration on 'utility.cfg':
        offsetX, offsetY, width, height
        """
        for item in self.m_dConfigFile:
            modify_line(CFG_VIDEOUTILITY_FILE, "%s_%s" % (self.m_sEnv, item),
                        "%s_%s %s" %
                        (self.m_sEnv, item, self.m_dConfigFile[item]))

    def test_data_init(self):
        """ Initialize option text and other dynamic datas """
        self.m_oPatternDatas.run(self.m_dPatternAdj,
                                 self.m_dConfigFile, self.m_sEnv)
        self.m_lInfoText, self.m_lInfoBox = self.m_oPatternDatas.get_info_datas()
        self.pattern_init_size_position()

    def render_test(self):
        """ Prepare all test elements """
        self.box_info_prepare_render()
        self.pattern_prepare_render()

    def draw_test(self):
        """ Draw all test elements """
        self.m_PGoScreen.fill(BLACK)
        self.draw_pattern()
        self.draw_info_box()
        pygame.display.flip()

    def draw_info_box(self):
        for opt in self.m_lInfoBox: #First draw rectangles box
            pygame.draw.rect(self.m_PGoScreen, opt["rndcolor"], (opt["posx"],
            opt["posy"], opt["width"], opt["height"]), opt["fill"])

        for opt in self.m_lInfoText: #Second draw text options
            self.m_PGoScreen.blit(opt["rndimg"], opt["rndpos"])

    def draw_pattern(self):
        """ Draw main centering pattern """
        self.m_PGoScreen.blit(self.m_lPattern["rndimg"],
                              self.m_lPattern["rndpos"])
        self.m_PGoScreen.blit(self.m_lFreqIcon["rndimg"],
                              self.m_lFreqIcon["rndpos"])

    def box_info_prepare_render(self):
        """ Render all text and take position """
        for opt in self.m_lInfoText:
            opt["rndimg"] = self.box_info_text_render(opt["text"], 
                                                      opt["rndcolor"],
                                                      self.m_PGTextVResizer,
                                                      self.m_PGTextHResizer)
            opt["rndpos"] = self.box_info_text_render_pos(opt["rndimg"],
                                                          opt["posx"],
                                                          opt["posy"],
                                                          opt["center"])

    def box_info_text_render(self, p_sText, p_lTextColor,
                             p_iVResizer = None, p_iHResizer = None):
        """ Function to render text """
        img = self.m_PGoFontText.render(p_sText, True, p_lTextColor)
        if p_iVResizer or p_iHResizer: #Resize text, needed at 1920 H_Res
            hsize = int(len(p_sText)*p_iHResizer)
            vsize = int(p_iVResizer)
            img = pygame.transform.smoothscale(img,(hsize,vsize))
        return img

    def box_info_text_render_pos(self, p_lRendText, p_iposx,
                                 p_iposy, p_sCenter = "center"):
        """ Function to take text position """
        pos = p_lRendText.get_rect()
        if p_sCenter == "center":
            pos.center = (p_iposx, p_iposy)
        elif p_sCenter == "midleft":
            pos.midleft = (p_iposx, p_iposy)
        return pos

    def pattern_prepare_render(self):
        self.pattern_render()
        self.pattern_pos()
        self.freq_icon_render()
        self.freq_icon_pos()

    def pattern_render(self):
        self.m_lPattern["rndimg"] = pygame.image.load(self.m_PGpPattern)
        self.m_lPattern["rndimg"] = pygame.transform.smoothscale(self.m_lPattern["rndimg"],
                                    (self.m_lPattern["width"],
                                    self.m_lPattern["height"]))

    def freq_icon_render(self):
        self.m_lFreqIcon["rndimg"] = pygame.image.load(self.m_PGoFreqIcon)
        self.m_lFreqIcon["rndimg"] = pygame.transform.smoothscale(self.m_lFreqIcon["rndimg"],
                                    (self.m_lFreqIcon["width"],
                                    self.m_lFreqIcon["height"]))

    def pattern_pos(self):
        self.m_lPattern["rndpos"] = self.m_lPattern["rndimg"].get_rect()
        self.m_lPattern["rndpos"].center = (self.m_lPattern["posx"],
                                            self.m_lPattern["posy"])

    def freq_icon_pos(self):
        self.m_lFreqIcon["rndpos"] = self.m_lFreqIcon["rndimg"].get_rect()
        self.m_lFreqIcon["rndpos"].center = (self.m_lFreqIcon["posx"],
                                            self.m_lFreqIcon["posy"])

    def prepare_cfg(self):
        """ Take config from utility.cfg """
        self.m_dConfigFile["offsetX"] = int(ini_get(CFG_VIDEOUTILITY_FILE,
                                            self.m_sEnv+"_offsetX"))
        self.m_dConfigFile["offsetY"] = int(ini_get(CFG_VIDEOUTILITY_FILE,
                                            self.m_sEnv+"_offsetY"))
        self.m_dConfigFile["width"] = int(ini_get(CFG_VIDEOUTILITY_FILE,
                                          self.m_sEnv+"_width"))
        self.m_dConfigFile["height"] = int(ini_get(CFG_VIDEOUTILITY_FILE,
                                           self.m_sEnv+"_height"))

    def prepare_screen_timings(self):
        #Detects MAX Offsets and prepare data to add to timings resolution
        #Vertical adjusting
        if self.m_lTimings["V_BP"] > self.m_lTimings["V_FP"]:
            self.m_iMaxOffSetY = self.m_lTimings["V_FP"] - 1
        else:
            self.m_iMaxOffSetY = self.m_lTimings["V_BP"] - 1

        #Adding vert diff timings for change resolution
        self.m_lResizeRes["V_Res"] = 2*self.m_iMaxOffSetY
        self.m_lResizeRes["V_BP"] = -self.m_iMaxOffSetY
        self.m_lResizeRes["V_FP"] = -self.m_iMaxOffSetY

        """ Horizontal adjusting """
        if self.m_lTimings["H_BP"] > self.m_lTimings["H_FP"]:
            self.m_iMaxOffSetX = self.m_lTimings["H_FP"] - 1
        else:
            self.m_iMaxOffSetX = self.m_lTimings["H_BP"] - 1

        #Adding hor diff timings for change resolution
        if self.m_sEnv == "test60" or self.m_sEnv == "test50":
            #Static OffsetX if testX0 and don't need to add diff on resolution
            self.m_iMaxOffSetX = 25

            """ Get dimensions of screen and drawn pattern for centering """
            # Static 1820 pattern width for 1920x240@60hz
            self.m_dPatternAdj["PatternHSize"] = 1820 
            self.m_dPatternAdj["PatternVSize"] = self.m_lTimings["V_Res"]
            self.m_dPatternAdj["ScreenHSize"] = self.m_lTimings["H_Res"]
            self.m_dPatternAdj["ScreenVSize"] = self.m_lTimings["V_Res"]

        elif self.m_sEnv == "system60" or self.m_sEnv == "system50":
            self.m_lResizeRes["H_Res"] = 2*self.m_iMaxOffSetX
            self.m_lResizeRes["H_BP"] = -self.m_iMaxOffSetX
            self.m_lResizeRes["H_FP"] = -self.m_iMaxOffSetX

            """ Get dimensions of screen and drawn pattern for centering """
            self.m_dPatternAdj["PatternHSize"] = self.m_lTimings["H_Res"]
            self.m_dPatternAdj["PatternVSize"] = self.m_lTimings["V_Res"]
            self.m_dPatternAdj["ScreenHSize"] = self.m_lTimings["H_Res"] +\
                                                self.m_lResizeRes["H_Res"]
            self.m_dPatternAdj["ScreenVSize"] = self.m_lTimings["V_Res"] +\
                                                self.m_lResizeRes["V_Res"]

    def get_diff_timings(self):
        #Return diff calculated timings to apply on the fly first time
        return self.m_lResizeRes

    def pattern_init_size_position(self):
        """
        Get:
        'PatternDatas': Pattern size and coordinates
        'm_PGpPattern': Path to pattern image
        """
        PatternDatas, IconDatas, self.m_PGpPattern, self.m_PGoFreqIcon = \
        self.m_oPatternDatas.get_pattern_datas()
        for item in PatternDatas:
            self.m_lPattern[item] = PatternDatas[item]
        for item in IconDatas:
            self.m_lFreqIcon[item] = IconDatas[item]

    def loop(self):
        while True:
            event = self.m_PGoJoyHandler.event_wait()
            if event & CRT_UP:
                self.choice_change(1)
            elif event & CRT_DOWN:
                self.choice_change(2)
            elif event & CRT_LEFT:
                self.choice_change(3)
            elif event & CRT_RIGHT:
                self.choice_change(4)
            elif event & CRT_BUTTON:
                self.m_PGSndLoad.play()
                if not self.choice_change(0):
                    #reset menu selections and exit
                    self.m_iCurrent = 0
                    self.m_iCurrentSub = 0
                    time.sleep(1)
                    return
            self.render_test()
            self.draw_test()

    def choice_change(self, p_iDirection = 0):
        if p_iDirection == 0: # Button pressed, move through the options
            #Increase option 0 -> 1 -> 2 -> 3 -> 0...
            if self.m_iCurrent == 3: #Last option, start from option #0
                if self.m_iCurrentSub == 0:
                    self.m_iCurrent = 0
                if self.m_iCurrentSub == 1:
                    return False
            else:
                self.m_iCurrent += 1

        else: # Direction pressed
            if self.m_iCurrent == 0: #Move Pattern option
                if p_iDirection == 1: #Move to Up
                    if self.m_sEnv == "system50" or self.m_sEnv == "system60":
                        if self.m_dConfigFile["offsetY"] > \
                           -abs(self.m_iMaxOffSetY -
                            self.m_dConfigFile["height"]):
                            self.m_dConfigFile["offsetY"] -= 1
                            self.m_PGSndCursor.play()
                    elif self.m_sEnv == "test50" or self.m_sEnv == "test60":
                        if self.m_dConfigFile["offsetY"] > -self.m_iMaxOffSetY:
                            self.m_dConfigFile["offsetY"] -= 1
                            self.m_PGSndCursor.play()
                elif p_iDirection == 2: #Move to Down
                    if self.m_sEnv == "system50" or self.m_sEnv == "system60":
                        if self.m_dConfigFile["offsetY"] < \
                           abs(self.m_iMaxOffSetY -
                           self.m_dConfigFile["height"]):
                            self.m_dConfigFile["offsetY"] += 1
                            self.m_PGSndCursor.play()
                    elif self.m_sEnv == "test50" or self.m_sEnv == "test60":
                        if self.m_dConfigFile["offsetY"] < self.m_iMaxOffSetY:
                            self.m_dConfigFile["offsetY"] += 1
                            self.m_PGSndCursor.play()
                elif p_iDirection == 3: #Move to Left
                    if self.m_sEnv == "system50" or self.m_sEnv == "system60":
                        if self.m_dConfigFile["offsetX"] > \
                           -abs(self.m_iMaxOffSetX -
                           self.m_dConfigFile["width"]):
                            self.m_dConfigFile["offsetX"] -= 1
                            self.m_PGSndCursor.play()
                    elif self.m_sEnv == "test50" or self.m_sEnv == "test60":
                        if self.m_dConfigFile["offsetX"] > \
                           -(self.m_iMaxOffSetX):
                            self.m_dConfigFile["offsetX"] -= 1
                            self.m_PGSndCursor.play()
                elif p_iDirection == 4: #Move to Right
                    if self.m_sEnv == "system50" or self.m_sEnv == "system60":
                        if self.m_dConfigFile["offsetX"] < \
                           abs(self.m_iMaxOffSetX -
                           self.m_dConfigFile["width"]):
                            self.m_dConfigFile["offsetX"] += 1
                            self.m_PGSndCursor.play()
                    elif self.m_sEnv == "test50" or self.m_sEnv == "test60":
                        if self.m_dConfigFile["offsetX"] < (self.m_iMaxOffSetX):
                            self.m_dConfigFile["offsetX"] += 1
                            self.m_PGSndCursor.play()

            elif self.m_iCurrent == 1: #Change Width Pattern option
                if p_iDirection == 3: #Decrease Width
                    if self.m_sEnv == "system50" or self.m_sEnv == "system60":
                        if self.m_dConfigFile["width"] > -self.m_iMaxOffSetX:
                            self.m_dConfigFile["width"] -= 1
                            self.m_PGSndCursor.play()
                    elif self.m_sEnv == "test50" or self.m_sEnv == "test60":
                        if self.m_dConfigFile["width"] > -(self.m_iMaxOffSetX):
                            self.m_dConfigFile["width"] -= 1
                            self.m_PGSndCursor.play()
                elif p_iDirection == 4:#Increase Width
                    if self.m_sEnv == "system50" or self.m_sEnv == "system60":
                        if self.m_dConfigFile["width"] < self.m_iMaxOffSetX:
                            self.m_dConfigFile["width"] += 1
                            if abs(self.m_dConfigFile["offsetX"]) > \
                               (self.m_iMaxOffSetX -
                               abs(self.m_dConfigFile["width"])):
                                if self.m_dConfigFile["offsetX"] < 0:
                                    self.m_dConfigFile["offsetX"] += 1
                                elif self.m_dConfigFile["offsetX"] > 0:
                                    self.m_dConfigFile["offsetX"] -= 1
                            self.m_PGSndCursor.play()
                    elif self.m_sEnv == "test50" or self.m_sEnv == "test60":
                        if self.m_dConfigFile["width"] < (self.m_iMaxOffSetX):
                            self.m_dConfigFile["width"] += 1
                            self.m_PGSndCursor.play()

            elif self.m_iCurrent == 2: #Change Height Pattern option
                if p_iDirection == 1: #Increase Height
                    if self.m_sEnv == "system50" or self.m_sEnv == "system60":
                        if self.m_dConfigFile["height"] < self.m_iMaxOffSetY:
                            self.m_dConfigFile["height"] += 1
                            if abs(self.m_dConfigFile["offsetY"]) > \
                               (self.m_iMaxOffSetY -
                               abs(self.m_dConfigFile["height"])):
                                if self.m_dConfigFile["offsetY"] < 0:
                                    self.m_dConfigFile["offsetY"] += 1
                                elif self.m_dConfigFile["offsetY"] > 0:
                                    self.m_dConfigFile["offsetY"] -= 1
                            self.m_PGSndCursor.play()

                elif p_iDirection == 2: #Decrease Height
                   if self.m_sEnv == "system50" or self.m_sEnv == "system60":
                        if self.m_dConfigFile["height"] > -self.m_iMaxOffSetY:
                            self.m_dConfigFile["height"] -= 1
                            self.m_PGSndCursor.play()

            elif self.m_iCurrent == 3: #Try again or EXIT option
                if p_iDirection == 1: #Try again
                    self.m_iCurrentSub = 0
                    self.m_PGSndCursor.play()
                elif p_iDirection == 2: #EXIT
                    self.m_iCurrentSub = 1
                    self.m_PGSndCursor.play()

        self.update_datas()
        return True

    def update_datas(self):
        self.m_oPatternDatas.pass_menu_options(self.m_iCurrent,
                                               self.m_iCurrentSub)
        self.m_lInfoText, self.m_lInfoBox = \
        self.m_oPatternDatas.update(self.m_iMaxOffSetX, self.m_iMaxOffSetY)
        self.pattern_init_size_position() #Need to calculate every

    # cleanup code
    def cleanup(self):
        pygame.display.quit()
        pygame.quit()
        self.__clean()

    # clean system
    def __clean(self):
        pass

class saveboot(object):
    """ virtual class save config.txt system resolution """
    m_dConfigFile = { "offsetX": "", "offsetY": "",
                      "width": "", "height": ""}
    m_lBootTimings = [] # To calculate system resolution on boot.txt

    m_lResizeRes = [] # To forwad diffs timings for pattern testing
    m_sEnv = ""

    def __init__(self, p_dConfigFile = None):
        self._prepare(p_dConfigFile)

    def _prepare(self, p_dConfigFile = None):
        self._get_boot_timing()
        if not p_dConfigFile:
            self._prepare_cfg()
            logging.info("INFO: taking custom parameters from utility.cfg")
        else:
            self.m_dConfigFile = p_dConfigFile
            logging.info("INFO: custom parameters passed to function")

        logging.info("INFO: OffsetX: %s, OffsetY: %s, Width: %s and Height: %s"%
        (self.m_dConfigFile["offsetX"],self.m_dConfigFile["offsetY"],
         self.m_dConfigFile["width"], self.m_dConfigFile["height"]))

    def _get_boot_timing(self):
        """ Take current system base timings from utility.cfg"""
        self.m_sEnv = ini_get(CFG_VIDEOUTILITY_FILE, "default")
        self.m_lBootTimings = ini_getlist(CFG_VIDEOUTILITY_FILE,
                                          "%s_timings" % self.m_sEnv)
        self.m_lBootTimings = map(int, self.m_lBootTimings)
        if not self._apply_fix_tv():
            logging.info("INFO: not fix tv to apply")
        logging.info("INFO: default system resolution: %s"%self.m_sEnv)

    def _apply_fix_tv(self):
        sSelected = ini_get(CFG_FIXMODES_FILE, "mode_default")
        if not sSelected or sSelected.lower() == "default":
            return False
        DiffTimings = ini_getlist(CFG_FIXMODES_FILE, 
                                  "%s_%s"%(sSelected, self.m_sEnv))
        DiffTimings = map(int, DiffTimings)
        if len(DiffTimings) != 17: #If not 17 timings, not valid
            return False
        i = 0
        for timing in DiffTimings: #SUM TV Fix to main timings
            self.m_lBootTimings[i] += DiffTimings[i]
            i += 1
        logging.info("INFO: resolution + MODE: %s"%self.m_lBootTimings)
        return True

    def _prepare_cfg(self):
        """ Take config from utility.cfg """
        self.m_dConfigFile["offsetX"] = int(ini_get(CFG_VIDEOUTILITY_FILE,
                                                    self.m_sEnv+"_offsetX"))
        self.m_dConfigFile["offsetY"] = int(ini_get(CFG_VIDEOUTILITY_FILE,
                                                    self.m_sEnv+"_offsetY"))
        self.m_dConfigFile["width"] = int(ini_get(CFG_VIDEOUTILITY_FILE,
                                                  self.m_sEnv+"_width"))
        self.m_dConfigFile["height"] = int(ini_get(CFG_VIDEOUTILITY_FILE,
                                                   self.m_sEnv+"_height"))

    def save(self):
        """ Save on boot.txt system timings """
        if self._boot_timing_calculation():
            self._write_boot_timing()
        self.cleanup()

    def _boot_timing_calculation(self):
        #This function will check if a valid timing set result of applying
        #offsetX, offsetY, width and height for config.txt system file.
        #check01 must be identical to check03 and check02 to check04.
        #If calculation is OK will return True, if not False.
        #[H_Res] = self.m_lBootTimings[0]       [V_Res] = self.m_lBootTimings[5]
        #[H_BP]  = self.m_lBootTimings[4]       [V_BP]  = self.m_lBootTimings[9]
        #[H_FP]  = self.m_lBootTimings[2]       [V_FP]  = self.m_lBootTimings[7]

        #Calculation of check01 & check02 on utility.cfg timings + MODES
        check01 = self.m_lBootTimings[0] + self.m_lBootTimings[4] + \
                  self.m_lBootTimings[2]
        check02 = self.m_lBootTimings[5] + self.m_lBootTimings[9] + \
                  self.m_lBootTimings[7]

        #Apply width to timings
        if self.m_dConfigFile["width"] < 0:
            self.m_lBootTimings[0] -= abs(2*self.m_dConfigFile["width"])
            self.m_lBootTimings[4] += abs(self.m_dConfigFile["width"])
            self.m_lBootTimings[2] += abs(self.m_dConfigFile["width"])
        else:
            self.m_lBootTimings[0] += abs(2*self.m_dConfigFile["width"])
            self.m_lBootTimings[4] -= abs(self.m_dConfigFile["width"])
            self.m_lBootTimings[2] -= abs(self.m_dConfigFile["width"])

        #Apply height to timings
        if self.m_dConfigFile["height"] < 0:
            self.m_lBootTimings[5] -= abs(2*self.m_dConfigFile["height"])
            self.m_lBootTimings[9] += abs(self.m_dConfigFile["height"])
            self.m_lBootTimings[7] += abs(self.m_dConfigFile["height"])
        else:
            self.m_lBootTimings[5] += abs(2*self.m_dConfigFile["height"])
            self.m_lBootTimings[9] -= abs(self.m_dConfigFile["height"])
            self.m_lBootTimings[7] -= abs(self.m_dConfigFile["height"])

        #Apply offsetX to timings
        if self.m_dConfigFile["offsetX"] < 0:
            self.m_lBootTimings[4] -= abs(self.m_dConfigFile["offsetX"])
            self.m_lBootTimings[2] += abs(self.m_dConfigFile["offsetX"])
        else:
            self.m_lBootTimings[4] += abs(self.m_dConfigFile["offsetX"])
            self.m_lBootTimings[2] -= abs(self.m_dConfigFile["offsetX"])

        #Apply offsetY to timings
        if self.m_dConfigFile["offsetY"] < 0:
            self.m_lBootTimings[9] -= abs(self.m_dConfigFile["offsetY"])
            self.m_lBootTimings[7] += abs(self.m_dConfigFile["offsetY"])
        else:
            self.m_lBootTimings[9] += abs(self.m_dConfigFile["offsetY"])
            self.m_lBootTimings[7] -= abs(self.m_dConfigFile["offsetY"])

        #Calculation of check03 & check04 on utility.cfg timings + MODES + CENTERING
        check03 = self.m_lBootTimings[0] + self.m_lBootTimings[4] + \
                  self.m_lBootTimings[2]
        check04 = self.m_lBootTimings[5] + self.m_lBootTimings[9] + \
                  self.m_lBootTimings[7]

        if (check01 == check03) and (check02 == check04):
            logging.info("INFO: center and size applied correctly")
            return True
        else:
            logging.error("ERROR: can't apply center and \
                           size, check utility.cfg")
            return False

    def _write_boot_timing(self):
        #Prepare timings, convert to string
        self.m_lBootTimings = map(str, self.m_lBootTimings)
        self.m_lBootTimings = " ".join(self.m_lBootTimings)
        logging.info("INFO: calculated resolution to add in config.txt: %s"% \
                     self.m_lBootTimings)

        os.system('cp %s %s' %(BOOTCFG_FILE, BOOTCFG_TEMP_FILE))
        modify_line(BOOTCFG_TEMP_FILE, "hdmi_timings=", 
                    "hdmi_timings=%s"%self.m_lBootTimings)
        os.system('sudo cp %s %s' %(BOOTCFG_TEMP_FILE, BOOTCFG_FILE))
        logging.info("INFO: boot resolution saved at %s"%BOOTCFG_FILE)

    # cleanup code
    def cleanup(self):
        self.__clean()

    # clean system
    def __clean(self):
        os.remove(BOOTCFG_TEMP_FILE)
