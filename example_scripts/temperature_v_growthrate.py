# This example toggles the turbidostat target between 0.1 and 0.4. The temperature starts
# at 30 C and after a few hours increases to 37 C. The data can be used to plot growth rate
# versus temperature. Flask A only.
# Note: adding media can lower the temperature in the flask - recommend placing the source
# bottle in a water bath at 37 C.

import time
import pandas as pd
import matplotlib.pyplot as plt
from enum import Enum
from ogi import sendcmd, connect_OGI3


FILENAME = 'temperature_growthrate.csv'   # Save data here

TARGET_OD_LOW = 0.1
TARGET_OD_HIGH = 0.4
targetOD = TARGET_OD_HIGH

INITIAL_TEMPERATURE = 30
FINAL_TEMPERATURE = 37
current_temperature = INITIAL_TEMPERATURE

CYCLE_TIME = 4  # Time in hours to wait before increasing temperature

connect_OGI3(verbose=True)

sendcmd('choose OD cal 1')
sendcmd('set temp controls 0')
sendcmd(f'set temp control target A {current_temperature}')
sendcmd('set temp control A 1')
sendcmd('set turbidostat controls 0')
sendcmd(f'set turbidostat target A {targetOD}')
sendcmd('set turbidostat control A 1')
sendcmd('start turbidostat')

# Pandas data frame
c = ['time','OD A','Target OD A', 'Temp A','Target Temp A']
df = pd.DataFrame(columns=c, dtype=float)

# This function takes measurements and updates the plot
def update_plot(df):
    if (payload := sendcmd('get OD A')):    # read OD
        # split payload into time and value:
        data = [float(s) for s in payload.split(',')]

        # save targets too
        data.append(targetOD)
        data.append(current_temperature)

        # join to existing dataframe
        tmp = pd.DataFrame([data], columns=['time', 'OD A', 'Target OD A', 'Target Temp A'])
        df = pd.concat([df, tmp], ignore_index=True)
        df = df.drop_duplicates()

    if (payload := sendcmd('get temperature A')):    # read temperature
        data = [float(s) for s in payload.split(',')]

        # save targets too
        data.append(targetOD)
        data.append(current_temperature)

        tmp = pd.DataFrame([data], columns=['time', 'Temp A', 'Target OD A', 'Target Temp A'])
        df = pd.concat([df, tmp], ignore_index=True)
        df = df.drop_duplicates()

    # Save data to file
    df.to_csv(FILENAME)

    # Plot data
    fig, ax = plt.subplots(num=0, clear=True)
    ax2 = ax.twinx()
    ax.plot(df['time'], df['OD A'], 'x-', c='tab:blue')
    ax.step(df['time'], df['Target OD A'], where='post', color='tab:green')
    ax2.plot(df['time'], df['Temp A'], '.', c='tab:orange')
    ax2.step(df['time'], df['Target Temp A'], where='post', color='tab:red')

    ax.set_xlabel('Time (hrs)')
    ax.set_ylabel('OD')
    ax.set_ylabel(r'Temperature ($\degree$C)')

    fig.legend(['OD A', ' Target OD A', 'Temperature A', 'Target temperature'])

    plt.pause(10)    # Runs the GUI loop for 10 s - keeps the plot interactive

    return df


class Phase(Enum):
    WAITING = 1
    LOW_T = 2
    HIGH_T = 37


phase = Phase.WAITING
start_time = 0

while(True):
    df = update_plot(df)

    # Adjust target
    if (df['OD A'].dropna().iloc[-1] > TARGET_OD_HIGH):
        targetOD = TARGET_OD_LOW
        sendcmd(f"set turbidostat target A {targetOD}")

        # If this is the first time above the high threshold, start the timer
        if phase == Phase.WAITING:
            phase = Phase.LOW_T
            start_time = time.time()

    if (df['OD A'].dropna().iloc[-1] < TARGET_OD_LOW):
        targetOD = TARGET_OD_HIGH
        sendcmd(f'set turbidostat target A {targetOD}')

    # increase temperature after some time
    if (
        phase == Phase.LOW_T and time.time() - start_time > CYCLE_TIME * 3600
    ):  # After 4 hours, increase temperature
        phase = Phase.HIGH_T
        current_temperature = FINAL_TEMPERATURE
        sendcmd(f"set temp control target A {current_temperature}")
