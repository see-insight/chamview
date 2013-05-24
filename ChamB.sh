#!/bin/bash
#ffmpeg -ss 85 -i "../ChamB_21Jul_720?60f.MOV" -y -sameq -f image2 ./ChamB/img-%06d.png

./chamview.py --ppos ChamB.txt --dir ./ChamB/ -c BasicGui -o ChamB.txt


