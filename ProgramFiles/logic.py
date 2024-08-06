import serial
import time
import numpy as np
import traceback
class App:
    def __init__(self, root):
        self.gaussSerial = None
        self.motorSerial = None

    #Check if both serial ports are connected
    #Return if True or False
    def has_serial_connect(self):
        gaussConnect = self.gaussSerial is not None
        motorConnect = self.motorSerial is not None
        return gaussConnect, motorConnect

  #Initialize connection to gaussmeter through serial port
  #Return serial connection link
    def serial_connect_gaussmeter(self, COM):
        try:
            # Test communication by sending a simple command
            serial_port = serial.Serial(COM, baudrate=9600, timeout=1, write_timeout=1, parity=serial.PARITY_ODD, bytesize=serial.SEVENBITS, stopbits=serial.STOPBITS_ONE)
            serial_port.write(b'*IDN?\r\n')
            time.sleep(0.1)
            response = serial_port.readline().decode()
            if str(response[0:4]) == "LSCI":
                self.serial_gauss_bool = True
                self.gaussSerial = serial_port
        except Exception as e:
            print(f'{e}\nAn error has occured. See above...')

  #Initialize connection to gaussmeter through serial port
    import serial

    def serial_connect_motor(self, COM):
        try:
            serial_port = serial.Serial(COM, baudrate=9600, timeout=1)
            serial_port.write(b'F\r')
            serial_port.write(b'N\r')
            serial_port.write(b'C\r')
            serial_port.write(b'setM1M6\r')
            serial_port.write(b'getM1M\r')

            response1_raw = serial_port.readline().decode().strip()
            print(f'Raw Motor 1 response: {response1_raw}')
            response1 = float(response1_raw)
            print(f'Motor 1: {response1}')

            serial_port.write(b'setM2M4\r')
            serial_port.write(b'getM2M\r')

            response2_raw = serial_port.readline().decode().strip()
            print(f'Raw Motor 2 response: {response2_raw}')
            response2 = float(response2_raw)
            print(f'Motor 2: {response2}')

            serial_port.write(b'setM3M4\r')
            serial_port.write(b'getM3M\r')

            response3_raw = serial_port.readline().decode().strip()
            print(f'Raw Motor 3 response: {response3_raw}')
            response3 = float(response3_raw)
            print(f'Motor 3: {response3}')

            # Condition for if the correct motor COM has been found and responding correctly
            if response1 == 6.0 and response2 == 4.0 and response3 == 4.0:
                print('Serial motor connection made')
                self.motorSerial = serial_port
        except serial.SerialException as e:
            print(f'Serial error: {e}')
        except ValueError as e:
            print(f'Value error: {e}')
        except Exception as e:
            print(f'Unexpected error: {e}\nAn error has occurred. See above...')
            print(traceback.print_exc())


    def moveMotor(self, distance, axisStr):
        
        axis_map = {"X": 1, "Y": 2, "Z": 3}
        axis = axis_map.get(axisStr, 0)
        #CHANGE THIS
        try:
            inches = distance / 2.54
            print(f'distance:{distance}')
            steps = int(inches / 0.00025)
            commands = [b'C\r', f'I{axis}M{steps}\r\n'.encode(), b'R\r']
            for command in commands:
                self.motorSerial.write(command)
            time.sleep(0.05)
        except Exception as e:
            print(f'{e}\nAn error has occurred. See above...')

    def isMotorMoving(self):
        self.motorSerial.write(b'V\r')
        status = str(self.motorSerial.readline().decode())
        if status == "B":
            return True
        else:
            return False

    def getMagneticField(self):
        command = 'CHNL X\r\n'
        self.gaussSerial.write(command.encode())
        command = 'RANGE 0\r\n'
        self.gaussSerial.write(command.encode())
        command = 'FIELD?\r\n'
        self.gaussSerial.write(command.encode())
        time.sleep(0.05)
        self.gaussSerial.write(command.encode())
        command = 'FIELDM?\r\n'
        x = float(self.gaussSerial.readline().decode())*10

        command = 'CHNL Y\r\n'
        self.gaussSerial.write(command.encode())
        command = 'RANGE 0\r\n'
        self.gaussSerial.write(command.encode())
        command = 'FIELD?\r\n'
        self.gaussSerial.write(command.encode())
        time.sleep(0.05)
        self.gaussSerial.write(command.encode())
        command = 'FIELDM?\r\n'
        y = float(self.gaussSerial.readline().decode())*10

        command = 'CHNL Z\r\n'
        self.gaussSerial.write(command.encode())
        command = 'RANGE 0\r\n'
        self.gaussSerial.write(command.encode())
        command = 'FIELD?\r\n'
        self.gaussSerial.write(command.encode())
        time.sleep(0.05)
        self.gaussSerial.write(command.encode())
        command = 'FIELDM?\r\n'
        z = float(self.gaussSerial.readline().decode())*10

        magnitudeField = np.sqrt(x**2+y**2+z**2)
        return x, y, z, float(magnitudeField)

    def closeCOMports(self):
        print(f'motor serial open: {self.motorSerial.is_open}')
        try:
            if self.gaussSerial.is_open:
                self.gaussSerial.close()
            if self.motorSerial.is_open:
                self.motorSerial.write(b'Q\r')
            return True
        except Exception as e:
            print(f'ERROR: {e}')
            return False

    def endPlot(self):
        self.motorSerial.write(b'Q\r')
        self.closeCOMports()

def main():
  pass
    
if __name__ == "__main__":
  main()
