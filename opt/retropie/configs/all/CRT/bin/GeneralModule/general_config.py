#!/usr/bin/python
# coding: utf-8
# Retropie code/integration by -krahs- and D_Skywalk (2019)

# TODO: add a json config to avoid this :D
XMLStringPCEnginceCD = "  <system>\n    <name>pcenginecd</name>\n    <fullname>PC Engine CD</fullname>\n    <path>/home/pi/RetroPie/roms/pcenginecd</path>\n    <extension>.cue .CUE .ccd .CCD</extension>\n    <command>python /opt/retropie/configs/all/CRT/bin/GeneralModule/emulator_launcher.py %%ROM%% pcenginecd dummy</command>\n    <platform>pcenginecd</platform>\n    <theme>pcenginecd</theme>\n  </system>\n"

XMLStringMAMETate = "  <system>\n    <name>mame-libretro-tate</name>\n    <fullname>mame-libretro TATE</fullname>\n    <path>/home/pi/RetroPie/roms/mame_tate</path>\n    <extension>.zip .ZIP</extension>\n    <command>python /opt/retropie/configs/all/CRT/bin/GeneralModule/emulator_launcher.py %%ROM%% mame-libretro dummy</command>\n    <platform>arcade</platform>\n    <theme>mame_tate</theme>\n  </system>\n"

XMLStringAdvMAMETate = "  <system>\n    <name>mame-advmame-tate</name>\n    <fullname>advmame TATE</fullname>\n    <path>/home/pi/RetroPie/roms/advmame_tate</path>\n    <extension>.zip .ZIP</extension>\n    <command>python /opt/retropie/configs/all/CRT/bin/GeneralModule/emulator_launcher.py %%ROM%% mame-advmame dummy</command>\n    <platform>arcade</platform>\n    <theme>advmame_tate</theme>\n  </system>\n"

XMLStringFBATate = "  <system>\n    <name>fba-tate</name>\n    <fullname>Final Burn Alpha-TATE</fullname>\n    <path>/home/pi/RetroPie/roms/fba_libretro_tate</path>\n    <extension>.zip .ZIP</extension>\n    <command>python /opt/retropie/configs/all/CRT/bin/GeneralModule/emulator_launcher.py %%ROM%% fba dummy</command>\n    <platform>arcade</platform>\n    <theme>fba_libretro_tate</theme>\n  </system>\n"

XMLStringCRT = "  <system>\n    <name>1CRT</name>\n    <fullname>CRT Utilities</fullname>\n    <path>/opt/retropie/configs/all/CRT/config</path>\n    <extension>.py</extension>\n    <command>python %%ROM%%</command>\n    <platform />\n    <theme>crt</theme>\n  </system>\n"

XMLStringVideoPlayer = "  <system>\n    <name>videoplayer</name>\n    <fullname>Video Player</fullname>\n    <path>/home/pi/RetroPie/roms/videos</path>\n    <extension>.mkv .avi .mp4 .mpg .MKV .AVI .MP4 .MPG</extension>\n    <command>python /opt/retropie/configs/all/CRT/bin/GeneralModule/emulator_launcher.py %ROM% videoplayer dummy</command>\n    <platform>videoplayer</platform>\n    <theme>videoplayer</theme>\n  </system>\n"


# ES_check Systems
SYSTEMS = {
    "pcenginecd": { "core": "pcenginecd", "check": False, "xml": XMLStringPCEnginceCD },
    "mame-libretro-tate": { "core": "mame-libretro", "check": False, "xml": XMLStringMAMETate },
    "mame-advmame": { "core": "mame-advmame", "check": False, "xml": None },
    "mame-advmame-tate": { "core": "mame-advmame", "check": False, "xml": XMLStringAdvMAMETate },
    "fba-tate": { "core": "fba", "check": False, "xml": XMLStringFBATate },
    "1CRT": { "core": "", "check": False, "xml": XMLStringCRT },
    "videoplayer": { "core": "videoplayer", "check": False, "xml": XMLStringVideoPlayer },
    "retropie": { "core": "", "check": False, "xml": None },
}

MAME_DB = {
    "mame2000": "/opt/retropie/configs/all/CRT/Resolutions/mame037b5_games.txt",
    "mame2003": "/opt/retropie/configs/all/CRT/Resolutions/mame078_games.txt",
    "mame2010": "/opt/retropie/configs/all/CRT/Resolutions/mame0139_games.txt"
}

