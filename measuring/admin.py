from django.contrib import admin
from . import models

@admin.register(models.Device)
class DeviceAdmin(admin.ModelAdmin):
    """
        Sitio administrativo para Device
    """
    list_display = ('device', 'token')
    list_filter = ('device', 'token',)
    search_fields = ('device', 'token', 'coords')
    readonly_fields = ('token',)
    fieldsets = (
        ('General', {
            'fields': (
                'device', 'token', 'coords',)}),
    )
    # filter_horizontal = ('sectors',)


@admin.register(models.TrafficCount)
class TrafficCountAdmin(admin.ModelAdmin):
    """
        Sitio administrativo para Device
    """
    list_display = ('device', 'datetime')
    list_filter = ('device',)
    search_fields = ('device',)
    fieldsets = (
        ('General', {
            'fields': (
                'device', 'datetime')}),
        ('Conteo', {
            'fields': (
                'car_count', 'person_count', 'bicycle_count',
                'motorcycle_count', 'truck_count', 'bus_count',)}),
    )
    # filter_horizontal = ('sectors',)