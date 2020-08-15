from showa.modules import config
# import config
import serial


def portCreate(lineNumber):
    firstSetMaxChamber = 1
    secondSetMinChamber = 31
    # set secondSetMaxChamber to 42 if want HLL and CTC
    secondSetMaxChamber = 40
    chamberToRemove = []

    if str(lineNumber) == '201':
        firstSetMaxChamber = 23
        chamberToRemove = [38]
    elif str(lineNumber) == '202':
        firstSetMaxChamber = 22
    elif str(lineNumber) == '205':
        firstSetMaxChamber = 27
        chamberToRemove = [38]
    else:
        firstSetMaxChamber = 29
        chamberToRemove = [38]
    portList = list(range(1, firstSetMaxChamber))
    portList += list(range(secondSetMinChamber, secondSetMaxChamber))
    for c in chamberToRemove:
        portList.remove(c)
    return portList


# create socket from ports of given line and return list
def socketCreate(line):
    socketList = []
    listy = portCreate(line)
    for i in listy:
        i += 5000
        socketList.append(i)
    return(socketList)


# Need to change for expansion line
def chNameCreate(line, port):
    try:
        # readVal = int(comPort.strip("COM"))
        # port = readVal - config.comOffset
        pStr = ""
        x = line
        if x == "201":
            lstCh = 22
            offset = 30-lstCh
            if port <= lstCh:
                pStr = "P"+str(port)
            elif port <= lstCh+offset+4 and port > lstCh+offset:
                pStr = "C"+str(port-(lstCh+offset))
            elif port == 35:
                pStr = "Load"
            elif port == 36:
                pStr = "Unload"
            elif port == 37:
                pStr = "P0"
            elif port == 39:
                pStr = "VTC"
            elif port == 38:
                pStr = "Not in Use"
                raise Exception("Invalid Chamber")
            elif port == 40:
                pStr = "HLL"
            elif port == 41:
                pStr = "CTC"
            else:
                pStr = "Invalid"
                raise Exception("Invalid Chamber")
        elif x == "202":
            lstCh = 21
            offset = 30-lstCh
            if port <= lstCh:
                pStr = "P"+str(port)
            elif port <= lstCh+offset+4 and port > lstCh+offset:
                pStr = "C"+str(port-(lstCh+offset))
            elif port == 35:
                pStr = "Load"
            elif port == 36:
                pStr = "Unload"
            elif port == 37:
                pStr = "P0-1"
            elif port == 38:
                pStr = "P0-2"
            elif port == 39:
                pStr = "VTC"
            elif port == 40:
                pStr = "HLL"
            elif port == 41:
                pStr = "CTC"
            else:
                pStr = "Invalid"
                raise Exception("Invalid Chamber")
        elif x == "205":
            lstCh = 26
            offset = 30-lstCh
            if port <= lstCh:
                pStr = "P"+str(port)
            elif port <= lstCh+offset+4 and port > lstCh+offset:
                pStr = "C"+str(port-(lstCh+offset))
            elif port == 35:
                pStr = "Load"
            elif port == 36:
                pStr = "Unload"
            elif port == 37:
                pStr = "P0"
            elif port == 39:
                pStr = "VTC"
            elif port == 38:
                pStr = "Not in use"
                raise Exception("Invalid Chamber")
            elif port == 40:
                pStr = "HLL"
            elif port == 41:
                pStr = "CTC"
            else:
                pStr = "Invalid"
                raise Exception("Invalid Chamber")
        else:
            lstCh = 28
            offset = 30-lstCh
            if port <= lstCh:
                pStr = "P"+str(port)
            elif port <= lstCh+offset+4 and port > lstCh+offset:
                pStr = "C"+str(port-(lstCh+offset))
            elif port == 35:
                pStr = "Load"
            elif port == 36:
                pStr = "Unload"
            elif port == 37:
                pStr = "P0"
            elif port == 39:
                pStr = "VTC"
            elif port == 40:
                pStr = "HLL"
            elif port == 41:
                pStr = "CTC"
            elif port == 38:
                pStr = "Not in use"
                raise Exception("Invalid Chamber")
            else:
                pStr = "Invalid"
                raise Exception("Invalid Chamber")
        return(pStr)
    except Exception as e:
        pass
        print("Error {}".format(e))
    return (pStr)


def serObj(_url_):
    return serial.serial_for_url(
        url=_url_,
        baudrate=config.baud_rate,
        do_not_open=True,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_EVEN,
        stopbits=1, timeout=config.tout)


def urlCreate(line):
    ipDict = config.ipConfig
    # print(ipDict)
    socketList = socketCreate(line)
    ip = ipDict[line]
    dummyURL = 'socket://'
    urlList = []
    for i in socketList:
        url = dummyURL+ip+':'+str(i)
        urlList.append(url)
    return(urlList)


def urlDict():
    d = {}
    for i in list(config.ipConfig.keys()):
        urlList = []
        allchList = []
        x = urlCreate(i)
        y = portCreate(i)
        chList = []
        for j in y:
            z = chNameCreate(str(i), j)
            chList.append(z)
        # List of all chmber
        allchList.append(chList)
        # List of all urls
        urlList.append(x)
        d['{}'.format(i)] = {}
        for a, b in zip(allchList, urlList):
            tempDict = dict(zip(a, b))
            for k, v in tempDict.items():
                d['{}'.format(i)]['{}'.format(k)] = v
    return d

# def readAll():
#     datalist = []
#     for i in range(5):
#         if i < 10:
#             x = "0"+str(i)
#         else:
#             x = str(i)
#         datalist.append(x)
#     lol = "005"
#     cmdList = []
#     for j in datalist:
#         cmd = cmdMake.cmdStr(lol, j)
#         cmdList.append(cmd)
#     return(cmdList)
def main():
    print(urlDict())



if __name__ == '__main__':
    main()
