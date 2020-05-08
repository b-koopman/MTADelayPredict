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
DANGER:  This will expose your MTA KEY and AWS KEY for the IAM to anyone with access to the shell history, and will be stored in one of the docker layers.  The ideal way to do this is to use the secrets server, but this gets something up and running quickly.

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

**Build**
<code>
docker build --tag mtadelaypredict-notebook:1.0 notebook/
</code>

**Run**
Right now this assumes that you already have a mount with a local git repository already set up.

TODO: Move some of this incantation inside the docker file
<code>
DATA_MOUNT=<MY_DATA_MOUNT> PROJECT_MOUNT=<MY_PROJECT_MOUNT> docker run -i -t -p 8888:8888  -v $DATA_MOUNT:/data -v $PROJECT_MOUNT:/opt/project -v /tmp:/local/tmp --env-file secrets.txt sklearn-notebook:1.0 /bin/bash -c"/miniconda3/bin/jupyter lab --notebook-dir=/opt/project --ip='*' --port=8888 --no-browser --allow-root"
</code>