from django.urls import path
from . import views

app_name = 'edital'

urlpatterns = [
    # Páginas HTML
    path('', views.edital_list_view, name='edital_list'),
    path('<int:edital_id>/', views.edital_detail_view, name='edital_detail'),
    
    # Endpoints da API
    path('api/criar/', views.criar_edital_api, name='api_criar_edital'),
    path('api/progresso/atualizar/', views.atualizar_progresso_api, name='api_atualizar_progresso'),
    path('api/ciclo/salvar/<int:edital_id>/', views.salvar_ciclo_api, name='api_salvar_ciclo'),
]
