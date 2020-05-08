FROM ubuntu:16.04

RUN apt-get update && apt-get -y install \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LO http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash Miniconda3-latest-Linux-x86_64.sh -bfp /miniconda3 && \
    rm Miniconda3-latest-Linux-x86_64.sh
ENV PATH=/miniconda3/bin:${PATH}

RUN conda update -y conda && \
    conda install python=3.6.7

COPY requirements.txt /requirements.txt
RUN python -m pip install -r /requirements.txt && \
    rm /requirements.txt
