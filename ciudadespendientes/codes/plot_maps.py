import geopandas as gpd
import folium
from .apis import get_place_polygon
from .mongodb import points_inside
from shapely.geometry import Point, Polygon


def middle_points_map(collection):
    projection = ['year', 'geometry']
    cursor = collection.find(
        points_inside,
        {'_id': 0, **dict.fromkeys(projection, 1)})

    data = list(cursor)
    parsed_data = []
    for item in data:
        parsed_proj = {}
        for key in projection:
            if key != 'geometry':
                parsed_proj.update({key: item[key]})
            else:
                parsed_proj.update(
                    {'geometry': Point(item[key]['coordinates'])})
        parsed_data.append(parsed_proj)

    gdf = gpd.GeoDataFrame(parsed_data).head(400)

    mapa = folium.Map(location=(-33.049689, -71.621202),    # Mi casa
                      zoom_start=13,    # Ver si es factible automatizar
                      control_scale=True
                      )
    geojson_data = gdf.to_json()
    folium.GeoJson(geojson_data).add_to(mapa)
    return mapa


def get_city_data(city):
    polygon = get_place_polygon(city)
    gdf_city = polygon[0].set_crs("epsg:4326")
    gdf_city = gdf_city.to_crs(crs=3857)
    gdf_city['area'] = gdf_city['geometry'].area
    data = gdf_city[gdf_city['area'] == gdf_city['area'].max()]
    data = data.to_crs(crs=4326).to_dict()
    return [data['geometry'][0], polygon[1]]


def get_ride_from_mongo(city_bounds, years, collection):
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


# Incluye visualización de ascensores
# Crear función con  las capas
def color_ride_map2(city, center, years, collection1, collection2):
    coords = list(Polygon(get_city_data(city)).exterior.coords)
    coords = [[round(x, 6), round(y, 6)] for x, y in coords]
    coords = [coords + [coords[0]]]
    inside = points_inside[0]['$match']
    inside['middlePoint']['$geoWithin']['$geometry']['coordinates'] = coords
    inside['year']['$in'] = years
    projection = ['total_trip_count', 'geometry']
    del coords
    cursor1 = collection1.find(
        inside,
        {'_id': 0, **dict.fromkeys(projection, 1)})

    cursor2 = collection2.find()

    tile = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}'  # noqa
    attr = 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ, TomTom, Intermap, iPC, USGS, FAO, NPS, NRCAN, GeoBase, Kadaster NL, Ordnance Survey, Esri Japan, METI, Esri China (Hong Kong), and the GIS User Community'  # noqa

    mapa = folium.Map(
        location=center,
        zoom_start=13,
        control_scale=True,
        prefer_canvas=True,
        tiles='')

    folium.TileLayer(tile, name='Mapa', attr=attr).add_to(mapa)

    color_layers = {'green': folium.FeatureGroup(name='Flujo bajo'),
                    'orange': folium.FeatureGroup(name='Flujo medio'),
                    'red': folium.FeatureGroup(name='Flujo alto'),
                    'ascensores': folium.FeatureGroup(name='Ascensores'),
                    }

    # https://sni.gob.cl/storage/docs/Ciclo-Rutas-2013.pdf (pag 16)
    def classify(trip_count, years, factor):
        trip_count = trip_count / factor
        by_day = trip_count / (365 * len(years))
        if (by_day > 251):
            return ['red', {"opacity": 0.9, "weight": 4}]
        elif (by_day > 151):
            return ['orange', {"opacity": 0.8, "weight": 3}]
        else:
            return ['green', {"opacity": 0.3, "weight": 3}]

    for item in cursor1:
        coords = [[lat, lon] for lon, lat in item['geometry']['coordinates']]
        total_trip_count = item['total_trip_count']
        classification = classify(total_trip_count, years)
        total_trip_count = '{:,.0f}'.format(
            round(item['total_trip_count'] / 0.1)).replace(',', '.')

        folium.PolyLine(locations=coords,
                        color=classification[0],
                        tooltip=f"Viajes anuales estimados: {total_trip_count}",  # noqa
                        **classification[1]).add_to(color_layers[classification[0]])  # noqa

    for item in cursor2:
        coords = item['punto_referencia']['coordinates']
        ascensor = item['nombre']
        pasajeros_informados = '{:,.0f}'.format(
            item['pasajeros_informados']).replace(',', '.')

        folium.Marker(
            coords,
            tooltip=f"{ascensor} - Viajes: {pasajeros_informados}"
        ).add_to(color_layers['ascensores'])

    for color_group in color_layers.values():
        color_group.add_to(mapa)

    folium.LayerControl(collapsed=False,
                        overlay=True).add_to(mapa)

    return mapa
