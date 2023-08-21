# RP2040 uctype definitions for MicroPython
# See https://iosoft.blog/picofreq_python for description
#
# Copyright (c) 2023 Jeremy P Bentham
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# v0.01 JPB 7/10/21  Derived from adc_dma_test v0.05
# v0.02 JPB 15/8/23  Added DMA and PWM classes
# v0.03 JPB 19/8/23  Renamed rp_devices.py to pico_devices.py
# v0.04 JPB 20/8/23  Additions for gated frequency measurement
# v0.05 JPB 21/8/23  Tidied up for release

from uctypes import BF_POS, BF_LEN, UINT32, BFUINT32, struct
import array, uctypes

PAD_BASE        = 0x4001c000
PAD_PIN_WIDTH   = 0x04
ADC_BASE        = 0x4004c000
PWM_BASE        = 0x40050000
PWM_SLICE_WIDTH = 0x14
PWM_SLICE_COUNT = 8
TIMER_BASE      = 0x40054000

# DMA: RP2040 datasheet 2.5.7
DMA_BASE        = 0x50000000
DMA_CHAN_WIDTH  = 0x40
DMA_CHAN_COUNT  = 12
DMA_SIZE_8, DMA_SIZE_16, DMA_SIZE_32 = 0, 1, 2
DREQ_PIO0_TX0, DREQ_PIO0_RX0, DREQ_PIO1_TX0 = 0, 4, 8
DREQ_PIO1_RX0, DREQ_SPI0_TX,  DREQ_SPI0_RX  = 12, 16, 17
DREQ_SPI1_TX,  DREQ_SPI1_RX,  DREQ_UART0_TX = 18, 19, 20
DREQ_UART0_RX, DREQ_UART1_TX, DREQ_UART1_RX = 21, 22, 23
DREQ_PWM_WRAP0                              = 24
DREQ_I2C0_TX,  DREQ_I2C0_RX,  DREQ_I2C1_TX  = 32, 33, 34
DREQ_I2C1_RX,  DREQ_ADC                     = 35, 36

DMA_CTRL_TRIG_FIELDS = {
    "AHB_ERROR":   31<<BF_POS | 1<<BF_LEN | BFUINT32,
    "READ_ERROR":  30<<BF_POS | 1<<BF_LEN | BFUINT32,
    "WRITE_ERROR": 29<<BF_POS | 1<<BF_LEN | BFUINT32,
    "BUSY":        24<<BF_POS | 1<<BF_LEN | BFUINT32,
    "SNIFF_EN":    23<<BF_POS | 1<<BF_LEN | BFUINT32,
    "BSWAP":       22<<BF_POS | 1<<BF_LEN | BFUINT32,
    "IRQ_QUIET":   21<<BF_POS | 1<<BF_LEN | BFUINT32,
    "TREQ_SEL":    15<<BF_POS | 6<<BF_LEN | BFUINT32,
    "CHAIN_TO":    11<<BF_POS | 4<<BF_LEN | BFUINT32,
    "RING_SEL":    10<<BF_POS | 1<<BF_LEN | BFUINT32,
    "RING_SIZE":    6<<BF_POS | 4<<BF_LEN | BFUINT32,
    "INCR_WRITE":   5<<BF_POS | 1<<BF_LEN | BFUINT32,
    "INCR_READ":    4<<BF_POS | 1<<BF_LEN | BFUINT32,
    "DATA_SIZE":    2<<BF_POS | 2<<BF_LEN | BFUINT32,
    "HIGH_PRIORITY":1<<BF_POS | 1<<BF_LEN | BFUINT32,
    "EN":           0<<BF_POS | 1<<BF_LEN | BFUINT32
}
# Channel-specific DMA registers
DMA_CHAN_REGS = {
    "READ_ADDR_REG":       0x00|UINT32,
    "WRITE_ADDR_REG":      0x04|UINT32,
    "TRANS_COUNT_REG":     0x08|UINT32,
    "CTRL_TRIG_REG":       0x0c|UINT32,
    "CTRL_TRIG":          (0x0c,DMA_CTRL_TRIG_FIELDS)
}
# General DMA registers
DMA_DEVICE_REGS = {
    "INTR":               0x400|UINT32,
    "INTE0":              0x404|UINT32,
    "INTF0":              0x408|UINT32,
    "INTS0":              0x40c|UINT32,
    "INTE1":              0x414|UINT32,
    "INTF1":              0x418|UINT32,
    "INTS1":              0x41c|UINT32,
    "TIMER0":             0x420|UINT32,
    "TIMER1":             0x424|UINT32,
    "TIMER2":             0x428|UINT32,
    "TIMER3":             0x42c|UINT32,
    "MULTI_CHAN_TRIGGER": 0x430|UINT32,
    "SNIFF_CTRL":         0x434|UINT32,
    "SNIFF_DATA":         0x438|UINT32,
    "FIFO_LEVELS":        0x440|UINT32,
    "CHAN_ABORT":         0x444|UINT32
}
DMA_CHANS = [struct(DMA_BASE + n*DMA_CHAN_WIDTH, DMA_CHAN_REGS) for n in range(0,DMA_CHAN_COUNT)]
DMA_DEVICE = struct(DMA_BASE, DMA_DEVICE_REGS)

