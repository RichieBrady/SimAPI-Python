# SimApi Building Energy Co-Simulation Platform

This project aims to update and re-design an existing project found at [SimAPI repo](https://github.com/ElsevierSoftwareX/SOFTX_2018_29).
The objective of this project is to re-design and update the linked project using python, Django rest framework, 
Celery, Docker, and pyFMI to create an application capable of co-simulation between an Energy Management System and
a Functional Mock-Up Unit. The end goal is to deploy the project on a Docker swarm and simulate multiple fmu models
simultaneously. 

## Prerequisites
Version of docker and docker-compose 
```
Docker
- version >= 18.09.9

Docker-compose
- version >= 1.25.0
```

## Instructions
To build and run the containers navigate to src folder and type in a terminal

```
docker-compose build

Once build is finished bring up the db container to initialize it. Only needed for the first time after building.

docker-compose up db

The message below signals that the database has been initialized.
database system is ready to accept connections

use ctrl-c to bring the database container down.

Next bring the whole system up

For a single simulation run

docker-compose up

To run multiple simulations run 
docker-compose up --scale simulator=n

where n is the desired number of simulations

```

### GUI
Below is a screenshot of the user interface. It's very basic but makes it easier to run the system for testing and does 
not represent the user experience intended for the final project. 
![User Interface](doc/gui.png)

##### Input Fields
Model Name: Any string value. Must be unique for generating different FMUs

Model Count: Number of simulator containers currently running

Step Size: Integer value corresponding to length of time in seconds of each time step

Final Time: Float value corresponding to length of time in hours the simulation spans. Min value = 24.0. 

##### Buttons
Upload idf: Opens a file select window. Choose .idf navigate to data_files folder and select new.idf

Upload epw: Opens a file select window. Choose .epw navigate to data_files folder and select new.epw



Upload cvs: Opens file select window, navigate to data_files folder and select one of the csv files new.csv, new1.csv, 
or new2.csv. If running multiple simulations up to a max of three ctrl select the three csv files. 

Validate Input: Click validate input to check if inputs are correct.

Generate: After input validated click to generate the FMU.

Initialize: After generating the FMU click to initialize the FMU

Simulate: After initializing the FMU click to run the simulation(s)

##### Instructions 
Use docker-compose up or --scale to run the desired number of simulator containers.

Once all containers are running, run the gui script **run_gui.py** located in the project root folder.

Fill all input fields and select .idf and .epw files. 

Validate the inputs are correct then, Generate, Initialize, Simulate.

Check for a confirmation message in the text area before clicking consecutive buttons.

##### Workflow
Use docker-compose up --scale simulator=n to test different values for n, higher values for n will be memory intensive
and may cause issues depending on host machine specs. The system has been tested with up to a maximum of 65 simulations 
using approximately 13 GiB of memory. It took roughly 30-40 minutes to complete all 65 simulations. 
The FMU simulated was generated with a final time of 24 (hours) and step size of 600 seconds (10 minutes per step).

Ensure that the model count value in the UI is the same as the value used to --scale the simulator container.
If no --scale command was used the value entered for model count should be 1.

When the simulation(s) have finished bring down the containers with ctrl-c. When running a new simulation the model should
be given a unique name.

To wipe the data from the database and containers run. 

```
docker-compose down --volumes
```
Then initialize the database again with
```
docker-compose up -d db 
```

If testing the system multiple times with different numbers of simulator containers it is a good idea, when finished, 
to wipe the data using **docker-compose down --volumes** and also run the command below to remove any hanging containers 
from the host machine. It may take sometime to complete a prune!
```
docker system prune
```
Hanging containers can quickly take up a lot of space. Warning when using this command if other containers separate from
this project are running.

## Project Development

If you would like to run the Django API or simulation scripts without docker the following steps are required.

1. Install python Anaconda

2. Create a virtual env python=3.7

3. Run conda commands

   conda config --append channels conda-forge
   
   conda install -c conda-forge assimulo
   
   conda install -c https://conda.binstar.org/chria pyfmi

4. pip install -r [dev_requirements.txt](doc/dev_requirements.txt) to install project dependencies

If running the Django project without Docker is all that is required then you can stop here. 

If you would also like to run simulation scripts then it is necessary to install energyPlus on your machine. 

Version 9 is required.

For windows installation see [energyPlus windows](https://energyplus.net/installation-windows)

For Linux installation see  [energyPlus Linux](https://energyplus.net/installation-linux)






