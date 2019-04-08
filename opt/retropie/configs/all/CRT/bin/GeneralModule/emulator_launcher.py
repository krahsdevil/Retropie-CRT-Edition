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

CompModesCFG = '/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/modes.cfg'
VideoUtilityCFG = "/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/utility.cfg"
npcfg= '/opt/retropie/configs/all/CRT/netplay.cfg'
timings_full_path = "/opt/retropie/configs/all/CRT/Resolutions/base_systems.cfg"
libretro_path = "/usr/lib/libretro"
ra_cfg_path ="/opt/retropie/configs/all/CRT/Retroarch/configs/"
configgen_retroarchcustom = "/opt/retropie/configs/all/retroarch.cfg"

retroarcharcadepath = "/tmp/"
retroarcharcadefile = "retroarcharcade"
retroarcharcade = "%s%s.cfg" % (retroarcharcadepath,retroarcharcadefile)
advmame_cfg_patch ="/opt/retropie/configs/mame-advmame/advmame.rc"

RuncommandClosed = False

#CLEAR RETROARCH LAUNCH INDICATOR FILE
logging.info("INFO: Eliminando trigger file /tmp/lchtmp")
os.system('rm /tmp/lchtmp > /dev/null 2>&1')

def easynetplay():

    # Read data from EasyNetplay
    np = "none"
    with open(npcfg, 'r') as file:
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

###################################################################################
#               RETROARCH CONSOLE EMULATORS WITH 60Hz/50Hz SELECTOR               #
###################################################################################
#                                                                                 #
#    1) SEGA MEGADRIVE                                                            #
#    2) SEGA MEGADRIVE CD                                                         #
#    3) SEGA 32X                                                                  #
#    4) SEGA MASTER SYSTEM                                                        #
#    5) NINTENDO 64                                                               #
#    6) NINTENDO ENTERTAINMENT SYSTEM                                             #
#    7) SUPER NINTENDO                                                            #
#    8) SONY PLAYSTATION                                                          #
#    9) MSX                                                                       #
#    10) ATARI 2600                                                               #
#    11) ATARI 7800                                                               #
#    12) ATARI ST                                                                 #
#    13) VIDEOPAC MAGNAVOX ODYSSEY 2                                              #
#    14) SINCLAIR ZX 81                                                           #
#    15) COMMODORE 64                                                             #
#                                                                                 #
###################################################################################

