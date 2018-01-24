#!/usr/bin/env python
import socket
import time
import signal
import serial
import subprocess

# Load environment variables
execfile("/KWH/datalogger/conf/pyvars.py")

# Global variables
RESET_LIMIT = 1

def signal_handler(signal, frame):
    if DEBUG == "1": log('SIGINT received...Closing SIM Server\n')
    sim.close()
    s.close()
    cs.close()
    exit(0)
signal.signal(signal.SIGINT, signal_handler)

# Log function
def log(logText):
    with open("/KWH/datalogger/transceive/simServer.log", "a") as log:
	log.write(logText)

# Reconfigure communications protocol with SIM Chip
def configure():
    execfile("/KWH/datalogger/conf/pyvars.py")
    if DEBUG == "1": log("Configuration variables reloaded\n")    
    subprocess.Popen("/KWH/datalogger/transceive/ttyAMA0_setup.sh")
    if DEBUG == "1": log("Executed ttyAMA0_setup.sh\n")    

# Reset the SIM card
def reset():
    execfile("/KWH/datalogger/transceive/reset_sim.py")
    if DEBUG == "1": log("Sleeping 5 for SIM reboot and reconfigure!\n")
    time.sleep(4)
    configure()
    time.sleep(1)

# Logs in simServer.log if the env variable DEBUG is 1
if DEBUG == "1": log("Starting SIM Server\n")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = ''
port = 9999
port_chosen = False

if DEBUG == "1": log("Starting port selection\n") 

# Find an open port for the service
while not port_chosen:
    try:
	s.bind((host, port))
        port_chosen = True
    except:
	if DEBUG == "1": log("Port "+str(port)+" in use\n")
	port = port + 1

# Update the env variables with the chosen active SIM_PORT
with open("/KWH/datalogger/conf/SIM_PORT", "w") as SIM_PORT:
    SIM_PORT.write(str(port))

if DEBUG == "1": log("SIM_PORT: "+str(port)+"\nListening...\n")

reset()

s.listen(1)
sim = serial.Serial('/dev/ttyAMA0', 115200, timeout=5)
sim.flushInput()
sim.flushOutput()

# Daemon listen on SIM_PORT for SIM commands
while True:
    # Waits for a command
    cs,addr = s.accept()

    configure()

    cmd = cs.recv(1024)
    if DEBUG == "2": log("Received: "+cmd+"\n")

    # Send command to SIM
    try:
	sim.write(cmd)

        if DEBUG == "1": log("Wrote to sim: "+cmd+"\n")

        if cmd == "AT+CGATT=1\n" \
            or cmd == "AT+CIICR\n":
            time.sleep(2)

        if cmd == "AT+CIPSTART=\"TCP\",\""+DOMAIN+"\",\""+PORT+"\"\n":
            time.sleep(3)

        # Get SIM response
        fromSIM = sim.inWaiting()

        # If no response, restart SIM, reset config, and retry
        count = 0
        while fromSIM < 1 and count < RESET_LIMIT:
#           time.sleep(1)
#           fromSIM = sim.inWaiting()
#           if fromSIM > 0:
#	        break
            if DEBUG == "1": log(str(fromSIM)+" bytes from SIM. Resetting SIM!\n")
            reset()
            count += 1
            try:
                sim.write(cmd)
	    except:
	        log("EXCEPTION: Write Failed")
            if DEBUG == "1": log("Wrote to sim: "+cmd+"\n")
            time.sleep(0.5)
            fromSIM = sim.inWaiting()

        if DEBUG == "1": log("Bytes to read: "+str(fromSIM)+"\n")
        resp = sim.read(fromSIM)
        if DEBUG == "1": log("Sim response: "+resp+"\n")
        if resp == "":
            resp = "No response"
        cs.send(resp)
        if DEBUG == "1": log("Response sent to: "+str(addr)+"\n")

#        fromSIM = sim.inWaiting()
#        if fromSIM > 0:
#            if DEBUG == "1": log("Bytes to read: "+str(fromSIM)+"\n")
#            resp = sim.read(fromSIM)
#            if DEBUG == "1": log("Sim response: "+resp+"\n")
#            cs.send(resp)
#            if DEBUG == "2": log("Response sent to: "+str(addr)+"\n")

#        sim.flushInput()
#        sim.flushOutput()
    
#       time.sleep(.5)
        cs.close()
    except:
        log("EXCEPTION: Write Failed")
        reset()

    cs.close()
    log("Client connection closed")