#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
launcher controls.py.

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

import os, logging, time, threading, commands
import pygame

from .core_paths import RETROPIE_CFG_PATH
from .file_helpers import ini_get

JOYCONFIG_PATH = os.path.join(RETROPIE_CFG_PATH, "all/retroarch/autoconfig")

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

ABS_DIF = 0.7
ABS_CTRL_STATE = False

class joystick(object):
    """
    joystick class for pygame/retropie
    need pygame already initialized
    """
    m_lJoys = []
    m_iNumJoys = 0
    m_iAxisTriggered = False
    m_bUnload = False
    
    m_oClock = None
    m_oScreen = None

    def __init__(self):
        self._set_clock()
        self.joy_daemon_watcher()

    def init(self):
        self.__init__()

    def _set_clock(self):
        self.m_oClock = pygame.time.Clock()

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
        self.m_bUnload = False
        p_iJoyNum = 2
        while not self.m_bUnload:
            p_iCount = 0
            p_lJoyRem = []
            p_lJoyAdd = []
            # detect how many joys are connected reading /dev/input
            for j in range(0, p_iJoyNum):
                if os.path.exists("/dev/input/js%s" % j):
                    p_lJoyAdd.append(j) # joy number existent
                    p_iCount += 1
                else: p_lJoyRem.append(j) # joy number missing
            
            # if there is MORE joys configured than counted
            if self.m_iNumJoys > p_iCount:
                for joy in p_lJoyRem:
                    try: self._remove(joy)
                    except: pass

            # if there is LESS joys configured than counted            
            elif self.m_iNumJoys < p_iCount:
                # reset pygame joystick module to load all joys
                if pygame.joystick.get_init():
                    pygame.joystick.quit()
                if self.m_bUnload: break
                pygame.joystick.init()
                # load all joys detected in system
                self.m_lJoys = []       # cleaning db buttons of joys
                try:
                    for joy in p_lJoyAdd:
                        self._initialize(joy)
                except: pass

            # detecting how many joystick are loaded in pygame
            self.m_iNumJoys = 0
            for j in range(0, p_iJoyNum):
                try:
                    if pygame.joystick.Joystick(j).get_init(): self.m_iNumJoys += 1
                except: pass
            self.m_oClock.tick(20)
            pygame.time.wait(0)

        for i in range(0, len(self.m_lJoys) + 1):
            try: pygame.joystick.Joystick.quit(i)
            except: pass
        logging.info("INFO: unloaded joystick daemon")

    def quit(self):
        self.m_bUnload = True

    def _remove(self, p_iJoy):
        pygame.joystick.Joystick(p_iJoy).quit()
        logging.info("INFO: disconnected device at /dev/input/js%s" % p_iJoy)
        logging.info("INFO: unloaded joystick %s" % self.m_lJoys[p_iJoy]['name'])
            
    def _initialize(self, p_iJoy):
        pygame.joystick.Joystick(p_iJoy).init()
        logging.info("INFO: connected device at /dev/input/js%s" % p_iJoy)
        sJoyName = pygame.joystick.Joystick(p_iJoy).get_name()
        logging.info("INFO: loading joystick %s" % sJoyName)
        self._joy_configuration(p_iJoy)
 
    def _joy_configuration(self, p_iJoy):
        jData = self._joy_base_cfg(p_iJoy) #setting default config
        sJoyName = pygame.joystick.Joystick(p_iJoy).get_name()
        sCfgFile = os.path.join(JOYCONFIG_PATH, sJoyName + '.cfg')

        if not os.path.exists(sCfgFile):
            logging.info("WARNING: joy config not found!: %s" % sCfgFile)
        else:
            #getting ES custom config for joy
            #Try to get AXIS X in joystick config file
            axis_tmp = self._joy_get_cfg(sCfgFile, 'input_l_x_minus_axis')
            if not axis_tmp:
                axis_tmp = self._joy_get_cfg(sCfgFile, 'input_left_axis')
            if axis_tmp:
                jData['x']['axis'] = abs(int(axis_tmp, 10))
                jData['x']['value'] = ABS_DIF if "-" not in axis_tmp else -ABS_DIF
            #Try to get AXIS Y in joystick config file
            axis_tmp = self._joy_get_cfg(sCfgFile, 'input_l_y_minus_axis')
            if not axis_tmp:
                axis_tmp = self._joy_get_cfg(sCfgFile, 'input_up_axis')
            if axis_tmp:
                jData['y']['axis'] = abs(int(axis_tmp, 10))
                jData['y']['value'] = ABS_DIF if "-" not in axis_tmp else -ABS_DIF
            #Try to get BUTTON A in joystick config file
            btn_tmp = self._joy_get_cfg(sCfgFile, 'input_a_btn')
            if btn_tmp:
                jData['ok'] = int(btn_tmp)
            #Try to get BUTTON B in joystick config file
            btn_tmp = self._joy_get_cfg(sCfgFile, 'input_b_btn')
            if btn_tmp:
                jData['cancel'] = int(btn_tmp)
        self.m_lJoys.append(jData)

    def _joy_get_cfg(self, p_sCfgFile, p_sINI):
        temp = ini_get(p_sCfgFile, p_sINI)
        if temp:
            try:
                temp = temp.replace('"', '')
                logging.info("INFO: found %s = %s" % (p_sINI, temp))
            except:
                logging.info("WARNING: value no found for %s in %s" % (p_sINI, p_sCfgFile))
                return False
        return temp
        
    def _joy_base_cfg(self, p_iJoy):
        #if config file is not found will apply this axis and 'standard' buttons
        jData = {'x': {}, 'y': {}}
        jData['axis_trigger'] = False
        jData['x']['axis'] = 0
        jData['x']['value'] = -ABS_DIF
        jData['y']['axis'] = 1
        jData['y']['value'] = -ABS_DIF
        jData['ok'] = 1
        jData['cancel'] = 0
        jData['name'] = pygame.joystick.Joystick(p_iJoy).get_name()
        return jData

    def get_num(self):
        return len(self.m_lJoys)

    def get_key(self, p_oKey):
        try: return KEY_CFG[p_oKey]
        except: return None

    def get_button(self, p_iDevice, p_iButton):
        if len(self.m_lJoys) == 0: return None
        if self.m_lJoys[p_iDevice]['ok'] == p_iButton: return CRT_OK
        elif self.m_lJoys[p_iDevice]['cancel'] == p_iButton: return CRT_CANCEL
        #logging.info("jb-ign: %i %i" % (p_iDevice, p_iButton))
        return None

    def get_axis(self, p_iDevice, p_iAxis, p_fValue):
        global ABS_CTRL_STATE
        if len(self.m_lJoys) == 0: return None
        fValue = round(float(p_fValue), 1)
        #logging.info("jb-ign: %i %i %s" % (p_iDevice, p_iAxis, str(fValue)))

        if abs(fValue) < ABS_DIF:
            ABS_CTRL_STATE = False
            return None
        elif ABS_CTRL_STATE: return None
            
        if self.m_lJoys[p_iDevice]['x']['axis'] == p_iAxis:
            ABS_CTRL_STATE = True
            if fValue > self.m_lJoys[p_iDevice]['x']['value']:
                return CRT_RIGHT
            else: return CRT_LEFT
        if self.m_lJoys[p_iDevice]['y']['axis'] == p_iAxis:
            ABS_CTRL_STATE = True
            if fValue > self.m_lJoys[p_iDevice]['y']['value']:
                return CRT_DOWN
            else: return CRT_UP
        return None

    def get_hat(self, p_lValue):
        try: return HAT_CFG[p_lValue]
        except: return None

    def _get_screen_resolution(self):
        """ main function to get screen resolution """
        commandline = "cat /sys/class/graphics/fb0/virtual_size"
        output = commands.getoutput(commandline)
        VirtRes = output.replace(',',' ').split(' ')
        RES_X = int(VirtRes[0])
        RES_Y = int(VirtRes[1])
        return (RES_X, RES_Y)

    def event_wait(self):
        while True:
            for event in pygame.event.get():
                if self.m_bUnload: break
                if event.type == pygame.KEYDOWN:
                    input = self.get_key(event.key)
                    if input: return input
                elif event.type == pygame.JOYBUTTONDOWN:
                    input = self.get_button(event.joy, event.button)
                    if input: return input
                elif event.type == pygame.JOYHATMOTION:
                    input = self.get_hat(event.value)
                    if input: return input
                elif event.type == pygame.JOYAXISMOTION:
                    input = self.get_axis(event.joy, event.axis, event.value)
                    if input: return input
            self.m_oClock.tick(20)
            pygame.time.wait(0)