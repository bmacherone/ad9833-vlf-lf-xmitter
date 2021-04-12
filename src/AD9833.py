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
