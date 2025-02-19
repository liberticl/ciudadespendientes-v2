from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from pymongo import MongoClient
from django.conf import settings
from .codes.plot_maps import (get_ride_from_mongo,
                              process_ride_data, get_city_data)
from .codes.classifier import get_statistics, classify
from .utils import get_middle_point
import pydeck as pdk

ALLOWED_YEARS = [2019, 2020, 2021, 2022, 2023]
ALLOWED_CITIES = ['Viña del Mar', 'Valparaíso',
                  'Villa Alemana', 'Quilpué', 'Concón']


@login_required
def index(request):
    if (not request.user.is_authenticated):
        redirect('login')

    if request.method == "POST":
        years = request.POST.getlist("periodo")
        cities = request.POST.getlist("comunas")

        return redirect(reverse("show_data") + f"?periodo={','.join(years)}&comunas={','.join(cities)}")  # noqa

    return render(request, "ciudadespendientes/buscar.html",
                  {'periodo': ALLOWED_YEARS, 'comunas': ALLOWED_CITIES})


@login_required
def show_data(request):
    if (not request.user.is_authenticated):
        redirect('error_404')

    years = [int(year) for year in request.GET["periodo"].split(',')]
    cities = [city + ', Chile' for city in request.GET["comunas"].split(',')]

    client = MongoClient(settings.MONGO_DB)
    db = client[settings.MONGO_CP_DB]
    collection = db[settings.CP_STRAVA_COLLECTION]

    all_bounds = []
    all_references = []
    for city in cities:
        city_data = get_city_data(city)
        all_bounds.append(city_data[0])
        all_references.append(city_data[1])

    center = get_middle_point(all_references)
    m, s = color_ride_map(all_bounds, center, years,
                          collection, anual=False)
    dynamic = m.to_html(as_string=True, notebook_display=True)
    stats = [round(x) for x in s]
    return render(request, 'ciudadespendientes/mapa.html', {
                  'stats': stats,
                  'dynamic_content': dynamic
                  })


def error_404(request, exception=None):
    return render(request, '404.html', status=404)


def prepare_map(center):
    view_state = pdk.ViewState(
        latitude=center[0],
        longitude=center[1],
        zoom=13,
        pitch=2,  # Inclinación del mapa (0 para 2D)
    )

    layers = {
        'green': pdk.Layer(
            type="PathLayer",
            data=[],
            get_path="coordinates",
            get_color="[0, 128, 0, 230]",
            get_width=4,
            # width_scale=4,
            width_min_pixels=2,
            pickable=True,
        ),
        'orange': pdk.Layer(
            type="PathLayer",
            data=[],
            get_path="coordinates",
            get_color="[255, 165, 0, 200]",
            get_width=3,
            # width_scale=3,
            width_min_pixels=2,
            pickable=True,
        ),
        'red': pdk.Layer(
            type="PathLayer",
            data=[],
            get_path="coordinates",
            get_color="[255, 0, 0, 200]",
            get_width=3,
            # width_scale=3,
            width_min_pixels=2,
            pickable=True,
        ),
    }

    return (view_state, layers)


def color_ride_map(city_bounds, center, years, collection,
                   factor=1, anual=False):
    view_state, layers = prepare_map(center)
    mongodata = get_ride_from_mongo(city_bounds, years, collection)
    ride_data, trip_count = process_ride_data(mongodata)

    stats = get_statistics(
        trip_count, years) if anual else get_statistics(trip_count)

    # Clasificar y agregar datos a las capas
    for coords, trips in ride_data:
        classification = classify(
            trips, years, method='general', factor=factor,
            statistics=stats, anual=anual
        )

        if anual and isinstance(years, list):
            trips = round(trips / len(years) / factor)
        else:
            trips = round(trips / factor)

        data = {
            "coordinates": coords,  # [[c[1],c[0]] for c in coords],
            "trips": trips,
        }

        # Agregar los datos a la capa correspondiente
        layers[classification[0]].data.append(data)

    mapa = pdk.Deck(
        layers=list(layers.values()),
        initial_view_state=view_state,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json", # noqa
        tooltip={"text": "Viajes totales: {trips}"},
    )
    return mapa, stats
