import os, sys
from datetime import datetime, timedelta
import threading
import argparse
import configparser
import sqlite3
import random
from gi.repository import GLib

from Xlib import X,display
from Xlib.ext import randr

MORELESS = .10

CONFIG_DIR = ["/home/davo/Scripts/Config.ini", "/home/davo/.config/scripts/config.ini"]
EXTENSIONS = [".png", ".jpeg", ".jpg"]
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

config = configparser.RawConfigParser()
config.read(CONFIG_DIR)

ImgFolder = config.get("BACKGROUNDS", "background-folder")
if (config.getboolean("BACKGROUNDS", "background-folder-auto")):
    ImgFolder = os.path.join(GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_PICTURES), "Wallpapers/")

def create_db_if_possible():
    con = sqlite3.connect(os.path.join(os.path.dirname(__file__), "wallpapers.db"))
    
    con.execute("""CREATE TABLE IF NOT EXISTS "wallpapers" (
	"date" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"head" INTEGER NOT NULL,
	"path" TEXT NOT NULL,
	"howchanged" TEXT DEFAULT 'auto',
	PRIMARY KEY("date","head"))""")

    con.execute("""CREATE VIEW IF NOT EXISTS wallpapers_leadchange AS
    SELECT `date`, `head`, `path`, LEAD(howchanged, 1, 'unknown') OVER (PARTITION BY `head` ORDER BY date ASC) `leadchange`
    FROM wallpapers
    ORDER BY date DESC""")

    con.commit()
    con.close()

def thr_set_background(head, fname, howchanged):
    con = sqlite3.connect(os.path.join(os.path.dirname(__file__), "wallpapers.db"))
    filtered = filter(lambda x : os.path.splitext(x)[1] in EXTENSIONS, os.listdir(fname))
    file = os.path.join(fname, random.choice(list(filtered)))
    os.system("/usr/bin/nitrogen --head={} --set-zoom-fill '{}'".format(head, file))
    con.execute("INSERT INTO wallpapers (head, path, howchanged) VALUES (?,?,?)", (head, file, howchanged))
    con.commit()
    con.close()

def getArgParser(head_count=1):
    parser = argparse.ArgumentParser(
        description="Welcome to my small script made for changing backgrounds in a multi-head setup")

    parser.add_argument("howchanged",
        help="Background change mode", 
        choices=["manual","chron"], 
        default="manual", 
        nargs="?")

    parser.add_argument("-H", "--head", 
        help="Head(s) on which to change the wallpaper", 
        choices=range(0,head_count), 
        type=int,
        nargs="+",
        dest="heads",
        default=list(range(0,head_count)))

    return parser

#feh --bg-fill /Directorio/Imagen.png
#Nota, copia .fehbg a esta carpeta
def main():
    parser = getArgParser(config.getint("BACKGROUNDS", "number-screens"))
    args = parser.parse_args()
    print(args.heads)
    
    interval = config.getint("BACKGROUNDS", "rotate-interval")
    create_db_if_possible()

    for i in args.heads:
        if (args.howchanged == "chron" and 
            config.has_option("BACKGROUNDS", "rotate-next-"+str(i)) and
            datetime.strptime(config.get("BACKGROUNDS", "rotate-next-"+str(i)), DATE_FORMAT) > datetime.now()): continue
        
        fname = os.path.join(ImgFolder, config.get("BACKGROUNDS", "screen-"+str(i)+"-folder"))
        t = threading.Thread(target=thr_set_background, args=(i, fname, args.howchanged))
        t.start()
        config.set("BACKGROUNDS", "rotate-next-"+str(i), (datetime.now()+timedelta(minutes=interval)).strftime(DATE_FORMAT))

    if not os.path.exists(os.path.dirname(CONFIG_DIR[-1])): os.makedirs(os.path.dirname(CONFIG_DIR[-1]))
    with open(CONFIG_DIR[-1], 'w+') as f:
        config.write(f)
        

if __name__ == "__main__":
    main()
