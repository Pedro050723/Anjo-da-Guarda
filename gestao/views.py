from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

# Importando seus Models (Note que mantive os nomes que você enviou)
from .models import E_Idoso, E_Contrato, Rotina, Profile, Plano, E_Assinatura, Chat, E_MSN

# ==============================================================================
# VCP 02 - Cadastrar Usuário (Sem forms.py)
# ==============================================================================
def cadastrar(request):
    if request.method == 'POST':
        # 1. Captura os dados brutos do HTML
        username = request.POST.get('username')
        email = request.POST.get('email')
        senha1 = request.POST.get('senha1')
        senha2 = request.POST.get('senha2')
        tipo_usuario = request.POST.get('tipo_usuario')

        # 2. Validações Manuais (Lógica do Controlador)
        erros = []
        
        if User.objects.filter(username=username).exists():
            erros.append("Este nome de usuário já está em uso.")
            
        if senha1 != senha2:
            erros.append("As senhas não conferem.")

        if erros:
            # Se tiver erros, volta para a tela mostrando as mensagens
            for erro in erros:
                messages.error(request, erro)
            return render(request, 'gestao/cadastrar.html')

        # 3. Criação Atômica (User + Profile)
        try:
            with transaction.atomic():
                # Cria o User padrão do Django (já criptografa a senha)
                user = User.objects.create_user(username=username, email=email, password=senha1)
                
                # Cria o Profile vinculado
                Profile.objects.create(user=user, tipo_usuario=tipo_usuario)
                
                # Loga e Redireciona
                login(request, user)
                return redirect('home')
                
        except Exception as e:
            messages.error(request, f"Erro ao cadastrar: {e}")

    # GET: Apenas mostra a tela
    return render(request, 'gestao/cadastrar.html')


# ==============================================================================
# VCP 01 e Home
# ==============================================================================
def home(request):
    context = {}
    
    if request.user.is_authenticated:
        try:
            # Lógica para Cuidador
            if request.user.profile.tipo_usuario == 'cuidador':
                convites = E_Contrato.objects.filter(
                    cuidador=request.user,
                    status='pendente'
                )
                meus_idosos = E_Contrato.objects.filter(
                    cuidador=request.user,
                    status='ativo'
                )
                context['convites'] = convites
                context['meus_contratos'] = meus_idosos
            
            # Lógica para Familiar
            elif request.user.profile.tipo_usuario == 'familiar':
                contratos_ativos = E_Contrato.objects.filter(
                    familiar=request.user, 
                    status='ativo'
                )
                context['contratos_familia'] = contratos_ativos

        except Exception:
            pass 

    return render(request, 'gestao/home.html', context)


# ==============================================================================
# VCP 03 - Cadastrar Idoso (Sem forms.py)
# ==============================================================================
@login_required
def cadastrar_idoso(request):
    # Verificação de Segurança (Apenas Familiar)
    if not hasattr(request.user, 'profile') or request.user.profile.tipo_usuario != 'familiar':
        return redirect('home')
    
    # --- Lógica do Plano (Upgrade) ---
    try:
        limite = request.user.assinatura.plano.limite_idosos
    except:
        limite = 2 

    if request.user.idosos.count() >= limite:
        messages.warning(request, f"Seu plano permite apenas {limite} idosos.")
        return redirect('gestao:listar_planos')
    # ---------------------------------

    if request.method == 'POST':
        # Captura dados
        nome = request.POST.get('nome')
        idade = request.POST.get('idade')
        observacoes = request.POST.get('condicoes_saude') # ou 'observacoes' dependendo do seu HTML

        # Salva no Banco
        E_Idoso.objects.create(
            familiar_responsavel=request.user,
            nome=nome,
            idade=idade,
            condicoes_saude=observacoes
        )
        return redirect('home')
        
    return render(request, 'gestao/cadastrar_idoso.html')


# ==============================================================================
# VCP 05 - Contratar Cuidador (Sem forms.py)
# ==============================================================================
@login_required
def contratar_cuidador(request):
    if not hasattr(request.user, 'profile') or request.user.profile.tipo_usuario != 'familiar':
        messages.error(request, "Acesso negado.")
        return redirect('home')

    if request.method == 'POST':
        username_cuidador = request.POST.get('username_cuidador')
        idoso_id = request.POST.get('idoso') # O valor virá de um <select>
        
        try:
            cuidador = User.objects.get(username=username_cuidador)
            idoso_obj = E_Idoso.objects.get(id=idoso_id, familiar_responsavel=request.user)

            if cuidador.profile.tipo_usuario != 'cuidador':
                messages.error(request, "Este usuário não é um cuidador.")
            else:
                # Cria o Contrato
                E_Contrato.objects.create(
                    familiar=request.user,
                    cuidador=cuidador,
                    idoso=idoso_obj,
                    status='pendente'
                )
                messages.success(request, f"Convite enviado para {cuidador.username}!")
                return redirect('home')

        except User.DoesNotExist:
            messages.error(request, "Cuidador não encontrado.")
        except E_Idoso.DoesNotExist:
            messages.error(request, "Idoso inválido.")
        except Exception as e:
            messages.error(request, f"Erro: {e}")

    # GET: Precisa enviar a lista de idosos para preencher o <select> no HTML
    meus_idosos = E_Idoso.objects.filter(familiar_responsavel=request.user)
    return render(request, 'gestao/contratar_cuidador.html', {'meus_idosos': meus_idosos})


