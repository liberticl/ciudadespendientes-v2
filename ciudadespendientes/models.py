from django.db import models
from . import choices


class Zone(models.Model):
    """
    Una zona es un lugar al que un usuario puede tener acceso de visualización.
    Esta puede ser un país, una región, una ciudad o un espacio particular.
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
