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

import pygame, time
import sys, os, math
import threading, logging

sys.dont_write_bytecode = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(SCRIPT_DIR + "/../"))
from main_paths import MODULES_PATH
sys.path.append(MODULES_PATH)

from index import index
from config_utils import change_watcher, restart_ES
from launcher_module.core_paths import TMP_LAUNCHER_PATH, CRT_SOUNDS_PATH
from launcher_module.utils import get_screen_resolution, get_side
from launcher_module.core_controls import joystick, CRT_UP, CRT_DOWN, \
                                          CRT_LEFT, CRT_RIGHT, CRT_OK, \
                                          CRT_CANCEL

DEFAULT_CFG = {
    'style': "default",

    'top': "top_frame.png",
    'bottom': "bottom_frame.png",
    'background': "background.png",
    'selector': "selector.png",

    'vtop': "vtop_frame.png",
    'vbottom': "vbottom_frame.png",
    'vbackground': "vbackground.png",
    'vselector': "vselector.png",

    'larrow': "larrow.png",
    'rarrow': "rarrow.png",

    'font': "font.ttf",
    'font_size': 8,
    'cap': True,

    'icon_true': "icon_true.png",
    'icon_false': "icon_false.png",
    'icon_clock': "icon_clock.png",
    'icon_warn': "icon_warn.png",
    'icon_edit': "icon_edit.png",
    'icon_eject': "icon_eject.png",
    'icon_es': "icon_es.png",
    'icon_sys': "icon_sys.png",
    'icon_bin': "icon_bin.png",
    'icon_info': "icon_info.png",
    'icon_power': "icon_power.png",
    'icon_folder': "icon_folder.png",
    'icon_foldero': "icon_foldero.png",

    'pointer': ["pointerf1.png", "pointerf2.png"],

    'type_color_1': pygame.Color(244,217, 48), # info values
    'type_color_2': pygame.Color(124,113,218), # menu access color
    'type_color_3': pygame.Color( 19, 14, 56), # text shadow
    'type_color_4': pygame.Color( 62, 50,162), # text color selected line
    'type_color_5': pygame.Color(124,113,218), # frame color
    'type_color_6': pygame.Color(255,180,  0), # for high vol
    'type_color_7': pygame.Color(202,199,219), # disabled color
}

C_BLACK  = pygame.Color(  0,   0,   0)
C_BLUE   = pygame.Color( 99, 202, 253)
C_WHITE  = pygame.Color(255, 255, 255)
C_YELLOW = pygame.Color(255, 255,   0)
C_GREY   = pygame.Color(125, 125, 125)

CURSOR_SOUND_FILE = os.path.join(CRT_SOUNDS_PATH, "sys_cursor_01.ogg")
CLICK_SOUND_FILE = os.path.join(CRT_SOUNDS_PATH, "sys_click_01.ogg")

