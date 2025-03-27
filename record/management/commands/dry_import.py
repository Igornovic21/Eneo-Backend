import csv, os, json

from datetime import datetime
from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from record.models import Record, Collector, Action, Enterprise
from itinary.models import Itinary
from region.constants import SRID
from utils.dry_json_to_models import dry_to_models

class Command(BaseCommand):
    help = 'Import records from csv file'

    def add_arguments(self, parser):
        parser.add_argument('--verbose', action='store_true', help='Enable verbose mode')

    def handle(self, *args, **kwargs):
        with open(os.path.join(settings.BASE_DIR, 'fixtures/dry_odk.csv'), mode='r', encoding='utf-8') as file:
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
                        "download_url": "",
                        "small_download_url": "",
                        "medium_download_url": ""
                    }
                    pl = {
                        "pl/info_pl/status": "actif" if row[7] == "ACTIVE" else "inactif",
                        "pl/info_pl/activite": row[18],
                        "pl/info_pl/batiment": row[17],
                        "pl/info_pl/code_bare": row[6],
                        "pl/info_pl/photo_index": row[20],
                        "pl/info_pl/serial_number": row[6],
                        "pl/info_pl/type_compteur": row[16]
                    }
                    date = row[24]
                    nbr_pl = 1
                    contrat = ""
                    montant = ""
                    collecteur = row[4]
                    geolocation = [float(row[14]), float(row[15])]
                    accesibilite = ""
                    code_anomaly = row[23]
                    matricule_co = row[3]
                    numero_scelle = ""
                    action_coupure = row[21]
                    entreprise_collecteur = ""
                    data = {
                        "id": "dry-odk-" + str(id),
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
                    saved = dry_to_models(data)
                    if not saved:
                        self.stdout.write(self.style.ERROR("Error when saving {} record").format(data["id"] if "id" in data.keys() else "Unknow"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR("Error during single reord process"))
            self.stdout.write(self.style.SUCCESS("All data loaded for form dry.xlsx"))
