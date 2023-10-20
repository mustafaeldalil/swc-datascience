import boto3
import os


def get_s3_resource():
    return boto3.resource(
        "s3",
        region_name=os.getenv("AWS_S3_REGION"),
        use_ssl=True,
        aws_access_key_id=os.getenv('AWS_S3_ACCESS_KEY'),
        aws_secret_access_key=os.getenv('AWS_S3_SECRET_KEY'),
    )


def load_text_file_from_s3(filepath):
    s3 = get_s3_resource()
    s3_object = s3.Object(os.getenv('AWS_S3_BUCKET'), filepath)
    object_as_streaming_body = s3_object.get()["Body"]
    object_as_bytes = object_as_streaming_body.read()
    return object_as_bytes