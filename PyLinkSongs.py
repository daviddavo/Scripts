#!/usr/bin/env python3
import os, glob
import configparser

CONFIG_DIR = "/home/davo/Scripts/Config.ini"

config = configparser.RawConfigParser()
config.read(CONFIG_DIR)

MOVIL_MUSICA_DIR = config.get("MUSIC", "movil-folder")
MAIN_MUSIC_DIR = config.get("MUSIC", "music-folder")
PLAYLIST_FOLDER = config.get("MUSIC", "playlist-folder")

def process_file(fname):
    movilfile = os.path.join(MOVIL_MUSICA_DIR, fname)
    mainfile = os.path.join(MAIN_MUSIC_DIR, fname)

    if (not os.path.exists(movilfile)):
        tolink = os.path.relpath(mainfile, os.path.dirname(movilfile))
        movildir = os.path.dirname(movilfile)

        if (not os.path.exists(movildir)):
            os.makedirs(movildir)
            os.chmod(movildir, 0o755)
        os.symlink(tolink, movilfile)
        print("File %s linked" % fname)

def process_m3u(fname):
    print("Processing file %s" % (fname))
    with open(fname, "r") as f:
        for l in f.readlines():
            process_file(l.strip("\n"))

if __name__ == "__main__":
    for file in glob.glob(os.path.join(PLAYLIST_FOLDER, "*.m3u")):
        process_m3u(file)
