from datetime import datetime
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from django.contrib.auth.models import (BaseUserManager,
                                        AbstractBaseUser, PermissionsMixin)
from ciudadespendientes.models import Zone
from ciudadespendientes.choices import COUNTRIES

SEPARATORS = ['_', '-', '.']


class AccountManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El correo es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class Account(PermissionsMixin, AbstractBaseUser):
    """
    El nombre de usuario es el correo electrónico.
    Al crearse un usuario, recibirá un mail para que active su cuenta.
    """
    email = models.EmailField(
        max_length=255, unique=True, db_index=True,
        verbose_name="Correo Electrónico")
    first_name = models.CharField(
        max_length=255, blank=True, verbose_name="Nombre(s)")
    last_name = models.CharField(
        max_length=255, blank=True, verbose_name="Apellido(s)")
    zones = models.ManyToManyField(
        Zone, blank=True, verbose_name="Zonas",
        help_text="Zonas que puede ver el usuario.")
    country = models.CharField(
        "País", max_length=20, choices=COUNTRIES, blank=True,
        help_text="País al que pertenece el usuario.")

    is_active = models.BooleanField(default=True, verbose_name="Activo")
    is_demo = models.BooleanField(default=False, verbose_name="Demo")
    is_staff = models.BooleanField(default=False,
                                   verbose_name="Andes Chile ONG")
    is_superuser = models.BooleanField(default=False,
                                       verbose_name="Superusuario")
    date_joined = models.DateTimeField(
        "Fecha de registro", default=timezone.now)

    cellphone = models.CharField(
        verbose_name="Celular", max_length=56, blank=True,
        validators=[
            RegexValidator(
                r"^\+?\d{11}$",
                "Sólo numeros en formato internacional (+56912345678).",
                "Número inválido"
            )
        ])
    birthdate = models.DateField(
        verbose_name="Fecha de Nacimiento", blank=True, null=True,
        default=None)

    profile_picture = models.ImageField(
        upload_to="pictures", verbose_name="Foto de perfil", blank=True,
        null=True)

    # groups = models.ManyToManyField(
    #     Group, related_name="custom_account_groups", blank=True)
    # user_permissions = models.ManyToManyField(
    #     Permission, related_name="custom_account_permissions", blank=True)

    objects = AccountManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ["email"]
        verbose_name = "Cuenta de usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.email

    def create_default_password(self):
        email = self.email.lower()
        user_name = email.split('@')
        for sep in SEPARATORS:
            first = user_name[0]
            user_name = first.split(sep)

        return user_name[0] + str(datetime.now().year)

    # def send_email(self, password):
    #     """
    #         Sends welcome email
    #     """
    #     to = [self.get_full_email()]
    #     subject = 'Bienvenido a Drivetech'
    #     template_name = 'enterprises/new_user'
    #     tags = ['register', 'enterprise']
    #     context = {
    #         'password': password, 'enterprise': None,
    #         'enterprise_admin': None,
    #         'name': self.get_full_name,
    #         'email': self.email}
    #     send_email.delay(
    #         subject, to, template_name, context=context, tags=tags)
