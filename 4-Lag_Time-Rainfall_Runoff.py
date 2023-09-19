# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Created by Tao Huang, October 2020, in Python 3.7
#
# Script to estimate the lag time and
# create a figure for rainfall (red bars) and runoff(a blue curve) of an event
# 
#
# Version 1.0        
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

import os
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()

# function to create a folder to store the results if it does not exist

def ResultsFolder(Folder):
    if os.path.exists(Folder) == False:
        os.mkdir(Folder)

# create a corresponding folder for lag times file and rainfall-runoff event figures

Folder1 = './lag_time/'
ResultsFolder(Folder1)

# obtain the file name of the flood event(.csv)

rawdata_folder = './raw_data/'
filename = os.listdir(rawdata_folder)

# create a dataframe to store lag time of all the rainfall-runoff events

LAG = pd.DataFrame(0, index=filename,columns=['Lag time_hr'])
LAG.index.name = 'File_Name'

for file in filename:
    # read the data
    Data = pd.read_csv(rawdata_folder + file,parse_dates=['Date1','Date2'])

    file = file.split(".")[0]

    date1=Data.Date1
    y1=Data.Discharge_cfs

    date2=Data.Date2
    date2=date2.dropna()
    y2=Data.Rainfall_in
    y2=y2.dropna()

    # SCS Curve Number Method FOR ABSTRACTIONS
    CN = Data.CN[0]

    # potential maximum retention
    S = 1000/CN-10

    # total rainfall (in/15min)
    P = y2.sum()

    # initial abstraction
    Ia = 0.2*S

    index_Ia = 0

    for i in range(len(y2)):
        Ia = Ia - y2[i]
        if Ia <= 0:
            index_Ia = i
            break

    # calculate the excess rainfall
    Pe = (P-Ia)**2/(P-Ia+S)
    # for visualization purposes
    y2=y2*Pe/P

    # obtain the peak discharge and the peak time
    Q_peak = Data.iloc[:,1].max()
    T_peak = date1[Data.iloc[:,1]==Q_peak]

    # obtain the duration of the excess rainfall
    D_rain = date2.iloc[-1]-date2.iloc[index_Ia]

    # calculate the lag time (in hours)

    Lag_time = (T_peak.iloc[0]-date1.iloc[0]-D_rain/2).days*24+(T_peak.iloc[0]-date1.iloc[0]-D_rain/2).seconds/3600
    LAG.loc[file+".csv"] = Lag_time
'''
    fig, ax1 = plt.subplots(figsize=(12,8))
    ax1.plot(date1, y1,color='blue',label="Runoff",linewidth = 3)

    ax1.set_ylim(0, max(y1)*1.5)
    ax1.set_xlabel("Date",fontsize=15)
    ax1.set_ylabel("Discharge(cfs)",fontsize=15)

    ax2 = ax1.twinx()
    ax2.bar(date2, y2,color='red',label="Rainfall",width=0.05)

    ax2.invert_yaxis()
    ax2.set_ylim(max(y2)+0.1, 0)
    ax2.set_ylabel("Rainfall(in)",fontsize=15)

    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    plt.legend(handles1+handles2, labels1+labels2,loc='best',edgecolor='k',fontsize=15)

    plt.title("Rainfall-Runoff Event of " + file,fontsize=15)

    plt.savefig(Folder1 + "Rainfall-Runoff Event of " + file + ".jpeg")
    plt.close()
'''
# save the lag time of all the runoff events as CSV in the "UH" folder

LAG.to_csv(Folder1+"Lag Time of Watersheds.csv")

print("Lag time processing is done!")
