import csv, os, json

from datetime import datetime
from django.utils import timezone
from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from record.models import Record, Collector, Action, Enterprise
from itinary.models import Itinary
from region.constants import SRID
from utils.drc_json_to_models import drc_to_models

class Command(BaseCommand):
    help = 'Import records from csv file'

    def add_arguments(self, parser):
        parser.add_argument('--verbose', action='store_true', help='Enable verbose mode')

    def handle(self, *args, **kwargs):
        with open(os.path.join(settings.BASE_DIR, 'fixtures/drc_odk.csv'), mode='r', encoding='utf-8') as file:
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
                        "download_url": row[53],
                        "small_download_url": row[53],
                        "medium_download_url": row[53]
                    }
                    pl = {
                        "pl/info_pl/status": row[47],
                        "pl/info_pl/activite": row[50],
                        "pl/info_pl/batiment": row[49],
                        "pl/info_pl/code_bare": row[45],
                        "pl/info_pl/photo_index": row[52],
                        "pl/info_pl/serial_number": row[51],
                        "pl/info_pl/type_compteur": row[48]
                    }
                    date = row[18]
                    nbr_pl = 1
                    contrat = row[32]
                    montant = row[38]
                    collecteur = row[19]
                    geolocation = [float(row[24]), float(row[25])]
                    accesibilite = row[22]
                    code_anomaly = row[30]
                    matricule_co = row[21]
                    numero_scelle = row[39]
                    action_coupure = row[40]
                    entreprise_collecteur = row[20]
                    data = {
                        "id": "drc-odk-" + str(id),
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
                    saved = drc_to_models(data)
                    if not saved:
                        self.stdout.write(self.style.ERROR("Error when saving {} record").format(data["id"] if "id" in data.keys() else "Unknow"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR("Error during single reord process"))
            self.stdout.write(self.style.SUCCESS("All data loaded for form dry.xlsx"))
