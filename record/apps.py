from django.apps import AppConfig

class RecordConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'record'

    def ready(self) -> None:
        from django.conf import settings

        from apscheduler.schedulers.background import BackgroundScheduler
        from django_apscheduler.jobstores import DjangoJobStore
        from apscheduler.triggers.interval import IntervalTrigger

        from utils.logger import logger

        from record.scheduler import get_record_job, delete_old_job_executions
        if settings.DEBUG:
            scheduler = BackgroundScheduler()
            scheduler.add_jobstore(DjangoJobStore(), "default")

            scheduler.add_job(
                get_record_job,
                trigger=IntervalTrigger(seconds=5),
                id="get_record_job",
                max_instances=1,
                replace_existing=True,
            )
            logger.info("Added job 'get_record_job'.")
            scheduler.add_job(
                delete_old_job_executions,
                trigger=IntervalTrigger(days=1),
                id="delete_old_job_executions",
                max_instances=1,
                replace_existing=True,
            )

            # try:
            #     logger.info("Starting scheduler...")
            #     scheduler.start()
            #     logger.info("Starting started")
            # except KeyboardInterrupt:
            #     logger.info("Stopping scheduler...")
            #     scheduler.shutdown()
            #     logger.info("Scheduler shut down successfully!")
        return super().ready()
