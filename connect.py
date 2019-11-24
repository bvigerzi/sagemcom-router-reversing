import serial
import configparser


def openPort():
    baudRate = 115200

    ser = serial.Serial('COM4', baudRate, timeout=1)
    return ser


def writeToPort(ser, message):
    message += '\n'
    ser.write(message.encode('utf-8'))


def readBuffer(ser):
    maxConsecutiveEmptyBytes = 5
    currConsecEmptyBytes = 0
    bufferSize = 1024
    allReadBytes = bytearray()
    while True:
        readBytes = ser.read(bufferSize)
        if len(readBytes) == 0:
            currConsecEmptyBytes = currConsecEmptyBytes + 1
        else:
            currConsecEmptyBytes = 0
            allReadBytes += readBytes
        if currConsecEmptyBytes >= maxConsecutiveEmptyBytes:
            break
        # print(readBytes.decode('utf-8'))
    return allReadBytes


config = configparser.ConfigParser()
config.read('secret_info.ini')
serialConnection = openPort()
print(readBuffer(serialConnection).decode('utf-8'))
print('Finished reading the buffer... ready to write')
writeToPort(serialConnection, '')
print(readBuffer(serialConnection).decode('utf-8'))
writeToPort(serialConnection, config['LOGIN_DETAILS']['login'])
print(readBuffer(serialConnection).decode('utf-8'))
writeToPort(serialConnection, config['LOGIN_DETAILS']['password'])
print(readBuffer(serialConnection).decode('utf-8'))
writeToPort(serialConnection, 'cat /etc/passwd')
print(readBuffer(serialConnection).decode('utf-8'))
