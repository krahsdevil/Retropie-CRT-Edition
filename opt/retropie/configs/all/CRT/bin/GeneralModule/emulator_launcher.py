#!/usr/bin/python
# coding: utf-8
#
# Original idea/coded by Ironic/aTg (2017) for RGB-Pi recalbox
# Retropie code/integration by -krahs- (2019)
#
# unlicense.org
#
# This script can be heavily optimized.

import struct
import os
import os.path
import sys
import shutil
import pygame
import time
import logging
import glob

import subprocess
import commands

from math import *
from pygame.locals import *
sys.path.append('/opt/retropie/configs/all/CRT/')
sys.path.append('/opt/retropie/configs/all/CRT/bin/SelectorsModule/')
sys.path.append('/opt/retropie/configs/all/CRT/bin/GeneralModule/')

from general_config import *
from general_functions import *
from selector_module_functions import *

#path = os.path.dirname(os.path.realpath(__file__))
#os.chdir(path)

logging.basicConfig(filename="/tmp/CRT_Launcher.log", level=logging.INFO, format='%(asctime)s %(message)s')
logging.info("INICIANDO EMULACION")
logging.info("INFO: Comprobando parametros recibidos por ES")
# Test if command line have parameters
try:
    rom_full_path = sys.argv[1]
    logging.info("INFO: Argumento 1 (ROM) = %s" % rom_full_path)
    emulator = sys.argv[2]
    logging.info("INFO: Argumento 2 (sistema) = %s" % emulator)
    core = sys.argv[3]
    logging.info("INFO: Argumento 3 (sin uso) = %s" % core)
except (IndexError):
    logging.info("ERROR: No se ha recibido alguno de los argumentos iniciales")
    logging.info("EXIT: Emul_Launcher se cerrara antes de tiempo")
    something_is_bad("No game to launch or no emulator !","none")
    sys.exit()

# PATHS
file_name = os.path.basename(rom_full_path)
file_name_no_ext = file_name[:-4]
game_name = file_name_no_ext

libretro_path = "/usr/lib/libretro"
COMPMODESCFG_PATH = '/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/modes.cfg'
VIDEOUTILITYCFG_PATH = "/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/utility.cfg"
NETPLAYCFG_PATH = '/opt/retropie/configs/all/CRT/netplay.cfg'
TIMINGS_PATH = "/opt/retropie/configs/all/CRT/Resolutions/base_systems.cfg"
RACFG_PATH ="/opt/retropie/configs/all/CRT/Retroarch/configs/"
configgen_retroarchcustom = "/opt/retropie/configs/all/retroarch.cfg"
RUNCOMMAND_PATH = "/opt/retropie/supplementary/runcommand/runcommand.sh"

retroarcharcadepath = "/tmp/"
retroarcharcadefile = "retroarcharcade"
retroarcharcade = "%s%s.cfg" % (retroarcharcadepath, retroarcharcadefile)
ADVANCEDMAMERC_PATH ="/opt/retropie/configs/mame-advmame/advmame.rc"

RuncommandClosed = False
runcommand_process = None

#CLEAR RETROARCH LAUNCH INDICATOR FILE
logging.info("INFO: Eliminando trigger file /tmp/lchtmp")
os.system('rm /tmp/lchtmp > /dev/null 2>&1')

def easynetplay():

    # Read data from EasyNetplay
    np = "none"
    with open(NETPLAYCFG_PATH, 'r') as file:
        for lineS in file:
            lineS = lineS.strip().split(' ')
            np = lineS

            # Get values from netplay.cfg
            host = int(np[0])
            client = int(np[1])
            ip1 = str(np[2]+"."+np[3]+"."+np[4]+"."+np[5])
            ip2 = str(np[6]+"."+np[7]+"."+np[8]+"."+np[9])
            ip3 = str(np[10]+"."+np[11]+"."+np[12]+"."+np[13])
            ip4 = str(np[14]+"."+np[15]+"."+np[16]+"."+np[17])
            ip5 = str(np[18]+"."+np[19]+"."+np[20]+"."+np[21])
            ip6 = str(np[22]+"."+np[23]+"."+np[24]+"."+np[25])

            if host == 1 and client == 0:
                return "--host"

            if host == 0 and client == 1:
                return "--connect "+ip1

            if host == 0 and client == 2:
                return "--connect "+ip2

            if host == 0 and client == 3:
                return "--connect "+ip3

            if host == 0 and client == 4:
                return "--connect "+ip4

            if host == 0 and client == 5:
                return "--connect "+ip5

            if host == 0 and client == 6:
                return "--connect "+ip6

            if host == 0 and client == 0:
                return ""

            if host == 1 and client == 1:
                return ""

