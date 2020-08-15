import matplotlib.pyplot as plt
import numpy as np
import os
from showa.modules import config
from scipy.integrate import trapz
# from showa.lib import logs
from datetime import datetime
from pathlib import Path

if config.picPath == "":
    here = Path(__file__).resolve().parents[3]
    fileLocation = str(here) + "/data/"
else:
    fileLocation = config.picPath


def newDir(dateTime, lineNo):
    dirName = fileLocation + "/" + lineNo + "/" + dateTime
    # Create target directory & all intermediate directories if don't exists
    try:
        os.makedirs(dirName)
        print("Directory ", dirName,  " Created ")
        # logs.logInfo("Directory for L{} is created".format(lineNo))
    except FileExistsError:
        # print("Directory ", dirName,  " already exists")
        pass

    # Create target directory & all intermediate directories if don't exists
    if not os.path.exists(dirName):
        os.makedirs(dirName)
        # print("Directory ", dirName,  " Created hor ")
    else:
        print("Directory Okay")
    return(dirName)


def picName(comport, lineNo):
    dt_string = datetime.now().strftime(config.pngdate)
    # dateTime = datetime.now().strftime("%d-%m-%Y_%H_%M_%S")
    picName = lineNo + "_" + comport + "_" + dt_string
    return(picName)


def picTitle(comport, lineNo):
    dt_string2 = datetime.now().strftime(config.dateonGraph)
    picTitle = lineNo + " " + comport + " " + dt_string2
    return(picTitle)


def absIntegrate(df):
    df1 = df.Torque
    dfMeanACC = df1[80:140].mean()
    newDfCS = df1[80:140].apply(lambda x: abs(x-dfMeanACC))
    CSRa = trapz(newDfCS)/60
    return CSRa


def status(dfTorque):
    x = config.controlLine
    y = config.controlLine*(-1)
    tmax = dfTorque['Torque'].max()
    tmin = dfTorque['Torque'].min()
    CSRa = round(absIntegrate(dfTorque), 1)
    if (tmax > x or tmin < y) and CSRa >= config.CSRa:
        status = 'Abnormal Torque Peak and Constant Speed detected.'
    elif CSRa >= config.CSRa:
        status = 'Abnormal Constant Speed detected.'
    elif tmax > x or tmin < y:
        status = 'Abnormal Torque Peak detected.'
    else:
        status = 'Normal'
    return (status)


def plot(dfSpeed, dfTorque, chname, dateTime, lineNo):
    try:
        CSRa = round(absIntegrate(dfTorque), 1)
        img = plt.imread("C:\\Users\\sputter.maint\\Desktop\\TDU_V5\\Automated TDU Torque Extraction\\src\\bg.jpg")
        fig, ax1 = plt.subplots(facecolor=config.facecolor, figsize=(7.5, 5))
        ax2 = ax1.twinx()
        ax1.plot(dfTorque.index, dfTorque, '{}-'.format(config.torquecolor))
        ax1.plot([0, 255], [config.controlLine, config.controlLine], 'c--')
        ax1.plot([0, 255], [config.controlLine*(-1), config.controlLine*(-1)],
                 'c--')
        ax1.plot([80, 80], [config.controlLine*(-1), config.controlLine], 'c*')
        ax1.plot([140, 140], [config.controlLine*(-1), config.controlLine], 'c*')
        ax2.plot(dfSpeed.index, dfSpeed, '{}-'.format(config.speedcolor))
        # Specify background color for the axis/plot
        ax1.imshow(img, extent=[0, 400, -200, 300])
        ax1.set_facecolor("black")
        ax1.set_xticks(np.arange(0, 256, 20))
        ax1.set_yticks(np.arange(-75, 80, 15))
        ax1.set_ylim((-75, 75))
        ax1.set_xlim((0, 240))
        ax1.set_clip_on(False)
        ax2.set_ylim((-1980, 220))
        ax2.set_xlim((0, 240))
        # fig.suptitle()
        temp = status(dfTorque)
        if temp == 'Normal':
            ax1.set_title(temp, color='green')
            ax1.text(87, 53, 'Const Avg = {}'.format(CSRa), color='magenta')
        else:
            ax1.set_title(temp, color='red')
            ax1.text(87, 53, 'Const Avg = {}'.format(CSRa), color='red')
        ax1.set_xlabel('{}'.format(picTitle(chname, lineNo)), fontsize=14,
                       fontweight='bold')
        ax1.set_ylabel('Torque', color=config.torquecolor)
        ax2.set_ylabel('Speed', color=config.speedcolor)
        ax1.grid(linestyle='-', linewidth='0.5', color=config.gridcolor)
        # print(fileLocation)
        # annotation of highest torque
        dfTorque = dfTorque.reset_index()
        tmax = dfTorque['Torque'].max()
        xindex = dfTorque.query('Torque == {}'.format(tmax))['index']
        xmax = xindex.iat[0]
        tmin = dfTorque['Torque'].min()
        xxindex = dfTorque.query('Torque == {}'.format(tmin))['index']
        xmin = xxindex.iat[0]
        bbox_props = dict(boxstyle="round,pad=0.3", fc="w", ec="k", lw=0.72)
        arrowprops = dict(arrowstyle="->",
                          connectionstyle="angle,angleA=0,angleB=60",
                          color="white")
        kw = dict(xycoords='data', textcoords="axes fraction",
                  arrowprops=arrowprops, bbox=bbox_props, ha="right", va="top")
        ax1.annotate('{}'.format(round(tmax, 1)), xy=(xmax, tmax),
                     xytext=(0.98, 0.95), **kw)
        ax1.annotate('{}'.format(round(tmin, 1)), xy=(xmin, tmin),
                     xytext=(0.08, 0.05), **kw)
        ax1.text(200, -75, f'Control:\nConst Avg < {config.CSRa}\n-{config.controlLine} < Peak < {config.controlLine}',
                 color='white', fontsize=8,
                 bbox={'boxstyle': 'round', 'facecolor': 'grey',
                       'alpha': 0.5, 'pad': 0.3})
        plt.tight_layout()
        fig.savefig("{}/{}.png".format(newDir(dateTime, lineNo),
                    picName(chname, lineNo)), facecolor=fig.get_facecolor(),
                    transparent=True)
        # plt.show()
        plt.close()
    except Exception as e:
        print("Error encountered during plotting.{}".format(e))
    if status(dfTorque) == 'Normal':
        return None, None, None, None
    else:
        return chname, tmax, tmin, CSRa
