# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Created by Tao Huang, August 2020, in Python 3.7
#
# Script to download and visualize the discharge data from NWIS, USGS
# and separate the flood events with a single peak
#
# Version 1.0        
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import hydrofunctions as hf
from scipy.signal import find_peaks

## function to create a folder to store the results if it does not exist

def ResultsFolder(Folder):
    if os.path.exists(Folder) == False:
        os.mkdir(Folder)

## A function to obtain the peak flow data of a USGS gauge

def GetFlow(site_no,begin_date,end_date):
    # download the discharge data (instantaneous values,15-min) from NWIS

    discharge = hf.NWIS(site_no, 'iv', begin_date, end_date)
    discharge.get_data()

    # save the data as TXT and CSV and store them in the "Raw_Data" folder

    Folder1 = './Raw_Data_' + site_no +'/'
    ResultsFolder(Folder1)

    raw_data = pd.DataFrame({'discharge_cfs':discharge.df().iloc[:,0],
                          'qualifiers':discharge.df().iloc[:,1]})
    raw_data.to_csv(Folder1 + "Raw_Discharge_" + site_no + ".txt")
    raw_data.to_csv(Folder1 + "Raw_Discharge_" + site_no + ".csv")

    # generate a discharge hydrograph and save as JPEG, and store them in the "Raw_Data" folder

    flow = pd.DataFrame(raw_data['discharge_cfs'])

    flow.plot(figsize=(12,6))
    plt.title("Discharge Hydrograph of "+ site_no)
    plt.legend(["Discharge"], loc='best',edgecolor='k')
    plt.xlabel("Date")
    plt.ylabel("Discharge (cfs)")
    plt.savefig(Folder1 + "Discharge_" + site_no +".jpeg")
    plt.close()

    # find the peak flow and store separately the data of each flood event

    # set minimal prominence as 40 cfs(the difference between peak and its nearest lowest point)

    peaks,_ =find_peaks(flow['discharge_cfs'],prominence=40)

    # seperate the flood event(assuming that duration is about 5 days) and save as JPEG and CSV
    # store them in the "Flood_Events" folder

    Folder2 = './Flood_Events_' + site_no +'/'
    ResultsFolder(Folder2)

    event_no = 1

    for index in peaks:
    
        if index-200 < 0:
            start = 0
        else:
            start = index-200
        end = index + 200
    
        flood_event=flow[start:end]
    
        flood_event.plot(figsize=(12,6))
        peakvalue = flow[index:index+1]
        plt.scatter(peakvalue.index,peakvalue['discharge_cfs'],color='r')
        plt.title("Flood Event " + str(event_no) +" of "+ site_no)
        plt.legend(["Discharge","Peak Rate"], loc='best',edgecolor='k')
        plt.xlabel("Date")
        plt.ylabel("Discharge (cfs)")
        plt.savefig(Folder2 + "Flood_Event_" + str(event_no) +"_"+ site_no +".jpeg")
        plt.close()

        flood_event.to_csv(Folder2 + "Flood_Event_" + str(event_no) +"_"+ site_no +".csv")
    
        event_no = event_no + 1

## main program    
# read all the gauge number from the TXT file
site_no = np.genfromtxt('USGS_Gauge.txt',dtype=str)

begin_date = input("Please enter the begin date(YYYY-MM-DD): ")
end_date = input("Please enter the end date(YYYY-MM-DD): ")

Results = [None]*30
i = 0

for site in site_no:
    try:
        GetFlow(site,begin_date,end_date)

    # skip the Nodata error and continue
    except Exception as msg:
        print("* "*20)
        print("Warnings for " + site + ":",msg)
        print("Please try again later!")
        print("* "*20)

        Results[i]=0
        i=i+1

    else:
        print("Gauge " + site + " is done!")
        
        Results[i]=1
        i=i+1
        
    continue
'''
for R in Results:
    print(R)
'''    
print("Discharge data processing is done!")
