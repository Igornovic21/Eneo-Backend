import requests, json

from datetime import datetime
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from constants.config import ONA_PROJECT
from constants.ona_api import ONA_DATA_URL, ONA_PROJECT_URL
from utils.logger import logger

from config.models import Credential
from region.models import Region
from record.models import Record
from itinary.models import Itinary

class Command(BaseCommand):
    help = 'Get list of data for any FormConfig Save in th App'

    def add_arguments(self, parser):
        parser.add_argument('--verbose', action='store_true', help='Enable verbose mode')

    def handle(self, *args, **kwargs):
        credential = Credential.objects.first()
        fields = credential.fields.split("/")
        ona_forms = []
        HEADERS = {
            "Authorization": "Token {}".format(credential.ona_token)
        }
        
        response = requests.get(ONA_PROJECT_URL, headers=HEADERS)
        if response.status_code != 200:
            self.stdout.write(self.style.ERROR("Error when getting list of forms"))
        
        for project in response.json():
            if project["name"] == ONA_PROJECT:
                ona_forms = project["forms"]
                    
        for form in ona_forms:
            response = requests.get(ONA_DATA_URL.format(form["formid"]), headers=HEADERS)
            
            if response.status_code != 200:
                self.stdout.write(self.style.ERROR("Error when getting {} form datas").format(form["title"]))
            
            for data in response.json():
                ona_id = data["id"]

                if Record.objects.only("ona_id").filter(ona_id=ona_id).exists():
                    self.stdout.write(self.style.WARNING("Record {} already saved".format(ona_id)))
                
                result = {}
                action = data["action"]
                collector = data["Collecteur"]
                enterprise = data["entreprise_collecteur"]
                date = datetime.fromisoformat(data["date"])
                latitude = data["_geolocation"][0]
                longitude = data["_geolocation"][1]

                for field in fields:
                    if field in data.keys():
                        result[field] = data[field]
                    else:
                        result[field] = ""
                
                record, _ = Record.objects.get_or_create(ona_id=ona_id)
                record.data = json.dumps(result)
                record.full_data = json.dumps(data)
                record.action = action
                record.collector = collector
                record.enterprise = enterprise
                record.date = date
                point = Point(longitude, latitude)
                results = Itinary.objects.only("boundary").filter(boundary__contains=point)
                if results.exists():
                    record.itinary = results[0]
                    record.save()
                else:
                    self.stdout.write("No itinary found for this submission {}".format(ona_id))
            return self.stdout.write(self.style.SUCCESS("All data loaded for configured forms"))
