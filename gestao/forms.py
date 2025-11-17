# gestao/forms.py
from django import forms
from .models import Idoso

class IdosoForm(forms.ModelForm):
    class Meta:
        model = Idoso
        # Os campos do formulário (Nome, Idade, Observações do SD03)
        fields = ['nome', 'idade', 'condicoes_saude']
        
        # Não incluímos 'familiar_responsavel' aqui
        # porque ele será pego automaticamente do usuário logado (na view).