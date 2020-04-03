# About

`covid-web` is a project aimed at making geospatial COVID-19 data from repuatable sources freely available to whoever needs it. The aim is to publish the data to the AWS Cloud, where it can be ingested by client-side applications in the GeoJSON format. There is a lot of room to grow here, so feel free to contribute.

#### Quick Start

The core of this project can be tested by running some simple commands. This has only been tested on Ubuntu 18.04.

```bash
python3.8 -m venv covid-web-env
pip install --upgrade pip
pip install -r requirements.txt
```

Then there is a python script that will create and publish the data:

```bash
python source/backend/publish_peese_geojson.py
```

## Data 

Currently the data is available as a public object on AWS S3. The first dataset that is available is from the PEESE Group, a lab at Cornell University. They have New York State COVID-19 cases by county available for public access on their [GitHub page](https://github.com/PEESEgroup/PEESE-COVID19). The PEESE cases data is merged with US Census Bureau data, distributed by Esri, which is available on the [Esri site](https://www.arcgis.com/home/item.html?id=a00d6b6149b34ed3b833e10fb72ef47b).

The Census data contains population estimates for 2018. The data is merged with the COVID cases based on the county name and FIPS code. In their final format, there are two separate GeoJSON layers available in two separate formats. The two formats include a raw JSON and a gzip encoded JSON.

### Full Census Data and COVID-19 Cases

The Census data from Esri that is combined with the PEESE COVID-19 data contains numerous attributes, to many to list here. You can examine the GIS census data from the source download at Esri's site, or you can examine the GeoJSON formatted version that is ingested by these tools. The GeoJSON formatted version is available in if you clone this repo at `./data/usa_counties.geojson`. You can view this file easily with a Desktop GIS tool like the cross-platform, open source [QGIS](https://qgis.org/en/site/).

The published data is available at two separate URLs, and should be updated daily to include the latest updates (time TBD):

|     File                             |                           URL                                |
|--------------------------------------|--------------------------------------------------------------|
| ./dist/peese/peese-latest.geojson    | https://covid-19-geojson.s3.amazonaws.com/peese-latest.geojson |
| ./dist/peese/peese-latest.geojson.gz | https://covid-19-geojson.s3.amazonaws.com/peese-latest.geojson.gz | 

The data is formatted such that each individual record is a feature in a GeoJSON feature collection. The geometry of the features are MultiPolygon features, and the properties of each feature include the date of the case count, all of the census data, and all of the census data. This data structure is anything but efficient, and we're open to suggestions.

### Slim Census Data and COVID-19 Cases

At this point, the COVID-19 cases data is being reported in a granular fashion. If data regarding segments of the population become more available, the full census data will be useful. For quick visualizations, though, it's a bit excessive to send all of that data over the wire to every visitor.

To that end, a "slim" version of the PEESE COVID/Census data will be available in the same S3 bucket. The data there will include a limited number of fields from the US Census data and all of the PEESE data. The field list is as follows:

- **geometry**: feature geometry
- **date**: date of case count
- **cases**: number of cases
- **name**: county name
- **state_name**: name of US state
- **fips**: fips code
- **population**: 2018 Census estimated pop
- **males**: 2018 census estimated male pop
- **females**: 2018 Census estimated female pop

The published data is available at two separate URLs, and should be updated daily to include the latest updates (time TBD):

|     File                             |                           URL                                |
|--------------------------------------|--------------------------------------------------------------|
| ./dist/peese/peese-latest-slim.geojson    | https://covid-19-geojson.s3.amazonaws.com/peese-latest-slim.geojson |
| ./dist/peese/peese-latest-slim.geojson.gz | https://covid-19-geojson.s3.amazonaws.com/peese-latest-slim.geojson.gz | 

## Project Organization

The majority of the project currently lives in the `./source/backend` directory. There is a script called `publish_peese_geojson.py`. If called using the Python 3.8 virtualenv that can be replicated using the `requirements.txt` file in this repository, it will reformat the PEESE data, merge it with the spatial census data, and publish it to S3. The AWS portion of the script uses `boto3`. See the [docs](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html) to decide how you'd like to configure your credentials for your AWS account.

## Future Work

We would also like to publish the NYT data from the [NYT GitHub](https://github.com/nytimes/covid-19-data). The work is almost complete here, but needs additional work surrounding their handling of the Kansas City metro area and surrounding counties.

It would be useful to generate JSON versions of the data using other data models. This data model is very GIS centric, and was modeled to work with the Esri JS API. There's a lot of redundant information in the GeoJSON files, and a more thoughtful model would help bring down file sizes.

The intention is to create a client side JS application that will make for an interactive viewing experience of these data. There is currently a simple map of the data that can be viewed on [Stackblitz](https://stackblitz.com/edit/esri-play-peese-data?file=src%2Fapp%2Fesri-map%2Fesri-map.component.ts)

Since this project is producing static JSON files, if the data become widely used, it would be worth considering using a CDN like AWS CloudFront to distribute the data. The naming convention may need to be modified, as daily cache invalidation could become expensive.

If more files are to be generated, we could consider using a Lambda@Edge function or some equivalent to give this project more of an API feel. For example, it may be useful to serve all of the files from one URL, and allow query params and headers determine the response. If the client requests gzip, send the gzipped version. If we were to create daily files, we could accept query params of dates and return the date range specified.
