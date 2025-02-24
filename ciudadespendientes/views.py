from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import LayerControlForm
from django.urls import reverse
from django.conf import settings
from .codes.plot_maps import (get_ride_from_mongo,
                              process_ride_data, get_city_data)
from .codes.classifier import get_statistics, classify
from .utils import get_middle_point
import pydeck as pdk
from bs4 import BeautifulSoup

collection = settings.STRAVA_COLLECTION
LAYER_COLORS = settings.LAYERS
GREEN = settings.GREEN
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
    layercontrol = LayerControlForm(request.POST or None)
    years = [int(year) for year in request.GET["periodo"].split(',')]
    cities = [city + ', Chile' for city in request.GET["comunas"].split(',')]

    all_bounds = []
    all_references = []
    for city in cities:
        city_data = get_city_data(city)
        all_bounds.append(city_data[0])
        all_references.append(city_data[1])

    center = get_middle_point(all_references)
    m, s = color_ride_map(all_bounds, center, years,
                          collection, anual=False, control=layercontrol)
    html_map = m.to_html(as_string=True)
    body_content = get_map_html(html_map)
    stats = [round(x) for x in s]
    return render(request, 'ciudadespendientes/map.html', {
                  'stats': stats,
                  'content': body_content,
                  'form': layercontrol,
                  })


def error_404(request, exception=None):
    return render(request, '404.html', status=404)


def create_layer(valid, data, is_visible=False):
    green = False if data['color_txt'] == GREEN else True
    return pdk.Layer(
        "PathLayer",
        data=[],
        get_path="coordinates",
        get_color=data['color'],
        get_width=data['width'],
        width_min_pixels=2,
        pickable=True,
        visible=is_visible if valid else green,
        name=data['label'],
    )


def prepare_map(center, control=None):
    view_state = pdk.ViewState(
        latitude=center[0],
        longitude=center[1],
        zoom=13,
        pitch=0,
    )

    layers = {}
    valid = control and control.is_valid()
    for layer, data in LAYER_COLORS.items():
        if (valid):
            is_visible = control.cleaned_data.get(layer, None)
            layers[layer] = create_layer(valid, data, is_visible=is_visible)
        else:
            layers[layer] = create_layer(False, data)

    return (view_state, layers)


def color_ride_map(city_bounds, center, years, collection,
                   factor=1, anual=False, control=None):
    view_state, layers = prepare_map(center, control=control)
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
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",  # noqa
        tooltip={"text": "Viajes totales: {trips}"},
    )

    return mapa, stats


def get_map_html(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    script = list(soup.find_all('script'))[-1].string
    return ''.join(
        str(child) for child in soup.body.children) + f"\n<script>{script}</script>" # noqa
