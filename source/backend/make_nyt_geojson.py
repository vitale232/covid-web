from datetime import datetime, timedelta
import gzip
import os
import shutil

import geopandas
import pandas as pd
from shapely.geometry import mapping

import constants
from make_peese_geojson import gzip_geojson


def merge_nyt_with_census(csv_url, counties_geojson, output_geojson, slim_output=None, gzip=False):
    print(f'\nReading in the NYT cases data:\n {csv_url}')
    cases_df = pd.read_csv(csv_url, dtype={'fips': str})
    cases_df.loc[cases_df.county == 'New York City', 'fips'] = constants.nyc_fake_fips
    cases_df.date = pd.to_datetime(cases_df.date)
    cases_df = cases_df.assign(date=lambda x: cases_df.date + timedelta(hours=12))

    cases_df = cases_df.sort_values(['fips', 'date'])
    cases_df = cases_df.set_index(['date', 'county', 'state', 'fips'])
    cases_df = cases_df.assign(new_cases=cases_df.cases.diff().fillna(0).astype(int))
    cases_df = cases_df.assign(new_deaths=cases_df.deaths.diff().fillna(0).astype(int))
    cases_df = cases_df.reset_index()
    cases_df.loc[cases_df.new_cases <0, 'new_cases'] = 0

    print(f'\nReading in the counties GeoJSON:\n {counties_geojson}')
    counties = geopandas.read_file(counties_geojson)
    counties = counties.rename(columns={
        col: col.lower() for col in counties.columns
    })

    # Merge the NYC counties into one polygon
    print(f'\nMerging NYC counties to one polygon for join with NYT data')
    counties['nyc'] = counties.fips.isin(constants.nyc_counties_fips)
    counties.loc[counties.nyc == True, 'name'] = 'New York City'
    nyc = counties.dissolve(by='nyc', aggfunc='sum').reset_index()
    # Add the same fake fips code to the NYC features to join on using pd.concat
    nyc['fips'] = constants.nyc_fake_fips
    counties_nyc = pd.concat(
        [
            counties.loc[~counties.fips.isin(constants.nyc_counties_fips)],
            nyc.loc[nyc['nyc'] == True]
        ]
    )

    # join cases to shapes using FIPS fields
    print(f'\nMerging NYT data with census data')
    county_cases = counties_nyc.merge(cases_df, how='outer', on='fips')
    county_cases.loc[county_cases.cases.isnull(), 'cases'] = 0

    # TODO: for now, throw out rows with no geometry or date
    county_cases = county_cases.loc[~county_cases.geometry.isnull()]
    county_cases = county_cases.loc[~county_cases.date.isnull()]

    print(f'\nCreating fields for # Cases normalized by population')
    # Calculate cases per 100k people
    county_cases['cases_per_100k'] = ((county_cases.cases/county_cases.population) * 100000).apply(lambda x: round(x, 3))
    county_cases['deaths_per_100k'] = ((county_cases.deaths/county_cases.population) * 100000).apply(lambda x: round(x, 3))

    print(f'\nWriting NYT GIS data to GeoJSON:\n {output_geojson}')
    county_cases = county_cases.assign(date=(
        (county_cases.date - datetime(1970, 1, 1)).dt.total_seconds() * 1000).apply(int)
    )
    if not os.path.isdir(os.path.dirname(output_geojson)):
        os.makedirs(os.path.dirname(output_geojson))
        print(f'  Created output dir: {os.path.dirname(output_geojson)}')
    county_cases.to_file(output_geojson, driver='GeoJSON')

    if slim_output:
        print(f'\nWriting NYT GIS data to GeoJSON with slim fields')
        print(f' {slim_output}\n Slim Fields:\n  {constants.nyt_slim_fields}')
        county_cases[constants.nyt_slim_fields].to_file(slim_output, driver='GeoJSON')

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
