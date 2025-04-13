import os, csv

from django.db import models
from django.dispatch import receiver
from django.db.models.fields.files import FieldFile

from config.models import OdkPosition

from constants.odk_api import ODK_BASE_URL
from utils.logger import logger
from utils.odk_json_to_models import odk_to_models

@receiver(models.signals.post_save, sender=OdkPosition)
def load_data_csv(sender, instance, **kwargs):
    name = instance.file.name.split(".")[0] if len(instance.form_name) <= 0 else instance.form_name
    project_id = instance.project_id
    with open(os.path.join(instance.file.path), mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        
        index = 1
        for row in csv_reader:
            try:
                id = index
                index += 1
                pl_image_url = ""
                if len(row[33]) > 0:
                    pl_image_url = "{}/projects/{}/forms/{}/submissions/{}/attachments/{}".format(ODK_BASE_URL, project_id, name, row[53], row[33])
                poste_image_url = ""
                if len(row[8]) > 0:
                    poste_image_url = "{}/projects/{}/forms/{}/submissions/{}/attachments/{}".format(ODK_BASE_URL, project_id, name, row[53], row[8])
                pl = {
                    "pl/info_pl/status": "actif" if row[21] == "oui" else "inactif",
                    "pl/info_pl/activite": row[29],
                    "pl/info_pl/batiment": row[24],
                    "pl/info_pl/code_bare": row[19],
                    "pl/info_pl/photo_index": row[33],
                    "pl/info_pl/serial_number": row[30],
                    "pl/info_pl/type_compteur": row[22],
                    "pl/info_pl/nbr_fil": row[23],
                    "pl/info_pl/raison": row[20],
                    "pl/info_pl/contrat": row[31],
                    "pl/info_pl/index": row[32],
                    "pl/info_pl/image_url": pl_image_url
                }
                date = row[51]
                nbr_pl = 1
                contrat = ""
                montant = ""
                collecteur = row[2]
                geolocation = [float(row[34]), float(row[35])]
                accesibilite = row[17]
                code_anomaly = row[40]
                matricule_co = row[3]
                numero_scelle = ""
                action_coupure = row[38]
                entreprise_collecteur = row[1]
                source = row[4]
                depart = row[5]
                poste = row[6]
                poste_type = row[7]
                poste_image_url = poste_image_url
                depart_nbr = row[9]
                depart_code = row[10]
                existence = row[14]
                telephone = row[15]
                quality = row[16]
                lighting = row[17]
                i1_input = row[41]
                i1_output = row[45]
                i2_input = row[42]
                i2_output = row[46]
                i3_input = row[43]
                i3_output = row[47]
                i4_input = row[44]
                i4_output = row[48]
                data = {
                    "id": "{}-odk-position-{}".format(name, str(id)),
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
                    "source": source,
                    "depart": depart,
                    "poste": poste,
                    "poste_type": poste_type,
                    "poste_image_url": poste_image_url,
                    "depart_nbr": depart_nbr,
                    "depart_code": depart_code,
                    "existence": existence,
                    "telephone": telephone,
                    "quality": quality,
                    "lighting": lighting,
                    "i1_input": i1_input,
                    "i1_output": i1_output,
                    "i2_input": i2_input,
                    "i2_output": i2_output,
                    "i3_input": i3_input,
                    "i3_output": i3_output,
                    "i4_input": i4_input,
                    "i4_output": i4_output,
                    "accesibilite": accesibilite,
                    "code_anomaly": code_anomaly,
                    "matricule_co": matricule_co,
                    "numero_scelle": numero_scelle,
                    "action_coupure": action_coupure,
                    "entreprise_collecteur": entreprise_collecteur
                }
                saved = odk_to_models(data)
                if not saved:
                    pass
                    logger.error("error when loading {} at index {}".format(instance.form_name, id))
            except:
                pass
                logger.error("error when loading {} at index {}".format(instance.form_name, id))