from ads1x15 import ADS1015
from ST7735 import ST7735
from machine import I2C, Pin
import sys
import time

CONV_2V_5V_DIFF = 5 / 1.798
CONV_2V_5V_COMMON = 5 / 1.799
CONV_2V_12V_COMMON = 12 / 1.797
CONV_2V_20V_COMMON = 20 / 1.818
BACK_COLOUR = 0x0000
FRONT_1_COLOUR = 0xDEDB
FRONT_2_COLOUR = 0xA514
HIGHLIGHT_1_COLOUR = 0x296B
HIGHLIGHT_2_COLOUR = 0x7380
CHANNEL_TXT_Y = 15
CHANNEL_TXT_GAP = 11
POWER_TXT_X = 96
POWER_TXT_Y = 14
POWER_TXT_BUFFER = 3
POWER_TXT_GAP = 11

def draw_background(tft: ST7735):
    tft.fill_screen(BACK_COLOUR)
    tft.draw_rect(0, 0, 180, 10, HIGHLIGHT_1_COLOUR)
    tft.draw_fast_text("POWER MONITOR", 32, 2, FRONT_1_COLOUR)
    tft.draw_fast_text("Ch0:      V", 5, CHANNEL_TXT_Y, FRONT_2_COLOUR)
    tft.draw_fast_text("Ch1:      V", 5, CHANNEL_TXT_Y + CHANNEL_TXT_GAP, FRONT_2_COLOUR)
    tft.draw_fast_text("Ch2:      V", 5, CHANNEL_TXT_Y + CHANNEL_TXT_GAP * 2, FRONT_2_COLOUR)
    tft.draw_fast_text("Ch3:      V", 5, CHANNEL_TXT_Y + CHANNEL_TXT_GAP * 3, FRONT_2_COLOUR)

    tft.draw_rect(POWER_TXT_X, POWER_TXT_Y, 61, 46, HIGHLIGHT_2_COLOUR)
    tft.draw_fast_text("     V", POWER_TXT_X + 3, POWER_TXT_Y + POWER_TXT_BUFFER, FRONT_1_COLOUR)
    tft.draw_fast_text("     A", POWER_TXT_X + 3, POWER_TXT_Y + POWER_TXT_BUFFER + POWER_TXT_GAP, FRONT_1_COLOUR)
    tft.draw_fast_text("     W", POWER_TXT_X + 3, POWER_TXT_Y + POWER_TXT_BUFFER + POWER_TXT_GAP * 2, FRONT_1_COLOUR)
    tft.draw_fast_text("     Wh", POWER_TXT_X + 3, POWER_TXT_Y + POWER_TXT_BUFFER + POWER_TXT_GAP * 3, FRONT_1_COLOUR)

    tft.draw_hline(3, 59, 90, HIGHLIGHT_1_COLOUR)

def draw_channel_volts(tft: ST7735, channel, v):
    y = CHANNEL_TXT_Y + (CHANNEL_TXT_GAP * channel)
    tft.draw_fast_text(f"{round(v, 3):.3f}", 42, y, FRONT_2_COLOUR, BACK_COLOUR)

def draw_volts(tft: ST7735, v):
    tft.draw_fast_text(f"{round(v, 3):05.3f}", POWER_TXT_X + 2, POWER_TXT_Y + POWER_TXT_BUFFER, FRONT_1_COLOUR, HIGHLIGHT_2_COLOUR)

def draw_amps(tft: ST7735, a):
    tft.draw_fast_text(f"{round(a, 2):05.2f}", POWER_TXT_X + 2, POWER_TXT_Y + POWER_TXT_BUFFER + POWER_TXT_GAP, FRONT_1_COLOUR, HIGHLIGHT_2_COLOUR)

def draw_watts(tft: ST7735, w):
    tft.draw_fast_text(f"{round(w, 1):05.1f}", POWER_TXT_X + 2, POWER_TXT_Y + POWER_TXT_BUFFER + POWER_TXT_GAP * 2, FRONT_1_COLOUR, HIGHLIGHT_2_COLOUR)

def draw_watt_hours(tft: ST7735, wh):
    tft.draw_fast_text(f"{int(wh):05d}", POWER_TXT_X + 2, POWER_TXT_Y + POWER_TXT_BUFFER + POWER_TXT_GAP * 3, FRONT_1_COLOUR, HIGHLIGHT_2_COLOUR)

def draw_time(tft: ST7735, secs):
    h = int(secs / 3600)
    m = int((secs % 3600) / 60)
    s = secs % 60
    tft.draw_fast_text(f"{h:02d}h {m:02d}m {s:02d}s", 40, 65, FRONT_2_COLOUR, BACK_COLOUR)


# Setup ADS1015
SDA_Pin = Pin(16)
SCL_Pin = Pin(17)
port = I2C(id=0, scl=SCL_Pin, sda=SDA_Pin, freq=400000)
ADS = ADS1015(port, 72, 2)

# Setup TFT
tft = ST7735(dc=28, cs=21, rt=27, sck=18, mosi=19, miso=20)
tft.tft_initialize()
tft.set_rotation(1)
draw_background(tft)

prev_ch_v = [0, 0, 0, 0]
ch_v = [0, 0, 0, 0]

prev_in_v = -1
in_v = 0

prev_amps = -1
amps = 0

prev_secs = -1
secs = 0

prev_wh = -1
wh = 0

prev_ticks = None
ticks = 0

start_time = time.time()

while True:
    ch_v = [
        ADS.raw_to_v(ADS.read(0, 0)),
        ADS.raw_to_v(ADS.read(0, 1)),
        ADS.raw_to_v(ADS.read(0, 2)),
        ADS.raw_to_v(ADS.read(0, 3))
    ]

    for i in range(4):
        if ch_v[i] != prev_ch_v[i]:
            draw_channel_volts(tft, i, ch_v[i])
    prev_ch_v = ch_v

    in_v = ch_v[2] * CONV_2V_5V_COMMON
    if in_v != prev_in_v:
        draw_volts(tft, in_v)

    acs_diff_v = ADS.raw_to_v(ADS.read(0, 0, 3)) * CONV_2V_5V_DIFF
    amps = (acs_diff_v * 1000) / 66

    ticks = time.ticks_ms()
    if prev_ticks is not None:
        ms_delta = time.ticks_diff(ticks, prev_ticks)
        h_delta = (ms_delta / 1000 / 3600)
        wh += in_v * amps * h_delta
    prev_ticks = time.ticks_ms()

    if amps != prev_amps:
        draw_amps(tft, amps)
    
    if amps != prev_amps or in_v != prev_in_v:
        draw_watts(tft, in_v * amps)

    if int(wh) != prev_wh:
        draw_watt_hours(tft, wh)
    prev_wh = int(wh)

    prev_in_v = in_v
    prev_amps = amps

    secs = time.time() - start_time
    if secs != prev_secs:
        draw_time(tft, secs)
    prev_secs = secs

    sys.stdout.write(f"dc_voltage,{in_v}\n")
    sys.stdout.write(f"dc_current,{amps}\n")