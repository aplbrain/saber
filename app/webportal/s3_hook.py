""" 
Function to upload and generate download links for output files.
"""

import boto3
import logging
from botocore.exceptions import ClientError

def upload_file(file_name, bucket, key):
    s3 = boto3.client("s3")
    try:
        response = s3.upload_file(filepath, bucket, key)
    except ClientError as e:
        logging.error(e)
        return False
    return True

def generate_download_link(bucket, key, expiration):
    s3 = boto3.client("s3")
    try:
        response = s3.generate_presigned_url('get_object', Params={'Bucket': bucket, "Key": key}, ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return
    return response
