import os
import threading
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

def thr_set_background(head, fname):
    os.system("nitrogen --save --random --head={} --set-zoom-fill '{}'".format(head, fname))

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

    for i, screen in enumerate(screen_arr):
        t = threading.Thread(target=thr_set_background, args=(i, screen["folder"]))
        t.start()

if __name__ == "__main__":
    main()
