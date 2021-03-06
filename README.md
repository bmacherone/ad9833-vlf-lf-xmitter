# ad9833 vlf/lf transmitter

## This circuit was designed to fill the following criteria:
- Ability to generate sine wave signals covering the 2200, 1750 and 630 meter bands, and be able to be stretched to 160 meters.
- Accurate frequency control without complex analog circuitry.
- Able to generate narrow band, Farsnworh Morse Code over a wide wpm range.
- Power output appropriae for the 2200, 1750 and 630 meter bands
- Harmonic free (or at least supressed) signal
- Controlled by a flexible, remotely accessible microcontroller, in this case a Raspbery Pi 3B+
- All frequency generation performed by hardware, not software
- Inexpensive (AD9833 module is $4 U.S dollars in 2020)

- Easily extensible to achieve remotely operated cw transmission with adjustable tuning

## more to come, this is a preliminary posting

***
## This is the schematic for the Raspberry Pi "hat"
![foo *bar*]

[foo *bar*]: images/xmithat.png "Schematic"
***
## cwtest.py (current code is in the src directory)
```python:src/cwtest.py
#!/usr/bin/env python3

import sys
import time

from AD9833 import AD9833

# set the frequency in hz
#
# 2200 meters
# frequency = 137700
# 630 meters
# frequency = 472700
# 160 meters beacon
frequency = 1992000
# 20 meters
#frequency = 14010000
# yes, it worked on 20 meters (with no low pass filter)

wpm = 10

# define Farnsworth timing
ditsperword = 50
secondsperdit = 60/(ditsperword*wpm)
dit = secondsperdit
dash = dit * 3
interelement = dit

# assume one interelement after each element
intercharacter = (interelement * 3) - interelement

# assume one intercharacter after each word
interword = (interelement * 7) - intercharacter

# operating conditions
print("frequency",frequency)
print("wpm",wpm)
print("seconds per dit",secondsperdit)
print("dit",dit)
print("dash",dash)
print("intercharacter",intercharacter)
print("interword",interword)

# a subset of the morse code table
morse = {
    "a": ".-",
    "b": "-...",
    "c": "-.-.",
    "d": "-..",
    "e": ".",
    "f": "..-.",
    "g": "--.",
    "h": "....",
    "i": "..",
    "j": ".---",
    "k": "-.-",
    "l": ".-..",
    "m": "--",
    "n": "-.",
    "o": "---",
    "p": ".--.",
    "q": "--.-",
    "r": ".-.",
    "s": "...",
    "t": "-",
    "u": "..-",
    "v": "...-",
    "w": ".--",
    "x": "-..-",
    "y": "-.--",
    "z": "--..",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
    "0": "-----"
}

# define the pins on the GPIO
data = 10
clk = 11
fsync = 8

# instantiate a AD9833 object
ad = AD9833(data,clk,fsync)

# start with everything off
ad.keyup()

# Morse code functions
#
# transmit a dit
def xdit(ad):
    ad.set_freq(frequency)
    time.sleep(dit)
    ad.keyup()
  
# transmit a dash
def xdash(ad):
    ad.set_freq(frequency)
    time.sleep(dash)
    ad.keyup()

# send a character
def send(ad,c):
    global morse
    c = c.lower()
    if c in morse:
        m = morse[c]
        for i in range(0,len(m)):
            if m[i] == ".":
                xdit(ad)
            else:
                xdash(ad)
            time.sleep(interelement)

# loop forever sending the "phrase"
#
phrase = "test beacon de ab2iu 1992khz FN32at generated by raspberry pi and ad9833"

xmit = 1
while xmit:
    for c in phrase:

        sys.stdout.write(c)
        sys.stdout.flush()

        if c == " ":
            time.sleep(interword)
        else:
            send(ad,c)
            time.sleep(intercharacter)
            
    # interword delay at end of line
    time.sleep(interword)

    sys.stdout.write("\n")
    sys.stdout.flush()
    # zero xmit to only transmit once
    #xmit = 0
    

# we normally never get here...
ad.keyup()
time.sleep(10)

```
***
## AD9833.py (current code is in the src directory)

