import json
from datetime import datetime
from django.core.management.base import BaseCommand

from record.models import Record

class Command(BaseCommand):
    help = 'Update all record date'

    def add_arguments(self, parser):
        parser.add_argument('--verbose', action='store_true', help='Enable verbose mode')
        
    def handle(self, *args, **kwargs):
        records = Record.objects.all()
        
        for record in records:
            data = json.loads(record.data)
            record.date = datetime.fromisoformat(data["date"])
            record.save()
        
        self.stdout.write("Records dates updated")
        
       