FROM mtadelaypredict-base:1.0

ARG mta_api_key
ENV mta_api_key=$mta_api_key

COPY requirements.txt /requirements.txt
RUN python -m pip install -r /requirements.txt && \
    rm /requirements.txt

COPY download_app.py /download_app.py

ARG s3_bucket
ENV S3_BUCKET=$s3_bucket
ARG aws_access_key_id
ENV aws_access_key_id=$aws_access_key_id
ARG aws_secret_access_key
ENV aws_secret_access_key=$aws_secret_access_key

CMD python download_app.py