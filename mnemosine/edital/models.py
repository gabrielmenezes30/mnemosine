from django.db import models
from django.contrib.auth.models import User

# Modelo principal para o Edital
class Edital(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='editais')
    nome = models.CharField(max_length=200)
    conteudo_bruto = models.TextField(help_text="O texto completo colado pelo usuário para referência.")
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

# Modelo para os Blocos (Ex: BLOCO I, BLOCO II)
class Bloco(models.Model):
    edital = models.ForeignKey(Edital, on_delete=models.CASCADE, related_name='blocos')
    nome = models.CharField(max_length=100)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordem']

    def __str__(self):
        return f"{self.edital.nome} - {self.nome}"

# Modelo para as Matérias/Disciplinas
class Materia(models.Model):
    bloco = models.ForeignKey(Bloco, on_delete=models.CASCADE, related_name='materias')
    nome = models.CharField(max_length=200)
    ordem = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['ordem']

    def __str__(self):
        return self.nome

# Modelo para os Tópicos de cada Matéria
class Topico(models.Model):
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='topicos')
    descricao = models.TextField()
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordem']

    def __str__(self):
        return self.descricao[:60]

# Modelo para salvar o progresso do usuário em cada tópico
class Progresso(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progressos')
    topico = models.OneToOneField(Topico, on_delete=models.CASCADE, related_name='progresso')
    teoria = models.BooleanField(default=False)
    revisao1 = models.BooleanField(default=False)
    revisao2 = models.BooleanField(default=False)
    revisao3 = models.BooleanField(default=False)
    revisao4 = models.BooleanField(default=False)
    revisao5 = models.BooleanField(default=False)

    def __str__(self):
        return f"Progresso de {self.usuario.username} em {self.topico.descricao[:30]}"

# Modelo para o Ciclo de Estudos
class Ciclo(models.Model):
    edital = models.OneToOneField(Edital, on_delete=models.CASCADE, related_name='ciclo')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ciclos')
    materias = models.ManyToManyField(Materia, related_name='ciclos')

    def __str__(self):
        return f"Ciclo de {self.usuario.username} para {self.edital.nome}"
