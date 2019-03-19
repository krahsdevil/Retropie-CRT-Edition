#!/bin/bash
echo "1" > /opt/retropie/configs/all/CRT/Datas/default.srt
echo "00:00:00,000 --> 00:00:07,000" >> /opt/retropie/configs/all/CRT/Datas/default.srt
echo $1 >> /opt/retropie/configs/all/CRT/Datas/default.srt 
omx_fnt="--font=/usr/share/fonts/dejavu/DejaVuSans-BoldOblique.ttf"
omx_opt="--no-keys --layer=10000 --aspect-mode=fill"
omx_srt="--no-ghost-box --lines=1 --align=center $omx_fnt --font-size=60 --subtitles=/opt/retropie/configs/all/CRT/Datas/default.srt"
/usr/bin/omxplayer.bin $omx_srt /opt/retropie/configs/all/CRT/Datas/default.mp4 > /dev/null
