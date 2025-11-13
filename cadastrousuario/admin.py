from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import E_Usuario

# Isso faz aparecer a tabela de Perfis no painel /admin
admin.site.register(E_Usuario)