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
from .core_controls import joystick, CRT_DIRECTION, CRT_BUTTON

SKINSELECTOR_PATH = os.path.join(CRTROOT_PATH, "Datas/FreqSelectorSkins")

BLACK = pygame.Color(0, 0, 0)
WHITE = pygame.Color(255,255,255)
FPS = 30

DEFAULT_CFG = {
    'style': "choice_example",
    'snd_cursor': "cursor.wav",
    'snd_load': "load.wav",
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
            dData['file'], dData['value'] = p_lOptPath
            dData['img'] = pygame.image.load(os.path.join(self.m_sSkinPath, dData['file']))
            self.m_lOpts.append(dData)
        except Exception as e:
            logging.error(e)

    def load_choices(self, p_lOpts):
        for opt in p_lOpts:
            logging.info(str(opt))
            self._add_opt(opt)

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
            if event & CRT_DIRECTION:
                self.m_SndCursor.play()
                self._choice_change()
            if event & CRT_BUTTON:
                self.m_SndLoad.play()
                return self._choice_select()

    def _choice_select(self):
        try:
            filename = 'selected-' + self.m_lOpts[self.m_iCurrent]['file']
            img = pygame.image.load(os.path.join(self.m_sSkinPath, filename))
            self._draw_screen(img)
            pygame.time.delay(2000)
        except Exception as e:
            logging.error("no selected img found: %s" % str(e))
        result = self.m_lOpts[self.m_iCurrent]['value']
        logging.info("selected: %s" % str(result))
        return result

    # TODO: allow another directions, atm is a simple up to down cursor
    def _choice_change(self):
        self.m_iCurrent += 1
        if self.m_iCurrent >= len(self.m_lOpts):
            self.m_iCurrent = 0
        self._update_screen()

    def _update_screen(self):
        self._draw_screen(self.m_lOpts[self.m_iCurrent]['img'])

    def _draw_screen(self, p_oImg):
        self.m_oScreen.fill(BLACK)
        rect = p_oImg.get_rect()
        rect.center = self.m_lScreenCenter
        self.m_oScreen.blit(p_oImg, rect)
        pygame.display.flip()
