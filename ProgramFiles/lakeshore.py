import serial
import serial.tools.list_ports
import time

def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

# List available serial ports
print("Available ports:", list_serial_ports())

try:
    # Set up the serial connection with the correct settings
    ser = serial.Serial(
        port='COM10',            # Update this to your actual port
        baudrate=9600,
        timeout=2,
        bytesize=serial.SEVENBITS,
        parity=serial.PARITY_ODD,
        stopbits=serial.STOPBITS_ONE
    )

    if ser.is_open:
        print(f"Successfully connected to {ser.name}")

    # Send the *IDN? command to the Gaussmeter
    command = '*IDN?\r\n'  # Ensure the command ends with CR LF
    ser.write(command.encode())

    # Wait for the device to respond
    time.sleep(0.1)

    # Read the response from the Gaussmeter
    response = ser.readline().decode()
    print('Response:', response)

    command = 'CHNL X\r\n'
    ser.write(command.encode())
    command = 'RANGE 0\r\n'
    ser.write(command.encode())
    command = 'FIELD?\r\n'
    ser.write(command.encode())
    time.sleep(0.1)
    ser.write(command.encode())
    command = 'FIELDM?\r\n'

    
    response = ser.readline().decode()
    print(f'Field: {float(response)}')

except serial.SerialException as e:
    print(f"Error: {e}")
