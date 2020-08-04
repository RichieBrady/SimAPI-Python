BROKER_URL = 'amqp://user:pass@broker:5672/vhost'
CELERY_RESULT_BACKEND = 'db+postgresql://postgres:backend@backend/backend_db'
CELERY_TASK_ROUTES = {'router_tasks.*': {'queue': 'router'}}
