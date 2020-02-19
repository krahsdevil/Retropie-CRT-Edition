#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
launcher controls.py.

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

import os, logging, time, threading
import pygame

from .core_paths import RETROPIECFG_PATH
from .file_helpers import ini_get

JOYCONFIG_PATH = os.path.join(RETROPIECFG_PATH, "all/retroarch/autoconfig")

CRT_UP      = 1
CRT_DOWN    = 2
CRT_LEFT    = 4
CRT_RIGHT   = 8
CRT_OK      = 16
CRT_CANCEL  = 32

CRT_BUTTON      = CRT_OK | CRT_CANCEL
CRT_DIRECTION   = CRT_UP | CRT_DOWN | CRT_LEFT | CRT_RIGHT

CRT_NONE    = 0
CRT_ZERO    = None

KEY_CFG     = {
    pygame.K_UP     : CRT_UP,
    pygame.K_DOWN   : CRT_DOWN,
    pygame.K_LEFT   : CRT_LEFT,
    pygame.K_RIGHT  : CRT_RIGHT,
    pygame.K_RETURN : CRT_OK,
    pygame.K_SPACE  : CRT_OK,
    pygame.K_LCTRL  : CRT_OK,
    pygame.K_ESCAPE : CRT_CANCEL,
    pygame.K_LALT : CRT_CANCEL,
}

HAT_CFG = {
    (1, 0)  : CRT_RIGHT,
    (0, 1)  : CRT_UP,
    (-1,0)  : CRT_LEFT,
    (0,-1)  : CRT_DOWN,
}

ABS_DIF        = 0.2
ABS_CTRL_STATE = False

