# Modified version of BGM script version 1.03 made by Livewire
# BGM Overlay code added by madmodder123
# Version 1.01 - Changed song_title.png to write to RAM instead of the SD Card (Thanks zerojay!)

import os
import time
import random
#import pygame # if you don't have pygame: sudo apt-get install python-pygame
#also that line is commented out as we import the mixer specifically a bit further down.
import re
import subprocess # used to grab screen resolution
    
###CONFIG SECTION###
startdelay = 0 # Value (in seconds) to delay audio start.  If you have a splash screen with audio and the script is playing music over the top of it, increase this value to delay the script from starting.
musicdir = '/opt/retropie/configs/music' # "~/" is the equivalent to "/home/pi"
maxvolume = 0.75
volumefadespeed = 0.02
restart = True # If true, this will cause the script to fade the music out and -stop- the song rather than pause it.
startsong = "" # if this is not blank, this is the EXACT, CaSeSeNsAtIvE filename of the song you always want to play first on boot.

### if ~ is used, change it to home directory (EXAMPLE: "~/BGM" to "/home/pi/BGM")
if "~/" in musicdir:
    musicdir = os.path.expanduser(musicdir)

# Read screen resolution for overlay settings
fbset_exists = os.path.isfile('/bin/fbset')
tvservice_exists = os.path.isfile('/usr/bin/tvservice')

if fbset_exists:
    screen_width = subprocess.check_output("fbset -fb /dev/fb0 | grep '\".*\"' | grep -m 1 -o '[0-9][0-9][0-9]\+x' | tr -d 'x'", shell=True)
    screen_width = screen_width.rstrip() # remove extra lines
    screen_height = subprocess.check_output("fbset -fb /dev/fb0 | grep '\".*\"' | grep -m 1 -o 'x[0-9][0-9][0-9]\+' | tr -d 'x'", shell=True)
    screen_height = screen_height.rstrip() # remove extra lines
elif tvservice_exists:
    screen_width = subprocess.check_output("tvservice -s | grep -m 1 -o '[0-9][0-9][0-9]\+x[0-9][0-9][0-9]\+' | grep -m 1 -o '[0-9][0-9][0-9]\+x' | grep -m 1 -o '[0-9][0-9][0-9]\+'", shell=True)
    screen_width = screen_width.rstrip() # remove extra lines
    screen_height = subprocess.check_output("tvservice -s | grep -m 1 -o '[0-9][0-9][0-9]\+x[0-9][0-9][0-9]\+' | grep -m 1 -o 'x[0-9][0-9][0-9]\+' | grep -m 1 -o '[0-9][0-9][0-9]\+'", shell=True)
    screen_height = screen_height.rstrip() # remove extra lines
else:
    print "ERROR COUDLN'T FIND FBSET OR TVSERVICE! Please contact madmodder123 for help!"
    
#print "Resolution - " + resolution + " - " + screen_width + "x" + screen_height

if int(screen_height) >= 900:
    resolution = "1080p"
elif int(screen_height) >= 600 and int(screen_height) <= 800:
    resolution = "720p"
elif int(screen_height) <= 599:
    resolution = "SD"
else:
    resolution = "ERROR"

###Overlay Config###
overlay_enable = False # Enable or disable the overlay
overlay_fade_out = True # Change to "False" to have the overlay remain on the screen until an emulator/application is launched
overlay_fade_out_time = 8 # Hide the overlay after X seconds
overlay_pngview_location = '/opt/retropie/configs/all/CRT/bin/BackGroundMusic/pngview'
overlay_background_color = 'White' #White is default
overlay_text_color = 'DimGray' #DimGray is default
#overlay_text_font = '/usr/share/fonts/opentype/Pixel.otf' # Pixel font included by default
overlay_text_font = '/opt/retropie/configs/all/CRT/config/PetMe64.ttf' # Pixel font included by default
#overlay_text_font = 'FreeSans' # Default system font
overlay_rounded_corners = False #Set to "True" round the corners of the overlay
overlay_replace_newline = True # Set to "True" to turn all " - " symbols in song title to new line characters. (Mostly for OGST Display)

