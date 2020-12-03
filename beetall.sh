#!/bin/bash
~/Scripts/OnPlaylist.sh
beet alt update android
beet mbsync
beet up
beet lastgenre
beet fetchart
beet extractart
beet acousticbrainz
beet write
