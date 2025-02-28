# led_signal.py
> used to create recurring function just like a thread signal

-   start_blinking(`[millisecond]`)
    -   default value `500`
-   stop_blinking()
-   led.value(`[0]`)
-   led.value(`[1]`)
```
from led_signal import LEDSignal

signal = LEDSignal(pin=2)
```