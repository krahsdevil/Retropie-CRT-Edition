#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
paths_lib.py.

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

import os

TMP_SPEEPER_NAME = "lchtmp"
TMP_LAUNCHER_PATH = "/dev/shm"
TMP_SLEEPER_FILE = os.path.join(TMP_LAUNCHER_PATH, TMP_SPEEPER_NAME)

PROCESSES = ["retroarch", "ags", "uae4all2", "uae4arm", "capricerpi",
            "linapple", "hatari", "stella", "atari800", "xroar",
            "vice", "daphne", "reicast", "pifba", "osmose", "gpsp",
            "jzintv", "basiliskll", "mame", "advmame", "dgen",
            "openmsx", "mupen64plus", "gngeo", "dosbox", "ppsspp",
            "simcoupe", "scummvm", "snes9x", "pisnes", "frotz",
            "fbzx", "fuse", "gemrb", "cgenesis", "zdoom", "eduke32",
            "lincity", "love", "kodi", "alephone", "micropolis",
            "openbor", "openttd", "opentyrian", "cannonball",
            "tyrquake", "ioquake3", "residualvm", "xrick", "sdlpop",
            "uqm", "stratagus", "wolf4sdl", "solarus", "drastic",
            "coolcv", "PPSSPPSDL", "moonlight", "Xorg", "smw",
            "wolf4sdl-3dr-v14", "wolf4sdl-gt-v14",
            "wolf4sdl-spear", "wolf4sdl-sw-v14", "xvic",
            "xvic cart", "xplus4", "xpet", "x128", "x64sc", "x64",
            "prince", "fba2x", "steamlink", "pcsx-rearmed",
            "limelight", "sdltrs", "ti99sm", "dosbox-sdl2",
            "minivmac", "quasi88", "xm7", "yabause", "abuse",
            "cdogs-sdl", "cgenius", "digger", "gemrb", "hcl",
            "love", "love-0.10.2", "openblok", "openfodder", "srb2",
            "yquake2", "amiberry", "zesarux", "dxx-rebirth",
            "zesarux", "daphne.bin", "omxplayer.bin"]

# RETROPIE
RETROPIE_PATH = "/opt/retropie"
RETROPIE_CFG_PATH = os.path.join(RETROPIE_PATH, "configs")
RETROPIE_EMULATORS_PATH = os.path.join(RETROPIE_PATH, "emulators")
RETROPIE_MUSIC_PATH = os.path.join(RETROPIE_CFG_PATH, "music")
RETROPIE_SPLASH_PATH = os.path.join(RETROPIE_PATH, "supplementary/splashscreen")
RETROPIE_VIDEOMODES_FILE = os.path.join(RETROPIE_CFG_PATH, "all/videomodes.cfg")
RETROPIE_CUSTEMU_FILE = os.path.join(RETROPIE_CFG_PATH, "all/emulators.cfg")
RETROPIE_RUNCOMMAND_CFG_FILE = os.path.join(RETROPIE_CFG_PATH, "all/runcommand.cfg")
RETROPIE_RUNCOMMAND_FILE = os.path.join(RETROPIE_PATH, "supplementary/runcommand/runcommand.sh")
RETROPIE_CFGRAAPP_FILE = os.path.join(TMP_LAUNCHER_PATH, "retroarch.cfg")

# EMULATIONSTATION
ES_PATH = "/etc/emulationstation"
ES_CFG_PATH = os.path.join(RETROPIE_CFG_PATH, "all/emulationstation")
ES_THEMES_PRI_PATH = os.path.join(ES_PATH, "themes")
ES_THEMES_SEC_PATH = os.path.join(ES_CFG_PATH, "themes")

ES_SYSTEMS_PRI_FILE = os.path.join(ES_PATH, "es_systems.cfg")
ES_CONTROLS_FILE = os.path.join(ES_CFG_PATH, "es_input.cfg")
ES_CFG_FILE = os.path.join(ES_CFG_PATH, "es_settings.cfg")

# RETROPIE CONTENT
RETROPIE_HOME_PATH = "/home/pi/RetroPie"
RETROPIE_ROMS_FOLDER = "roms"
RETROPIE_ROMS_PATH = os.path.join(RETROPIE_HOME_PATH, RETROPIE_ROMS_FOLDER)
RETROPIE_BIOS_FOLDER = "BIOS"
RETROPIE_BIOS_PATH = os.path.join(RETROPIE_HOME_PATH, RETROPIE_BIOS_FOLDER)
RETROPIE_GAMELIST_FOLDER = "gamelists"
RETROPIE_GAMELIST_PATH = os.path.join(ES_CFG_PATH, RETROPIE_GAMELIST_FOLDER)

# RETROARCH
RA_CFG_FILE = os.path.join(RETROPIE_CFG_PATH, "all/retroarch.cfg")
RA_BIN_FILE = os.path.join(RETROPIE_EMULATORS_PATH, "retroarch/bin/retroarch")

# CRT MAIN LAUNCHING SOFTWARE
CRT_ROOT_PATH = os.path.join(RETROPIE_CFG_PATH, "all/CRT")
CRT_BIN_PATH = os.path.join(CRT_ROOT_PATH, "bin")
CRT_LAUNCHER_FILE = os.path.join(CRT_BIN_PATH, "GeneralModule/emulator_launcher.py")

# CRT MAIN EXTRA SOFTWARE
CRT_APPS_PATH = os.path.join(CRT_BIN_PATH, "ScreenUtilityFiles")
CRT_MODULES_PATH = os.path.join(CRT_APPS_PATH, "bin")
CRT_RSC_PATH = os.path.join(CRT_APPS_PATH, "resources")

