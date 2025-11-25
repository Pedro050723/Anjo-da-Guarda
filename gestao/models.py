from django.db import models
from django.conf import settings

# Create your models here.

class Idoso(models.Model):
    # Esta linha conecta o Idoso ao usuário Familiar
    # Usamos settings.AUTH_USER_MODEL para referenciar o User padrão
    familiar_responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="idosos" # Permite acessar user.idosos
    )

    # Informações básicas pedidas no RF04 
    nome = models.CharField(max_length=100)
    idade = models.PositiveIntegerField()
    condicoes_saude = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Condições de Saúde Principais"
    )

    # Esta é a relação Muitos-para-Muitos com o Usuário (Cuidador)
    # através do nosso futuro modelo 'Contrato'.
    cuidadores = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Contrato', # O modelo que fará a ponte
        through_fields=('idoso', 'cuidador'),
        related_name="idosos_cuidados"
    )

    def __str__(self):
        return self.nome
    
class Contrato(models.Model):
    # Quem contratou (o dono do Idoso)
    familiar = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="contratos_feitos"
    )
    # Quem foi contratado
    cuidador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="contratos_recebidos"
    )
    # Para qual idoso é o contrato
    idoso = models.ForeignKey(
        Idoso,
        on_delete=models.CASCADE
    )
    
    # Status do convite (como o RF06 menciona "Após o aceite")
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('ativo', 'Ativo'),
        ('recusado', 'Recusado'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pendente')
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Garante que não se pode convidar o mesmo cuidador 
        # para o mesmo idoso duas vezes
        unique_together = ('cuidador', 'idoso')

    def __str__(self):
        return f"Contrato para {self.idoso.nome} com {self.cuidador.username} ({self.get_status_display()})"
    
class Rotina(models.Model):
    idoso = models.ForeignKey(Idoso, on_delete=models.CASCADE, related_name="rotinas")
    cuidador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    data = models.DateField(auto_now_add=True)

    medicamentos = models.TextField(blank=True, null=True, verbose_name="Medicamentos")
    refeicoes = models.TextField(blank=True, null=True, verbose_name="Refeições")
    atividades = models.TextField(blank=True, null=True, verbose_name="Atividades de Lazer")
    anormalidades = models.TextField(blank=True, null=True, verbose_name="Anormalidades/Ocorrências")

    class Meta:
        unique_together = ('idoso', 'data')
        ordering = ['-data']

    def __str__(self):
        return f"Rotina de {self.idoso.nome} em {self.data}"