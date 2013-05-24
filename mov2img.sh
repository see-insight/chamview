#!/bin/bash
#ffmpeg -ss $tstart -threads 4 -i $Right.MOV -y -sameq -f image2 $RightScratch/img-%06d.${ext}  
if [ "$3" == "" ]
then
	$3=0
fi
echo "ffmpeg -ss $3 -i $1 -y -sameq -f image2 $2/img-%06d.png " 
ffmpeg -ss $3 -i $1 -y -sameq -f image2 $2/img-%06d.png  
