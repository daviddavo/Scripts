import sys, os, subprocess,time, configparser
import random
import smtplib
from shutil import move
from email.message import EmailMessage
from email.headerregistry import Address
from email.utils import make_msgid

config      = configparser.RawConfigParser()
configdir   = "Config.ini"
config.read(configdir)

#Será usado próximamente
tosort = {16/9:"16x9/", 16/10:"16x9", 9/16:"Vertical/", 4/3:"4x3/"}

source = "/home/davo/Imágenes/Wallpapers/"
print("Source:", source)
files = os.listdir(source)
os.chdir(source)
wallsorted = []

def main(ratio, destination):
    global files
    global source
    
    files = os.listdir(source)
    #print("R,d", ratio, destination)
    if not os.path.exists(destination):
        print("No existia la carpeta, la hemos tenido que crear")
        os.makedirs(destination)
    print("Destination", destination)
    for f in files:
        if f.endswith(".png") or f.endswith(".jpg"):
            try:
                out = subprocess.check_output('identify -format "%[fx:abs((' + str(ratio) + ')-(w/h))]:%M\n" ' + f + ' | sort -n -k1 -t:', shell=True).decode("utf-8").replace("\n", "").split(":")
                #print(out[0] + ":" + out[1])
                if float(out[0]) < 0.15:
                    try:
                        move(source + out[1],destination + out[1])
                        print("Moviendo archivo", out[1])
                        wallsorted.append("Movido " + source + out[1] + " a " + destination + out[1])
                        files.remove(f)
                    except:
                        print("No se ha podido copiar", out[1])
                        wallsorted.append("No se ha podido copiar " + out[1])
                        raise
            except:
                print("Error con {}".format(f))
        else:
            #print(f, "no termina en png, jpg")
            pass

main(16/9, "16x9/")
main(16/10, "16x9/")
main(9/16, "Vertical/")
main(4/3, "4x3/")

if "--mail" in sys.argv and len(wallsorted) > 0:
    sender = "david@ddavo.me"
    receiv = "david@ddavo.me"
    msg = EmailMessage()
    msg["From"] = Address(config.get("MAIL", "from-name"), "arch@ddavo.me")
    msg["To"] = Address(config.get("MAIL", "to-name"), config.get("MAIL", "to-addr"))
    msg['Subject'] = "Wallpapers sorted " + time.strftime("%d/%m/%Y %H:%M:%S")
    msg.preamble = "WTF"
    contenido = "\n".join(wallsorted)
    msg.set_content(contenido)

    #message = msg.as_string()

    try:
        smtpObj = smtplib.SMTP('smtp.ddavo.me')
        smtpObj.send_message(msg)
        print("Successfully sent email")
        smtpObj.quit()
    except:
        print("Unable to to send email")
        raise
