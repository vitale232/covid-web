from datetime import datetime
import json
import os

from cloud_functions import upload_file_to_s3
from colormap import get_rgbs
import constants
from make_nyt_geojson import merge_nyt_with_census


def main():
    """This function will be called if this python file is executed from the
    command line interpreter. The function manages the transformation of the raw NYT
    CSV file from GitHub into a GeoJSON formatted text file. The text files
    are compressed using the gzip algorithm, and the raw GeoJSON and g-zipped
    GeoJSONs are uploaded to AWS S3.

    The URL for the source data and information regarding the S3 bucket can
    be viewed and edited in the `./constants.py` folder also contained in this
    `./source/backend` directory.
    """
    start_time = datetime.now()
    print(f'\nRunning script : {os.path.abspath(__file__)}')
    print(f'Start time     : {start_time}')

    gzip_output = True
    color_bins = 5
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
        'nyt',
        'nyt-latest.geojson'
    ))
    slim_output_geojson = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        '..',
        '..',
        'dist',
        'nyt',
        'nyt-latest-slim.geojson'
    ))
    colormap_json = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        '..',
        '..',
        'dist',
        'nyt',
        'nyt-latest-colormap.json'
    ))
    # List of files to be uploaded to S3
    s3_upload_files = [
        output_geojson,
        slim_output_geojson,
        colormap_json,
    ]
    if gzip_output:
        # Add the gzip version if appropriate
        s3_upload_files += [
            geojson+'.gz' for geojson in s3_upload_files if 'colormap' not in geojson
        ]

    nyt_data_frame = merge_nyt_with_census(
        constants.nyt_csv_url,
        counties_geojson,
        output_geojson,
        slim_output=slim_output_geojson,
        gzip=gzip_output
    )

    cases_rgbs = get_rgbs(
        nyt_data_frame.cases_per_100k.values.tolist(),
        color_bins,
        mode='equalinterval'
    )

    if len(cases_rgbs['cuts']['rgb_colors']) != color_bins:
        cases_rgbs = get_rgbs(
            nyt_data_frame.cases.values.tolist(),
            color_bins,
            mode='equalcount'
        )

    print(f'\nWriting NYT colormap JSON:\n {colormap_json}')
    with open(colormap_json, 'w') as colormap_file:
        json.dump(cases_rgbs, colormap_file)

    for upload_geojson_file in s3_upload_files:
        # Choose S3 Metadata based on the upload file extension
        if upload_geojson_file.split('.')[-1] == 'gz':
            extra_args = constants.gzip_extra_args
        else:
            extra_args = constants.json_extra_args
        success = upload_file_to_s3(
            upload_geojson_file,
            constants.s3_bucket,
            object_name=os.path.basename(upload_geojson_file),
            extra_args=extra_args
        )
        print(f'S3 Upload success? {success}')

    end_time = datetime.now()
    print(f'\nScript completed : {end_time}')
    print(f'Run time         : {end_time-start_time}\n')

if __name__ == '__main__':
    main()
