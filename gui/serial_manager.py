import serial
# Xijun is still debugging this file
class SerialManager:
    _instance = None

    def __new__(cls, port='COM8', baudrate=115200, timeout=1):
        if cls._instance is None:
            cls._instance = super(SerialManager, cls).__new__(cls)
            try:
                cls._instance.ser = serial.Serial(port, baudrate, timeout=timeout)
            except serial.SerialException as e:
                print(f"Error opening serial port: {e}")
                cls._instance.ser = None
        return cls._instance

    def read_line(self):
        if self.ser and self.ser.in_waiting > 0:
            line = self.ser.readline().decode('utf-8').rstrip()
            return line
        return None

    def close(self):
        if self.ser:
            self.ser.close()