check_videomodes() # remove video modes if exists


def core_freq_name(emulator, game, data):
    global RACFG_PATH, rom_full_path
    freq = "" # default freq
    emulator_freq_name = emulator

    if "has_selector" in data:
        logging.info("INFO: Lanzando selector de frecuencia")
        freq = str(selector_frequency(game)) # TODO: better fix selector_frequency
        logging.info("INFO: Frecuencia establecida: %shz" % freq)

    if "core_freq_name" in data:
        emulator_freq_name = data["core_freq_name"]
        logging.info("INFO: Cambiada variable de nombre de emulador (emulatorWFQ): %s" % emulator_freq_name)

    emulator_freq_name = emulator_freq_name + freq
    logging.info("INFO: variable final de emulador (emulatorWFQ): %s" % emulator_freq_name)
    return emulator_freq_name


def fix_core_command(emulator, net_ip, emulator_freq_name, game, data):
    global retroarcharcadefile, retroarcharcadepath, RACFG_PATH
    emulator_path = RACFG_PATH
    if "game_freq_db" in data:
        emulator_freq_name = retroarcharcadefile
        emulator_path = retroarcharcadepath

    logging.info("INFO: change_retropie_runcommand_emulator_init(easy,emulator,emulatorWFQ,ra_cfg_path,game) parametros: %s,%s,%s,%s,%s" % (net_ip, emulator, emulator_freq_name, RACFG_PATH, game))
    LoadDBFile=change_retropie_runcommand_emulator_init(easy, emulator, emulator_freq_name, emulator_path, game)
    logging.info("INFO: change_retropie_runcommand_emulator_init - returns: %s" % str(LoadDBFile) )
    return LoadDBFile


# launch_core: run emulator!
#   @emulator: system name.
#   @net_ip: easy netplay ip.
#   @emulator_freq_name: internal freq emulator name, some times we need force this.
#   @game: game name.
def launch_core(emulator, net_ip, emulator_freq_name, game):
    global RUNCOMMAND_PATH, rom_full_path, runcommand_process
    commandline = "%s 0 _SYS_ %s \"%s\"" % (RUNCOMMAND_PATH, emulator, rom_full_path)
    runcommand_process = subprocess.Popen(commandline, shell=True)
    logging.info("INFO: Subproceso lanzado: %s", commandline)


# wait_runcommand: wait for user launcher menu
#   @data: system data.
#   @full_checks: off, just check current process.
#   return: True, if user wants close emulation directly.
def wait_runcommand(data, full_checks = True):
    global runcommand_process
    RuncommandClosed = False
    binaries = ["retroarch"] # default emulator binary is retroarch
    if "bin_names" in data:
        binaries = data["bin_names"]

    logging.info("INFO: Esperando que runcommand termine e inicie: %s (full_checks: %s)" % (str(binaries), str(full_checks)) )
    while True:
        if full_checks:
            if os.path.exists('/tmp/lchtmp'):
                logging.info("INFO: Detectado trigger file /tmp/lchtmp")
                break;
            # try to detect if user exits from runcommand
            poll = runcommand_process.poll()
            if poll != None:
                logging.info("INFO: Detectado el cierre de runcommand (poll = %s)" % poll)
                RuncommandClosed = True
                break
        output = commands.getoutput('ps -A')
        for system in binaries:
            if system in output:
                logging.info("INFO: Detectado %s en los procesos activos", system)


    splash_info("black") # clean screen
    os.system('rm /tmp/lchtmp > /dev/null 2>&1') # clean
    return RuncommandClosed

