#!/usr/bin/python3
import sys, os, subprocess,time, configparser
import random
from PIL import Image
import mimetypes

CONFIG_DIR   = "Config.ini"
DEBUG = True
MORELESS = .10
UNKNOWN_FOLDER = "UnknownResolution"
ERROR_FOLDER = "Error"
TOO_LOW_FOLDER = "TooLowResolution"
# UNKNOWN_FOLDER = None
tosort = [(16/9,"16x9/", 1920, 1080), (9/16,"Vertical/", 1080, 1920), (4/3,"4x3/", 1400, 1050)]

def getToMove(toMove, fname):
    files = os.listdir(fname)
    for f in files:
        af = os.path.join(fname, f)

        try:
            mime = mimetypes.guess_type(af)[0]
            if mime is not None and mime.split("/")[0] == "image":
                im = Image.open(af)
                w, h = im.size
                
                sort = False
                for r in tosort:
                    if (r[0]-MORELESS < w/h < r[0]+MORELESS):
                        if (TOO_LOW_FOLDER is not None and (w < r[2] or h < r[3])):
                            toMove[TOO_LOW_FOLDER].append(f)
                        else:
                            toMove[r[1]].append(f)
                        
                        print("Moving %s to %s" % (f, r[1]))
                        sort = True
                        break

                if UNKNOWN_FOLDER is not None and not sort:
                    toMove[UNKNOWN_FOLDER].append(f)
        except:
            if (ERROR_FOLDER is not None): toMove[ERROR_FOLDER].append(f)

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
    config = configparser.RawConfigParser()
    config.read(CONFIG_DIR)

    sourceFolder = config.get("BACKGROUNDS", "background-folder")
    processFolder(sourceFolder)

if __name__ == "__main__":
    main()
