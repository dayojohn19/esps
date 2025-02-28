import time
Vcc = 3.3  # Supply voltage
R1 = 1000  # Resistor between Vcc and A0 (1kΩ)
R2 = 1000  # Resistor between A0 and GND (1kΩ)

# Function to read ADC and calculate voltage
def get_voltage():
    # Read ADC value (0 to 1023 for 10-bit resolution)
    sensor_value = 637.5
    
    # Calculate the voltage on A0 (scale from 0-1023 to 0-3.3V)
    voltage_at_a0 = (sensor_value * Vcc) / 1023.0
    
    # Since both resistors are equal (1kΩ), the voltage at A0 will be half of Vcc
    # Voltage divider formula: V_out = V_in * (R2 / (R1 + R2))
    # Since R1 == R2, V_out = V_in / 2
    voltage = voltage_at_a0 * 2  # Multiply by 2 to account for the voltage divider
    
    return voltage

# Continuously read and display the voltage
while True:
    voltage = get_voltage()
    print(f"Voltage at A0: {voltage:.2f}V")
    time.sleep(1)  # Wait 1 second before the next reading