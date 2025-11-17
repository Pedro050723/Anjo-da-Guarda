from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import IdosoForm
from cadastrousuario.models import Profile

# Create your views here.

@login_required # 1. Garante que o usuário está logado
def cadastrar_idoso(request):
    
    # 2. Verifica se o usuário é um 'Familiar'
    try:
        # Pega o profile do usuário logado
        is_familiar = request.user.profile.tipo_usuario == 'familiar'
    except Profile.DoesNotExist:
        # Se não tiver profile (ex: admin), não é familiar
        is_familiar = False

    if not is_familiar:
        # Se não for familiar, redireciona para a home
        return redirect('home')

    # 3. Lógica do Formulário (igual ao de cadastro de usuário)
    if request.method == 'POST':
        form = IdosoForm(request.POST)
        if form.is_valid():
            # Esta é a lógica do SD03:
            idoso = form.save(commit=False) # Não salva no banco ainda
            idoso.familiar_responsavel = request.user # Associa o ID_Usuario (Familiar)
            idoso.save() # Agora salva no banco
            return redirect('home') # Redireciona para home (ou painel do familiar)
    else:
        form = IdosoForm()
        
    return render(request, 'gestao/cadastrar_idoso.html', {'form': form})