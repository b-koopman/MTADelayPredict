import boto3
import os
import requests
from datetime import datetime
import pytz
from io import BytesIO
import time

bucket_name = os.getenv('S3_BUCKET')
aws_access_key_id = os.getenv('aws_access_key_id')
aws_secret_access_key = os.getenv('aws_secret_access_key')
test_filename = 'test_file.txt'
object_name = 'test/test_file.txt'

mta_api_key = os.getenv('mta_api_key')

s3_client = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)


FEEDS = {1:'123456S',
         26:'ACEHS',
         16:'NQRW',
         21:'BDFM',
         2:'L',
         11:'SIR',
         31:'G',
         36:'JZ',
         51:'7'}


while True:
    try:
        for feed_id,lines in FEEDS.items():
            uri = "http://datamine.mta.info/mta_esi.php?key={}&feed_id={}".format(mta_api_key,feed_id)
            response = requests.get(uri)
#            print("Fetched from {}".format(uri))
            gtfs_file = BytesIO(response.content)
            ts = datetime.now(pytz.timezone('US/Eastern'))
            ts.strftime('%y%m%d_%H%M%S')
            object_name = 'status/{}/{}/{}/gtfs_{}_{}.gtfs'.format(lines,
                                                                   ts.strftime('%Y%m'),
                                                                   ts.strftime('%Y%m%d'),
                                                                   lines,
                                                                   ts.strftime('%Y%m%d_%H%M%S'))
            s3_response = s3_client.upload_fileobj(gtfs_file, bucket_name, object_name)
            #print("Uploaded to: {}  {}".format(bucket_name, object_name))
    except Exception as e:
        with open("failures.log", 'a') as f:
            f.write("Failed to fetch {} with {}\n".format(object_name, e))
    time.sleep(15)
