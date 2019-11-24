import serial


def openPort():
    baudRate = 115200

    ser = serial.Serial('COM4', baudRate, timeout=1)
    return ser


def readBuffer(ser):
    maxConsecutiveEmptyBytes = 5
    currConsecEmptyBytes = 0
    bufferSize = 1024
    while True:
        readBytes = ser.read(bufferSize)
        if len(readBytes) == 0:
            currConsecEmptyBytes = currConsecEmptyBytes + 1
        else:
            currConsecEmptyBytes = 0
        if currConsecEmptyBytes >= maxConsecutiveEmptyBytes:
            break
        print(readBytes.decode('utf-8'))


serialConnection = openPort()
readBuffer(serialConnection)
print('Finished reading the buffer... ready to write')
