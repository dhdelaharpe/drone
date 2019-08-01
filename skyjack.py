#!/usr/bin/python

#1 aug 2019
#skyjack translation by Daniel de la Harpe
#adapted from Samy Kamkar skyjack.pl available at github.com/samyk/skyjack

#Parrot drone mac addresses from http://standards-oui.ieee.org/oui/oui.txt
drone_macs = ["90:03:B7","00:12:1C","90:3A:E6", "A0:14:3D", "00:12:1C", "00:26:7E"]


#declare wireless interface 
interface = "wlan0"

#relevant paths to needed applications
pathControlJs = "control/drone_pwn.js"
pathDhclient = "dhclient"
pathIwconfig = "iwconfig"
pathIfconfig = "ifconfig"
pathAirmon = "armon-ng"
pathAireplay = "aireplay-ng"
pathAircrack = "aircrack-ng"
pathAirodump = "airodump-ng"
pathNodejs = "nodejs"

#import subprocess to make calls to terminal
import os, subprocess, shlex, time
#DNull to redirect away from terminal, temp file to store output
DNull=open(os.devnull,'w')
tmpfilePath = "temp/droneAttack.csv"

import re
 

def scan(writeTo,interface):
'''function to scan all wireless networks and produce a table in a txt file for further inspection'''
    table = ''
    stdout = []
    runtime=10
    table_start = re.compile('\sCH')
    startTime = time.time()

    subprocess.call([pathIfconfig, interface, "down"])
    airodump = subprocess.Popen(['airodump-ng', interface], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, bufsize=1)

    while time.time() < startTime + runtime:
        line = airodump.stdout.readline()
        if table_start.match(line):
            table = ''.join(stdout)
            stdout = []
        stdout.append(line)
    airodump.terminate()
    f=open(writeTo,'w+')
    f.write(table)
    f.close()



def main():
    scan(tmpfilePath,interface)
    #restarting normal use of interface
    subprocess.call([pathIfconfig, interface, "up"])
main()
