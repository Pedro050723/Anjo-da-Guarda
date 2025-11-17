# gestao/urls.py
from django.urls import path
from . import views

app_name = 'gestao' # Boa prática para organizar

urlpatterns = [
    # URL: /gestao/cadastrar-idoso/
    path('cadastrar-idoso/', views.cadastrar_idoso, name='cadastrar_idoso'),
]