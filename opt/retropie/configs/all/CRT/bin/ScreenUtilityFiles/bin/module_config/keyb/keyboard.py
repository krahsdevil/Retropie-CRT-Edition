#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Configuration Utility

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

import pygame, os, sys, logging
import time, math

sys.dont_write_bytecode = True

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(SCRIPT_DIR + "/../"))
from main_paths import MODULES_PATH
sys.path.append(MODULES_PATH)

from launcher_module.core_paths import CRT_SOUNDS_PATH
from launcher_module.core_controls import joystick, CRT_UP, CRT_DOWN, \
                                          CRT_LEFT, CRT_RIGHT, CRT_OK, \
                                          CRT_CANCEL

CURSOR_SOUND_FILE = os.path.join(CRT_SOUNDS_PATH, "sys_cursor_01.ogg")
CLICK_SOUND_FILE = os.path.join(CRT_SOUNDS_PATH, "sys_click_01.ogg")

class keyboard(object):
    m_sLayout     = os.path.join(SCRIPT_DIR, "layout.png")
    m_sCursor     = os.path.join(SCRIPT_DIR, "cursor.png")
    m_sFont       = os.path.join(SCRIPT_DIR, "font.ttf")
    m_iFontSize   = 8

    m_sText       = ""
    m_sText_Bck   = ""
    m_iText_Max   = 0  # max chars in the string

    m_iTextLine   = 9
    m_iTextLft    = 5
    m_iTextRgt    = 185

    m_iFstLine    = 35 # first keyboard line
    m_iSpcLine    = 12 # space between lines

    m_iFstChar    = 10 # first left character
    m_iSpcChar    = 14 # space between character
    m_iCharsLine  = 13 # chars per line

    m_iChar       = 1  # char of the list

    m_oSfKBD      = None
    m_oRndLayout  = None
    m_oRndCursor  = None
    m_oRndText    = None

    m_lKeyb = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M']
    m_lKeyb += ['N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    m_lKeyb += ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm']
    m_lKeyb += ['n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    m_lKeyb += ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '#', '/', ' ']
    m_lKeyb += ['-', '_', '.', ',', ':', ';', '\'', '!', '?', '(', ')', 'del', False]

    def __init__(self):
        pygame.font.init()
        self.m_oFontText = pygame.font.Font(self.m_sFont, self.m_iFontSize)
        self.m_oJoyHandler = None
        self._init_sounds()

    def _init_sounds(self):
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()
        try:
            self.m_PGSndCursor = pygame.mixer.Sound(CURSOR_SOUND_FILE)
            self.m_PGSndLoad = pygame.mixer.Sound(CLICK_SOUND_FILE)
        except Exception as e:
            logging.error(e)

    def write(self, p_sText = "your text", p_iMax = 15):
        if not self.m_oJoyHandler:
            self.m_oJoyHandler = joystick()
            self.m_iChar = 1
            self.m_sText = p_sText
            self.m_iText_Max = p_iMax
            self.m_sText_Bck = p_sText

        if not pygame.mixer.get_init():
            self._init_sounds()

        if not self.m_oSfKBD:
            self._render_keyboard()
            return self.m_oSfKBD
        else:
            value = self._input()
            if value: return self.m_oSfKBD
            elif value == None: text = self.m_sText_Bck
            else: text = self.m_sText
            self.quit()
            return text

    def _input(self):
            event = self.m_oJoyHandler.event_wait()
            if event & CRT_UP:
                self.m_PGSndCursor.play()
                self._move_up()
            if event & CRT_DOWN:
                self.m_PGSndCursor.play()
                self._move_down()
            if event & CRT_RIGHT:
                self.m_PGSndCursor.play()
                self._move_right()
            if event & CRT_LEFT:
                self.m_PGSndCursor.play()
                self._move_left()
            if event & CRT_OK:
                self.m_PGSndLoad.play()
                value = self.m_lKeyb[self.m_iChar - 1]
                if value == False: return False
                elif value == "del": self.m_sText = self.m_sText[:-1]
                else:
                    if len(self.m_sText) <= self.m_iText_Max:
                        self.m_sText += value
            if event & CRT_CANCEL:
                self.m_PGSndLoad.play()
                return None
            self._render_keyboard()
            return True

    def _get_coord(self, p_bPos = False):
        if self.m_iChar < 1: self.m_iChar = 1
        elif self.m_iChar > len(self.m_lKeyb): self.m_iChar = len(self.m_lKeyb)
        # line of the char
        line = int(math.ceil(((self.m_iChar * 1.0)/ self.m_iCharsLine)))
        # char position in the line
        char = self.m_iChar - ((line - 1) * self.m_iCharsLine)
        POS_X = ((char - 1) * self.m_iSpcChar) + self.m_iFstChar
        POS_Y = ((line - 1) * self.m_iSpcLine) + self.m_iFstLine
        if p_bPos: return char
        return (POS_X, POS_Y)

    def _move_right(self):
        pos = self._get_coord(True)
        if (pos + 1) > self.m_iCharsLine:
            self.m_iChar -= (self.m_iCharsLine - 1)
        else: self.m_iChar +=1

    def _move_left(self):
        pos = self._get_coord(True)
        if (pos - 1) < 1:
            self.m_iChar += (self.m_iCharsLine - 1)
        else: self.m_iChar -=1

    def _move_up(self):
        if (self.m_iChar - self.m_iCharsLine) > 0:
            self.m_iChar = self.m_iChar - self.m_iCharsLine
        else:
            pos = self._get_coord(True)
            self.m_iChar = len(self.m_lKeyb) - (self.m_iCharsLine - pos)

    def _move_down(self):
        if (self.m_iChar + self.m_iCharsLine) <= len(self.m_lKeyb):
            self.m_iChar = self.m_iChar + self.m_iCharsLine
        else:
            pos = self._get_coord(True)
            self.m_iChar = 0 + pos

    def _render_keyboard(self):
        if not self.m_oRndLayout:
            self.m_oRndLayout = self.render_image(self.m_sLayout)
        if not self.m_oRndCursor:
            self.m_oRndCursor = self.render_image(self.m_sCursor)

        self.m_oRndText = self._line_text()

        self.m_oSfKBD = pygame.Surface((self.m_oRndLayout.get_width(),
                                        self.m_oRndLayout.get_height()),
                                        pygame.SRCALPHA)

        rect = self.m_oRndLayout.get_rect()
        rect.topleft = (0, 0)
        self.m_oSfKBD.blit(self.m_oRndLayout, rect)

        rect = self.m_oRndCursor.get_rect()
        pos = self._get_coord()
        rect.midtop = (pos[0], pos[1])
        self.m_oSfKBD.blit(self.m_oRndCursor, rect)

        rect = self.m_oRndText.get_rect()
        rect.midleft = (self.m_iTextLft, self.m_iTextLine)
        self.m_oSfKBD.blit(self.m_oRndText, rect)

    def _line_text(self):
        max_width = self.m_iTextRgt - self.m_iTextLft
        text = self.render_text(self.m_sText)
        sf = pygame.Surface((max_width, text.get_height()), pygame.SRCALPHA)

        LnWidth = text.get_width() + self.m_oRndCursor.get_width()
        textSf = pygame.Surface((LnWidth, text.get_height()), pygame.SRCALPHA)
        rect = text.get_rect()
        rect.bottomleft = (0, textSf.get_height())
        textSf.blit(text, rect)
        rect = self.m_oRndCursor.get_rect()
        rect.bottomright = (LnWidth, textSf.get_height())
        textSf.blit(self.m_oRndCursor, rect)

        if LnWidth < max_width:
            rect = textSf.get_rect()
            rect.midbottom = (max_width / 2, sf.get_height())
            sf.blit(textSf, rect)
        else:
            rect = textSf.get_rect()
            rect.bottomright = (max_width, sf.get_height())
            sf.blit(textSf, rect)
        return sf

    def render_text(self, p_sText, p_bShadow = True):
        C_SHADOW = pygame.Color( 19, 14, 56)
        C_TEXT = pygame.Color(202,199,219)

        p_sText = str(p_sText)
        img = self.m_oFontText.render(p_sText, False, C_TEXT)
        rect = img.get_rect()
        sf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        if p_bShadow:
            shadow = self.m_oFontText.render(p_sText, False, C_SHADOW)
            shadow_rect = img.get_rect()
            shadow_rect.x += 1
            shadow_rect.y += 1
            sf.blit(shadow, shadow_rect)
        sf.blit(img, rect)
        return sf

    def render_image(self, p_sImg):
        if not os.path.exists(p_sImg):
            logging.info("INFO: image not found")
            return None
        try:
            img = pygame.image.load(p_sImg).convert_alpha()
            rect = img.get_rect()
            rect.bottomleft = (0, rect.height)
            sf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            sf.blit(img, rect)
            return sf
        except:
            raise

    def _clean(self):
        self.m_oSfKBD = None
        self.m_oRndLayout = None
        self.m_oRndCursor = None
        self.m_oRndText   = None

    def quit(self):
        self.m_oJoyHandler.quit()
        self.m_oJoyHandler = None
        self._clean()

