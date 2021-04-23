#!/usr/bin/python3

import os
import time
import threading

import urllib.request
import shutil

import pyperclip
from concurrent.futures import *

import gi
gi.require_version('Notify', '0.7')
from gi.repository import Notify
from gi.repository import GdkPixbuf

WP_FOLDER=os.path.expanduser("~/Pictures/Wallpapers/")
MAX_SIZE=500

def is_url_image(url):
    return os.path.splitext(url)[1][1:] in ["jpeg","png","jpg","gif"]

def print_to_stdout(clipboard_content):
    print ("Found url: %s" % str(clipboard_content))

def download_file(clipboard_content):
    destination = os.path.join(WP_FOLDER, os.path.basename(clipboard_content))
    print(f"Downloading file {clipboard_content} to {destination}")
    with urllib.request.urlopen(clipboard_content) as response, open (destination, "wb") as fout:
        shutil.copyfileobj(response, fout)

    n = Notify.Notification.new(
        summary="Download finished",
        body=f"Download finished for {os.path.basename(clipboard_content)}"
    )
    n.set_urgency(Notify.Urgency.NORMAL)
    p = GdkPixbuf.Pixbuf.new_from_file(destination)
    h = p.get_height()
    w = p.get_width()
    if (w > h): # horizontal
        sp = p.new_subpixbuf(w/2-h/2, 0, h, h)
    else: # vertical
        sp = p.new_subpixbuf(0, h/2-w/2, w, w)

    sp = sp.scale_simple(MAX_SIZE, MAX_SIZE, GdkPixbuf.InterpType.NEAREST)
    n.set_image_from_pixbuf(sp)
    try:
        n.show()
    except Exception as e:
        print("Error showing notification")
        print(e)
        Notify.uninit()
        Notify.init("Clipboard Watcher")
        n = Notify.Notification.new(summary="Error showing notification")
        n.set_urgency(Notify.Urgency.CRITICAL)
        n.show()
    print("Finished!")

class ClipboardWatcher(threading.Thread):
    def __init__(self, predicate, callback, pause=5., max_workers=2):
        super(ClipboardWatcher, self).__init__()
        self._predicate = predicate
        self._callback = callback
        self._pause = pause
        self._stopping = False
        self.executor = ThreadPoolExecutor(max_workers)

    def run(self):       
        recent_value = ""
        while not self._stopping:
            # tmp_value = pyperclip.waitForNewPaste()
            tmp_value = pyperclip.paste()
            if tmp_value != recent_value:
                recent_value = tmp_value
                if self._predicate(recent_value):
                    print(f"Predicate accepted: {recent_value}")
                    self.executor.submit(self._callback, recent_value)
                else:
                    print(f"Predicate failed: {recent_value}")
            time.sleep(self._pause)

    def stop(self):
        self._stopping = True

def main():
    pyperclip.set_clipboard("xsel")
    Notify.init("Clipboard Watcher")

    watcher = ClipboardWatcher(is_url_image, 
                               download_file,
                               .1)
    watcher.start()
    while True:
        try:
            print("Waiting for changed clipboard...")
            time.sleep(60)
        except KeyboardInterrupt:
            watcher.stop()
            break


if __name__ == "__main__":
    main()
