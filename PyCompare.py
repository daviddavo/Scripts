#!/usr/bin/env python3
#fdupes
import subprocess, sys, time
tmp = subprocess.Popen(["fdupes", "/home/davo/Imágenes/Wallpapers/", "-rS"], stdout=subprocess.PIPE)
tmp = str(tmp.stdout.read().decode("utf-8"))
tmp2 = tmp.split("\n")
print(tmp)
print(int((len(tmp.split("\n"))-1)/4))

for i in tmp2:
    i.replace("\n", "")
    #print(i[-5:])
    if i == "" or (i[-5:] == "each:"):
        tmp2.remove(i)
#print(tmp2)

if "--mail" in sys.argv and len(tmp.split("\n")) > 2:
    import smtplib

    from email.message import EmailMessage
    from email.headerregistry import Address
    from email.utils import make_msgid

    sender = "david@ddavo.me"
    receiv = "david@ddavo.me"
    msg = EmailMessage()
    msg["From"] = Address("Davo-Arch10", "david@ddavo.me")
    msg["To"] = Address("Yo mismo", "david@ddavo.me")
    msg['Subject'] = "Wallpapers compared " + time.strftime("%d/%m/%Y %H:%M:%S")
    msg.preamble = "WTF"
    contenido = "Duplicados encontrados {}:\n\n".format(int((len(tmp.split("\n"))-1)/4)) + tmp
    msg.set_content(contenido)

    try:
        smtpObj = smtplib.SMTP('smtp.ddavo.me')
        smtpObj.send_message(msg)
        print("Successfully sent email")
        smtpObj.quit()
    except:
        print("Unable to to send email")
        raise