# The code below adjusts the size/location of the overlay depending upon the screen resolution
# Adjust these to your needs
if resolution == "1080p":
    overlay_size = '600x32'
    overlay_x_offset = '0'
    overlay_y_offset = '0'
elif resolution == "720p":
    overlay_size = '300x21'
    overlay_x_offset = '0'
    overlay_y_offset = '0'
else:
    # Any resolution lower than 720p
    overlay_size = '150x14'
    overlay_x_offset = '0'
    overlay_y_offset = '0'

# Get the user's name
user = os.path.expanduser('~')          
user = os.path.split(user)[-1]  
OGST_exists = False # Don't change this. It will automatically detect if OGST is used.
if user == "pi":
    HOST_SYSTEM = "Raspberry Pi"
    #print "Raspberry Pi"
elif user == "pigaming":
    HOST_SYSTEM = "ODROID"
    #print "ODROID"
    #Check if the OGST case is being used (ODROID ONLY)
    framebuffer1_exists = os.path.exists('/dev/fb1')
    ogstdir = os.path.expanduser("~/ogst")
    OGST_dir_exists = os.path.isdir(ogstdir)
    if framebuffer1_exists == OGST_dir_exists == True:
        OGST_exists = True
        #print "OGST CONFIRMED"
else:
    HOST_SYSTEM = "Linux"
    #print "Linux System"

## ~~~~~~~~~ODROID OGST SETTINGS~~~~~~~~~~~~~~~~~~
if OGST_exists == True:
    overlay_size = '320x240' # Change me to adjust overlay size (ONLY FOR OGST CASE!) [OGST SCREEN IS 320x240]
    overlay_rounded_corners = True

if overlay_rounded_corners == True:
    overlay_rounded = "-alpha set -virtual-pixel transparent -channel A -blur 0x8 -threshold 50% +channel " # Add code for rounded corners if enabled.
else:
    overlay_rounded = "" # Add nothing to code if not enabled.

###Local Variables###
bgm = [mp3 for mp3 in os.listdir(musicdir) if mp3[-4:] == ".mp3" or mp3[-4:] == ".ogg"] # Find everything that's .mp3 or .ogg
lastsong = -1
currentsong = -1
from pygame import mixer # import PyGame's music mixer
mixer.init() # Prep that bad boy up.
random.seed()
volume = maxvolume # Store this for later use to handle fading out.

shm_exists = os.path.isdir('/dev/shm') 
if shm_exists == True:
    overlay_tmp_file = '/dev/shm/song_title.png'
    tmp_folder= '/dev/shm/'
else:
    overlay_tmp_file = '/tmp/song_title.png'
    tmp_folder= '/tmp/'

# Create song_title.png if it doesn't exist
if not os.path.exists(overlay_tmp_file):
    os.mknod(overlay_tmp_file)

#TODO: Fill in all of the current RetroPie Emulator process names in this list.
emulatornames = ["retroarch","ags","uae4all2","uae4arm","capricerpi","linapple","hatari","stella","atari800","xroar","vice","daphne","reicast","pifba","osmose","gpsp","jzintv","basiliskll","mame","advmame","dgen","openmsx","mupen64plus","gngeo","dosbox","ppsspp","simcoupe","scummvm","snes9x","pisnes","frotz","fbzx","fuse","gemrb","cgenesis","zdoom","eduke32","lincity","love","kodi","alephone","micropolis","openbor","openttd","opentyrian","cannonball","tyrquake","ioquake3","residualvm","xrick","sdlpop","uqm","stratagus","wolf4sdl","solarus","drastic","coolcv","PPSSPPSDL","moonlight","Xorg","smw","omxplayer.bin","wolf4sdl-3dr-v14","wolf4sdl-gt-v14","wolf4sdl-spear","wolf4sdl-sw-v14","xvic","xvic cart","xplus4","xpet","x128","x64sc","x64","prince","fba2x","steamlink","pcsx-rearmed","limelight","sdltrs","ti99sm","dosbox-sdl2","minivmac","quasi88","xm7","yabause","abuse","cdogs-sdl","cgenius","digger","gemrb","hcl","love","love-0.10.2","openblok","openfodder","srb2","yquake2","amiberry","zesarux","dxx-rebirth","zesarux"]

