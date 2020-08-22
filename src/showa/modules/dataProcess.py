from time import sleep
from showa.lib import logs
from showa.modules import config, cmdMake
import time


class Error(Exception):
    """Base class for other exceptions"""
    pass


class portDisconnectError(Error):
    """Raised when b'' is detected."""
    pass


def resetElapsedTime():
    time_start = time.perf_counter()
    return(time_start)


def elapsedTime(x):
    time_elapsed = time.perf_counter() - x
    return(time_elapsed)


# read whatever available in buffer and decoded bytes
def read_serial(ser):
    # bytesToRead = ser.inWaiting()
    readback = ser.read(18)
    return readback.decode()


def read_setup(ser):
    readback = ser.read(6)
    return readback.decode()


# read and return raw bytes
def read_checker(ser):
    # bytestoCheck = ser.inWaiting()
    checkByte = ser.read(10)
    return(checkByte)


def setupCmd(dat5):
    i = "036"
    j = "0B6"
    a = {}
    a['dat1'] = cmdMake.cmdStr(i, "00")
    a['dat2'] = cmdMake.cmdStr(i, "03")
    a['dat3'] = cmdMake.cmdStr(i, "02")
    a['dat4'] = cmdMake.cmdStr(i, "01")
    a['dat5'] = dat5
    a['dat6'] = cmdMake.cmdStr(j, "010004")
    a['dat7'] = cmdMake.cmdStr(j, "028182")
    a['dat8'] = cmdMake.cmdStr(j, "810000")
    a['dat9'] = cmdMake.cmdStr(j, "820000")
    a['dat10'] = cmdMake.cmdStr(j, "830000")
    a['dat11'] = cmdMake.cmdStr(j, "840000")
    a['dat12'] = cmdMake.cmdStr(j, "850000")
    a['dat13'] = cmdMake.cmdStr(j, "860000")
    a['dat14'] = cmdMake.cmdStr(j, "870000")
    a['dat15'] = cmdMake.cmdStr(j, "880000")
    a['dat16'] = cmdMake.cmdStr(j, "101EA5")
    listy = list(a.values())
    return(listy)


# write command and data in serial string format
def write_speed(speed1, speed2, comPort, ser):
    cleanList = []
    ser.reset_input_buffer()
    ser.write(cmdMake.dummyCmd())
    sleep(config.delay1)
    print(read_setup(ser))
    print("setting up for speed...")
    for i in setupCmd(speed1):
        ser.write(i)
        sleep(config.delay1)
        x = read_setup(ser)
        print(x)
    print("checking ZSP for speed...")
    ser.reset_input_buffer()
    # start timer
    x = resetElapsedTime()
    ser.reset_input_buffer()
    ser.write(cmdMake.checkerCmd())
    sleep(config.delay1)
    y = read_checker(ser)
    print(y)
    while y == b'':
        ser.reset_input_buffer()
        ser.write(cmdMake.checkerCmd())
        sleep(config.delay1)
        y = read_checker(ser)
        print(y)
        if(elapsedTime(x) >= config.max_duration):
            config.unresponsiveList.append(comPort)
            logs.logError("Port is not working", includeErrorLine=True)
            raise portDisconnectError
            break
    if y != b'':
        x = resetElapsedTime()
        while y != bytearray(b'\x020A0000\x0334'):
            ser.reset_input_buffer()
            ser.write(cmdMake.checkerCmd())
            sleep(config.delay1)
            y = read_checker(ser)
            print(y)
            if(elapsedTime(x) >= config.max_duration):
                config.carrierStopCount.append(comPort)
                logs.logError("The carrier is not moving.",
                              includeErrorLine=True)
                raise Exception("The carrier is not moving.")
                break
        ser.reset_input_buffer()
        ser.write(speed2)
        sleep(config.delay1)
        read_setup(ser)
        ser.reset_input_buffer()
        print("Fetching data")
        k = 0
        while k < 257:
            for i in cmdMake.fetchCmd():
                ser.write(i)
                sleep(config.delay1)
                x = read_serial(ser)
                print(x)
                while len(x) is None or len(x) > 18 and k < 257:
                    x = read_serial(ser)
                    if len(x) != 18:
                        x = read_serial(ser)
                    elif len(x) == 18:
                        break
                k = k+1
                cleanList.append(x)
            if k == 256:
                break
    return (cleanList)


# convert hexstring to signed decimal
def decodeOut(hexstr, bits):
    value = int(hexstr, 16)
    if value & (1 << (bits-1)):
        value -= 1 << bits
    return(value)


def cleanSpeeddata(inComing):
    clean_data = []
    for j in inComing:
        # print(j)
        if j != '' and len(j) < 20:
            x = j[:-3]
            s = str(x[7:])
            if s != '':
                a = decodeOut(s, config.decodeBits)
                a = (a/100000)*1.55
                clean_data.append(str(a))
            else:
                pass
        else:
            pass
    return (clean_data)


def cleanTorquedata(inComing):
    clean_data = []
    for j in inComing:
        # print(j)
        if j != '' and len(j) < 20:
            x = j[:-3]
            s = str(x[7:])
            if s != '':
                a = decodeOut(s, config.decodeBits)
                a = a*1.5/1000000
                clean_data.append(str(a))
            else:
                pass
        else:
            pass
    return (clean_data)
