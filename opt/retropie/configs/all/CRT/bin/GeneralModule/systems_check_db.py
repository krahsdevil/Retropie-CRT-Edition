#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Retropie code integration by -krahs-. 
Database of special systems configuration on es_systems.cfg.

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
import os, sys
import xml.etree.ElementTree as ET

CRT_PATH = "/opt/retropie/configs/all/CRT"
RESOURCES_PATH = os.path.join(CRT_PATH, "bin/GeneralModule")
sys.path.append(RESOURCES_PATH)

from launcher_module.core_paths import CRT_LAUNCHER_FILE

LAST_HASH = "d6ce2b8a6bde5a1eb7a0ef82bfa31686"

LAUNCH_DEF_STR = "python3 " + CRT_LAUNCHER_FILE + " %ROM%"
LAUNCH_RET_STR = "sudo /home/pi/RetroPie-Setup/retropie_packages.sh "
LAUNCH_RET_STR += "retropiemenu launch %ROM% "
LAUNCH_RET_STR += "&lt;/dev/tty &gt;/dev/tty"

XML_PCECD =  "  <system>\n"
XML_PCECD += "    <name>pcenginecd</name>\n"
XML_PCECD += "    <fullname>PC Engine CD</fullname>\n"
XML_PCECD += "    <path>/home/pi/RetroPie/roms/pcenginecd</path>\n"
XML_PCECD += "    <extension>.cue .CUE .ccd .CCD</extension>\n"
XML_PCECD += "    <command>%s pcenginecd dummy</command>\n" % LAUNCH_DEF_STR
XML_PCECD += "    <platform>pcenginecd</platform>\n"
XML_PCECD += "    <theme>pcenginecd</theme>\n"
XML_PCECD += "  </system>\n"

XML_NEOGEOCD =  "  <system>\n"
XML_NEOGEOCD += "    <name>neogeocd</name>\n"
XML_NEOGEOCD += "    <fullname>Neo Geo CD</fullname>\n"
XML_NEOGEOCD += "    <path>/home/pi/RetroPie/roms/neogeocd</path>\n"
XML_NEOGEOCD += "    <extension>.chd .iso .cue .CHD .ISO .CUE</extension>\n"
XML_NEOGEOCD += "    <command>%s neogeocd dummy</command>\n" % LAUNCH_DEF_STR
XML_NEOGEOCD += "    <platform>neogeocd</platform>\n"
XML_NEOGEOCD += "    <theme>neogeocd</theme>\n"
XML_NEOGEOCD += "  </system>\n"

XML_MAMEV =  "  <system>\n"
XML_MAMEV += "    <name>mame-libretro-tate</name>\n"
XML_MAMEV += "    <fullname>mame-libretro TATE</fullname>\n"
XML_MAMEV += "    <path>/home/pi/RetroPie/roms/mame_tate</path>\n"
XML_MAMEV += "    <extension>.zip .ZIP</extension>\n"
XML_MAMEV += "    <command>%s mame-libretro dummy</command>\n" % LAUNCH_DEF_STR
XML_MAMEV += "    <platform>arcade</platform>\n"
XML_MAMEV += "    <theme>mame_tate</theme>\n"
XML_MAMEV += "  </system>\n"

XML_ADVMAMEV =  "  <system>\n"
XML_ADVMAMEV += "    <name>mame-advmame-tate</name>\n"
XML_ADVMAMEV += "    <fullname>advmame TATE</fullname>\n"
XML_ADVMAMEV += "    <path>/home/pi/RetroPie/roms/advmame_tate</path>\n"
XML_ADVMAMEV += "    <extension>.zip .ZIP</extension>\n"
XML_ADVMAMEV += "    <command>%s mame-advmame dummy</command>\n" % LAUNCH_DEF_STR
XML_ADVMAMEV += "    <platform>arcade</platform>\n"
XML_ADVMAMEV += "    <theme>advmame_tate</theme>\n"
XML_ADVMAMEV += "  </system>\n"

