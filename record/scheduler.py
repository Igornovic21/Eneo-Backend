from datetime import datetime

from django_apscheduler.models import DjangoJobExecution

from utils.logger import logger

def get_record_job():
    logger.info(f"Job Record Started {datetime.now()}")
    print(f"Job Record Started {datetime.now()}")

def delete_old_job_executions(max_age=172800):
    logger.info("Delete older job than 2 days in the historic")
    DjangoJobExecution.objects.delete_old_job_executions(max_age)
