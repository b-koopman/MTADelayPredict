# Docker files for running the project

You can build these and add them to ECR, or can also run them manually.

## Secrets

Make sure to populate secrets.txt with all your information.  Ideally this would use a secrets server, but this will do for now.

## Base
To build the base Dockerfile:

**Build**
<code>
sudo docker build --tag mtadelaypredict-base:1.0 base/
</code>

## rt_data

For downloading realtime gtfs feeds and pushing to S3 for now

**Build**
<code>
docker build --build-arg mta_api_key=<MTA_API_KEY> --build-arg s3_bucket=<S3_BUCKET> --build-arg aws_access_key_id=<AWS_ACCESS_KEY_ID> --build-arg aws_secret_access_key=<AWS_SECRET_ACCESS_KEY> --tag mtadelaypredict-rt_data:1.0 rt_data/
</code>

**Run**
This is a little hacky, but runs a loop of fetching GTFS files to s3.
<code>
docker run mtadelaypredict-rt_data:1.0
</code>

## Notebook
For running development notebook
<code>
docker build --tag mtadelaypredict-notebook:1.0 notebook/
</code>
