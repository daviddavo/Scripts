import sys, os, subprocess
import random
from shutil import move

source = "/home/davo/Imágenes/Wallpapers/"
print("Source:", source)
files = os.listdir(source)
os.chdir(source)

def main(ratio, destination):
    global source
    global files
    #print("R,d", ratio, destination)
    if not os.path.exists(destination):
        print("No existia la carpeta, la hemos tenido que crear")
        os.makedirs(destination)
    print("Destination", destination)
    for f in files:
        if f.endswith(".png") or f.endswith(".jpg"):
            out = subprocess.check_output('identify -format "%[fx:abs((' + str(ratio) + ')-(w/h))]:%M\n" ' + f + ' | sort -n -k1 -t:', shell=True).decode("utf-8").replace("\n", "").split(":")
            #print(out[0] + ":" + out[1])
            if float(out[0]) < 0.15:
                try:
                    move(source + out[1],destination + out[1])
                    print("Moviendo archivo", out[1])
                    files.remove(f)
                except:
                    print("No se ha podido copiar", out[1])
                    raise
        else:
            #print(f, "no termina en png, jpg")
            pass

main(16/9, "16x9/")
main(16/10, "16x9/")
main(9/16, "Vertical/")
main(4/3, "4x3/")
