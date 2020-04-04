from datetime import datetime, timedelta
import gzip
import os
import shutil

import geopandas
import pandas as pd
from shapely.geometry import mapping

import constants


def prep_peese_csv(csv_url, county_fips):
    """Takes a GitHub raw CSV URL (or optionally a filepath on disk) and a 
    dictionary `'county_name': 'fips_code'` and reformats the source data into
    long format, adding a column with the FIPS code for the county.
    
    :param csv_url: A URL pointing to raw CSV on GitHub (or filepath on disk). Data
        is expected to be of the format distributed by the PEESE group at Cornell Uni.
        See their github for an example (url in `./constants.py`)
    :param county_fips: Dictionary with the county name as the key and the FIPS code
        as the value. This data is added as a column to the long-formatted csv

    :return df: A Pandas DataFrame of the PEESE COVID-19 data in long format
    """
    print(f'\nReading PEESE CSV from GitHub as Data Frame:\n {csv_url}')
    df = pd.read_csv(csv_url)

    # Make long formatted table and add FIPS column
    print(f'\nCreating NYC region and melting CSV to long format')
    df['fips'] = df['region'].map(constants.county_fips)

    # NYC is not reporting to the county level. Replace the NYC counties with
    # a new region called 'new york city', add a no data value to fips, and
    # sum up the cases across the NYC counties
    df.loc[df.fips.isin(constants.nyc_counties_fips), 'region'] = 'new york city'
    df.loc[df.region == 'new york city', 'fips'] = constants.nyc_fake_fips
    df = df.groupby(['region', 'fips']).sum().reset_index()

    # Long format the data frame
    df = pd.melt(df, id_vars=['region', 'fips'], var_name='date', value_name='cases')

    # Coerce to Pandas datetime and add 12 hours to account for local time adjustments in JS (esri in particular)
    df = df.assign(date=lambda x: pd.to_datetime(x['date']))
    df = df.assign(date=lambda x: df.date + timedelta(hours=12))

    # Calculate new daily cases
    df = df.sort_values(['region', 'date'])
    df = df.set_index(['date', 'region', 'fips'])
    df = df.assign(new_cases=df.cases.diff().fillna(0).astype(int))
    df = df.reset_index()
    df.loc[df.new_cases <0, 'new_cases'] = 0

    df.to_csv('/home/vitale232/Desktop/covid.csv')


    print(' success')
    return df

def merge_peese_with_census(cases_df, counties_geojson, output_geojson, slim_output=None, gzip=False):
    """Merge the PEESE COVID data with the US Census Bureau 2018 County Data (including population)
    
    :param cases_df: A Pandas DataFrame in long format of the PEESE covid data
    :param counties_geojson: A GeoJSON formatted GIS file of the US Census Bureau 2018 population estimates.
        The file will serve as the shape for the output geojson file from this function.
        Data is documented in the `./data/US_Census`, relative to the root of this repo
    :param output_geojson: A filepath on disk. The US Census data merged with the PEESE covid data will
        be saved to the location specified in this param.
    :param slim_output: Defaults None. If value is given, it should be a filepath to disk. This file
        will be similar to the output_geojson file, but will contain less fields, thus produce a smaller
        file that is more friendly to the web. Fields can be added and removed as needed in `./constants.py`
    :param gzip: Bool, defaults False. If True, a g-zipped version of the geojson will also be produced.
        The file will be in the same location as output_geojson param, appended with '.gz' extension.
    
    :returns output_geojson: Returns the output geojson file location as a string
    """
    print(f'\nReading in the counties GeoJSON:\n {counties_geojson}')
    counties = geopandas.read_file(counties_geojson, dtype={'fips': str})
    counties = counties.rename(columns={
        col: col.lower() for col in counties.columns
    })
    counties = counties.loc[counties.state_name == 'New York']

    print(f'\nMerging NYC counties to one polygon for join with PEESE data')
    counties['nyc'] = counties.fips.isin(constants.nyc_counties_fips)
    counties.loc[counties.nyc == True, 'name'] = 'New York City'
    # Use sum to ensure population columns contain sum of NYC counties
    nyc = counties.dissolve(by='nyc', aggfunc='sum').reset_index()
    # Add the same fake fips code to the NYC features to join on using pd.concat
    nyc['fips'] = constants.nyc_fake_fips

    # Join all NY counties except NYC with the NYC shape and add logical names
    counties_nyc = pd.concat(
        [
            counties.loc[counties.nyc == False],
            nyc.loc[nyc['nyc'] == True]
        ]
    )
    counties_nyc.loc[counties_nyc.nyc == True, 'name'] = 'New York City'
    counties_nyc.loc[counties_nyc.nyc == True, 'state_name'] = 'New York'
    print(' success')

    print(f'\nMerging PEESE data with Census GIS data')
    county_cases = counties_nyc.merge(cases_df, how='outer', on='fips')
    print(' success')

    print(f'\nCreating field for # Cases normalized by population')
    # Calculate cases per 100k people
    county_cases['cases_per_100k'] = ((county_cases.cases/county_cases.population) * 100000).apply(lambda x: round(x, 3))

    print(f'\nWriting PEESE GIS data to GeoJSON:\n {output_geojson}')
    county_cases = county_cases.assign(date=(
        (county_cases.date - datetime(1970, 1, 1)).dt.total_seconds() * 1000).apply(int)
    )
    if not os.path.isdir(os.path.dirname(output_geojson)):
        os.makedirs(os.path.dirname(output_geojson))
        print(f'  Created output dir: {os.path.dirname(output_geojson)}')
    county_cases.to_file(output_geojson, driver='GeoJSON')

    if slim_output:
        print(f'\nWriting PEESE GIS data to GeoJSON with slim fields')
        print(f' {slim_output}\n Slim Fields:\n  {constants.peese_slim_fields}')
        county_cases[constants.peese_slim_fields].to_file(slim_output, driver='GeoJSON')

    if gzip:
        gzip_geojson(
            output_geojson,
            output_geojson+'.gz'
        )
        if slim_output:
            gzip_geojson(
                slim_output,
                slim_output+'.gz'
            )

    return output_geojson

def gzip_geojson(input_filepath, output_filepath):
    """Compress a file using gzip algorithm
    
    :param input_filepath: The file to be compressed
    :param output_filepath: The file location to create a compressed copy of the input file

    :returns bool: True on success.
    """
    print(f'\nGZIP file:\n {input_filepath}\n  as\n {output_filepath}')
    with open(input_filepath, 'rb') as f_in:
        with gzip.open(output_filepath, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    return True

def main():
    start_time = datetime.now()
    print(f'\nRunning script : {os.path.abspath(__file__)}')
    print(f'Start time     : {start_time}')

    counties_geojson = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        '..',
        '..',
        'data',
        'usa_counties.geojson'
    ))
    output_geojson = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        '..',
        '..',
        'dist',
        'peese',
        'peese-latest.geojson'
    ))
    slim_output_geojson = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        '..',
        '..',
        'dist',
        'peese',
        'peese-latest-slim.geojson'
    ))

    peese_data_frame = prep_peese_csv(
        constants.csv_url,
        constants.county_fips
    )

    merge_peese_with_census(
        peese_data_frame,
        counties_geojson,
        output_geojson,
        slim_output=slim_output_geojson,
        gzip=True
    )

    end_time = datetime.now()
    print(f'\nScript completed : {end_time}')
    print(f'Run time         : {end_time-start_time}\n')


if __name__ == '__main__':
    main()