# runcommand it could be change our config, we check this here...
# TODO: esto se puede mejorar si sabemos que runcommand no permite cambiar opciones.
def second_check(emulator, emulator_freq_name, data):
    global RACFG_PATH, RUNCOMMAND_PATH, rom_full_path
    global retroarcharcadefile, retroarcharcadepath
    global info_error_line1, info_error_line2

    emulator_path = RACFG_PATH
    if "game_freq_db" in data:
        emulator_freq_name = retroarcharcadefile
        emulator_path = retroarcharcadepath

    binaries = ["retroarch"] # default emulator binary is retroarch
    if "bin_names" in data:
        binaries = data["bin_names"]

    Wrong_Emulator = second_check_runcommand_emulator_init(emulator, emulator_path, emulator_freq_name, RACFG_PATH, "unknown")
    logging.info("INFO: Devueltos los siguientes valores para Wrong_Emulator: %s, %s" % (Wrong_Emulator[0], Wrong_Emulator[1]))
    Wrong_Videomode = check_videomodes() # remove video modes if exists returns true
    logging.info("INFO: Devueltos los siguientes valores para Wrong_Videomode: %s" % Wrong_Videomode)

    if Wrong_Emulator[0] == True or Wrong_Videomode == True:
        wait_runcommand(data, False)
        logging.info("ERROR: Cerrando el proceso de Retroarch")
        for system in binaries:
            if system == "mupen":
                os.system('pkill -9 -f "mupen" > /dev/null 2>&1')
            else:
                os.system('killall %s > /dev/null 2>&1' % system)

        if Wrong_Emulator[0] == True:
            logging.info("ERROR: Mensaje en pantalla por cambio de emulador no permitido")
            if Wrong_Emulator[1] == "core_changed": # FIXME: is amiga really need it?
                info_error_line1 = "Emulator was changed for amiga system..."
                info_error_line2 = "Please, restart the emulation"
            else:
                info_error_line1 = "You didn't choose wisely..."
                info_error_line2 = "Try with other core/emulator"

        else if Wrong_Videomode == True:
            logging.info("ERROR: Mensaje en pantalla por cambio de resolucion no permitido")
            info_error_line1 = "You didn't choose wisely..."
            info_error_line2 = "Don't let Retropie play with my resolutions!"

    return (Wrong_Emulator[0] == True or Wrong_Videomode == True)


# load_videodata: Read GamesList from Games Database
#   @db_file: full path to db freq file
#   @game: game name.
#   return: game video data or default if not found (warns user using a video)
def load_videodata(db_file, game):
    default_freq_data = []
    with open(db_file) as file:
        for line in file:
            data = line.strip().split(' ')
            if data[0] == game:
                return data
            elif data[0] == "default":
                default_freq_data = data
    # show to user freq not found - using default freq
    os.system("/opt/retropie/configs/all/CRT/Datas/default.sh")
    return default_freq_data


# set_tvfix: Get values from FIX
#   @video_data: current video data - IS MODIFIED!
#   return: new video data
def set_tvfix(video_data):
    global COMPMODESCFG_PATH
    SelectedMode = None
    with open(COMPMODESCFG_PATH, 'r') as file:
        for line in file:
            line = line.strip().replace('=',' ').split(' ')
            if line[0] == 'mode_default':
                SelectedMode = line[1]
        if SelectedMode.lower() != 'default':
            file.seek(0)
            for line in file:
                mask = line.strip().replace('=',' ').split(' ')
                if mask[0] == '%s_game_mask'%SelectedMode:
                    GameMask = line.replace('%s_game_mask'%SelectedMode,'').strip().split(' ')
            video_data["H_Res"]  += int(GameMask[0])
            video_data["V_Res"]  += int(GameMask[1])
            video_data["R_Rate"] += float(GameMask[2])
            video_data["H_Pos"]  += int(GameMask[3])
            video_data["H_Zoom"] += int(GameMask[4])
            video_data["V_Pos"]  += int(GameMask[5])
            video_data["H_FP"]   += int(GameMask[6])
            video_data["H_Sync"] += int(GameMask[7])
            video_data["H_BP"]   += int(GameMask[8])
            video_data["V_Sync"] += int(GameMask[9])
            video_data["H_Freq"] += int(GameMask[10])
    return video_data


