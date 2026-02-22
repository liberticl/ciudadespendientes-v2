import os
import re
import requests
import pandas as pd
import geopandas as gpd
from .mongodb import middle_points_aggregate, points_inside
from zipfile import ZipFile
from bs4 import BeautifulSoup
from pymongo import MongoClient, UpdateOne
from shapely.geometry import Polygon
# from .decorators import calculate_execution_time
from andeschileong.settings import (
    MONGO_DB, MONGO_CP_DB, CP_STRAVA_COLLECTION,
    DATA_DIR, DECKGL_VERSION)


# Creates the mongodb files to upload
def create_features(geodata, max=10):
    features = []
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
def strava_to_mongo(path, collection):
    print(f'Extrayendo los datos de {path}')

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


# @calculate_execution_time
def get_ride_from_mongo(city_bounds, years, collection, osm_ids=[]):
    full_coords = []
    for bounds in city_bounds:
        coords = list(Polygon(bounds).exterior.coords)
        coords = [[round(x, 6), round(y, 6)] for x, y in coords]
        coords = [coords + [coords[0]]]
        full_coords.append(coords)
    del coords

    projection = ['total_trip_count', 'geometry']
    pipeline = points_inside
    inside = pipeline[0]['$match']
    inside['middlePoint']['$geoWithin']['$geometry']['coordinates'] = full_coords  # noqa
    # pipeline = points_inside_2
    # inside = pipeline[0]['$match']
    # inside['osmId']['$in'] = osm_ids
    inside['year']['$in'] = years
    pipeline[1]['$project'] = {'_id': 0, **dict.fromkeys(projection, 1)}

    return collection.aggregate(pipeline)


def process_ride_data(mongodata):
    ride_data = []
    trip_count = []
    for item in mongodata:
        coords = item['_id']['coordinates']
        total_trip_count = item['total_trip_count']
        ride_data.append((coords, total_trip_count))
        trip_count.append(total_trip_count)
    return (ride_data, trip_count)


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


def upload_data(zip_path='data.zip'):
    client = MongoClient(MONGO_DB)
    db = client[MONGO_CP_DB]
    collection = db[CP_STRAVA_COLLECTION]

    print('Importando datos a MongoDB...')
    strava_to_mongo(zip_path, collection)

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


def change_gl_version(url: str):
    match = re.search(r'@~(\d+\.\d+\.\*)', url)
    if match:
        return url.replace(match.group(1), DECKGL_VERSION)
    else:
        return url


def get_html(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    scripts = list(soup.find_all('script'))
    links = list(soup.find_all('link'))
    html = links + scripts[:2]
    headers = [change_gl_version(str(h)) for h in html]
    gl_script = scripts[-1].string
    deckgl = f'\n<div id="deck-container"></div>\n<script>{gl_script}</script>'  # noqa
    return '\n'.join(headers), deckgl
