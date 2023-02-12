# Estimating-Parameters-of-NRCS-Unit-Hydrographs
These Python scripts are developed for refining the Natural Resources Conservation Service (NRCS, formerly the Soil Conservation Service, SCS) unit hydrograph (UH), which is one of the most commonly used synthetic UH methods for hydrologic modeling and engineering design all over the world. Specifically, two key parameters of this method, namely, the peak rate factor (PRF) and the lag time can be estimated based on the unit hydrographs derived based on observed rainfall-runoff events. For more information, please refer to the technical report, “Developing customized NRCS unit hydrographs (Finley UHs) for ungauged watersheds in Indiana” (Huang and Merwade, 2023).

A brief introduction to the features of each Python script is as follows.

(1) This Python script is developed to download and visualize the discharge data from NWIS, USGS and separate the flood events with a single peak.

(2) This Python script is developed to download and visualize the precipitation data from NCDC, NOAA.

(3) This Python script is developed to derive a UH, dimensionless UH, and estimate the PRF based on a given flood event (in cubic feet per second) stored in a CSV file.

(4) This Python script is developed to estimate the lag time and create a figure for rainfall (red bars) and runoff (a blue curve) of an event.
