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

import pygame, os, sys, logging, math

sys.dont_write_bytecode = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(SCRIPT_DIR + "/../"))
from main_paths import MODULES_PATH
sys.path.append(MODULES_PATH)

#from launcher_module.core_paths import *
from config_core import core

C_BLACK  = pygame.Color(  0,   0,   0)
C_BLUE   = pygame.Color( 99, 202, 253)
C_WHITE  = pygame.Color(255, 255, 255)
C_YELLOW = pygame.Color(255, 255, 0)
C_GREY = pygame.Color(125, 125, 125)
C_BLUEDK = pygame.Color(0, 9, 28)
C_ORANGE = pygame.Color(255, 140, 0)

class render(core):
    def _img_render(self, p_sImg):
        if p_sImg:
            path = os.path.join(self.m_sSkinPath, p_sImg)
            try:
                img = pygame.image.load(path).convert_alpha()
                rect = img.get_rect()
                rect.bottomleft = (0, rect.height)
                sf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                sf.blit(img, rect)
                return sf
            except:
                return None

    def _text_render(self, p_sText, p_lTextColor, p_lShadowColor = None,
                     p_bCropText = False, p_iShadowDrop = 1):
        p_sText = str(p_sText)
        if p_bCropText == True:
            # max length 16 chars for values
            if len(p_sText) > 16 and self.m_iSide != 0:
                p_sText = (p_sText[:15] + "~")
            elif len(p_sText) > 21 and self.m_iSide == 0:
                p_sText = (p_sText[:20] + "~")

        p_oTextColor = C_WHITE
        if p_lTextColor and "type" in p_lTextColor:
            try: p_oTextColor = self.dCFG[p_lTextColor]
            except: p_oTextColor = C_WHITE
        elif p_lTextColor:
            p_oTextColor = p_lTextColor

        if p_lShadowColor and "type" in p_lShadowColor:
            try: p_oShadowColor = self.dCFG[p_lShadowColor]
            except: p_oShadowColor = C_WHITE
        else:
            p_oShadowColor = p_lShadowColor

        if self.dCFG['cap']: p_sText = p_sText.upper()
        img = self.m_oFontText.render(p_sText, False, p_oTextColor)
        rect = img.get_rect()
        sf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        if p_oShadowColor:
            shadow = self.m_oFontText.render(p_sText, False, p_oShadowColor)
            shadow_rect = img.get_rect()
            shadow_rect.x += p_iShadowDrop
            shadow_rect.y += p_iShadowDrop
            sf.blit(shadow, shadow_rect)
        sf.blit(img, rect)
        return sf

    def _render_line_menu(self, p_lLine):
        oLineSf = pygame.Surface((self.m_iText_rgt - self.m_iText_lft,
                  self.dCFG['font_line'] + 4), pygame.SRCALPHA)

        oTextSf = None
        oValueSf = None

        spacer = 10                                         # space between text & value
        ltoffset = 0                                        # move left text if icon
        rtoffset = oLineSf.get_width()                      # move right text if rarrow
        rtoffset -= self.dCFG['rarrow_render'].get_width()
        rtoffset -= 1

        raoffset = oLineSf.get_width()                      # right arrow offset
        laoffset = 0                                        # left arrow offset

        # check/append left icon in line surface
        if p_lLine["icon"]:
            if not p_lLine['icon_render'] or p_lLine["icon"] != p_lLine["prev_icon"]:
                p_lLine['icon_render'] = self._img_render(self.dCFG[p_lLine["icon"]])
            alignY = 0
            if p_lLine['icon_render'].get_height() > self.dCFG['font_size']:
                alignY -= math.ceil((p_lLine['icon_render'].get_height() - \
                          self.dCFG['font_size']) / 2.0)
            rect = p_lLine['icon_render'].get_rect()
            rect.midleft = (0, (oLineSf.get_height() / 2) + alignY)
            ltoffset = rect.width + 3
            oLineSf.blit(p_lLine['icon_render'], rect)
        p_lLine["prev_icon"] = p_lLine["icon"]

        # check/append selected value in line surface
        if p_lLine['value'] or p_lLine['value'] == False:
            if type(p_lLine['value']) == type(True):
                oValueSf = self.dCFG['icon_true_render']
                if not p_lLine['value']: oValueSf = self.dCFG['icon_false_render']
                rect1 = oValueSf.get_rect()
                rect1.midright = (rtoffset, oLineSf.get_height() / 2)
            else:
                if p_lLine["value"] != p_lLine["prev_value"] or not p_lLine["value_render"]:
                    p_lLine["value_render"] = self._text_render(p_lLine['value'],
                                              p_lLine['color_val'], 'type_color_3', True)
                    p_lLine["prev_value"] = p_lLine["value"]
                oValueSf = p_lLine["value_render"]

                rect1 = oValueSf.get_rect()
                rect1.midright = (rtoffset, oLineSf.get_height() / 2)
                # check if multiple values for draw arrow
                if p_lLine['options'] and p_lLine['value'] in p_lLine['options']:
                    pos = p_lLine['options'].index(p_lLine['value']) + 1
                    qty = len(p_lLine['options'])
                    if qty > 1:
                        if pos < qty: # right arrow
                            rect = self.dCFG['rarrow_render'].get_rect()
                            rect.midright = (raoffset, oLineSf.get_height() / 2)
                            oLineSf.blit(self.dCFG['rarrow_render'], rect)
                        if pos > 1: # left arrow
                            rect = self.dCFG['larrow_render'].get_rect()
                            laoffset = rtoffset # left arrow offset
                            laoffset -= (oValueSf.get_width() + 1)
                            rect.midright = (laoffset, oLineSf.get_height() / 2)
                            oLineSf.blit(self.dCFG['larrow_render'], rect)
            oLineSf.blit(oValueSf, rect1)

        # check/append left text on line surface
        if p_lLine["text"] != p_lLine["prev_text"] or not p_lLine["text_render"]:
            p_lLine["text_render"] = self._text_render(p_lLine["text"], C_WHITE, 'type_color_3')
            p_lLine["prev_text"] = p_lLine["text"]
        text = p_lLine["text_render"]

        TotSize = self.dCFG['rarrow_render'].get_rect().width
        TotSize += ltoffset
        TotSize += text.get_rect().width + spacer
        if oValueSf: TotSize += oValueSf.get_rect().width
        if laoffset: TotSize += self.dCFG['larrow_render'].get_rect().width + 3

        # check if left text need scroll
        calc = TotSize - oLineSf.get_rect().width
        if calc > 4: # text needs scroll or crop
            crop = text.get_rect().width - calc
            if self.m_lLines.index(p_lLine) == self.m_iLine:
                self.m_iScroll_dif = calc
                oTextSf = pygame.Surface((crop, self.dCFG['font_line'] + 4),
                                         pygame.SRCALPHA)
                rect = text.get_rect()
                rect.midleft = (0, oLineSf.get_height() / 2)
                rect.x += self.m_iScroll_mov
                oTextSf.blit(text, rect)
            else:
                self.m_iScroll_dif = 0
                self.m_iScroll_mov = 0
                oTextSf = text.subsurface(0, 0, crop, text.get_rect().height)
        else:
            oTextSf = text

        rect = oTextSf.get_rect()
        rect.midleft = (ltoffset, oLineSf.get_height() / 2)
        oLineSf.blit(oTextSf, rect)

        return oLineSf

    def _render_info_text(self, p_sText, p_sIcon = None):
        ltoffset = 0
        if p_sIcon:
            icon = self._img_render(self.dCFG[p_sIcon])
            ltoffset += icon.get_width() + 3

        text = self._text_render(p_sText, C_WHITE, 'type_color_3')
        size = ltoffset + text.get_width()
        oSectSf = pygame.Surface((size, self.dCFG['font_line'] + 4), pygame.SRCALPHA)

        if size > text.get_width():
            alignY = 0
            if icon.get_height() > self.dCFG['font_size']:
                alignY -= math.ceil((icon.get_height() - self.dCFG['font_size']) / 2.0)
            rect = icon.get_rect()
            rect.midleft = (0, (oSectSf.get_height() / 2) + alignY)
            oSectSf.blit(icon, rect)

        rect = text.get_rect()
        rect.midleft = (ltoffset, oSectSf.get_height() / 2)
        oSectSf.blit(text, rect)
        return oSectSf

    def _render_info_layer(self, p_sText, p_sIcon = None):
        render_lines = []
        icon_width = 0

        if p_sIcon:
            rnd = self._img_render(p_sIcon)
            if rnd: icon_width = rnd.width + 3

        if type(p_sText) is list:
            for line in p_sText:
                render_lines.append(self._render_info_text(line, p_sIcon))
                p_sIcon = None
        else:
            render_lines.append(self._render_info_text(p_sText, p_sIcon))

        # find widthest line and define table
        line_width = 0
        spc = 12
        for line in render_lines:
            if line.get_width() > line_width: line_width = line.get_width()

        p_oTable = Table(line_width + spc, spc * (len(render_lines) + 1))
        p_oTable.img = pygame.Surface(p_oTable.get_size())
        p_oTable.fill(self.dCFG['type_color_3'])

        # create rectangles for info box
        rectangle = pygame.Rect(0, 0, p_oTable.width - 1, p_oTable.height - 1)
        rectangle.topleft = (0, 0)
        pygame.draw.rect(p_oTable.img, C_GREY, rectangle)

        pos = spc
        count = 0
        for line in render_lines:
            rect = line.get_rect()
            rect.midleft = (spc / 2, pos)
            p_oTable.img.blit(line, rect)
            pos += spc
            count += 1

        # Create layer 40 surface
        self.m_oLayer40 = pygame.Surface(self.m_lRES, pygame.SRCALPHA)
        rect = p_oTable.img.get_rect()
        rect.center = (self.m_lScreenCenter[0] + 1, self.m_lScreenCenter[1])

        # draw text
        self.m_oLayer40.blit(p_oTable.img, rect)

        # Rotate if vertical mode
        if self.m_iSide == 1:
            self.m_oLayer40 = pygame.transform.rotate(self.m_oLayer40, -90)
        elif self.m_iSide == 3:
            self.m_oLayer40 = pygame.transform.rotate(self.m_oLayer40, 90)
        return

    def push_info_image(self, p_oImg):
        self.m_oLayer40 = pygame.Surface(self.m_lRES, pygame.SRCALPHA)
        rect = p_oImg.get_rect()
        rect.center = (self.m_lScreenCenter[0], self.m_lScreenCenter[1])
        self.m_oLayer40.blit(p_oImg, rect)

        # Rotate if vertical mode
        if self.m_iSide == 1:
            self.m_oLayer40 = pygame.transform.rotate(self.m_oLayer40, -90)
        elif self.m_iSide == 3:
            self.m_oLayer40 = pygame.transform.rotate(self.m_oLayer40, 90)
        return

class Table(object):
    """docstring for Table."""
    img = None
    height = 0
    width = 0
    position = 0

    # BG TYPES
    BG_FLAT = 1
    BG_DEGRADE = 2

    def __init__(self, w, h):
        self.height = h
        self.width = w

    def __str__(self):
        return str((self.width, self.height, self.position, self.img))

    def get_size(self):
        return (self.width, self.height)

    def fill(self, p_lBaseColor, p_iType = BG_FLAT):
        if p_iType == self.BG_FLAT:
            self.img.fill(p_lBaseColor)
            return
        ndeg = min(p_lBaseColor)/8
        height = (self.height/ndeg) + 1
        cont = 0
        for y in range(0, self.height, height):
            color = map(lambda x: x - (8 * cont), p_lBaseColor)
            pygame.draw.rect(self.img, color, (0,y, self.width, height) )
            cont += 1