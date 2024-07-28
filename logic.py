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
  def serial_connect_motor(self, COM):
      def send_command(command):
          serial_port.write(command)
          return float(serial_port.readline().decode())

      try:
          serial_port = serial.Serial(COM, baudrate=9600, timeout=1)
          init_commands = [b'F\r', b'N\r', b'C\r']
          for cmd in init_commands:
              serial_port.write(cmd)
          motor_commands = [
              (b'setM1M6\r', b'getM1M\r'),
              (b'setM2M4\r', b'getM2M\r'),
              (b'setM3M4\r', b'getM3M\r')
          ]
          responses = [send_command(set_cmd) for set_cmd, get_cmd in motor_commands]
          for i, response in enumerate(responses, 1):
              print(f'Motor {i}: {response}')
          
          if responses == [6.0, 4.0, 4.0]:
              self.motorSerial = serial_port
      except Exception as e:
          print(f'{e}\nAn error has occurred. See above...')

  def moveMotor(self, distance, axisStr):
    axis_map = {"X": 0, "Y": 1, "Z": 2}
    axis = axis_map.get(axisStr, 0)

    try:
        inches = distance / 2.54
        steps = int(inches / 0.00025)
        commands = [b'C\r', f'I{axis}M{steps}\r\n'.encode(), b'R\r']
        for command in commands:
            self.motorSerial.write(command)
        time.sleep(0.2)
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
      def get_field(channel):
          commands = [
              f'CHNL {channel}\r\n',
              'RANGE 0\r\n',
              'FIELD?\r\n',
              'FIELD?\r\n',  # This command is repeated in the original code
              'FIELDM?\r\n'
          ]
          for cmd in commands:
              self.gaussSerial.write(cmd.encode())
              if cmd == 'FIELD?\r\n':
                  time.sleep(0.05)
          return float(self.gaussSerial.readline().decode())

      x = get_field('X')
      y = get_field('Y')
      z = get_field('Z')

      magnitudeField = np.sqrt(x**2 + y**2 + z**2)
      return magnitudeField

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

def main():
  pass
    
if __name__ == "__main__":
  main()
