#!/usr/bin/env python3
import csv
import configparser
import time, datetime
import os
from math import floor

config      = configparser.RawConfigParser()
config.read("Config.ini")

CSV_FILE = config.get("PASCAL", "csvfile")
RESERVA  = config.getint("PASCAL", "reserve")
MARGEN   = config.getint("PASCAL", "margin")/100.0
WAIT     = config.getint("PASCAL", "sleep")
BELL     = config.getboolean("PASCAL", "bell")

# TIMESTAMP;QUANTITY\n
def readcsv():
    total = 0
    loses = 0
    wins  = 0

    with open(CSV_FILE, 'r') as csvfile:
        for row in csv.reader(csvfile, delimiter=";"):
            if (row[0] == ""):
                total = 0
                loses = 0
                wins = 0
            else:
                total += int(row[1])
                if (int(row[1]) < 0): loses += 1
                else: wins += 1

    return total, max(1,wins), max(1,loses)

def countdown(t):
    while t:
        print("Time remaining: {:02d}".format(t), end='\r')
        time.sleep(1)
        t -= 1

def main():
    total, wins, loses = readcsv()
    print("Total:", total, "pascalpuntos")
    print("Winrate:", round(float(wins)/(wins+loses)*100, 2), "%")
    print("W/L Ratio:", round(float(wins)/loses,3))
    print("Using:", total-RESERVA)
    # Esta formula no funciona :( 
    bet = floor((total-RESERVA)*(float(loses)/wins))
    print("Bet:", bet)

    response = input("You should bet %d, (w/l/q)? " % bet)
    quantity = bet
    if (response == "w"):
        pass
    elif (response == "l"):
        quantity = -quantity

    with open(CSV_FILE, 'a') as csvfile:
        csvfile.write("%s;%d\n" % (datetime.datetime.now().isoformat(), quantity))

    countdown(WAIT)
    if(BELL): os.system("play -nq -t alsa synth .5 sine 440")


if __name__ == '__main__':
    while (True):
        main()