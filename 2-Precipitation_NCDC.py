# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Created by Tao Huang, September 2020, in Python 3.7
#
# Script to download and visualize the precipitation data from NCDC, NOAA
#
# Version 1.0         
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from cdo_api_py import Client


# function to create a folder to store the results if it does not exist

def ResultsFolder(Folder):
    if os.path.exists(Folder) == False:
        os.mkdir(Folder)

## A function to obtain the rainfall data within a watershed

def GetRain(USGS_Gauge,start_date,end_date,extent):

    # default_units="None(0.01in)/metric(mm)/standard(in)"

    my_client = Client(my_token,default_units="standard",default_limit=1000)

    # 15-min precipitation

    datasetid = "PRECIP_15"

    Folder1 = './Raw_Rainfall_Data_'+USGS_Gauge+'_'+start_date+'/'
    ResultsFolder(Folder1)

    # find_station returns the dataframe containing stations' info within the input extent.
    stations = my_client.find_stations(datasetid = datasetid,
                                       extent = extent,
                                       startdate = pd.to_datetime(start_date),
                                       enddate = pd.to_datetime(end_date),
                                       return_dataframe = True)

    print(stations)

    # download data from all stations specified by their id
    for stationid in stations.id:
        raw_rainfall = my_client.get_data_by_station(datasetid = datasetid,
                                                     stationid = stationid,
                                                     startdate = pd.to_datetime(start_date),
                                                     enddate = pd.to_datetime(end_date),
                                                     return_dataframe = True,
                                                     include_station_meta = False)
    
    # save the data as CSV and store it in the "Raw_Rainfall_Data" folder
    
        station_id = stationid.split(":")[1]
        raw_rainfall.to_csv(Folder1 + datasetid + "min_COOP_" + station_id + ".csv")

    # combine the rainfall data from all stations

    rainfall=[]

    for stationid in stations.id:
        station_id = stationid.split(":")[1]
        df = pd.read_csv(Folder1 + datasetid + "min_COOP_" + station_id + ".csv")
        try:
            df = df[['date','QPCP']]
        except Exception as msg:
            print("Warnings for " + USGS_Gauge + ":",msg)
        else:
            rainfall.append(df)
        continue
            
    rainfall = pd.concat(rainfall,axis=0,ignore_index=True)
    rainfall.to_csv(Folder1 + 'rainfall of all stations.csv')
    rainfall = rainfall.set_index('date')

    # replace the defined flag value (999.99) with NaN and delete all NaN

    rainfall[rainfall==999.99] = np.nan
    rainfall = rainfall.dropna()

    # compute the average rainfal values of all stations

    rainfall_mean = pd.DataFrame({'rainfall_in':rainfall.groupby('date')['QPCP'].mean()})
    rainfall_mean.index = pd.to_datetime(rainfall_mean.index)

    # save the hyetograph as JPEG and store it in the "Hyetograph" folder

    Folder2 = './Results_Rainfall_'+USGS_Gauge+'_'+start_date+'/'
    ResultsFolder(Folder2)

    rainfall_mean.to_csv(Folder2 + 'rainfall_mean.csv')

    rainfall_mean.plot.bar(figsize=(20,18))
    plt.title("Hyetograph")
    plt.legend(["Rainfall"], loc='best',edgecolor='k')
    plt.xlabel("Date")
    plt.ylabel("Rainfall (in)")
    plt.savefig(Folder2 + "Hyetograph.jpeg")
    plt.close()

    rainfall_mean.plot(figsize=(20,10),style='bo')
    plt.title("Raifall scatter")
    plt.legend(["Rainfall"], loc='best',edgecolor='k')
    plt.xlabel("Date")
    plt.ylabel("Rainfall (in)")
    plt.savefig(Folder2 + "Rainfall_scatter.jpeg")
    plt.close()

    
## Main program

# access the data from the NCDC database with my token

my_token = "DBtMXiWkKSWyqfpLsFCyFXcSMndgPCml"

NSEW = pd.read_csv("watershed_extent.csv",dtype={'Gauge_No':str})

for i in range(len(NSEW)):
    # The extend is the lat, long of the target region.
    extent = dict()
    Directions = ['north','south','east','west']
    USGS_Gauge = str(NSEW.iloc[i,0])

    for j in range(4):
        extent[Directions[j]] = NSEW.iloc[i,j+1]
    
    # display the extent of the study area
    '''
    print("Extent for Study Watershed " + USGS_Gauge + ":")
    for key, value in extent.items():
	    print(str(key)+': '+str(value))
	    '''

    # create the begin date, end date, and type of dataset

    start_date = NSEW.iloc[i,5]

    end_date = NSEW.iloc[i,6]

    try:
        GetRain(USGS_Gauge,start_date,end_date,extent)
        # skip the Nodata error and continue
    except Exception as msg:
            print("* "*20)
            print("Warnings for " + USGS_Gauge + ":",msg)
            print("Please expand the extent of the watershed!")
            print("* "*20)

            # add ex(in degree) in each direction of the extent
            ex = 0.2
        
            extent['north'] = NSEW.iloc[0,1] + ex
            extent['south'] = NSEW.iloc[0,2] - ex
            extent['east'] = NSEW.iloc[0,3] + ex
            extent['west'] = NSEW.iloc[0,4] - ex

            # display the extent of the study area
            '''
            print("New Extent for Study Watershed " + USGS_Gauge + ":")
            for key, value in extent.items():
	            print(str(key)+': '+str(value))
	            '''

            GetRain(USGS_Gauge,start_date,end_date,extent)
            print("Rainfall data for "+ USGS_Gauge +"_"+start_date+" processing is done!")
        
    else:
        print("Rainfall data for "+ USGS_Gauge +"_"+start_date+" processing is done!")
