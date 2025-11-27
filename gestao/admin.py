# gestao/admin.py
from django.contrib import admin
# Importe todas as classes que você quer gerenciar
from .models import Profile, Idoso, Contrato, Chat, Mensagem, Rotina, Plano, Assinatura

# Registre elas para aparecerem no painel
admin.site.register(Profile)
admin.site.register(Idoso)
admin.site.register(Contrato)
admin.site.register(Chat)
admin.site.register(Mensagem)
admin.site.register(Rotina)
admin.site.register(Plano)
admin.site.register(Assinatura)