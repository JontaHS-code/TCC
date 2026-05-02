# backend/corrigir_analytics.py
"""
Script de correção: preenche os campos de analytics para TODOS os políticos
usando os dados de gastos que já estão no banco e o CSV de despesas.
"""
import os, csv
from datetime import datetime
from collections import defaultdict

from database import SessionLocal
from models import Politico
from analytics import analisar_deputado_completo

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "dados", "despesas_2023_2026.csv")
ANO = 2025

def obter_transacoes_csv(nome: str, ano: int):
    """Carrega transações do CSV de fallback."""
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


def main():
    db = SessionLocal()
    try:
        politicos = db.query(Politico).all()
        total = len(politicos)
        print(f"Encontrados {total} políticos no banco.\n")

        # Agrupamentos para Z-scores
        gastos_por_partido = defaultdict(list)
        gastos_por_estado = defaultdict(list)
        for p in politicos:
            if p.gasto_total:
                gastos_por_partido[p.partido].append(p.gasto_total)
                gastos_por_estado[p.uf].append(p.gasto_total)

        atualizados = 0
        for i, p in enumerate(politicos, 1):
            nome = p.nome
            transacoes = obter_transacoes_csv(nome, ANO)

            if transacoes:
                analise = analisar_deputado_completo(
                    transacoes=transacoes,
                    gastos_partido=gastos_por_partido.get(p.partido, []),
                    gastos_estado=gastos_por_estado.get(p.uf, []),
                    nome=nome,
                )

                p.benford_chi2 = analise["benford"].get("chi2")
                p.benford_significativo = analise["benford"].get("significativo", False)
                p.hhi = analise["hhi"].get("hhi")
                p.hhi_nivel = analise["hhi"].get("nivel")
                p.pct_valores_redondos = analise["valores_redondos"].get("percentual")
                p.top1_pct = analise["hhi"].get("top1_pct")
                p.zscore_partido = analise["z_scores"].get("partido")
                p.zscore_estado = analise["z_scores"].get("estado")
                p.risk_score = analise["risk_score"].get("score")
                p.risk_nivel = analise["risk_score"].get("nivel")
                p.red_flags = analise["risk_score"].get("red_flags", [])
                p.n_red_flags = analise["risk_score"].get("n_red_flags", 0)
                p.analytics_atualizado = datetime.now()

                atualizados += 1
                print(f"[{i}/{total}] ✅ {nome}: Risk={p.risk_score}, HHI={p.hhi}, Benford={p.benford_chi2}")

            db.commit()  # Commit a cada político

        print(f"\n✅ {atualizados} políticos atualizados com analytics!")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Erro: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()