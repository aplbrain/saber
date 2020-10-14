""" 
Function to upload and generate download links for output files.
"""

import logging
import re
import os
import datetime

import boto3
from botocore.exceptions import ClientError


def upload_file(file_name, bucket, key):
    s3 = boto3.client("s3")
    try:
        response = s3.upload_file(file_name, bucket, key)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def delete_folder(bucket, prefix):
    s3 = boto3.resource("s3")
    try:
        bucket = s3.Bucket(bucket)
        bucket.objects.filter(Prefix=prefix + "/").delete()
    except ClientError as e:
        logging.error(e)
        return False
    return True


def generate_download_link(bucket, key, expiration):
    s3 = boto3.client("s3")
    try:
        response = s3.generate_presigned_url(
            "get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=expiration
        )
    except ClientError as e:
        logging.error(e)
        return
    return response


def get_log_stream_name(dag_id, log_dir):
    pattern = re.compile("'logStreamName': '(.*?)'")
    for logs in os.listdir(log_dir):
        if dag_id in logs:
            for root, _, files in os.walk(os.path.join(log_dir, logs)):
                if files:
                    with open(os.path.join(root, files[0]), "r") as log_file:
                        log_content = log_file.read()
                    match = re.search(pattern, log_content)
                    if match:
                        return match.group(1)


def get_batch_logs(dag_id, log_dir, **kwargs):
    log_stream = get_log_stream_name(dag_id, log_dir)
    if log_stream:
        log_buffer = []
        logs = boto3.client("logs")
        events = logs.get_log_events(
            logGroupName="/aws/batch/job", logStreamName=log_stream, **kwargs
        )["events"]
        for event in events:
            seconds = event["timestamp"] / 1000
            time = datetime.datetime.fromtimestamp(seconds).strftime(
                "%m/%d/%Y %H:%M:%S"
            )
            log_buffer.append(time + " " * 8 + event["message"])
    return "\n".join(log_buffer)
