from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    # Conexão 1-para-1 com o modelo User padrão do Django
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Nossos campos personalizados
    TIPO_USUARIO_ESCOLHAS = (
        ('familiar', 'Familiar'),
        ('cuidador', 'Cuidador'),
    )
    tipo_usuario = models.CharField(max_length=10, choices=TIPO_USUARIO_ESCOLHAS)

    def __str__(self):
        return f"{self.user.username} - {self.get_tipo_usuario_display()}"