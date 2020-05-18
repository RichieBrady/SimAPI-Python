FROM python:3.7-slim-buster

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends \
               wget \
               sudo

RUN useradd -rm -d /home/router -s /bin/bash -g root -G sudo -u 1003 router
COPY run.sh /run.sh

RUN chmod +x /run.sh

USER router
RUN mkdir /home/router/code
WORKDIR /home/router/code
COPY . /home/router/code/

ENV PATH=/home/router/.local/bin:$PATH

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
