from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from pymongo import MongoClient
from django.conf import settings
from .codes.plot_maps import get_city_data, color_ride_map
from .utils import get_middle_point

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

        return redirect(reverse("show_data") + f"?periodo={','.join(years)}&comunas={','.join(cities)}") # noqa

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
    dynamic = m.get_root().render()
    stats = [round(x) for x in s]
    return render(request, 'ciudadespendientes/mapa.html', {
                  'stats': stats,
                  'dynamic_content': dynamic
                  })


def error_404(request, exception=None):
    return render(request, '404.html', status=404)
