FROM python:3.7-slim-buster

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends \
               wget \
               vim \
               sudo \
               iputils-ping \
               unzip \
               libx11-6

RUN useradd -rm -d /home/deb -s /bin/bash -g root -G sudo -u 1002 deb
COPY run.zip /run.zip
RUN unzip /run.zip
RUN chmod +x /run.sh

USER deb
RUN mkdir /home/deb/code
RUN mkdir /home/deb/code/fmu_data
WORKDIR /home/deb/code
COPY . /home/deb/code/
RUN mkfifo /home/deb/code/proc_pipe

RUN wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh \
    && bash ~/miniconda.sh -b -p ~/miniconda \
    && rm ~/miniconda.sh

RUN wget https://github.com/NREL/EnergyPlus/releases/download/v9.3.0/EnergyPlus-9.3.0-baff08990c-Linux-x86_64.tar.gz -O ~/EnergyPlus-9.3.0-baff08990c-Linux-x86_64.tar.gz \
    && mkdir /home/deb/EnergyPlus \
    && tar -xzvf ~/EnergyPlus-9.3.0-baff08990c-Linux-x86_64.tar.gz -C  ~/EnergyPlus/ \
    && rm ~/EnergyPlus-9.3.0-baff08990c-Linux-x86_64.tar.gz \
    && mv ~/EnergyPlus/EnergyPlus-9.3.0-baff08990c-Linux-x86_64/* ~/EnergyPlus/ \
    && rm -d ~/EnergyPlus/EnergyPlus-9.3.0-baff08990c-Linux-x86_64

ENV PATH /root/miniconda/bin:$PATH
ENV PATH /home/deb/miniconda/bin:$PATH
ENV PATH /home/deb/EnergyPlus:$PATH

RUN conda update conda \
   && conda update --all \
   && conda create --name simapi37 -y \
   && activate simapi37 \
   && conda config --append channels conda-forge \
   && conda install -c conda-forge assimulo \
   && conda install -c https://conda.binstar.org/chria pyfmi \
   && pip install -r requirements.txt