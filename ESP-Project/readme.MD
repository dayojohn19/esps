

##     Pins Map
0   batteryPin      --- Divider Resistor on 5v and Ground __ down to 1.2v using ADC.atten=2
1   doorservoPin    ___ warning please change this to other pin it is connected on built in LED
2   gatePin
3   BatteryMotorPin --- Divider Resistor with Diode on High Current VCC and ground down to 1v ussing ADC.atten=2
4   clock_sqw       --- Resistor on 3.3v ___ to keep the pin high on for the sleep mode DS3231 SQW pin only work pull low
5   doorPin
6   clock_sda
7   clock_scl       --- Changed to Pin 7 ___ Pin7 naturally Low
8   ledsignalPin
9   feederPin
10  groundPin
20  sim_tx
21  sim_rx
## Note See Configs.configs.py for updated pins



# Mechanics

## Power Supply 
-   TP4056 Output to XL0009 Converter - Relay NO

### Relay
-   NO  -   Charger
-   NC  -   VCC High input 
-   Common  -   Battery

Charger on NO relay
VCC High Current input on NC relay
High Current Battery on Common

Module 5v and ground on relay driven by 2N222 NPN Transistor 

! Added 100uf on Module VCC input and ground to stabilize the Wifi
! Added 100uf on Sim Module
! Sim and RTC are Connected on High Current 
! RTC module added added 100ohm resistor on vcc input
! Added 2200uf on High Current

