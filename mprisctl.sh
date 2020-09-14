#!/bin/sh

# https://gist.github.com/hrnr/43d926875577f6c3fd70#file-mprisctl-sh

#PlayPause Next Previous Play Pause Stop
func="$1"

# get first mpris interface
bus=$(dbus-send --session           \
  --dest=org.freedesktop.DBus \
  --type=method_call          \
  --print-reply=literal       \
  /org/freedesktop/DBus       \
  org.freedesktop.DBus.ListNames |
  tr ' ' '\n' |
  grep 'org.mpris.MediaPlayer2' |
  head -n 1)

dbus-send --type=method_call --dest=$bus /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.$func
