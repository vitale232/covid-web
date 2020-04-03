# About

`covid-web` is a project aimed at making geospatial COVID-19 data from repuatable sources freely available to whoever needs it. The aim is to publish the data to the AWS Cloud, where it can be ingested by client-side applications in the GeoJSON format. There is a lot of room to grow here, so feel free to contribute.

#### Quick Start

The core of this project can be tested by running some simple commands. This has only been tested on Ubuntu 18.04.

Start by cloning the repository:

```bash
git clone https://github.com/vitale232/covid-web.git
```

Then set up the Python environment (py3.8 is suggested, but this will probably work on other py3 versions):

```bash
python3.8 -m venv covid-web-env
pip install --upgrade pip
pip install -r requirements.txt
```

If you have never used AWS `boto3` on your machine, you may need to [configure your credentials](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html).

Then there is a python script that will create and publish the data:

```bash
python source/backend/publish_peese_geojson.py
```

The script will create a folder: `dist/peese`, which will contain local copies of the data that's uploaded to AWS S3.

## Data 

Currently the data is available as a public object on AWS S3. The first dataset that is available is from the [PEESE Group](https://www.peese.org/), a lab at Cornell University. They have New York State COVID-19 cases by county available for public access on their [GitHub page](https://github.com/PEESEgroup/PEESE-COVID19). The PEESE cases data is merged with US Census Bureau data, distributed by Esri, which is available on the [Esri site](https://www.arcgis.com/home/item.html?id=a00d6b6149b34ed3b833e10fb72ef47b).

The Census data contains population estimates for 2018. The data is merged with the COVID cases based on the county name and FIPS code. In their final format, there are two separate GeoJSON layers available in two separate formats. The two formats include a raw JSON and a gzip encoded JSON.

### Full Census Data and COVID-19 Cases

The Census data from Esri that is combined with the PEESE COVID-19 data contains numerous attributes, too many to list here. You can examine the GIS census data from the source download at Esri's site, or you can examine the GeoJSON formatted version that is ingested by these tools. The GeoJSON formatted version is available if you clone this repository at `./data/usa_counties.geojson`. You can view this file easily with a Desktop GIS tool like the cross-platform, open source [QGIS](https://qgis.org/en/site/).

The published data is available at two separate URLs, and should be updated daily to include the latest updates (time TBD):

|     File                             |                           URL                                |
|--------------------------------------|--------------------------------------------------------------|
| ./dist/peese/peese-latest.geojson    | https://covid-19-geojson.s3.amazonaws.com/peese-latest.geojson |
| ./dist/peese/peese-latest.geojson.gz | https://covid-19-geojson.s3.amazonaws.com/peese-latest.geojson.gz | 

The data is formatted such that each individual record is a feature in a GeoJSON feature collection. The geometry of the features are MultiPolygon features, and the properties of each feature include the date of the case count, the case count, and all of the census data. This data structure is anything but efficient, and we're open to suggestions.

*NOTE: the `new_cases` field is calculated by this toolset. It is not reported by PEESE.*

### Slim Census Data and COVID-19 Cases

At this point, the COVID-19 cases data is being reported in a granular fashion. If data regarding segments of the population become more available, the full census data will be useful. For quick visualizations, though, it's a bit excessive to send all of that data over the wire to every visitor.

To that end, a "slim" version of the PEESE COVID/Census data will be available in the same S3 bucket. The data there will include a limited number of fields from the US Census data and all of the PEESE data. The field list is as follows:

- **geometry**: feature geometry
- **date**: date of case count
- **cases**: number of cases
- **new_cases**: number of new cases on the `date`
- **name**: county name
- **state_name**: name of US state
- **fips**: fips code
- **population**: 2018 Census estimated pop
- **males**: 2018 census estimated male pop
- **females**: 2018 Census estimated female pop

*NOTE: the `new_cases` field is calculated by this toolset. It is not reported by PEESE.*

The published data is available at two separate URLs, and should be updated daily to include the latest updates (time TBD):

|     File                             |                           URL                                |
|--------------------------------------|--------------------------------------------------------------|
| ./dist/peese/peese-latest-slim.geojson    | https://covid-19-geojson.s3.amazonaws.com/peese-latest-slim.geojson |
| ./dist/peese/peese-latest-slim.geojson.gz | https://covid-19-geojson.s3.amazonaws.com/peese-latest-slim.geojson.gz | 

## Project Organization

The majority of the project currently lives in the `./source/backend` directory. There is a script called `publish_peese_geojson.py`. If called using the Python 3.8 virtualenv that can be replicated using the `requirements.txt` file in this repository, it will reformat the PEESE data, merge it with the spatial census data, and publish it to S3. The AWS portion of the script uses `boto3`. See the [docs](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html) to decide how you'd like to configure your credentials for your AWS account.

## Example JSON Response

Here are some samples to show the basic structure of the JSON response. They are technically FeatureCollections that contain MultiPolygon features, which follow the [GeoJSON specification](https://geojson.org/). The types can be inferred from the samples on the `properties`.

## Slim Version

```json
{
    "type": "FeatureCollection",
    "crs": {
        "type": "name",
        "properties": {
            "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
        }
    },
    "features": [
        ...,
        {
            "type": "Feature",
            "properties": {
                "date": 1583064000000,
                "cases": 0,
                "new_cases": 0,
                "name": "New York City",
                "state_name": "New York",
                "fips": "-9999",
                "population": 8679919,
                "males": 3882544,
                "females": 4292589,
                "pop2010": 8175133
            },
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [
                    [
                        [
                            [
                                -74.236939682477441,
                                40.506003322552658
                            ],
                            ...,
                            [
                                -73.846060798530061,
                                40.652600102974191
                            ]
                        ]
                    ],
                    [
                        [
                            [
                                -73.977061092200756,
                                40.797487091072867
                            ],
                            ...,
                            [
                                -73.977061092200756,
                                40.797487091072867
                            ]
                        ]
                    ]
                ]
            }
        },
        ...,
       {
            "type": "Feature",
            "properties": {
                "date": 1585915200000,
                "cases": 57159,
                "new_cases": 5350,
                "name": "New York City",
                "state_name": "New York",
                "fips": "-9999",
                "population": 8679919,
                "males": 3882544,
                "females": 4292589,
                "pop2010": 8175133
            },
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [
                    ...
                ]
        }
    ]
}
```

### All Census Data

```json
{
    "type": "FeatureCollection",
    "crs": {
        "type": "name",
        "properties": {
            "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
        }
    },
    "features": [
        {
            "type": "Feature",
            "properties": {
                "objectid": 1829,
                "name": "Albany",
                "state_name": "New York",
                "state_fips": "36",
                "cnty_fips": "001",
                "fips": "36001",
                "population": 317479,
                "pop_sqmi": 595.5,
                "pop2010": 304204,
                "pop10_sqmi": 570.6,
                "white": 237873,
                "black": 38609,
                "ameri_es": 654,
                "asian": 14579,
                "hawn_pi": 98,
                "hispanic": 14917,
                "other": 4744,
                "mult_race": 7647,
                "males": 147076,
                "females": 157128,
                "age_under5": 15286,
                "age_5_9": 16131,
                "age_10_14": 17639,
                "age_15_19": 23752,
                "age_20_24": 28017,
                "age_25_34": 39522,
                "age_35_44": 37218,
                "age_45_54": 45425,
                "age_55_64": 38900,
                "age_65_74": 20644,
                "age_75_84": 14570,
                "age_85_up": 7100,
                "med_age": 38.4,
                "med_age_m": 36.7,
                "med_age_f": 40.0,
                "households": 126251,
                "ave_hh_sz": 2.27,
                "hsehld_1_m": 18848,
                "hsehld_1_f": 23879,
                "marhh_chd": 20699,
                "marhh_no_c": 29943,
                "mhh_child": 2826,
                "fhh_child": 9834,
                "families": 71364,
                "ave_fam_sz": 2.95,
                "hse_units": 137739,
                "vacant": 11488,
                "owner_occ": 72577,
                "renter_occ": 53674,
                "no_farms17": 440.0,
                "ave_size17": 135.0,
                "crop_acr17": 34535.0,
                "ave_sale17": 107565.0,
                "sqmi": 533.16,
                "shape_length": 1.6997230927008167,
                "shape_area": 0.15090687684789317,
                "nyc": false,
                "date": 1583064000000,
                "region": "albany",
                "cases": 0,
                "new_cases": 0
            },
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [
                    [
                        [
                            [
                                -73.779528093580041,
                                42.460290922360059
                            ],
                            ...
                        ]
                    ]
                ]
            },
            ...
        },
    ]
}
```

## Future Work

We would also like to publish the NYT data from the [NYT GitHub](https://github.com/nytimes/covid-19-data). The work is almost complete here, but needs additional work surrounding their handling of the Kansas City metro area and surrounding counties.

It would be useful to generate JSON versions of the data using other data models. This data model is very GIS centric, and was modeled to work with the Esri JS API. There's a lot of redundant information in the GeoJSON files, and a more thoughtful model would help bring down file sizes.

The intention is to create a client side JS application that will make for an interactive viewing experience of these data. There is currently a simple map of the data that can be viewed on [Stackblitz](https://stackblitz.com/edit/esri-play-peese-data?file=src%2Fapp%2Fesri-map%2Fesri-map.component.ts)

Since this project is producing static JSON files, if the data become widely used, it would be worth considering using a CDN like AWS CloudFront to distribute the data. The naming convention may need to be modified, as daily cache invalidation could become expensive.

If more files are to be generated, we could consider using a Lambda@Edge function or some equivalent to give this project more of an API feel. For example, it may be useful to serve all of the files from one URL, and allow query params and headers determine the response. If the client requests gzip, send the gzipped version. If we were to create daily files, we could accept query params of dates and return the date range specified.
