from showa.lib import logs
import serial
from datetime import datetime
from time import sleep
from showa.modules import writeUpload, config, socketSerial, emailReport, dataProcess


# main start; looping COM ports(devices) and run main code
def main():
    logs.initLogger(logLevel=logs.LEVEL_DEBUG)
    dateTime = datetime.now().strftime(config.pngdate)
    temp = socketSerial.urlDict()
    lineList = list(temp.keys())
    for line in lineList:
        try:
            config.carrierStopCount = []
            config.unresponsiveList = []
            ngGraphList = []
            tmaxlst = []
            tminlst = []
            CSRalst = []
            churlDict = temp[line]
            chList = list(churlDict.keys())
            urlList = list(churlDict.values())
            ngList = []
            for x, y in zip(urlList, chList):
                print(y)
                print(x)
                if y == 'VTC':
                    logs.logInfo(f"{line} {y} was run at {dateTime}")
                else:
                    pass
                carrierIdleCount = config.carrierStopCount
                if len(carrierIdleCount) > 2:
                    raise Exception("The line is idle")
                    break
                try:
                    ser = socketSerial.serObj(x)
                    ser.open()
                    # say greeting to port
                    ser.reset_input_buffer()
                    ser.write(bytearray(b'\x01005\x0200\x03FA'))
                    sleep(0.03)
                    ser.readline()
                    ser.write(bytearray(b'\x01005\x0200\x03FA'))
                    sleep(0.03)
                    ser.readline()
                    ser.reset_input_buffer()
                    # command and data read/write start here
                    df = writeUpload.write_readSer(y, ser)
                    ser.close()
                    dfUP, ngGraph, tmax, tmin, CSRa = writeUpload.dfToPlot(df, y,
                                                                           dateTime, line)
                    writeUpload.uploadDB(dfUP, y)
                    if ngGraph is not None:
                        ngGraphList.append(ngGraph)
                        tmaxlst.append(tmax)
                        tminlst.append(tmin)
                        CSRalst.append(CSRa)
                    else:
                        pass
                except dataProcess.portDisconnectError:
                    logs.logError("Port disconnect error at main",
                                  includeErrorLine=True)
                except Exception as err:
                    print("Error: {}".format(err))
                    logs.logError("Error occured {}".format(err),
                                  includeErrorLine=True)
                    ngList.append(y)
                ser.close()
            print(ngList)
            if ngList != []:
                for chamber in ngList:
                    url = churlDict[chamber]
                    print(url)
                    try:
                        ser = socketSerial.serObj(url)
                        ser.open()
                        ser.reset_input_buffer()
                        ser.write(bytearray(b'\x01005\x0200\x03FA'))
                        sleep(0.03)
                        ser.readline()
                        ser.write(bytearray(b'\x01005\x0200\x03FA'))
                        sleep(0.03)
                        ser.readline()
                        ser.reset_input_buffer()
                        # command and data read/write start here
                        df = writeUpload.write_readSer(chamber, ser)
                        ser.close()
                        dfUP, ngGraph, tmax, tmin, CSRa = writeUpload.dfToPlot(df, chamber,
                                                                               dateTime, line)
                        writeUpload.uploadDB(dfUP, chamber)
                        if ngGraph is not None:
                            ngGraphList.append(ngGraph)
                            tmaxlst.append(tmax)
                            tminlst.append(tmin)
                            CSRalst.append(CSRa)
                        else:
                            pass
                    except serial.SerialException as e:
                        print("Unexpected error for serial connection:{}"
                              .format(e))
                        logs.logError("Unexpected error for serial conn {}"
                                      .format(e), includeErrorLine=True)
                    except serial.SerialTimeoutException as e:
                        print("Serial write timeout error :{}".format(e))
                        logs.logError("Serial write time out error occured {}"
                                      .format(e), includeErrorLine=True)
                    except Exception as err:
                        print("still cannot:( {}".format(err))
                        logs.logError("Error occured {}".format(err),
                                      includeErrorLine=True)
            unresponsiveList = config.unresponsiveList
            if len(ngList) != 0:
                for i in unresponsiveList:
                    chamber = i
                    print("Chamber not responding to command:{}".format(chamber))
                    logs.logInfo("Chamber not responding to command:{}".format(chamber))
                if len(ngGraphList) != 0:
                    emailReport.send_NGemail(line, ngGraphList,
                                             tmaxlst, tminlst, CSRalst,
                                             unresponsiveList, dateTime)
                else:
                    emailReport.send_OKemail(line)
            else:
                print("Successfully completed all chambers")
                logs.logInfo("Successfully completed all chambers")
        except Exception as err:
            print("Error: {}".format(err))
            logs.logError("Error occured running for Line {}".format(err),
                          includeErrorLine=True)
    logs.closeLogger()


if __name__ == '__main__':
    main()
