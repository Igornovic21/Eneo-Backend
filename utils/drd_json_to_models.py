from datetime import datetime
from django.utils import timezone

from django.contrib.gis.geos import Point

from itinary.models import Itinary
from record.models import Record, DeliveryPoint, Action, Enterprise, Collector, Location
from region.constants import SRID

def drd_to_models(json: dict) -> bool:
    try:
        latitude = json["_geolocation"][0]
        longitude = json["_geolocation"][1]
        point = Point(longitude, latitude, srid=SRID)
        itinaries = Itinary.objects.only("boundary").filter(boundary__contains=point)
        if itinaries.exists():
            action, _ = Action.objects.get_or_create(name=json["action"])
            collector, _ = Collector.objects.get_or_create(
                name=json["Collecteur"],
                matricule=json["matricule_co"],
            )
            enterprise, _ = Enterprise.objects.get_or_create(name=json["entreprise_collecteur"])
            record, _ = Record.objects.get_or_create(ona_id=json["id"])
            record.contrat = json["contrat"] if "contrat" in json.keys() else ""
            record.amount = json["montant"] if "montant" in json.keys() else ""
            record.accessibility = json["accesibilite"] if "accesibilite" in json.keys() else ""
            record.code_anomaly = json["code_anomaly"] if "code_anomaly" in json.keys() else ""
            record.sealed_number = json["numero_scelle"] if "numero_scelle" in json.keys() else ""
            record.cut_action = json["action_coupure"] if "action_coupure" in json.keys() else ""
            record.delivery_points = json["nbr_pl"] if "nbr_pl" in json.keys() else len(json["pl"]) if "pl" in json.keys() else 0
            record.action = action
            record.collector = collector
            record.enterprise = enterprise
            record.itinary = itinaries[0]
            date = datetime.strptime(json["date"], "%d/%m/%Y %H:%M")
            date = timezone.make_aware(date, timezone.get_current_timezone())
            record.date = date
            record.save()

            Location.objects.create(coordinates=point, record=record)
            if "pl" in json.keys():
                for pl in json["pl"]:
                    if not DeliveryPoint.objects.filter(
                        serial_number=pl["pl/info_pl/serial_number"] if "pl/info_pl/serial_number" in pl.keys() else "",
                        record=record
                        ).exists():
                        delivery_point = DeliveryPoint.objects.create(
                            status=pl["pl/info_pl/status"] if "pl/info_pl/status" in pl.keys() else "",
                            reason=pl["pl/info_pl/raison"] if "pl/info_pl/raison" in pl.keys() else "",
                            activite=pl["pl/info_pl/activite"] if "pl/info_pl/activite" in pl.keys() else "",
                            batiment=pl["pl/info_pl/batiment"] if "pl/info_pl/batiment" in pl.keys() else "",
                            code_bare=pl["pl/info_pl/code_bare"] if "pl/info_pl/code_bare" in pl.keys() else "",
                            type=pl["pl/info_pl/type_compteur"] if "pl/info_pl/type_compteur" in pl.keys() else "",
                            serial_number=pl["pl/info_pl/serial_number"] if "pl/info_pl/serial_number" in pl.keys() else "",
                        )
                        delivery_point.image_url = json["_attachments"][0]["download_url"] if "download_url" in json["_attachments"][0].keys() else ""
                        delivery_point.record = record
                        delivery_point.save()
        return True
    except Exception as e:
        print(e)
        return False