import os, sys
import threading
import sqlite3
import random
from gi.repository import GLib

from Xlib import X,display
from Xlib.ext import randr

MORELESS = .10

ImgFolder = os.path.join(GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_PICTURES), "Wallpapers/")
# ImgFolder = "$XDG_PICTURES_DIR/Wallpapers/"
resolutions = [(16/9,"16x9/"), (9/16,"Vertical/"), (4/3,"4x3/")]

# TODO: Load this from config
screen_arr = [
    {
        "folder":ImgFolder+"16x9/",
    },
    {
        "folder":ImgFolder+"16x9/",
    },
    {
        "folder":ImgFolder+"Vertical/",
    },
    {
        "folder":ImgFolder+"4x3/",
    }
]

def thr_set_background(head, fname, howchanged):
    con = sqlite3.connect(os.path.join(os.path.dirname(__file__), "wallpapers.db"))
    file = os.path.join(fname, random.choice(os.listdir(fname)))
    os.system("/usr/bin/nitrogen --save --head={} --set-zoom-fill '{}'".format(head, file))
    con.execute("INSERT INTO wallpapers (head, path, howchanged) VALUES (?,?,?)", (head, file, howchanged))
    con.commit()
    con.close()

#feh --bg-fill /Directorio/Imagen.png
#Nota, copia .fehbg a esta carpeta
def main():
    '''
    d = display.Display() # default display
    s = d.screen()
    print(d.screen_count())

    for output in randr.get_screen_resources(s.root).outputs:
        d.get_output_info(output)
        print(str(randr.list_output_properties(s.root, output)))

    for m in get_monitors():
        w, h = m.width, m.height
        print(m.name)
        # if (r[0]-MORELESS < w/h < r[0]+MORELESS):
    '''     

    howchanged = sys.argv[1] if len(sys.argv)>1 else "unknown"

    for i, screen in enumerate(screen_arr):
        t = threading.Thread(target=thr_set_background, args=(i, screen["folder"], howchanged))
        t.start()

if __name__ == "__main__":
    main()
