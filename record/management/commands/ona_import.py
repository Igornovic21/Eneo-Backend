import requests, json

from datetime import datetime
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from constants.config import ONA_PROJECTS
from constants.ona_api import ONA_DATA_URL, ONA_PROJECT_URL

from config.models import Credential
from record.models import Record, Collector, Action, Enterprise
from itinary.models import Itinary
from region.constants import SRID
from utils.ona_json_to_models import ona_to_models

class Command(BaseCommand):
    help = 'Get list of data for any FormConfig Save in th App'

    def add_arguments(self, parser):
        parser.add_argument('--verbose', action='store_true', help='Enable verbose mode')

    def handle(self, *args, **kwargs):
        credential = Credential.objects.first()
        target_forms = []
        HEADERS = {
            "Authorization": "Token {}".format(credential.ona_token)
        }
        
        response = requests.get(ONA_PROJECT_URL, headers=HEADERS)
        if response.status_code != 200:
            return self.stdout.write(self.style.ERROR("Error when getting list of forms"))
        
        for project in response.json():
            if project["name"] in ONA_PROJECTS:
                target_forms += project["forms"]
        
        print(len(target_forms))
        for form in target_forms:
            print(form)
            response = requests.get(ONA_DATA_URL.format(form["formid"]), headers=HEADERS)
            
            if response.status_code != 200:
                self.stdout.write(self.style.ERROR("Error when getting {} form datas").format(form["title"]))
            
            for data in response.json():
                saved = ona_to_models(data)
                if not saved:
                    self.stdout.write(self.style.ERROR("Error when saving {} record").format(data["id"] if "id" in data.keys() else "Unknow"))
            self.stdout.write(self.style.SUCCESS("All data loaded for form {}".format(form["name"] or "Unknow")))
