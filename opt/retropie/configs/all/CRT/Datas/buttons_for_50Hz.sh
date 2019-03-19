#!/bin/bash

echo "1" > /tmp/problem.srt
echo "00:00:01,500 --> 00:00:07,000" >> /tmp/problem.srt
echo "For 50Hz hold upper button before" >> /tmp/problem.srt 
omx_fnt="--font=/usr/share/fonts/dejavu/DejaVuSans-BoldOblique.ttf"
omx_opt="--no-keys --layer=10000 --aspect-mode=fill"
omx_srt="--no-ghost-box --lines=1 --align=center $omx_fnt --font-size=60 --subtitles=/tmp/problem.srt"
/usr/bin/omxplayer.bin $omx_srt /recalbox/share/CRT/Datas/v60Hz_v2.mp4 > /dev/null
