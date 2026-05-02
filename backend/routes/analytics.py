# backend/routes/analytics.py
import os
import csv
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Politico, AnaliseCategoria
from analytics import (
    analise_benford,
    analise_concentracao,
    pct_valores_redondos,
    calcular_zscore,
    calcular_risk_score,
    analisar_deputado_completo,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])

# CSV de despesas (mesmo usado no atualizar.py)
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "dados", "despesas_2023_2026.csv")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def obter_transacoes_csv(nome: str, ano: int) -> List[dict]:
    """Carrega transações do CSV local (fallback)."""
    if not os.path.exists(CSV_PATH):
        return []
    transacoes = []
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            try:
                if int(row.get("numAno", 0)) != ano:
                    continue
                if row.get("txNomeParlamentar", "").upper() != nome.upper():
                    continue
                transacoes.append({
                    "valor": float(row.get("vlrLiquido", 0)),
                    "fornecedor": row.get("txtCNPJCPF", ""),
                    "categoria": row.get("txtDescricao", ""),
                    "data": row.get("datEmissao", ""),
                })
            except (ValueError, KeyError):
                continue
    return transacoes


@router.get("/politico/{politico_id}")
def get_analytics_politico(
    politico_id: int,
    ano: int = Query(2025),
    db: Session = Depends(get_db),
):
    """
    Retorna a análise completa de um político:
    - Lei de Benford
    - HHI (concentração de fornecedores)
    - Valores redondos
    - Z-score vs partido e estado
    - Risk Score
    """
    politico = db.query(Politico).filter(Politico.id == politico_id).first()
    if not politico:
        raise HTTPException(status_code=404, detail="Político não encontrado")

    # Obtém transações do CSV
    transacoes = obter_transacoes_csv(politico.nome, ano)

    if not transacoes:
        # Retorna dados já salvos no banco (se existirem)
        if politico.risk_score is not None:
            return {
                "politico_id": politico_id,
                "nome": politico.nome,
                "gasto_total": politico.gasto_total,
                "n_transacoes": 0,
                "benford": {
                    "chi2": politico.benford_chi2,
                    "significativo": politico.benford_significativo,
                },
                "hhi": {
                    "hhi": politico.hhi,
                    "nivel": politico.hhi_nivel,
                    "top1_pct": politico.top1_pct,
                },
                "valores_redondos": {"percentual": politico.pct_valores_redondos},
                "z_scores": {
                    "partido": politico.zscore_partido,
                    "estado": politico.zscore_estado,
                },
                "risk_score": {
                    "score": politico.risk_score,
                    "nivel": politico.risk_nivel,
                    "red_flags": politico.red_flags,
                    "n_red_flags": politico.n_red_flags,
                },
                "mensagem": "Dados do banco (sem CSV disponível para este ano)",
            }
        raise HTTPException(
            status_code=404,
            detail="Sem dados de transações para este político/ano",
        )

    # Métricas de grupo (partido e estado)
    gastos_partido = [
        p.gasto_total
        for p in db.query(Politico).filter(
            Politico.partido == politico.partido,
            Politico.id != politico_id,
        ).all()
        if p.gasto_total
    ]
    gastos_estado = [
        p.gasto_total
        for p in db.query(Politico).filter(
            Politico.uf == politico.uf,
            Politico.id != politico_id,
        ).all()
        if p.gasto_total
    ]

    # Análise completa
    analise = analisar_deputado_completo(
        transacoes=transacoes,
        gastos_partido=gastos_partido,
        gastos_estado=gastos_estado,
        nome=politico.nome,
    )

    # Persiste no banco para consultas futuras
    politico.benford_chi2 = analise["benford"].get("chi2")
    politico.benford_significativo = analise["benford"].get("significativo", False)
    politico.hhi = analise["hhi"].get("hhi")
    politico.hhi_nivel = analise["hhi"].get("nivel")
    politico.pct_valores_redondos = analise["valores_redondos"].get("percentual")
    politico.top1_pct = analise["hhi"].get("top1_pct")
    politico.zscore_partido = analise["z_scores"]["partido"]
    politico.zscore_estado = analise["z_scores"]["estado"]
    politico.risk_score = analise["risk_score"]["score"]
    politico.risk_nivel = analise["risk_score"]["nivel"]
    politico.red_flags = analise["risk_score"]["red_flags"]
    politico.n_red_flags = analise["risk_score"]["n_red_flags"]
    politico.analytics_atualizado = datetime.now()
    db.commit()

    return analise


@router.get("/ranking/risk")
def ranking_risk_score(
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """Ranking de políticos por risk score (maior risco primeiro)."""
    politicos = (
        db.query(Politico)
        .filter(Politico.risk_score.isnot(None))
        .order_by(Politico.risk_score.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": p.id,
            "nome": p.nome,
            "partido": p.partido,
            "uf": p.uf,
            "gasto_total": p.gasto_total,
            "risk_score": p.risk_score,
            "risk_nivel": p.risk_nivel,
            "red_flags": p.red_flags,
            "n_red_flags": p.n_red_flags,
        }
        for p in politicos
    ]