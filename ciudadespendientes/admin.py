from django.contrib import admin
from easy_select2 import Select2
from . import models
from django.db import models as mod


@admin.register(models.Zone)
class ZoneAdmin(admin.ModelAdmin):
    """
        Sitio administrativo para Zone
    """
    list_display = ('name', 'zone_type', 'country',)
    list_filter = ('name', 'zone_type', 'country',)
    search_fields = ('name', 'zone_type', 'country',)
    fieldsets = (
        ('General', {
            'fields': (
                'name', 'zone_type', 'country',)}),
        ('Pertenencia de la zona', {
            'fields': ('sectors',)}),
    )
    filter_horizontal = ('sectors',)


@admin.register(models.StravaData)
class StravaDataAdmin(admin.ModelAdmin):
    """
        Sitio administrativo para StravaData
    """
    list_display = ('sector', 'year', 'month', 'osm_id', 'coords', 'on_mongo',)
    list_filter = ('on_mongo',
                   'year', 'sector',)
    search_fields = ('zone', 'year', 'sector',)
    readonly_fields = ('osm_id', 'coords',)
    formfield_overrides = {
        mod.ForeignKey: {'widget': Select2},
    }
