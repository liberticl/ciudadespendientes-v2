from . import models
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import AccountChangeForm, AccountCreationForm


@admin.register(models.Account)
class AccountAdmin(UserAdmin):
    # The forms to add and change user instances
    form = AccountChangeForm
    add_form = AccountCreationForm

    list_display = (
        'email', 'first_name', 'last_name', 'cellphone', 'country',
        'is_active', 'last_login')
    list_filter = (
        'is_active', 'country', 'zones')
    fieldsets = (
        ('Información Personal', {
            'fields': (
                'email', 'first_name', 'last_name', 'cellphone',
                'birthdate', 'country', 'password',)}),
        ('Sobre el usuario', {
            'fields': ('is_active', 'is_demo', 'is_staff', 'is_superuser',)}),
        ('Accesos', {
            'fields': ('zones',)}),
        ('Fechas Importantes', {
            'fields': ('last_login', 'date_joined',)}),
        # ('Ajustes', {'fields': ('timezone', 'settings',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email',)}  # 'password1', 'password2')}
         ),
    )
    search_fields = (
        'email', 'first_name', 'last_name',)
    ordering = ('email',)
    filter_horizontal = ('zones',)

    # actions = [
    #     actions.set_password,
    #     actions.reset_pin,
    #     actions.send_email,
    #     actions.generate_permissions_token,
    #     actions.generate_vehicles_token,
    #     actions.delete_user_sessions,
    #     actions.clean_user
    # ]
    # inlines = (EnterprisePermissionInline, NotificationInline,)