```python:src/AD9833.py
# 
#   simple control of the AD9833 DDS chip
# 
# 
#   adopted from code by M J Oldfield
# 

import gpiozero

class AD9833:

    def __init__(self, data, clk, fsync):
        self.dataPin  = gpiozero.OutputDevice(pin = data)
        self.clkPin   = gpiozero.OutputDevice(pin = clk)
        self.fsyncPin = gpiozero.OutputDevice(pin = fsync)

        self.fsyncPin.on()
        self.clkPin.on()
        self.dataPin.off()

        self.clk_freq = 25.0e6

        # control word format
        #DB15	DB14	DB13	DB12	DB11	DB10	DB9	DB8	DB7	DB6	DB5	DB4	DB3	DB2	DB1	DB0
        #0	0	B28	HLB	FSELECT	PSELECT	0	RESET	SLEEP1	SLEEP12	OPBITEN	0	DIV2	0	MODE	0

        # 0 reserved
        self.mode_t = 1 << 1
        # 2 reserved
        self.mode_div2 = 1 << 3
        # 4 reserved
        self.opbiten = 1 << 5
        self.sleep12 = 1 << 6
        self.sleep1 = 1 << 7
        self.flag_reset = 1 << 8
        # 9 reserved
        self.pselect = 1 << 10
        self.fselect = 1 << 11
        self.hlb = 1 << 12
        self.flag_b28  = 1 << 13
        
        # flags that indicate freq0 or freq1
        self.flag_freq0 = 1 << 14
        self.flag_freq1 = 1 << 15

        self.ff = self.flag_freq0
        
        self.scale = 1 << 28
        self.sbyf = self.scale / self.clk_freq

    # set the current output frequency and turn on the output
    # this is for sinewave output
    def set_freq(self, f):
        # which freq register controlled by self.ff
        # frequency setting = f * scalebyclockfreq
        n_reg = int(f * self.sbyf)

        n_low = n_reg         & 0x3fff
        n_hi  = (n_reg >> 14) & 0x3fff

        self.send16(self.flag_b28)
        self.send16(self.ff | n_low)
        self.send16(self.ff | n_hi)


    # send a 16 bit word, msb first, indicating frame with fsync, each bit with clock
    def send16(self, n):
        # fsync to zero indicates new 16 bit word
        self.fsyncPin.off()

        # iterate through all 16 bits, msb first
        mask = 1 << 15
        for i in range(0, 16):

            self.dataPin.value = bool(n & mask)
            # falling edge of clock latches data
            self.clkPin.off()
            self.clkPin.on()

            # move to next bit
            mask = mask >> 1

        # data at zero when not transmitting bits
        self.dataPin.off()
        # fsync to on indicates end of transfer
        self.fsyncPin.on()

    # keyup turns off all output and sets output to center of range
    def keyup(self):
        self.send16(self.flag_reset)
        
        
# needs code for phase setting and choice; triange and square output
 
```
***

## assembled hat on Pi minus AD9833 module
![hatonpi](images/xmithat_onPi.JPG "Hat on Pi")
***

## assembled hat on Pi with AD9833 module
![hatonpiw](images/xmithat_onPiwAD.JPG "Hat on Pi")
***

<table style="width:100%">
<tr>
<th colspan=2, align=left>

## AD9833 module
</th>
<tr>
<td>
<img src="images/s-l1600.jpg">
</td>
<td>
<img src="images/s-l1600-1.jpg">
</td>
</tr>
<tr>
<td colspan=2 align=center>
<img src="images/s-l1600-2.jpg">
</td>
</tr>
<tr>
<td>
<img src="images/ad9833mod01.JPG">
<td>
<td>
<img src="images/ad9833mod02.JPG">
<td>
<tr>
</table>