# GPIO status and control: RP2040 datasheet 2.19.6.1.10
GPIO_BASE       = 0x40014000
GPIO_CHAN_WIDTH = 0x08
GPIO_PIN_COUNT  = 30
GPIO_FUNC_SPI, GPIO_FUNC_UART, GPIO_FUNC_I2C = 1, 2, 3
GPIO_FUNC_PWM, GPIO_FUNC_SIO, GPIO_FUNC_PIO0 = 4, 5, 6
GPIO_FUNC_NULL = 0x1f
GPIO_STATUS_FIELDS = {
    "IRQTOPROC":  26<<BF_POS | 1<<BF_LEN | BFUINT32,
    "IRQFROMPAD": 24<<BF_POS | 1<<BF_LEN | BFUINT32,
    "INTOPERI":   19<<BF_POS | 1<<BF_LEN | BFUINT32,
    "INFROMPAD":  17<<BF_POS | 1<<BF_LEN | BFUINT32,
    "OETOPAD":    13<<BF_POS | 1<<BF_LEN | BFUINT32,
    "OEFROMPERI": 12<<BF_POS | 1<<BF_LEN | BFUINT32,
    "OUTTOPAD":    9<<BF_POS | 1<<BF_LEN | BFUINT32,
    "OUTFROMPERI": 8<<BF_POS | 1<<BF_LEN | BFUINT32
}
GPIO_CTRL_FIELDS = {
    "IRQOVER":    28<<BF_POS | 2<<BF_LEN | BFUINT32,
    "INOVER":     16<<BF_POS | 2<<BF_LEN | BFUINT32,
    "OEOVER":     12<<BF_POS | 2<<BF_LEN | BFUINT32,
    "OUTOVER":     8<<BF_POS | 2<<BF_LEN | BFUINT32,
    "FUNCSEL":     0<<BF_POS | 5<<BF_LEN | BFUINT32
}
GPIO_REGS = {
    "GPIO_STATUS_REG":     0x00|UINT32,
    "GPIO_STATUS":        (0x00,GPIO_STATUS_FIELDS),
    "GPIO_CTRL_REG":       0x04|UINT32,
    "GPIO_CTRL":          (0x04,GPIO_CTRL_FIELDS)
}
GPIO_PINS = [struct(GPIO_BASE + n*GPIO_CHAN_WIDTH, GPIO_REGS) for n in range(0,GPIO_PIN_COUNT)]

