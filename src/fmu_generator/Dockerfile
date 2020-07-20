FROM python:2.7-slim-buster

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends \
               wget \
               unzip \
               build-essential \
               sudo \
               iputils-ping

RUN useradd -rm -d /home/fmu -s /bin/bash -g root -G sudo -u 1001 fmu

COPY run.sh /run.sh
RUN chmod +x /run.sh
USER fmu

RUN mkdir /home/fmu/code
WORKDIR /home/fmu/code
COPY . /home/fmu/code/

ENV PATH=/home/fmu/.local/bin:$PATH


RUN pip install -r requirements.txt

RUN mkdir /home/fmu/code/energy \
    && mkdir /home/fmu/code/simulator \
    && mkdir /home/fmu/code/energy/test \
    && mkdir /home/fmu/code/fmu_test \
    && wget https://github.com/lbl-srg/EnergyPlusToFMU/releases/download/v3.0.0/EnergyPlusToFMU-v3.0.0.zip \
        -P /home/fmu/code/energy \
    && unzip /home/fmu/code/energy/EnergyPlusToFMU-v3.0.0.zip \
        -d /home/fmu/code/energy \
    && rm /home/fmu/code/energy/EnergyPlusToFMU-v3.0.0.zip \
    && rm energy/Scripts/EnergyPlusToFMU.py \
    && mv ./EnergyPlusToFMU.py energy/Scripts/ \
    && cd energy/Scripts/linux \
    && echo '\nTesting EnergyPlusToFMU batch files' \
    && ./test-c-exe.sh \
    && ./compile-c.sh ../../SourceCode/utility/get-address-size.c \
    && ls *.o \
    && ./link-c-exe.sh  test.exe  get-address-size.o \
    && ls  *.exe \
    && ./test.exe \
    && echo '\nEnd of tests\n'
