# This script will control the pumps directly to periodically dilute the culture
# in all flasks, and then switch media after a certain amount of time. It uses both
# input and "output" pumps as inputs. Excess is drained via an external module.

import time
import pandas as pd
from dataclasses import dataclass
from enum import Enum
from ogi import sendcmd, connect_OGI3

@dataclass(frozen=True)
class Params:
    FILENAME: str = "media_switch.csv"  # Save data here
    FLASK_VOL_ML: float = 15
    SAMPLE_INTERVAL_MINS: int = 5
    THRESHOLD_OD: float = 0.3
    DILUTION_FACTOR: float = 0.25

    @property
    def SAMPLE_INTERVAL_SEC(self) -> float:
        return self.SAMPLE_INTERVAL_MINS * 60

class PumpType(Enum):
    INPUT = 1
    OUTPUT = 2

@dataclass
class Pump:
    media1: str
    media2: str
    pumptype: PumpType = PumpType.INPUT

    INPUMP_FLOWRATE_ML_PER_MIN: float = 3.0
    OUTPUMP_FLOWRATE_ML_PER_MIN: float = 5.0

    @property
    def INPUMP_FLOWRATE_ML_PER_SEC(self) -> float:
        return self.INPUMP_FLOWRATE_ML_PER_MIN / 60

    @property
    def OUTPUMP_FLOWRATE_ML_PER_SEC(self) -> float:
        return self.OUTPUMP_FLOWRATE_ML_PER_MIN / 60

    # current flowrate
    @property
    def FLOWRATE_ML_PER_MIN(self) -> float:
        if self.pumptype == PumpType.INPUT:
            return self.INPUMP_FLOWRATE_ML_PER_MIN
        else:
            return self.OUTPUMP_FLOWRATE_ML_PER_MIN

    @property
    def FLOWRATE_ML_PER_SEC(self) -> float:
        return self.FLOWRATE_ML_PER_MIN / 60

    @property
    def media(self) -> str:
        if self.pumptype == PumpType.INPUT:
            return self.media1
        else:
            return self.media2

    @property
    def string(self) -> str:
        if self.pumptype == PumpType.INPUT:
            return "inpump"
        else:
            return "outpump"

@dataclass
class Flask:
    f: str # label
    pump: Pump
    MEDIA_SWITCH_TIME_HRS: float = 48
    cycle: int = 0

    @property
    def MEDIA_SWITCH_TIME_SEC(self) -> float:
        return self.MEDIA_SWITCH_TIME_HRS * 3600


def update_ODs(df: pd.DataFrame, flask: Flask) -> pd.DataFrame:
    if payload:= sendcmd(f"get OD {flask.f}"):  # read OD
        data = [float(s) for s in payload.split(",")]

        tmp = pd.DataFrame([data], columns=["Time (hrs)", "OD"])
        tmp["Reactor"] = f"{flask.f}"
        tmp["media"] = flask.pump.media
        tmp["cycle #"] = flask.cycle

        df = pd.concat([df, tmp], ignore_index=True)
        df = df.drop_duplicates()

    return df

def dilutionFactor2Duration(params: Params, pump: Pump) -> float:
    return (params.FLASK_VOL_ML / pump.FLOWRATE_ML_PER_SEC) * (params.DILUTION_FACTOR / (1 - params.DILUTION_FACTOR))


def update_pumps(flask: Flask, OD: float, params: Params) -> int:
    if OD < params.THRESHOLD_OD:    # do nothing
        return flask.cycle

    duration = dilutionFactor2Duration(params, flask.pump)
    print(f"Diluting for {duration:.2f} s")

    sendcmd(f"{flask.pump.string} {flask.f} 1")
    time.sleep(duration)
    sendcmd(f"{flask.pump.string} {flask.f} 0")

    return flask.cycle + 1

def main():
    params = Params()

    # Remove flasks as needed
    flasks: list[Flask] = [
        Flask('A', Pump("MM9+Glucose", "MM9+Glycerol")),
        Flask('B', Pump("MM9+Glucose", "MM9+Glycerol")),
        Flask('C', Pump("MM9+Glucose", "MM9+Glycerol")),
        Flask('D', Pump("MM9+Glucose", "MM9+Glycerol")),
    ]

    # Pandas dataframe to store data
    c = ["Time (hrs)", "Reactor", "OD", "media", "cycle #"]
    df = pd.DataFrame(columns=c, dtype=float)

    connect_OGI3(verbose=True)

    sendcmd("choose OD cal 0")
    sendcmd("choose O2 cal 0")
    sendcmd(f"set sample interval {params.SAMPLE_INTERVAL_MINS}")
    sendcmd("set exp length 192")
    sendcmd("set temp control targets 37")
    sendcmd("set temp controls 1")
    sendcmd("start batch culture")

    for f in flasks:
        df = update_ODs(df, f)

    t0 = time.time()
    t = time.time()

    try:
        while True:
            time.sleep(1)
            if time.time() - t > params.SAMPLE_INTERVAL_SEC:
                t = time.time()
                for f in flasks:
                    df = update_ODs(df, f)

                    OD = df["OD"][df["Reactor"] == f.f].iloc[-1]
                    f.cycle = update_pumps(f, OD, params)

                    if time.time() - t0 > f.MEDIA_SWITCH_TIME_SEC and f.pump.pumptype == PumpType.INPUT:
                        print("Switching media...")
                        f.pump.pumptype = PumpType.OUTPUT

                # Save data to file
                df.to_csv(params.FILENAME)


    except Exception as e:
        print("Error:", e)

    finally:
        # switch off pumps on any exit, including Ctrl+C
        sendcmd("inpumps 0")
        sendcmd("outpumps 0")


if __name__ == "__main__":
    main()
