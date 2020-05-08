FROM mtadelaypredict-base

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
    
COPY notebook/requirements.txt /requirements.txt

RUN python -m pip install -r /requirements.txt && \
    rm /requirements.txt