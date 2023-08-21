# Pico MicroPython: using PWM as pulse counter
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
# v0.01 JPB 15/8/23
# v0.02 JPB 15/8/25 Added DMA abort
#                   Clear PWM counter before running as timer
# v0.03 JPB 19/8/23 Renamed rp_pwm_counter.py to pico_counter.py
# v0.04 JPB 20/8/23 Switched input from pin 7 to pin 3

import time, pico_devices as devs

PWM_OUT_PIN, PWM_IN_PIN = 4, 3

PWM_DIV = 125               # 125e6 / 125 = 1 MHz
PWM_WRAP = 9                # 1 MHz / (9 + 1) = 100 kHz
PWM_LEVEL = (PWM_WRAP+1)//2 # 50% PWM

ext_data = devs.array32(1)  # Dummy array for extended counter

# Start a PWM output
def pwm_out(pin, div, level, wrap): 
    devs.gpio_set_function(pin, devs.GPIO_FUNC_PWM)
    pwm = devs.PWM(pin)
    pwm.set_clkdiv_int_frac(div, 0)
    pwm.set_wrap(wrap)
    pwm.set_chan_level(pwm.gpio_to_channel(pin), level)
    pwm.set_enabled(1)
    return pwm

# Initialise PWM as a pulse counter (gpio must be odd number)
def pulse_counter_init(pin, rising=True):
    if pin & 1 == 0:
        print("Error: pulse counter must be on add GPIO pin")
    devs.gpio_set_function(pin, devs.GPIO_FUNC_PWM)
    pwm = devs.PWM(pin)
    pwm.set_clkdiv_mode(devs.PWM_DIV_B_RISING if rising else devs.PWM_DIV_B_FALLING)
    pwm.set_clkdiv(1)
    return pwm

# Enable or disable pulse counter
def pulse_counter_enable(ctr, en):
    if en:
        ctr.set_ctr(0)
    ctr.set_enabled(en)

# Get value of pulse counter
def pulse_counter_value(ctr):
    return ctr.get_counter()

# Use DMA to extend pulse counter to 32 bits
def pulse_counter_ext_init(ctr):
    ctr.set_enabled(False)
    ctr.set_wrap(0)
    ctr.set_ctr(0)
    dma = devs.DMA()
    dma.set_transfer_data_size(devs.DMA_SIZE_8)
    dma.set_read_increment(False)
    dma.set_write_increment(False)
    dma.set_read_addr(devs.addressof(ext_data))
    dma.set_write_addr(devs.addressof(ext_data))
    dma.set_dreq(ctr.get_dreq())
    ctr.set_enabled(True)
    return dma

# Start the extended pulse counter
def pulse_counter_ext_start(ctr_dma):
    ctr_dma.abort()
    ctr_dma.set_trans_count(0xffffffff, True)
 
# Stop the extended pulse counter
def pulse_counter_ext_stop(ctr_dma):
    ctr_dma.set_enable(False)
 
# Return value from extended pulse counter
def pulse_counter_ext_value(ctr_dma):
    return 0xffffffff - ctr_dma.get_trans_count()

if __name__ == "__main__":
    test_signal = pwm_out(PWM_OUT_PIN, PWM_DIV, PWM_LEVEL, PWM_WRAP)
    print("PWM output %3.1f kHz on GPIO %u" % (test_signal.get_output_frequency()/1000.0, PWM_OUT_PIN))

    counter = pulse_counter_init(PWM_IN_PIN)
    pulse_counter_enable(counter, True)
    time.sleep(0.1)
    pulse_counter_enable(counter, False)
    val = pulse_counter_value(counter)
    print("Sleep 0.1s, count %u" % val)

    counter_dma = pulse_counter_ext_init(counter)
    pulse_counter_ext_start(counter_dma)
    time.sleep(0.1)
    val = pulse_counter_ext_value(counter_dma)
    pulse_counter_ext_stop(counter_dma)
    print("Sleep 0.1s, ext count %u" % val)

    pulse_counter_ext_start(counter_dma)
    time.sleep(1.0)
    val = pulse_counter_ext_value(counter_dma)
    pulse_counter_ext_stop(counter_dma)
    print("Sleep 1.0s, ext count %u" % val)

# EOF
