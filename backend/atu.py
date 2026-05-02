# backend/atualizar_analytics.py
"""
Atualiza SOMENTE presenças e analytics (Benford, HHI, Risk Score).
Não altera gastos nem proposições já existentes no banco.
Usa o CSV de despesas como fonte.
"""
import os, csv, re, httpx
from datetime import datetime
from collections import defaultdict

from database import SessionLocal
from models import Politico
from analytics import analisar_deputado_completo

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "dados", "despesas_2023_2026.csv")
PRESENCA_URL = "https://www.camara.leg.br/deputados/{id}/presenca-plenario/2025"
ANO = 2025

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def carregar_csv(caminho):
    """Carrega o CSV inteiro em memória."""
    if not os.path.exists(caminho):
        return []
    with open(caminho, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter=";"))


def obter_transacoes(rows, nome):
    """Filtra transações de um deputado no CSV."""
    return [
        {
            "valor": float(r["vlrLiquido"]),
            "fornecedor": r["txtCNPJCPF"],
            "categoria": r["txtDescricao"],
            "data": r["datEmissao"],
        }
        for r in rows
        if r.get("txNomeParlamentar", "").upper() == nome.upper()
        and int(r.get("numAno", 0)) == ANO
        and float(r.get("vlrLiquido", 0)) > 0
    ]


def obter_presenca(deputado_id):
    """Busca presença oficial na página da Câmara."""
    try:
        url = PRESENCA_URL.format(id=deputado_id)
        resp = httpx.get(url, timeout=15, headers=HEADERS, follow_redirects=True)
        if resp.status_code == 200:
            match = re.search(
                r'Total de dias com presença.*?<td[^>]*>\s*(\d{1,3},\d{2})%\s*</td>',
                resp.text, re.DOTALL | re.IGNORECASE
            )
            if match:
                return float(match.group(1).replace(',', '.'))
            # Fallback
            todos = re.findall(r'<td[^>]*>\s*(\d{1,3},\d{2})%\s*</td>', resp.text)
            if len(todos) >= 2:
                return float(todos[1].replace(',', '.'))
    except Exception:
        pass
    return 0.0


def main():
    print("=" * 60)
    print("ATUALIZAÇÃO DE PRESENÇAS E ANALYTICS")
    print("=" * 60)

    # Carrega CSV
    print("\n📂 Carregando CSV de despesas...")
    csv_rows = carregar_csv(CSV_PATH)
    print(f"   {len(csv_rows):,} registros carregados.")

    db = SessionLocal()
    try:
        politicos = db.query(Politico).all()
        total = len(politicos)
        print(f"\n👥 {total} políticos no banco.\n")

        # Agrupamentos para Z-scores
        gastos_partido = defaultdict(list)
        gastos_estado = defaultdict(list)
        for p in politicos:
            if p.gasto_total:
                gastos_partido[p.partido].append(p.gasto_total)
                gastos_estado[p.uf].append(p.gasto_total)

        atualizados = 0
        for i, p in enumerate(politicos, 1):
            nome = p.nome
            dep_id = p.id

            # 1. Busca presença oficial
            if i == 1 or i % 50 == 0:
                print(f"  📡 Buscando presenças... ({i}/{total})", end="\r")
            presenca = obter_presenca(dep_id)

            # 2. Obtém transações do CSV
            transacoes = obter_transacoes(csv_rows, nome.upper())

            # 3. Calcula analytics
            if transacoes:
                analise = analisar_deputado_completo(
                    transacoes=transacoes,
                    gastos_partido=gastos_partido.get(p.partido, []),
                    gastos_estado=gastos_estado.get(p.uf, []),
                    nome=nome,
                )

                p.presenca_percentual = presenca
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
            else:
                # Sem transações, só atualiza presença
                p.presenca_percentual = presenca

            # Commit a cada 10
            if i % 10 == 0:
                db.commit()
                print(f"  💾 {i}/{total} salvos...", end="\r")

        # Commit final
        db.commit()
        print(f"\n\n✅ {atualizados} políticos atualizados com analytics!")
        print(f"   Verifique com: SELECT COUNT(*) FROM politicos WHERE risk_score IS NOT NULL;")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Erro: {type(e).__name__}: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()