# gestao/forms.py
from django import forms
from .models import Idoso, Contrato
from django.contrib.auth.models import User

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