class joystick(object):
    """
    joystick class for pygame/retropie
    need pygame already initialized
    """
    m_lJoys = []
    m_iNumJoys = 0
    m_iAxisTriggered = False
    def __init__(self):
        self.joy_daemon_watcher()

    def joy_daemon_watcher(self):
        oJoyWatcher = threading.Thread(target = self.joystick_detection)
        oJoyWatcher.setDaemon(True)
        oJoyWatcher.start()
        
    def joystick_detection(self):
        """ 
        This function will be continously checking if there is at least
        one joystick connected, if not of removed, will looking for it
        during all 'core_controls' module execution.
        Launched internally as daemon
        """
        p_iTime = 1
        p_iJoyNum = 4
        while True:
            if not self.m_iNumJoys:
                if pygame.joystick.get_init():
                    pygame.joystick.quit()
                pygame.joystick.init()
                try:
                    for j in range(0, p_iJoyNum):
                        self._initialize(j)
                        self.m_iNumJoys = j + 1
                except:
                    pass
                if self.m_iNumJoys:
                    logging.info("INFO: joysticks found: %i" % self.m_iNumJoys)
                    p_iTime = 5
            else:
                p_iCount = 0
                for j in range(0, p_iJoyNum):
                    try:
                        pygame.joystick.Joystick(j).quit()
                        pygame.joystick.Joystick(j).init()
                        p_iCount += 1
                    except:
                        pass
                if p_iCount == 0:
                    if self.m_iNumJoys > 0: 
                        logging.info("INFO: joysticks seems to be removed")
                    self.m_iNumJoys = 0
                    p_iTime = 1
            time.sleep(p_iTime)

    def _initialize(self, p_iJoy):
        jData = self._base_joy_config() #setting most standard parameters
        pygame.joystick.Joystick(p_iJoy).init()
        sJoyName = pygame.joystick.Joystick(p_iJoy).get_name()
        sCfgFile = os.path.join(JOYCONFIG_PATH, sJoyName + '.cfg')

        if not os.path.exists(sCfgFile):
            logging.info("WARNING: joy config not found!: %s" % sCfgFile)
        else:
            #getting ES custom config for joy
            #Try to get AXIS X in joystick config file
            axis_tmp = self._get_joy_cfg(sCfgFile, 'input_l_x_minus_axis')
            if not axis_tmp:
                axis_tmp = self._get_joy_cfg(sCfgFile, 'input_left_axis')
            if axis_tmp:
                jData['x']['axis'] = abs(int(axis_tmp, 10))
                jData['x']['value'] = ABS_DIF if "-" not in axis_tmp else -ABS_DIF
            #Try to get AXIS Y in joystick config file
            axis_tmp = self._get_joy_cfg(sCfgFile, 'input_l_y_minus_axis')
            if not axis_tmp:
                axis_tmp = self._get_joy_cfg(sCfgFile, 'input_up_axis')
            if axis_tmp:
                jData['y']['axis'] = abs(int(axis_tmp, 10))
                jData['y']['value'] = ABS_DIF if "-" not in axis_tmp else -ABS_DIF
            #Try to get BUTTON A in joystick config file
            btn_tmp = self._get_joy_cfg(sCfgFile, 'input_a_btn')
            if btn_tmp:
                jData['ok'] = int(btn_tmp)
            #Try to get BUTTON B in joystick config file
            btn_tmp = self._get_joy_cfg(sCfgFile, 'input_b_btn')
            if btn_tmp:
                jData['cancel'] = int(btn_tmp)
        self.m_lJoys.append(jData)

    def _get_joy_cfg(self, p_sCfgFile, p_sINI):
        temp = ini_get(p_sCfgFile, p_sINI)
        if temp:
            try:
                temp = temp.replace('"', '')
                logging.info("INFO: found value ini {%s} for %s" % (temp, p_sINI))
            except:
                logging.info("WARNING: not possible to find value for %s in %s" % (p_sINI, p_sCfgFile))
                return False
        return temp
        
    def _base_joy_config(self):
        #if config file is not found will apply this axis and 'standard' buttons
        jData = {'x': {}, 'y': {}}
        jData['axis_trigger'] = False
        jData['x']['axis'] = 0
        jData['x']['value'] = -ABS_DIF
        jData['y']['axis'] = 1
        jData['y']['value'] = -ABS_DIF
        jData['ok'] = 1
        jData['cancel'] = 0
        return jData

    def get_num(self):
        return len(self.m_lJoys)

    def get_key(self, p_oKey):
        try:
            return KEY_CFG[p_oKey]
        except:
            return CRT_NONE

    def get_button(self, p_iDevice, p_iButton):
        if self.m_lJoys[p_iDevice]['ok'] == p_iButton:
            return CRT_OK
        elif self.m_lJoys[p_iDevice]['cancel'] == p_iButton:
            return CRT_CANCEL
        #logging.info("jb-ign: %i %i" % (p_iDevice, p_iButton))
        return CRT_NONE

    def check_axis(self, p_iDevice, p_fValue, p_iButton):
        global ABS_CTRL_STATE
        if abs(p_fValue) > ABS_DIF:
            if not ABS_CTRL_STATE:
                ABS_CTRL_STATE = True
                return p_iButton
        else:
            ABS_CTRL_STATE = False
        return CRT_NONE
        
    def get_axis(self, p_iDevice, p_iAxis, p_fValue):
        if self.m_lJoys[p_iDevice]['x']['axis'] == p_iAxis:
            if p_fValue > 0:
                return self.check_axis(p_iDevice, p_fValue, CRT_RIGHT)
            else:
                return self.check_axis(p_iDevice, p_fValue, CRT_LEFT)
        if self.m_lJoys[p_iDevice]['y']['axis'] == p_iAxis:
            if p_fValue > 0:
                return self.check_axis(p_iDevice, p_fValue, CRT_DOWN)
            else:
                return self.check_axis(p_iDevice, p_fValue, CRT_UP)
        return CRT_NONE

    def get_hat(self, p_lValue):
        try:
            return HAT_CFG[p_lValue]
        except:
            return CRT_NONE

    def event_wait(self):
        while True:
            event = pygame.event.wait()
            pygame.event.clear()
            if event.type == pygame.KEYDOWN:
                return self.get_key(event.key)
            elif event.type == pygame.JOYBUTTONDOWN:
                return self.get_button(event.joy, event.button)
            elif event.type == pygame.JOYHATMOTION:
                return self.get_hat(event.value)
            elif event.type == pygame.JOYAXISMOTION and event.axis < 2:
                return self.get_axis(event.joy, event.axis, event.value)