if emulator == "megadrive" or emulator == "segacd" or emulator == "sega32x" or emulator == "mastersystem" or emulator == "n64" or emulator == "nes" or emulator == "snes" or emulator == "psx" or emulator == "msx" or emulator == "atari2600" or emulator == "odyssey2" or emulator == "zx81" or emulator == "atarist" or emulator == "c64" or emulator == "atari7800" :
    logging.info("INFO: Detectado sistema compatible: %s" % emulator)
    logging.info("INFO: Categoria con selector de frecuencia")
    logging.info("INFO: Lanzando selector de frecuencia")
    freq = selector_frequency(game_name)
    logging.info("INFO: Frecuencia establecida: %shz" % freq)
    emulatorWFQ = emulator
    logging.info("INFO: Declarada variable de nombre de emulador con etiqueta de frecuencia (emulatorWFQ) por defecto: %s" % emulatorWFQ)
    if freq == 50:
        emulatorWFQ = emulator + "50"
        logging.info("INFO: Detectada seleccion a 50hz, modificada variable de nombre de emulador con etiqueta de frecuencia (emulatorWFQ): %s" % emulatorWFQ)
    logging.info("INFO: Chequeando si CRT Netplay está habilitado")
    easy = easynetplay()
    logging.info("INFO: Variable de estado de Netplay (easy): %s" % easy)
    logging.info("INFO: Iniciando primer check de emulador")
    logging.info("INFO: Llamada a la funcion change_retropie_runcommand_emulator_init(easy,emulator,emulatorWFQ,ra_cfg_path,game_name) con los siguientes parametros:")
    logging.info("INFO: %s,%s,%s,%s,%s" % (easy,emulator,emulatorWFQ,ra_cfg_path,game_name))
    change_retropie_runcommand_emulator_init(easy,emulator,emulatorWFQ,ra_cfg_path,game_name)
    logging.info("INFO: Preparando linea de comandos para lanzar runcommand:")
    logging.info("INFO: /opt/retropie/supplementary/runcommand/runcommand.sh 0 _SYS_ %s \"%s\"" % (emulator,rom_full_path))
    commandline = "/opt/retropie/supplementary/runcommand/runcommand.sh 0 _SYS_ %s \"%s\"" % (emulator,rom_full_path)
    logging.info("INFO: Lanzando como subproceso")
    runcommand_process = subprocess.Popen(commandline, shell=True)
    logging.info("INFO: Subproceso lanzado")
    
    logging.info("INFO: Esperando a retroarch o que runconmmand termine")
    while True:
        output = commands.getoutput('ps -A')
        if 'retroarch' in output or 'mupen' in output or os.path.exists('/tmp/lchtmp'):
            if 'retroarch' in output:
                logging.info("INFO: Detectado retroarch en los procesos activos")
            if os.path.exists('/tmp/lchtmp'):
                logging.info("INFO: Detectado trigger file /tmp/lchtmp")
            logging.info("INFO: Ocultando pantalla")
            splash_info("black")
            logging.info("INFO: Lanzando cambio de frecuencia de monitor:")
            logging.info("INFO: crt_open_screen_from_timings_cfg(%s,%s)" % (emulatorWFQ,timings_full_path))
            crt_open_screen_from_timings_cfg(emulatorWFQ,timings_full_path)
            logging.info("INFO: Frecuencia cambiada, saliendo del bucle de espera")
            break
        poll = runcommand_process.poll()
        if poll != None:
            logging.info("INFO: Detectado el cierre de runcommand (poll = %s)" % poll)
            # Exits if runcommand finish unexpectedly or by user
            RuncommandClosed = True
            logging.info("INFO: Establecida variable de deteccion de cierre de runcommand (RuncommnadClose = %s)" % RuncommandClosed)
            logging.info("INFO: Saliendo del bucle de espera")
            break
    logging.info("INFO: Iniciando segundo check de Emulador")
    Wrong_Emulator = second_check_runcommand_emulator_init(emulator,rom_full_path,emulatorWFQ,ra_cfg_path,"unknown")
    logging.info("INFO: Devueltos los siguientes valores para Wrong_Emulator: %s, %s" % (Wrong_Emulator[0],Wrong_Emulator[1]))
    logging.info("INFO: Iniciando check de cambios de resolucion de retropie")
    Wrong_Videomode = check_videomodes()
    logging.info("INFO: Devueltos los siguientes valores para Wrong_Videomode: %s" % Wrong_Videomode)
    if (Wrong_Emulator[0] == True or Wrong_Videomode == True) and RuncommandClosed != True:
        logging.info("ERROR: Detectado cambio de emulador o resolucion no permitido")
        logging.info("ERROR: Esperando a que Retroarch inicie para forzar el cierre y salir")
        while True:
            output = commands.getoutput('ps -A')
            if 'retroarch' in output or 'mupen' in output:
                break
        logging.info("ERROR: Cerrando el proceso de Retroarch")
        os.system('killall retroarch > /dev/null 2>&1')
        os.system('pkill -9 -f "mupen" > /dev/null 2>&1')
    logging.info("INFO: Esperando a que el subproceso de Runcommand finalice")
    runcommand_process.wait()
    logging.info("INFO: Cerrando Pygame")
    pygame.quit()
    # Restore ES resolution from 1st line of /boot/config.txt
    logging.info("INFO: Restaurando resolucion base")
    es_restore_screen()
    logging.info("INFO: Resolucion restaurada")
    if (Wrong_Emulator[0] == True or Wrong_Videomode == True) and RuncommandClosed != True:
        logging.info("ERROR: Detectado un cierre forzado por CRT:")
        logging.info("ERROR: Wrong_Emulator = %s, Wrong_Videomode = %s, RuncommandClosed = %s" % (Wrong_Emulator,Wrong_Videomode,RuncommandClosed))
        if Wrong_Emulator[0] == True:
            logging.info("ERROR: Mensaje en pantalla por cambio de emulador no permitido")
            infos = "You didn't choose wisely..."
            infos2 = "Try with other core/emulator"
            something_is_bad(infos,infos2)
        if Wrong_Videomode == True:
            logging.info("ERROR: Mensaje en pantalla por cambio de resolucion no permitido")
            infos = "You didn't choose wisely..."
            infos2 = "Don't let Retropie play with my resolutions!"
            something_is_bad(infos,infos2)
    logging.info("INFO: Saliendo de la aplicacion")
    sys.exit()


###################################################################################
#              RETROARCH CONSOLE EMULATORS WITHOUT 60Hz/50Hz SELECTOR             #
###################################################################################
#                                                                                 #
#     1) SEGA SG-1000                                                             #
#     2) NINTENDO FDS                                                             #
#     3) NEC PC ENGINE                                                            #
#     4) NEC PC ENGINE CD                                                         #
#     5) NEOGEO                                                                   #
#     6) COLECOVISION                                                             #
#     7) AMSTRAD CPC                                                              #
#     8) PRBOOM                                                                   #
#    9) SINCLAIR ZX SPECTRUM                                                     #
#                                                                                 #
###################################################################################

