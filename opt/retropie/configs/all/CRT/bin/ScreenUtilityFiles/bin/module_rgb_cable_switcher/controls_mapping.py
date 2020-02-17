#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
pi2jamma_controls.py

Pi2Jamma key controls configurator for retroarch and ES by -Krahs-

https://github.com/krahsdevil/crt-for-retropie/

Copyright (C)  2018/2020 -krahs- - https://github.com/krahsdevil/
Copyright (C)  2020 dskywalk - http://david.dantoine.org

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

import os, sys, logging
import xml.etree.ElementTree as ET

CRT_PATH = "/opt/retropie/configs/all/CRT"
RESOURCES_PATH = os.path.join(CRT_PATH, "bin/GeneralModule")
sys.path.append(RESOURCES_PATH)

from launcher_module.core_paths import *
from launcher_module.file_helpers import *

ADVMAMECFG_FILE = os.path.join(RETROPIECFG_PATH, "mame-advmame/advmame.rc")

class CTRLSMgmt(object):
    """
    This class for keyboard configuration for PI2JAMMA is based on MAME 
    KEYBOARD defaults. Whether pikeyd165.conf or rest of software (retroarch,
    EmulationStation) will be configured in the same way:

            PLAYER 1                           PLAYER 2
    -----------------------              -------------------
    Label           Key                  Label           Key
    --------        -------              --------        ---
    P1 START        1                    P2 START        2
    P1 COIN         6                    P2 COIN         6
    P1 RIGHT        R arrow              P2 RIGHT        G    
    P1 LEFT         L arrow              P2 LEFT         D
    P1 UP           U arrow              P2 UP           R
    P1 DOWN         D arrow              P2 DOWN         F
    P1 SW 1         L-ctrl               P2 SW 1         A    
    P1 SW 2         L-alt                P2 SW 2         S    
    P1 SW 3         space                P2 SW 3         Q    
    P1 SW 4         L-shift              P2 SW 4         W    
    P1 SW 5         Z                    P2 SW 5         I
    P1 SW 6         X                    P2 SW 6         K
    
    """
    # player 1 keyboard retroarch default config
    m_lRArchKBP1DF = ({'line': 'input_player1_b', 'value': 'z'},           #P1BTN1
                      {'line': 'input_player1_a', 'value': 'x'},           #P1BTN2
                      {'line': 'input_player1_x', 'value': 's'},           #P1BTN3
                      {'line': 'input_player1_y', 'value': 'a'},           #P1BTN4
                      {'line': 'input_player1_l', 'value': 'q'},           #P1BTN5
                      {'line': 'input_player1_r', 'value': 'w'},           #P1BTN6
                      {'line': 'input_player1_start', 'value': 'enter'},   #P1START
                      {'line': 'input_player1_select', 'value': 'rshift'}, #P1COIN
                      {'line': 'input_player1_left', 'value': 'left'},     #P1LEFT
                      {'line': 'input_player1_right', 'value': 'right'},   #P1RIGHT
                      {'line': 'input_player1_up', 'value': 'up'},         #P1UP
                      {'line': 'input_player1_down', 'value': 'down'})     #P1DOWN

    # player 1 keyboard retroarch config for pi2jamma
    m_lRArchKBP1 = ({'line': 'input_player1_b', 'value': 'ctrl'},          #P1BTN1
                    {'line': 'input_player1_a', 'value': 'alt'},           #P1BTN2
                    {'line': 'input_player1_x', 'value': 'space'},         #P1BTN3
                    {'line': 'input_player1_y', 'value': 'shift'},         #P1BTN4
                    {'line': 'input_player1_l', 'value': 'z'},             #P1BTN5
                    {'line': 'input_player1_r', 'value': 'x'},             #P1BTN6
                    {'line': 'input_player1_start', 'value': 'num1'},      #P1START
                    {'line': 'input_player1_select', 'value': 'num5'},     #P1COIN
                    {'line': 'input_player1_left', 'value': 'left'},       #P1LEFT
                    {'line': 'input_player1_right', 'value': 'right'},     #P1RIGHT
                    {'line': 'input_player1_up', 'value': 'up'},           #P1UP
                    {'line': 'input_player1_down', 'value': 'down'})       #P1DOWN
                 
    # player 2 keyboard retroarch config for pi2jamma
    m_lRArchKBP2 = ({'line': 'input_player2_b', 'value': 'a'},             #P2BTN1
                    {'line': 'input_player2_a', 'value': 's'},             #P2BTN2
                    {'line': 'input_player2_x', 'value': 'q'},             #P2BTN3
                    {'line': 'input_player2_y', 'value': 'w'},             #P2BTN4
                    {'line': 'input_player2_l', 'value': 'i'},             #P2BTN5
                    {'line': 'input_player2_r', 'value': 'k'},             #P2BTN6
                    {'line': 'input_player2_start', 'value': 'num2'},      #P2START
                    {'line': 'input_player2_select', 'value': 'num6'},     #P2COIN
                    {'line': 'input_player2_left', 'value': 'd'},          #P2LEFT
                    {'line': 'input_player2_right', 'value': 'g'},         #P2RIGHT
                    {'line': 'input_player2_up', 'value': 'r'},            #P2UP
                    {'line': 'input_player2_down', 'value': 'f'})          #P2DOWN
                  
    """
    Variable 'm_lRarchKBDS':
    Will disable some retroarch keyboard hotkeys to avoid conflict with
    pi2jamma keystrokes and also make sure some other needed options and 
    are well configured:
        line  : config entry to search
        value : standard value when pi2jamma is disabled
        dis   : value to apply when pi2jamma is enabled
    """
    # hotkeys keyboard retroarch disabling for conflicts
    m_lRarchKBDS = ({'line': 'input_toggle_fast_forward',
                     'value': 'space', 'dis': 'nul'},
                    {'line': 'input_toggle_fullscreen',
                     'value': 'f', 'dis': 'nul'},
                    {'line': 'input_rewind', 
                     'value': 'r', 'dis': 'nul'},
                    {'line': 'input_netplay_flip_players', 
                     'value': 'i', 'dis': 'nul'},
                    {'line': 'input_frame_advance', 
                     'value': 'k', 'dis': 'nul'},
                    {'line': 'input_enable_hotkey', 
                     'value': 'nul', 'dis': 'nul'},
                    {'line': 'input_exit_emulator', 
                     'value': 'escape', 'dis': 'escape'},
                    {'line': 'input_menu_toggle', 
                     'value': 'f1', 'dis': 'f1'})
                    
    # emulationstation keyboard configuration xml for PI2JAMMA
    m_lESP2JInputs = ({'name': 'a', 'type': 'key', 'id': '1073742048', 'value': '1'},
                      {'name': 'b', 'type': 'key', 'id': '1073742050', 'value': '1'},
                      {'name': 'down', 'type': 'key', 'id': '1073741905', 'value': '1'},
                      {'name': 'hotkeyenable', 'type': 'key', 'id': '49', 'value': '1'},
                      {'name': 'left', 'type': 'key', 'id': '1073741904', 'value': '1'},
                      {'name': 'leftshoulder', 'type': 'key', 'id': '122', 'value': '1'},
                      {'name': 'right', 'type': 'key', 'id': '1073741903', 'value': '1'},
                      {'name': 'rightshoulder', 'type': 'key', 'id': '120', 'value': '1'},
                      {'name': 'select', 'type': 'key', 'id': '53', 'value': '1'},
                      {'name': 'start', 'type': 'key', 'id': '49', 'value': '1'},
                      {'name': 'up', 'type': 'key', 'id': '1073741906', 'value': '1'},
                      {'name': 'x', 'type': 'key', 'id': '32', 'value': '1'},
                      {'name': 'y', 'type': 'key', 'id': '1073742049', 'value': '1'})
                      
    # emulationstation keyboard configuration xml for STANTARD KEYBOARD (not for play)
    m_lESKBDInputs = ({'name': 'a', 'type': 'key', 'id': '13', 'value': '1'},
                      {'name': 'b', 'type': 'key', 'id': '27', 'value': '1'},
                      {'name': 'down', 'type': 'key', 'id': '1073741905', 'value': '1'},
                      {'name': 'hotkeyenable', 'type': 'key', 'id': '49', 'value': '1'},
                      {'name': 'left', 'type': 'key', 'id': '1073741904', 'value': '1'},
                      {'name': 'right', 'type': 'key', 'id': '1073741903', 'value': '1'},
                      {'name': 'select', 'type': 'key', 'id': '53', 'value': '1'},
                      {'name': 'start', 'type': 'key', 'id': '49', 'value': '1'},
                      {'name': 'up', 'type': 'key', 'id': '1073741906', 'value': '1'})
                      
    # advmame keyboard configuration User Interface
    m_lADVMAMEKBDUI = ({'line': 'input_map[ui_select]',
                        'value': 'auto', 'dis': 'keyboard[0,enter] or keyboard[0,lcontrol]'},
                       {'line': 'input_map[ui_cancel]',
                        'value': 'auto', 'dis': 'keyboard[0,esc] or keyboard[0,backspace]'})

    m_bChange = False

    def pi2jamma_enable_controls(self):
        self.inputs_retroarch_pi2jamma_enable()
        self.inputs_emulationstation_pi2jamma_enable()
        self.inputs_advmame_pi2jamma_enable()
        return self.m_bChange

    def pi2jamma_disable_controls(self):
        self.inputs_retroarch_pi2jamma_disable()
        self.inputs_emulationstation_pi2jamma_disable()
        self.inputs_advmame_pi2jamma_disable()
        return self.m_bChange

    def inputs_retroarch_pi2jamma_enable(self):
        """ All actions to enable pi2jamma in retroarch """
        self._inputs_retroarch_ctrls(self.m_lRArchKBP1, True)
        self._inputs_retroarch_ctrls(self.m_lRArchKBP2, True)
        self._inputs_retroarch_hotkeys(self.m_lRarchKBDS, True)
        
    def inputs_retroarch_pi2jamma_disable(self):
        """ All actions to enable pi2jamma in retroarch """
        self._inputs_retroarch_ctrls(self.m_lRArchKBP1DF, True)
        self._inputs_retroarch_ctrls(self.m_lRArchKBP2, False)
        self._inputs_retroarch_hotkeys(self.m_lRarchKBDS, False)
    
    def _inputs_retroarch_ctrls(self, p_lInputs, p_bEnable):
        """ 
        This function enable or disable keyboard controls for pi2jamma in
        main retroarch.cfg. If input are not defined will be created.
        For enable or disable line will be commented or uncommented.
        p_bEnable = True Enable keyboard inputs
        p_bEnable = False Enable keyboard inputs
        """
        if not self._check_file(RETROARCHCFG_FILE):
            return
        for key in p_lInputs:
            p_Return = self._ini_get(RETROARCHCFG_FILE, key['line'])
            p_bChange = False
            p_sCFGLine = '%s = "%s"' % (key['line'], key['value'])
            if not p_bEnable:
                p_sCFGLine = '# ' + p_sCFGLine

            if p_Return[0] == False:
                add_line(RETROARCHCFG_FILE, p_sCFGLine)
            else:
                if not p_Return[1] and not p_bEnable:
                    p_bChange = True
                elif p_Return[1] and p_bEnable:
                    p_bChange = True
                if key['value'] != p_Return[2]:
                    p_bChange = True
                # edit line if needed
                if p_bChange:
                    modify_line(RETROARCHCFG_FILE, 
                                      key['line'] + ' ', p_sCFGLine)
    
    def _inputs_retroarch_hotkeys(self, p_lInputs, p_bEnable, p_bComment = False):
        """ 
        This function enable or disable some retroarch hotkey controls
        to avoid keyboard keystrokes conflicts.
        p_bEnable = True    Enable for pi2jamma keyboard inputs
        p_bEnable = False   Disable for pi2jamma keyboard inputs
        """
        if not self._check_file(RETROARCHCFG_FILE):
            return
        for key in p_lInputs:
            p_Return = self._ini_get(RETROARCHCFG_FILE, key['line'])
            p_bChange = False
            p_sValue = '"%s"' % key['dis']
            p_sCFGLine = '%s = ' % key['line']
            if not p_bEnable:
                if p_bComment:
                    p_sCFGLine = '# ' + p_sCFGLine # Comment line
                p_sValue = '"%s"' % key['value']

            p_sCFGLine += '%s' % p_sValue

            if p_Return[0] == False:
                add_line(RETROARCHCFG_FILE, p_sCFGLine)
            else:
                if p_Return[1] and p_bEnable:
                    p_bChange = True
                if p_Return[2] != p_sValue.strip('"'):
                        p_bChange = True
                if p_bChange:
                    modify_line(RETROARCHCFG_FILE, 
                                      key['line'] + ' ', p_sCFGLine)

    def inputs_advmame_pi2jamma_enable(self):
        """ All actions to enable pi2jamma in advmame """
        self._inputs_advmame_keys(self.m_lADVMAMEKBDUI, True)
        
    def inputs_advmame_pi2jamma_disable(self):
        """ All actions to enable pi2jamma in advmame """
        self._inputs_advmame_keys(self.m_lADVMAMEKBDUI, False)

    def _inputs_advmame_keys(self, p_lInputs, p_bEnable):
        """ 
        This function some advmame hotkey controls like UI select.
        p_bEnable = True    Enable for pi2jamma keyboard inputs
        p_bEnable = False   Disable for pi2jamma keyboard inputs
        """
        if not self._check_file(ADVMAMECFG_FILE):
            return
        for key in p_lInputs:
            p_Return = self._ini_get(ADVMAMECFG_FILE, key['line'])
            p_bChange = False
            p_sValue = key['dis']
            p_sCFGLine = key['line'] + " "
            if not p_bEnable:
                p_sValue = key['value']
            p_sCFGLine += p_sValue

            if p_Return[0] == False:
                add_line(ADVMAMECFG_FILE, p_sCFGLine)
            else:
                if p_Return[1] and p_bEnable:
                    p_bChange = True
                if p_Return[2]:
                    p_Return[2] = p_Return[2].replace(']or', '] or ')
                    if p_Return[2] != p_sValue:
                        p_bChange = True
                        if not p_bEnable:
                            # don't change if custom kbd/joy found
                            p_bChange = True if p_Return[2] == key['dis'] else False
                if p_bChange:
                    modify_line(ADVMAMECFG_FILE, 
                                      key['line'] + ' ', p_sCFGLine)
   
    def inputs_emulationstation_pi2jamma_enable(self):
        """ All actions to enable pi2jamma in emulationstation """
        self.inputs_emulationstation_ctrls(True)
        
    def inputs_emulationstation_pi2jamma_disable(self):
        """ All actions to disable pi2jamma in emulationstation """
        self.inputs_emulationstation_ctrls(False)

    def inputs_emulationstation_ctrls(self, p_bEnable):
        """
        This function clean or install keyboard config for pi2jamma
        in es_input.cfg. Also will try to backup and/or restore any user's
        custom keyboard configuration 
        p_bEnable = True    Enable pi2jamma keyboard inputs and backup
                            any pre-existent custom keyboard config.
        p_bEnable = False   Remove any pi2jamma keyboard inputs and restore
                            any pre-existent custom keyboard config. 
        """
        p_bXMLSave = False
        p_lCtmDev = []
        p_lBckDev = []
        p_lP2JDev = []
        
        # create emulationstation 'es_input.cfg' file if doesn't exist 
        if not self._check_file(ESCTRLS_FILE):
            self._emulationstation_create_inputs_file()
        # analize xml configurations
        else:
            tree = ET.parse(ESCTRLS_FILE)
            root = tree.getroot()
            p_lClean = []
            for device in root:
                if device.attrib['type'].lower() == "keyboard":
                    if device.attrib['deviceGUID'] == 'disabled':
                        p_lBckDev.append(device)
                    else:
                        if 'class' in device.attrib:
                            if device.attrib['class'].lower() == "pi2jamma":
                                p_lP2JDev.append(device)
                            elif device.attrib['class'].lower() == "custom":
                                p_lCtmDev.append(device)
                        else:
                            p_lCtmDev.append(device)

            # always clean pi2jamma config even if already exist
            # will be applied again at the end if p_bEnable = True
            for device in p_lP2JDev:
                root.remove(device)
                p_bXMLSave = True

            if p_bEnable:
                if len(p_lCtmDev) > 1:
                    for device in p_lCtmDev:
                        root.remove(device)
                        p_bXMLSave = True
                elif len(p_lCtmDev) == 1:
                    for device in p_lBckDev:
                        root.remove(device)
                    p_lCtmDev[0].attrib['class'] = 'custom'
                    p_lCtmDev[0].attrib['deviceGUID'] = 'disabled'
                    p_lCtmDev[0].attrib['deviceName'] = 'Keyboard'
                    p_lCtmDev[0].attrib['type'] = 'keyboard'
                    p_bXMLSave = True
            else:
                if len(p_lBckDev) > 1:
                    for device in p_lBckDev:
                        root.remove(device)
                        p_bXMLSave = True
                    for device in p_lCtmDev:
                        root.remove(device)
                        p_bXMLSave = True                    
                elif len(p_lBckDev) == 1:
                    for device in p_lCtmDev:
                        root.remove(device)
                    p_lBckDev[0].attrib['class'] = 'custom'
                    p_lBckDev[0].attrib['deviceGUID'] = '-1'
                    p_lBckDev[0].attrib['deviceName'] = 'Keyboard'
                    p_lBckDev[0].attrib['type'] = 'keyboard'
                    p_bXMLSave = True

            # save 'es_input.cfg' only if any change happens
            if p_bXMLSave:
                tree.write(ESCTRLS_FILE, encoding='UTF-8')

            # once xml is reorganized, create clean pi2jamma config
            if p_bEnable:
                self._inputs_emulationstation_ctrls_create(self.m_lESP2JInputs)
                self.m_bChange = True

    def _emulationstation_create_inputs_file(self):
        root = ET.Element("inputList")
        root.text = "\n  "
        p_sNewAction = ET.Element("inputAction")
        p_sNewAction.set("type", "onfinish")
        p_sNewAction.text = ("\n    ")
        p_sNewAction.tail = "\n"
        p_sNewCommand = ET.SubElement(p_sNewAction, "command")
        p_sNewCommand.text = "/opt/retropie/supplementary/emulationstation"
        p_sNewCommand.text += "/scripts/inputconfiguration.sh"
        p_sNewCommand.tail = "\n  "
        root.append(p_sNewAction)
        tree = ET.ElementTree(root)
        tree.write(ESCTRLS_FILE, encoding='UTF-8')

    def _inputs_emulationstation_ctrls_create(self, p_lESInputs):
        """ Create keyboard inputs for manage EmulationStation"""
        # 1 tab = 2 x spaces
        # \n    = new line
        tree = ET.parse(ESCTRLS_FILE)
        root = tree.getroot()
        p_sNewDevice = ET.Element("inputConfig")
        p_sNewDevice.set("deviceGUID", "-1")
        p_sNewDevice.set("deviceName", "Keyboard")
        p_sNewDevice.set("type", "keyboard")
        p_sNewDevice.set("class", "pi2jamma")
        p_sNewDevice.tail = "\n"
        p_sNewDevice.text = "\n    "
        for input in p_lESInputs:
            p_sNewAtb = ET.SubElement(p_sNewDevice, "input")
            for attrib in input:
                p_sNewAtb.set(attrib, input[attrib])
                p_sNewAtb.tail = "\n    " 
        p_sNewDevice[-1].tail = "\n  "  # change last atb tab
        if len(root) > 0:               # at least one element under root
            root[-1].tail = "\n  "      # Edit the previous element's tail
        root.append(p_sNewDevice)       # Add the element to the tree.
        tree.write(ESCTRLS_FILE, encoding='UTF-8')

    def _ini_get(self, p_sFile, p_sFindMask):
        """
        This function will return three values:
        p_lCheck = [value0, value1, value2]:
            value0 = True or False; True if ini value was found
            value1 = True or False; True if line is commented with '#'
            value2 = String; Value of requested ini 
        """
        p_lCheck = [False, False, None]
        if not os.path.isfile(p_sFile):
            logging.info('WARNING: %s NOT found' % p_sFile)
            return p_lCheck
        with open(p_sFile, "r") as f:
            for line in f:
                line = line.strip().replace('=',' ').replace(' or ','or')
                lValues = line.strip().replace('# ','#').split(' ')
                if p_sFindMask == lValues[0].strip('# '):
                    p_lCheck[0] = True
                    if line[:1] == '#':
                        p_lCheck[1] = True
                        logging.info('WARNING: %s is ' % p_sFindMask + \
                                     'commented or without value')
                    try:
                        p_lCheck[2] = lValues[1].strip('" ')
                        logging.info('INFO: %s=' % p_sFindMask + \
                                      '%s' % p_lCheck[2])
                    except:
                        logging.info('WARNING: %s has ' % p_sFindMask + \
                                     'not value')

        if not p_lCheck[0]:
            logging.info('WARNING: %s NOT found' % p_sFindMask)
        return p_lCheck

    def xinmo_usb_driver_enable(self):
        sXinMoCfg = "usbhid.quirks=0x16c0:0x05e1:0x040"
        sTempFile = generate_random_temp_filename(CMDLINE_FILE)
        os.system('cp %s %s' %(CMDLINE_FILE, sTempFile))
        bFound = False
        bReboot = False
        with open(sTempFile, "r+") as f:
            new_file = f.read().replace('\n', ' ').strip()
            lValues = new_file.strip().split(' ')
            if sXinMoCfg in lValues: bFound = True
            if not bFound:
                new_file += " " + sXinMoCfg
                f.seek(0)
                f.truncate(0)
                f.write(new_file)
                f.close()
                # upload file to /boot and set reboot to True
                bReboot = True
                os.system('sudo cp %s %s' %(sTempFile, CMDLINE_FILE))
        os.system('rm %s' % sTempFile)
        return bReboot
        
    def _check_file(self, p_sFile):
        if os.path.exists(p_sFile):
            return True
        return False

