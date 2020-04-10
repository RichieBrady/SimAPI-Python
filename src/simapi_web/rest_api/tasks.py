from celery import shared_task
from celery.utils.log import get_task_logger
import requests
import json

from rest_api import models

logger = get_task_logger(__name__)


@shared_task
def post_model(data):
    logger.info(f'post_model data {data}')
    model_name = data['model_name']
    auth_t = data['Authorization']
    logger.info(f'post_model data AUTH {auth_t}')
    model = models.FmuModel.objects.get(model_name=model_name)

    # TODO set simulator to hostname for multiple containers
    if model is not None:
        url = 'http://generator:8000/file_upload/{0}'.format(model_name)
        logger.info(f'post_model url {url}')

        epw_file = open(model.epw_file.path, 'rb')
        idf_file = open(model.idf_file.path, 'rb')

        file = {'epw': (model_name + '.epw', epw_file, 'application/octet-stream'),
                'idf': (model_name + '.idf', idf_file, 'application/octet-stream'),
                'json': (None, json.dumps(data), 'application/json')}

        r = requests.post(url, files=file)

        epw_file.close()
        idf_file.close()

        return "{0} : {1}".format(r.content, r.status_code)


@shared_task
def send_fmu(data):
    logger.info(f'send_fmu data {data}')

    url = 'http://generator:8000/fmu_to_simulator/{0}'.format(data['model_name'])

    r = requests.post(url=url, json=data)

    return "{0} | {1}".format(r.content, r.status_code)


@shared_task
def post_input(data):
    logger.info(f'post_input data {data}')
    # TODO create middleware to add DateTime to data
    input_instance = models.Input.objects.last()

    if input_instance is not None:
        url = 'http://{0}:8000/model_input'.format(data['container_id'])
        logger.info(f'post_input url {url}')
        headers = {'Content-type': 'application/json'}
        data = {'time_step': data['time_step']}
        r = requests.post(url=url, json=json.dumps(data), headers=headers)


@shared_task
def post_router_input(data):
    logger.info(f'post_input data {data}')
    # TODO create middleware to add DateTime to data
    input_instance = models.Input.objects.last()

    if input_instance is not None:
        url = 'http://router:8000/route_input/{0}'.format(data['container_id'])
        logger.info(f'post_input url {url}')
        headers = {'Content-type': 'application/json'}
        data = {'time_step': data['time_step']}
        r = requests.post(url=url, json=json.dumps(data), headers=headers)

        return r.status_code