# PAD control: RP2040 datasheet 2.19.6.3
PAD_FIELDS = {
    "OD":          7<<BF_POS | 1<<BF_LEN | BFUINT32,
    "IE":          6<<BF_POS | 1<<BF_LEN | BFUINT32,
    "DRIVE":       4<<BF_POS | 2<<BF_LEN | BFUINT32,
    "PUE":         3<<BF_POS | 1<<BF_LEN | BFUINT32,
    "PDE":         2<<BF_POS | 1<<BF_LEN | BFUINT32,
    "SCHMITT":     1<<BF_POS | 1<<BF_LEN | BFUINT32,
    "SLEWFAST":    0<<BF_POS | 1<<BF_LEN | BFUINT32
}
PAD_REGS = {
    "PAD_REG":             0x00|UINT32,
    "PAD":                (0x00,PAD_FIELDS)
}
PAD_PINS =  [struct(PAD_BASE + n*PAD_PIN_WIDTH, PAD_REGS) for n in range(0,GPIO_PIN_COUNT)]

# ADC: RP2040 datasheet 4.9.6
ADC_CS_FIELDS = {
    "RROBIN":     16<<BF_POS | 5<<BF_LEN | BFUINT32,
    "AINSEL":     12<<BF_POS | 3<<BF_LEN | BFUINT32,
    "ERR_STICKY": 10<<BF_POS | 1<<BF_LEN | BFUINT32,
    "ERR":         9<<BF_POS | 1<<BF_LEN | BFUINT32,
    "READY":       8<<BF_POS | 1<<BF_LEN | BFUINT32,
    "START_MANY":  3<<BF_POS | 1<<BF_LEN | BFUINT32,
    "START_ONCE":  2<<BF_POS | 1<<BF_LEN | BFUINT32,
    "TS_EN":       1<<BF_POS | 1<<BF_LEN | BFUINT32,
    "EN":          0<<BF_POS | 1<<BF_LEN | BFUINT32
}
ADC_FCS_FIELDS = {
    "THRESH":     24<<BF_POS | 4<<BF_LEN | BFUINT32,
    "LEVEL":      16<<BF_POS | 4<<BF_LEN | BFUINT32,
    "OVER":       11<<BF_POS | 1<<BF_LEN | BFUINT32,
    "UNDER":      10<<BF_POS | 1<<BF_LEN | BFUINT32,
    "FULL":        9<<BF_POS | 1<<BF_LEN | BFUINT32,
    "EMPTY":       8<<BF_POS | 1<<BF_LEN | BFUINT32,
    "DREQ_EN":     3<<BF_POS | 1<<BF_LEN | BFUINT32,
    "ERR":         2<<BF_POS | 1<<BF_LEN | BFUINT32,
    "SHIFT":       1<<BF_POS | 1<<BF_LEN | BFUINT32,
    "EN":          0<<BF_POS | 1<<BF_LEN | BFUINT32,
}
ADC_DEVICE_REGS = {
    "CS_REG":              0x00|UINT32,
    "CS":                 (0x00,ADC_CS_FIELDS),
    "RESULT_REG":          0x04|UINT32,
    "FCS_REG":             0x08|UINT32,
    "FCS":                (0x08,ADC_FCS_FIELDS),
    "FIFO_REG":            0x0c|UINT32,
    "DIV_REG":             0x10|UINT32,
    "INTR_REG":            0x14|UINT32,
    "INTE_REG":            0x18|UINT32,
    "INTF_REG":            0x1c|UINT32,
    "INTS_REG":            0x20|UINT32
}
ADC_DEVICE = struct(ADC_BASE, ADC_DEVICE_REGS)
ADC_FIFO_ADDR = ADC_BASE + 0x0c

# PWM: RP2040 data sheet 4.5.3
PWM_DIV_FREE_RUNNING, PWM_DIV_B_HIGH, PWM_DIV_B_RISING, PWM_DIV_B_FALLING = 0, 1, 2, 3

