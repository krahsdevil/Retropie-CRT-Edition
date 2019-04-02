# Original idea/coded by Ironic/aTg (2017) for RGB-Pi recalbox
# Retropie code/integration by -krahs- (2018)

# unlicense.org

import os, time, subprocess
import pygame

PYGAME_FLAGS = (pygame.FULLSCREEN|pygame.HWSURFACE)

def something_is_bad(infos,infos2):
    time.sleep(2)
    problem = "/opt/retropie/configs/all/CRT/Datas/problem.sh \"%s\" \"%s\"" % (infos, infos2)
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

    fullscreen = pygame.display.set_mode([x_screen, y_screen], PYGAME_FLAGS)
    fullscreen.fill(black)

    if SplashImagePath != "black":
        SplashImagePath = pygame.image.load(SplashImagePath)
        SplashImagePathPos = SplashImagePath.get_rect()
        SplashImagePathPos.center = ((x_screen/2), (y_screen/2))
        fullscreen.blit(SplashImagePath, SplashImagePathPos)
        pygame.display.flip()
        time.sleep(5)
    pygame.quit()

