import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Edital, Bloco, Materia, Topico, Progresso, Ciclo

# --- Funções de Análise (Parser) ---
def parse_e_salva_edital(usuario, nome_edital, conteudo_bruto):
    """
    Analisa o texto bruto e cria os objetos Edital, Bloco, Materia e Topico no banco.
    Esta é a versão aprimorada da função de análise.
    """
    edital = Edital.objects.create(usuario=usuario, nome=nome_edital, conteudo_bruto=conteudo_bruto)
    
    linhas = [linha.strip() for linha in conteudo_bruto.split('\n') if linha.strip()]
    
    bloco_atual = None
    materia_atual = None
    bloco_ordem = 0
    materia_ordem = 0
    topico_ordem = 0

    for linha in linhas:
        # Verifica se é um bloco
        if linha.upper().startswith('BLOCO'):
            bloco_ordem += 1
            bloco_atual = Bloco.objects.create(edital=edital, nome=linha, ordem=bloco_ordem)
            materia_ordem = 0 # Reseta a ordem da matéria
            continue
        
        # Heurística para matéria (Toda em maiúscula e termina com : ou é longa)
        if bloco_atual and linha == linha.upper() and len(linha) > 5:
            materia_ordem += 1
            materia_atual = Materia.objects.create(bloco=bloco_atual, nome=linha.replace(':', ''), ordem=materia_ordem)
            topico_ordem = 0 # Reseta a ordem do tópico
            continue
            
        # O resto é considerado tópico
        if materia_atual:
            topico_ordem += 1
            Topico.objects.create(materia=materia_atual, descricao=linha, ordem=topico_ordem)

    return edital

# --- Views de Página ---

@login_required
def edital_list_view(request):
    """Mostra a lista de editais do usuário logado."""
    editais = Edital.objects.filter(usuario=request.user).order_by('-criado_em')
    return render(request, 'edital/edital_list.html', {'editais': editais})

@login_required
def edital_detail_view(request, edital_id):
    """Mostra a view detalhada de um edital específico."""
    edital = get_object_or_404(Edital, id=edital_id, usuario=request.user)
    
    # Obter ciclo e progresso para passar ao template
    ciclo, _ = Ciclo.objects.get_or_create(edital=edital, usuario=request.user)
    materias_do_ciclo = ciclo.materias.values_list('id', flat=True)
    
    # Mapear o progresso para acesso rápido no template
    progressos = Progresso.objects.filter(usuario=request.user, topico__materia__bloco__edital=edital)
    progresso_map = {p.topico.id: p for p in progressos}

    context = {
        'edital': edital,
        'materias_do_ciclo': list(materias_do_ciclo),
        'progresso_map': progresso_map
    }
    return render(request, 'edital/edital_detail.html', context)


# --- API Endpoints ---

@login_required
@require_POST
def criar_edital_api(request):
    """API para criar um novo edital a partir do conteúdo colado."""
    data = json.loads(request.body)
    nome_edital = data.get('nome')
    conteudo_bruto = data.get('conteudo')

    if not nome_edital or not conteudo_bruto:
        return JsonResponse({'status': 'error', 'message': 'Nome e conteúdo são obrigatórios.'}, status=400)
    
    try:
        parse_e_salva_edital(request.user, nome_edital, conteudo_bruto)
        return JsonResponse({'status': 'success', 'message': 'Edital criado com sucesso!'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
@require_POST
def atualizar_progresso_api(request):
    """API para atualizar o status de um checkbox de um tópico."""
    data = json.loads(request.body)
    topico_id = data.get('topicId')
    tipo_progresso = data.get('type') # 'teoria', 'revisao1', etc.
    status = data.get('status')
    
    try:
        topico = Topico.objects.get(id=topico_id)
        progresso, _ = Progresso.objects.get_or_create(usuario=request.user, topico=topico)
        
        # Atualiza o campo correspondente
        setattr(progresso, tipo_progresso, status)
        progresso.save()
        
        return JsonResponse({'status': 'success'})
    except Topico.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Tópico não encontrado.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
@require_POST
def salvar_ciclo_api(request, edital_id):
    """API para salvar o ciclo de estudos de um edital."""
    data = json.loads(request.body)
    materia_ids = data.get('materia_ids', [])
    
    edital = get_object_or_404(Edital, id=edital_id, usuario=request.user)
    ciclo, _ = Ciclo.objects.get_or_create(edital=edital, usuario=request.user)
    
    # Limpa as matérias antigas e adiciona as novas
    ciclo.materias.set(materia_ids)
    
    return JsonResponse({'status': 'success', 'message': 'Ciclo salvo com sucesso!'})
