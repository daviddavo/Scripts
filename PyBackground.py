import os, sys
from datetime import datetime, timedelta
import threading
import configparser
import sqlite3
import random
from gi.repository import GLib

from Xlib import X,display
from Xlib.ext import randr

MORELESS = .10

CONFIG_DIR = "/home/davo/Scripts/Config.ini"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

config = configparser.RawConfigParser()
config.read(CONFIG_DIR)

ImgFolder = config.get("BACKGROUNDS", "background-folder")
if (config.getboolean("BACKGROUNDS", "background-folder-auto")):
    ImgFolder = os.path.join(GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_PICTURES), "Wallpapers/")

def thr_set_background(head, fname, howchanged):
    con = sqlite3.connect(os.path.join(os.path.dirname(__file__), "wallpapers.db"))
    file = os.path.join(fname, random.choice(os.listdir(fname)))
    os.system("/usr/bin/nitrogen --head={} --set-zoom-fill '{}'".format(head, file))
    con.execute("INSERT INTO wallpapers (head, path, howchanged) VALUES (?,?,?)", (head, file, howchanged))
    con.commit()
    con.close()

#feh --bg-fill /Directorio/Imagen.png
#Nota, copia .fehbg a esta carpeta
def main():
    howchanged = sys.argv[1] if len(sys.argv)>1 else "unknown"
    
    if (howchanged == "rotate" and 
        config.has_option("BACKGROUNDS", "rotate-next") and 
        datetime.strptime(config.get("BACKGROUNDS", "rotate-next"), DATE_FORMAT) > datetime.now()): return

    interval = config.getint("BACKGROUNDS", "rotate-interval")
    config.set("BACKGROUNDS", "rotate-next", (datetime.now()+timedelta(minutes=interval)).strftime(DATE_FORMAT))
    with open(CONFIG_DIR, 'w') as f:
        config.write(f)

    for i in range(config.getint("BACKGROUNDS", "number-screens")):
        fname = os.path.join(ImgFolder, config.get("BACKGROUNDS", "screen-"+str(i)+"-folder"))
        t = threading.Thread(target=thr_set_background, args=(i, fname, howchanged))
        t.start()
        

if __name__ == "__main__":
    main()
