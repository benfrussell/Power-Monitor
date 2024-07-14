from ADS1115 import ADS1115
from machine import I2C, Pin
import sys

SDA_Pin = Pin(14)
SCL_Pin = Pin(15)
port = I2C(id=1, scl=SCL_Pin, sda=SDA_Pin, freq=400000)
print(port.scan())

ADS = ADS1115(i2c=port, gain=0)

while True:
    acs_1_diff_v = ADS.raw_to_v(ADS.read(rate=0, channel1=0, channel2=1))
    in_v_1 = ADS.raw_to_v(ADS.read(rate=0, channel1=2))
    lm35_1_v = ADS.raw_to_v(ADS.read(rate=0, channel1=3))

    amps_1 = (acs_1_diff_v * 1000) / 66
    temp_1 = lm35_1_v * 100

    sys.stdout.write(f"dc_1_voltage,{in_v_1}\n")
    sys.stdout.write(f"dc_1_current,{amps_1}\n")
    sys.stdout.write(f"temp_1,{temp_1}\n")