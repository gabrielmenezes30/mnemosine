from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.db.models import Sum
import json
from django.contrib.auth.forms import AuthenticationForm

from .models import Materia, SessaoEstudo

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'dashboard/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home(request):
    """Página inicial com o cronômetro."""
    materias = Materia.objects.filter(usuario=request.user)
    context = {
        'materias': materias
    }
    return render(request, 'dashboard/home.html', context)

@login_required
def dashboard(request):
    """Página com os gráficos de desempenho."""
    return render(request, 'dashboard/dashboard.html')

# View para fornecer os dados ao gráfico
@login_required
def dados_grafico_pizza(request):
    """Agrega os dados de estudo por matéria e retorna como JSON."""
    usuario = request.user
    dados = Materia.objects.filter(usuario=usuario, sessoes__isnull=False) \
                           .annotate(total_segundos=Sum('sessoes__duracao_segundos')) \
                           .values('nome', 'total_segundos') \
                           .order_by('-total_segundos')

    # Filtra matérias que realmente tiveram tempo de estudo
    dados_filtrados = [item for item in dados if item['total_segundos'] > 0]

    labels = [item['nome'] for item in dados_filtrados]
    data = [item['total_segundos'] / 3600 for item in dados_filtrados] # Convertendo para horas

    return JsonResponse({'labels': labels, 'data': data})

# View para salvar a sessão via AJAX/Fetch
@login_required
def salvar_sessao(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            materia_id = data.get('materia_id')
            duracao = data.get('duracao_segundos')

            if not all([materia_id, isinstance(duracao, int)]):
                 return JsonResponse({'status': 'erro', 'mensagem': 'Dados inválidos.'}, status=400)

            materia = get_object_or_404(Materia, id=materia_id, usuario=request.user)
            SessaoEstudo.objects.create(materia=materia, duracao_segundos=duracao)

            return JsonResponse({'status': 'ok', 'mensagem': 'Sessão salva com sucesso!'})
        except Exception as e:
            return JsonResponse({'status': 'erro', 'mensagem': str(e)}, status=500)
    return JsonResponse({'status': 'erro', 'mensagem': 'Método não permitido.'}, status=405)


# --- Views de Cadastro e CRUD de Matérias ---

def cadastro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'dashboard/cadastro.html', {'form': form})

@login_required
def listar_materias(request):
    materias = Materia.objects.filter(usuario=request.user)
    return render(request, 'dashboard/listar_materias.html', {'materias': materias})

@login_required
def cadastrar_materia(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        if nome:
            Materia.objects.create(usuario=request.user, nome=nome)
            return redirect('listar_materias')
    return render(request, 'dashboard/form_materia.html', {'acao': 'Cadastrar'})

@login_required
def editar_materia(request, id):
    materia = get_object_or_404(Materia, id=id, usuario=request.user)
    if request.method == 'POST':
        nome = request.POST.get('nome')
        if nome:
            materia.nome = nome
            materia.save()
            return redirect('listar_materias')
    return render(request, 'dashboard/form_materia.html', {'acao': 'Editar', 'materia': materia})

@login_required
def deletar_materia(request, id):
    materia = get_object_or_404(Materia, id=id, usuario=request.user)
    if request.method == 'POST':
        materia.delete()
        return redirect('listar_materias')
    return render(request, 'dashboard/confirmar_delete.html', {'materia': materia})