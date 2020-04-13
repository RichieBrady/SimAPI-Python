FROM python:3

ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y --no-install-recommends \
               iputils-ping \
               net-tools \
               nmap

RUN mkdir /code
RUN mkdir /code/Media
WORKDIR /code
COPY . /code
RUN pip install -r requirements.txt