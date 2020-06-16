#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
pattern_generator.py.

Centering Pattern Utility for CRT image adjusting by Krahs

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


import os, sys, time, math
import subprocess, commands
import logging
import pygame

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(SCRIPT_DIR + "/../"))
from main_paths import MODULES_PATH
sys.path.append(MODULES_PATH)

from launcher_module.core_paths import *
from launcher_module.utils import get_screen_resolution
from launcher_module.file_helpers import *
from launcher_module.core_controls import joystick, CRT_UP, CRT_DOWN, CRT_LEFT, \
                                          CRT_RIGHT, CRT_BUTTON
from pattern_datas import *

__VERSION__ = '0.1'
__DEBUG__ = logging.INFO # logging.ERROR

TEST_MEDIA_PATH = os.path.join(CRT_ASST_PATH, "screen_center_utility")
FONT_FILE = os.path.join(CRT_FONTS_PATH, "RPGSystem.ttf")
CURSOR_SOUND_FILE = os.path.join(CRT_SOUNDS_PATH, "sys_cursor_01.ogg")
CLICK_SOUND_FILE = os.path.join(CRT_SOUNDS_PATH, "sys_click_01.ogg")

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

    m_iCurSide = 0

    m_iRES_X = 0
    m_iRES_Y = 0
    m_iMaxOffSetX = 0
    m_iMaxOffSetY = 0

    m_iVOverscan = 0
    m_iHOverscan = 0

    m_PGoJoyHandler = None
    m_PGSndCursor = None
    m_PGSndLoad = None
    m_PGoScreen = None
    m_PGpPattern = None
    m_PGoFreqIcon = None
    m_PGoFontText = None
    m_PGoFontTextSize = 16

    m_iCurrent = 0
    m_iCurrentSub = 0

    m_lInfoText = []
    m_lInfoBox = []
    m_lPattern = {"posx": 0, "posy": 0, "width": 0, "height": 0,
                  "rndimg": None, "rndpos": None}
    m_lFreqIcon = {"width": 68, "height": 28,
                  "rndimg": None, "rndpos": None}

    def __init__(self):
        self.m_oPatternDatas = datas()
        self.m_iCurSide = self.m_oPatternDatas.side()
        
    def initialize(self, m_sEnv, p_lTimings = {}):
        self.m_sEnv = m_sEnv
        self.m_lTimings = p_lTimings
        self.prepare()    
    
    def prepare(self):
        self.prepare_cfg()
        self.prepare_screen_timings()
        self.test_data_init()

    def launch(self):
        self.m_iRES_X, self.m_iRES_Y = get_screen_resolution()
        self._init_pygame()
        self.loop()
        self.save()
        self.cleanup()

    def _init_pygame(self):
        pygame.mixer.pre_init(44100, -16, 2, 1024)
        pygame.init()
        self.m_PGoJoyHandler = joystick()
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

    def _init_sounds(self):
        try:
            self.m_PGSndCursor = pygame.mixer.Sound(CURSOR_SOUND_FILE)
            self.m_PGSndLoad = pygame.mixer.Sound(CLICK_SOUND_FILE)
        except Exception as e:
            logging.error(e)

    def save(self):
        self._save_config()

    def _save_config(self):
        """
        Save main configuration on 'utility.cfg':
        offsetX, offsetY, width, height
        """
        for item in self.m_dConfigFile:
            ini = "%s_%s" % (self.m_sEnv, item)
            ini_set(CRT_UTILITY_FILE, ini, self.m_dConfigFile[item])

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
        POS_X = 0
        POS_Y = 0
        table = pygame.Surface((190, 77), pygame.SRCALPHA)
        for opt in self.m_lInfoBox: #First draw rectangles box
            pygame.draw.rect(table, opt["rndcolor"], (opt["posx"],
            opt["posy"], opt["width"], opt["height"]), opt["fill"])

        for opt in self.m_lInfoText: #Second draw text options
            table.blit(opt["rndimg"], opt["rndpos"])

        if self.m_sEnv == "system60":
            if self.m_iCurSide == 0:
                POS_X = self.m_iRES_X/2
                POS_Y = self.m_iRES_Y - 90
            elif self.m_iCurSide == 1:
                table = pygame.transform.rotate(table, -90)
                POS_X = 86
                POS_Y = self.m_iRES_Y/2
            elif self.m_iCurSide == 3:
                table = pygame.transform.rotate(table, 90)
                POS_X = self.m_iRES_X - 86
                POS_Y = self.m_iRES_Y/2
        elif self.m_sEnv == "test60":
            if self.m_iCurSide == 0:
                size = table.get_rect()
                table = pygame.transform.scale(table, (size.width*5, size.height))
                POS_X = self.m_iRES_X/2
                POS_Y = self.m_iRES_Y - 90
            elif self.m_iCurSide == 1:
                table = pygame.transform.rotate(table, -90)
                size = table.get_rect()
                table = pygame.transform.scale(table, (size.width*5, size.height))
                POS_X = 390
                POS_Y = self.m_iRES_Y/2
            elif self.m_iCurSide == 3:
                table = pygame.transform.rotate(table, 90)
                size = table.get_rect()
                table = pygame.transform.scale(table, (size.width*5, size.height))
                POS_X = self.m_iRES_X - 390
                POS_Y = self.m_iRES_Y/2
        size = table.get_rect()
        size.center = (POS_X, POS_Y)
        self.m_PGoScreen.blit(table, size)

    def draw_pattern(self):
        """ Draw main centering pattern """
        self.m_PGoScreen.blit(self.m_lPattern["rndimg"],
                              self.m_lPattern["rndpos"])
        self.m_PGoScreen.blit(self.m_lFreqIcon["rndimg"],
                              self.m_lFreqIcon["rndpos"])

    def box_info_prepare_render(self):
        """ Render all text and take position """
        for opt in self.m_lInfoText:
            opt["rndimg"] = self.box_info_text_render(opt["text"], opt["rndcolor"])
            opt["rndpos"] = self.box_info_text_render_pos(opt["rndimg"],
                                                          opt["posx"],
                                                          opt["posy"],
                                                          opt["center"])

    def box_info_text_render(self, p_sText, p_lTextColor):
        """ Function to render text """
        img = self.m_PGoFontText.render(p_sText, True, p_lTextColor)
        return img

    def box_info_text_render_pos(self, p_lRendText, p_iposx,
                                 p_iposy, p_sCenter = "center"):
        """ Function to take text position """
        pos = p_lRendText.get_rect()
        if p_sCenter == "center":
            pos.center = (p_iposx, p_iposy)
        elif p_sCenter == "midleft":
            pos.midleft = (p_iposx, p_iposy)
        elif p_sCenter == "midright":
            pos.midright = (p_iposx, p_iposy)
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
        if self.m_iCurSide == 3:
            self.m_lPattern["rndimg"] = pygame.transform.rotate(self.m_lPattern["rndimg"], 180)

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
        POS_X = 0
        POS_Y = 0
        tmp = self.m_lFreqIcon["rndimg"]
        if self.m_sEnv == "system60":
            if self.m_iCurSide == 0:
                POS_X = 270
                POS_Y = 37
            elif self.m_iCurSide == 1:
                tmp = pygame.transform.rotate(tmp, -90)
                POS_X = self.m_iRES_X - 50
                POS_Y = self.m_iRES_Y - 60
            elif self.m_iCurSide == 3:
                tmp = pygame.transform.rotate(tmp, 90)
                POS_X = 43
                POS_Y = 60
        elif self.m_sEnv == "test60":
            if self.m_iCurSide == 0:
                size = tmp.get_rect()
                tmp = pygame.transform.scale(tmp, (size.width*5, size.height))
                POS_X = 1600
                POS_Y = 30
            elif self.m_iCurSide == 1:
                tmp = pygame.transform.rotate(tmp, -90)
                size = tmp.get_rect()
                tmp = pygame.transform.scale(tmp, (size.width*5, size.height))
                POS_X = self.m_iRES_X - 150
                POS_Y = self.m_iRES_Y - 67
            elif self.m_iCurSide == 3:
                tmp = pygame.transform.rotate(tmp, 90)
                size = tmp.get_rect()
                tmp = pygame.transform.scale(tmp, (size.width*5, size.height))
                POS_X = 120
                POS_Y = 50

        size = tmp.get_rect()
        size.center = (POS_X, POS_Y)
        self.m_lFreqIcon["rndimg"] = tmp
        self.m_lFreqIcon["rndpos"] = size
        self.m_lFreqIcon["rndpos"].center = (size.center)

    def prepare_cfg(self):
        """ Take config from utility.cfg """
        self.m_dConfigFile["offsetX"] = int(ini_get(CRT_UTILITY_FILE,
                                            self.m_sEnv+"_offsetX"))
        self.m_dConfigFile["offsetY"] = int(ini_get(CRT_UTILITY_FILE,
                                            self.m_sEnv+"_offsetY"))
        self.m_dConfigFile["width"] = int(ini_get(CRT_UTILITY_FILE,
                                          self.m_sEnv+"_width"))
        self.m_dConfigFile["height"] = int(ini_get(CRT_UTILITY_FILE,
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
        if self.m_sEnv == "test60":
            #Static OffsetX if testX0 and don't need to add diff on resolution
            self.m_iMaxOffSetX = 25

            """ Get dimensions of screen and drawn pattern for centering """
            # Static 1820 pattern width for 1920x240@60hz
            self.m_dPatternAdj["PatternHSize"] = 1820 
            self.m_dPatternAdj["PatternVSize"] = self.m_lTimings["V_Res"]
            self.m_dPatternAdj["ScreenHSize"] = self.m_lTimings["H_Res"]
            self.m_dPatternAdj["ScreenVSize"] = self.m_lTimings["V_Res"]

        elif self.m_sEnv == "system60":
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
        PatternDatas, self.m_PGpPattern, self.m_PGoFreqIcon = \
        self.m_oPatternDatas.get_pattern_datas()
        for item in PatternDatas:
            self.m_lPattern[item] = PatternDatas[item]

    def loop(self):
        while True:
            self.render_test()
            self.draw_test()
            event = self.m_PGoJoyHandler.event_wait()
            if event & CRT_UP:
                if self.m_iCurSide == 0 or self.m_iCurrent == 3:
                    self.choice_change(1)
                elif self.m_iCurSide == 1: self.choice_change(4)
                elif self.m_iCurSide == 3: self.choice_change(3)
            elif event & CRT_DOWN:
                if self.m_iCurSide == 0 or self.m_iCurrent == 3:
                    self.choice_change(2)
                elif self.m_iCurSide == 1: self.choice_change(3)
                elif self.m_iCurSide == 3: self.choice_change(4)
            elif event & CRT_LEFT:
                if self.m_iCurSide == 0 or self.m_iCurrent == 3:
                    self.choice_change(3)
                elif self.m_iCurSide == 1: self.choice_change(1)
                elif self.m_iCurSide == 3: self.choice_change(2)
            elif event & CRT_RIGHT:
                if self.m_iCurSide == 0 or self.m_iCurrent == 3:
                    self.choice_change(4)
                elif self.m_iCurSide == 1: self.choice_change(2)
                elif self.m_iCurSide == 3: self.choice_change(1)
            elif event & CRT_BUTTON:
                self.m_PGSndLoad.play()
                if not self.choice_change(0):
                    #reset menu selections and exit
                    self.m_iCurrent = 0
                    self.m_iCurrentSub = 0
                    time.sleep(1)
                    return

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
                    if self.m_sEnv == "system60":
                        if self.m_dConfigFile["offsetY"] > \
                           -abs(self.m_iMaxOffSetY -
                            self.m_dConfigFile["height"]):
                            self.m_dConfigFile["offsetY"] -= 1
                            self.m_PGSndCursor.play()
                    elif self.m_sEnv == "test60":
                        if self.m_dConfigFile["offsetY"] > -self.m_iMaxOffSetY:
                            self.m_dConfigFile["offsetY"] -= 1
                            self.m_PGSndCursor.play()
                elif p_iDirection == 2: #Move to Down
                    if self.m_sEnv == "system60":
                        if self.m_dConfigFile["offsetY"] < \
                           abs(self.m_iMaxOffSetY -
                           self.m_dConfigFile["height"]):
                            self.m_dConfigFile["offsetY"] += 1
                            self.m_PGSndCursor.play()
                    elif self.m_sEnv == "test60":
                        if self.m_dConfigFile["offsetY"] < self.m_iMaxOffSetY:
                            self.m_dConfigFile["offsetY"] += 1
                            self.m_PGSndCursor.play()
                elif p_iDirection == 3: #Move to Left
                    if self.m_sEnv == "system60":
                        if self.m_dConfigFile["offsetX"] > \
                           -abs(self.m_iMaxOffSetX -
                           self.m_dConfigFile["width"]):
                            self.m_dConfigFile["offsetX"] -= 1
                            self.m_PGSndCursor.play()
                    elif self.m_sEnv == "test60":
                        if self.m_dConfigFile["offsetX"] > \
                           -(self.m_iMaxOffSetX):
                            self.m_dConfigFile["offsetX"] -= 1
                            self.m_PGSndCursor.play()
                elif p_iDirection == 4: #Move to Right
                    if self.m_sEnv == "system60":
                        if self.m_dConfigFile["offsetX"] < \
                           abs(self.m_iMaxOffSetX -
                           self.m_dConfigFile["width"]):
                            self.m_dConfigFile["offsetX"] += 1
                            self.m_PGSndCursor.play()
                    elif self.m_sEnv == "test60":
                        if self.m_dConfigFile["offsetX"] < (self.m_iMaxOffSetX):
                            self.m_dConfigFile["offsetX"] += 1
                            self.m_PGSndCursor.play()

            elif self.m_iCurrent == 1: #Change Width Pattern option
                if p_iDirection == 3: #Decrease Width
                    if self.m_sEnv == "system60":
                        if self.m_dConfigFile["width"] > -self.m_iMaxOffSetX:
                            self.m_dConfigFile["width"] -= 1
                            self.m_PGSndCursor.play()
                    elif self.m_sEnv == "test60":
                        if self.m_dConfigFile["width"] > -(self.m_iMaxOffSetX):
                            self.m_dConfigFile["width"] -= 1
                            self.m_PGSndCursor.play()
                elif p_iDirection == 4:#Increase Width
                    if self.m_sEnv == "system60":
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
                    elif self.m_sEnv == "test60":
                        if self.m_dConfigFile["width"] < (self.m_iMaxOffSetX):
                            self.m_dConfigFile["width"] += 1
                            self.m_PGSndCursor.play()

            elif self.m_iCurrent == 2: #Change Height Pattern option
                if p_iDirection == 1: #Increase Height
                    if self.m_sEnv == "system60":
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
                   if self.m_sEnv == "system60":
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
        self.m_PGoJoyHandler.quit()
        pygame.display.quit()
        pygame.quit()
        self.__clean()

    # clean system
    def __clean(self):
        pass