XML_ADVMAME =  "  <system>\n"
XML_ADVMAME += "    <name>mame-advmame</name>\n"
XML_ADVMAME += "    <fullname>Multiple Arcade Machine Emulator</fullname>\n"
XML_ADVMAME += "    <path>/home/pi/RetroPie/roms/mame-advmame</path>\n"
XML_ADVMAME += "    <extension>.zip .ZIP</extension>\n"
XML_ADVMAME += "    <command>%s mame-advmame dummy</command>\n" % LAUNCH_DEF_STR
XML_ADVMAME += "    <platform>arcade</platform>\n"
XML_ADVMAME += "    <theme>mame-advmame</theme>\n"
XML_ADVMAME += "  </system>\n"

XML_FBAV =  "  <system>\n"
XML_FBAV += "    <name>fba-tate</name>\n"
XML_FBAV += "    <fullname>Final Burn Alpha-TATE</fullname>\n"
XML_FBAV += "    <path>/home/pi/RetroPie/roms/fba_libretro_tate</path>\n"
XML_FBAV += "    <extension>.zip .ZIP</extension>\n"
XML_FBAV += "    <command>%s fba dummy</command>\n" % LAUNCH_DEF_STR
XML_FBAV += "    <platform>arcade</platform>\n"
XML_FBAV += "    <theme>fba_libretro_tate</theme>\n"
XML_FBAV += "  </system>\n"

XML_CRT =  "  <system>\n"
XML_CRT += "    <name>1CRT</name>\n"
XML_CRT += "    <fullname>CRT Utilities</fullname>\n"
XML_CRT += "    <path>/opt/retropie/configs/all/CRT/config</path>\n"
XML_CRT += "    <extension>.py</extension>\n"
XML_CRT += "    <command>python3 %ROM%</command>\n"
XML_CRT += "    <platform />\n"
XML_CRT += "    <theme>crt</theme>\n"
XML_CRT += "  </system>\n"

XML_PLAYER =  "  <system>\n"
XML_PLAYER += "    <name>videoplayer</name>\n"
XML_PLAYER += "    <fullname>Video Player</fullname>\n"
XML_PLAYER += "    <path>/home/pi/RetroPie/roms/videos</path>\n"
XML_PLAYER += "    <extension>.mkv .avi .mp4 .mpg .MKV .AVI .MP4 .MPG</extension>\n"
XML_PLAYER += "    <command>%s videoplayer dummy</command>\n" % LAUNCH_DEF_STR
XML_PLAYER += "    <platform>videoplayer</platform>\n"
XML_PLAYER += "    <theme>videoplayer</theme>\n"
XML_PLAYER += "  </system>\n"

XML_RETROPIE =  "  <system>\n"
XML_RETROPIE += "    <name>retropie</name>\n"
XML_RETROPIE += "    <fullname>RetroPie</fullname>\n"
XML_RETROPIE += "    <path>/home/pi/RetroPie/retropiemenu</path>\n"
XML_RETROPIE += "    <extension>.rp .sh</extension>\n"
XML_RETROPIE += "    <command>%s</command>\n" % LAUNCH_RET_STR
XML_RETROPIE += "    <platform/>\n"
XML_RETROPIE += "    <theme>retropie</theme>\n"
XML_RETROPIE += "    </system>\n"


SYSTEMS = {
    "pcenginecd":         { "core": "pcenginecd", "check": False,
                            "xml": XML_PCECD, "theme": "pcenginecd" },
    "neogeocd":           { "core": "neogeocd", "check": False,
                            "xml": XML_NEOGEOCD, "theme": "neogeocd" },
    "mame-libretro-tate": { "core": "mame-libretro", "check": False,
                            "xml": XML_MAMEV, "theme": "mame_tate" },
    "mame-advmame":       { "core": "mame-advmame", "check": False,
                            "xml": XML_ADVMAME, "theme": "mame-advmame" },
    "mame-advmame-tate":  { "core": "mame-advmame", "check": False,
                            "xml": XML_ADVMAMEV, "theme": "advmame_tate" },
    "fba-tate":           { "core": "fba", "check": False,
                            "xml": XML_FBAV, "theme": "fba_libretro_tate" },
    "1CRT":               { "core": "", "check": False,
                            "xml": XML_CRT, "theme": "crt" },
    "videoplayer":        { "core": "videoplayer", "check": False,
                            "xml": XML_PLAYER, "theme": "videoplayer" },
    "retropie":           { "core": "", "check": False,
                            "xml": XML_RETROPIE, "theme": "retropie" },
}