FBALPHA_DB = { "default": "/opt/retropie/configs/all/CRT/Resolutions/fbalpha_games.txt" }
ADVMAME_DB = { "default": "/opt/retropie/configs/all/CRT/Resolutions/advmame_games.txt" }


# launcher Systems - TODO: unify
#
L_SYSTEM = {

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
    #    11) ATARI ST                                                                 #
    #    12) VIDEOPAC MAGNAVOX ODYSSEY 2                                              #
    #    13) SINCLAIR ZX 81                                                           #
    #    14) COMMODORE 64                                                             #
    #                                                                                 #
    ###################################################################################
    "megadrive": { "has_selector": True },
    "segacd": { "has_selector": True },
    "sega32x": { "has_selector": True },
    "mastersystem": { "has_selector": True },
    "n64": { "has_selector": True },
    "nes": { "has_selector": True },
    "snes": { "has_selector": True },
    "psx": { "has_selector": True },
    "msx": { "has_selector": True },
    "atari2600": { "has_selector": True },
    "odyssey2": { "has_selector": True },
    "zx81": { "has_selector": True },
    "atarist": { "has_selector": True },
    "c64": { "has_selector": True },

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
    #     9) ATARI 7800                                                               #
    #    10) SINCLAIR ZX SPECTRUM                                                     #
    #                                                                                 #
    ###################################################################################
    "sg-1000": { },
    "fds": { },
    "pcengine": { },
    "neogeo": { },
    "colecovision": { },
    "amstradcpc": { },
    "prboom": { },
    "atari7800": { },
    "vectrex": { },
    "pcenginecd": { "core_freq_name": "pcengine" },
    "zxspectrum": { "core_freq_name": "zxspectrum50" },

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
    "atarilynx": { "has_bezel": True },
    "gbc": { "has_bezel": True },
    "gb": { "has_bezel": True },
    "gba": { "has_bezel": True },
    "ngpc": { "has_bezel": True },
    "ngp": { "has_bezel": True },
    "wonderswan": { "has_bezel": True },
    "wonderswancolor": { "has_bezel": True },
    "gamegear": { "has_bezel": True },

    #####################################################################################
    # RETROARCH AND NON RETROARCH ARCADE/CONSOLE SPECIAL TIMINGS CONFIGURATION PER GAME #
    #####################################################################################
    #                                                                                   #
    #    1) LIBRETRO MAME 2000/2003/2010                                                #
    #    2) LIBRETRO FBA v.0.2.97.43                                                    #
    #    3) ADVMAME v3                                                                  #
    #                                                                                   #
    #####################################################################################
    "arcade": { "game_freq_db": True },
    "mame-advmame": { "game_freq_db": True, "freq_db": ADVMAME_DB },
    "mame-libretro": { "game_freq_db": True, "freq_db": MAME_DB },
    "fba": { "game_freq_db": True, "freq_db": FBALPHA_DB },

    #####################################################################################
    #          NON RETROARCH CONSOLE/SYSTEMS WITH/WITHOUT 60Hz/50Hz SELECTOR            #
    #                    (WITH RAW RESOLUTION IN TIMINGS.CFG)                           #
    #####################################################################################
    #                                                                                   #
    #    1) SCUMMVM                                                                     #
    #    2) DOSBox ('pc' in Retropie)                                                   #
    #                                                                                   #
    #####################################################################################
    "scummvm": { "core_raw_freq": True, "bin_names": ["scummvm"] },
    "pc": { "core_raw_freq": True, "bin_names": ["dosbox"] },

    #####################################################################################
    #    COMMODORE AMIGA WHDLoad Only                                                   #
    #####################################################################################
    "amiga": { "core_freq_name": "amiga50" },

    #####################################################################################
    #    VIDEOPLAYER                                                                    #
    #####################################################################################
    "videoplayer": { "ignore_netplay": True, "core_freq_name": "videoplayer50" }, # FIXME: por que 50

    #####################################################################################
    #    ANY OTHER EMULATOR NOT SUPPORTED                                               #
    #####################################################################################
    #####################################################################################
    #    PORTS                                                                          #
    #####################################################################################
    #"testing_ports": { "is_invalid": True },
    # '' in output or '' in output or 'retroarch' 'amiberry' 'advmame' 'mupen'


}
