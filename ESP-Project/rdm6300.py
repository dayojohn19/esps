from machine import RTC, UART
import time
from configs.configs import clock_scl, clock_sda, clock_sqw , alarm, doorservoPin, rdm6300Pin, sim_tx
from clockModule import Clock, updateClock
from led_signal import LEDSignal
import gc
import json
import _thread
import select
from textwriter import textWriter
from main_sub import Battery, Power, Train