PWM_CSR_FIELDS = {
    "PH_ADV":    7<<BF_POS | 1<<BF_LEN | BFUINT32,
    "PH_RET":    6<<BF_POS | 1<<BF_LEN | BFUINT32,
    "DIVMODE":   4<<BF_POS | 2<<BF_LEN | BFUINT32,
    "B_INV":     3<<BF_POS | 1<<BF_LEN | BFUINT32,
    "A_INV":     2<<BF_POS | 1<<BF_LEN | BFUINT32,
    "PH_CORRECT":1<<BF_POS | 1<<BF_LEN | BFUINT32,
    "EN":        0<<BF_POS | 1<<BF_LEN | BFUINT32
}
PWM_CC_FIELDS = {
    "A":    0<<BF_POS  | 16<<BF_LEN | BFUINT32,
    "B":    16<<BF_POS | 16<<BF_LEN | BFUINT32
}
PWM_CHAN_A, PWM_CHAN_B = 0, 1
PWM_DIV_FIELDS = {
    "INT":       4<<BF_POS | 8<<BF_LEN | BFUINT32,
    "FRAC":      0<<BF_POS | 4<<BF_LEN | BFUINT32,
}
PWM_SLICE_REGS = {
    "CSR_REG":             0x00|UINT32,
    "CSR":                (0x00,PWM_CSR_FIELDS),
    "DIV_REG":             0x04|UINT32,
    "DIV":                (0x04,PWM_DIV_FIELDS),
    "CTR_REG":             0x08|UINT32,
    "CC_REG":              0x0c|UINT32,
    "CC":                 (0x0C,PWM_CC_FIELDS),
    "TOP_REG":             0x10|UINT32
}
# General PWM registers
PWM_DEVICE_REGS = {
    "EN_REG":              0xa0|UINT32
}
PWM_DEVICE = struct(PWM_BASE, PWM_DEVICE_REGS)
PWM_SLICES = [struct(PWM_BASE + n*PWM_SLICE_WIDTH, PWM_SLICE_REGS) for n in range(0,PWM_SLICE_COUNT)]
PWM_EN_REG_ADDR = PWM_BASE + 0xa0

# Address of lower 32 bits of 1 MHz timer
TIMER_RAWL_ADDR = TIMER_BASE + 0x28

# Set GPIO pin function
def gpio_set_function(gpio, f):
    PAD_PINS[gpio].PAD.OD = 0;
    PAD_PINS[gpio].PAD.IE = 1;
    GPIO_PINS[gpio].GPIO_CTRL_REG = f

# Get address of variable (for DMA)
def addressof(var):
    return uctypes.addressof(var)

# Create 32-bit array (to receive DMA data)
def array32(size):
    return array.array('I', (0 for _ in range(size)))

# Class for RP2040 DMA
class DMA:
    instance_number = 0
    def __init__(self):
        self.chan_number = DMA.instance_number
        DMA.instance_number += 1
        self.DMA_DEVICE = DMA_DEVICE
        self.chan = DMA_CHANS[self.chan_number]
        self.abort()
        self.chan.READ_ADDR_REG = self.chan.WRITE_ADDR_REG = 0
        self.chan.TRANS_COUNT_REG = self.chan.CTRL_TRIG_REG =0
        self.chan.CTRL_TRIG.CHAIN_TO = self.chan_number
    # Cancel the current DMA transfer
    def abort(self):
        self.DMA_DEVICE.CHAN_ABORT = 1 << self.chan_number
        while self.DMA_DEVICE.CHAN_ABORT & (1 << self.chan_number):
            pass
    # Enable DMA transfer, or resume if already started
    def set_trigger(self, trigger):
        if trigger:
            self.chan.CTRL_TRIG.EN = 1
    # Enable/resume data transfer, or suspend it
    def set_enable(self, en):
        self.chan.CTRL_TRIG.EN = 1 if en else 0
    # Set size of data to be transferred: 8 / 16 / 32 bits
    def set_transfer_data_size(self, size):
        self.chan.CTRL_TRIG.DATA_SIZE = size
    # Set source address        
    def set_read_addr(self, addr, trigger=False):
        self.chan.READ_ADDR_REG = addr
        self.set_trigger(trigger)
    # Set destination address
    def set_write_addr(self, addr, trigger=False):
        self.chan.WRITE_ADDR_REG = addr
        self.set_trigger(trigger)
    # Set number of transfers        
    def set_trans_count(self, count, trigger=False):
        self.chan.TRANS_COUNT_REG = count
        self.set_trigger(trigger)
    # Enable/disable auto-increment of source address
    def set_read_increment(self, incr):
        self.chan.CTRL_TRIG.INCR_READ = 1 if incr else 0
    # Enable/disable auto-increment of destination address
    def set_write_increment(self, incr):
        self.chan.CTRL_TRIG.INCR_WRITE = 1 if incr else 0
    # Set signal that will request a transfer
    def set_dreq(self, dreq):
        self.chan.CTRL_TRIG.TREQ_SEL = dreq
    # Set destination address and count, and enable DMA
    def transfer_to_buffer_now(self, addr, count):
        self.set_write_addr(addressof(addr))
        self.set_trans_count(counter, True)
    # Return number of transfers that remain        
    def get_trans_count(self):
        return self.chan.TRANS_COUNT_REG
    # Print register values
    def print_regs(self):
        print("READ_ADDR  %08X, "      % self.chan.READ_ADDR_REG, end="")
        print("WRITE_ADDR %08X, "      % self.chan.WRITE_ADDR_REG, end="")
        print("TRANS_COUNT_REG %08X, " % self.chan.TRANS_COUNT_REG, end="")
        print("CTRL_TRIG_REG %08X"     % self.chan.CTRL_TRIG_REG)
        
