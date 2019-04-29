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
import logging
import pygame

from .core_paths import CRTROOT_PATH
from .screen import CRT
from .core_controls import joystick, CRT_UP, CRT_DOWN, CRT_BUTTON

SKINSELECTOR_PATH = os.path.join(CRTROOT_PATH, "Datas/FreqSelectorSkins")

C_BLACK = pygame.Color(  0,   0,   0)
C_WHITE = pygame.Color(255, 255, 255)
BG_COLOR = (128, 120, 211) # 15
BG_COLOR_SEL = (180, 80, 100) # 15
BG_FLAT = 1
BG_DEGRADE = 2

FPS = 30

DEFAULT_CFG = {
    'style': "choice_dynamic",

    'border': "border.png",
    'border_round': "border_round.png",
    'border_vertical': "border_vert.png",
    'border_height': 8,

    'cursor': "cursor.png",
    'font': "font.ttf",
    'snd_cursor': "cursor.wav",
    'snd_load': "load.wav",

    'bgcolor': BG_COLOR,
    'bgcolor_selected': BG_COLOR_SEL,
    'bgtype': BG_DEGRADE,
}

class choices(object):
    """show a selector with choices using pygame."""

    m_oJoyHandler = None
    m_oClock = None
    m_lOpts = []
    m_iCurrent = 0
    m_sSkinPath = ""
    m_SndCursor = None
    m_SndLoad = None
    m_lResolutionXY = ()
    m_oScreen = None
    m_oFont = None
    m_oFontTitle = None
    m_oTable = None

    def __init__(self, p_dChoices = DEFAULT_CFG):
        self.dCFG = p_dChoices
        self.m_sSkinPath = os.path.join(SKINSELECTOR_PATH, self.dCFG['style'])
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()
        self.m_oClock = pygame.time.Clock()
        self.oJoyHandler = joystick()
        self._init_screen()
        self._init_sounds()

    def _init_screen(self):
        pygame.display.init()
        pygame.font.init()
        # fonts
        self.m_oFontText = pygame.font.Font(os.path.join(self.m_sSkinPath, self.dCFG['font']), 16)
        self.dCFG['font_line'] = self.m_oFontText.get_linesize()
        self.m_oFontTitle = pygame.font.Font(os.path.join(self.m_sSkinPath, self.dCFG['font']), 32)
        self.dCFG['title_line'] = self.m_oFontTitle.get_linesize()
        # gfx
        self.be = pygame.image.load(os.path.join(self.m_sSkinPath, self.dCFG['border_round']))
        self.b = pygame.image.load(os.path.join(self.m_sSkinPath, self.dCFG['border']))
        self.c = pygame.image.load(os.path.join(self.m_sSkinPath, self.dCFG['cursor']))
        pygame.mouse.set_visible(0)
        self.m_lResolutionXY = CRT.get_xy_screen()
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

    def load_choices(self, p_lOpts):
        self.m_lOpts = []
        for opt in p_lOpts:
            logging.info(str(opt))
            self._add_opt(opt)
        self._table_render()

    def _table_create(self):
        self.m_oTable = Table(0, self.dCFG['font_line'] * len(self.m_lOpts))
        for opt in self.m_lOpts:
            if opt['img'].get_width() > self.m_oTable.width:
                self.m_oTable.width = opt['img'].get_width()
        self.m_oTable.width += self.dCFG['border_height'] * 4
        self.m_oTable.height += self.dCFG['border_height'] * 2
        self.m_oTable.img = pygame.Surface(self.m_oTable.get_size())
        rect = self.m_oTable.img.get_rect()
        rect.center = self.m_lScreenCenter
        self.m_oTable.position = rect
        self.m_oTable.fill(self.dCFG['bgcolor'])

    def _table_border(self):
        w = self.be.get_width()
        h = self.be.get_height()
        bottom = self.m_oTable.img.get_height() - h
        right = self.m_oTable.img.get_width() - w

        # edges
        tmp = pygame.transform.flip(self.b, 0, 1)
        for x in range(w, right):
            self.m_oTable.img.blit(self.b, (x, 0))
            self.m_oTable.img.blit(tmp, (x, bottom))
        tmp = pygame.transform.rotate(self.b, 90)
        tmp2 = pygame.transform.rotate(self.b, -90)
        for y in range(h, bottom):
            self.m_oTable.img.blit(tmp, (0, y))
            self.m_oTable.img.blit(tmp2, (right, y))

        # corners
        self.m_oTable.img.blit(self.be, (0,0))
        tmp = pygame.transform.rotate(self.be, -90)
        self.m_oTable.img.blit(tmp, (right, 0))
        tmp = pygame.transform.rotate(self.be, 180)
        self.m_oTable.img.blit(tmp, (right, bottom))
        tmp = pygame.transform.rotate(self.be, 90)
        self.m_oTable.img.blit(tmp, (0, bottom))

    def _table_render(self):
        self._table_create()
        self._table_border()
        line = self.dCFG['border_height']
        for opt in self.m_lOpts:
            rect = opt['img'].get_rect()
            rect.x = 16
            rect.top = line
            self.m_oTable.img.blit(opt['img'], rect)
            line += self.dCFG['font_line']

    def text_render(self, p_sText, p_lTextColor, p_lShadowColor = None, p_iShadowDrop = 1):
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
        pygame.display.quit()
        pygame.quit()

    def run(self):
        if self.oJoyHandler.get_num() < 1:
            # TODO: no opts or no joys
            logging.error("no joysticks found, using default opt.")
            return self._choice_select()
        self._update_screen()
        result = self.loop()
        return result

    def loop(self):
        while True:
            self.m_oClock.tick(FPS)
            event = self.oJoyHandler.event_wait()
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

    def _choice_select(self):
        result = self.m_lOpts[self.m_iCurrent]['value']
        text = self.m_lOpts[self.m_iCurrent]['text']
        # just create a new simple table to show the result
        self.dCFG['bgcolor'] = self.dCFG['bgcolor_selected']
        self.load_choices([("SELECTED: %s" % text, 0)])
        self.m_oScreen.blit(self.m_oTable.img, self.m_oTable.position)
        pygame.display.flip()
        # wait end sound
        pygame.time.delay(2000)
        logging.info("selected: %s" % str(result))
        return result

    # TODO: allow another directions, atm is a simple up to down cursor
    def _choice_change(self, p_iDirection):
        self.m_iCurrent += p_iDirection
        if self.m_iCurrent >= len(self.m_lOpts):
            self.m_iCurrent = 0
        elif self.m_iCurrent < 0:
            self.m_iCurrent = len(self.m_lOpts) - 1
        self._update_screen()

    def _update_screen(self):
        self._draw_screen(self.m_iCurrent)

    def _draw_screen(self, p_iSelect):
        self.m_oScreen.fill(C_BLACK)
        self.m_oScreen.blit(self.m_oTable.img, self.m_oTable.position)
        y = self.m_oTable.position.y + self.dCFG['border_height'] + (p_iSelect * self.dCFG['font_line'])
        self.m_oScreen.blit(self.c, (self.m_oTable.position.x,y))
        pygame.display.flip()


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

    def fill(self, p_lBaseColor):
        ndeg = min(p_lBaseColor)/8
        height = (self.height/ndeg) + 1
        cont = 0
        for y in range(0, self.height, height):
            color = map(lambda x: x - (8 * cont), p_lBaseColor)
            pygame.draw.rect(self.img, color, (0,y, self.width, height) )
            cont += 1
