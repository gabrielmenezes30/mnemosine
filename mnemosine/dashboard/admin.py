# dashboard/admin.py

from django.contrib import admin
from .models import Materia, SessaoEstudo
import time

@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    """
    Configuração do Admin para o modelo Materia.
    """
    list_display = ('nome', 'usuario')
    search_fields = ('nome', 'usuario__username')
    list_filter = ('usuario',)
    ordering = ('usuario', 'nome')
    # Adiciona um campo de busca para o 'usuario', útil quando há muitos usuários
    autocomplete_fields = ('usuario',) 

@admin.register(SessaoEstudo)
class SessaoEstudoAdmin(admin.ModelAdmin):
    """
    Configuração do Admin para o modelo SessaoEstudo.
    """
    list_display = ('materia', 'get_usuario', 'duracao_formatada', 'data')
    search_fields = ('materia__nome', 'materia__usuario__username')
    list_filter = ('data', 'materia__usuario', 'materia__nome')
    ordering = ('-data',)
    
    # Melhora a performance, evitando uma consulta N+1 para buscar o usuário
    list_select_related = ('materia', 'materia__usuario') 

    def get_usuario(self, obj):
        """Retorna o nome de usuário associado à matéria."""
        return obj.materia.usuario.username
    get_usuario.short_description = 'Usuário' # Nome da coluna no admin
    get_usuario.admin_order_field = 'materia__usuario' # Permite ordenar por esta coluna

    def duracao_formatada(self, obj):
        """Formata a duração de segundos para HH:MM:SS."""
        secs = obj.duracao_segundos
        # Usa time.gmtime para converter segundos em uma struct de tempo
        struct_time = time.gmtime(secs)
        return time.strftime('%H:%M:%S', struct_time)
    duracao_formatada.short_description = 'Duração (HH:MM:SS)' # Nome da coluna
    duracao_formatada.admin_order_field = 'duracao_segundos' # Permite ordenar