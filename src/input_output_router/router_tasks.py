from celery import Celery
from pathlib import Path
import celeryconfig
import subprocess
import requests
import time
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

app = Celery('simulator_tasks')
app.config_from_object(celeryconfig)


def write_json(params, filename):
    with open(filename, 'w') as f:
        data_dict = {"model_params": [params]}

        logger.info("HERE: {0}".format(str(data_dict)))
        json.dump(data_dict, f, indent=4)


@app.task
def set_model(model_params):
    model_name = model_params['model_name']
    step_size = model_params['step_size']
    final_time = model_params['final_time']
    fmu_path = '/home/deb/code/fmu_location/' + model_name + '/' + model_name + '.fmu'
    auth_token = model_params['Authorization']
    logger.info(f'PATH TO FMU IN SET_MODEL: {fmu_path}')
    time.sleep(5)

    swarm_check = Path('/home/deb/code/isSwarm.txt')
    if not swarm_check.exists():
        init_url = 'http://web:8000/init_model/'
        hostname = subprocess.getoutput("cat /etc/hostname")
        model_name = model_name + '_' + hostname
        logger.info('MODEL_NAME IN EXTRA CONTAINER: {0}'.format(model_name))

        init_data = {
            'model_name': model_name,  # change name each time script is run!
            'step_size': step_size,  # step size in seconds. 600 secs = 10 mins
            'final_time': final_time,  # 24 hours = 86400 secs
            'container_id': hostname
        }
        header = {'Authorization': auth_token}
        requests.post(init_url, headers=header, data=init_data)

    params = {'model_name': model_name,
              'step_size': step_size,
              'final_time': final_time,
              'fmu_path': fmu_path,
              'Authorization': auth_token}

    write_json(params, 'fmu_data/model_params.json')

    if swarm_check.exists():
        os.system('rm /home/deb/code/isSwarm.txt')


@app.task
def post_output(output_json, header):
    output_url = 'http://web:8000/output/'

    header['Content-Type'] = 'application/json'

    r = requests.post(output_url, headers=header, data=output_json)
    logger.info(f'post_output -> request status {r.status_code}')
    logger.info(f'post_output -> request text {r.text}')
    return r.text
