import os
import requests
import pandas as pd
import geopandas as gpd
from .codes.mongodb import middle_points_aggregate
from zipfile import ZipFile
from pymongo import MongoClient, UpdateOne
from andeschileong.settings import (
    MONGO_DB, MONGO_CP_DB, CP_STRAVA_COLLECTION,
    DATA_DIR, DEBUG)


# Creates the mongodb files to upload
def create_features(geodata, max=10):
    features = []
    # if DEBUG:
    #     geodata = geodata.head(max)

    for feature in geodata.iterfeatures():
        prop = feature.pop('properties', None)
        if prop:
            feature.update(prop)
        feature.pop('id', None)
        feature.pop('type', None)
        feature.pop('edge_uid', None)
        feature.pop('osm_reference_id', None)
        features.append(feature)

    return features


# Get data from Strava's ZIP file.
# - SHP file for geometry objects
# - CSV file for getting Strava info
def strava_to_mongo(stravazipfile, collection):
    print(f'Extrayendo los datos de {stravazipfile}')
    path = os.getcwd() + os.sep + DATA_DIR + os.sep + stravazipfile

    with ZipFile(path, 'r') as zip:
        files = zip.infolist()
        shpfile = [file.filename for file in files if 'shp' in file.filename][0] # noqa
        csvfile = [file for file in files if 'csv' in file.filename][0]

        geodata = gpd.read_file(path + '!' + shpfile, )
        with zip.open(csvfile) as csv:
            data = pd.read_csv(csv, low_memory=False)

    print('Generando elementos para subir a mongodb')
    merged_df = pd.merge(geodata, data,
                         how='inner', left_on='edgeUID', right_on='edge_uid')

    features = create_features(merged_df)
    print(f'Insertando {len(features)} elementos en mongodb')
    collection.insert_many(features, ordered=False)


# Get middle point for all lines
def create_middle_points(collection):
    pipeline = middle_points_aggregate
    cursor = collection.aggregate(pipeline)
    data = list(cursor)

    update_operation = [
        {
            'filter': {'_id': result['_id']},
            'update': {'$set': {'middlePoint': result['middlePoint']}}
        }
        for result in data
    ]

    collection.bulk_write([UpdateOne(**op) for op in update_operation])


# Get middle point of city reference
def get_middle_point(references):
    references_sum = [0, 0]

    for ref in references:
        references_sum = [x + y for x, y in zip(references_sum, ref)]

    return tuple([element / len(references) for element in references_sum])


def get_user_ip(ip):
    url = f"https://ipinfo.io/{ip}/json"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        data.pop('ip', None)
        data.pop('org', None)
    else:
        data = data.get('error', None)

    return {
        'sucess': r.status_code == 200,
        'info': data
    }


def upload_data():
    client = MongoClient(MONGO_DB)
    db = client[MONGO_CP_DB]
    collection = db[CP_STRAVA_COLLECTION]

    print('Importando datos a MongoDB...')
    strava_to_mongo('data.zip', collection)

    print('Creando puntos medios...')
    create_middle_points(collection)
    print('Finalizado!')
    client.close()


def get_city_data(polygon):
    gdf_city = polygon.set_crs("epsg:4326")
    gdf_city = gdf_city.to_crs(crs=3857)
    gdf_city['area'] = gdf_city['geometry'].area
    data = gdf_city[gdf_city['area'] == gdf_city['area'].max()]
    data = data.to_crs(crs=4326).to_dict()
    return data['geometry'][0]
