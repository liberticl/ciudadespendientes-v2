from django.db import models


class Device(models.Model):
    """
    Modelo para gestionar dispositivos, su ubicación y tokens únicos.
    """
    device_name = models.CharField(
        max_length=100, unique=True,
        help_text="Nombre único para el dispositivo")
    token = models.CharField(
        max_length=64, unique=True,
        help_text="Token de autenticación único para el dispositivo")
    coords = models.CharField(
        "Coordenadas", max_length=30,
        help_text="Ubicación del dispositivo. Ej: '-33.0458456,-71.6196749'.")

    def __str__(self):
        return self.device_name


class TrafficCount(models.Model):
    """
    Modelo para almacenar datos agrupados de tráfico.
    """
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    datetime = models.DateTimeField(help_text="Fecha y hora de la medición")
    car_count = models.PositiveIntegerField(default=0)
    person_count = models.PositiveIntegerField(default=0)
    bicycle_count = models.PositiveIntegerField(default=0)
    motorcycle_count = models.PositiveIntegerField(default=0)
    truck_count = models.PositiveIntegerField(default=0)
    bus_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Conteo de tráfico"
        ordering = ['-datetime']

    def __str__(self):
        return f"Conteo de tráfico de {self.device.device_name} en {self.datetime}" # noqa
