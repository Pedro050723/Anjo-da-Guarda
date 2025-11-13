# Create your views here.

# usuarios/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm

def cadastrar(request):
    # Se o formulário foi enviado (POST)
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # O método save() do nosso formulário (que criamos no Passo 3)
            # já cria o User E o Profile.
            user = form.save()
            
            # Loga o usuário automaticamente após o registro
            login(request, user)
            
            # Redireciona para uma página de "sucesso" ou "home"
            # (Vamos supor que você tenha uma URL 'home' definida)
            return redirect('home') # NOTA: Você precisará criar essa URL 'home'
    
    # Se for a primeira vez (GET), apenas mostra o formulário vazio
    else:
        form = CustomUserCreationForm()
        
    # Renderiza o template HTML com o formulário
    return render(request, 'cadastrousuario/cadastrar.html', {'form': form})

def home(request):
    return render(request, 'home.html')