elif emulator == "sg-1000" or emulator == "fds" or emulator == "pcengine" or emulator == "pcenginecd" or emulator == "neogeo" or emulator == "coleco" or emulator == "amstradcpc" or emulator == "prboom" or emulator == "vectrex" or emulator == "zxspectrum":
    #RETROPIE Identifies pcenginecd as same system as pcengine. Here we make the translation pcenginecd -> pcengine
    if emulator == "pcenginecd":
        emulatorWFQ = "pcenginecd"
        emulator = "pcengine"
    #In the past there was a screen resolution selector and two configs for zxspectrum. Now it's always launched at 50hz.
    elif emulator == "zxspectrum":
        emulatorWFQ = "zxspectrum50"
        emulator = "zxspectrum"
    else:
        emulatorWFQ = emulator
    easy = easynetplay()
    change_retropie_runcommand_emulator_init(easy,emulator,emulatorWFQ,ra_cfg_path,game_name)
    commandline = "/opt/retropie/supplementary/runcommand/runcommand.sh 0 _SYS_ %s \"%s\"" % (emulator,rom_full_path)
    runcommand_process = subprocess.Popen(commandline, shell=True)
    while True:
        output = commands.getoutput('ps -A')
        if 'retroarch' in output or os.path.exists('/tmp/lchtmp'):
            # Exits if main emulator is launched
            splash_info("black")
            crt_open_screen_from_timings_cfg(emulatorWFQ,timings_full_path)
            break
        poll = runcommand_process.poll()
        if poll != None:
            # Exits if runcommand finish unexpectedly or by user
            RuncommandClosed = True
            break
    Wrong_Emulator = second_check_runcommand_emulator_init(emulator,rom_full_path,emulatorWFQ,ra_cfg_path,"unknown")
    Wrong_Videomode = check_videomodes()
    if (Wrong_Emulator[0] == True or Wrong_Videomode == True) and RuncommandClosed != True:
        while True:
            output = commands.getoutput('ps -A')
            if 'retroarch' in output:
                break
        os.system('killall retroarch > /dev/null 2>&1')
    runcommand_process.wait()
    pygame.quit()
    # Restore ES resolution from 1st line of /boot/config.txt
    es_restore_screen()

    if (Wrong_Emulator[0] == True or Wrong_Videomode == True) and RuncommandClosed != True:
        if Wrong_Emulator[0] == True:
            infos = "You didn't choose wisely..."
            infos2 = "Try with other core/emulator"
            something_is_bad(infos,infos2)
        if Wrong_Videomode == True:
            infos = "You didn't choose wisely..."
            infos2 = "Don't let Retropie play with my resolutions!"
            something_is_bad(infos,infos2)
    sys.exit()

###################################################################################
#       RETROARCH HANDHELD CONSOLE EMULATORS WITH CRT BEZEL SUPPORT MOD           #
###################################################################################
#                                                                                 #
#    1) ATARI LYNX                                                                #
#    2) NINTENDO GAMEBOY                                                          #
#    3) NINTENDO GAMEBOY COLOR                                                    #
#    4) NINTENDO GAMEBOY ADVANCE                                                  #
#    5) NEOGEO POCKET                                                             #
#    6) NEOGEO POCKET COLOR                                                       #
#    7) WONDERSWAN                                                                #
#    8) WONDERSWAN COLOR                                                          #
#    9) SEGA GAMEGEAR                                                             #
#                                                                                 #
###################################################################################

elif emulator == "atarilynx" or emulator == "gbc" or emulator == "gb" or emulator == "gba" or emulator == "ngpc" or emulator == "ngp" or emulator == "wonderswan" or emulator == "wonderswancolor" or emulator == "gamegear":
    # Read data from Screen Utility
    su = "none"
    emulatorWOV = "none"
    # Get values from su.cfg
    with open(VideoUtilityCFG, 'r') as file:
        for line in file:
            line = line.strip().replace('=',' ').split(' ')
            if line[0] == 'handheld_bezel':
                if line[1] == "1":
                    S_Game = "_s"
                else:
                    S_Game = ""
    emulatorWOV = emulator + S_Game
    easy = easynetplay()
    change_retropie_runcommand_emulator_init(easy,emulator,emulatorWOV,ra_cfg_path,game_name)
    commandline = "/opt/retropie/supplementary/runcommand/runcommand.sh 0 _SYS_ %s \"%s\"" % (emulator,rom_full_path)
    runcommand_process = subprocess.Popen(commandline, shell=True)
    while True:
        output = commands.getoutput('ps -A')
        if 'retroarch' in output or os.path.exists('/tmp/lchtmp'):
            # Exits if main emulator is launched
            splash_info("black")
            crt_open_screen_from_timings_cfg(emulator,timings_full_path)
            break
        poll = runcommand_process.poll()
        if poll != None:
            # Exits if runcommand finish unexpectedly or by user
            RuncommandClosed = True
            break
    Wrong_Emulator = second_check_runcommand_emulator_init(emulator,rom_full_path,emulatorWOV,ra_cfg_path,"unknown")
    Wrong_Videomode = check_videomodes()
    if (Wrong_Emulator[0] == True or Wrong_Videomode == True) and RuncommandClosed != True:
        while True:
            output = commands.getoutput('ps -A')
            if 'retroarch' in output:
                break
        os.system('killall retroarch > /dev/null 2>&1')
    runcommand_process.wait()
    pygame.quit()
    # Restore ES resolution from 1st line of /boot/config.txt
    es_restore_screen()
    if (Wrong_Emulator[0] == True or Wrong_Videomode == True) and RuncommandClosed != True: 
        if Wrong_Emulator[0] == True:
            infos = "You didn't choose wisely..."
            infos2 = "Try with other core/emulator"
            something_is_bad(infos,infos2)
        if Wrong_Videomode == True:
            infos = "You didn't choose wisely..."
            infos2 = "Don't let Retropie play with my resolutions!"
            something_is_bad(infos,infos2)
    sys.exit()

