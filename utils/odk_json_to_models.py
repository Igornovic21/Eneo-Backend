from datetime import datetime

from django.contrib.gis.geos import Point

from itinary.models import Itinary
from record.models import Record, DeliveryPoint, Action, Enterprise, Collector, Location
from region.constants import SRID

def odk_to_models(json: dict) -> bool:
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
            record.source = json["source"] if "source" in json.keys() else ""
            record.poste = json["poste"] if "poste" in json.keys() else ""
            record.depart = json["depart"] if "depart" in json.keys() else ""
            record.depart_nbr = json["depart_nbr"] if "depart_nbr" in json.keys() else ""
            record.depart_code = json["depart_code"] if "depart_code" in json.keys() else ""
            record.poste_type = json["poste_type"] if "poste_type" in json.keys() else ""
            record.existence = json["existence"] if "existence" in json.keys() else ""
            record.telephone = json["telephone"] if "telephone" in json.keys() else ""
            record.quality = json["quality"] if "quality" in json.keys() else ""
            record.lighting = json["lighting"] if "lighting" in json.keys() else ""
            record.poste_image_url = json["poste_image_url"] if "poste_image_url" in json.keys() else ""
            record.i1_input = json["i1_input"] if "i1_input" in json.keys() else ""
            record.i1_output = json["i1_output"] if "i1_output" in json.keys() else ""
            record.i2_input = json["i2_input"] if "i2_input" in json.keys() else ""
            record.i2_output = json["i2_output"] if "i2_output" in json.keys() else ""
            record.i3_input = json["i3_input"] if "i3_input" in json.keys() else ""
            record.i3_output = json["i3_output"] if "i3_output" in json.keys() else ""
            record.i4_input = json["i4_input"] if "i4_input" in json.keys() else ""
            record.i4_output = json["i4_output"] if "i4_output" in json.keys() else ""
            date = datetime.fromisoformat(json["date"])
            record.date = date
            record.save()
            if not Location.objects.filter(record=record).exists():
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
                            index=pl["pl/info_pl/index"] if "pl/info_pl/index" in pl.keys() else "",
                            contrat=pl["pl/info_pl/contrat"] if "pl/info_pl/contrat" in pl.keys() else "",
                            thread_nbr=pl["pl/info_pl/nbr_fil"] if "pl/info_pl/nbr_fil" in pl.keys() else "",
                            image_url=pl["pl/info_pl/image_url"] if "pl/info_pl/image_url" in pl.keys() else "",
                            serial_number=pl["pl/info_pl/serial_number"] if "pl/info_pl/serial_number" in pl.keys() else "",
                        )
                        delivery_point.record = record
                        delivery_point.save()
        return True
    except Exception as e:
        print(json["id"])
        print(e)
        return False