from datetime import datetime
import os
import json

import geopandas
import pandas as pd
from shapely.geometry import mapping


nyt_cases_url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'
start_time = datetime.now()
print(f'\nRunning script : {os.path.abspath(__file__)}')
print(f'Start time     : {start_time}')

fabricated_fips = {
    'New York City': '-9999',
}

nyc_counties_fips = ['36005', '36047', '36061', '36081', '36085']
simple_fields = [
    'objectid', 'fips', 'county', 'state_name', 'population', 'males', 'females',
    'date', 'cases', 'deaths',
    'geometry'
]

# read in the census polygon and NYT cases data
counties_geojson = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    '..',
    '..',
    'census_data',
    'usa_counties.geojson'
))

print(f'\nReading in the counties GeoJSON:\n {counties_geojson}')
counties = geopandas.read_file(counties_geojson)
counties = counties.rename(columns={
    col: col.lower() for col in counties.columns
})

print(f'\nReading in the NYT cases data:\n {nyt_cases_url}')
cases = pd.read_csv(nyt_cases_url, dtype={'fips': str})
# Add a fake fips code to the NYC area in the NYT csv to join on using pd.concat
cases.loc[cases.county == 'New York City', 'fips'] = fabricated_fips['New York City']
cases.date = pd.to_datetime(cases.date)

# Merge the NYC counties into one polygon
print(f'\nMerging NYC counties to one polygon for join with NYT data')
counties['nyc'] = counties.fips.isin(nyc_counties_fips)
counties.loc[counties.nyc == True, 'name'] = 'New York City'
nyc = counties.dissolve(by='nyc').reset_index()
# Add the same fake fips code to the NYC features to join on using pd.concat
nyc['fips'] = fabricated_fips['New York City']
counties_nyc = pd.concat(
    [
        counties.loc[~counties.fips.isin(nyc_counties_fips)],
        nyc.loc[nyc['nyc'] == True]
    ]
)

# join cases to shapes using FIPS fields
print(f'\nMerging NYT data with census data')
county_cases = counties_nyc.merge(cases, how='outer', on='fips')
county_cases.loc[county_cases.cases.isnull(), 'cases'] = 0

county_cases_geojson = os.path.join(
    os.path.dirname(counties_geojson),
    'county_cases.geojson'
)
county_cases.to_file(county_cases_geojson, driver='GeoJSON')

# save a simpler geojson that ditches lots of the fields
county_cases_simple_geojson = os.path.join(
    os.path.dirname(county_cases_geojson),
    'county_cases_simple.geojson'
)
# add objectid field
print(f'Saving county cases with less fields as:\n {county_cases_simple_geojson}')
print(f'  including fields: {simple_fields}')
county_cases = county_cases.assign(objectid=[i for i in range(1, len(county_cases)+1)])
county_cases_simple = county_cases[simple_fields]
county_cases_simple = county_cases_simple.loc[~county_cases_simple.geometry.isnull()].assign(
    date=(county_cases_simple.date - datetime(1970, 1, 1)).dt.total_seconds() * 1000
)
county_cases_simple = county_cases_simple.loc[~county_cases_simple.date.isnull()]
county_cases_simple.to_file(county_cases_simple_geojson, driver='GeoJSON')

print(f'\nCreating nested cases dictionary with merged data')
features = []
for fips_code in counties.fips.tolist() + list(fabricated_fips.values()):
    fips_cases = county_cases.loc[county_cases.fips == fips_code].sort_values('date')
    if fips_cases.shape[0] > 1:
        first_row = fips_cases.iloc[0]
        cases = {
            str(case_day.date): {
                'cases': case_day.cases,
                'deaths': case_day.deaths
        } for case_day in fips_cases.itertuples()}
        properties = {
            'fips_code': str(first_row.fips),
            'state': str(first_row.state),
            'county': str(first_row.county),
            'population': float(first_row.population),
            'males': float(first_row.males),
            'females': float(first_row.females),
        }
        feat = mapping(first_row.geometry)
        features.append({
            'type': 'Feature',
            'bbox': first_row.geometry.bounds,
            'geometry': feat,
            'properties': properties,
            'cases': cases,
        })
        continue
output_geojson = {
    'type': 'FeatureCollection',
    'features': features
}

output_geojson_path = os.path.abspath(os.path.join(
    os.path.dirname(counties_geojson),
    'nyt_cases.geojson'
))
print(f'\nSaving merged data as nested GeoJSON:\n {output_geojson_path}')
with open(output_geojson_path, 'w') as geofile:
    geofile.write(json.dumps(output_geojson))

end_time = datetime.now()
print(f'\nScript completed : {end_time}')
print(f'Run time         : {end_time-start_time}\n')
