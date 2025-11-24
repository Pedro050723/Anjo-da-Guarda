from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Profile

# Isso faz aparecer a tabela de Perfis no painel /admin
admin.site.register(Profile)