#####################################################################################
# RETROARCH AND NON RETROARCH ARCADE/CONSOLE SPECIAL TIMINGS CONFIGURATION PER GAME #
#####################################################################################
#                                                                                   #
#    1) LIBRETRO MAME 2000/2003/2010                                                #
#    2) LIBRETRO FBA v.0.2.97.43                                                    #
#    3) ADVMAME v3                                                                  #
#                                                                                   #
#####################################################################################

elif emulator == "arcade" or emulator == "mame-advmame" or emulator == "mame-libretro" or emulator == "fba":

    easy = easynetplay()
    LoadDBFile=change_retropie_runcommand_emulator_init(easy,emulator,retroarcharcadefile,retroarcharcadepath,game_name)
    games_datas = []
    # Read GamesList from Games Database
    with open(LoadDBFile[0]) as file:
        for line in file:
            line = line.strip().split(' ')
            games_datas.append(line)
    games_datas_len = len(games_datas)

    # Get Game Number from GamesList
    game = 0

    for i in range(games_datas_len):
        if games_datas[i][0] == game_name:
            game = i
    if game == 0:
        os.system("/opt/retropie/configs/all/CRT/Datas/default.sh")
        for i in range(games_datas_len):
            if games_datas[i][0] == "default":
                game = i

    H_Res = int(games_datas[game][1])
    V_Res = int(games_datas[game][2])
    R_Rate = float(games_datas[game][3])
    H_Pos = int(games_datas[game][4])
    H_Zoom = int(games_datas[game][5])
    V_Pos = int(games_datas[game][6])
    H_FP = int(games_datas[game][7])
    H_Sync = int(games_datas[game][8])
    H_BP = int(games_datas[game][9])
    V_Sync = int(games_datas[game][10])
    H_Freq = int(games_datas[game][11])

    # Encapsulator    
    # Center a little but don't launch the encapsulator
    if V_Res == 240:
        V_Pos -= int(5)

    # Launch the encapsulator
    if V_Res > 240:
        select = selector_encapsulate()
        if select == 1:
            # Encapsulate
            H_Freq = int(15840)
            V_Pos += int(10)

        else:
            # Cropped if is under 55Hz
            if R_Rate < 55:
                H_Freq = int(15095)
            V_Pos -= int(10)

    # Get values from FIX
    if os.path.exists(CompModesCFG):
        with open(CompModesCFG, 'r') as file:
            for line in file:
                line = line.strip().replace('=',' ').split(' ')
                if line[0] == 'mode_default':
                    SelectedMode = line[1]
        if SelectedMode.lower() != 'default':
            with open(CompModesCFG, 'r') as file:
                for line in file:
                    mask = line.strip().replace('=',' ').split(' ')
                    if mask[0] == '%s_game_mask'%SelectedMode:
                        GameMask = line.replace('%s_game_mask'%SelectedMode,'').strip().split(' ')
            H_Res = int(H_Res)+int(GameMask[0])
            V_Res = int(V_Res)+int(GameMask[1])
            R_Rate = float(R_Rate)+float(GameMask[2])
            H_Pos = int(H_Pos)+int(GameMask[3])
            H_Zoom = int(H_Zoom)+int(GameMask[4])
            V_Pos = int(V_Pos)+int(GameMask[5])
            H_FP = int(H_FP)+int(GameMask[6])
            H_Sync = int(H_Sync)+int(GameMask[7])
            H_BP = int(H_BP)+int(GameMask[8])
            V_Sync = int(V_Sync)+int(GameMask[9])
            H_Freq = int(H_Freq)+int(GameMask[10])
    
    # Get values from Screen Utility
    with open(VideoUtilityCFG, 'r') as file:
        for line in file:
            line = line.strip().replace('=',' ').split(' ')
            if line[0] == 'test60_offsetX':
                H_Pos += int(line[1])
            elif line[0] == 'test60_width':
                H_Zoom += int(line[1])
            elif line[0] == 'test60_offsetY':
                V_Pos += int(line[1])
            elif line[0] == 'frontend_rotation':
                R_Sys = int(line[1])
            elif line[0] == 'game_rotation':
                R_Game = int(line[1])

    Side_Game = games_datas[game][13]

    if LoadDBFile[1] == "mame-libretro" or LoadDBFile[1] == "fba" or LoadDBFile[1] == "unknown" or emulator == "mame-libretro" or emulator == "fba":
        if games_datas[game][13] == 'V' and R_Game == -90:
            Side_Game = 'H'
            make_retroarcharcade_configfile('1220',games_datas[game][2],0,0,games_datas[game][3],Side_Game)
            H_Pos = int('130')
        elif (games_datas[game][13] == 'V' and R_Game == 0 and R_Sys != -90) or (games_datas[game][13] == 'V' and R_Sys == 90):
            Side_Game = 'V3'
            if V_Res == 240:
                offsety = 4
            else:
                offsety = 0
            offsetx = '-10'
            make_retroarcharcade_configfile(games_datas[game][1],games_datas[game][2],offsetx,offsety,games_datas[game][3],Side_Game)
        elif games_datas[game][13] == 'V' and R_Sys == -90:
            Side_Game = 'V1'
            if V_Res == 240:
                offsety = 4
            else:
                offsety = 0
            offsetx = '-10'
            make_retroarcharcade_configfile(games_datas[game][1],games_datas[game][2],offsetx,offsety,games_datas[game][3],Side_Game)
        else:
            make_retroarcharcade_configfile(games_datas[game][1],games_datas[game][2],0,0,games_datas[game][3],Side_Game)

    if LoadDBFile[1] == "mame-advmame" or LoadDBFile[1] == "unknown" or emulator == "mame-advmame":
        if (games_datas[game][13] == 'V' and R_Game == 0 and R_Sys != -90) or (games_datas[game][13] == 'V' and R_Sys == 90):
            modificarLinea(advmame_cfg_patch,"display_ror ","display_ror yes")
            modificarLinea(advmame_cfg_patch,"display_rol ","display_rol no")
        elif games_datas[game][13] == 'V' and R_Sys == -90:
            modificarLinea(advmame_cfg_patch,"display_rol ","display_rol yes")
            modificarLinea(advmame_cfg_patch,"display_ror ","display_ror no")
        else:
            modificarLinea(advmame_cfg_patch,"display_ror ","display_ror no")
            modificarLinea(advmame_cfg_patch,"display_rol ","display_rol no")

        # Find the rom directory
        lengdir = len(rom_full_path) - len(game_name) - 5
        romr = str(rom_full_path)
        romdir = romr[0:lengdir]

        #Put the correct game folder
        modificarLinea(advmame_cfg_patch,"misc_smp ","misc_smp yes")
        modificarLinea(advmame_cfg_patch,"display_vsync ","display_vsync yes")
        modificarLinea(advmame_cfg_patch,"misc_safequit ","misc_safequit no")
        modificarLinea(advmame_cfg_patch,"dir_rom ","dir_rom "+ romdir +":/home/pi/RetroPie/BIOS")
        modificarLinea(advmame_cfg_patch,"misc_quiet ", "misc_quiet yes")
        modificarLinea(advmame_cfg_patch,"display_resizeeffect ","display_resizeeffect none")
        modificarLinea(advmame_cfg_patch,"display_resize ","display_resize none")
        modificarLinea(advmame_cfg_patch,"display_mode ","display_mode generate")


    commandline = "/opt/retropie/supplementary/runcommand/runcommand.sh 0 _SYS_ %s \"%s\"" % (emulator,rom_full_path)
    
    runcommand_process = subprocess.Popen(commandline, shell=True)
    while True:
        output = commands.getoutput('ps -A')
        if 'retroarch' in output or 'advmame' in output or os.path.exists('/tmp/lchtmp'):
            # Exits if main emulator is launched
            splash_info("black")
            crt_open_screen(H_Res, V_Res, R_Rate, H_Pos, H_Zoom, V_Pos, H_FP, H_Sync, H_BP, V_Sync, H_Freq)
            #os.system('echo %s %s %s %s %s %s %s %s %s %s %s >> /tmp/advmameres.txt'%(H_Res, V_Res, R_Rate, H_Pos, H_Zoom, V_Pos, H_FP, H_Sync, H_BP, V_Sync, H_Freq))
            break
        poll = runcommand_process.poll()
        if poll != None:
            # Exits if runcommand finish unexpectedly or by user
            RuncommandClosed = True
            break
    Wrong_Emulator = second_check_runcommand_emulator_init(emulator,rom_full_path,retroarcharcadefile,retroarcharcadepath,"unknown")
    Wrong_Videomode = check_videomodes()
    if (Wrong_Emulator[0] == True or Wrong_Videomode == True) and RuncommandClosed != True:
        while True:
            output = commands.getoutput('ps -A')
            if 'advmame' in output or 'retroarch' in output:
                break
        os.system('killall advmame > /dev/null 2>&1')
        os.system('killall retroarch > /dev/null 2>&1')

    runcommand_process.wait()
    pygame.quit()
    # Restore ES resolution from 1st line of /boot/config.txt
    es_restore_screen()
    if (Wrong_Emulator[0] == True or Wrong_Videomode == True) and RuncommandClosed != True:
        if Wrong_Emulator[0] == True:
            infos = "You didn't choose wisely..."
            infos2 = "Try with other core/emulator"
            something_is_bad(infos,infos2)
        if Wrong_Videomode == True:
            infos = "You didn't choose wisely..."
            infos2 = "Don't let Retropie play with my resolutions!"
            something_is_bad(infos,infos2)
    sys.exit()

