#!/bin/sh
ang=0
esdir="$(dirname $0)"
astdir="/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/resources/assets/screen_emulationstation/CRTResources/configs"
cablesel="/opt/retropie/configs/all/CRT/bin/ScreenUtilityFiles/bin/module_rgb_cable_switcher/CRT-RGB-Cable_Launcher.py"
tate1="$astdir/es-select-tate1"
tate3="$astdir/es-select-tate3"
yoko="$astdir/es-select-yoko"
fstboot="$astdir/first-boot"

if [ -f $tate1 ]; then
    ang=1
elif [ -f $tate3 ]; then
    ang=3
elif [ -f $yoko ]; then
    ang=0
else
    ang=0
fi

while true; do
    rm -f /tmp/es-restart /tmp/es-sysrestart /tmp/es-shutdown
    if [ -f $fstboot ]; then
		rm -f $fstboot
		python $cablesel
	fi
	"$esdir/emulationstation" --screenrotate $ang "$@"
    ret=$?
    if [ -f /tmp/es-restart ]; then
        if [ -f $tate1 ]; then
            ang=1
        elif [ -f $tate3 ]; then
            ang=3
        elif [ -f $yoko ]; then
            ang=0
        else
            ang=0
        fi
        continue
    fi
    if [ -f /tmp/es-sysrestart ]; then
        rm -f /tmp/es-sysrestart
        sudo reboot
        break
    fi
    if [ -f /tmp/es-shutdown ]; then
        rm -f /tmp/es-shutdown
        sudo poweroff
        break
    fi
    break
done
exit $ret

