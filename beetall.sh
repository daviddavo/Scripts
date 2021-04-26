#!/bin/bash

set -euxo pipefail

emptyalbums=$(beet ls -a mb_albumid:'^$')
if [ -z $emptyalbums ]; then
    ~/Scripts/OnPlaylist.sh
    # beet alt update android
    beet mbsync
    beet mbupdate 
    beet lastgenre
    beet up
    beet fetchart
    beet extractart
    beet acousticbrainz
    beet write
else
    echo "There are the following albums without mb_albumid" >2
    echo $emptyalbums > 2
fi
