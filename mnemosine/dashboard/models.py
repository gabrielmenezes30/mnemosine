from django.db import models
from django.contrib.auth.models import User

class Materia(models.Model):
    """Representa uma matéria/disciplina cadastrada pelo usuário."""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='materias')
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

    class Meta:
        # Garante que um usuário não pode ter matérias com o mesmo nome
        unique_together = ('usuario', 'nome')

class SessaoEstudo(models.Model):
    """Representa uma sessão de estudo cronometrada."""
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='sessoes')
    duracao_segundos = models.IntegerField()
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Converte segundos para um formato H:M:S para melhor visualização no admin
        mins, secs = divmod(self.duracao_segundos, 60)
        hours, mins = divmod(mins, 60)
        return f'{self.materia.nome} - {hours:02d}:{mins:02d}:{secs:02d} em {self.data.strftime("%d/%m/%Y")}'