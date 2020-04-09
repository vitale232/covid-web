from datetime import datetime
import json
import os

from cloud_functions import upload_file_to_s3
from colormap import get_rgbs
import constants
from make_peese_geojson import merge_peese_with_census, prep_peese_csv


def main():
    """This function will be called if this python file is called from the
    command line. The function manages the transformation of the raw PEESE
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
    colormap_json = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        '..',
        '..',
        'dist',
        'peese',
        'peese-latest-colormap.json'
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

    peese_data_frame = prep_peese_csv(
        constants.peese_csv_url,
        constants.county_fips
    )

    peese_merged_df = merge_peese_with_census(
        peese_data_frame,
        counties_geojson,
        output_geojson,
        slim_output=slim_output_geojson,
        gzip=gzip_output
    )

    print('\nAttempting to calculate equal count color bin')
    cases_rgbs = get_rgbs(
        peese_merged_df.cases_per_100k.values.tolist(),
        color_bins,
        mode='equalcount'
    )

    if len(cases_rgbs['cuts']['rgb_colors']) != color_bins:
        try_color_bins = [
            bin_count+i for i, bin_count in enumerate(range(1, color_bins+1))
        ]
        for equal_count_bins in try_color_bins:
            current_bin_count = len(cases_rgbs['cuts']['rgb_colors'])
            print(f' Desired bins: {color_bins} | Current bins: {current_bin_count}')
            cases_rgbs = get_rgbs(
                peese_merged_df.cases_per_100k.values.tolist(),
                equal_count_bins,
                mode='equalcount'
            )
            if len(cases_rgbs['cuts']['rgb_colors']) == color_bins:
                current_bin_count = len(cases_rgbs['cuts']['rgb_colors']) 
                print(f' Desired bins: {color_bins} | Current bins: {current_bin_count}')
                print('  Equal Count Success!')
                need_equal_interval = False
                break
            else:
                need_equal_interval = True
    else:
        print(' success')
        need_equal_interval = False

    if need_equal_interval:
        print('Falling back to equal interval color bin')
        cases_rgbs = get_rgbs(
            peese_merged_df.cases_per_100k.values.tolist(),
            color_bins,
            mode='equalinterval'
        )

    print(f'\nWriting colormap PEESE JSON:\n {colormap_json}')
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
