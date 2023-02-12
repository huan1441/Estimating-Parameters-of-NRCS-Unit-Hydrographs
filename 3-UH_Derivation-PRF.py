# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Created by Tao Huang, April 2020, in Python 3.7
#
# Script to derive a Unit Hydrograph, dimensionless UH, and estimate PRF
# based on a given flood event(in cfs) in a CSV file
#
# Version 1.0        
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# function to create a folder to store the results if it does not exist

def ResultsFolder(Folder):
    if os.path.exists(Folder) == False:
        os.mkdir(Folder)

# obtain the file name of the flood event(.csv)

rawdata_folder = './raw_data/'
#folder_path = r'.\raw_data'
filename = os.listdir(rawdata_folder)

# create a dataframe to store PRF of all the runoff events

PRF = pd.DataFrame(0, index=filename,columns=['PRF'])
PRF.index.name = 'File_Name'

for file in filename:
    rawdata = pd.read_csv(rawdata_folder + file)

    print("\nResults of the runoff event in " + file + ":\n")

    file = file.split(".")[0]

    # create a corresponding folder for a runoff event to store the results

    Folder0 = './UH/'
    ResultsFolder(Folder0)

    Folder1 = './UH/'+ file +'/'
    ResultsFolder(Folder1)

    # obtain the drainage area of the watershed
    # the value of area is stored in the second row and third column in the original file

    area = rawdata.iloc[0,2]
   
    print("The drainage area of the watershed is " + str(area) + " mile\u00b2.\n".format())

    # compute the time interval (in seconds) of the discharge data

    rawdata.iloc[:,0] = pd.to_datetime(rawdata.iloc[:,0])
    delta_t = (rawdata.iloc[1,0] - rawdata.iloc[0,0]).seconds
    print("The time interval of the discharge data is " + str(delta_t/60) + " mins.\n")

    # create a new time index in days

    index = np.linspace(0,delta_t/86400*(len(rawdata)-1),len(rawdata))

    # compute the direct runoff(cfs)
    # separate baseflow with straight line method and assign the first value as baseflow

    baseflow = rawdata.iloc[0,1]

    directQ_cfs = pd.DataFrame(0.0, index=index, columns=['Direct_runoff_cfs'])

    for i in range(len(rawdata)):
        if rawdata.iloc[i,1] - baseflow < 0:
            directQ_cfs.iloc[i] = 0
        else:
            directQ_cfs.iloc[i] = rawdata.iloc[i,1] - baseflow   

    # compute the depth of the direct runoff(in)

    directQ_in = pd.DataFrame(0.0, index=index, columns=['Direct_runoff_in'])

    for i in range(1,len(rawdata)):
        # 1 mile = 5280 ft, and 1 ft = 12 in
        directQ_in.iloc[i] = float((directQ_cfs.iloc[i-1]+directQ_cfs.iloc[i])/2*delta_t*12/(area*5280**2))

    # derive the Unit Hydrograph(cfs/in), save as CSV & JPEG in the "UH" folder

    sum_directQ_in = float(directQ_in.iloc[:,0].sum())

    UH = pd.DataFrame(0.0, index=index, columns=['UH_cfs/in'])

    for i in range(len(rawdata)):
        UH.iloc[i] = float(directQ_cfs.iloc[i]/sum_directQ_in)

    UH.index.name = 'Days'

    UH.to_csv(Folder1 + "Unit Hydrograph of " + file + ".csv")

    UH.plot(figsize=(12,6))
    plt.title("Unit Hydrograph of "+ file)
    plt.legend(["Discharge"], loc='best',edgecolor='k')
    plt.xlabel("Days")
    plt.ylabel("Discharge (cfs/in)")
    plt.savefig(Folder1 + "Unit Hydrograph of " + file + ".jpeg")
    plt.close()

    # check whether the depth of the UH is equal to 1 inch

    depth_UH = UH.iloc[:,0].sum()*delta_t*12/(area*5280**2)
    depth_UH = round(depth_UH,1)

    print("The depth of direct runoff in the Unit Hydrograph is " + str(depth_UH) + " inch.")

    if depth_UH != 1.0:
        print("Note: The ordinates of UH shall be adjusted by proportion so that the depth of direct runoff is 1 inch!\n")

    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    
    # generate the Dimensionless Unit Hydrograph, save as CSV & JPEG in the "UH" folder

    Q_peak = UH.iloc[:,0].max()
    T_peak = UH[UH.iloc[:,0]==Q_peak].index[0]

    index_dl = index/T_peak

    DUH = pd.DataFrame(0.0, index=index_dl, columns=['Q/Qp'])

    for i in range(len(rawdata)):
        DUH.iloc[i] = float(UH.iloc[i]/Q_peak)

    DUH.index.name = 't/Tp'

    DUH.to_csv(Folder1 + "Dimensionless Unit Hydrograph of " + file + ".csv")

    DUH.plot(figsize=(12,6))
    plt.title("Dimensionless Unit Hydrograph of " + file)
    plt.legend(["DUH"], loc='best',edgecolor='k')
    plt.xlabel("t / Tp")
    plt.ylabel("Q / Qp")
    plt.savefig(Folder1 + "Dimensionless Unit Hydrograph of " + file + ".jpeg")
    plt.close()

    # compute PRF based on the UH

    PRF.loc[file+".csv"] = round(float(Q_peak*T_peak*24/area))

# save PRF of all the runoff events as CSV in the "UH" folder

PRF.to_csv("./UH/" + "PRF of Watersheds.csv")

print("UH derivation for the " + str(len(filename)) + " runoff events is done!")
