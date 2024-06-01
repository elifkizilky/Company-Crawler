#!/bin/bash
celery -A celery_tasks worker --concurrency=27 --loglevel=info 