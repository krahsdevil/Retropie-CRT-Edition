#!/usr/bin/python
# coding: utf-8
# Retropie code/integration by -krahs- and D_Skywalk (2019)

# TODO: add a json config to avoid this :D
XMLStringPCEnginceCD = "  <system>\n    <name>pcenginecd</name>\n    <fullname>PC Engine CD</fullname>\n    <path>/home/pi/RetroPie/roms/pcenginecd</path>\n    <extension>.cue .CUE .ccd .CCD</extension>\n    <command>python /opt/retropie/configs/all/CRT/bin/GeneralModule/emulator_launcher.py %ROM% pcenginecd dummy</command>\n    <platform>pcenginecd</platform>\n    <theme>pcenginecd</theme>\n  </system>\n"

XMLStringMAMETate = "  <system>\n    <name>mame-libretro-tate</name>\n    <fullname>mame-libretro TATE</fullname>\n    <path>/home/pi/RetroPie/roms/mame_tate</path>\n    <extension>.zip .ZIP</extension>\n    <command>python /opt/retropie/configs/all/CRT/bin/GeneralModule/emulator_launcher.py %ROM% mame-libretro dummy</command>\n    <platform>arcade</platform>\n    <theme>mame_tate</theme>\n  </system>\n"

XMLStringAdvMAMETate = "  <system>\n    <name>mame-advmame-tate</name>\n    <fullname>advmame TATE</fullname>\n    <path>/home/pi/RetroPie/roms/advmame_tate</path>\n    <extension>.zip .ZIP</extension>\n    <command>python /opt/retropie/configs/all/CRT/bin/GeneralModule/emulator_launcher.py %ROM% mame-advmame dummy</command>\n    <platform>arcade</platform>\n    <theme>advmame_tate</theme>\n  </system>\n"

XMLStringAdvMAME = "  <system>\n    <name>mame-advmame</name>\n    <fullname>Multiple Arcade Machine Emulator</fullname>\n    <path>/home/pi/RetroPie/roms/mame-advmame</path>\n    <extension>.zip .ZIP</extension>\n    <command>python /opt/retropie/configs/all/CRT/bin/GeneralModule/emulator_launcher.py %ROM% mame-advmame dummy</command>\n    <platform>arcade</platform>\n    <theme>mame-advmame</theme>\n  </system>\n"

XMLStringFBATate = "  <system>\n    <name>fba-tate</name>\n    <fullname>Final Burn Alpha-TATE</fullname>\n    <path>/home/pi/RetroPie/roms/fba_libretro_tate</path>\n    <extension>.zip .ZIP</extension>\n    <command>python /opt/retropie/configs/all/CRT/bin/GeneralModule/emulator_launcher.py %ROM% fba dummy</command>\n    <platform>arcade</platform>\n    <theme>fba_libretro_tate</theme>\n  </system>\n"

XMLStringCRT = "  <system>\n    <name>1CRT</name>\n    <fullname>CRT Utilities</fullname>\n    <path>/opt/retropie/configs/all/CRT/config</path>\n    <extension>.py</extension>\n    <command>python %ROM%</command>\n    <platform />\n    <theme>crt</theme>\n  </system>\n"

XMLStringVideoPlayer = "  <system>\n    <name>videoplayer</name>\n    <fullname>Video Player</fullname>\n    <path>/home/pi/RetroPie/roms/videos</path>\n    <extension>.mkv .avi .mp4 .mpg .MKV .AVI .MP4 .MPG</extension>\n    <command>python /opt/retropie/configs/all/CRT/bin/GeneralModule/emulator_launcher.py %ROM% videoplayer dummy</command>\n    <platform>videoplayer</platform>\n    <theme>videoplayer</theme>\n  </system>\n"

XMLStringRetropie = "  <system>\n    <name>retropie</name>\n    <fullname>RetroPie</fullname>\n    <path>/home/pi/RetroPie/retropiemenu</path>\n    <extension>.rp .sh</extension>\n    <command>sudo /home/pi/RetroPie-Setup/retropie_packages.sh retropiemenu launch %ROM% &lt;/dev/tty &gt;/dev/tty</command>\n    <platform/>\n    <theme>retropie</theme>\n    </system>\n"


SYSTEMS = {
    "pcenginecd": { "core": "pcenginecd", "check": False, "xml": XMLStringPCEnginceCD, "theme": "pcenginecd" },
    "mame-libretro-tate": { "core": "mame-libretro", "check": False, "xml": XMLStringMAMETate, "theme": "mame_tate" },
    "mame-advmame": { "core": "mame-advmame", "check": False, "xml": XMLStringAdvMAME, "theme": "mame-advmame" },
    "mame-advmame-tate": { "core": "mame-advmame", "check": False, "xml": XMLStringAdvMAMETate, "theme": "advmame_tate" },
    "fba-tate": { "core": "fba", "check": False, "xml": XMLStringFBATate, "theme": "fba_libretro_tate" },
    "1CRT": { "core": "", "check": False, "xml": XMLStringCRT, "theme": "crt" },
    "videoplayer": { "core": "videoplayer", "check": False, "xml": XMLStringVideoPlayer, "theme": "videoplayer" },
    "retropie": { "core": "", "check": False, "xml": XMLStringRetropie, "theme": "retropie" },
}

