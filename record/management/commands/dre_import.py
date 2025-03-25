import csv, os, json

from datetime import datetime
from django.utils import timezone
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
        with open(os.path.join(settings.BASE_DIR, 'fixtures/dre_odk.csv'), mode='r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            
            index = 1
            for row in csv_reader:
                try:
                    id = index
                    index += 1
                    attachments = {
                        "id": row[16],
                        "name": None,
                        "xform": None,
                        "filename": None,
                        "instance": None,
                        "mimetype": None,
                        "download_url": row[11],
                        "small_download_url": row[11],
                        "medium_download_url": row[11]
                    }
                    pl = {
                        "pl/info_pl/status": row[8],
                        "pl/info_pl/activite": row[3],
                        "pl/info_pl/batiment": row[4],
                        "pl/info_pl/code_bare": row[2],
                        "pl/info_pl/photo_index": row[5],
                        "pl/info_pl/serial_number": row[6],
                        "pl/info_pl/type_compteur": row[9]
                    }
                    date = row[17]
                    nbr_pl = 1
                    contrat = row[26]
                    montant = row[19]
                    collecteur = row[12]
                    geolocation = [float(row[32]), float(row[33])]
                    accesibilite = row[15]
                    code_anomaly = row[18]
                    matricule_co = None
                    numero_scelle = row[20]
                    action_coupure = row[21]
                    entreprise_collecteur = row[14]
                    data = {
                        "id": "dre-odk-" + str(id),
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
                            date = datetime.strptime(data["date"], "%d/%m/%Y %H:%M")
                            date = timezone.make_aware(date, timezone.get_current_timezone())
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
                        print(e)
                        print("during saving ============")
                        self.stdout.write(self.style.ERROR("Error during single record process"))
                except Exception as y:
                    print(y)
                    print("during saving ============")
                    self.stdout.write(self.style.ERROR("Error during single record process"))
            self.stdout.write(self.style.SUCCESS("All data loaded for form dry.xlsx"))
