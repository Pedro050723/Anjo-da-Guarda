from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages # Para enviar feedback (ex: "Cuidador não encontrado")
from .forms import IdosoForm, ContratoForm, RotinaForm, C_Cadastro # Importe o novo form
from django.utils import timezone # Para pegar a data de hoje
from .models import Idoso, Contrato, Rotina # Importe o modelo
from .models import Profile
from django.shortcuts import get_object_or_404 #segurança

# Create your views here.
def cadastrar(request):
    # Se o formulário foi enviado (POST)
    if request.method == 'POST':
        form = C_Cadastro(request.POST)
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
        form = C_Cadastro()
        
    # Renderiza o template HTML com o formulário
    return render(request, 'gestao/cadastrar.html', {'form': form})

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

        except:
            pass # Se der erro no profile (ex: superuser), ignora

    return render(request, 'gestao/home.html', context)

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

@login_required
def atualizar_rotina(request, idoso_id):
    # 1. Segurança: Verifica se o Cuidador tem contrato ATIVO com esse Idoso
    # (Isso cobre a validação inicial do diagrama)
    idoso = get_object_or_404(Idoso, id=idoso_id)
    tem_contrato = Contrato.objects.filter(
        cuidador=request.user, 
        idoso=idoso, 
        status='ativo'
    ).exists()

    if not tem_contrato:
        messages.error(request, "Você não tem permissão para cuidar deste idoso.")
        return redirect('home')

    # 2. Verifica se já existe rotina HOJE (Lógica de "Atualizar")
    hoje = timezone.now().date()
    rotina_existente = Rotina.objects.filter(idoso=idoso, data=hoje).first()

    if request.method == 'POST':
        # Se já existe, atualiza (instance=rotina_existente). Se não, cria nova.
        form = RotinaForm(request.POST, instance=rotina_existente)
        if form.is_valid():
            rotina = form.save(commit=False)
            rotina.idoso = idoso
            rotina.cuidador = request.user
            rotina.save()
            messages.success(request, "Rotina atualizada com sucesso!")
            return redirect('home')
    else:
        # Preenche o formulário com dados existentes se houver
        form = RotinaForm(instance=rotina_existente)

    return render(request, 'gestao/atualizar_rotina.html', {
        'form': form, 
        'idoso': idoso,
        'hoje': hoje
    })

@login_required
def visualizar_rotina(request, idoso_id):
    # 1. Busca o Idoso
    idoso = get_object_or_404(Idoso, id=idoso_id)

    # 2. Segurança: Só o Familiar dono do idoso pode ver (RF05)
    # (Ou um cuidador com contrato ativo, se quisermos expandir depois)
    if idoso.familiar_responsavel != request.user:
        messages.error(request, "Você não tem permissão para ver a rotina deste idoso.")
        return redirect('home')

    # 3. Busca as rotinas no banco (ordenadas da mais recente para a antiga)
    # O 'related_name="rotinas"' que definimos no models.py ajuda aqui
    rotinas = idoso.rotinas.all().order_by('-data')

    return render(request, 'gestao/visualizar_rotina.html', {
        'idoso': idoso,
        'rotinas': rotinas
    })