#test: Ran into some issues with script crashing on a cold boot, so we're camping for emulationstation (if ES can start, so can we!)
esStarted = False
while not esStarted:
    time.sleep(1)
    pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
    for pid in pids:
        try:
            procname = open(os.path.join('/proc',pid,'comm'),'rb').read()
            if procname[:-1] == "emulationstatio": # Emulation Station's actual process name is apparently short 1 letter.
                esStarted=True
        except IOError:    
            continue

#ES Should be going, see if we need to delay our start

if startdelay > 0:
    time.sleep(startdelay) # Delay audio start per config option above

#Look for OMXplayer - if it's running, someone's got a splash screen going!
pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
for pid in pids:
    try:
        procname = open(os.path.join('/proc',pid,'comm'),'rb').read()
        if procname[:-1] == "omxplayer" or procname[:-1] == "omxplayer.bin": # Looking for a splash screen!
            while os.path.exists('/proc/'+pid):
                time.sleep(1) #OMXPlayer is running, sleep 1 to prevent the need for a splash.
    except IOError:    
        continue

#Check for a starting song
if not startsong == "":
    try:
        currentsong = bgm.index(startsong) #Set the currentsong to the index in BGM that is our startingsong.
    except:
        currentsong = -1 #If this triggers, you probably screwed up the filename, because our startsong wasn't found in the list.

