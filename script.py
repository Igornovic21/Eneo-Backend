import json, csv

def gen_geo_points():
    # Load OSM JSON data
    with open('douala_points.json', 'r', encoding='utf-8') as file:
        osm_data = json.load(file)

    # Generate fixture data
    fixtures = {}
    for index, element in enumerate(osm_data['elements']):
        if element['type'] == 'node' and 'tags' in element and 'name' in element['tags']:
            fixtures[f"geoData_{index + 1}"] = {
                "osmId": element['id'],
                "longitude": element['lon'],
                "latitude": element['lat'],
                "name": element['tags']['name']
            }

    # Save to a YAML-like format
    with open('geo_fixtures.yaml', 'w') as file:
        for key, value in fixtures.items():
            file.write(f"  {key}:\n")
            for k, v in value.items():
                file.write(f"    {k}: {v}\n")

def import_odk_csv_data():
    # Define the path to your CSV file
    csv_file_path = 'pl.csv'

    # Open and read the CSV file
    try:
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            records = []
            # Print each row
            for row in csv_reader:
                try:
                    id = row[0]
                    attachments = {
                        "id": None,
                        "name": None,
                        "xform": None,
                        "filename": None,
                        "instance": None,
                        "mimetype": None,
                        "download_url": None,
                        "small_download_url": None,
                        "medium_download_url": None
                    }
                    pl = {
                        "pl/info_pl/status": row[8],
                        "pl/info_pl/activite": row[11],
                        "pl/info_pl/batiment": row[10],
                        "pl/info_pl/code_bare": row[6],
                        "pl/info_pl/photo_index": row[13],
                        "pl/info_pl/serial_number": row[12],
                        "pl/info_pl/type_compteur": row[9]
                    }
                    date = row[0]
                    nbr_pl = row[5]
                    contrat = row[23]
                    montant = row[29]
                    collecteur = row[1]
                    geolocation = [float(row[16]), float(row[15])]
                    accesibilite = row[4]
                    code_anomaly = row[21]
                    matricule_co = row[3]
                    numero_scelle = row[30]
                    action_coupure = row[31]
                    entreprise_collecteur = row[2]
                    data = {
                        "id": id,
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
                    records.append(data)
                except Exception as e:
                    print(f"Convertion error {e}")

        # Save to a YAML-like format
        with open('csv_to_json.json', 'w') as file:
            json.dump(records, file, indent=2)
            # for key, value in fixtures.items():
            #     file.write(f"  {key}:\n")
            #     for k, v in value.items():
            #         file.write(f"    {k}: {v}\n")
    except FileNotFoundError:
        print(f"Error: File '{csv_file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def edit_block_code():
    # Load GEO JSON data
    with open('DCUD.geojson', 'r', encoding='utf-8') as file:
        geo_json_data = json.load(file)

    itinaries = geo_json_data['features']
    itinaries_digits = len(str(len(itinaries)))
    new_itinaries = []

    for index, itinary in enumerate(itinaries):
        index_digits = len(str(index))
        zeros = itinaries_digits - index_digits
        suffix = ""
        for i in range(zeros):
            suffix = suffix + "0"
        itinary['properties']['BLOCK_CODE'] = itinary['properties']['REGION'] + '-{}{}'.format(suffix, index+1)
        new_itinaries.append(itinary)

        # print(new_itinaries)

    with open('NEW_DCUD.geojson', 'w') as file:
        geo_json_data['features'] = new_itinaries
        json.dump(geo_json_data, file, separators=(",", ":"), indent=None)

import pandas as pd
def import_odk_xlsx_data():
    file_path = "dry.xlsx"
    # DIR = Path(__file__).resolve().parent.parent
    # file_path = os.path.join(DIR, 'dry.xlsx')
    # print(file_path)
    df = pd.read_excel(file_path, sheet_name="Feuil1")
    print(df)

    for index, row in df.iterrows():
        print(f"Row {index}: {row.to_dict()}")

if __name__ == "__main__":
    import_odk_xlsx_data()
    pass
