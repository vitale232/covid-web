# Census Data

## USA\_Counties Directory
This directory contains the source data that provides geographic shapes for all counties in the United States, including 2018 US Census Bureau estimates of population. The data is provided by Esri at this address: https://www.arcgis.com/home/item.html?id=a00d6b6149b34ed3b833e10fb72ef47b

## usa\_counties.geojson
This file is a reformatted version of the data from the USA\Counties directory. It was created by extracting the Esri layer package linked in the `USA\_Counties` portion of this README. Once the layer package is unzipped, there is a file geodatabase ('.gdb' filepath), which was loaded into QGIS for easy visualization. The file gdb was then exported from QGIS to geojson format as `usa_counties.geojson`.

