# gestao/forms.py
from django import forms
from .models import Idoso, Contrato, Rotina, Profile
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction # Para garantir que os dois sejam criados

class C_Cadastro(UserCreationForm):
    # Adicionamos nosso campo 'tipo_usuario' ao formulário
    TIPO_USUARIO_ESCOLHAS = (
        ('familiar', 'Familiar'),
        ('cuidador', 'Cuidador'),
    )
    tipo_usuario = forms.ChoiceField(
        choices=TIPO_USUARIO_ESCOLHAS, 
        label="Tipo de conta"
    )

    class Meta(UserCreationForm.Meta):
        # Usamos o modelo User e os campos padrão
        model = User
        fields = UserCreationForm.Meta.fields + ('email',) # Adiciona o campo email

    @transaction.atomic # Garante que ou tudo dá certo, ou nada é salvo
    def save(self, commit=True):
        # 1. Salva o usuário (username, password)
        user = super().save(commit=False)
        # O UserCreationForm já cuida da criptografia da senha
        
        if commit:
            user.save()
            
            # 2. Pega o 'tipo_usuario' do formulário
            tipo = self.cleaned_data.get('tipo_usuario')

            # 3. Cria o Profile conectado ao usuário
            Profile.objects.create(
                user=user,
                tipo_usuario=tipo
            )
        return user
    
class IdosoForm(forms.ModelForm):
    class Meta:
        model = Idoso
        # Os campos do formulário (Nome, Idade, Observações do SD03)
        fields = ['nome', 'idade', 'condicoes_saude']
        
        
        # Não incluímos 'familiar_responsavel' aqui
        # porque ele será pego automaticamente do usuário logado (na view).

class ContratoForm(forms.ModelForm):
    # Campo para encontrar o cuidador
    username_cuidador = forms.CharField(
        label="Nome de usuário do Cuidador",
        max_length=150
    )
    # Campo para selecionar o idoso
    # Vamos preencher as opções (choices) dinamicamente na view
    idoso = forms.ModelChoiceField(
        queryset=Idoso.objects.none(), 
        label="Para qual idoso?"
    )

    class Meta:
        model = Contrato
        fields = ['idoso', 'username_cuidador'] # Campos que o usuário vê

    def __init__(self, *args, **kwargs):
        # Pega o 'user' (Familiar) que passamos da view
        familiar = kwargs.pop('familiar', None)
        super().__init__(*args, **kwargs)
        
        if familiar:
            # Filtra o campo 'idoso' para mostrar APENAS os idosos
            # que pertencem ao Familiar logado
            self.fields['idoso'].queryset = Idoso.objects.filter(
                familiar_responsavel=familiar
            )
class RotinaForm(forms.ModelForm):
    class Meta:
        model = Rotina
        fields = ['medicamentos', 'refeicoes', 'atividades', 'anormalidades']
        widgets = {
            'medicamentos': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Quais remédios foram dados?'}),
            'refeicoes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'O que o idoso comeu?'}),
            'atividades': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Passeios, TV, conversas...'}),
            'anormalidades': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Algo fora do comum?'}),
        }