# set_screencfg: Get values from Screen Utility
#   @video_data: current video data - IS MODIFIED!
#   return: new video data
def set_screencfg(video_data):
    global VIDEOUTILITYCFG_PATH
    with open(VIDEOUTILITYCFG_PATH, 'r') as file:
        for line in file:
            line = line.strip().replace('=',' ').split(' ')
            if line[0] == 'test60_offsetX':
                video_data["H_Pos"] += int(line[1])
            elif line[0] == 'test60_width':
                video_data["H_Zoom"] += int(line[1])
            elif line[0] == 'test60_offsetY':
                video_data["V_Pos"] += int(line[1])
            elif line[0] == 'frontend_rotation':
                video_data["R_Sys"] = int(line[1])
            elif line[0] == 'game_rotation':
                video_data["R_Game"] = int(line[1])
    return video_data


# prepare advmame config
def prepare_advmame(video_data):
    global rom_full_path, ADVANCEDMAMERC_PATH
    display_ror = "no"
    display_rol = "no"

    if video_data["Side_Game"] == 'V':
        if (video_data["R_Game"] == 0 and video_data["R_Sys"] != -90) or video_data["R_Sys"] == 90:
            display_ror = "yes"
        elif video_data["R_Sys"] == -90:
            display_rol = "yes"


    # Find the rom directory
    romdir = os.path.dirname(rom_full_path)
    logging.info("INFO: advmame result - ror %s, %rol %s [ %s ] - DIR: %s" % (display_ror, display_rol, str(video_data), romdir) )

    # TODO: quitar ese espacio del modificarLinea
    modificarLinea(ADVANCEDMAMERC_PATH, "display_ror ", "display_ror %s" % display_ror)
    modificarLinea(ADVANCEDMAMERC_PATH, "display_rol ", "display_rol %s" % display_rol)
    modificarLinea(ADVANCEDMAMERC_PATH, "misc_smp ","misc_smp yes")
    modificarLinea(ADVANCEDMAMERC_PATH, "display_vsync ","display_vsync yes")
    modificarLinea(ADVANCEDMAMERC_PATH, "misc_safequit ","misc_safequit no")

    # put the correct game folder
    modificarLinea(ADVANCEDMAMERC_PATH, "dir_rom ","dir_rom %s:/home/pi/RetroPie/BIOS" % romdir)
    modificarLinea(ADVANCEDMAMERC_PATH, "misc_quiet ", "misc_quiet yes")
    modificarLinea(ADVANCEDMAMERC_PATH, "display_resizeeffect ","display_resizeeffect none")
    modificarLinea(ADVANCEDMAMERC_PATH, "display_resize ","display_resize none")
    modificarLinea(ADVANCEDMAMERC_PATH, "display_mode ","display_mode generate")


# fixes libretro cfg file and modify video_data!
def prepare_libretro(org_data, video_data):
    if video_data["Side_Game"] != 'V':
        make_retroarcharcade_configfile(org_data[1], org_data[2], 0, 0, org_data[3], video_data["Side_Game"])
        return video_data

    offsetx = '-10'
    offsety = 0
    if video_data["R_Game"] == -90:
        video_data["Side_Game"] = 'H'
        make_retroarcharcade_configfile('1220', org_data[2], 0, 0, org_data[3], video_data["Side_Game"])
        video_data["H_Pos"] = int('130')
    elif (video_data["R_Game"] == 0 and video_data["R_Sys"] != -90) or video_data["R_Sys"] == 90:
        video_data["Side_Game"] = 'V3'
        if video_data["V_Res"] == 240:
            offsety = 4
        make_retroarcharcade_configfile(org_data[1], org_data[2], offsetx, offsety, org_data[3], video_data["Side_Game"])
    elif video_data["R_Sys"] == -90:
        video_data["Side_Game"] = 'V1'
        if video_data["V_Res"] == 240:
            offsety = 4
        make_retroarcharcade_configfile(org_data[1], org_data[2], offsetx, offsety, org_data[3], video_data["Side_Game"])
    return video_data


