# Usage
Download `ogi.py` and keep it in the same directory as your script - it provides functions for connection and sending commands.
Use like
```
from ogi import sendcmd, connect_OGI3

connect_OGI3()
sendcmd('list OD cals')
```

To use these scripts you'll need to install python 3 and the following libraries:
  1) pyserial
  2) pandas
  3) matplotlib

# Examples
We have some examples to do different things like plot ODs, toggle turbidostat targets etc. to get you started.
You can use and modify these as you like.
If you have questions or feedback, you can open an issue in this repository or contact help@ogibiotec.com.

### `ogi.py`
Provides functions for connecting and sending commands.

### `command_prompt.py`
Provides a simple interactive prompt where you can type in commands and see the response.

### `plotODs.py`
Periodically updates a figure with new OD measurements. Start your experiment before
running the script.

### `batch_culture.py`
Demonstrates setting some experiment parameters and starting an experiment automatically.

### `turbidostat.py`
Shows how to update experiment parameters based on measurements by toggling target OD
between two values to get repeat growth curves.

<img width="640" height="480" alt="251212_3" src="https://github.com/user-attachments/assets/7ecba4d6-df97-4cb1-b3e1-8d3c5a765685" />


### `temperature_ramp.py`
Starts a batch culture at 30 C until OD=0.5, then increases temperature by 1 C per hr to 37 C.

<img width="729" height="535" alt="temp_ramp_1" src="https://github.com/user-attachments/assets/9bc18f16-365c-45d7-a1d2-f3e0bd561427" />

### `valentine_chemostat.py`
Controls OD of two flasks via chemostat to generate a heart shape:

<img width="822" height="591" alt="valentine" src="https://github.com/user-attachments/assets/8f3ff9d0-2a14-4ea2-a348-09bd9f1aa548" />

### `temperature_v_growthrate.py`
Toggles turbidostat OD target between 0.1 and 0.4 to get repeated growth curves; after 4 hrs increases the temperature from 30 C to 37 C.

<img width="953" height="662" alt="temperature_v_growthrate" src="https://github.com/user-attachments/assets/3f3d8dbb-7a5e-40fc-8b49-195a5179bd61" />

### `media_switch.py`
Controls pumps directly to periodically dilute culture, switching medium (by switching from input -> output pump) partway through.

Note: Requires external liquid control module!

![Growth rate of E. coli with media switch](./imgs/Media_switch_growthrate.png)
