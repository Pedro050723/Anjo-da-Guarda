#import relacionados a forms
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
from django.db import transaction # Para garantir que os dois sejam criados

# usuarios/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login
#from .models import C_Cadastro não faz mais esse import pq agora a classe está aqui

#aqui entra a parte de forms
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
    return render(request, 'cadastrousuario/cadastrar.html', {'form': form})

def home(request):
    return render(request, 'home.html')