from django.contrib import admin

from record.models import Record, Collector, Action, Enterprise

# Register your models here.
admin.site.register(Record)
admin.site.register(Collector)
admin.site.register(Action)
admin.site.register(Enterprise)