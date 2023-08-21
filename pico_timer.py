# Pico MicroPython: reciprocal (time-interval) frequency measurement
# See https://iosoft.blog/picofreq_python for description
#
# Copyright (c) 2021 Jeremy P Bentham
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
# v0.01 JPB 20/8/23 Adapted from pico_freq.py
# v0.02 JPB 21/8/23 Removed unneeded gate definitions

import time, pico_devices as devs

PWM_OUT_PIN, PWM_IN_PIN = 4, 3

# Output signal for testing
PWM_DIV = 250               # 125e6 / 125 = 500 kHz
PWM_WRAP = 50000 - 1        # 500 kHz / 50000 = 10 Hz
PWM_LEVEL = (PWM_WRAP+1)//2 # 50% PWM

NTIMES = 9                       # Number of time samples
time_data = devs.array32(NTIMES) # Time data

# Start a PWM output
def pwm_out(pin, div, level, wrap): 
    devs.gpio_set_function(pin, devs.GPIO_FUNC_PWM)
    pwm = devs.PWM(pin)
    pwm.set_clkdiv_int_frac(div, 0)
    pwm.set_wrap(wrap)
    pwm.set_chan_level(pwm.gpio_to_channel(pin), level)
    pwm.set_enabled(1)
    return pwm

# Initialise PWM as a timer (gpio must be odd number)
def timer_init(pin, rising=True):
    if pin & 1 == 0:
        print("Error: pulse counter must be on add GPIO pin")
    devs.gpio_set_function(pin, devs.GPIO_FUNC_PWM)
    pwm = devs.PWM(pin)
    pwm.set_clkdiv_mode(devs.PWM_DIV_B_RISING if rising else devs.PWM_DIV_B_FALLING)
    pwm.set_clkdiv(1)
    pwm.set_wrap(0);
    return pwm

# Initialise timer DMA
def timer_dma_init(timer):
    dma = devs.DMA()
    dma.set_transfer_data_size(devs.DMA_SIZE_32)
    dma.set_read_increment(False)
    dma.set_write_increment(True)
    dma.set_dreq(timer.get_dreq())
    dma.set_read_addr(devs.TIMER_RAWL_ADDR)
    return dma

# Start frequency measurment using gate
def timer_start(timer, dma):
    timer.set_ctr(0)
    timer.set_enabled(True)
    dma.abort()
    dma.set_write_addr(devs.addressof(time_data))
    dma.set_trans_count(NTIMES, True)

# Stop frequency measurment using gate
def timer_stop(timer):
    timer.set_enabled(False)
    
if __name__ == "__main__":
    test_signal = pwm_out(PWM_OUT_PIN, PWM_DIV, PWM_LEVEL, PWM_WRAP)
    
    timer_pwm = timer_init(PWM_IN_PIN)
    timer_dma = timer_dma_init(timer_pwm)
    
    timer_start(timer_pwm, timer_dma)
    time.sleep(1.0)
    timer_stop(timer_pwm)
    
    count = NTIMES - timer_dma.get_trans_count()
    data = time_data[0:count]
    diffs = [data[n]-data[n-1] for n in range(1, len(data))]
    total = sum(diffs)
    freq = (1e6 * len(diffs) / total) if total else 0
    print("%u samples, total %u us, freq %3.1f Hz" % (count, total, freq))
    
# EOF
