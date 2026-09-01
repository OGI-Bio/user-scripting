# This example toggles the turbidostat target between 0.1 and 0.4. The temperature starts
# at 30 C and after a few hours increases to 37 C. The data can be used to plot growth rate
# versus temperature.
# Note: adding media can lower the temperature in the flask - recommend placing the source
# bottle in a water bath at 37 C.

import time
import pandas as pd
import matplotlib.pyplot as plt
from enum import Enum
from ogi import sendcmd, connect_OGI3

FILENAME = "temperature_growthrate.csv"  # Save data here

FLASKS = ["A", "B", "C", "D"]

TARGET_OD_LOW = 0.1
TARGET_OD_HIGH = 0.4
targetOD = TARGET_OD_HIGH

INITIAL_TEMPERATURE = 30
FINAL_TEMPERATURE = 37
current_temperature = INITIAL_TEMPERATURE

CYCLE_TIME = 4  # Time in hours to wait before increasing temperature

connect_OGI3(verbose=True)

sendcmd("choose OD cal 1")
sendcmd(f"set temp control targets {current_temperature}")
sendcmd("set temp controls 1")
sendcmd(f"set turbidostat targets {targetOD}")
sendcmd("set turbidostat controls 1")
sendcmd("start turbidostat")

# Pandas data frame
c = ["time"]
for f in FLASKS:
    c.append(f"OD {f}")
    c.append(f"Target OD {f}")
    c.append(f"Temp {f}")
    c.append(f"Target Temp {f}")
df = pd.DataFrame(columns=c, dtype=float)
# print(df)


# This function takes measurements and updates the plot
def update_plot(df: pd.DataFrame, f: str):
    if payload := sendcmd(f"get OD {f}"):  # read OD
        # split payload into time and value:
        data = [float(s) for s in payload.split(",")]

        # save targets too
        data.append(targetOD)
        data.append(current_temperature)

        # join to existing dataframe
        tmp = pd.DataFrame(
            [data], columns=["time", f"OD {f}", f"Target OD {f}", f"Target Temp {f}"]
        )
        df = pd.concat([df, tmp], ignore_index=True)
        df = df.drop_duplicates()

    if payload := sendcmd(f"get temperature {f}"):  # read temperature
        data = [float(s) for s in payload.split(",")]

        # save targets too
        data.append(targetOD)
        data.append(current_temperature)

        tmp = pd.DataFrame(
            [data], columns=["time", f"Temp {f}", f"Target OD {f}", f"Target Temp {f}"]
        )
        df = pd.concat([df, tmp], ignore_index=True)
        df = df.drop_duplicates()

    # Save data to file
    df.to_csv(FILENAME)

    # Plot data
    fig, ax = plt.subplots(num=f, clear=True)
    ax2 = ax.twinx()
    data = df[["time", f"OD {f}", f"Target OD {f}", f"Temp {f}", f"Target Temp {f}"]]
    data = data.dropna(how="all")

    ax.plot(data["time"], data[f"OD {f}"], "x-", c="tab:blue")
    ax.step(data["time"], data[f"Target OD {f}"], where="post", color="tab:green")
    ax2.plot(data["time"], data[f"Temp {f}"], ".", c="tab:orange")
    ax2.step(data["time"], data[f"Target Temp {f}"], where="post", color="tab:red")

    ax.set_xlabel("Time (hrs)")
    ax.set_ylabel("OD")
    ax2.set_ylabel(r"Temperature ($\degree$C)")

    fig.legend(
        [f"OD {f}", f"Target OD {f}", f"Temperature {f}", f"Target temperature {f}"]
    )

    return df


class Phase(Enum):
    WAITING = 1
    LOW_T = 2
    HIGH_T = 37


phase = Phase.WAITING
start_time = 0

time.sleep(3 * 60)

while True:
    for f in FLASKS:
        df = update_plot(df, f)
        # print(df)

        # Adjust target
        if df[f"OD {f}"].dropna().iloc[-1] > TARGET_OD_HIGH:
            targetOD = TARGET_OD_LOW
            sendcmd(f"set turbidostat target {f} {targetOD}")

            # If this is the first time above the high threshold, start the timer
            if phase == Phase.WAITING:
                phase = Phase.LOW_T
                start_time = time.time()

        if df[f"OD {f}"].dropna().iloc[-1] < TARGET_OD_LOW:
            targetOD = TARGET_OD_HIGH
            sendcmd(f"set turbidostat target {f} {targetOD}")

        plt.pause(10)  # Runs the GUI loop for 10 s - keeps the plot interactive

    # increase temperature after some time
    if (
        phase == Phase.LOW_T and time.time() - start_time > CYCLE_TIME * 3600
    ):  # After 4 hours, increase temperature
        phase = Phase.HIGH_T
        current_temperature = FINAL_TEMPERATURE
        sendcmd(f"set temp control targets {current_temperature}")
