import dbus
import time

radio_URI = "http://radio5.rtveradio.cires21.com/radio5.mp3"
ttl = 60*5

tmpvol = 100 #El volumen al que quieres que se ponga la radio

with open("tmp.log", "w") as f:
    f.write("LALALALALA")

#Configuramos unas cuantas variables
session_bus = dbus.SessionBus()
player = session_bus.get_object('org.mpris.clementine', '/Player')
tracklist = session_bus.get_object("org.mpris.clementine", "/TrackList")
ifacepl = dbus.Interface(player, dbus_interface='org.freedesktop.MediaPlayer')
ifacetl = dbus.Interface(tracklist, dbus_interface="org.freedesktop.MediaPlayer")

#Guardamos la info de la canción, para dejarlo tal y como estaba
current = ifacetl.GetCurrentTrack()
vol  = ifacepl.VolumeGet()
print("Vol", vol)
print("Current", current)
meta = ifacetl.GetMetadata(current)
#print(meta)
#print(meta["location"])

#Reproducimos la radio
with open("tmp.log", "w") as f:
    f.write("LOLOLOL")
if current >= 0:
    ifacetl.AddTrack(radio_URI, 1)
    ifacepl.VolumeSet(tmpvol)
    time.sleep(10)
    torm = ifacetl.GetCurrentTrack()
    print("Torm", torm)

    for i in range(ttl-10):
        time.sleep(1)
        print("Time left: ", '{:>3}'.format((ttl-10)-i), end="\r")

    ifacepl.VolumeSet(vol)
    ifacetl.PlayTrack(current)
    ifacetl.DelTrack(torm)
