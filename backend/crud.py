from sqlalchemy.orm import Session
from models import Politico, DespesaAgregada, Proposicao
from datetime import datetime
import requests
import re   # <-- ADICIONE ESTA LINHA
from DadosAbertosBrasil import camara

def buscar_deputados():
    """Busca lista de deputados com informações atualizadas, incluindo a URL da foto."""
    url = "https://dadosabertos.camara.leg.br/api/v2/deputados"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json().get('dados', [])
    except Exception as e:
        print(f"Erro ao buscar deputados: {e}")
        return []

def buscar_gastos_deputado(id_deputado, ano=2025):
    """Busca gastos de um deputado (CEAP)."""
    url = f"https://dadosabertos.camara.leg.br/api/v2/deputados/{id_deputado}/despesas"
    params = {'ano': ano, 'itens': 100}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json().get('dados', [])
    except Exception as e:
        print(f"Erro ao buscar gastos do deputado {id_deputado}: {e}")
        return []

def buscar_proposicoes_deputado(id_deputado):
    """Busca todas as proposições de um deputado usando o pacote DadosAbertosBrasil.
    Em caso de erro, retorna lista vazia para não interromper a atualização."""
    todas_proposicoes = []
    pagina = 1
    itens_por_pagina = 100
    try:
        while True:
            proposicoes_df = camara.lista_proposicoes(
                autor_cod=id_deputado,
                pagina=pagina,
                itens=itens_por_pagina,
                formato='pandas',
                asc=True,
                ordenar_por='id'
            )
            if proposicoes_df.empty:
                break
            todas_proposicoes.extend(proposicoes_df.to_dict('records'))
            if len(proposicoes_df) < itens_por_pagina:
                break
            pagina += 1
    except Exception as e:
        print(f"    ERRO ao buscar proposições do deputado {id_deputado}: {e}. Retornando lista vazia.")
        return []
    return todas_proposicoes

def calcular_irep(gasto_total, num_proposicoes, presenca_percentual):
    """Calcula o Índice de Relevância e Eficiência Política (IREP)."""
    max_gasto = 500000  # R$ 500k como referência
    g_norm = max(0, min(1, 1 - (gasto_total / max_gasto))) if max_gasto > 0 else 0
    p_norm = min(1, num_proposicoes / 200)
    a_norm = presenca_percentual / 100 if presenca_percentual <= 100 else 0
    irep = (p_norm * 0.4) + (g_norm * 0.3) + (a_norm * 0.3)
    return round(irep * 100, 2)

def buscar_foto_politico(dep_id, nome_deputado):
    """
    Busca a URL da foto do político utilizando múltiplas estratégias.
    Retorna a URL da foto ou None se não encontrar.
    """
    # 1. Tentar pegar da API da Câmara (já feita na função atualizar_cache)
    # 2. Tentar acessar o padrão conhecido de URL de foto da Câmara
    url_camara_padrao = f"https://www.camara.leg.br/internet/deputado/bandep/{dep_id}.jpg"
    try:
        response = requests.head(url_camara_padrao, timeout=5)
        if response.status_code == 200:
            return url_camara_padrao
    except:
        pass
    
    # 3. Tentar buscar na Wikipedia
    try:
        nome_busca = re.sub(r'[^\w\s]', '', nome_deputado).replace(' ', '_')
        url_wikipedia = f"https://pt.wikipedia.org/api/rest_v1/page/summary/{nome_busca}"
        response = requests.get(url_wikipedia, timeout=5)
        data = response.json()
        if 'thumbnail' in data and 'source' in data['thumbnail']:
            return data['thumbnail']['source']
    except:
        pass
    
    return None

def atualizar_cache(db: Session):
    """Atualiza o cache local (banco) com dados da API."""
    print("Atualizando cache de políticos...")
    deputados_data = buscar_deputados()
    if not deputados_data:
        print("ERRO: Nenhum deputado retornado pela API.")
        return

    for i, dep in enumerate(deputados_data, 1):
        try:
            nome = dep.get('nome', f"Deputado {dep.get('id', 'desconhecido')}")
            print(f"Processando ({i}/{len(deputados_data)}): {nome} (ID {dep['id']})")
            
            # Busca a foto com o novo método
            foto_url = buscar_foto_politico(dep['id'], nome)
            if not foto_url:
                foto_url = dep.get('ultimoStatus', {}).get('urlFoto', '')
            
            gastos = buscar_gastos_deputado(dep['id'])
            gasto_total = sum(g.get('valorLiquido', 0) for g in gastos)
            proposicoes = buscar_proposicoes_deputado(dep['id'])
            num_proposicoes = len(proposicoes)
            presenca = dep.get('ultimoStatus', {}).get('presenca', 85)
            irep = calcular_irep(gasto_total, num_proposicoes, presenca)
            
            politico = db.query(Politico).filter(Politico.id == dep['id']).first()
            if not politico:
                politico = Politico(
                    id=dep['id'],
                    nome=nome,
                    partido=dep.get('siglaPartido', 'Sem partido'),
                    uf=dep.get('siglaUf', 'XX'),
                    cargo='deputado',
                    ultima_atualizacao=datetime.now()
                )
            politico.gasto_total = gasto_total
            politico.num_proposicoes = num_proposicoes
            politico.presenca_percentual = presenca
            politico.irep_score = irep
            politico.foto_url = foto_url
            politico.ultima_atualizacao = datetime.now()
            
            db.merge(politico)
            db.commit()
            print(f"    -> Salvo: IREP={irep}, foto={'sim' if foto_url else 'não'}, props={num_proposicoes}")
        except Exception as e:
            print(f"    ERRO ao processar deputado {dep.get('id', '?')}: {e}")
            db.rollback()
            continue
    print("Cache atualizado com sucesso!")