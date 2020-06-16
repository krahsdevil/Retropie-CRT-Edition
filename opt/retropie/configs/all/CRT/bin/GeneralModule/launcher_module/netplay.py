#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Netplay configuration

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

import sys, os, time, commands
import logging, re

sys.dont_write_bytecode = False

from file_helpers import ini_get, ini_set, add_line, \
                         touch_file, modify_line, ini_getlist
from core_paths import *

class netplay(object):
    NETPLAY_CFG = ['__netplaymode="H"',
                   '__netplayport="55435"',
                   '__netplayhostip="192.168.0.1"',
                   '__netplayhostip_cfile=""',
                   '__netplaynickname="\'RP_CRT_Edition\'"',
                   ]

    ini_mode = '__netplaymode'
    ini_port = '__netplayport'
    ini_host = '__netplayhostip'
    ini_nick = '__netplaynickname'
    
    def __init__(self):
        self._check_netplay_cfg()
        pass
        
    def _check_netplay_cfg(self):
        if not os.path.exists(CRT_NETPLAY_FILE):
            touch_file(CRT_NETPLAY_FILE)
            for line in NETPLAY_CFG:
                add_line(CRT_NETPLAY_FILE, line)

    def enable(self):
        ini_set(CRT_UTILITY_FILE, "netplay", "true")
        return self.status()

    def disable(self):
        ini_set(CRT_UTILITY_FILE, "netplay", "false")
        return self.status()
        
    def status(self):
        value = ini_get(CRT_UTILITY_FILE, "netplay")
        if value.lower() == "true": return True
        elif value.lower() == "false": return False
        return None

    def mode(self, p_sMode):
        if p_sMode.lower() == "host": 
            line = self.ini_mode + '="H"'
            value = "H"
        elif p_sMode.lower() == "client": 
            line = self.ini_mode + '="C"'
            value = "C"
        else:
            logging.info("INFO: no valid mode: host or client")
            return False
        modify_line(CRT_NETPLAY_FILE, self.ini_mode, line)
        new = self.get_mode()
        if new == p_sMode.lower(): return new
        logging.info("INFO: %s wrong edited" % self.ini_mode)
        return False

    def get_mode(self):
        value = ini_get(CRT_NETPLAY_FILE, self.ini_mode)
        if not value: 
            self._add_miss_ini(self.ini_mode)
            value = ini_get(CRT_NETPLAY_FILE, self.ini_mode)
        if value == value: 
            if value == "H": return "host"
            elif value == "C": return "client"
        return value
    
    def port(self, p_sPort):
        try: 
            num = int(p_sPort)
            if num < 0 or num > 65535: return False
        except:
            logging.info("INFO: incorrect port")
            return False
        line = self.ini_port + '=' + '"%s"' % p_sPort
        modify_line(CRT_NETPLAY_FILE, self.ini_port, line)
        new = self.get_port()
        if new == p_sPort: return new
        logging.info("INFO: %s wrong edited" % self.ini_port)
        return False
        
    def get_port(self):
        value = ini_get(CRT_NETPLAY_FILE, self.ini_port)
        if not value: 
            self._add_miss_ini(self.ini_port)
            value = ini_get(CRT_NETPLAY_FILE, self.ini_port)        
        return value

    def nick(self, p_sNick):
        line = self.ini_nick + '=' + '"\'%s\'"' % p_sNick
        modify_line(CRT_NETPLAY_FILE, self.ini_nick, line)
        new = self.get_nick()
        if new == p_sNick: return new
        logging.info("INFO: %s wrong edited" % self.ini_nick)
        return False
        
    def get_nick(self):
        value = ini_getlist(CRT_NETPLAY_FILE, self.ini_nick)
        if not value: 
            self._add_miss_ini(self.ini_nick)
            value = ini_getlist(CRT_NETPLAY_FILE, self.ini_nick)
        value = " ".join(value).replace("'", '')
        if " " in value: 
            value = value.replace(" ", '')
            modify_line(CRT_NETPLAY_FILE, self.ini_nick, value)
        return value

    def host(self, p_sHost):
        if not self.check_ip_format(p_sHost): return False
        line = self.ini_host + '=' + '"%s"' % p_sHost
        modify_line(CRT_NETPLAY_FILE, self.ini_host, line)
        new = self.get_host()
        if new == p_sHost: return new
        logging.info("INFO: %s wrong edited" % self.ini_host)
        return False
        
    def get_host(self):
        value = ini_get(CRT_NETPLAY_FILE, self.ini_host)
        if not value: 
            self._add_miss_ini(self.ini_host)
            value = ini_get(CRT_NETPLAY_FILE, self.ini_host)
        if not self.check_ip_format(value): 
            line = self.ini_host + '=' + '"192.168.0.1"'
            modify_line(CRT_NETPLAY_FILE, self.ini_host, line)
            value = "192.168.0.1"
        return value

    def stateless_enable(self):
        ini_set(CRT_UTILITY_FILE, "netplay_stateless", "true")
        return self.get_stateless()

    def stateless_disable(self):
        ini_set(CRT_UTILITY_FILE, "netplay_stateless", "false")
        return self.get_stateless()
        
    def get_stateless(self):
        value = ini_get(CRT_UTILITY_FILE, "netplay_stateless")
        if value.lower() == "true": return True
        elif value.lower() == "false": return False
        return None

    def lframes(self, p_iFrames):
        ini_set(CRT_UTILITY_FILE, "netplay_lframes", p_iFrames)
        return self.get_lframes()
        
    def get_lframes(self):
        value = ini_get(CRT_UTILITY_FILE, "netplay_lframes")
        try: frame = int(value)
        except: frame = 2
        return frame

    def check_ip_format(self, p_sIP):
        addr = p_sIP.split(".")
        if len(addr) != 4: return False
        for item in addr:
            try: 
                num = int(item)
                if num < 0 or num > 255: return False
            except: return False
        return True

    def _add_miss_ini(self, p_sIni):
        p_bCheck = False
        with open(CRT_NETPLAY_FILE, "r") as f:
            for line in f:
                lValues = line.strip()
                lValues = lValues.replace('"', '')
                lValues = lValues.replace('=',' ')
                lValues = re.sub(r' +', " ", lValues).split(' ')
                if p_sIni == lValues[0]:
                    p_bCheck = True
                    break
        if not p_bCheck:
            for ini in self.NETPLAY_CFG:
                if p_sIni == ini.split("=")[0]:
                    add_line(CRT_NETPLAY_FILE, ini)
                    break