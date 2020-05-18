import json

from bottle import request, route, run
from celery.utils.log import get_task_logger

from router_tasks import post_input, post_output

logger = get_task_logger(__name__)


@route('/route_input/<container_id>', method='POST')
def route_input(container_id):
    post_input.apply_async((request.json, container_id), queue='router', routing_key='router')


@route('/route_output/', method='POST')
def route_output():
    output_data = json.loads(request.json)
    post_output.apply_async((output_data,), queue='router', routing_key='router')


run(host='0.0.0.0', port=8000, debug=True, reloader=True)
