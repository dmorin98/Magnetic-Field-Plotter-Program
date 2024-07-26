import serial
import time
import numpy as np

class App:
  def __init__(self, root):
    self.gaussSerial = None
    self.motorSerial = None

  #Check if both serial ports are connected
  #Return if True or False
  def has_serial_connect(self):
    if self.gaussSerial == None:
      gaussConnect = False
    else:
      gaussConnect = True
    if self.motorSerial == None:
      motorConnect = False
    else:
      motorConnect = True
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
  #Return serial connection link
  def serial_connect_motor(self, COM):
    try:
      serial_port = serial.Serial('COM5', baudrate=9600, timeout=1)
      serial_port.write(b'F\r')
      serial_port.write(b'N\r')
      serial_port.write(b'C\r')
      serial_port.write(b'setM1M6\r')
      serial_port.write(b'getM1M\r')
      response1 = float(serial_port.readline().decode())
      print(f'Motor 1: {response1}')
      serial_port.write(b'setM2M4\r')
      serial_port.write(b'getM2M\r')
      response2 = float(serial_port.readline().decode())
      print(f'Motor 2: {response2}')
      serial_port.write(b'setM3M4\r')
      serial_port.write(b'getM3M\r')
      response3 = float(serial_port.readline().decode())
      print(f'Motor 3: {response3}')

      #Condition for if the correct motor COM has been found and responding correctly
      if response1 == 6.0 and response2 == 4.0 and response3 == 4.0:
        self.motorSerial = serial_port
    except Exception as e:
      print(f'{e}\nAn error has occured. See above...')

  def moveMotor(self, distance, axis):
    try:
      inches = distance/2.54
      steps = int(inches/.00025)
      self.motorSerial.write(b'C\r')
      self.motorSerial.write((f'I{str(axis)}M{str(steps)}\r\n').encode())
      self.motorSerial.write(b'R\r')
      time.sleep(0.2)
    except Exception as e:
      print(f'{e}\nAn error has occured. See above...')

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
    x = float(self.gaussSerial.readline().decode())

    command = 'CHNL Y\r\n'
    self.gaussSerial.write(command.encode())
    command = 'RANGE 0\r\n'
    self.gaussSerial.write(command.encode())
    command = 'FIELD?\r\n'
    self.gaussSerial.write(command.encode())
    time.sleep(0.05)
    self.gaussSerial.write(command.encode())
    command = 'FIELDM?\r\n'
    y = float(self.gaussSerial.readline().decode())

    command = 'CHNL Z\r\n'
    self.gaussSerial.write(command.encode())
    command = 'RANGE 0\r\n'
    self.gaussSerial.write(command.encode())
    command = 'FIELD?\r\n'
    self.gaussSerial.write(command.encode())
    time.sleep(0.05)
    self.gaussSerial.write(command.encode())
    command = 'FIELDM?\r\n'
    z = float(self.gaussSerial.readline().decode())
     
    magnitudeField = np.sqrt(x**2+y**2+z**2)
    return float(magnitudeField)

  def closeCOMports(self):
    print(f'motor serial open:{str(self.motorSerial.is_open)}')
    try:
      if self.gaussSerial.is_open:
        self.gaussSerial.close()
      if self.motorSerial.is_open:
        self.motorSerial.write(b'Q\r')
        #self.motorSerial.close()

      return True
    except Exception as e:
      print(f'ERROR:{e}')
      return False

  def endPlot(self):
    self.motorSerial.write(b'Q\r')

def main():
  pass
    
if __name__ == "__main__":
  main()