#####################################################################################
#          NON RETROARCH CONSOLE/SYSTEMS WITH/WITHOUT 60Hz/50Hz SELECTOR            #
#                    (WITH RAW RESOLUTION IN TIMINGS.CFG)                           #
#####################################################################################
#                                                                                   #
#    1) SCUMMVM                                                                     #
#    2) DOSBox ('pc' in Retropie)                                                   #
#                                                                                   #
#####################################################################################
elif emulator == "scummvm" or emulator == "pc":
    emulatorWFQ = emulator
    logging.info("INFO: Chequeando si CRT Netplay está habilitado")
    easy = easynetplay()
    logging.info("INFO: Variable de estado de Netplay (easy): %s" % easy)
    logging.info("INFO: Iniciando primer check de emulador")
    logging.info("INFO: Llamada a la funcion change_retropie_runcommand_emulator_init(easy,emulator,emulatorWFQ,ra_cfg_path,game_name) con los siguientes parametros:")
    logging.info("INFO: %s,%s,%s,%s,%s" % (easy,emulator,emulatorWFQ,ra_cfg_path,game_name))
    change_retropie_runcommand_emulator_init(easy,emulator,emulatorWFQ,ra_cfg_path,game_name)
    logging.info("INFO: Preparando linea de comandos para lanzar runcommand:")
    commandline = "/opt/retropie/supplementary/runcommand/runcommand.sh 0 _SYS_ %s \"%s\"" % (emulator,rom_full_path)
    commandline_paused = "touch /tmp/lchtmp && sleep 1 && /opt/retropie/supplementary/runcommand/runcommand.sh 0 _SYS_ %s \"%s\"" % (emulator,rom_full_path)
    if '+start' in game_name.lower():
        logging.info("INFO: Entrando a utilidad de configuracion para %s (%s)" % (emulator, game_name))
        logging.info("INFO: touch /tmp/lchtmp && sleep 1 && /opt/retropie/supplementary/runcommand/runcommand.sh 0 _SYS_ %s \"%s\"" % (emulator,rom_full_path))
        runcommand_process = subprocess.Popen(commandline_paused, shell=True)
    else:
        logging.info("INFO: /opt/retropie/supplementary/runcommand/runcommand.sh 0 _SYS_ %s \"%s\"" % (emulator,rom_full_path))
        runcommand_process = subprocess.Popen(commandline, shell=True)
    logging.info("INFO: Subproceso lanzado")
    logging.info("INFO: Esperando a %s o que runconmmand termine" %emulator)
    while True:
        output = commands.getoutput('ps -A')
        if 'scummvm' in output or 'dosbox' in output or 'retroarch' in output or os.path.exists('/tmp/lchtmp'):
            if 'retroarch' in output:
                logging.info("INFO: Detectado retroarch en los procesos activos")
            if 'scummvm' in output:
                logging.info("INFO: Detectado scummvm en los procesos activos")
            if 'dosbox' in output:
                logging.info("INFO: Detectado dosbox en los procesos activos")
            if os.path.exists('/tmp/lchtmp'):
                logging.info("INFO: Detectado trigger file /tmp/lchtmp")
            logging.info("INFO: Ocultando pantalla")
            splash_info("black")
            logging.info("INFO: Lanzando cambio de frecuencia de monitor:")
            logging.info("INFO: crt_open_screen_raw(%s,%s)" % (emulator,timings_full_path))
            crt_open_screen_raw(emulator,timings_full_path)
            logging.info("INFO: Frecuencia cambiada, saliendo del bucle de espera")
            break
        poll = runcommand_process.poll()
        if poll != None:
            logging.info("INFO: Detectado el cierre de runcommand (poll = %s)" % poll)
            # Exits if runcommand finish unexpectedly or by user
            RuncommandClosed = True
            logging.info("INFO: Establecida variable de deteccion de cierre de runcommand (RuncommnadClose = %s)" % RuncommandClosed)
            logging.info("INFO: Saliendo del bucle de espera")
            break
    logging.info("INFO: Iniciando segundo check de Emulador")
    Wrong_Emulator = second_check_runcommand_emulator_init(emulator,rom_full_path,emulatorWFQ,ra_cfg_path,"unknown")
    logging.info("INFO: Devueltos los siguientes valores para Wrong_Emulator: %s, %s" % (Wrong_Emulator[0],Wrong_Emulator[1]))
    logging.info("INFO: Iniciando check de cambios de resolucion de retropie")
    Wrong_Videomode = check_videomodes()
    logging.info("INFO: Devueltos los siguientes valores para Wrong_Videomode: %s" % Wrong_Videomode)
    if (Wrong_Emulator[0] == True or Wrong_Videomode == True) and RuncommandClosed != True:
        logging.info("ERROR: Detectado cambio de emulador o resolucion no permitido")
        logging.info("ERROR: Esperando a que Retroarch inicie para forzar el cierre y salir")
        while True:
            output = commands.getoutput('ps -A')
            if 'retroarch' in output or 'dosbox' in output or 'scummvm' in output:
                break
        logging.info("ERROR: Cerrando el proceso de %s" % emulator)
        os.system('killall retroarch > /dev/null 2>&1')
        os.system('killall "dosbox" > /dev/null 2>&1')
        os.system('killall "scummvm" > /dev/null 2>&1')
    logging.info("INFO: Esperando a que el subproceso de Runcommand finalice")
    runcommand_process.wait()
    logging.info("INFO: Cerrando Pygame")
    pygame.quit()
    # Restore ES resolution from 1st line of /boot/config.txt
    logging.info("INFO: Restaurando resolucion base")
    es_restore_screen()
    logging.info("INFO: Resolucion restaurada")
    if (Wrong_Emulator[0] == True or Wrong_Videomode == True) and RuncommandClosed != True:
        logging.info("ERROR: Detectado un cierre forzado por CRT:")
        logging.info("ERROR: Wrong_Emulator = %s, Wrong_Videomode = %s, RuncommandClosed = %s" % (Wrong_Emulator,Wrong_Videomode,RuncommandClosed))
        if Wrong_Emulator[0] == True:
            logging.info("ERROR: Mensaje en pantalla por cambio de emulador no permitido")
            infos = "You didn't choose wisely..."
            infos2 = "Try with other core/emulator"
            something_is_bad(infos,infos2)
        if Wrong_Videomode == True:
            logging.info("ERROR: Mensaje en pantalla por cambio de resolucion no permitido")
            infos = "You didn't choose wisely..."
            infos2 = "Don't let Retropie play with my resolutions!"
            something_is_bad(infos,infos2)
    logging.info("INFO: Saliendo de la aplicacion")
    sys.exit()