# ==============================================================================
# Lógica de Contrato (Responder)
# ==============================================================================
@login_required
def responder_contrato(request, contrato_id, resposta):
    contrato = get_object_or_404(E_Contrato, id=contrato_id, cuidador=request.user)

    if resposta == 'aceitar':
        contrato.status = 'ativo'
        contrato.save()
        messages.success(request, "Contrato aceito!")
    elif resposta == 'recusar':
        contrato.status = 'recusado'
        contrato.save()
    
    return redirect('home')


# ==============================================================================
# VCP Rotina (Atualizar e Visualizar)
# ==============================================================================
@login_required
def atualizar_rotina(request, idoso_id):
    idoso = get_object_or_404(E_Idoso, id=idoso_id)
    
    # Segurança
    tem_contrato = E_Contrato.objects.filter(cuidador=request.user, idoso=idoso, status='ativo').exists()
    if not tem_contrato:
        return redirect('home')

    hoje = timezone.localdate()
    # Busca rotina existente ou None
    rotina = Rotina.objects.filter(idoso=idoso, data=hoje).first()

    if request.method == 'POST':
        # Captura manual
        medicamentos = request.POST.get('medicamentos')
        refeicoes = request.POST.get('refeicoes')
        atividades = request.POST.get('atividades')
        anormalidades = request.POST.get('anormalidades')

        # Update ou Create manual
        if rotina:
            rotina.medicamentos = medicamentos
            rotina.refeicoes = refeicoes
            rotina.atividades = atividades
            rotina.anormalidades = anormalidades
            rotina.save()
        else:
            Rotina.objects.create(
                idoso=idoso,
                cuidador=request.user,
                data=hoje,
                medicamentos=medicamentos,
                refeicoes=refeicoes,
                atividades=atividades,
                anormalidades=anormalidades
            )
        
        messages.success(request, "Rotina atualizada!")
        return redirect('home')

    return render(request, 'gestao/atualizar_rotina.html', {
        'idoso': idoso,
        'hoje': hoje,
        'rotina': rotina # Passa a rotina atual para preencher os campos no HTML
    })

@login_required
def visualizar_rotina(request, idoso_id):
    idoso = get_object_or_404(E_Idoso, id=idoso_id)

    if idoso.familiar_responsavel != request.user:
        return redirect('home')

    rotinas = idoso.rotinas.all().order_by('-data')

    # Lógica Premium
    try:
        assinatura = request.user.assinatura
        eh_premium = assinatura.esta_valida() and assinatura.plano.historico_ilimitado
    except:
        eh_premium = False

    aviso_limitacao = False
    if not eh_premium:
        sete_dias_atras = timezone.now().date() - timedelta(days=7)
        rotinas = rotinas.filter(data__gte=sete_dias_atras)
        aviso_limitacao = True

    return render(request, 'gestao/visualizar_rotina.html', {
        'idoso': idoso,
        'rotinas': rotinas,
        'aviso_limitacao': aviso_limitacao
    })


# ==============================================================================
# Financeiro (Planos e Pagamento)
# ==============================================================================
@login_required
def listar_planos(request):
    planos = Plano.objects.all().order_by('valor')
    return render(request, 'gestao/planos.html', {'planos': planos})

@login_required
def assinar_plano(request, plano_id):
    plano = get_object_or_404(Plano, id=plano_id)
    return render(request, 'gestao/pagamento_mock.html', {'plano': plano})

@login_required
def processar_pagamento(request, plano_id):
    plano = get_object_or_404(Plano, id=plano_id)
    assinatura, created = E_Assinatura.objects.get_or_create(familiar=request.user)
    assinatura.plano = plano
    assinatura.ativar()
    messages.success(request, f"Plano {plano.nome} assinado!")
    return redirect('home')


# ==============================================================================
# Chat
# ==============================================================================
@login_required
def abrir_chat(request, contrato_id):
    contrato = get_object_or_404(E_Contrato, id=contrato_id)
    
    if request.user != contrato.familiar and request.user != contrato.cuidador:
        return redirect('home')
    
    chat, created = Chat.objects.get_or_create(contrato=contrato)

    if request.method == 'POST':
        texto = request.POST.get('mensagem') # Nome do input no HTML
        if texto:
            E_MSN.objects.create(
                chat=chat,
                remetente=request.user,
                texto=texto
            )
            return redirect('gestao:abrir_chat', contrato_id=contrato.id)

    mensagens = chat.mensagens.all()

    return render(request, 'gestao/chat.html', {
        'contrato': contrato,
        'chat': chat,
        'mensagens': mensagens
    })