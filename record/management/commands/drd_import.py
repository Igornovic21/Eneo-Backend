import csv, os, json

from datetime import datetime, timezone
from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from config.models import Credential
from record.models import Record, Collector, Action, Enterprise
from itinary.models import Itinary
from region.constants import SRID

class Command(BaseCommand):
    help = 'Import records from csv file'

    def add_arguments(self, parser):
        parser.add_argument('--verbose', action='store_true', help='Enable verbose mode')

    def handle(self, *args, **kwargs):
        with open(os.path.join(settings.BASE_DIR, 'fixtures/drd_odk.csv'), mode='r') as file:
            csv_reader = csv.reader(file)
            
            index = 1
            for row in csv_reader:
                try:
                    id = index
                    index += 1
                    attachments = {
                        "id": row[17],
                        "name": None,
                        "xform": None,
                        "filename": None,
                        "instance": None,
                        "mimetype": None,
                        "download_url": row[10],
                        "small_download_url": row[10],
                        "medium_download_url": row[10]
                    }
                    pl = {
                        "pl/info_pl/status": row[7],
                        "pl/info_pl/activite": row[3],
                        "pl/info_pl/batiment": row[4],
                        "pl/info_pl/code_bare": row[2],
                        "pl/info_pl/photo_index": None,
                        "pl/info_pl/serial_number": row[6],
                        "pl/info_pl/type_compteur": row[8]
                    }
                    date = row[18]
                    nbr_pl = 1
                    contrat = row[24]
                    montant = None
                    collecteur = row[13]
                    geolocation = [float(row[19]), float(row[20])]
                    accesibilite = row[16]
                    code_anomaly = None
                    matricule_co = row[14]
                    numero_scelle = ""
                    action_coupure = None
                    entreprise_collecteur = row[15]
                    data = {
                        "id": "drd-odk-" + str(id),
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
                        print(data)         
                        ona_id = data["id"]
                        record, _ = Record.objects.get_or_create(ona_id=ona_id)
                        if not _:
                            self.stdout.write(self.style.WARNING("Record {} already saved".format(ona_id)))
                        if data["action"] is None:
                            action = None
                        else:
                            action, _ = Action.objects.get_or_create(name=data["action"])
                        if data["Collecteur"] is None:
                            collector = None
                        else:
                            collector, _ = Collector.objects.get_or_create(name=data["Collecteur"])
                        if data["entreprise_collecteur"] is None:
                            enterprise = None
                        else:
                            enterprise, _ = Enterprise.objects.get_or_create(name=data["entreprise_collecteur"])
                        date = datetime.strptime(data["date"], "%d/%m/%Y %H:%M")
                        date = timezone.make_aware(date, timezone.get_current_timezone())
                        latitude = data["_geolocation"][0]
                        longitude = data["_geolocation"][1]
                        record.data = json.dumps(data)
                        record.action = action
                        record.collector = collector
                        record.enterprise = enterprise
                        record.date = date
                        point = Point(longitude, latitude, srid=SRID)
                        itinaries = Itinary.objects.only("boundary").filter(boundary__contains=point)
                        print(itinaries)
                        if itinaries.exists():
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