#####################################################################################
#    COMMODORE AMIGA WHDLoad Only                                                   #
#####################################################################################

elif emulator == "amiga":
    easy = easynetplay()
    emulatorWFQ = emulator + "50"
    AmigaEmulatorEmpty = False
    Amiberry_HostPrefs_File = "/opt/retropie/configs/amiga/amiberry/whdboot/hostprefs.conf"
    Amiberry_WHDLoad_Database = "/opt/retropie/configs/amiga/amiberry/whdboot/game-data/whdload_db.xml"
    LoadDBFile=change_retropie_runcommand_emulator_init(easy,emulator,emulatorWFQ,ra_cfg_path,game_name)
    if "amiberry" in LoadDBFile[1]:
        infos = "none"
        infos2 = "none"
        if not os.path.exists(Amiberry_HostPrefs_File):
            infos = "Can't find this amiberry config file:"
            infos2 = "hostprefs.conf"
        if not os.path.exists(Amiberry_WHDLoad_Database):
            if infos == "none":
                infos = "Can't find this amiberry config file:"
            else:
                infos = "Can't find any of these amiberry config files:"
            if infos2 == "none":
                infos2 = "whdload_db.xml"
            else:
                infos2 = infos2 + " and whdload_db.xml"
        if infos != "none" and infos2 != "none":
            something_is_bad(infos,infos2)
            sys.exit()
        Game_VRES_WHDLoad = find_amiberry_WHDLoadDB_vertical_res("SCREEN_HEIGHT=",game_name,Amiberry_WHDLoad_Database)
        if Game_VRES_WHDLoad[1] != 0:
            HStretch = selector_stretch()
            if HStretch == True:
                modificarLinea(Amiberry_HostPrefs_File,"ASPECT_RATIO_FIX=","ASPECT_RATIO_FIX=FALSE")
                AmigaRes = "amiga_amiberry_" + str(Game_VRES_WHDLoad[1])
            else:
                modificarLinea(Amiberry_HostPrefs_File,"ASPECT_RATIO_FIX=","ASPECT_RATIO_FIX=FALSE")
                AmigaRes = "amiga_amiberry_default"
        elif Game_VRES_WHDLoad[0] == False:
            splash_info('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/stretch/nogame.png')
            modificarLinea(Amiberry_HostPrefs_File,"ASPECT_RATIO_FIX=","ASPECT_RATIO_FIX=FALSE")
            AmigaRes = "amiga_amiberry_default"
        elif Game_VRES_WHDLoad[1] == 0:
            splash_info('/opt/retropie/configs/all/CRT/Datas/FreqSelectorSkins/stretch/nores.png')
            modificarLinea(Amiberry_HostPrefs_File,"ASPECT_RATIO_FIX=","ASPECT_RATIO_FIX=FALSE")
            AmigaRes = "amiga_amiberry_default"
    elif "lr-puae" in LoadDBFile[1]:
        AmigaRes = "amiga_lr-puae"
    #elif "unknown" in LoadDBFile[1]:
    else:
        AmigaRes = "amiga_amiberry_default"
    commandline = "/opt/retropie/supplementary/runcommand/runcommand.sh 0 _SYS_ %s \"%s\"" % (emulator,rom_full_path)
    runcommand_process = subprocess.Popen(commandline, shell=True)
    while True:
        output = commands.getoutput('ps -A')
        if 'amiberry' in output or 'retroarch' in output or os.path.exists('/tmp/lchtmp'):
            # Exits if main emulator is launched
            splash_info("black")
            if 'amiberry' in LoadDBFile[1]:
                crt_open_screen_raw(AmigaRes,LoadDBFile[0])
                #crt_open_screen_raw_with_adjustement(AmigaRes,LoadDBFile[0])
            else:
                crt_open_screen_from_timings_cfg(AmigaRes,LoadDBFile[0])
            break
        poll = runcommand_process.poll()
        if poll != None:
            # Exits if runcommand finish unexpectedly or by user
            RuncommandClosed = True
            break
    Wrong_Emulator = second_check_runcommand_emulator_init(emulator,rom_full_path,retroarcharcadefile,retroarcharcadepath,LoadDBFile[1])
    Wrong_Videomode = check_videomodes()
    if (Wrong_Emulator[0] == True or Wrong_Videomode == True) and RuncommandClosed != True:
        while True:
            output = commands.getoutput('ps -A')
            if 'amiberry' in output or 'retroarch' in output:
                break
        os.system('killall amiberry > /dev/null 2>&1')
        os.system('killall retroarch > /dev/null 2>&1')
    runcommand_process.wait()
    pygame.quit()
    # Restore ES resolution from 1st line of /boot/config.txt
    es_restore_screen()
    if (Wrong_Emulator[0] == True or Wrong_Videomode == True) and RuncommandClosed != True:
        if Wrong_Emulator[0] == True:
            if Wrong_Emulator[1] == "core_changed":
                infos = "Emulator was changed for amiga system..." 
                infos2 = "Please, restart the emulation"
            else:
                infos = "You didn't choose wisely..." 
                infos2 = "Try with other core/emulator"
            something_is_bad(infos,infos2)
        if Wrong_Videomode == True:
            infos = "You didn't choose wisely..." 
            infos2 = "Don't let Retropie play with my resolutions!"
            something_is_bad(infos,infos2)
    os.system('rm /tmp/lchtmp > /dev/null 2>&1')
    sys.exit()

