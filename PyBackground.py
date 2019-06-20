import os, random, datetime
from Xlib import display
from Xlib.ext import randr
#ImgFolder = "/mnt/ssh/Imágenes/Wallpapers/"
ImgFolder = "/home/davo/Imágenes/Wallpapers/"
log  = "/home/davo/Scripts/BckLog.log"
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

#feh --bg-fill /Directorio/Imagen.png
#Nota, copia .fehbg a esta carpeta
def main():
    os.system("DISPLAY=:0")
    for i, screen in enumerate(screen_arr):
        # screen["file"] = screen["folder"] + random.choice(os.listdir(screen["folder"]))
        os.system("nitrogen --save --random --head={} --set-zoom-fill '{}'".format(i, screen["folder"]))


#print(file1, file2, file3)
#os.system("DISPLAY=:0 feh --bg-fill " + file1 + " --bg-fill " + file2 + " --bg-fill " + file3 + " --bg-fill " + file4)

if __name__ == "__main__":
    main()
