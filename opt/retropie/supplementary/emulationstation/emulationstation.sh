#!/bin/sh
ang=0
esdir="$(dirname $0)"
tate1="/opt/retropie/configs/all/CRT/bin/emulationstation/CRTResources/configs/es-select-tate1"
tate3="/opt/retropie/configs/all/CRT/bin/emulationstation/CRTResources/configs/es-select-tate3"
yoko="/opt/retropie/configs/all/CRT/bin/emulationstation/CRTResources/configs/es-select-yoko"
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

