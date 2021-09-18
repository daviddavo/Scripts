#!/usr/bin/python3
import sys
import os
import subprocess
import time
import configparser
import random
from PIL import Image
import mimetypes
from gi.repository import GLib

CONFIG_DIR = ["/home/davo/Scripts/Config.ini", "/home/davo.config/scripts/config.ini"]

config = configparser.RawConfigParser()
config.read(CONFIG_DIR)

DEBUG = True
MORELESS = .10
UNKNOWN_FOLDER = config.get("BACKGROUNDS", "unknown-subfolder")
ERROR_FOLDER = config.get("BACKGROUNDS", "error-subfolder")
TOO_LOW_FOLDER = config.get("BACKGROUNDS", "too-low-resolution-subfolder")

# UNKNOWN_FOLDER = None
tosort = [
    (16/9,  "16x9/", 1920, 1080),
    (9/16,  "Vertical/", 1080, 1920),
    (4/3,   "4x3/", 1400, 1050),
    (5/4,   "4x3/", 1280, 1024),
    (16/10, UNKNOWN_FOLDER+"/16x10", 1440, 900),
    (3/2,   UNKNOWN_FOLDER+"/3x2", 2160, 1440),
    (21/9,  UNKNOWN_FOLDER+"/21x9", 2560, 1080),
    (1,     UNKNOWN_FOLDER+"/1x1", 1000, 1000)
]

def whereToMove(fpath):
    try:
        mime = mimetypes.guess_type(fpath)[0]
        if mime is not None and mime.split("/")[0] == "image":
            im = Image.open(fpath)
            w, h = im.size
            
            sort = False
            for r in tosort:
                if (r[0]-MORELESS < w/h < r[0]+MORELESS):
                    if (TOO_LOW_FOLDER is not None and (w < r[2] or h < r[3])):
                        return TOO_LOW_FOLDER
                    else:
                        return r[1]
                    
                    sort = True
                    break

            if not sort:
                return UNKNOWN_FOLDER
    except:
        if (ERROR_FOLDER is not None):
            return ERROR_FOLDER

def getToMove(toMove, fname):
    files = os.listdir(fname)
    for f in files:
        af = os.path.join(fname, f)
        wtm = whereToMove(af)
        if wtm:
            toMove[wtm].append(af)
            print("Moving %s to %s" % (f, wtm))


def processFolder(fname):
    toMove = {}

    def auxCreateFolder(folder):
        if folder is not None:
            if not os.path.exists(os.path.join(fname, folder)):
                print("Creating folder %s" % folder)
                os.makedirs(os.path.join(fname, folder))

            toMove[folder] = []

    auxCreateFolder(UNKNOWN_FOLDER)
    auxCreateFolder(TOO_LOW_FOLDER)
    auxCreateFolder(ERROR_FOLDER)

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
    if (config.getboolean("BACKGROUNDS", "background-folder-auto")):
        sourceFolder = os.path.join(
            GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_PICTURES), 
            "Wallpapers/")
    else:
        sourceFolder = config.get("BACKGROUNDS", "background-folder")
    processFolder(sourceFolder)

if __name__ == "__main__":
    main()
