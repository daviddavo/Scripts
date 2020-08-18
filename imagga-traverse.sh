#!/bin/bash

MAX_CNT=10

function traverse {
    # for file in "$1"/*
    cnt=1

    find $1 -type f ! -iname "*_original" ! -iname "*.gif" -print0 | while IFS= read -r -d '' file
    do
        if identify $file >/dev/null; then
            # echo $file is image
            if [ -z "$(exiftool -keywords $file)" ]; then
                echo "Image $cnt/$MAX_CNT: $file"
                ~/Scripts/imagga-tool.py "$file"
                sleep 1.5
                cnt=$((cnt+1))
                [ $cnt -gt $MAX_CNT ] && exit 0
            fi
        fi
    done
}

imgfolder="$HOME/Imágenes/Wallpapers/"
if [ ! -z "${1}" ]; then
    imgfolder="$1"
fi

if [ ! -z "${2}" ]; then
    MAX_CNT="$2"
fi

echo "Traversing folder ${imgfolder}"
traverse $imgfolder
