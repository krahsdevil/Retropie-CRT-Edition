# Original idea/coded by Ironic/aTg (2017) for RGB-Pi recalbox
# Retropie code/integration by -krahs- (2018)

# unlicense.org

import os, time, imp, subprocess, re, logging, commands
import pygame

from launcher_module.core_paths import CRTROOT_PATH, RETROPIEEMU_PATH
from launcher_module.file_helpers import md5_file, ini_get, touch_file, add_line, modify_line
from distutils.version import LooseVersion

PYGAME_FLAGS = (pygame.FULLSCREEN|pygame.HWSURFACE)

#
# simple plugin system
#

# returns a list of .py files and ignores __init__.py
def plugin_list(p_sPath):
    plugins = []
    possibleplugins = os.listdir(p_sPath)
    for pl in possibleplugins:
        location = os.path.join(p_sPath, pl)
        if pl.endswith(".py") and not pl.endswith("_.py"):
            sClass = pl[:-3]
            info = imp.find_module(sClass, [p_sPath])
            plugins.append({"name": sClass, "info": info})
    return plugins

# load module dinamically and his main class (same name as .py file)
# ex: userplugin.py, userplugin()
def plugin_load(p_oPlugin):
    _module = imp.load_module(p_oPlugin["name"], *p_oPlugin["info"])
    return getattr(_module, p_oPlugin["name"])


#
# CRT Team functions
#
def something_is_bad(infos,infos2):
    time.sleep(0.5)
    problem = "/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/media/info_splash_screen/problem.sh \"%s\" \"%s\"" % (infos, infos2)
    os.system(problem)

def get_xy_screen():
    global x_screen
    global y_screen
    process = subprocess.Popen("fbset", stdout=subprocess.PIPE)
    output = process.stdout.read()
    for line in output.splitlines():
        if 'x' in line and 'mode' in line:
            ResMode = line
            ResMode = ResMode.replace('"','').replace('x',' ').split(' ')
            x_screen = int(ResMode[1])
            y_screen = int(ResMode[2])

def splash_info(SplashImagePath):
    get_xy_screen()
    pygame.init()
    black = pygame.Color(0, 0, 0)
    white = pygame.Color(255,255,255)
    pygame.display.init()
    pygame.mouse.set_visible(0)

    """Try to fill black, sometimes error because big superresolution"""
    try:
        fullscreen = pygame.display.set_mode([x_screen, y_screen], PYGAME_FLAGS)
        fullscreen.fill(black)
        logging.info("black screen %s x %s applied"%(x_screen, y_screen))
    except:
        pygame.quit()
        raise

    if SplashImagePath != "black":
        SplashImagePath = pygame.image.load(SplashImagePath)
        SplashImagePathPos = SplashImagePath.get_rect()
        SplashImagePathPos.center = ((x_screen/2), (y_screen/2))
        fullscreen.blit(SplashImagePath, SplashImagePathPos)
        pygame.display.flip()
        time.sleep(5)
    pygame.quit()

#  check if retroarch is lower than v1.7.5 because a change in aspect_ratio_index value
def ra_check_version(p_sSystemCfgPath = None):
    p_sRetroarchDB = os.path.join(CRTROOT_PATH, "bin/ScreenUtilityFiles/config_files/retroarchdb.txt")
    p_sRetroarchBin = os.path.join(RETROPIEEMU_PATH, "retroarch/bin/retroarch")
    logging.info("checking retroarch version")
    if not p_sSystemCfgPath:
        return
    if not os.path.isfile(p_sRetroarchDB):
        touch_file(p_sRetroarchDB)
        logging.info("Created retroarch database")
        
    ra_hash = md5_file(p_sRetroarchBin)
    f = open(p_sRetroarchDB, "r")
    full_lines = f.readlines()
    f.close()
    ra_version = None
    for line in full_lines:
        if line != "\n":
            lValues = line.strip().split(' ')
            if ra_hash == lValues[1]:
                ra_version = lValues[2]
                break
    # update file if not found
    if not ra_version:
        ra_output = commands.getoutput("%s --version" % p_sRetroarchBin)
        for line in ra_output.splitlines():
            lValues = line.strip().split(' ')
            if 'RetroArch' in lValues[0]:
                ra_version = lValues[5]
                add_line(p_sRetroarchDB, "RetroArch %s %s" % (ra_hash,ra_version))

    ratio = "23" # default 1.7.5 value
    if LooseVersion(ra_version) < LooseVersion("v1.7.5"):
        logging.info("early retroarch version, fixing ratio number - %s"%LooseVersion(ra_version))
        ratio = "22"
    ratio_value = ini_get(p_sSystemCfgPath, "aspect_ratio_index")
    if ratio != ratio_value.replace('"', ''):
        modify_line(p_sSystemCfgPath, "aspect_ratio_index", "aspect_ratio_index = \"%s\"" % ratio)
        logging.info("fixed: %s version: %s ratio: %s (%s)" % (p_sSystemCfgPath, ra_version, ratio, ratio_value))

def compact_rom_name(p_sRomName):
    sPreCleanedGame = re.sub('[^a-zA-Z0-9-_]+','', p_sRomName )
    sCleanedGame = re.sub(' ','', sPreCleanedGame)
    return sCleanedGame