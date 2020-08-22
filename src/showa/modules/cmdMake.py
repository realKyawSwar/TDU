import binascii


# ASCII to HEX conversion
def convertAscii_Hex(cd):
    x = bytes(cd, 'utf-8')
    y = str(binascii.hexlify(x), 'ascii')
    # cd = bytearray(' '.join(a+b for a,b in zip(y[::2], y[1::2])), 'utf-8')
    cd = ' '.join(a+b for a, b in zip(y[::2], y[1::2]))
    return(cd)


# Create command string from command input and data input,
# Checksum is added
def cmdStr(inputC, inputD):
    SOH = '01 '
    STX = ' 02 '
    ETX = ' 03'
    a = convertAscii_Hex(inputC).split()
    b = convertAscii_Hex(inputD).split()
    for i in range(0, len(a)):
        a[i] = int(a[i], 16)
    for i in range(0, len(b)):
        b[i] = int(b[i], 16)
    total = int(STX, 16)+int(ETX, 16) + sum(a) + sum(b)
    dummy1 = str(hex(total))
    checksum = convertAscii_Hex(''.join((dummy1[-2:]).split()).upper())
    stringy = bytearray.fromhex(SOH+convertAscii_Hex(inputC)+STX +
                                convertAscii_Hex(inputD)+ETX+" "+checksum)
    return(stringy)


def checkerCmd():
    return cmdStr("036", "00")


def dummyCmd():
    return cmdStr("005", "00")


def fetchCmd():
    data_str = ([hex(i)[2:].zfill(2).upper() for i in range(256)])
    fetchCmdLst = []
    for i in data_str:
        fetchCmd = cmdStr("037", i)
        fetchCmdLst.append(fetchCmd)
    return(fetchCmdLst)


def main():
    print(speedCmd2())



if __name__ == '__main__':
    main()
