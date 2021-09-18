#!/bin/bash

set -euxo pipefail

emptyalbums=$(beet ls -a mb_albumid::'^$')
# if [ -z $emptyalbums ]; then
if true; then
    ~/Scripts/OnPlaylist.sh
    beet mod -y singleton:true album='' albumartist='Various Artists' comp=1 albumtype="compilation"
    # beet alt update android
    beet mbsync
    beet mbupdate 
    beet lastgenre
    beet up
    beet fetchart
    beet embedart
    beet acousticbrainz
    beet write
else
    echo "There are the following albums without mb_albumid" >2
    echo $emptyalbums > 2
fi
