import boto3
import os

bucket_name = os.getenv('S3_BUCKET')
aws_access_key_id = os.getenv('aws_access_key_id')
aws_secret_access_key = os.getenv('aws_secret_access_key')
test_filename = 'test_file.txt'
objectname = 'test/test_file.txt'

s3_client = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

with open(test_filename, 'w') as f:
    f.write("Hello World!\n")

try:
    with open(test_filename, 'rb') as f:
        response = s3_client.upload_fileobj(f, bucket_name, objectname)

    print("Success!")
except Exception as e:
    print("Failed to upload file with Exception\n{}".format(e))
