import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Edital, Bloco, Materia, Topico, Progresso, Ciclo

# --- Funções de Análise (Parser) ---
def cria_edital_estruturado(usuario, nome_edital, data):
    """
    Cria os objetos Edital, Bloco, Materia e Topico a partir de um JSON estruturado.
    """
    edital = Edital.objects.create(usuario=usuario, nome=nome_edital, conteudo_bruto=json.dumps(data)) # Salva o JSON para referência

    blocos_data = data.get('blocos', [])
    for bloco_ordem, bloco_dict in enumerate(blocos_data, 1):
        # O nome do bloco será "BLOCO I", "BLOCO II", etc.
        bloco = Bloco.objects.create(edital=edital, nome=f"BLOCO {bloco_ordem}", ordem=bloco_ordem)

        materias_data = bloco_dict.get('materias', [])
        for materia_ordem, materia_dict in enumerate(materias_data, 1):
            nome_materia = materia_dict.get('nome')
            if not nome_materia: continue # Pula matérias sem nome

            materia = Materia.objects.create(bloco=bloco, nome=nome_materia, ordem=materia_ordem)

            topicos_data = materia_dict.get('topicos', [])
            for topico_ordem, descricao_topico in enumerate(topicos_data, 1):
                if not descricao_topico: continue # Pula tópicos vazios

                Topico.objects.create(materia=materia, descricao=descricao_topico, ordem=topico_ordem)

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
    """API para criar um novo edital a partir do formulário estruturado."""
    data = json.loads(request.body)
    nome_edital = data.get('nome_edital')
    blocos = data.get('blocos')

    if not nome_edital or not blocos:
        return JsonResponse({'status': 'error', 'message': 'Nome do edital e ao menos um bloco são obrigatórios.'}, status=400)

    try:
        # A função de parse antiga foi substituída pela nova
        cria_edital_estruturado(request.user, nome_edital, data)
        return JsonResponse({'status': 'success', 'message': 'Edital criado com sucesso!'})
    except Exception as e:
        # É uma boa prática logar o erro no servidor também
        # import logging
        # logging.error(f"Erro ao criar edital: {e}")
        return JsonResponse({'status': 'error', 'message': f'Ocorreu um erro interno: {e}'}, status=500)


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
