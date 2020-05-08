FROM mtadelaypredict-base:1.0

# Copied from AWS sklearn docker files
RUN apt-get update && \
    apt-get -y install build-essential libatlas-dev git wget curl nginx jq libatlas3-base && \
    apt-get -y install chromium-driver

# Copied from AWS sklearn docker files, adding notebook
RUN conda update -y conda && \
    conda install -c conda-forge jupyterlab && \
    conda install -c conda-forge notebook && \
    conda install -c conda-forge pyarrow=0.14.1 && \
    conda install -c mlio -c conda-forge mlio-py=0.1 && \
    conda install -c anaconda scipy && \
    conda install selenium && \
    conda install protobuf
    
COPY requirements.txt /requirements.txt

RUN python -m pip install -r /requirements.txt && \
    rm /requirements.txt

ARG s3_bucket
ENV S3_BUCKET=$s3_bucket
ARG aws_access_key_id
ENV aws_access_key_id=$aws_access_key_id
ARG aws_secret_access_key
ENV aws_secret_access_key=$aws_secret_access_key
