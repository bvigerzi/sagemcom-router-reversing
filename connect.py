import serial

baudRate = 115200

ser = serial.Serial('COM4')
print(ser.name)
ser.close()
