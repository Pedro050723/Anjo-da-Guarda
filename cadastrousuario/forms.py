#o arquivo forms.py não é mais necessário e foi incluido dentro de views
""" usuarios/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import E_Usuario
from django.db import transaction # Para garantir que os dois sejam criados

class CustomUserCreationForm(UserCreationForm):
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
            E_Usuario.objects.create(
                user=user,
                tipo_usuario=tipo
            )
        return user"""