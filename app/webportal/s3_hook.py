""" 
Function to upload and generate download links for output files.
"""

import logging
import re
import os
import datetime

import boto3
from botocore.exceptions import ClientError

# List of ECR Repositories to not list on webapp.
REPOSITORY_IGNORE = [
    "aplbrain/boss-access",
    "aplbrain/i2gdetect",
    "aplbrain/i2gdetect_gpu",
    "aplbrain/i2gseg",
    "boss-images",
    "boss-speed-test-images",
    "colocar/colocard",
    "colocar/keycloak-proxy.js",
    "colocar/mongo-grove",
    "microns-agents",
    "microns-syn",
    "microns-unet",
    "microns-unet-gpu",
    "nap/ingest",
    "nap/nri",
    "nap/test",
    "nap/trace-to-edgeframe",
    "test"
]

def upload_file(file_name, bucket, key):
    s3 = boto3.client("s3")
    try:
        response = s3.upload_file(file_name, bucket, key)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def download_file(bucket, key, directory):
    s3 = boto3.client("s3")
    fn = key.split('/')[-1]
    path = os.path.join(directory, fn)
    with open(path, 'wb') as fp:
        try:
            s3.download_fileobj(bucket, key, fp)
        except ClientError as e:
            logging.error(e)
            return False
    return True


def download_files(buckets, keys, directory):
    s3 = boto3.client("s3")
    for bucket, key in zip(buckets, keys):
        path = os.path.join(directory, key)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as fp:
            s3.download_fileobj(bucket, key, fp)


def delete_folder(bucket, prefix):
    s3 = boto3.resource("s3")
    try:
        bucket = s3.Bucket(bucket)
        bucket.objects.filter(Prefix=prefix + "/").delete()
    except ClientError as e:
        logging.error(e)
        return False
    return True


def get_log_stream_name(dag_id, execution_date, log_dir):
    pattern = re.compile("'logStreamName': '(.*?)'")
    dag_logs = os.path.join(log_dir, dag_id+".0", 'algorithm.0')
    if not os.path.isdir(dag_logs):
        # TODO: Return Airflow Log
        print("dag log not found")
        return 
    for dates in os.listdir(dag_logs):
        if execution_date in dates:
            for root, _, files in os.walk(os.path.join(dag_logs, dates)):
                if files:
                    with open(os.path.join(root, files[0]), "r") as log_file:
                        log_content = log_file.read()
                    match = re.search(pattern, log_content)
                    if match:
                        return match.group(1)


def get_batch_logs(dag_id, execution_date, log_dir, **kwargs):
    log_stream = get_log_stream_name(dag_id, execution_date, log_dir)
    if log_stream:
        log_buffer = []
        logs = boto3.client("logs")
        try:
            events = logs.get_log_events(
                logGroupName="/aws/batch/job", logStreamName=log_stream, **kwargs
            )["events"]
        except ClientError as e:
            logging.error(e)
            return
        for event in events:
            seconds = event["timestamp"] / 1000
            time = datetime.datetime.fromtimestamp(seconds).strftime(
                "%m/%d/%Y %H:%M:%S.%f"
            )[:-3]
            log_buffer.append(time + " " * 8 + event["message"])
        return "\n".join(log_buffer)


def list_repositories():
    repository_names = []
    ecr = boto3.client("ecr")
    repositories = ecr.describe_repositories()['repositories']
    for rep in repositories:
        if rep['repositoryName'] not in REPOSITORY_IGNORE:
            repository_names.append(rep['repositoryName'])
    return sorted(repository_names)


def list_images(repository):
    image_tags = []
    ecr = boto3.client("ecr")
    images = ecr.describe_images(repositoryName=repository, filter={"tagStatus": "TAGGED"})['imageDetails']
    sorted_images = sorted(images, key=lambda x: x['imagePushedAt'], reverse=True)
    for image in sorted_images:
        for tag in image["imageTags"]:
            if tag != "s3":
                image_tags.append(tag)
    return image_tags
