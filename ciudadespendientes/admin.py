from django.contrib import admin
from easy_select2 import Select2
from . import models
from django.db import models as mod
from django import forms
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.files.storage import FileSystemStorage
from . import choices
from .utils import upload_data


@admin.register(models.Zone)
class ZoneAdmin(admin.ModelAdmin):
    """
        Sitio administrativo para Zone
    """
    list_display = ('name', 'zone_type', 'country', 'region', 'osm_id', 'coords')
    list_filter = ('name', 'zone_type', 'country', 'region')
    search_fields = ('name', 'zone_type', 'country', 'region', 'osm_id')
    readonly_fields = ('osm_id', 'coords',)
    fieldsets = (
        ('General', {
            'fields': (
                'name', 'zone_type', 'country', 'region', 'available_years')}),
        # ('Pertenencia de la zona', {
        #     'fields': ('sectors',)}),
        ('Datos de OSM', {
            'fields': ('osm_id', 'coords', 'mapped_ways')}),
    )
    # filter_horizontal = ('sectors',)


class StravaDataForm(forms.ModelForm):
    start_year = forms.ChoiceField(
        choices=choices.YEARS, required=False, label="Año inicio",
        help_text="Opcional. Si se especifica junto con Año fin, se crearán múltiples registros para cada año en el rango."
    )
    end_year = forms.ChoiceField(
        choices=choices.YEARS, required=False, label="Año fin",
        help_text="Opcional."
    )

    class Meta:
        model = models.StravaData
        fields = '__all__'

    def clean(self):
        cd = super().clean()
        start = cd.get('start_year')
        end = cd.get('end_year')
        if start and end:
            if int(start) > int(end):
                self.add_error('end_year', 'El año final debe ser mayor o igual al inicial.')
        return cd


@admin.register(models.StravaData)
class StravaDataAdmin(admin.ModelAdmin):
    """
        Sitio administrativo para StravaData
    """
    form = StravaDataForm
    list_display = ('sector', 'year', 'month', 'on_mongo',)
    list_filter = ('on_mongo', 'year', 'sector', 'sector__region')
    search_fields = ('sector__name', 'year',)
    formfield_overrides = {
        mod.ForeignKey: {'widget': Select2},
    }
    actions = ['set_on_mongo', 'unset_on_mongo', 'duplicate_with_new_year']
    change_list_template = "admin/ciudadespendientes/stravadata_changelist.html"

    def save_model(self, request, obj, form, change):
        start = form.cleaned_data.get('start_year')
        end = form.cleaned_data.get('end_year')

        if not change and start and end:
            start_yr, end_yr = int(start), int(end)
            obj.year = start_yr
            super().save_model(request, obj, form, change)
            
            # Duplicar objeto principal
            for y in range(start_yr + 1, end_yr + 1):
                models.StravaData.objects.create(
                    on_mongo=obj.on_mongo,
                    sector=obj.sector,
                    month=obj.month,
                    year=y
                )
        else:
            super().save_model(request, obj, form, change)

    @admin.action(description='Marcar como cargados en MongoDB')
    def set_on_mongo(self, request, queryset):
        count = queryset.update(on_mongo=True)
        self.message_user(request, f"{count} registros marcados como cargados en MongoDB.")

    @admin.action(description='Desmarcar como cargados en MongoDB')
    def unset_on_mongo(self, request, queryset):
        count = queryset.update(on_mongo=False)
        self.message_user(request, f"{count} registros desmarcados de MongoDB.")

    @admin.action(description="Duplicar selección para otro año")
    def duplicate_with_new_year(self, request, queryset):
        if 'apply' in request.POST:
            new_year = request.POST.get('new_year')
            if new_year:
                for obj in queryset:
                    obj.pk = None
                    obj.year = int(new_year)
                    obj.save()
                self.message_user(request, f"{queryset.count()} colecciones duplicadas exitosamente al año {new_year}.")
                return HttpResponseRedirect(request.get_full_path())
            else:
                self.message_user(request, "Debe ingresar un año.", level=messages.ERROR)
        
        context = dict(
            self.admin_site.each_context(request),
            queryset=queryset,
            years=choices.YEARS,
            opts=self.model._meta,
        )
        return render(request, "admin/ciudadespendientes/duplicate_new_year.html", context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload/', self.admin_site.admin_view(self.upload_zip_view), name='strava-upload'),
        ]
        return custom_urls + urls

    def upload_zip_view(self, request):
        if request.method == "POST":
            zip_file = request.FILES.get("zip_file")
            if zip_file:
                if not zip_file.name.endswith('.zip'):
                    messages.error(request, 'El archivo debe ser un .zip.')
                else:
                    fs = FileSystemStorage()
                    filename = fs.save(zip_file.name, zip_file)
                    file_path = fs.path(filename)
                    try:
                        upload_data(file_path)
                        messages.success(request, 'Datos importados a MongoDB correctamente.')
                    except Exception as e:
                        messages.error(request, f'Ocurrió un error al subir: {e}')
                    finally:
                        fs.delete(filename)
                return redirect("..")
            else:
                messages.error(request, "Ningún archivo seleccionado.")
                
        context = dict(
            self.admin_site.each_context(request),
            opts=self.model._meta,
        )
        return render(request, "admin/ciudadespendientes/upload_zip.html", context)
