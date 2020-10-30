# SimApi Building Energy Co-Simulation Platform

This project aims to update and re-design an existing project found at [SimAPI repo](https://github.com/ElsevierSoftwareX/SOFTX_2018_29).
The objective of this project is to re-design and update the linked project using python, Django rest framework, 
Celery, Docker, and pyFMI to create an application capable of co-simulation between an Energy Management System and
a Functional Mock-Up Unit.

## Prerequisites
Version of docker and docker-compose 
```
Docker
- version >= 18.09.9

Docker-compose
- version >= 1.25.0
```

### Deployment
It should be noted that simapi is a work in progress and the instructions to deploy the system reflect this. 

To build and deploy the containers navigate to src folder and type in a terminal

```
docker-compose build
```
Once the build command is finished bring up the db container to initialize it. 
Initializing the database container first ensures that no errors occur, as db initialization
can take longer than bringing the rest of the system online.

```
docker-compose up db
```
The message below signals that the database has been initialized.
```
database system is ready to accept connections
```
use ctrl-c to bring the database container down. 

Next bring the whole system up

For a single simulation run
```
docker-compose up
```
To run multiple simulations
```
docker-compose up --scale simulator=n
```
where n is the desired number of simulations

##### Simulating FMUs 
Use docker-compose up or --scale to run the desired number of simulator containers.

Once all containers are running, edit the **example_simulate.py** file at the root of the project.
```python
model_name = "test"  # unique for each simulation run
model_count = 1  # must be <= to scaling factor
step_size = 900  # in seconds
final_time = 24  # in hours
idf_path = "data_files/new.idf"  # example idf
epw_path = "data_files/new.epw"  # example weather file
csv = ["data_files/new1.csv"]  # inputs for simulation, can add csv inputs for each simulation
```

Once all fields have been edited, run the script and communication will start with the api container.

##### Outputs
Outputs will print in the terminal where **example_simulate.py** is running and internal communication 
of the system can be seen in the terminal window where the docker-compose up command was run.

A new folder will also be created in the project root folder called **output_csv**. 
This folder will contain the csv output files. 

##### Workflow
Use docker-compose up --scale simulator=n to test different values for n, higher values for n will be memory intensive
and may cause issues depending on host machine specs. The system has been tested with up to a maximum of 65 simulations 
using approximately 13 GiB of memory. The memory usage mentioned is based on running the example idf, more realistic
models will require more memory and can crash the host machine if the user is not careful with available memory. 

When the simulation(s) have finished, the containers will reset and will be ready to run again.
When running a new simulation the model should be given a unique name. If running multiple simulations
a single name is adequate.

To wipe the data from the database and containers run.

```
docker-compose down --volumes
```

If testing the system multiple times with different number of simulator containers it is a good idea, when finished, 
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






