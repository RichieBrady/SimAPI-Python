FROM python:3.7-slim-buster

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends \
               wget \
               vim \
               sudo \
               iputils-ping \
               curl

RUN useradd -rm -d /home/deb -s /bin/bash -g root -G sudo -u 1003 deb
COPY run.sh /run.sh

RUN chmod +x /run.sh

USER deb
RUN mkdir /home/deb/code
WORKDIR /home/deb/code
COPY . /home/deb/code/

ENV PATH /root/miniconda/bin:$PATH
ENV PATH /home/deb/miniconda/bin:$PATH

RUN pip install -r requirements.txt
