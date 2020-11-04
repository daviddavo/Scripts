#!/bin/bash
beet mbsync
beet up
beet lastgenre
beet fetchart
beet extractart
beet acousticbrainz
beet write
beet alt update android
