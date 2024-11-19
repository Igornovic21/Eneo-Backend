import requests, json
from datetime import datetime
from django.core.management.base import BaseCommand

from constants.config import ONA_PROJECT
from constants.ona_api import ONA_DATA_URL, ONA_PROJECT_URL
from utils.logger import logger

from record.models import Record
from config.models import FormData

HEADERS = {
    "Authorization": "Token a8996c762270c9104b53f42d50061028c22d4896"
}

class Command(BaseCommand):
    help = 'Get list of data for any FormConfig Save in th App'

    def add_arguments(self, parser):
        parser.add_argument('--form', type=str, help='A specific ONA Form name')

    def handle(self, *args, **kwargs):
        form_arg = kwargs['form']
        ona_forms = []
        
        response = requests.get(ONA_PROJECT_URL, headers=HEADERS)
        if response.status_code != 200:
            self.stdout.write(self.style.ERROR("Error when getting list of forms"))
        
        for project in response.json():
            if project["name"] == ONA_PROJECT:
                ona_forms = project["forms"]
                    
        if form_arg is None:
            for form in ona_forms:
                forms_obj = FormData.objects.filter(region__name=form["name"])

                if forms_obj.exists():
                    response = requests.get(ONA_DATA_URL.format(form["formid"]), headers=HEADERS)
                    fields = forms_obj[0].fields.split("/")
                    
                    if response.status_code != 200:
                        self.stdout.write(self.style.ERROR("Error when getting {} form datas").format(form["title"]))
                    
                    for data in response.json():
                        ona_id = data["id"]

                        if Record.objects.filter(ona_id=ona_id).exists():
                            self.stdout.write(self.style.WARNING("Record {} already saved").format(ona_id))
                        
                        result = {}
                        action = data["action"]
                        collector = data["Collecteur"]
                        enterprise = data["entreprise_collecteur"]
                        date = datetime.fromisoformat(data["date"])

                        for field in fields:
                            if field in data.keys():
                                result[field] = data[field]
                            else:
                                result[field] = ""
                        records = Record.objects.only("ona_id").filter(ona_id=ona_id)
                        if records.exists():
                            records[0].data = json.dumps(result)
                            records[0].full_data = json.dumps(data)
                            records[0].action = action
                            records[0].collector = collector
                            records[0].enterprise = enterprise
                            records[0].date = date
                            records[0].save()
                        else:
                            Record.objects.create(
                                form=forms_obj[0],
                                ona_id=ona_id,
                                data=json.dumps(result),
                                full_data=json.dumps(data),
                                action=action,
                                collector=collector,
                                enterprise=enterprise,
                                date=date
                            )
                    self.stdout.write("All data loaded for configured forms")
        else:
            for form in ona_forms:
                if form["name"] == form_arg:
                    forms_obj = FormData.objects.filter(region__name=form["name"])

                    if forms_obj.exists():
                        response = requests.get(ONA_DATA_URL.format(form["formid"]), headers=HEADERS)
                        fields = forms_obj[0].fields.split("/")
                        
                        if response.status_code != 200:
                            self.stdout.write(self.style.ERROR("Error when getting {} form datas").format(form["title"]))
                        
                        for data in response.json():
                            ona_id = data["id"]

                            if Record.objects.filter(ona_id=ona_id).exists():
                                self.stdout.write(self.style.WARNING("Record {} already saved").format(ona_id))
                            
                            result = {}
                            action = data["action"]
                            collector = data["Collecteur"]
                            enterprise = data["entreprise_collecteur"]
                            date = datetime.fromisoformat(date["date"])

                            for field in fields:
                                if field in data.keys():
                                    result[field] = data[field]
                                else:
                                    result[field] = ""

                            Record.objects.create(
                                form=forms_obj[0],
                                ona_id=ona_id,
                                data=json.dumps(result),
                                full_data=json.dumps(response.json()),
                                action=action,
                                collector=collector,
                                enterprise=enterprise,
                                date=date
                            )
                        self.stdout.write("All data loaded for {} forms".format(form_arg))
