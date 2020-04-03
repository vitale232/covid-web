from datetime import datetime
import os

import boto3
from botocore.exceptions import ClientError


def upload_file_to_s3(file_name, bucket, object_name=None, extra_args=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :param extra_args: a dictionary specifying extra args to set while uploading the file.
        Often used to set metadata. For more options, see
        https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html
    
    :return: True if file was uploaded, else False
    """
    print(f'\nUploading file:\n {file_name}')
    print(f'Bucket name:\n {bucket}')
    if object_name:
        print(f'Object name:\n {object_name}')
    if extra_args:
        print(f'Extra args:\n {extra_args}')
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name, ExtraArgs=extra_args)
    except ClientError as e:
        print(e)
        return False
    return True

def upload_county_simple():
    """Used during dev"""
    DIST_DIR = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        '..',
        '..',
        'dist'
    ))

    county_simple_gzip = os.path.join(DIST_DIR, 'county_cases_simple.geojson.gz')
    s3_bucket = 'covid-19-geojson'
    object_name = 'upload_test.geojson.gz'
    extra_args = {
        'ContentType': 'application/json',
        'ContentEncoding': 'gzip',
        'ACL': 'public-read',
    }

    print(f'\nUploading file:\n {county_simple_gzip}')
    print(f'Bucket name:\n {s3_bucket}')
    if object_name:
        print(f'Object name:\n {object_name}')
    print(f'Extra args:\n {extra_args}')

    success = upload_file_to_s3(
        county_simple_gzip,
        s3_bucket,
        object_name=object_name,
        extra_args=extra_args
    )
    print(f'Upload successful?\n {success}')


    peese_gzip = os.path.join(
        DIST_DIR,
        'peese',
        'peese-latest.geojson.gz'
    )
    peese_gzip_object_name = 'peese-latest.geojson.gz'

    print(f'\nUploading file:\n {peese_gzip}')
    print(f'Bucket name:\n {s3_bucket}')
    if object_name:
        print(f'Object name:\n {object_name}')
    print(f'Extra args:\n {extra_args}')

    success = upload_file_to_s3(
        peese_gzip,
        s3_bucket,
        object_name=peese_gzip_object_name,
        extra_args=extra_args
    )
    print(f'Upload successful?\n {success}')


    peese_slim_gzip = os.path.join(
        DIST_DIR,
        'peese',
        'peese-latest-slim.geojson.gz'
    )
    peese_slim_object_name = 'peese-latest-slim.geojson.gz'
    print(f'\nUploading file:\n {peese_slim_gzip}')
    print(f'Bucket name:\n {s3_bucket}')
    if peese_slim_object_name:
        print(f'Object name:\n {peese_slim_object_name}')
    print(f'Extra args:\n {extra_args}')

    success = upload_file_to_s3(
        peese_slim_gzip,
        s3_bucket,
        object_name=peese_slim_object_name,
        extra_args=extra_args
    )
    print(f'Upload successful?\n {success}')


def main():
    start_time = datetime.now()
    print(f'\nRunning script : {os.path.abspath(__file__)}')
    print(f'Start time     : {start_time}')

    upload_county_simple()

    end_time = datetime.now()
    print(f'\nScript completed : {end_time}')
    print(f'Run time         : {end_time-start_time}\n')


if __name__ == '__main__':
    main()
