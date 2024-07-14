# Power Monitor
A combined AC/DC power monitor and data logger developed for a Python Linux host and MicroPython Raspberry Pi Pico for driving the embedded modules.

The solution was developed and hosted on a Steam Deck.

## Components
- AC sensing is done using a PZEM-016 connected to the host over an RS485 to USB cable.
- DC sensing uses a pair of ACS712 current sensing modules and an ADS1015 ADC module to convert analog current & voltage for the Pico.
    - The Pico has a built in ADC, but this project uses a dedicated external module to side-step the extra configuration required to get an accurate reading.
    - One ACS712 monitors no current and is used as a baseline for the other ACS712, with the ADC's difference mode used to compare them.
    - The ACS712 requires a 5V supply and the ADS1015's supply has to match the Pico's logic level (3.3V), so a step-up converter is used to bring the 3.3V analog supply-out from the ADS1015 up to 5V for the ACS712s. 
    - Simple voltage dividers are used to ensure all analog inputs to the ADS1015 remain under 3.3V. 
- An ST7735 TFT display is included to provide a basic status of the DC sensing components.

### Parts
- [Raspberry Pi Pico WH (Pre-Soldered Headers)](https://www.pishop.ca/product/raspberry-pi-pico-wh-pre-soldered-headers/)
- [UART to RS485 Voltmeter Ammeter Voltage Current Power Factor Frequency Energy Tester Multi Function Meter(Split CT(100A)+USB to 485 Module PZEM-016) ](https://www.amazon.ca/dp/B0BSV2THYK)
- [DAOKI 5 Pack 30A Range Current Sensor Module ACS712 Module for Arduino](https://www.amazon.ca/dp/B00XT0PL20)
- [ADS1015 12-Bit ADC - 4 Channel with Programmable Gain Amplifier](https://www.pishop.ca/product/ads1015-12-bit-adc-4-channel-with-programmable-gain-amplifier/)
- [Adafruit MiniBoost 5V @ 1A - TPS61023](https://www.adafruit.com/product/4654)
- [0.96" 160x80 Color SPI TFT Display](https://www.dfrobot.com/product-2445.html)

*Note: These parts are a mix of what I had laying around and what I could get for cheap at the time - you could almost certainly do better!*

## Steam Deck Implementation

In my setup the Power Monitor is hosted on a Steam Deck. It's portability makes it easy to bring the devices directly to appliances. The desktop environment also allows for developing and prototyping directly on the platform.

Some additional configuration is required for the environment to allow communicating with the Pico.

### Allow Device Communication

On the Steam Deck you will need to give your user account permission to access the serial port the Pico is connected on. This can be done using the below script. 

``` bash
#!/bin/bash
# This script will give your useraccount access to the serial port ttyACM0

THEUSER=""

if [ -v $SUDO_USER ]; then
    THEUSER=$USER
else
    THEUSER=$SUDO_USER
fi

echo "You are ${THEUSER}..."
# !INFO! change /dev/ttyACM0 to your serial port if it is different for your Pico
GROUP=$(stat -c '%G' /dev/ttyACM0)
echo "And get the '${GROUP}' group..."

# add user to group
sudo usermod -a -G $GROUP $THEUSER
echo "Done! Please logout and login again to activate changes."
```

*Taken with great appreciation from https://github.com/paulober/MicroPico/wiki/Linux*

You can determine which port your Pico is connecting with by connecting it and running this command:

``` bash
sudo dmesg | grep tty
```

Look for the most recently connected device.

### Development Environment

Development was done using the VS Code flatpak found in the Software Center.

#### MicroPico Setup

In VS Code you can develop on the Pico using the [MicroPico Extension](https://marketplace.visualstudio.com/items?itemName=paulober.pico-w-go). Make sure to also pick up the prerequesite extensions.

You may need to specify the serial port that the MicroPico is connecting on for MicroPico to find the device. Use the above **dmesg** command to find the port and enter it in the MicroPico Workspace Setting: **Manual Com Device** *(Ctrl+Shift+P, MicroPico: Workspace Settings)*

In my case the Manual Com Device needed to be set to **/dev/ttyACM1**

#### Integrated Terminal Fix

Flatpaks run in a sandbox environment. For the VS Code integrated terminal to access outside of the sandbox, will need to add the following lines to your user settings:

``` json
{
    // Use bash by default
    "terminal.integrated.defaultProfile.linux": "bash",
    "terminal.integrated.profiles.linux": {
        // Use host-spawn to create the bash process
		"bash": {
			"path": "/app/bin/host-spawn",
            "args": ["bash"],
			"icon": "terminal-bash",
            "overrideName": true
		},
        // These remain the same as the defaults
		"zsh": {
			"path": "zsh"
		},
		"fish": {
			"path": "fish"
		},
		"tmux": {
			"path": "tmux",
			"icon": "terminal-tmux"
		},
		"pwsh": {
			"path": "pwsh",
			"icon": "terminal-powershell"
		}
	}
}
```

*For more info see https://github.com/flathub/com.visualstudio.code?tab=readme-ov-file#usage*