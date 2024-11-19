import requests, json

from constants.config import ONA_PROJECT
from record.models import Record
from config.models import FormData

FIELDS:str = "id/pl/date/action/nbr_pl/contrat/montant/Collecteur/_geolocation/_attachements/accesibilite/code_anomaly/matricule_co/numero_scelle/action_coupure/entreprise_collecteur"
HEADERS = {
    "Authorization": "Token a8996c762270c9104b53f42d50061028c22d4896"
}

def get_project() -> list[dict]:
    response = requests.get("https://api.ona.io/api/v1/projects", headers=HEADERS)
    if response.status_code != 200:
        print("error when getting projects")
    
    for project in response.json():
        if project["name"] == ONA_PROJECT:
            return project["forms"]

def get_form_data(forms: list[dict]):
    for form in forms:
        print(form["title"])
        forms_obj = FormData.objects.filter(region__name=form["title"])
        if forms_obj.exists():
            print(forms_obj[0].region.name)
            response = requests.get("https://api.ona.io/api/v1/data/{}".format(form["formid"]), headers=HEADERS)
            fields = FIELDS.split("/")
            
            if response.status_code == 200:
                data:dict = response.json()[0]
                result = {}
                ona_id = data["ona_id"]
                action = data["action"]
                collector = data["Collecteur"]
                enterprise = data["entreprise_collecteur"]
                for field in fields:
                    if field in data.keys():
                        result[field] = data[field]
                    else:
                        result[field] = ""
                Record.objects.create(
                    form=forms_obj[0],
                    ona_id=ona_id,
                    data=json.dumps(result),
                    full_data=json.dumps(response.json()),
                    action=action,
                    collector=collector,
                    enterprise=enterprise
                )

if __name__ == "__main__":
    forms = get_project()
    get_form_data(forms)
