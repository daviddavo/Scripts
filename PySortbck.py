#!/usr/bin/python3
import sys, os, subprocess,time, configparser
import random
from PIL import Image
import mimetypes

CONFIG_DIR   = "Config.ini"
DEBUG = True
MORELESS = .10
UNKNOWN_FOLDER = "UnknownResolution"
# UNKNOWN_FOLDER = None
tosort = [(16/9,"16x9/"), (9/16,"Vertical/"), (4/3,"4x3/")]

def getToMove(toMove, fname):
    files = os.listdir(fname)
    for f in files:
        af = os.path.join(fname, f)

        mime = mimetypes.guess_type(af)[0]
        if mime is not None and mime.split("/")[0] == "image":
            im = Image.open(af)
            w, h = im.size
            
            for r in tosort:
                sort = False
                if (r[0]-MORELESS < w/h < r[0]+MORELESS):
                    toMove[r[1]].append(f)
                    print("Moving %s to %s" % (f, r[1]))
                    sort = True
                    break

            if UNKNOWN_FOLDER is not None and not sort:
                toMove[UNKNOWN_FOLDER].append(f)

def processFolder(fname):

    toMove = {}
    if UNKNOWN_FOLDER is not None:
        if not os.path.exists(os.path.join(fname, UNKNOWN_FOLDER)):
            print("Creating folder %s" % fname)
            os.makedirs(os.path.join(fname, UNKNOWN_FOLDER))
        toMove[UNKNOWN_FOLDER] = []

    # First we create needed folders
    for r in tosort:
        toMove[r[1]] = []
        destination = os.path.join(fname, r[1])
        if not os.path.exists(destination):
            print("Creating folder %s" % fname)
            os.makedirs(destination)

    getToMove(toMove, fname)

    for k, v in toMove.items():
        for f in v:
            ffrom = os.path.join(fname, f)
            fto = os.path.join(fname, k, f)
            if DEBUG: print("Moving from %s to %s" % (ffrom, fto))
            os.rename(ffrom, fto)


                
                

def main():
    config = configparser.RawConfigParser()
    config.read(CONFIG_DIR)

    sourceFolder = config.get("BACKGROUNDS", "background-folder")
    processFolder(sourceFolder)

if __name__ == "__main__":
    main()