# Class for RP2040 PWM
class PWM:
    def __init__(self, gpio, clock=125000000):
        self.gpio = gpio
        self.clock = clock
        self.slice_num = self.gpio_to_slice_num(gpio)
        self.slice = PWM_SLICES[self.slice_num]
        self.slice.CSR_REG = self.slice.DIV_REG = self.slice.CTR_REG = 0
        self.slice.CC_REG = self.slice.TOP_REG = 0
        self.set_clkdiv_int_frac(1, 0)
        self.set_wrap(0xffff)
    # Convert PIO number to slice number
    def gpio_to_slice_num(self, gpio):
        return (gpio >> 1) & 7
    # Convert GPIO number to channel number 0 or 1 (A or B)
    def gpio_to_channel(self, gpio):
        return(gpio & 1)
    # Set clock divisor (integer and fraction)
    def set_clkdiv_int_frac(self, i, f):
        self.slice.DIV.INT = i
        self.slice.DIV.FRAC = f
    # Set clock divisor (integer only)
    def set_clkdiv(self, i):
        self.set_clkdiv_int_frac(i, 0)
    # Set clocking mode
    def set_clkdiv_mode(self, mode):
        self.slice.CSR.DIVMODE = mode
    # Set wraparound value
    def set_wrap(self, w):
        self.slice.TOP_REG = w
    # Set initial counter value        
    def set_ctr(self, val):
        self.slice.CTR_REG = val
    # Set PWM comparison value
    def set_chan_level(self, chan, level):
        if chan:
            self.slice.CC.B = level
        else:
            self.slice.CC.A = level
    # Enable/disable phase-correct operation
    def set_phase_correct(self, correct):
        self.slice.CSR.PH_CORRECT = 1 if correct else 0
    # Enable/disable PWM        
    def set_enabled(self, en):
        self.slice.CSR.EN = en
    # Enable/disable multiple PWM slices, using bit-mask
    def set_enables(self, mask, en):
        if en:
            PWM_DEVICE.EN_REG |= mask
        else:
            PWM_DEVICE.EN_REG &= ~mask
    # Get current counter value
    def get_counter(self):
        return self.slice.CTR_REG
    # Calculate current PWM output frequency
    def get_output_frequency(self):
        div = float(self.slice.DIV.INT) + self.slice.DIV.FRAC / 16.0
        return self.clock / (div * (self.slice.TOP_REG + 1))
    # Return a data-request signal for this slice
    def get_dreq(self):
        return DREQ_PWM_WRAP0 + self.slice_num
    # Return address of CSR register, to be used by DMA
    def get_csr_address(self):
        return PWM_BASE + self.slice_num*PWM_SLICE_WIDTH
    # Print register values
    def print_regs(self):
        print("CSR %08X, " % self.slice.CSR_REG, end="")
        print("DIV %08X, " % self.slice.DIV_REG, end="")
        print("CTR %08X, " % self.slice.CTR_REG, end="")
        print("CC  %08X, " % self.slice.CC_REG,  end="")
        print("TOP %08X"   % self.slice.TOP_REG)
# EOF
