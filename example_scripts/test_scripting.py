# this assumes a unit with a LC module is connected to the computer via a USB cable

import time
import ogi

ogi.connect_OGI3(verbose=False,exit_on_fail=True)
ogi.sendcmd('echo')

print("===============================================================")
ret=ogi.sendcmd('list OD cals')
print("List of OD calibrations\n",ret,"\n")
print("===============================================================\n")

# these are all supposed to run fine:
print("running some low-level commands:")
ogi.ogi_flags.add('verbose')


# motors tests
if False:
    print(ogi.sendcmd("motors 1000"))
    print(ogi.sendcmd("motors 0"))
    print(ogi.sendcmd("motor A 4000"))
    print(ogi.sendcmd("motor A 0"))



# temp and OD tests
if False:
    print(ogi.sendcmd("LEDs 1"))   # all LEDs on
    ret=ogi.sendcmd("get rawOD A")
    print(ret)
    try:
        odraw=int(ret)        
    except:
        print("error converting rawOD to integer")
        exit()

    ret=ogi.sendcmd('get temperature A')
    print(ret)
    try:
        ret=ret.strip().split(',')
        temp=float(ret[1])
        print("rawOD:", odraw, "Temp:", temp)
    except:
        print("error parsing temperature")

    print(ogi.sendcmd("measure OD A"))

    print(ogi.sendcmd("set temp control target A 30"))
    print(ogi.sendcmd("set temp control A 1"))
    time.sleep(1)
    print(ogi.sendcmd("set temp control A 0"))
    print(ogi.sendcmd("LEDs 0"))   # all LEDs on


# LC tests
if False:
    print(ogi.sendcmd("pumps 1 1.0"))
    time.sleep(1)
    for fl in ['A','B','C','D']:
        print(ogi.sendcmd("inpump "+fl+" 1 1.0"))
        time.sleep(1)
        print(ogi.sendcmd("outpump "+fl+" 1 1.0"))
        time.sleep(1)

# higher-level command testing
if True:
    print(ogi.sendcmd("set turbidostat controls 1")) # should this not operate only if turbidostat mode is on?
    print(ogi.sendcmd("set turbidostat target A 2"))  # this does range checking

    print(ogi.sendcmd("set chemostat flowrate A 1.5"))  # this does range checking"))  

    print(ogi.sendcmd("set pH controls -1")) # enable/disable pH control
    print(ogi.sendcmd("set pH control A -1")) # enable/disable pH control
    print(ogi.sendcmd("set pH control targets 7.0"))  # target pH
    print(ogi.sendcmd("set pH control type D acid")) # pH control type
    print(ogi.sendcmd("set pH control durations 5.0")) # pH control pump duration
    print(ogi.sendcmd("set pH2x controls 10")) # enable/disable pH2x control
    print(ogi.sendcmd("set pH2x control targets 7.0")) # target pH
    print(ogi.sendcmd("set pH2x control durations 2.0")) # pH control pump duration
    print(ogi.sendcmd("set pH2x control duration A 2.0"))

    #print(sendcmd("start batch culture"))
    #print(sendcmd("start turbidostat"))
    #print(sendcmd("start chemostat"))
    #print(sendcmd("start pH control"))
    #print(sendcmd("start pH2x control"))
    #print(sendcmd("start pHchemo control"))



def ThisShouldFail(cmd):
    ret=ogi.sendcmd(cmd)
    if ret is not None:
        print("command did not fail as expected!")
        exit()


print("these commands are supposed to fail, but the script should continue running testing all of them\n")
ogi.ogi_flags=set()
ogi.ogi_flags.add("automatic_reconnect")
ogi.ogi_flags.add("verbose")
#ogi.sendcmd("motors 10000") # this should fail, but it does not!
#ogi.sendcmd("motors -1000") # this should fail, but it does not!
# ogi.sendcmd("motor A 10000") # this should fail, but it does not!
ThisShouldFail("set temp control target A 51")
ThisShouldFail("set temp control target A -100")
ThisShouldFail("set temp control target E 37")
ThisShouldFail("set temp control target 37")


print("finished testing, exiting")