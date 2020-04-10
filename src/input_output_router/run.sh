#!/bin/bash

python router_api.py \
& celery -A router_tasks worker -l info --concurrency=2 --queues="router"
