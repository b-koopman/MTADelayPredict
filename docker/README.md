# Docker files for running the project

You can build these and add them to ECR, or can also run them manually.

## Secrets

Make sure to populate secrets.txt with all your information.  Ideally this would use a secrets server, but this will do for now.

## Base
To build the base Dockerfile:

### Build
<code>
sudo docker build --tag mtadelaypredict-base:1.0 base/
</code>

## rt_data

For downloading realtime gtfs feeds and pushing to S3 for now

### Build
<code>
docker build --env-file secrets.txt --tag mtadelaypredict-rt_data:1.0 rt_data/
</code>

## Notebook
For running development notebook
<code>
docker build --env-file secrets.txt --tag mtadelaypredict-notebook:1.0 notebook/
</code>
