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

if (config.getboolean("BACKGROUNDS", "background-folder-auto")):
    ImgFolder = os.path.join(
        GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_PICTURES), 
        "Wallpapers/")
else:
    ImgFolder = config.get("BACKGROUNDS", "background-folder")

DBFile = os.path.expanduser("~/.config/scripts/wallpapers.db")

def searchFractionInConfig(fr, thr):
    strstart = len('res-')
    strend = -len('-folder')
    for k,v in [(k,v) for k,v in config.items("BACKGROUNDS") if k.startswith('res-') and k.endswith('-folder')]:
        cfgfr = Fraction(k[strstart:strend].replace('x', '/'))
        if (1 - thr < cfgfr / fr < 1 + thr):
            return v


class DBConnection:
    def __init__(self, dbfile):
        self.con = sqlite3.connect(dbfile,
            detect_types=sqlite3.PARSE_DECLTYPES)

    def __del__(self):
        self.con.close()

    def create_db_if_possible(self):
        self.con.execute("""CREATE TABLE IF NOT EXISTS "wallpapers" (
            "date" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "head" INTEGER NOT NULL,
            "path" TEXT NOT NULL,
            "howchanged" TEXT DEFAULT 'auto',
            PRIMARY KEY("date","head"))""")

        self.con.execute("""CREATE VIEW IF NOT EXISTS wallpapers_leadchange AS
        SELECT `date`, `head`, `path`, LEAD(howchanged, 1, 'unknown') OVER (PARTITION BY `head` ORDER BY date ASC) `leadchange`
        FROM wallpapers
        ORDER BY date DESC""")

        self.con.execute("""CREATE VIEW IF NOT EXISTS wallpapers_current AS
        SELECT head, date, path current_path
        FROM wallpapers JOIN (
	    SELECT head, MAX(date) date
            FROM wallpapers
	    GROUP BY head
	) USING (head,date);
        """
        )

        self.con.commit()

    def insert_change(self, head:int, path:str, howchanged:str):
        self.con.execute(
            "INSERT INTO wallpapers (head, path, howchanged) VALUES (?,?,?)",
            (head, path, howchanged))
        self.con.commit()

    def get_last_change(self, head:int):
        c =self.con.cursor()
        c.execute("""
            SELECT date
            FROM wallpapers_current
            WHERE head=?
            """, (head,))
        d = c.fetchone()
        if d == None: return datetime.min

        return d[0]

    def get_current_bg(self, head:int):
        c = self.con.cursor()
        c.execute("""
            SELECT current_path
            FROM wallpapers_current
            WHERE head=?
            """, (head,))
        d = c.fetchone()
        
        if d == None: return None
        return d[0]

def get_background_folder(n, head):
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
    
    return fname

def get_background(n, head):
    bg_folder = get_background_folder(n, head)

    filtered = [x for x in os.listdir(bg_folder) if os.path.splitext(x)[1] in EXTENSIONS]
    # filter(lambda x : os.path.splitext(x)[1] in EXTENSIONS, os.listdir(fname))
    print(f"Found {len(filtered)} wallpapers")
    return os.path.join(bg_folder, random.choice(list(filtered)))

def thr_set_background(n, file):
    print(f"Setting wallpaper {file} on head {n}")
    os.system("/usr/bin/nitrogen --force-setter=xinerama --head={} --set-zoom-fill '{}'".format(n, file))

def getArgParser(head_count=1):
    parser = argparse.ArgumentParser(
        description="Welcome to my small script made for changing backgrounds in a multi-head setup")

    parser.add_argument("-d", "--daemon",
        help="Daemon commands (also available through DBUS)",
        choices=["start, stop", "restart"],
        default="start",
        nargs=1)

    parser.add_argument("howchanged",
        help="Background change mode", 
        choices=["manual","chron","saved"], 
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
    print(monitors)
    
    interval = config.getint("BACKGROUNDS", "rotate-interval")
    db = DBConnection(DBFile)
    db.create_db_if_possible()

    for i,x in [(i,x) for i,x in enumerate(monitors) if i in args.heads]:
        if (args.howchanged == "chron" and
            (db.get_last_change(i) + timedelta(minutes=interval)) > datetime.utcnow()):
                continue
        
        # fname = os.path.join(ImgFolder, config.get("BACKGROUNDS", "screen-"+str(i)+"-folder"))
        file = None
        if (args.howchanged == "saved"):
            file = db.get_current_bg(i)
        
        if (file == None):
            file = get_background(i, x)
        t = threading.Thread(target=thr_set_background, args=(i,file))
        t.start()
        db.insert_change(i, file, args.howchanged)

    with open(CONFIG_DIR[-1], 'w') as f:
        config.write(f)
        

if __name__ == "__main__":
    main()
