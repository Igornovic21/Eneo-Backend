from django.apps import AppConfig

class RecordConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'record'

    def ready(self) -> None:
        from django.conf import settings

        from apscheduler.schedulers.background import BackgroundScheduler
        from django_apscheduler.jobstores import DjangoJobStore
        from apscheduler.triggers.interval import IntervalTrigger
        from apscheduler.triggers.cron import CronTrigger
        from datetime import datetime, timedelta

        from utils.logger import logger

        from record.scheduler import get_record_job, get_csv_record_job, delete_old_job_executions
        if settings.DEBUG:
            run_time = datetime.now() + timedelta(minutes=1)
            scheduler = BackgroundScheduler()
            # scheduler.add_jobstore(DjangoJobStore(), "default")

            scheduler.add_job(
                get_record_job,
                trigger=CronTrigger(hour=0, minute=0),
                id="get_record_job",
                max_instances=1,
                replace_existing=True,
            )
            logger.info("Added job 'get_record_job' at midnight interval.")

            scheduler.add_job(
                get_record_job,
                trigger="date",
                run_date=run_time,
                id="get_record_job_once",
                replace_existing=True,
            )
            logger.info("Added 'get_record_job_once'. on startup once time")

            scheduler.add_job(
                get_csv_record_job,
                trigger="date",
                run_date=run_time,
                id="get_csv_record_job",
                replace_existing=True,
            )
            logger.info("Added job 'get_csv_record_job'. on startup once time")

            # scheduler.add_job(
            #     delete_old_job_executions,
            #     trigger=IntervalTrigger(days=1),
            #     id="delete_old_job_executions",
            #     max_instances=1,
            #     replace_existing=True,
            # )

            # logger.info("Starting scheduler...")
            # scheduler.start()
            # logger.info("Starting started")
            
            try:
                logger.info("Starting scheduler...")
                scheduler.start()
                logger.info("Starting started")
            except Exception as e:
                print(e)
                logger.info("Stopping scheduler...")
                scheduler.shutdown()
                logger.info("Scheduler shut down successfully!")
        return super().ready()
