#!/usr/bin/env python3
# coding: utf-8
#
# Retropie code/integration by -krahs- (2019)
#
# unlicense.org
#
# This script can be heavily optimized.

import os
import subprocess
import time

def get_mountedlist():
    return [(item.split()[0].replace("├─", "").replace("└─", ""),
             item[item.find("/"):]) for item in subprocess.check_output(
            ["lsblk"]).decode("utf-8").split("\n") if "/" in item]

def identify(disk):
    cmd = "find /dev/disk -ls | grep /"+disk
    output = subprocess.check_output(["/bin/bash", "-c", cmd]).decode("utf-8")
    return True if "usb" in output else False

done = []; check = []
dt = "/home/pi/RetroPie/roms"
# Remove mounted points on first boot
os.system("sudo umount -l /home/pi/RetroPie/roms > /dev/null 2>&1")
os.system("sudo umount -l /home/pi/RetroPie/BIOS > /dev/null 2>&1")
os.system("sudo umount -l /opt/retropie/configs/all/emulationstation/gamelists > /dev/null 2>&1")
# First Cleaning
os.system("rm /opt/retropie/configs/all/CRT/bin/AutomountService/mounted.cfg > /dev/null 2>&1")
os.system("rm /opt/retropie/configs/all/CRT/bin/AutomountService/umounted.cfg > /dev/null 2>&1")
os.system("touch /opt/retropie/configs/all/CRT/bin/AutomountService/umounted.cfg > /dev/null 2>&1")
MountedUSB = False
while True:
    mnt = get_mountedlist(); mount_check = [item[1] for item in mnt]
    for item in check:
        if not item in mount_check:
            try:
                # Remove mounted points when external USB is removed
                os.system("sudo umount -l /home/pi/RetroPie/roms > /dev/null 2>&1")
                os.system("sudo umount -l /home/pi/RetroPie/BIOS > /dev/null 2>&1")
                os.system("sudo umount -l /opt/retropie/configs/all/emulationstation/gamelists > /dev/null 2>&1")
                os.system("sudo umount -l %s > /dev/null 2>&1" % item)
                # Wait if there is any emulator running
                MountedUSB = False
                os.system("rm /opt/retropie/configs/all/CRT/bin/AutomountService/mounted.cfg > /dev/null 2>&1")
                os.system("touch /opt/retropie/configs/all/CRT/bin/AutomountService/umounted.cfg > /dev/null 2>&1")
                while True:
                    output = subprocess.getoutput('ps -A')
                    if not 'retroarch' in output or not 'advmame' in output or not 'scummvm' in output:
                        break
                    time.sleep(1)
                output = subprocess.getoutput('ps -A')
                # Restart ES if it is running
                if 'emulationstatio' in output:
                    os.system('touch /tmp/es-restart && pkill -f \"/opt/retropie/supplementary/.*/emulationstation([^.]|$)\"')
                check.remove(item)
            except FileNotFoundError:
                pass
    new_paths = [dev for dev in mnt if not dev in done and not dev[1] == "/"]
    valid = [dev for dev in new_paths if identify(dev[0]) == True]
    # Enter if connected device is an USB storage
    for item in valid:
        new = item[1]
        USBPhysicalDisk = item[0]
        USBMountPoing = item[1]
        # Def of hiphotetic roms paths
        RomPaths = "%s/roms" % new
        BiosPaths = "%s/bios" % new
        GamelistPaths = "%s/gamelists" % new
        ###############################################################################################################
        #    If at least exist on USB a 'roms' folder, device is allowed for external storage, function will do:      #
        #                                                                                                             #
        #       1) Check for an existing 'roms' folder if not, devide will be discarded, if yes:                      #
        #          a) Check for an existing 'bios' folder if not, function will create it                             #
        #             If 'BIOS' folder exists, function will rename it to 'bios'                                      #
        #          b) Check for an existing 'gamelist' folder if not, function will create it and:                    #
        #             b.1) Check for existing 'retropie' and 'CRT' folders if not, function will create it and:       #
        #                b.1.1) Replicate to USB gamelist.xml for both, 'retropie' ang 'CRT', this allows that     #
        #                       their options will be available after USB mounting.                                   #
        #          c) Try to replicate, if not exist, current structure of system folders to 'gamelist' and 'roms'    #
        #                                                                                                             #
        #    These are the folders will be mounted on usb:                                                            #
        #       /media/usbX/roms -> /home/pi/RetroPie/roms                                                            #
        #       /media/usbX/bios -> /home/pi/RetroPie/BIOS                                                            #
        #       /media/usbX/gamelists -> /opt/retropie/configs/all/emulationstation/gamelists                         #
        #        *Retropie also support gamelist.xml in the same folder as roms                                       #
        #                                                                                                             #
        #    *'save states' are saved in the same folder as the game i                                                #
        ###############################################################################################################
        if os.path.exists(RomPaths) and MountedUSB == False:
            #Check if there is any folder with recalbox name 'libretro-fba' and change to 'fba'
            if os.path.exists('%s/fba_libretro' % RomPaths):
                if not os.path.exists('%s/fba' % RomPaths):
                    os.rename("%s/fba_libretro" % RomPaths,"%s/fba" % RomPaths)
            if os.path.exists("%s/mame" % RomPaths):
                if not os.path.exists('%s/mame-libretro' % RomPaths):
                    os.rename("%s/mame" % RomPaths,"%s/mame-libretro" % RomPaths)
            if os.path.exists('%s/advmame' % RomPaths):
                if not os.path.exists('%s/mame-advmame' % RomPaths):
                    os.rename("%s/advmame" % RomPaths,"%s/mame-advmame" % RomPaths)
            if os.path.exists('%s/sg1000' % RomPaths):
                if not os.path.exists('%s/sg-1000' % RomPaths):
                    os.rename("%s/sg1000" % RomPaths,"%s/sg-1000" % RomPaths)
            if os.path.exists('%s/wswan' % RomPaths):
                if not os.path.exists('%s/wonderswan' % RomPaths):
                    os.rename("%s/wswan" % RomPaths,"%s/wonderswan" % RomPaths)
            if os.path.exists('%s/wswanc' % RomPaths):
                if not os.path.exists('%s/wonderswancolor' % RomPaths):
                    os.rename("%s/wswanc" % RomPaths,"%s/wonderswancolor" % RomPaths)
            if os.path.exists('%s/colecovision' % RomPaths):
                if not os.path.exists('%s/coleco' % RomPaths):
                    os.rename("%s/colecovision" % RomPaths,"%s/coleco" % RomPaths)
            if os.path.exists('%s/lynx' % RomPaths):
                if not os.path.exists('%s/atarilynx' % RomPaths):
                    os.rename("%s/lynx" % RomPaths,"%s/atarilynx" % RomPaths)
            if not os.path.exists(BiosPaths):
                if os.path.exists('%s/BIOS' % USBMountPoing):
                    os.rename("%s/BIOS" % USBMountPoing,BiosPaths)
                else:
                    os.makedirs(BiosPaths)
            if not os.path.exists(GamelistPaths):
                os.makedirs(GamelistPaths)
            if not os.path.exists("%s/1CRT" % GamelistPaths):
                os.makedirs ("%s/1CRT" % GamelistPaths)
            if not os.path.exists("%s/retropie" % GamelistPaths):
                os.makedirs ("%s/retropie" % GamelistPaths)

            os.system("rsync -a --delete /opt/retropie/configs/all/emulationstation/gamelists/1CRT/ %s/1CRT/" % GamelistPaths)
            os.system("rsync -a --delete /opt/retropie/configs/all/emulationstation/gamelists/retropie/ %s/retropie/" % GamelistPaths)

            #Check ROM folders from internal Retropie to USB external
            for item in os.listdir("/home/pi/RetroPie/roms"):
                InternalRomPath = "/home/pi/RetroPie/roms/%s" % item
                ExternalRomPath = "%s/%s" % (RomPaths,item)
                ExternalGamelistPath = "%s/%s" % (GamelistPaths,item)
                if not os.path.exists(ExternalRomPath):
                    os.makedirs(ExternalRomPath)
                #If folders exist copy .sh files from some emulator like ScummVM, DosBox or Amiga
                os.system("cp -n %s/+*.sh %s" % (InternalRomPath,ExternalRomPath))
                if not os.path.exists(ExternalGamelistPath):
                    os.makedirs(ExternalGamelistPath)

            #Reverse Check, ROM folders from USB external to internal
            for item in os.listdir(RomPaths):
                InternalRomPath = "/home/pi/RetroPie/roms/%s" % item
                ExternalRomPath = "%s/%s" % (RomPaths,item)
                InternalGamelistPath = "/opt/retropie/configs/all/emulationstation/gamelists/%s" % item
                if not os.path.exists(InternalRomPath):
                    os.makedirs(InternalRomPath)
                #If folders exist copy .sh files from some emulator like ScummVM, DosBox or Amiga
                os.system("cp -n %s/+*.sh %s" % (ExternalRomPath,InternalRomPath))
                if not os.path.exists(InternalGamelistPath):
                    os.makedirs(InternalGamelistPath)

            os.system("sudo mount --bind %s /home/pi/RetroPie/roms > /dev/null 2>&1" % RomPaths)
            os.system("sudo mount --bind %s /home/pi/RetroPie/BIOS > /dev/null 2>&1" % BiosPaths)
            os.system("sudo mount --bind %s /opt/retropie/configs/all/emulationstation/gamelists > /dev/null 2>&1" % GamelistPaths)
            MountedUSB = True
            os.system("rm /opt/retropie/configs/all/CRT/bin/AutomountService/umounted.cfg > /dev/null 2>&1")
            os.system("echo \"/dev/%s %s\" > /opt/retropie/configs/all/CRT/bin/AutomountService/mounted.cfg" % (USBPhysicalDisk,USBMountPoing))
            while True:
                # Wait if there is any emulator running
                output = subprocess.getoutput('ps -A')
                if not 'retroarch' in output or not 'advmame' in output or not 'scummvm' in output:
                    break
                time.sleep(1)
            output = subprocess.getoutput('ps -A')
            # Restart ES if it is running
            if 'emulationstatio' in output:
                os.system('touch /tmp/es-restart && pkill -f \"/opt/retropie/supplementary/.*/emulationstation([^.]|$)\"')
            check.append(new)
        #else:
            # If USB is not identified as external storage for roms.
    time.sleep(4)
    done = mnt