class core(object):
    m_sSkinPath = ""

    m_oThreads      = [] # to store threads
    m_bPause        = [False]
    m_bExit         = False
    m_lRestart      = {'restart': False, 'icon_render': None}
    m_lReboot       = {'reboot': False, 'icon_render': None}

    m_iSide         = 0

    m_oLayer0       = None # background
    m_oLayer10      = None # selector
    m_oLayer20      = None # all menu text except selected line
    m_oLayer21      = None # selected line
    m_oLayer30      = None # pointer
    m_oLayer40      = None # info

    m_lLayer40      = [None, None] # text & icon label from submenus
    m_lLayer40_core = [None, None] # text & icon label from core

    m_iScroll_dif   = 0 # part of text out of assigned space
    m_iScroll_mov   = 0 # current displacement of scroll

    m_iLine         = 0    # Current menu line
    m_lPointer      = {'frame': 0, 'pointer_render': []}

    m_oIndex        = None # for import current submenu/section
    m_lLines        = []

    m_lIcon         = {}   # icon for submenu/section
    m_sSection      = ""   # title for submenu/section
    m_sTitle        = "CONFIGURATION UTILITY"
    m_lInfo         = ({'info': "A:OK"}, {'info': "B:BACK"})

    def __init__(self, p_dSkin = DEFAULT_CFG):
        self.check_cfg_file()
        self.dCFG = p_dSkin.copy()
        self.m_sSkinPath = os.path.join(SCRIPT_DIR, self.dCFG['style'])
        self.m_oIndex = index()
        self._init_pygame()
        self.m_oWach = change_watcher(self.m_lLines, self.m_iLine)
        self._create_threads()
        self.run()

    def run(self):
        self.check_es_launcher()
        self._main_loop()

    def _draw_screen(self):
        self._side_and_size()
        self._import_index()
        self._get_pages()
        self._prepare_datas()
        self._render_layers()
        self._join_layers()
        pygame.display.flip()

    def _import_index(self):
        self.m_bPause = self.m_oIndex.m_bPause
        self.m_lLines = self.m_oIndex.m_lLines
        self.m_lIcon = self.m_oIndex.m_lIcon
        self.m_sSection = self.m_oIndex.m_sSection
        self.m_lLayer40 = self.m_oIndex.m_lLayer40
        self.m_lRestart['restart'] = self.m_oIndex.m_bRestart
        self.m_lReboot['reboot'] = self.m_oIndex.m_bReboot

    def _create_threads(self):
        p_oDmns = [self._dmn_rfrsh_scr, self._dmn_pnt_anim, self._dmn_scroll]
        for dmn in p_oDmns:
            t = threading.Thread(target=dmn)
            t.setDaemon(True)
            t.start()
            self.m_oThreads.append(t)

    def _dmn_rfrsh_scr(self):
        try:
            while True:
                if self.m_bPause[0]: self._pause()
                if self.m_bExit: return
                self._draw_screen()
                self.m_oClock.tick(15)
                pygame.time.wait(0)
        except: raise

    def _dmn_pnt_anim(self):
        try:
            freq = 2 #increse/decrease for speed animation (FPS)
            while True:
                if self.m_bPause[0]: self._wait()
                if self.m_bExit: return
                if len(self.m_lPointer['pointer_render']) > 1:
                    if (self.m_lPointer['frame'] + 1) == len(self.m_lPointer['pointer_render']):
                        self.m_lPointer['frame'] = 0
                    else:
                        self.m_lPointer['frame'] += 1
                self.m_oClock.tick(freq)
                pygame.time.wait(0)
        except: raise

    def _dmn_scroll(self):
        try:
            freq = 15 #increse/decrease for speed animation (FPS)
            while True:
                if self.m_bPause[0]: self._wait()
                if self.m_bExit: return
                if self.m_iScroll_dif:
                    self.m_iScroll_mov = 0
                    prev_dif = self.m_iScroll_dif
                    side = -1
                    while self.m_iScroll_dif:
                        if self.m_bPause[0]: self._wait()
                        if self.m_bExit: return
                        if self.m_iScroll_mov > 0 or prev_dif != self.m_iScroll_dif: break
                        self.m_iScroll_mov += (1 * side)
                        if abs(self.m_iScroll_mov) >= abs(self.m_iScroll_dif) or \
                           abs(self.m_iScroll_mov) == 0:
                            side = -(side)
                            if self.m_iScroll_mov == 0: time.sleep(1.5)
                        self.m_oClock.tick(freq)
                        pygame.time.wait(0)
                self.m_oClock.tick(freq)
                pygame.time.wait(0)
        except: raise

    def _wait(self):
        while self.m_bPause[0]:
            if self.m_bExit: return
            time.sleep(0.1)

    def _pause(self):
        self.m_oJoyHandler.quit()
        if self.m_bPause[0]: self._wait()
        if self.m_bExit: return
        self.m_oJoyHandler.init()
        self.m_oScreen = pygame.display.set_mode(self.m_lResolutionXY, pygame.FULLSCREEN)

    def _init_pygame(self):
        pygame.mixer.pre_init(44100, -16, 2, 4096)
        pygame.display.init()
        pygame.mouse.set_visible(0)
        self.m_oJoyHandler = joystick()
        self._init_screen()
        self.m_oClock = pygame.time.Clock()
        self._init_sounds()

    def _init_screen(self):
        pygame.display.init()
        pygame.font.init()
        pygame.mouse.set_visible(0)

        # gfx
        self.m_oFontText = pygame.font.Font(os.path.join(self.m_sSkinPath,
                           self.dCFG['font']), self.dCFG['font_size'])
        self.dCFG['font_line'] = self.m_oFontText.get_linesize()

        # screen
        self.m_lResolutionXY = get_screen_resolution()
        self._side_and_size()
        self.m_oScreen = pygame.display.set_mode(self.m_lResolutionXY, pygame.FULLSCREEN)

    def _side_and_size(self):
        self.m_lRES = list(self.m_lResolutionXY)
        p_iSide = get_side()

        self.m_iText_fst = 30
        self.m_iText_spc = 14
        self.m_iText_lft = 37
        self.m_iText_rgt = 285
        self.m_iTitl_Pos = self.m_iText_fst
        self.m_iMenu_pos = self.m_iText_fst + (2 * self.m_iText_spc)
        self.m_iSect_pos = self.m_iText_fst + (12 * self.m_iText_spc)
        self.m_iInfo_pos = self.m_iText_fst + (13 * self.m_iText_spc + 6)
        self.m_iInfo_lft = 30
        self.m_iInfo_rgt = 292
        self.m_iMax_Lines = 9

        if p_iSide != 0:
            self.m_lRES[0] = self.m_lResolutionXY[1]
            self.m_lRES[1] = self.m_lResolutionXY[0]
            self.m_iText_fst = 30
            self.m_iText_spc = 14
            self.m_iText_lft = 31
            self.m_iText_rgt = 214
            self.m_iTitl_Pos = self.m_iText_fst
            self.m_iMenu_pos = self.m_iText_fst + (2 * self.m_iText_spc)
            self.m_iSect_pos = self.m_iText_fst + (18 * self.m_iText_spc) - 5
            self.m_iInfo_pos = self.m_iText_fst + (19 * self.m_iText_spc)
            self.m_iInfo_lft = 21
            self.m_iInfo_rgt = 219
            self.m_iMax_Lines = 15

        self.m_lScreenCenter = map(lambda x: x/2, self.m_lRES)
        self.m_iSide = p_iSide

    def _init_sounds(self):
        pygame.mixer.init()
        try:
            self.m_PGSndCursor = pygame.mixer.Sound(CURSOR_SOUND_FILE)
            self.m_PGSndLoad = pygame.mixer.Sound(CLICK_SOUND_FILE)
        except Exception as e:
            logging.error(e)

    def _prepare_datas(self):
        p_lLines = ('icon', 'icon_render', 'value',
                    'options', 'color_txt', 'color_val',
                    'icon_prev', 'text', 'text_render',
                    'prev_text', 'value_render',
                    'prev_value')
        p_lTheme = ('background_render', 'top_render',
                    'bottom_render', 'selector_render',
                    'icon_true_render', 'icon_false_render',
                    'larrow_render', 'rarrow_render')
        p_lPointer = ()

        for line in self.m_lLines:
            for item in p_lLines:
                try: line[item]
                except: line[item] = None

        for item in p_lTheme:
            try: self.dCFG[item]
            except: self.dCFG[item] = None

        try: self.m_lIcon['icon']
        except: self.m_lIcon['icon'] = None

    def _get_pages(self):
        self.m_iPageTot = int(math.ceil(len(self.m_lLines) \
                          * 1.0 / self.m_iMax_Lines * 1.0))
        self.m_iPageCur = int(math.ceil((self.m_iLine + 1) \
                          * 1.0 / self.m_iMax_Lines * 1.0))

        # calculate lines to be drawn among pages
        self.m_iLDrawMax = int((self.m_iPageCur * self.m_iMax_Lines) - 1)
        self.m_iLDrawMin = int((self.m_iLDrawMax - (self.m_iMax_Lines - 1)))

    def _get_onscreen_menu_line(self):
        for i in range(1, self.m_iPageTot + 1):
            page = i * self.m_iMax_Lines
            if page > self.m_iLine:
                scrpos = self.m_iMax_Lines - (page - self.m_iLine)
                return scrpos

    def _main_loop(self):
        exit = False
        while True:
            if self.m_bPause[0]: self._wait()
            if self.m_bExit: return
            event = self.m_oJoyHandler.event_wait()
            if event & CRT_UP:
                self.m_PGSndCursor.play()
                if self.m_iLine == 0:
                    self.m_iLine = int(len(self.m_lLines) - 1)
                else:
                    self.m_iLine -= 1
            elif event & CRT_DOWN:
                self.m_PGSndCursor.play()
                if self.m_iLine == int(len(self.m_lLines) - 1):
                    self.m_iLine = 0
                else:
                    self.m_iLine += 1
            else:
                self.m_PGSndLoad.play()
                if event & CRT_CANCEL:
                    self.m_iLine = 0
                if self.m_oIndex.input(self.m_iLine, event) == CRT_CANCEL:
                    self.quit()

    def _render_layers(self):
        p_bCheck01 = self._check_side_change()
        p_bCheck02 = self._check_pending_rest_reb()
        p_bCheck03 = self._check_text_change()
        p_bCheck04 = self._check_line_change()
        p_bCheck05 = self.m_iScroll_dif

        # render Layer 0; Background and frames
        if p_bCheck01 or p_bCheck02:
            self._render_layer0()

        # render Layer 10; Selector
        if p_bCheck04 or p_bCheck01:
            self._render_layer10(p_bCheck01)

        # render Layer 20 Text and 21
        if p_bCheck03 or p_bCheck01:
            self._render_layer20()
            self._render_layer21()

        # render Layer 21;
        if p_bCheck05:
            self._render_layer21()

        # render Layer 30; Pointer
        self._render_layer30()

        # render Layer 40; Info
        self._render_layer40()

    def _join_layers(self):
        self.m_oScreen.fill(C_BLACK)

        # append Layer 0 on main screen surface
        rect = self.m_oLayer0.get_rect()
        rect.topleft = (0, 0)
        self.m_oScreen.blit(self.m_oLayer0, rect)

        # append Layer 10 on main screen surface
        rect = self.m_oLayer10.get_rect()
        rect.topleft = (0, 0)
        self.m_oScreen.blit(self.m_oLayer10, rect)

        # append Layer 20 on main screen surface
        rect = self.m_oLayer20.get_rect()
        rect.topleft = (0, 0)
        self.m_oScreen.blit(self.m_oLayer20, rect)

        # append Layer 21 on main screen surface
        rect = self.m_oLayer21.get_rect()
        rect.topleft = (0, 0)
        self.m_oScreen.blit(self.m_oLayer21, rect)

        # append Layer 30 on main screen surface
        rect = self.m_oLayer30.get_rect()
        rect.topleft = (0, 0)
        self.m_oScreen.blit(self.m_oLayer30, rect)

        # append Layer 40 on main screen surface
        if self.m_oLayer40:
            rect = self.m_oLayer40.get_rect()
            rect.topleft = (0, 0)
            self.m_oScreen.blit(self.m_oLayer40, rect)

    def _render_layer0(self):
        # Layer 0 surface, background + top frame + bottom frame
        self.m_oLayer0 = pygame.Surface(self.m_lRES, pygame.SRCALPHA)
        # append background to layer0
        img = "background"
        if self.m_iSide != 0: img = "vbackground"
        self.dCFG['background_render'] = self._img_render(self.dCFG[img])
        rect = self.dCFG['background_render'].get_rect()
        rect.topleft = (0, 0)
        self.m_oLayer0.blit(self.dCFG['background_render'], rect)

        # append top to layer0
        img = "top"
        if self.m_iSide != 0: img = "vtop"
        try:
            self.dCFG['top_render'] = self._img_render(self.dCFG[img])
            rect = self.dCFG['top_render'].get_rect()
            rect.topleft = (0, 0)
            self.m_oLayer0.blit(self.dCFG['top_render'], rect)
        except: logging.info("INFO: top image not found")

        # append ES reload icon to layer 0
        if not self.m_lRestart['icon_render']:
            img = 'icon_es'
            self.m_lRestart['icon_render'] = self._img_render(self.dCFG[img])
        if not self.m_lReboot['icon_render']:
            img = 'icon_sys'
            self.m_lReboot['icon_render'] = self._img_render(self.dCFG[img])

        if self.m_lReboot['reboot']:
            rect = self.m_lReboot['icon_render'].get_rect()
            rect.center = (self.m_lRES[0] / 2, self.m_iInfo_pos)
            self.m_oLayer0.blit(self.m_lReboot['icon_render'], rect)
        elif self.m_lRestart['restart']:
            rect = self.m_lRestart['icon_render'].get_rect()
            rect.center = (self.m_lRES[0] / 2, self.m_iInfo_pos)
            self.m_oLayer0.blit(self.m_lRestart['icon_render'], rect)

        # append bottom to layer0
        img = "bottom"
        if self.m_iSide != 0: img = "vbottom"
        try:
            self.dCFG['bottom_render'] = self._img_render(self.dCFG[img])
            rect = self.dCFG['bottom_render'].get_rect()
            rect.bottomleft = (0, self.m_lRES[1])
            self.m_oLayer0.blit(self.dCFG['bottom_render'], rect)
        except: logging.info("INFO: bottom image not found")

        # Rotate if vertical mode
        if self.m_iSide == 1:
            self.m_oLayer0 = pygame.transform.rotate(self.m_oLayer0, -90)
        elif self.m_iSide == 3:
            self.m_oLayer0 = pygame.transform.rotate(self.m_oLayer0, 90)

    def _render_layer10(self, p_bReload = False):
        # layer10 surface, selector
        line = self._get_onscreen_menu_line()
        Y_POS = self.m_iMenu_pos + (line * self.m_iText_spc)
        self.m_oLayer10 = pygame.Surface(self.m_lRES, pygame.SRCALPHA)

        # append selector to layer10
        if not self.dCFG['selector_render'] or p_bReload:
            img = "selector"
            if self.m_iSide != 0: img = "vselector"
            self.dCFG['selector_render'] = self._img_render(self.dCFG[img])
        rect = self.dCFG['selector_render'].get_rect()

        rect.midleft = (0, Y_POS)
        self.m_oLayer10.blit(self.dCFG['selector_render'], rect)

        # Rotate if vertical mode
        if self.m_iSide == 1:
            self.m_oLayer10 = pygame.transform.rotate(self.m_oLayer10, -90)
        elif self.m_iSide == 3:
            self.m_oLayer10 = pygame.transform.rotate(self.m_oLayer10, 90)

    def _render_layer20(self):
        Y_POS = self.m_iMenu_pos
        # create layer20 surface
        self.m_oLayer20 = pygame.Surface(self.m_lRES, pygame.SRCALPHA)

        # render left arrow/right arrow/true/false icons
        if not self.dCFG['icon_true_render']:
            self.dCFG['icon_true_render'] = self._img_render(self.dCFG['icon_true'])
        if not self.dCFG['icon_false_render']:
            self.dCFG['icon_false_render'] = self._img_render(self.dCFG['icon_false'])
        if not self.dCFG['larrow_render']:
            self.dCFG['larrow_render'] = self._img_render(self.dCFG['larrow'])
        if not self.dCFG['rarrow_render']:
            self.dCFG['rarrow_render'] = self._img_render(self.dCFG['rarrow'])

        count = 0
        # render/append all menu lines to layer20 surface
        for line in self.m_lLines:
            if count in range(self.m_iLDrawMin, self.m_iLDrawMax + 1):
                if count != self.m_iLine:
                    oLine = self._render_line_menu(line)
                    # append line surface to layer20 surface
                    rect = oLine.get_rect()
                    rect.midleft = (self.m_iText_lft, Y_POS)
                    self.m_oLayer20.blit(oLine, rect)
                Y_POS += self.m_iText_spc
            count += 1

        # check/append info text on line surface
        oInfoSf = pygame.Surface((self.m_iInfo_rgt - self.m_iInfo_lft,
                                  self.dCFG['font_line']), pygame.SRCALPHA)

        ltoffset = 0
        # info text: button info
        self.m_lInfo[1]['info'] = "B:BACK"
        if self.m_sSection.lower() == "main":
            self.m_lInfo[1]['info'] = "B:EXIT"
        for item in self.m_lInfo:
            line = self._text_render(item['info'], C_WHITE, 'type_color_3')
            rect = line.get_rect()
            rect.midleft = (ltoffset, oInfoSf.get_height() / 2)
            oInfoSf.blit(line, rect)
            ltoffset += (line.get_width() + 4)

        # info text: pages info
        txt = "PAGE %s/%s" % (self.m_iPageCur, self.m_iPageTot)
        pages = self._text_render(txt, 'type_color_1', 'type_color_3')
        rect = pages.get_rect()
        rect.midright = (oInfoSf.get_width(), oInfoSf.get_height() / 2)
        oInfoSf.blit(pages, rect)

        # render/append text info line to layer20
        rect = oInfoSf.get_rect()
        rect.midleft = (self.m_iInfo_lft, self.m_iInfo_pos)
        self.m_oLayer20.blit(oInfoSf, rect)

        # check/append title on layer20
        title = self._text_render(self.m_sTitle, C_WHITE, 'type_color_3')
        rect = title.get_rect()
        rect.center = (self.m_lRES[0] / 2, self.m_iTitl_Pos)
        self.m_oLayer20.blit(title, rect)

        # check/append section on layer20
        oSectSf = self._render_info_text(self.m_sSection, 'icon_foldero')
        rect = oSectSf.get_rect()
        rect.center = (self.m_lRES[0] / 2, self.m_iSect_pos)
        self.m_oLayer20.blit(oSectSf, rect)

        # Rotate if vertical mode
        if self.m_iSide == 1:
            self.m_oLayer20 = pygame.transform.rotate(self.m_oLayer20, -90)
        elif self.m_iSide == 3:
            self.m_oLayer20 = pygame.transform.rotate(self.m_oLayer20, 90)

    def _render_layer21(self):
        # selected line
        self.m_oLayer21 = pygame.Surface(self.m_lRES, pygame.SRCALPHA)
        line = self._get_onscreen_menu_line()
        Y_POS = self.m_iMenu_pos + (line * self.m_iText_spc)

        oLine = self._render_line_menu(self.m_lLines[self.m_iLine])

        # append line surface to layer21 surface
        rect = oLine.get_rect()
        rect.midleft = (self.m_iText_lft, Y_POS)
        self.m_oLayer21.blit(oLine, rect)

        # Rotate if vertical mode
        if self.m_iSide == 1:
            self.m_oLayer21 = pygame.transform.rotate(self.m_oLayer21, -90)
        elif self.m_iSide == 3:
            self.m_oLayer21 = pygame.transform.rotate(self.m_oLayer21, 90)


    def _render_layer30(self):
        # layer30 pointer
        line = self._get_onscreen_menu_line()
        Y_POS = self.m_iMenu_pos + (line * self.m_iText_spc)
        self.m_oLayer30 = pygame.Surface(self.m_lRES, pygame.SRCALPHA)
        if not self.m_lPointer['pointer_render']:
            if type(self.dCFG['pointer']) is list:
                for item in self.dCFG['pointer']:
                    ptr = self._img_render(item)
                    self.m_lPointer['pointer_render'].append(ptr)
            else:
                ptr = self._img_render(self.dCFG['pointer'])
                self.m_lPointer['pointer_render'].append(ptr)

        ptr = self.m_lPointer['pointer_render'][self.m_lPointer['frame']]
        rect = ptr.get_rect()
        rect.midright = (self.m_iText_lft - 2, Y_POS)
        self.m_oLayer30.blit(ptr, rect)

        # Rotate if vertical mode
        if self.m_iSide == 1:
            self.m_oLayer30 = pygame.transform.rotate(self.m_oLayer30, -90)
        elif self.m_iSide == 3:
            self.m_oLayer30 = pygame.transform.rotate(self.m_oLayer30, 90)

    def _render_layer40(self):
        p_lList = []
        if self.m_lLayer40_core[0]:
            p_lList = self.m_lLayer40_core
        elif self.m_lLayer40[0]:
            p_lList = self.m_lLayer40

        try: self.prev_L40Input
        except: self.prev_L40Input = None

        if p_lList:
            if not self.m_oLayer40 or (self.prev_L40Input != p_lList[0]):
                if type(p_lList[0]) is str or type(p_lList[0]) is list:
                    self._render_info_layer(p_lList[0], p_lList[1])
                elif type(p_lList[0]) == pygame.Surface:
                    self.push_info_image(p_lList[0])
            self.prev_L40Input = p_lList[0]
        else:
            self.m_oLayer40 = None
            self.prev_L40Input = None

    def _check_text_change(self):
        p_bCheck = False
        if not self.m_oLayer20:
            p_bCheck = True
        elif self.m_oIndex.check_new_sub():
            self.m_iLine = 0
            p_bCheck = True
        else:
            return self.m_oWach.check(self.m_lLines, self.m_iLine, self.m_iMax_Lines)
        return p_bCheck

    def _check_line_change(self):
        p_bCheck = False
        try: self.m_bLine_Check
        except: self.m_bLine_Check = None
        if self.m_iLine != self.m_bLine_Check:
            self.m_bLine_Check = self.m_iLine
            p_bCheck = True
        return p_bCheck

    def _check_side_change(self):
        p_bCheck = False
        try: self.m_bSide_Check
        except: self.m_bSide_Check = None
        if self.m_iSide != self.m_bSide_Check:
            logging.info("cambio de orientacion")
            self.m_bSide_Check = self.m_iSide
            p_bCheck = True
        return p_bCheck

    def _check_pending_rest_reb(self):
        p_bCheck = False
        try: self.m_bRest_Check
        except: self.m_bRest_Check = None
        try: self.m_bRebo_Check
        except: self.m_bRebo_Check = None
        if self.m_bRest_Check != self.m_lRestart['restart']:
            self.m_bRest_Check = self.m_lRestart['restart']
            p_bCheck = True
        if self.m_bRebo_Check != self.m_lReboot['reboot']:
            self.m_bRebo_Check = self.m_lReboot['reboot']
            p_bCheck = True
            logging.info("layer0 update %s" % p_bCheck)
        return p_bCheck

    def quit(self):
        if self.m_lReboot['reboot']:
            self.m_lLayer40_core = ["Restarting System", "icon_info"]
            time.sleep(2)
        elif self.m_lRestart['restart']:
            self.m_lLayer40_core = ["Restarting ES", "icon_info"]
            time.sleep(2)
        self.m_bExit = True
        self.m_oJoyHandler.quit()
        while pygame.mixer.get_busy(): pass
        time.sleep(1.2)
        pygame.display.quit()
        pygame.mixer.quit()
        if self.m_lReboot['reboot']:
            os.system('sudo reboot')
        elif self.m_lRestart['restart']:
            restart_ES()
            time.sleep(6)
        sys.exit(0)

