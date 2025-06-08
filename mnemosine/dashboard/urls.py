from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Página principal com o cronômetro
    path('', views.home, name='home'),

    # Dashboard com os gráficos
    path('dashboard/', views.dashboard, name='dashboard'),

    # CRUD de Matérias
    path('materias/', views.listar_materias, name='listar_materias'),
    path('materias/nova/', views.cadastrar_materia, name='cadastrar_materia'),
    path('materias/editar/<int:id>/', views.editar_materia, name='editar_materia'),
    path('materias/deletar/<int:id>/', views.deletar_materia, name='deletar_materia'),

    # Endpoint para salvar a sessão de estudo via JavaScript
    path('salvar-sessao/', views.salvar_sessao, name='salvar_sessao'),
    # Endpoint para fornecer dados para o gráfico
    path('dados-grafico/', views.dados_grafico_pizza, name='dados_grafico_pizza'),

    # Autenticação
    path('login/', auth_views.LoginView.as_view(template_name='dashboard/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('cadastro/', views.cadastro, name='cadastro'),
]
