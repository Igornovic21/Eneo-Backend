from django.apps import AppConfig


class RegionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'region'

    def ready(self) -> None:
        from region import signals
        return super().ready()