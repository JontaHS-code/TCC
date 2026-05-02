# backend/atualizar_apenas_analytics.py
"""
Atualiza SOMENTE os campos de analytics (Benford, HHI, Risk Score, etc.)
Usa o CSV de despesas como fonte.
"""
import os, csv
from datetime import datetime
from collections import defaultdict

from database import SessionLocal
from models import Politico
from analytics import analisar_deputado_completo

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "dados", "despesas_2023_2026.csv")
ANO = 2025


def carregar_csv():
    if not os.path.exists(CSV_PATH):
        print(f"❌ CSV não encontrado: {CSV_PATH}")
        return []
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        primeira_linha = f.readline().strip()
        # Detecta o delimitador correto
        if ";" in primeira_linha:
            delimitador = ";"
        else:
            delimitador = ","
        f.seek(0)
        return list(csv.DictReader(f, delimiter=delimitador))


def obter_transacoes(rows, nome):
    return [
        {
            "valor": float(r.get("vlrLiquido", 0)),
            "fornecedor": r.get("txtCNPJCPF", ""),
            "categoria": r.get("txtDescricao", ""),
            "data": r.get("datEmissao", ""),
        }
        for r in rows
        if r.get("txNomeParlamentar", "").upper().strip() == nome.upper().strip()
        and int(r.get("numAno", 0)) == ANO
        and float(r.get("vlrLiquido", 0)) > 0
    ]


def main():
    print("=" * 60)
    print("ATUALIZAÇÃO DE ANALYTICS (Benford, HHI, Risk Score)")
    print("=" * 60)

    print("\n📂 Carregando CSV...")
    csv_rows = carregar_csv()
    if not csv_rows:
        return
    print(f"   {len(csv_rows):,} registros.")

    db = SessionLocal()
    try:
        politicos = db.query(Politico).all()
        total = len(politicos)

        gastos_partido = defaultdict(list)
        gastos_estado = defaultdict(list)
        for p in politicos:
            if p.gasto_total:
                gastos_partido[p.partido].append(p.gasto_total)
                gastos_estado[p.uf].append(p.gasto_total)

        atualizados = 0
        sem_transacoes = 0

        for i, p in enumerate(politicos, 1):
            transacoes = obter_transacoes(csv_rows, p.nome)

            if transacoes:
                analise = analisar_deputado_completo(
                    transacoes=transacoes,
                    gastos_partido=gastos_partido.get(p.partido, []),
                    gastos_estado=gastos_estado.get(p.uf, []),
                    nome=p.nome,
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

                if atualizados <= 5:
                    print(f"  ✅ {p.nome}: Risk={p.risk_score}, HHI={p.hhi}")
            else:
                sem_transacoes += 1

            if i % 50 == 0:
                db.commit()
                print(f"  💾 Commit: {i}/{total} ({atualizados} c/ analytics)")

        db.commit()
        print(f"\n✅ Concluído!")
        print(f"   Com analytics: {atualizados}")
        print(f"   Sem transações: {sem_transacoes}")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Erro: {type(e).__name__}: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()