import boto3

from django.conf import settings


def get_s3_resource():
    return boto3.resource(
        "s3",
        region_name=settings.AWS_S3_REGION,
        use_ssl=True,
        aws_access_key_id=settings.AWS_S3_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_S3_SECRET_KEY,
    )


def get_s3_client():
    return boto3.client(
        "s3",
        region_name=settings.AWS_S3_REGION,
        use_ssl=True,
        aws_access_key_id=settings.AWS_S3_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_S3_SECRET_KEY,
    )


def delete_file_from_s3(filepath):
    s3 = get_s3_resource()
    s3.delete_object(Bucket=settings.AWS_S3_BUCKET, Key=filepath)


def save_text_file_to_s3(filepath, data_string):
    s3 = get_s3_client()
    s3.put_object(Bucket=settings.AWS_S3_BUCKET, Key=filepath, Body=data_string)


def load_text_file_from_s3(filepath):
    s3 = get_s3_resource()
    s3_object = s3.Object(settings.AWS_S3_BUCKET, filepath)
    object_as_streaming_body = s3_object.get()["Body"]
    object_as_bytes = object_as_streaming_body.read()
    return object_as_bytes
