from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages # Para enviar feedback (ex: "Cuidador não encontrado")
from .forms import IdosoForm, ContratoForm # Importe o novo form
from .models import Contrato # Importe o modelo
from cadastrousuario.models import Profile
from django.shortcuts import get_object_or_404 #segurança

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

@login_required
def contratar_cuidador(request):
    try:
        is_familiar = request.user.profile.tipo_usuario == 'familiar'
    except Profile.DoesNotExist:
        is_familiar = False

    if not is_familiar:
        messages.error(request, "Acesso negado.")
        return redirect('home')

    if request.method == 'POST':
        # Passa o 'familiar' (request.user) para o formulário
        form = ContratoForm(request.POST, familiar=request.user)
        
        if form.is_valid():
            username_cuidador = form.cleaned_data['username_cuidador']
            idoso_selecionado = form.cleaned_data['idoso']
            
            try:
                # 1. Tenta encontrar o Cuidador
                cuidador = User.objects.get(username=username_cuidador)
                
                # 2. Verifica se ele é mesmo um Cuidador
                if cuidador.profile.tipo_usuario != 'cuidador':
                    messages.error(request, f"'{username_cuidador}' não é uma conta de Cuidador.")
                else:
                    # 3. Salva o Contrato (SD05 - criarContrato)
                    Contrato.objects.create(
                        familiar=request.user,
                        cuidador=cuidador,
                        idoso=idoso_selecionado
                        # O status 'pendente' é o padrão
                    )
                    messages.success(request, f"Convite enviado para {cuidador.username}!")
                    return redirect('home')

            except User.DoesNotExist:
                messages.error(request, f"Cuidador '{username_cuidador}' não encontrado.")
            except Profile.DoesNotExist:
                 messages.error(request, f"'{username_cuidador}' não tem um perfil válido.")

    else:
        # Passa o 'familiar' (request.user) para o formulário
        form = ContratoForm(familiar=request.user)

    return render(request, 'gestao/contratar_cuidador.html', {'form': form})

@login_required
def responder_contrato(request, contrato_id, resposta):
    # Busca o contrato no banco ou dá erro 404 se não existir.
    # O filtro 'cuidador=request.user' garante que ninguém aceite o contrato de outro!
    contrato = get_object_or_404(Contrato, id=contrato_id, cuidador=request.user)

    if resposta == 'aceitar':
        contrato.status = 'ativo'
        contrato.save()
        messages.success(request, f"Você aceitou cuidar de {contrato.idoso.nome}!")
    
    elif resposta == 'recusar':
        contrato.status = 'recusado'
        contrato.save()
        messages.info(request, f"Você recusou o convite.")

    # Volta para a home
    return redirect('home')