from django.db import models
from . import choices
import requests
import geopandas as gpd
from django.conf import settings
from django.db.models.signals import pre_save


class StravaData(models.Model):
    """
        Representa un conjunto de datos cargados en MongoDB para
        la plataforma. De aquí el sistema obtiene el listado de
        ciudades y años de datos disponibles.
    """

    on_mongo = models.BooleanField(
        "Cargado en MongoDB",
        help_text="Indica si los datos se encuentran disponibles en MongoDB")
    sector = models.CharField(
        "Sector", max_length=45,
        help_text="Sector que representan los datos. Ej: 'Valparaíso'.")
    year = models.IntegerField(
        "Año", help_text="Año al que pertenece el registro. Ej: 2024.")
    month = models.CharField(
        "Mes", choices=choices.MONTHS, max_length=15, default='Todo el año',
        help_text="Mes al que pertenece el registro. Ej: Enero.")
    osm_id = models.CharField(
        "ID OSM", max_length=15,
        help_text="Identificador en OpenStreetMaps. Ej: '110808'.")
    coords = models.CharField(
        "Coordenadas", max_length=30,
        help_text="Punto central del polígono. Ej: '-33.0458456,-71.6196749'.")

    def __str__(self):
        return f"{self.sector} - {self.get_month_display()} {self.year}"

    def get_coords(self):
        lat, lon = map(float, self.coords.split(','))
        return (lat, lon)

    def get_osm_data(self, save=True):
        """
            Obtiene OSM ID y coordenadas de un polígono según el
            lugar que representa.
        """
        url = f'https://nominatim.openstreetmap.org/search?q={self.sector}&format=json'  # noqa
        headers = {
            'Referer': settings.CSRF_TRUSTED_ORIGINS[0],
            'User-Agent': 'Urban planning by Andes Chile ONG'
        }
        ans = requests.get(url, headers=headers)
        data = ans.json()

        for element in data:
            if (element['type'] == 'administrative'):
                osmid = element['osm_id']
                center = f"{float(element['lat'])},{float(element['lon'])}"
                self.osm_id = osmid
                self.coords = center
                if (save):
                    self.save()
                return [osmid, center]
        print("No se ha encontrado información")
        return []

    def get_polygon(self, save=True):
        gdf = None
        url = f'http://polygons.openstreetmap.fr/get_geojson.py?id={self.osm_id}&params=0'  # noqa
        ans = requests.get(url, timeout=5)
        if (ans.status_code == 200 and save):
            self.save()
            return ans.status_code
        gdf = gpd.read_file(ans.text)
        gdf = gdf.explode(index_parts=False)
        # print(f"Búsqueda de polígono finalizada con status {ans.status_code}")
        return {
            'success': ans.status_code == 200,
            'polygon': gdf
        }

    class Meta:
        verbose_name = u'colección de Strava'
        verbose_name_plural = u'Datos de Strava'

    @classmethod
    def before_save(cls, sender, instance, *args, **kwargs):
        # Buscar datos de OSM
        if (not instance.osm_id or not instance.coords):
            instance.get_osm_data()


pre_save.connect(StravaData.before_save, sender=StravaData)


class Zone(models.Model):
    """
        Una zona es un lugar al que un usuario puede tener acceso de
        visualización. Esta puede ser un país, una región, una ciudad
        o un espacio particular.
    """

    name = models.CharField(
        "Nombre de la zona", max_length=30,
        help_text="Nombre con el que se identifica la zona. Ej: 'Mi región'.")
    zone_type = models.CharField(
        "Tipo", max_length=20, choices=choices.ZONE_TYPES,
        help_text="'Tipo de zona que representa.")
    country = models.CharField(
        "País", max_length=20, choices=choices.COUNTRIES,
        help_text="País al que pertenece la zona.")
    sectors = models.ManyToManyField(
        StravaData, blank=True, verbose_name="Sectores",
        related_name="sectores",
        help_text="Sectores asociadas a esta zona"
    )

    def __str__(self):
        return f"{self.zone_type} - {self.name}"

    class Meta:
        verbose_name = u'zona'
        verbose_name_plural = u'Zonas'
