# PicoFreq project: accurate frequency measurement using an RP2040

cmake_minimum_required(VERSION 3.12)
include(pico_sdk_import.cmake)

project(picofreq C CXX ASM)

pico_sdk_init()

# Enable compiler warnings
add_compile_options(-Wall)

add_executable(picofreq picofreq.c)

target_link_libraries(picofreq pico_stdlib hardware_pwm hardware_dma)
pico_add_extra_outputs(picofreq)

# EOF
