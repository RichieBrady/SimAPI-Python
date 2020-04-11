from celery import Celery
import celeryconfig
import requests
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

app = Celery('router_tasks')
app.config_from_object(celeryconfig)


@app.task
def post_input(input_json, container_id):
    logger.info(f'route_input data {str(input_json)}')
    headers = {'Content-type': 'application/json'}
    url = 'http://{0}:8000/model_input'.format(container_id)
    r = requests.post(url, json=input_json, headers=headers)
    logger.info(f'post_input -> request status {str(r.status_code)}')

    return r.status_code


@app.task
def post_output(output_json):
    output_url = 'http://web:8000/output/'

    auth_t = output_json['Authorization']
    logger.info(f'post_output -> auth token {auth_t}')
    headers = {'Authorization': auth_t, 'Content-type': 'application/json'}

    logger.info(f'post_output -> headers {str(headers)}')
    r = requests.post(output_url, headers=headers, json=output_json)
    logger.info(f'post_output -> request status {r.status_code}')

    return r.text
