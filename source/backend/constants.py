# PEESE data transformation variables
county_fips = {              # FIPS codes for NYS counties (state fips+county fips)
    'albany': '36001',       # See US Census for more info
    'allegany': '36003',
    'bronx': '36005',
    'broome': '36007',
    'cattaraugus': '36009',
    'cayuga': '36011',
    'chautauqua': '36013',
    'chemung': '36015',
    'chenango': '36017',
    'clinton': '36019',
    'columbia': '36021',
    'cortland': '36023',
    'delaware': '36025',
    'dutchess': '36027',
    'erie': '36029',
    'essex': '36031',
    'franklin': '36033',
    'fulton': '36035',
    'genesee': '36037',
    'greene': '36039',
    'hamilton': '36041',
    'herkimer': '36043',
    'jefferson': '36045',
    'kings': '36047',
    'lewis': '36049',
    'livingston': '36051',
    'madison': '36053',
    'monroe': '36055',
    'montgomery': '36057',
    'nassau': '36059',
    'new york': '36061',
    'niagara': '36063',
    'oneida': '36065',
    'onondaga': '36067',
    'ontario': '36069',
    'orange': '36071',
    'orleans': '36073',
    'oswego': '36075',
    'otsego': '36077',
    'putnam': '36079',
    'queens': '36081',
    'rensselaer': '36083',
    'richmond': '36085',
    'rockland': '36087',
    'saratoga': '36091',
    'schenectady': '36093',
    'schoharie': '36095',
    'schuyler': '36097',
    'seneca': '36099',
    'st. lawrence': '36089',
    'steuben': '36101',
    'suffolk': '36103',
    'sullivan': '36105',
    'tioga': '36107',
    'tompkins': '36109',
    'ulster': '36111',
    'warren': '36113',
    'washington': '36115',
    'wayne': '36117',
    'westchester': '36119',
    'wyoming': '36121',
    'yates': '36123'
}

csv_url = 'https://raw.githubusercontent.com/PEESEgroup/PEESE-COVID19/master/ny%20cases%20by%20county.csv'

nyc_counties_fips = [ # FIPS of 5 NYC counties
    '36005',
    '36047',
    '36061',
    '36081',
    '36085'
]

nyc_fake_fips = '-9999' # New York City is not a US Census defined place. Set nodata value for FIPS code

peese_slim_fields = [  # Keep select fields for a "slim" geojson that will result in smaller requests
    'geometry',
    'date',
    'cases',
    'name',
    'state_name',
    'fips',
    'population',
    'males',
    'females',
    'pop2010',
]

# AWS variables
s3_bucket = 'covid-19-geojson'          # the bucket to which the geojson will be published
gzip_extra_args = {                          # these args set the headers and permissions on the s3 object
    'ContentType': 'application/json',  # set content-type: application/json header on GET/HEAD requests
    'ContentEncoding': 'gzip',          # inform clients the content is gzip encoded with content-encoding: gzip header
    'ACL': 'public-read',               # CAUTION!!!!!: allow public read access for object
}

json_extra_args = {
    'ContentType': 'application/json',
    'ACL': 'public-read', # CAUTION!!!! Public file will be created.
}