# backend/routes/politicos_detalhes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from crud import buscar_gastos_deputado, buscar_proposicoes_deputado
from collections import defaultdict

router = APIRouter(prefix="/politicos", tags=["Políticos"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{politico_id}/gastos")
def get_gastos_detalhados(politico_id: int):
    """
    Retorna TODOS os gastos agrupados por categoria (tipo de despesa).
    Exemplo: 'Combustíveis', 'Divulgação', 'Passagens', etc.
    """
    gastos = buscar_gastos_deputado(politico_id, ano=2025)
    if not gastos:
        raise HTTPException(status_code=404, detail="Gastos não encontrados")
    
    # Agrupamento por tipoDespesa
    categorias = defaultdict(float)
    for g in gastos:
        categoria = g.get("tipoDespesa", "Outros")
        valor = g.get("valorLiquido", 0)
        categorias[categoria] += valor
    
    # Ordena do maior para o menor e retorna TODAS as categorias
    resultado = [
        {"categoria": cat, "valor": val}
        for cat, val in sorted(categorias.items(), key=lambda x: x[1], reverse=True)
    ]
    return resultado  # Retorna TODAS as categorias, sem limite


@router.get("/{politico_id}/proposicoes")
def get_proposicoes_detalhadas(politico_id: int):
    """
    Retorna TODAS as proposições (projetos de lei, PECs, etc.) do deputado,
    ordenadas da mais recente para a mais antiga.
    """
    proposicoes = buscar_proposicoes_deputado(politico_id)
    if not proposicoes:
        raise HTTPException(status_code=404, detail="Nenhuma proposição encontrada")
    
    # Ordena por data de apresentação (mais recentes primeiro)
    # Se não tiver data, usa o id como fallback (ids maiores = mais recentes)
    props_ordenadas = sorted(
        proposicoes,
        key=lambda x: (
            x.get("dataApresentacao") or "",  # ordena por data (string vazia se não existir)
            x.get("id", 0)  # fallback pelo id
        ),
        reverse=True
    )
    
    resultado = []
    for p in props_ordenadas:
        ementa = p.get("ementa", "Sem ementa")
        # Remove limite de tamanho da ementa (exibe completa)
        resultado.append({
            "titulo": ementa,
            "data": p.get("dataApresentacao", "Data não informada"),
            "tipo": p.get("siglaTipo", "Proposição")
        })
    
    return resultado  # Retorna TODAS as proposições, sem limite