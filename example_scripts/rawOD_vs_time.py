# This script will record raw OD and temperature from all flasks in a loop, and save the data to a csv file. 
# It will also plot the raw OD in real time.

from matplotlib import pyplot as plt
import numpy as np
import time
from ogi import sendcmd, connect_OGI3
import datetime
import os

flasks=['A','B','C','D']
tts=[[] for _ in flasks]
ods=[[] for _ in flasks]
T_set=20.0 # temperature setpoint in degrees C. If below room temperature, the temp control will be off

connect_OGI3(verbose=True)

sendcmd('LEDs 1')   # all LEDs on
sendcmd("motors 1000") # start stirring to improve mixing

for f in flasks:
    sendcmd("set temp control target "+f+" "+str(int(T_set)))
    sendcmd("set temp control "+f+" 1")

now = datetime.datetime.now()
filename = "rawOD_"+now.strftime("%Y-%m-%d_%H-%M-%S") + ".csv"
folder = r"folder_of_your_choice" # change this to a folder where you want to save the data
path = os.path.join(folder, filename) if os.path.isdir(folder) else filename # otherwise, it will save in the current working directory
file = open(path, "w")
t0=time.time()

try:
    i=0
    while True:
        t1=time.time()
        tt=t1-t0
        file.write(f"{tt},")
        for n in range(0,len(flasks)):
            try:
                odraw=int(sendcmd("get rawOD "+flasks[n]))
            except:
                print("error getting rawOD")
                odraw=np.nan
                
            ret=sendcmd('get temperature '+flasks[n])
            try:
                ret=ret.strip().split(',')
                temp=float(ret[1])
                print(i,tt,flasks[n], " rawOD:", odraw, "Temp:", temp)
            except:
                print("error parsing temperature:", ret)
                temp=np.nan
                print(i,tt,flasks[n], " rawOD:", odraw, "Temp: ERROR")
            file.write(f"{odraw},{temp},")
            tts[n].append(tt)
            ods[n].append(odraw)

        file.write("\n")
        file.flush() 

        plt.cla()
        for j in range(0,len(flasks)):
            plt.plot(tts[j],ods[j])
        plt.pause(0.5)    # Need this to keep plot interactive

        i+=1


except KeyboardInterrupt:
    print("exiting due to keyboard interrupt")
    sendcmd("set temp controls 0")
    sendcmd("motors 0")
    sendcmd("LEDs 0") 
finally:
    file.close()   

