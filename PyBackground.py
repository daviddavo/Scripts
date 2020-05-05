#!/usr/bin/python3
import os, sys
from datetime import datetime, timedelta
import threading
import argparse
import configparser
import sqlite3
import random
import screeninfo
from fractions import Fraction
from gi.repository import GLib

MORELESS = .10

CONFIG_DIR = ["/home/davo/Scripts/Config.ini", "/home/davo/.config/scripts/config.ini"]
EXTENSIONS = [".png", ".jpeg", ".jpg"]
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

config = configparser.RawConfigParser()
config.read(CONFIG_DIR)

ImgFolder = config.get("BACKGROUNDS", "background-folder")
if (config.getboolean("BACKGROUNDS", "background-folder-auto")):
    ImgFolder = os.path.join(GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_PICTURES), "Wallpapers/")

def searchFractionInConfig(fr, thr):
    strstart = len('res-')
    strend = -len('-folder')
    for k,v in [(k,v) for k,v in config.items("BACKGROUNDS") if k.startswith('res-') and k.endswith('-folder')]:
        cfgfr = Fraction(k[strstart:strend].replace('x', '/'))
        if (1 - thr < cfgfr / fr < 1 + thr):
            return v

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

def thr_set_background(n, head, howchanged):
    fr = Fraction(head.width, head.height)
    res = f'{fr.numerator}x{fr.denominator}'
    if config.has_option("BACKGROUNDS", f'res-{res}-folder'):
        fname = os.path.join(ImgFolder, config.get("BACKGROUNDS", f'res-{res}-folder'))
        print("Res %s found, using folder %s" % (res, fname))
    elif config.has_option("BACKGROUNDS", f'screen-{n}-folder'):
        fname = os.path.join(ImgFolder, config.get("BACKGROUNDS", f'screen-{n}-folder'))
        print("Res %s not found, using folder %s" % (res, fname))
    else:
        fname = os.path.join(ImgFolder, searchFractionInConfig(fr, .5))
        print(f"Res {res} not found neither head {n} in options, using {fname}")

    con = sqlite3.connect(os.path.join(os.path.dirname(__file__), "wallpapers.db"))
    filtered = [x for x in os.listdir(fname) if os.path.splitext(x)[1] in EXTENSIONS]
    # filter(lambda x : os.path.splitext(x)[1] in EXTENSIONS, os.listdir(fname))
    print(f"Found {len(filtered)} wallpapers")
    file = os.path.join(fname, random.choice(list(filtered)))
    os.system("/usr/bin/nitrogen --force-setter=xinerama --head={} --set-zoom-fill '{}'".format(n, file))
    con.execute("INSERT INTO wallpapers (head, path, howchanged) VALUES (?,?,?)", (n, file, howchanged))
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
    monitors = screeninfo.get_monitors(screeninfo.Enumerator.Xinerama)
    parser = getArgParser(len(monitors))
    args = parser.parse_args()
    print(args.heads)
    print(monitors)
    
    interval = config.getint("BACKGROUNDS", "rotate-interval")
    create_db_if_possible()

    for i,x in [(i,x) for i,x in enumerate(monitors) if i in args.heads]:
        if (args.howchanged == "chron" and 
            config.has_option("BACKGROUNDS", "rotate-next-"+str(i)) and
            datetime.strptime(config.get("BACKGROUNDS", "rotate-next-"+str(i)), DATE_FORMAT) > datetime.now()): continue
        
        # fname = os.path.join(ImgFolder, config.get("BACKGROUNDS", "screen-"+str(i)+"-folder"))
        t = threading.Thread(target=thr_set_background, args=(i, x, args.howchanged))
        t.start()
        config.set("BACKGROUNDS", "rotate-next-"+str(i), (datetime.now()+timedelta(minutes=interval)).strftime(DATE_FORMAT))

    with open(CONFIG_DIR[-1], 'w') as f:
        config.write(f)
        

if __name__ == "__main__":
    main()
