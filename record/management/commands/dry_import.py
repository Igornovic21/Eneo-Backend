import csv, os, json

from datetime import datetime
from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from record.models import Record, Collector, Action, Enterprise
from itinary.models import Itinary
from region.constants import SRID

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
                        "download_url": "https://fakeimg.pl/600x400",
                        "small_download_url": "https://fakeimg.pl/600x400",
                        "medium_download_url": "https://fakeimg.pl/600x400"
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

                    try:
                        ona_id = data["id"]
                        latitude = data["_geolocation"][0]
                        longitude = data["_geolocation"][1]
                        point = Point(longitude, latitude, srid=SRID)
                        itinaries = Itinary.objects.only("boundary").filter(boundary__contains=point)
                        if itinaries.exists():
                            record, _ = Record.objects.get_or_create(ona_id=ona_id)
                            if not _:
                                self.stdout.write(self.style.WARNING("Record {} already saved".format(ona_id)))
                            action, _ = Action.objects.get_or_create(name=data["action"])
                            collector, _ = Collector.objects.get_or_create(name=data["Collecteur"])
                            enterprise, _ = Enterprise.objects.get_or_create(name=data["entreprise_collecteur"])
                            date = datetime.fromisoformat(data["date"])
                            record.data = json.dumps(data)
                            record.action = action
                            record.collector = collector
                            record.enterprise = enterprise
                            record.date = date
                            record.itinary = itinaries[0]
                            record.save()
                        else:
                            self.stdout.write("No itinary found for this submission {}".format(ona_id))         
                        
                    except Exception as e:
                        self.stdout.write(self.style.ERROR("Error during single reord process"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR("Error during single reord process"))
            self.stdout.write(self.style.SUCCESS("All data loaded for form dry.xlsx"))
