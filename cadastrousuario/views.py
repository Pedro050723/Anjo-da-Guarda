# Create your views here.

# usuarios/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from gestao.models import Contrato

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
    # Vamos criar um contexto vazio
    context = {}
    
    if request.user.is_authenticated:
        try:
            # Se for CUIDADOR, busca os convites pendentes
            if request.user.profile.tipo_usuario == 'cuidador':
                convites = Contrato.objects.filter(
                    cuidador=request.user,
                    status='pendente'
                )
                # Adiciona os convites ao pacote de dados (contexto)
                context['convites'] = convites
                
                # Também podemos buscar os contratos já ACEITOS para mostrar a lista de idosos
                meus_idosos = Contrato.objects.filter(
                    cuidador=request.user,
                    status='ativo'
                )
                context['meus_contratos'] = meus_idosos
            
            elif request.user.profile.tipo_usuario == 'familiar':
                # Busca contratos aceitos para mostrar o botão de chat
                contratos_ativos = Contrato.objects.filter(
                    familiar=request.user, 
                    status='ativo'
                )
                context['contratos_familia'] = contratos_ativos

        except:
            pass # Se der erro no profile (ex: superuser), ignora

    return render(request, 'cadastrousuario/home.html', context)