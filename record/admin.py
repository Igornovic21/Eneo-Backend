from django.contrib import admin

from record.models import Record, Collector, Action, Enterprise, DeliveryPoint, Location

# Register your models here.
admin.site.register(Record)
admin.site.register(Collector)
admin.site.register(Action)
admin.site.register(Enterprise)
admin.site.register(Location)
admin.site.register(DeliveryPoint)