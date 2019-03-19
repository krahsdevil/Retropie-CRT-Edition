#!/bin/bash
echo "1" > /tmp/problem.srt
echo "00:00:00,000 --> 00:00:07,000" >> /tmp/problem.srt
echo $1 >> /tmp/problem.srt
echo $2 >> /tmp/problem.srt
omx_fnt="--font=/usr/share/fonts/dejavu/DejaVuSans-BoldOblique.ttf"
omx_opt="--no-keys --layer=10000 --aspect-mode=fill"
omx_srt="--no-ghost-box --lines=2 --align=center $omx_fnt --font-size=50 --subtitles=/tmp/problem.srt"
/usr/bin/omxplayer.bin $omx_srt /opt/retropie/configs/all/CRT/Datas/problem.mp4 > /dev/null