#####################################################################################
#    PORTS                                                                          #
#####################################################################################

elif emulator == "testing_ports":
    pass
    os.system('rm /tmp/lchtmp > /dev/null 2>&1')
    sys.exit()

#####################################################################################
#    VIDEOPLAYER                                                                    #
#####################################################################################
elif emulator == "videoplayer":
    emulatorWFQ = emulator + "50"
    video_path = os.path.dirname(rom_full_path)
    VideoPosition = 0
    video_ext = ['avi', 'mkv', 'mp4', 'mpg', 'AVI', 'MKV', 'MP4', 'MPG']
    videos = []
    for extension in video_ext:
        videos = videos + glob.glob(("%s/*.%s")%(video_path,extension))
    videos = sorted(videos)
    for srchvideo in videos:
        if srchvideo == rom_full_path:
            break
        else:
            VideoPosition += 1
    counter = 0
    for srchvideo in videos:
        counter += 1
    if counter <= 1:
        PlayAllVideos = False
    else:
        PlayAllVideos = selector_allvideos()
    launch_joy2key('kcub1', 'kcuf1', 'kcuu1', 'kcud1', '0x20', '0x71', '0x6b', '0x6a', '0x6d', '0x6e')
    crt_open_screen_from_timings_cfg(emulatorWFQ,timings_full_path)
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
    es_restore_screen()

#####################################################################################
#    ANY OTHER EMULATOR NOT SUPPORTED                                               #
#####################################################################################
else:
    infos = "System not supported [%s]" % emulator
    infos2 = ""
    something_is_bad(infos,infos2)
    es_restore_screen()
    os.system('rm /tmp/lchtmp > /dev/null 2>&1')
    sys.exit()

# Restore ES resolution from 1st line of /boot/config.txt
#es_restore_screen()
os.system('clear')
sys.exit()