# CRT CONFIGURATIONS
CRT_CONFIG_PATH = os.path.join(CRT_APPS_PATH, "config_files")
CRT_RA_HASHDB_FILE = os.path.join(CRT_CONFIG_PATH, "retroarchdb.txt")
CRT_FIXMODES_FILE = os.path.join(CRT_CONFIG_PATH, "modes.cfg")
CRT_UTILITY_FILE = os.path.join(CRT_CONFIG_PATH, "utility.cfg")
CRT_NETPLAY_FILE = os.path.join(RETROPIE_CFG_PATH, "all/retronetplay.cfg")
CRT_AUTOFREQ_FILE = os.path.join(CRT_CONFIG_PATH, "autofreqdb.cfg")
CRT_STATS_FILE = os.path.join(CRT_CONFIG_PATH, "statistics.cfg")
CRT_ES_SYSTEMDB_FILE = os.path.join(CRT_BIN_PATH, "GeneralModule/systems_check_db.py")

# CRT CONFIGURATIONS FOR RETROARCH
CRT_DB_PATH = os.path.join(CRT_ROOT_PATH, "Resolutions")
CRT_DB_SYSTEMS_FILE = os.path.join(CRT_DB_PATH, "base_systems.cfg")
CRT_RA_MAIN_CFG_PATH = os.path.join(CRT_ROOT_PATH, "Retroarch/configs")
CRT_RA_CORES_CFG_PATH = os.path.join(CRT_ROOT_PATH, "Retroarch/cores")

# CRT RESOURCES
CRT_ASST_PATH = os.path.join(CRT_RSC_PATH, "assets")
CRT_ADDN_PATH = os.path.join(CRT_RSC_PATH, "addons")
CRT_MEDIA_PATH = os.path.join(CRT_RSC_PATH, "media")

CRT_ES_VERT_MENU = os.path.join(CRT_ASST_PATH, "screen_emulationstation/crt_vertical_menu")

CRT_ES_RES_PATH = os.path.join(CRT_ASST_PATH, "screen_emulationstation/crt_modes_change")
CRT_LNCH_IMG_MOD_PATH = os.path.join(CRT_ES_RES_PATH, "launch_images_modes")
CRT_LNCH_IMG_ROT_PATH = os.path.join(CRT_ES_RES_PATH, "launch_images_rotate")
CRT_ICONS_SET_PATH = os.path.join(CRT_ES_RES_PATH, "crt_icons")
CRT_ES_CONFIGS_PATH = os.path.join(CRT_ES_RES_PATH, "configs")

ROTMODES_TATE1_FILE = os.path.join(CRT_ES_CONFIGS_PATH, "es-tate1")
ROTMODES_TATE3_FILE = os.path.join(CRT_ES_CONFIGS_PATH, "es-tate3")

CRT_FONTS_PATH = os.path.join(CRT_ASST_PATH, "screen_fonts")
CRT_SOUNDS_PATH = os.path.join(CRT_ASST_PATH, "screen_sounds")

# RASPBIAN SETUP
RASP_BOOTCFG_FILE = "/boot/config.txt"
RASP_CMDLINE_FILE = "/boot/cmdline.txt"
RASP_SERVICES_PATH = "/etc/systemd/system"

# CRT SERVICE EXTERNAL STORAGE
CRT_EXTSTRG_PATH = os.path.join(CRT_MODULES_PATH, "service_extstorage")
CRT_EXTSTRG_CORE_FILE = "ext_storage.py"
CRT_EXTSTRG_CORE_PATH = os.path.join(CRT_EXTSTRG_PATH, CRT_EXTSTRG_CORE_FILE)
CRT_EXTSTRG_SRV_FILE = "ext_storage.service"
CRT_EXTSTRG_SRV_PATH = os.path.join(CRT_EXTSTRG_PATH, CRT_EXTSTRG_SRV_FILE)
CRT_EXTSTRG_TRIG_MNT_PATH = os.path.join(CRT_EXTSTRG_PATH, "mounted.cfg")
CRT_EXTSTRG_TRIG_UMNT_PATH = os.path.join(CRT_EXTSTRG_PATH, "umounted.cfg")

# CRT SERVICE BACKGROUND MUSIC
CRT_BGM_PATH = os.path.join(CRT_MODULES_PATH, "service_bgm")
CRT_BGM_CORE_FILE = "bgm.py"
CRT_BGM_CORE_PATH = os.path.join(CRT_BGM_PATH, CRT_BGM_CORE_FILE)
CRT_BGM_SRV_FILE = "bgm.service"
CRT_BGM_SRV_PATH = os.path.join(CRT_BGM_PATH, CRT_BGM_SRV_FILE)
CRT_BGM_MUS_PATH = os.path.join(RETROPIE_CFG_PATH, "music")

# CRT SERVICE RGB CABLE
CRT_RGB_PATH = os.path.join(CRT_MODULES_PATH, "module_cable")
CRT_RGB_CORE_FILE = "rgb_cable.py"
CRT_RGB_CORE_PATH = os.path.join(CRT_RGB_PATH, CRT_RGB_CORE_FILE)
CRT_RGB_SRV_FILE = "rgb_cable.service"
CRT_RGB_SRV_PATH = os.path.join(CRT_RGB_PATH, CRT_RGB_SRV_FILE)

# PYTHON SCRIPTS PROCESSES NAME
PNAME_LAUNCHER = "CRTLauncher"
PNAME_CONFIG = "CRTconfig"
PNAME_EXTSTRG = "CRTautomnt"
PNAME_BGM = "CRTbgm"
PNAME_RGBCABLE = "CRTcable"