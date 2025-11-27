# gestao/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    # Conexão 1-para-1 com o modelo User padrão do Django
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Nossos campos personalizados
    TIPO_USUARIO_ESCOLHAS = (
        ('cuidador', 'Cuidador'),
        ('familiar', 'Familiar'),
    )
    tipo_usuario = models.CharField(max_length=10, choices=TIPO_USUARIO_ESCOLHAS)

    def __str__(self):
        return f"{self.user.username} - {self.get_tipo_usuario_display()}"
    
class Idoso(models.Model):
    familiar_responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="idosos"
    )
    nome = models.CharField(max_length=100)
    idade = models.PositiveIntegerField()
    condicoes_saude = models.TextField(blank=True, null=True, verbose_name="Condições de Saúde")
    
    # Relação com cuidadores via Contrato
    cuidadores = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Contrato',
        through_fields=('idoso', 'cuidador'),
        related_name="idosos_cuidados"
    )

    def __str__(self):
        return self.nome

# 2. Modelo CONTRATO (Vínculo Familiar-Cuidador-Idoso)
class Contrato(models.Model):
    familiar = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="contratos_feitos")
    cuidador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="contratos_recebidos")
    idoso = models.ForeignKey(Idoso, on_delete=models.CASCADE)
    
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('ativo', 'Ativo'),
        ('recusado', 'Recusado'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pendente')
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cuidador', 'idoso')

    def __str__(self):
        return f"Contrato: {self.idoso.nome} - {self.cuidador.username}"

# 3. Modelo CHAT (Sala de conversa ligada ao Contrato)
class Chat(models.Model):
    contrato = models.OneToOneField(Contrato, on_delete=models.CASCADE, related_name="chat_room")
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat do Contrato #{self.contrato.id}"

# 4. Modelo MENSAGEM (Do Chat)
class Mensagem(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="mensagens")
    remetente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    texto = models.TextField()
    data_envio = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['data_envio']

# 5. Modelo ROTINA (Diário)
class Rotina(models.Model):
    idoso = models.ForeignKey(Idoso, on_delete=models.CASCADE, related_name="rotinas")
    cuidador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    data = models.DateField(auto_now_add=True)

    medicamentos = models.TextField(blank=True, null=True)
    refeicoes = models.TextField(blank=True, null=True)
    atividades = models.TextField(blank=True, null=True)
    anormalidades = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('idoso', 'data')
        ordering = ['-data']

# 6. Modelo PLANO (Financeiro)
class Plano(models.Model):
    nome = models.CharField(max_length=50)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    limite_idosos = models.IntegerField(default=2)
    historico_ilimitado = models.BooleanField(default=False)
    dias_validade = models.IntegerField(default=30)

    def __str__(self):
        return self.nome

# 7. Modelo ASSINATURA (Financeiro)
class Assinatura(models.Model):
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('ativa', 'Ativa'),
        ('cancelada', 'Cancelada'),
    )
    familiar = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='assinatura'
    )
    plano = models.ForeignKey(Plano, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    data_inicio = models.DateTimeField(auto_now_add=True)
    data_expiracao = models.DateTimeField(null=True, blank=True)

    def ativar(self):
        self.status = 'ativa'
        self.data_inicio = timezone.now()
        if self.plano:
            self.data_expiracao = self.data_inicio + timedelta(days=self.plano.dias_validade)
        self.save()

    def esta_valida(self):
        agora = timezone.now()
        return self.status == 'ativa' and self.data_expiracao and self.data_expiracao > agora
    
class Chat(models.Model):
    # Vínculo 1-para-1 com o Contrato (conforme VCP08)
    # Assim que um contrato é aceito, esse chat passa a existir virtualmente
    contrato = models.OneToOneField(
        Contrato, 
        on_delete=models.CASCADE, 
        related_name="chat_room"
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat do Contrato #{self.contrato.id}"

class Mensagem(models.Model):
    # Vínculo com o Chat (E-Chat)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="mensagens")
    
    # Vínculo com o Usuário (Quem enviou - E-Usuário)
    remetente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    texto = models.TextField()
    data_envio = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['data_envio'] # Mensagens antigas no topo, novas embaixo

    def __str__(self):
        return f"{self.remetente.username}: {self.texto[:20]}..."