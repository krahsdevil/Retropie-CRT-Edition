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

# RETROPIE
RETROPIE_PATH = "/opt/retropie"
RETROPIE_CFG_PATH = os.path.join(RETROPIE_PATH, "configs")
RETROPIE_EMULATORS_PATH = os.path.join(RETROPIE_PATH, "emulators")
RETROPIE_MUSIC_PATH = os.path.join(RETROPIE_CFG_PATH, "music")
RETROPIE_SPLASH_PATH = os.path.join(RETROPIE_PATH, "supplementary/splashscreen")
RETROPIE_VIDEOMODES_FILE = os.path.join(RETROPIE_CFG_PATH, "all/videomodes.cfg")
RETROPIE_CUSTEMU_FILE = os.path.join(RETROPIE_CFG_PATH, "all/emulators.cfg")
RETROPIE_RUNCOMMAND_FILE = os.path.join(RETROPIE_PATH, "supplementary/runcommand/runcommand.sh")

# RETROARCH
RA_CFG_FILE = os.path.join(RETROPIE_CFG_PATH, "all/retroarch.cfg")
RA_BIN_FILE = os.path.join(RETROPIE_EMULATORS_PATH, "retroarch/bin/retroarch")

# EMULATIONSTATION
ES_PATH = "/etc/emulationstation"
ES_CFG_PATH = os.path.join(RETROPIE_CFG_PATH, "all/emulationstation")
ES_THEMES_PRI_PATH = os.path.join(ES_PATH, "themes")
ES_THEMES_SEC_PATH = os.path.join(ES_CFG_PATH, "themes")

ES_SYSTEMS_PRI_FILE = os.path.join(ES_PATH, "es_systems.cfg")
ES_CONTROLS_FILE = os.path.join(ES_CFG_PATH, "es_input.cfg")
ES_CFG_FILE = os.path.join(ES_CFG_PATH, "es_settings.cfg")

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
CRT_NETPLAY_FILE = os.path.join(CRT_CONFIG_PATH, "netplay.cfg")
CRT_AUTOFREQ_FILE = os.path.join(CRT_CONFIG_PATH, "autofreqdb.cfg")
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

ROTMODES_TATE1_FILE = os.path.join(CRT_ES_CONFIGS_PATH, "es-select-tate1")
ROTMODES_TATE3_FILE = os.path.join(CRT_ES_CONFIGS_PATH, "es-select-tate3")
ROTMODES_YOKO_FILE = os.path.join(CRT_ES_CONFIGS_PATH, "es-select-yoko")

CRT_FONTS_PATH = os.path.join(CRT_ASST_PATH, "screen_fonts")
CRT_SOUNDS_PATH = os.path.join(CRT_ASST_PATH, "screen_sounds")

# RASPBIAN SETUP
RASP_BOOTCFG_FILE = "/boot/config.txt"
RASP_CMDLINE_FILE = "/boot/cmdline.txt"
RASP_SERVICES_PATH = "/etc/systemd/system"