# fixed default video data and returned
def prepare_video(db_file, emulator, video_data):
    fixed_data = {
        "H_Res":    int(video_data[1]),
        "V_Res":    int(video_data[2]),
        "R_Rate":   float(video_data[3]),
        "H_Pos":    int(video_data[4]),
        "H_Zoom":   int(video_data[5]),
        "V_Pos":    int(video_data[6]),
        "H_FP":     int(video_data[7]),
        "H_Sync":   int(video_data[8]),
        "H_BP":     int(video_data[9]),
        "V_Sync":   int(video_data[10]),
        "H_Freq":   int(video_data[11]),
        "Side_Game": video_data[13],
        "R_Sys":    0,
        "R_Game":   0,
    }

    # Encapsulator
    # Center a little but don't launch the encapsulator
    if fixed_data["V_Res"] == 240:
        fixed_data["V_Pos"] -= int(5)

    # Launch the encapsulator
    if fixed_data["V_Res"] > 240:
        select = selector_encapsulate()
        if select == 1:
            # Encapsulate
            fixed_data["H_Freq"] = int(15840)
            fixed_data["V_Pos"] += int(10)

        else:
            # Cropped if is under 55Hz
            if fixed_data["R_Rate"] < 55:
                fixed_data["H_Freq"] = int(15095)
            fixed_data["V_Pos"] -= int(10)

    fixed_data = set_tvfix(fixed_data)
    fixed_data = set_screencfg(fixed_data)

    if db_file == "mame-advmame" or emulator == "mame-advmame":
        prepare_advmame(fixed_data)
    # FIXME: maybe just need an else....
    elif (db_file in ["mame-libretro", "fba", "unknown"]) or (emulator in ["mame-libretro", "fba"]):
        fixed_data = prepare_libretro(fixed_data)

    # return final video data
    return fixed_data


def prepare_amiberry(game):
    global info_error_line1, info_error_line2
    AmigaEmulatorEmpty = False
    Amiberry_HostPrefs_File = "/opt/retropie/configs/amiga/amiberry/whdboot/hostprefs.conf"
    Amiberry_WHDLoad_Database = "/opt/retropie/configs/amiga/amiberry/whdboot/game-data/whdload_db.xml"
    emulator_freq_name = ""
    # check config files
    not_found_files = ""
    if not os.path.exists(Amiberry_HostPrefs_File):
        not_found_files += "hostprefs.conf"
    if not os.path.exists(Amiberry_WHDLoad_Database):
        if not_found_files:
            not_found_files += " and "
        not_found_files += "whdload_db.xml"
    if not_found_files:
        info_error_line1 = "amiberry can't found:"
        info_error_line2 = not_found_files
        return emulator_freq_name

    emulator_freq_name = "amiga_amiberry_default"
    modificarLinea(Amiberry_HostPrefs_File, "ASPECT_RATIO_FIX=", "ASPECT_RATIO_FIX=FALSE") # TEST THIS!
    Game_VRES_WHDLoad = find_amiberry_WHDLoadDB_vertical_res("SCREEN_HEIGHT=", game, Amiberry_WHDLoad_Database)
    if Game_VRES_WHDLoad[1]:
        HStretch = selector_stretch()
        if HStretch == True:
            emulator_freq_name = "amiga_amiberry_" + str(Game_VRES_WHDLoad[1])
    elif not Game_VRES_WHDLoad[0]:
        splash_info('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/stretch/nogame.png')
    elif not Game_VRES_WHDLoad[1]:
        splash_info('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/stretch/nores.png')
    return emulator_freq_name


