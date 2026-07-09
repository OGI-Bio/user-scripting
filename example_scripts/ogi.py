# Provides functions to connect to bioreactor and send commands.

import sys
import time
import serial as s
import serial.tools.list_ports as stl


def sendcmd(cmd):
    global ser, ogi_flags

    if "verbose" in ogi_flags:
        print("sending the command: " + cmd)

    try:
        while ser.in_waiting:  # there is data in the buffer - print until clear
            print(ser.read(64).decode("utf-8"))

        # ready to send - appending a '\r' will force the OGI3 to respond faster instead
        # of waiting for a 100 ms timeout
        ser.write((cmd + "\r").encode("utf-8"))

        # wait for response
        while True:
            if ser.in_waiting:
                # read back response
                mystr = ser.read_until(b"\r").decode("utf-8")

                # check that return message starts with our command
                if not mystr.startswith(cmd):
                    print(f"error, return message {mystr} does not match command {cmd}")
                    if "exit_on_fail" in ogi_flags:
                        sys.exit()
                    return

                # check for error
                if mystr.find("ERR") != -1:
                    print(mystr.rstrip().partition("ERR"))
                    if "exit_on_fail" in ogi_flags:
                        sys.exit()
                    return

                # success - return payload
                return mystr.rstrip().partition(cmd)[2]

    except:
        print("error, serial connection lost")
        if "exit_on_fail" in ogi_flags:
            sys.exit()
        if "automatic_reconnect" in ogi_flags:
            print("attempting to reconnect...")
            connect_go()
        else:
            sys.exit()
        return


## Serial connection
def connect_go():
    global ser

    ser = s.Serial()
    try:
        ser.port = next(
            stl.grep("COM*")
        ).name  # Try to automatically find the port - replace with eg 'COM15' if it doesn't work
        ser.baudrate = 115200
        ser.timeout = 1

        # Disable DTR to prevent Arduino auto-reset
        ser.dtr = False
        ser.rts = False

        # Wait a moment for settings to take effect
        ser.open()
        time.sleep(1.0)

    except:
        print(
            "error, couldn't open port - check connection and that port isn't being used in another process"
        )
        return False

    if ser.isOpen():
        print("Serial connection established\n")
        return True
    else:
        return False


## Serial connection
def connect_OGI3(automatic_reconnect=True, exit_on_fail=False, verbose=False):
    global ser, ogi_flags

    ogi_flags = set()

    if automatic_reconnect:
        ogi_flags.add("automatic_reconnect")
    if exit_on_fail:
        ogi_flags.add("exit_on_fail")
    if verbose:
        ogi_flags.add('verbose')

    if not connect_go():
        sys.exit()
