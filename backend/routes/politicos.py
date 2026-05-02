from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Politico
from typing import Optional

router = APIRouter(prefix="/politicos", tags=["Políticos"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def listar_politicos(
    db: Session = Depends(get_db),
    nome: Optional[str] = None,
    partido: Optional[str] = None,
    uf: Optional[str] = None,
    cargo: Optional[str] = None,
    gasto_min: Optional[float] = None,
    gasto_max: Optional[float] = None,
    props_min: Optional[int] = None,
    props_max: Optional[int] = None,
    presenca_min: Optional[float] = None,
    presenca_max: Optional[float] = None,
    min_irep: Optional[float] = None,
    max_irep: Optional[float] = None,
    ordenar_por: Optional[str] = "irep_score",
    ordem: Optional[str] = "desc",
    limit: Optional[int] = None   # <--- sem valor padrão, retorna todos quando ausente
):
    query = db.query(Politico)

    if nome:
        query = query.filter(Politico.nome.ilike(f"%{nome}%"))
    if partido:
        query = query.filter(Politico.partido == partido)
    if uf:
        query = query.filter(Politico.uf == uf)
    if cargo:
        query = query.filter(Politico.cargo == cargo)
    if gasto_min is not None:
        query = query.filter(Politico.gasto_total >= gasto_min)
    if gasto_max is not None:
        query = query.filter(Politico.gasto_total <= gasto_max)
    if props_min is not None:
        query = query.filter(Politico.num_proposicoes >= props_min)
    if props_max is not None:
        query = query.filter(Politico.num_proposicoes <= props_max)
    if presenca_min is not None:
        query = query.filter(Politico.presenca_percentual >= presenca_min)
    if presenca_max is not None:
        query = query.filter(Politico.presenca_percentual <= presenca_max)
    if min_irep is not None:
        query = query.filter(Politico.irep_score >= min_irep)
    if max_irep is not None:
        query = query.filter(Politico.irep_score <= max_irep)

    colunas_validas = {
        "nome": Politico.nome,
        "partido": Politico.partido,
        "gasto_total": Politico.gasto_total,
        "num_proposicoes": Politico.num_proposicoes,
        "presenca_percentual": Politico.presenca_percentual,
        "irep_score": Politico.irep_score,
    }
    coluna = colunas_validas.get(ordenar_por, Politico.irep_score)
    if ordem == "asc":
        query = query.order_by(coluna.asc())
    else:
        query = query.order_by(coluna.desc())

    # Se limit for None ou 0, retorna todos
    if limit and limit > 0:
        politicos = query.limit(limit).all()
    else:
        politicos = query.all()

    # Serialização explícita – inclui os novos campos
    resultado = []
    for p in politicos:
        resultado.append({
            "id": p.id,
            "nome": p.nome,
            "partido": p.partido,
            "uf": p.uf,
            "cargo": p.cargo,
            "gasto_total": p.gasto_total,
            "num_proposicoes": p.num_proposicoes,
            "presenca_percentual": p.presenca_percentual,
            "irep_score": p.irep_score,
            "ultima_atualizacao": p.ultima_atualizacao.isoformat() if p.ultima_atualizacao else None,
            "foto_url": p.foto_url,
            "gasto_per_capita": p.gasto_per_capita,
            "ranking_estadual": p.ranking_estadual,
            "evolucao_gastos": p.evolucao_gastos,
            "palavras_chave": p.palavras_chave,
            "trocas_partido": p.trocas_partido,
        })
    return resultado

@router.get("/partidos")
def listar_partidos(db: Session = Depends(get_db)):
    partidos = db.query(Politico.partido).distinct().order_by(Politico.partido).all()
    return [p[0] for p in partidos if p[0]]