from showa.modules import dataProcess, plotting, config
from showa.lib.database import Postgres
from showa.lib import logs
import pandas as pd


# return clean dataframe
def write_readSer(comPort, ser):
    print("reading data..")
    dataDict = dataProcess.write_data(comPort, ser)
    df = pd.DataFrame.from_dict(dataDict)
    df['Speed'] = df['original'].apply(lambda x: dataProcess.speedClean(x))
    df['Torque'] = df['original'].apply(lambda x: dataProcess.torqueClean(x))
    df = df.drop(['original'], axis=1)
    return(df)


def dfToPlot(df, comPort, dateTime, line):
    print("plotting..")
    dfSpeed = df[['Speed']]
    dfSpeed = dfSpeed.astype(float)
    dfTorque = df[['Torque']]
    dfTorque = dfTorque.astype(float)
    dfRecon = pd.concat([dfSpeed, dfTorque], axis=1)
    dfRecon.insert(0, 'TimeStamp', pd.datetime.now().replace(microsecond=0))
    dfRecon.insert(1, 'Line', line)
    dfRecon.insert(2, 'Chamber', comPort)
    if config.plotEnable is True:
        ngGraph, tmax, tmin, CSRa = plotting.plot(dfSpeed, dfTorque, comPort, dateTime, line)
    else:
        pass
    if config.csvEnable is True:
        dfRecon.to_csv("{}/{}.csv".format(plotting.newDir(dateTime, line),
                                          plotting.picName(comPort, line)), sep=';', index=True, mode='w')
    else:
        pass
    return(dfRecon, ngGraph, tmax, tmin, CSRa)


def uploadDB(df, comPort):
    myPg = None
    try:
        myPg = Postgres(config.url, config.database, config.user,
                        config.password)
        myPg.connect()
        print("Connection succeeded..")
        listy = df.to_csv(None, header=False, index=False).split('\n')
        vals = [','.join(ele.split()) for ele in listy]
        for i in vals:
            y = i.split(",")
            y[0: 2] = [' '.join(y[0: 2])]
            x = tuple(y)
            if x == ('',):
                pass
            else:
                strSQL = "INSERT INTO tdu.{} values {}".format(
                         config.schema, x)
                myPg.execute(strSQL)
        myPg.commit()
    except Exception as err:
        logs.logError(
            "Upload Error Occured: {}".format(str(err)), includeErrorLine=True)
    finally:
        if myPg is not None:
            myPg.close()