# TODO: separe launch process, but need more tests...
def launch_videoplayer(emulator_freq_name):
    global rom_full_path, TIMINGS_PATH
    video_path = os.path.dirname(rom_full_path)
    VideoPosition = 0
    video_ext = ['avi', 'mkv', 'mp4', 'mpg', 'AVI', 'MKV', 'MP4', 'MPG']
    videos = []
    for extension in video_ext:
        videos = videos + glob.glob( "%s/*.%s" % (video_path, extension))
    videos = sorted(videos)
    for srchvideo in videos:
        if srchvideo == rom_full_path:
            break
        else:
            VideoPosition += 1
    if len(videos) <= 1:
        PlayAllVideos = False
    else:
        PlayAllVideos = selector_allvideos()
    launch_joy2key('kcub1', 'kcuf1', 'kcuu1', 'kcud1', '0x20', '0x71', '0x6b', '0x6a', '0x6d', '0x6e')
    crt_open_screen_from_timings_cfg(emulator_freq_name, TIMINGS_PATH)
    commandline = 'omxplayer -b --align center --layer 10000 --font-size 72 --font="/opt/retropie/configs/all/CRT/bin/VideoPlayer/Ubuntu_MOD_WIDE.ttf" \"%s\" > /dev/null 2>&1' % videos[VideoPosition]
    runcommand_process = subprocess.Popen(commandline, shell=True)
    while True:
        poll = runcommand_process.poll()
        if poll != None:
            returncoded = runcommand_process.returncode
            if returncoded == 3:
                break
            else:
                if PlayAllVideos == True:
                    VideoPosition += 1
                    try:
                        videos[VideoPosition]
                        runcommand_process = subprocess.Popen('omxplayer -b --align center --layer 10000 --font-size 72 --font="/opt/retropie/configs/all/CRT/bin/VideoPlayer/Ubuntu_MOD_WIDE.ttf" \"%s\" > /dev/null 2>&1' % videos[VideoPosition], shell=True)
                    except:
                        break
                else:
                    break
    os.system('echo %s >> /tmp/proces' % returncoded)
    os.system('sudo killall joy2key.py')


has_errors = False
info_error_line1 = ""
info_error_line2 = ""

if emulator in L_SYSTEM:
    logging.info("INFO: Detectado sistema compatible: %s" % emulator)
    easy = "" # default - netplay ip is empty
    data = L_SYSTEM[emulator]

    if not "ignore_netplay" in data:
        easy = easynetplay()
        logging.info("INFO: Variable de estado de Netplay (easy): %s" % easy)

    emulatorWFQ = core_freq_name(emulator, game_name, L_SYSTEM[emulator])
    LoadDBFile = fix_core_command(emulator, easy, emulatorWFQ, game_name, data)
    if "amiga" == emulator:
        AmigaRes = "amiga_amiberry_default"
        if "amiberry" in LoadDBFile[1]:
            AmigaRes = prepare_amiberry()
            if not AmigaRes:
                has_errors = True
            else:
                crt_open_screen_raw(AmigaRes,LoadDBFile[0])
        elif "lr-puae" in LoadDBFile[1]:
            AmigaRes = "amiga_lr-puae"
            crt_open_screen_from_timings_cfg(AmigaRes,LoadDBFile[0]) # FIXME: MAL debe de hacerse en el wait... ahora a cascarla xd
    elif emulator == "videoplayer":
        launch_videoplayer() # FIXME: atm simply launch
    elif "game_freq_db" in data:
        video_data = load_videodata(LoadDBFile[0], game_name)
        video_data = prepare_video(LoadDBFile[0], emulator, video_data)
        crt_open_screen(video_data["H_Res"], video_data["V_Res"], video_data["R_Rate"],
                        video_data["H_Pos"], video_data["H_Zoom"], video_data["V_Pos"],
                        video_data["H_FP"], video_data["H_Sync"], video_data["H_BP"],
                        video_data["V_Sync"], video_data["H_Freq"])
    elif "core_raw_freq" in data:
        crt_open_screen_raw(emulator, TIMINGS_PATH)
    else:
        crt_open_screen_from_timings_cfg(emulator, TIMINGS_PATH)

    if not has_errors or emulator == "videoplayer": # FIXME videoplayer special case
        launch_core(emulator, easy, emulatorWFQ, game)
        # return true if user want finish emulation
        if not wait_runcommand(data):
            has_errors = second_check()
            logging.info("INFO: Esperando a que el subproceso iniciado finalice")
            runcommand_process.wait()
        else:
            logging.info("INFO: Forzo la salida")
else:
    #####################################################################################
    #    ANY OTHER EMULATOR NOT SUPPORTED                                               #
    #####################################################################################
    has_errors = True
    info_error_line1 = "System not supported [%s]" % emulator

if has_errors:
    something_is_bad(info_error_line1, info_error_line2)

logging.info("INFO: Cerrando Pygame")
pygame.quit()
# Restore ES resolution from 1st line of /boot/config.txt
es_restore_screen()
logging.info("INFO: Resolucion restaurada")
os.system('clear')
sys.exit()