#This is where the magic happens.
while True:
    while not esStarted: #New check (4/23/16) - Make sure EmulationStation is actually started.  There is code further down that, as part of the emulator loop, makes sure eS is running.
        if mixer.music.get_busy():
            mixer.music.stop(); #halt the music, emulationStation is not running!
        time.sleep(10)
        pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
        for pid in pids:
            try:
                procname = open(os.path.join('/proc',pid,'comm'),'rb').read()
                if procname[:-1] == "emulationstatio": # Emulation Station's actual process name is apparently short 1 letter.
                    esStarted=True # Will cause us to break out of the loop because ES is now running.
            except IOError:    
                continue
                
    #Check to see if the DisableMusic file exists; if it does, stop doing everything!
    #disablefile = os.path.expanduser('~/DisableMusic')
    #if os.path.exists(disablefile):
        #print "Music Disabled - Exiting"
    #    exit()

    if not mixer.music.get_busy(): # We aren't currently playing any music
        while currentsong == lastsong and len(bgm) > 1:    #If we have more than one BGM, choose a new one until we get one that isn't what we just played.
            currentsong = random.randint(0,len(bgm)-1)
        song = os.path.join(musicdir,bgm[currentsong])
        mixer.music.load(song)
        if overlay_enable == True :
            if HOST_SYSTEM == "Raspberry Pi":
                os.system("sudo killall -q " + overlay_pngview_location + " &") # Kill song overlay if it is open
                #print "Killing pngview overlay if it is open before starting"
        lastsong=currentsong
        mixer.music.set_volume(maxvolume) # Pygame sets this to 1.0 on new song; in case max volume -isnt- 1, set it to max volume.
        mixer.music.play()
        #print "BGM Now Playing: " + song
        song_title = re.sub(r"(" + musicdir + "/|\.\w*$)", "", song) # Remove directory and extension from song
        song_title = song_title.upper()
        if overlay_replace_newline == True:
            song_title = song_title.replace(" - ","\n")
        if overlay_enable == True:
            if HOST_SYSTEM == "Raspberry Pi":
                #print "Starting Raspberry Pi overlay"
                generate_image = "sudo convert " + overlay_rounded + "-background " + overlay_background_color + " -fill " + overlay_text_color + " -font " + overlay_text_font + " -gravity center -size " + overlay_size + " label:\"" + song_title + "\" " + overlay_tmp_file # Generate png from text 
                os.system(generate_image)
                show_overlay = overlay_pngview_location + " -d 0 -b 0x0000 -l 15000 -y " + overlay_y_offset + " -x " + overlay_x_offset + " " + overlay_tmp_file + " &" # ( -n cmd doesn't seem to work)
                time.sleep(1)
                os.system(show_overlay)
                if overlay_fade_out == True:
                    time.sleep(overlay_fade_out_time)
                    os.system("sudo killall -q " + overlay_pngview_location + " &") # Kill song overlay
            elif HOST_SYSTEM == "ODROID":
                #ODROID
                #print "Starting ODROID (or other linux) overlay"
                generate_image = "sudo convert " + overlay_rounded + "-background " + overlay_background_color + " -fill " + overlay_text_color + " -font " + overlay_text_font + " -gravity center -size " + overlay_size + " label:\"" + song_title + "\" " + overlay_tmp_file # Generate png from text
                os.system(generate_image)
                if OGST_exists == True:
                    #OGST SCREEN
                    #print "Starting OGST overlay"
                    OGST_display_code = "cat /dev/fb1 > " + tmp_folder + "image.raw; img2fb -i " + overlay_tmp_file + "; sleep " + str(overlay_fade_out_time) + "; cat " + tmp_folder + "image.raw > /dev/fb1"
                    os.system(OGST_display_code) 
                else:
                    print "framebuffer write for ODROID"
            else:
                #LINUX HOST
                print "framebuffer write linux"
        
    #Emulator check
    pids = [pid for pid in os.listdir('/proc') if pid.isdigit()] 
    emulator = -1;
    esStarted=False #New check 4-23-16 - set this to False (assume ES is no longer running until proven otherwise)
    for pid in pids:
        try:
            procname = open(os.path.join('/proc',pid,'comm'),'rb').read()
            if procname[:-1] == "emulationstatio": # Killing 2 birds with one stone, while we look for emulators, make sure EmulationStation is still running.
                    esStarted=True # And turn it back to True, because it wasn't done running.  This will prevent the loop above from stopping the music.
            
            if procname[:-1] in emulatornames: #If the process name is in our list of known emulators
                emulator = pid;
                #Turn down the music
                ##print "Emulator found! " + procname[:-1] + " Muting the music..."
                if overlay_enable == True:
                    if HOST_SYSTEM == "Raspberry Pi":
                        os.system("sudo killall -q " + overlay_pngview_location + " &") # Kill song overlay
                while volume > 0:
                    volume = volume - volumefadespeed
                    if volume < 0:
                        volume=0
                    mixer.music.set_volume(volume);
                    time.sleep(0.05)            
                if restart:
                    mixer.music.stop() #we aren't going to resume the audio, so stop it outright.
                else:
                    mixer.music.pause() #we are going to resume, so pause it.
                #print("Muted.  Monitoring emulator.")
                while os.path.exists("/proc/" + pid):
                    time.sleep(1); # Delay 1 second and check again.
                #Turn up the music
                #print "Emulator finished, resuming audio..."
                if not restart:
                    mixer.music.unpause() #resume
                    while volume < maxvolume:
                        volume = volume + volumefadespeed;
                        if volume > maxvolume:
                            volume=maxvolume
                        mixer.music.set_volume(volume);
                        time.sleep(0.05)
                    if overlay_enable == True:
                        if HOST_SYSTEM == "Raspberry Pi":
                            os.system(show_overlay) # Display generated PNG
                            if overlay_fade_out == True:
                                time.sleep(overlay_fade_out_time)
                                os.system("sudo killall -q " + overlay_pngview_location + " &") # Kill song overlay    
                #print "Music Resumed"
                volume=maxvolume # ensures that the volume is manually set (if restart is True, volume would be at zero)
        except IOError: #proc has already terminated, ignore.
            continue

    time.sleep(1);
    #end of the main while loop
    
print "An error has occurred that has stopped BGM.py from executing." #theoretically you should never get this far.
