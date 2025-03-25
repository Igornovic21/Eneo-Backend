import requests, json, os, csv

from datetime import datetime

from django.conf import settings
from django_apscheduler.models import DjangoJobExecution
from datetime import datetime
from django.contrib.gis.geos import Point

from constants.config import ONA_PROJECT
from constants.ona_api import ONA_DATA_URL, ONA_PROJECT_URL

from config.models import Credential
from record.models import Record, Collector, Action, Enterprise
from itinary.models import Itinary
from region.constants import SRID

from utils.logger import logger

def get_record_job():
    logger.info(f"Job Record Started {datetime.now()}")
    credential = Credential.objects.first()
    fields = credential.fields.split("/")
    ona_forms = []
    HEADERS = {
        "Authorization": "Token {}".format(credential.ona_token)
    }
    
    response = requests.get(ONA_PROJECT_URL, headers=HEADERS)
    if response.status_code != 200:
        return print("Error when getting list of forms")
    
    for project in response.json():
        if project["name"] == ONA_PROJECT:
            ona_forms = project["forms"]
                
    for form in ona_forms:
        print(form)
        response = requests.get(ONA_DATA_URL.format(form["formid"]), headers=HEADERS)
        
        if response.status_code != 200:
            print("Error when getting {} form datas").format(form["title"])
        
        for data in response.json():
            try:
                ona_id = data["id"]

                record, _ = Record.objects.get_or_create(ona_id=ona_id)

                if not _:
                    print("Record {} already saved".format(ona_id))
                
                result = {}
                action, _ = Action.objects.get_or_create(name=data["action"])
                collector, _ = Collector.objects.get_or_create(name=data["Collecteur"])
                enterprise, _ = Enterprise.objects.get_or_create(name=data["entreprise_collecteur"])
                date = datetime.fromisoformat(data["date"])
                latitude = data["_geolocation"][0]
                longitude = data["_geolocation"][1]

                for field in fields:
                    if field in data.keys():
                        result[field] = data[field]
                    else:
                        result[field] = None
                
                record.data = json.dumps(result)
                record.action = action
                record.collector = collector
                record.enterprise = enterprise
                record.date = date
                point = Point(longitude, latitude, srid=SRID)
                itinaries = Itinary.objects.only("boundary").filter(boundary__contains=point)
                if itinaries.exists():
                    record.itinary = itinaries[0]
                    record.save()
                else:
                    print("No itinary found for this submission {}".format(ona_id))
            except:
                print("Error during single reord process")
        print("All data loaded for form {}".format(form["name"] or "Unknow"))

def get_csv_record_job():
    with open(os.path.join(settings.BASE_DIR, 'fixtures/dry.csv'), mode='r') as file:
        csv_reader = csv.reader(file)
        
        index = 1
        for row in csv_reader:
            try:
                id = index
                index += 1
                attachments = {
                    "id": None,
                    "name": None,
                    "xform": None,
                    "filename": None,
                    "instance": None,
                    "mimetype": None,
                    "download_url": "https://eneoservices.position.cm/static/admin/img/icon-addlink.svg",
                    "small_download_url": "https://eneoservices.position.cm/static/admin/img/icon-addlink.svg",
                    "medium_download_url": "https://eneoservices.position.cm/static/admin/img/icon-addlink.svg"
                }
                pl = {
                    "pl/info_pl/status": "actif" if row[7] == "ACTIVE" else "inactif",
                    "pl/info_pl/activite": row[18],
                    "pl/info_pl/batiment": row[17],
                    "pl/info_pl/code_bare": row[12],
                    "pl/info_pl/photo_index": row[20],
                    "pl/info_pl/serial_number": row[12],
                    "pl/info_pl/type_compteur": row[16]
                }
                date = row[24]
                nbr_pl = 1
                contrat = ""
                montant = ""
                collecteur = row[1]
                geolocation = [float(row[14]), float(row[15])]
                accesibilite = ""
                code_anomaly = row[23]
                matricule_co = row[3]
                numero_scelle = ""
                action_coupure = row[21]
                entreprise_collecteur = ""
                data = {
                    "id": id,
                    "pl": [
                        pl
                    ],
                    "date": date,
                    "action": action_coupure,
                    "nbr_pl": nbr_pl,
                    "contrat": contrat,
                    "montant": montant,
                    "Collecteur": collecteur,
                    "_geolocation": geolocation,
                    "_attachments": [
                        attachments
                    ],
                    "accesibilite": accesibilite,
                    "code_anomaly": code_anomaly,
                    "matricule_co": matricule_co,
                    "numero_scelle": numero_scelle,
                    "action_coupure": action_coupure,
                    "entreprise_collecteur": entreprise_collecteur
                }

                try:                        
                    ona_id = data["id"]

                    record, _ = Record.objects.get_or_create(ona_id=ona_id)

                    if not _:
                        print("Record {} already saved".format(ona_id))
                    
                    action, _ = Action.objects.get_or_create(name=data["action"])
                    collector, _ = Collector.objects.get_or_create(name=data["Collecteur"])
                    enterprise, _ = Enterprise.objects.get_or_create(name=data["entreprise_collecteur"])
                    date = datetime.fromisoformat(data["date"])
                    latitude = data["_geolocation"][0]
                    longitude = data["_geolocation"][1]
                    
                    record.data = json.dumps(data)
                    record.action = action
                    record.collector = collector
                    record.enterprise = enterprise
                    record.date = date
                    point = Point(longitude, latitude, srid=SRID)
                    itinaries = Itinary.objects.only("boundary").filter(boundary__contains=point)
                    if itinaries.exists():
                        record.itinary = itinaries[0]
                        record.save()
                    else:
                        print("No itinary found for this submission {}".format(ona_id))
                except:
                    print("Error during single reord process")
            except:
                print("Error during single reord process")
        print("All data loaded for form dry.xlsx")



def delete_old_job_executions(max_age=172800):
    logger.info("Delete older job than 2 days in the historic")
    DjangoJobExecution.objects.delete_old_job_executions(max_age)
