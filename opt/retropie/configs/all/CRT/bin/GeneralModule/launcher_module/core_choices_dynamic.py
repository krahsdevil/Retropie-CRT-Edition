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

"""
### HOW TO THEME YOUR CHOICES!!

    # first get default cfg
    custom_cfg = DEFAULT_CFG

    # change some default values (see DEFAULT_CFG to see options)
    custom_cfg['font'] = "font_16.ttf"
    custom_cfg['font_size'] = 16
    custom_cfg['bgcolor'] = (80, 180, 120)

    # init class using your theme
    ch = choices(custom_cfg)

"""


import os, sys
import logging
import pygame

from .core_paths import CRT_MEDIA_PATH, CRT_ES_RES_PATH, ROTMODES_TATE1_FILE, \
                        ROTMODES_TATE3_FILE
from .screen import CRT
from .core_controls import joystick, CRT_UP, CRT_DOWN, CRT_BUTTON

# BASE COLORS
BG_COLOR = (128, 120, 211)
BG_COLOR_SEL = (180, 80, 100)

# BG TYPES
BG_FLAT = 1
BG_DEGRADE = 2


DEFAULT_CFG = {
    'style': "skin_choice_dynamic",

    'border': "border.png",
    'border_corner': "border_corner.png",
    'border_height': 8,

    'cursor': "cursor.png",
    'font': "font.ttf",
    'font_size': 16,
    'snd_cursor': "cursor.wav",
    'snd_load': "load.wav",

    'bgcolor': BG_COLOR,
    'bgcolor_selected': BG_COLOR_SEL,
    'bgtype': BG_DEGRADE,
}

# internal
C_BLACK = pygame.Color(  0,   0,   0)
C_WHITE = pygame.Color(255, 255, 255)
FPS = 30

