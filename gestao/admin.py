# gestao/admin.py
from django.contrib import admin
# Importe todas as classes que você quer gerenciar
from .models import Profile, E_Idoso, E_Contrato, Chat, E_MSN, Rotina, Plano, E_Assinatura

# Registre elas para aparecerem no painel
admin.site.register(Profile)
admin.site.register(E_Idoso)
admin.site.register(E_Contrato)
admin.site.register(Chat)
admin.site.register(E_MSN)
admin.site.register(Rotina)
admin.site.register(Plano)
admin.site.register(E_Assinatura)