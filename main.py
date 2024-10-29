# mesh-beacon.py 
# By Andy Z - K1RA

# Interface with a Meshtastic node's API via WiFi IP and periodically send a message
#   otherwise print received packets, or text payloads from other nodes

# Note the Android / IOS Meshtastic app can NOT be connected or used with the node via
# its IP address at the same time this app is running and connecting to it

# See and use requirements.txt to ensure all supporting libraries are being loaded

import random
import re
import time
from datetime import datetime
import meshtastic.tcp_interface
from pubsub import pub


VERSION = "1.0"

# user's private IP of node on your LAN
nodeIP = '192.168.2.177'

# user's name of chosing
BOTNAME = "K1RA"

# user defined timer1 beacon message and frequency (seconds)
msg1 = "Visit https://groups.io/g/NoVa-Meshtastic"
TIMER1 = 1800

# user defined timer2 beacon message and frequency (seconds)
msg2 = "Fauquier Mesh is on Long Fast Slot 9"
TIMER2 = 3600


# Called when an IP packet arrives from the node
def onReceive(packet, interface):
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d_%H%M")

    # if its a text Payload msg pull text and print
    if re.search(r"payload: \"(.+)\"", str(packet)):
        regex = re.search(r"payload: \"(.+)\"", str(packet))
        msg = regex.group(1)
        print(f"{current_time} Received: {str(packet['from'])} {msg}")
    else:
        # print raw packet msg received
        print(f"{current_time} Received: {str(packet['from'])} " + str(packet))


    return


# Called when we (re)connect to the radio node IP
def onConnection(interface, topic=pub.AUTO_TOPIC):
    # defaults to broadcast, specify a destination ID if you wish
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d_%H%M")

    print(f"{current_time} Connected")
    return


# connect to local node
interface = meshtastic.tcp_interface.TCPInterface(hostname=nodeIP)

# set up some trigger events
pub.subscribe(onReceive, "meshtastic.receive")
pub.subscribe(onConnection, "meshtastic.connection.established")

try:
    # reset timers
    first = 0
    t1 = TIMER1 - 10
    t2 = TIMER2 - 10

    while True:
        # wait one second
        time.sleep(1)

        # get date/time and format
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d_%H%M")

        # count one second per timer
        first += 1
        t1 += 1
        t2 += 1
        
#       5 seconds after app starts send BOT active msg to Mesh
        if first == 5:
            print(f"\n{current_time} {BOTNAME} Beacon BOT v{VERSION} restarted\n")
            interface.sendText("{BOTNAME} Beacon BOT v" + VERSION + " restarted\n")

#       Every timer1 seconds send this msg to Mesh
        if t1 >= TIMER1:
            print(f"\n{current_time} {msg1}\n")
            interface.sendText("{msg1}\n")

            # reset timer1
            t1 = 0

#       Every timer2 seconds send this msg to Mesh
        if t2 >= TIMER2:
            print(f"\n{current_time} {msg2}\n")
            interface.sendText("{msg2}\n")

            # reset timer
            t2 = 0


# trap Ctrl-C to end app
except KeyboardInterrupt:
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d_%H%M")


    print(f"{current_time} {BOTNAME} Beacon BOT v{VERSION} Halting\n")

    interface.sendText("{BOTNAME} Beacon BOT v" + VERSION + "Halting\n")

    interface.close()
