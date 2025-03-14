#  ldr_pin for esp32
from machine import ADC
ldr_pin = 34
ldr = ADC(Pin(ldr_pin))
ldr.atten(ADC.ATTN_11DB)
ldr.read()