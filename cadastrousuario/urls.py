from django.urls import path
from . import views # Importa as views do app (o arquivo views.py)

urlpatterns = [
    # Quando a URL for '/contas/registrar/',
    # chame a função 'registrar' de 'views.py'
    path('cadastrar/', views.cadastrar, name='cadastrar'),
    
    # Você adicionaria as URLs de login/logout aqui também
    # path('login/', ...),
]