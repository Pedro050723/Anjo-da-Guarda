"""
URL configuration for anjodaguarda project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# urls.py (Principal)
from django.contrib import admin
from django.urls import path, include
from gestao import views as usuario_views

# 1. Adicione esta importação para podermos configurar o Login manualmente
from django.contrib.auth import views as auth_views 

urlpatterns = [
    path('admin/', admin.site.urls),

    # 2. ADICIONE ESTA LINHA AQUI (A "Interceptadora")
    # Ela diz: "Quando acessar 'contas/login/', use MEU template, e não o padrão."
    path('contas/login/', auth_views.LoginView.as_view(template_name='gestao/login.html'), name='login'),

    # 3. Mantenha essa linha (ela vai cuidar do logout e senha, mas o login já foi resolvido acima)
    path('contas/', include('django.contrib.auth.urls')),
    
    path('', usuario_views.home, name='home'),
    path('gestao/', include('gestao.urls')),
]