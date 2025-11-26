# gestao/urls.py
from django.urls import path
from . import views

app_name = 'gestao' # Boa prática para organizar

urlpatterns = [
    # URL: /gestao/cadastrar-idoso/
    path('cadastrar/', views.cadastrar, name='cadastrar'),
    path('cadastrar-idoso/', views.cadastrar_idoso, name='cadastrar_idoso'),
    path('contratar/', views.contratar_cuidador, name='contratar_cuidador'),
    path('responder/<int:contrato_id>/<str:resposta>/', views.responder_contrato, name='responder_contrato'),
    path('rotina/atualizar/<int:idoso_id>/', views.atualizar_rotina, name='atualizar_rotina'),
    path('rotina/visualizar/<int:idoso_id>/', views.visualizar_rotina, name='visualizar_rotina'),
]