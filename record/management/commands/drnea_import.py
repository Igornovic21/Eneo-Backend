import csv, os, json

from datetime import datetime
from django.utils import timezone
from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from record.models import Record, Collector, Action, Enterprise
from itinary.models import Itinary
from region.constants import SRID
from utils.drnea_json_to_models import drnea_to_models

class Command(BaseCommand):
    help = 'Import records from csv file'

    def add_arguments(self, parser):
        parser.add_argument('--verbose', action='store_true', help='Enable verbose mode')

    def handle(self, *args, **kwargs):
        with open(os.path.join(settings.BASE_DIR, 'fixtures/drnea_odk.csv'), mode='r', encoding='utf-8') as file:
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
                        "download_url": row[12],
                        "small_download_url": row[12],
                        "medium_download_url": row[12]
                    }
                    pl = {
                        "pl/info_pl/status": "actif" if row[37] == "ACTIVE" else "inactif",
                        "pl/info_pl/activite": row[9],
                        "pl/info_pl/batiment": row[8],
                        "pl/info_pl/code_bare": row[4],
                        "pl/info_pl/photo_index": "",
                        "pl/info_pl/serial_number": row[10],
                        "pl/info_pl/type_compteur": row[7]
                    }
                    date = row[29]
                    nbr_pl = 1
                    contrat = row[19]
                    montant = row[24]
                    collecteur = row[0]
                    geolocation = [float(row[13]), float(row[14])]
                    accesibilite = row[3]
                    code_anomaly = row[17]
                    matricule_co = row[2]
                    numero_scelle = row[25]
                    action_coupure = row[26]
                    entreprise_collecteur = row[1]
                    data = {
                        "id": "drnea-odk-" + str(id),
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
                    saved = drnea_to_models(data)
                    if not saved:
                        self.stdout.write(self.style.ERROR("Error when saving {} record").format(data["id"] if "id" in data.keys() else "Unknow"))
                except Exception as e:
                    print(e)
                    self.stdout.write(self.style.ERROR("Error during single reord process"))
            self.stdout.write(self.style.SUCCESS("All data loaded for form dry.xlsx"))
