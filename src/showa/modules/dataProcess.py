from time import sleep
from showa.lib import logs
from showa.modules import config, cmdMake
import time
# import config, cmdMake


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


# write command and data in serial string format
def write_data(comPort, ser):
    cleanList = []
    setupCmd = [bytearray(b'\x01036\x0200\x03FE'),
                bytearray(b'\x01036\x0203\x0301'),
                bytearray(b'\x01036\x0202\x0300'),
                bytearray(b'\x01036\x0201\x03FF'),
                bytearray(b'\x010B6\x020082FFFFFF00FF\x0307'),
                bytearray(b'\x010B6\x02010004\x03D2'),
                bytearray(b'\x010B6\x02028182\x03E2'),
                bytearray(b'\x010B6\x02810000\x03D6'),
                bytearray(b'\x010B6\x02820000\x03D7'),
                bytearray(b'\x010B6\x02830000\x03D8'),
                bytearray(b'\x010B6\x02840000\x03D9'),
                bytearray(b'\x010B6\x02850000\x03DA'),
                bytearray(b'\x010B6\x02860000\x03DB'),
                bytearray(b'\x010B6\x02870000\x03DC'),
                bytearray(b'\x010B6\x02880000\x03DD'),
                bytearray(b'\x010B6\x02101EA5\x03FA')]
    speed2 = bytearray(b'\x01036\x0281\x0307')
    ser.reset_input_buffer()
    ser.write(cmdMake.dummyCmd())
    sleep(config.delay1)
    print(read_setup(ser))
    print("setting up...")
    for i in setupCmd:
        ser.write(i)
        sleep(config.delay1)
        x = read_setup(ser)
        print(x)
    print("checking ZSP...")
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


def cleanSpeedata(inComing):
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

def main():
    speed1  = bytearray(b'\x010B6\x020082FFFFFF00FF\x0307')
    print(setupCmd(speed1))



if __name__ == '__main__':
    main()
