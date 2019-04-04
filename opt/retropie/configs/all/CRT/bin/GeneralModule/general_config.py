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

