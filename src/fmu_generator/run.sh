#!/bin/bash

python generator_api.py \
& celery -A generator_tasks worker -l info --concurrency=1 --queues=gen