class choices(object):
    """show a selector with choices using pygame."""

    m_oJoyHandler = None
    m_lOpts = []
    m_iCurrent = 0
    m_iUpdateScreen = 1
    m_bShowCursor = True
    m_sSkinPath = ""
    m_SndCursor = None
    m_SndLoad = None
    m_lResolutionXY = ()
    m_oScreen = None
    m_oFont = None
    m_oTitle = None
    m_oTable = None
    m_iRotate = 0

    def __init__(self, p_dChoices = DEFAULT_CFG):
        self._check_current_es_side()
        self.dCFG = p_dChoices.copy()
        self.m_sSkinPath = os.path.join(CRT_MEDIA_PATH, self.dCFG['style'])
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()
        self._init_screen()
        self._init_sounds()

    def _init_screen(self):
        pygame.display.init()
        pygame.font.init()
        pygame.mouse.set_visible(0)

        # gfx
        self.m_oFontText = pygame.font.Font(os.path.join(self.m_sSkinPath,
            self.dCFG['font']),
            self.dCFG['font_size'])
        self.dCFG['font_line'] = self.m_oFontText.get_linesize()

        self.be = pygame.image.load(os.path.join(self.m_sSkinPath, self.dCFG['border_corner']))
        self.b = pygame.image.load(os.path.join(self.m_sSkinPath, self.dCFG['border']))
        self.c = pygame.image.load(os.path.join(self.m_sSkinPath, self.dCFG['cursor']))
        self.c = pygame.transform.rotate(self.c, self.m_iRotate)

        # screen
        self.m_lResolutionXY = CRT.get_screen_resolution()
        self.m_lScreenCenter = map(lambda x: x/2, self.m_lResolutionXY)
        self.m_oScreen = pygame.display.set_mode(self.m_lResolutionXY, pygame.FULLSCREEN)

    def _init_sounds(self):
        try:
            self.m_SndCursor = pygame.mixer.Sound(os.path.join(self.m_sSkinPath, self.dCFG['snd_cursor']))
            self.m_SndLoad = pygame.mixer.Sound(os.path.join(self.m_sSkinPath, self.dCFG['snd_load']))
        except Exception as e:
            logging.error(e)

    def _add_opt(self, p_lOptPath):
        try:
            dData = {}
            dData['text'], dData['value'] = p_lOptPath
            dData['img'] = self.text_render(dData['text'], C_WHITE, C_BLACK)
            self.m_lOpts.append(dData)
        except Exception as e:
            logging.error(e)

    def set_title(self, p_sTitle, p_lColor = C_WHITE, p_lShadowColor = C_BLACK):
        self.m_oTitle = self.text_render(p_sTitle, p_lColor, p_lShadowColor)
        self.m_iTitleSize = self.dCFG['font_line'] + (self.dCFG['border_height'] * 2) + 1

    def _reset_data(self):
        self.m_lOpts = []
        self.m_oTitle = None

    def load_choices(self, p_lRecevOpts):
        self.m_lOpts = []
        for opt in p_lRecevOpts:
            logging.info(str(opt))
            self._add_opt(opt)
        self._table_render()

    def _table_create(self):
        self.m_oTable = Table(0, self.dCFG['font_line'] * len(self.m_lOpts))
        if self.m_oTitle:
            self.m_oTable.width = self.m_oTitle.get_width()
            self.m_oTable.height += self.m_iTitleSize
        for opt in self.m_lOpts:
            if opt['img'].get_width() > self.m_oTable.width:
                self.m_oTable.width = opt['img'].get_width()
        self.m_oTable.width += self.dCFG['border_height'] * 4
        self.m_oTable.height += self.dCFG['border_height'] * 2
        self.m_oTable.img = pygame.Surface(self.m_oTable.get_size())
        self.m_oTable.fill(self.dCFG['bgcolor'], self.dCFG['bgtype'])

    def _table_border(self):
        top = 0
        # title
        if self.m_oTitle:
            bottom = self.m_iTitleSize - self.be.get_height() - 1
            self._draw_border(top, bottom)
            top = bottom + self.be.get_height() + 1
        bottom = self.m_oTable.img.get_height() - self.be.get_height()
        self._draw_border(top, bottom)

    def _draw_border(self, top, bottom):
        w = self.be.get_width()
        h = self.be.get_height()
        right = self.m_oTable.img.get_width() - w

        # edges
        tmp = pygame.transform.flip(self.b, 0, 1)
        for x in range(w, right):
            self.m_oTable.img.blit(self.b, (x, top))
            self.m_oTable.img.blit(tmp, (x, bottom))
        tmp = pygame.transform.rotate(self.b, 90)
        tmp2 = pygame.transform.rotate(self.b, -90)
        for y in range(h + top, bottom):
            self.m_oTable.img.blit(tmp, (0, y))
            self.m_oTable.img.blit(tmp2, (right, y))

        # corners
        self.m_oTable.img.blit(self.be, (0, top))
        tmp = pygame.transform.rotate(self.be, -90)
        self.m_oTable.img.blit(tmp, (right, top))
        tmp = pygame.transform.rotate(self.be, 180)
        self.m_oTable.img.blit(tmp, (right, bottom))
        tmp = pygame.transform.rotate(self.be, 90)
        self.m_oTable.img.blit(tmp, (0, bottom))

    def _table_render(self):
        self._table_create()
        self._table_border()
        line = self.dCFG['border_height']

        # title
        if self.m_oTitle:
            rect = self.m_oTitle.get_rect()
            rect.x = (self.m_oTable.width - self.m_oTitle.get_width()) / 2
            rect.y = line
            self.m_oTable.img.blit(self.m_oTitle, rect)
            line += self.m_iTitleSize

        for opt in self.m_lOpts:
            rect = opt['img'].get_rect()
            rect.x = 16
            rect.top = line
            self.m_oTable.img.blit(opt['img'], rect)
            line += self.dCFG['font_line']
            
        # center the whole image
        self.m_oTable.img = pygame.transform.rotate(self.m_oTable.img, self.m_iRotate)
        rect = self.m_oTable.img.get_rect()
        rect.center = self.m_lScreenCenter
        self.m_oTable.position = rect

    def text_render(self, p_sText, p_lTextColor, p_lShadowColor = None, p_iShadowDrop = 1, p_bUseBiggerFont = True):
        img = self.m_oFontText.render(p_sText, False, p_lTextColor)
        rect = img.get_rect()
        sf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        if p_lShadowColor:
            shadow = self.m_oFontText.render(p_sText, False, p_lShadowColor)
            shadow_rect = img.get_rect()
            shadow_rect.x += p_iShadowDrop
            shadow_rect.y += p_iShadowDrop
            sf.blit(shadow, shadow_rect)
        sf.blit(img, rect)
        return sf

    def cleanup(self):
        self._clean_on_finish()

    def show(self, p_iTimeOut = 2000, p_bShowCursor = False):
        self.m_iUpdateScreen = 1
        self.m_bShowCursor = p_bShowCursor
        self._update_screen()
        pygame.time.delay(p_iTimeOut)
        self._clean_on_finish()

    def run(self):
        self.m_oJoyHandler = joystick() # Load Joystick
        self._update_screen()
        result = self.loop()
        self._clean_on_finish()
        return result

    def loop(self):
        while True:
            event = self.m_oJoyHandler.event_wait()
            #logging.info("event %s" % str(event))
            if event & CRT_UP:
                self.m_SndCursor.play()
                self._choice_change(-1)
            if event & CRT_DOWN:
                self.m_SndCursor.play()
                self._choice_change(1)
            if event & CRT_BUTTON:
                self.m_SndLoad.play()
                return self._choice_select()
            if self.m_iUpdateScreen:
                self._update_screen()

    def _choice_select(self):
        result = self.m_lOpts[self.m_iCurrent]['value']
        text = self.m_lOpts[self.m_iCurrent]['text']
        text = self._clean_text(text)
        self._reset_data()
        # just create a new simple table to show the result
        self.dCFG['bgcolor'] = self.dCFG['bgcolor_selected']
        self.load_choices([("SELECTED: %s" % text, 0)])
        self.m_oScreen.blit(self.m_oTable.img, self.m_oTable.position)
        pygame.display.flip()
        # wait end sound
        pygame.time.delay(2000)
        logging.info("selected: %s" % str(result))
        return result

    def _clean_text(self, text):
        # Clean not wanted characters or strings in output message
        clean = ('[ ] ', '[*] ', '[ ]', '[*]')
        for char in clean:
            text = text.replace(char, "")
        return text

    # TODO: allow another directions, atm is a simple up to down cursor
    def _choice_change(self, p_iDirection):
        self.m_iCurrent += p_iDirection
        if self.m_iCurrent >= len(self.m_lOpts):
            self.m_iCurrent = 0
        elif self.m_iCurrent < 0:
            self.m_iCurrent = len(self.m_lOpts) - 1
        self.m_iUpdateScreen = 1

    def _update_screen(self):
        self._draw_screen(self.m_iCurrent)
        self.m_iUpdateScreen = 0

    def _draw_screen(self, p_iSelect):
        self.m_oScreen.fill(C_BLACK)
        self.m_oScreen.blit(self.m_oTable.img, self.m_oTable.position)

        if self.m_iRotate == 90:
            POS_X = self.m_oTable.position.x + self.dCFG['border_height']
            POS_X = POS_X + (p_iSelect * self.dCFG['font_line'])
            POS_Y = self.m_oTable.position.y + self.m_oTable.position.height
            if self.m_oTitle:
                POS_X += self.m_iTitleSize
            if self.m_bShowCursor:
                rect = self.c.get_rect()
                rect.bottomleft = (POS_X, POS_Y)
                self.m_oScreen.blit(self.c, rect)
        elif self.m_iRotate == -90:
            POS_X = self.m_oTable.position.x + self.m_oTable.position.width
            POS_X = POS_X - self.dCFG['border_height'] - (p_iSelect * self.dCFG['font_line'])
            POS_Y = self.m_oTable.position.y
            if self.m_oTitle:
                POS_X -= self.m_iTitleSize
            if self.m_bShowCursor:
                rect = self.c.get_rect()
                rect.topright = (POS_X, POS_Y)
                self.m_oScreen.blit(self.c, rect)
        elif self.m_iRotate == 0:
            POS_X = self.m_oTable.position.x
            POS_Y = self.m_oTable.position.y + self.dCFG['border_height']
            POS_Y = POS_Y + (p_iSelect * self.dCFG['font_line'])
            if self.m_oTitle:
                POS_Y += self.m_iTitleSize
            if self.m_bShowCursor:
                self.m_oScreen.blit(self.c, (POS_X, POS_Y))

        pygame.display.flip()

    def _check_current_es_side(self):
        """ Check current side of EmulatioStation """
        self.m_iRotate = 0
        if os.path.exists(ROTMODES_TATE1_FILE):
            self.m_iRotate = -90
        elif os.path.exists(ROTMODES_TATE3_FILE):
            self.m_iRotate = 90
        
    def _clean_on_finish(self):
        if self.m_oJoyHandler: self.m_oJoyHandler.quit()
        pygame.quit()


class Table(object):
    """docstring for Table."""
    img = None
    height = 0
    width = 0
    position = 0

    def __init__(self, w, h):
        self.height = h
        self.width = w

    def __str__(self):
        return str((self.width, self.height, self.position, self.img))

    def get_size(self):
        return (self.width, self.height)

    def fill(self, p_lBaseColor, p_iType):
        if p_iType == BG_FLAT:
            self.img.fill(p_lBaseColor)
            return
        ndeg = min(p_lBaseColor)/8
        height = (self.height/ndeg) + 1
        cont = 0
        for y in range(0, self.height, height):
            color = map(lambda x: x - (8 * cont), p_lBaseColor)
            pygame.draw.rect(self.img, color, (0,y, self.width, height) )
            cont += 1
