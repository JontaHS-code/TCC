# backend/atualizar.py - Versão final CORRIGIDA para salvar no banco
import os, csv, re, httpx, asyncio
from datetime import datetime
from typing import Dict, List
from collections import defaultdict

from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Politico
from analytics import analisar_deputado_completo

# ---------------------------------------------------------------
# CONFIGURAÇÕES
# ---------------------------------------------------------------
CAMARA_API_URL = "https://dadosabertos.camara.leg.br/api/v2"
ANO_PADRAO = 2025
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "dados", "despesas_2023_2026.csv")
PRESENCA_URL = "https://www.camara.leg.br/deputados/{id}/presenca-plenario/{ano}"
DELAY = 0.3
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}

presenca_cache: Dict[str, float] = {}

# ---------------------------------------------------------------
# 1. REQUISIÇÕES
# ---------------------------------------------------------------
async def fetch_json(client, url, params=None):
    try:
        r = await client.get(url, params=params, timeout=60)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"  ❌ Erro ao acessar {url}: {type(e).__name__}")
        return {}

async def deputados(client):
    d = await fetch_json(client, f"{CAMARA_API_URL}/deputados", {"itens": 600})
    return d.get("dados", [])

# ---------------------------------------------------------------
# 2. DESPESAS
# ---------------------------------------------------------------
async def despesas_api(client, dep_id, ano):
    d = await fetch_json(client, f"{CAMARA_API_URL}/deputados/{dep_id}/despesas",
                         {"ano": ano, "itens": 1000})
    return [
        {"valor": float(x.get("valorLiquido", 0)),
         "fornecedor": x.get("cnpjCpfFornecedor", ""),
         "categoria": x.get("tipoDespesa", ""),
         "data": x.get("dataEmissao", "")}
        for x in d.get("dados", [])
        if float(x.get("valorLiquido", 0)) > 0
    ]

def despesas_csv(nome, ano):
    if not os.path.exists(CSV_PATH):
        return []
    with open(CSV_PATH, encoding="utf-8") as f:
        return [
            {"valor": float(r["vlrLiquido"]),
             "fornecedor": r["txtCNPJCPF"],
             "categoria": r["txtDescricao"],
             "data": r["datEmissao"]}
            for r in csv.DictReader(f, delimiter=";")
            if int(r.get("numAno", 0)) == ano
            and r.get("txNomeParlamentar", "").upper() == nome.upper()
        ]

async def transacoes(client, dep_id, nome, ano):
    t = await despesas_api(client, dep_id, ano)
    return t or despesas_csv(nome, ano)

# ---------------------------------------------------------------
# 3. PROPOSIÇÕES (todas as páginas)
# ---------------------------------------------------------------
async def total_proposicoes(client, dep_id):
    total, pagina = 0, 1
    while True:
        d = await fetch_json(
            client, f"{CAMARA_API_URL}/proposicoes",
            {"idDeputadoAutor": dep_id, "itens": 100, "pagina": pagina, "ordem": "DESC"}
        )
        itens = d.get("dados", [])
        total += len(itens)
        if len(itens) < 100:
            break
        pagina += 1
        await asyncio.sleep(0.15)
    return total

# ---------------------------------------------------------------
# 4. PRESENÇA OFICIAL
# ---------------------------------------------------------------
def carregar_presencas_plenario(ano: int, deputados_dict: Dict[str, str]) -> Dict[str, float]:
    print(f"📡 Obtendo presenças oficiais de Plenário para {ano}...")
    resultado = {}
    total = len(deputados_dict)
    sucessos = 0

    with httpx.Client(timeout=15, limits=httpx.Limits(max_connections=5)) as client:
        for i, (id_dep, nome) in enumerate(deputados_dict.items(), 1):
            url = PRESENCA_URL.format(id=id_dep, ano=ano)
            try:
                resp = client.get(url, follow_redirects=True, headers=HEADERS)
                if resp.status_code == 200:
                    texto = resp.text

                    # Método 1: Valor APÓS "Total de dias com presença"
                    match = re.search(
                        r'Total de dias com presença.*?<td[^>]*>\s*(\d{1,3},\d{2})%\s*</td>',
                        texto, re.DOTALL | re.IGNORECASE
                    )
                    if match:
                        pct = float(match.group(1).replace(',', '.'))
                        resultado[nome.upper()] = pct
                        sucessos += 1
                    else:
                        # Método 2: Fallback – segundo percentual da tabela
                        todos = re.findall(r'<td[^>]*>\s*(\d{1,3},\d{2})%\s*</td>', texto)
                        if len(todos) >= 2:
                            pct = float(todos[1].replace(',', '.'))
                            resultado[nome.upper()] = pct
                            sucessos += 1
                        else:
                            resultado[nome.upper()] = 0.0
                else:
                    resultado[nome.upper()] = 0.0
            except Exception:
                resultado[nome.upper()] = 0.0

            if i % 50 == 0 or i == total:
                print(f"  {i}/{total} processados ({sucessos} com sucesso)...", end="\r")

    print(f"\n  ✓ {sucessos} deputados com presença oficial carregada")
    return resultado

# ---------------------------------------------------------------
# 5. IREP
# ---------------------------------------------------------------
def irep(gasto, props, pres, mg, mp):
    sp = (props / mp * 100) if mp else 0
    sg = max(0, 100 - (gasto / mg * 100)) if mg else 100
    return round(sp * 0.4 + sg * 0.3 + pres * 0.3, 2)

# ---------------------------------------------------------------
# 6. ATUALIZAÇÃO PRINCIPAL
# ---------------------------------------------------------------
async def atualizar_politicos(ano=ANO_PADRAO):
    print(f"\n{'='*60}")
    print(f"ATUALIZAÇÃO COMPLETA - {ano}")
    print(f"{'='*60}\n")

    async with httpx.AsyncClient(headers=HEADERS, timeout=60) as client:
        print("Obtendo lista de deputados...")
        deps = await deputados(client)
        total = len(deps)
        print(f"Encontrados {total} deputados.\n")

        if total == 0:
            print("❌ Nenhum deputado encontrado. Abortando.")
            return

        dep_dict = {str(dep["id"]): dep["nome"] for dep in deps}

        global presenca_cache
        presenca_cache = carregar_presencas_plenario(ano, dep_dict)
        print()

        max_gasto, max_props = 0, 0
        dados_parciais = []

        for i, dep in enumerate(deps, 1):
            nome = dep["nome"]
            dep_id = dep["id"]
            partido = dep.get("siglaPartido", "")
            uf = dep.get("siglaUf", "")

            pres = presenca_cache.get(nome.upper(), 0.0)

            print(f"[{i}/{total}] {nome} ({partido}-{uf})", end="   ")

            t = await transacoes(client, dep_id, nome, ano)
            gasto = sum(x["valor"] for x in t)
            props = await total_proposicoes(client, dep_id)

            dados_parciais.append({
                "dep": dep,
                "transacoes": t,
                "gasto_total": gasto,
                "num_props": props,
                "presenca": pres,
            })

            max_gasto = max(max_gasto, gasto)
            max_props = max(max_props, props)

            print(f"💰 R$ {gasto:,.2f} | 📋 {props} props | ✓ {pres:.1f}% presença")

            if i % 10 == 0:
                await asyncio.sleep(DELAY)

        print(f"\n📊 Máximo gasto: R$ {max_gasto:,.2f} | Máximo props: {max_props}\n")

        por_partido = defaultdict(list)
        por_estado = defaultdict(list)
        for d in dados_parciais:
            por_partido[d["dep"]["siglaPartido"]].append(d["gasto_total"])
            por_estado[d["dep"]["siglaUf"]].append(d["gasto_total"])

        print("Calculando métricas e salvando no banco...\n")
        
        # ---- SALVAMENTO NO BANCO (CORRIGIDO) ----
        db = SessionLocal()
        try:
            for i, dados in enumerate(dados_parciais, 1):
                dep = dados["dep"]
                nome = dep["nome"]
                t = dados["transacoes"]
                gasto = dados["gasto_total"]
                props = dados["num_props"]
                pres = dados["presenca"]

                ir = irep(gasto, props, pres, max_gasto, max_props)

                # Calcula analytics
                if t:
                    a = analisar_deputado_completo(
                        t,
                        por_partido.get(dep["siglaPartido"], []),
                        por_estado.get(dep["siglaUf"], []),
                        nome,
                    )
                else:
                    a = {
                        "gasto_total": 0, "n_transacoes": 0,
                        "benford": {}, "hhi": {}, "valores_redondos": {},
                        "z_scores": {"partido": None, "estado": None},
                        "risk_score": {
                            "score": None, "nivel": None,
                            "red_flags": [], "n_red_flags": 0,
                        },
                    }

                # Busca ou cria o político
                p = db.query(Politico).filter(Politico.nome == nome).first()
                if not p:
                    p = Politico(
                        nome=nome,
                        partido=dep.get("siglaPartido", ""),
                        uf=dep.get("siglaUf", ""),
                        cargo="deputado",
                        foto_url=dep.get("urlFoto", ""),
                    )
                    db.add(p)
                    db.flush()  # Garante o ID

                # Atualiza campos básicos
                p.gasto_total = gasto
                p.num_proposicoes = props
                p.presenca_percentual = pres
                p.irep_score = ir
                p.ultima_atualizacao = datetime.now()

                # Atualiza campos de analytics
                p.benford_chi2 = a["benford"].get("chi2")
                p.benford_significativo = a["benford"].get("significativo", False)
                p.hhi = a["hhi"].get("hhi")
                p.hhi_nivel = a["hhi"].get("nivel")
                p.pct_valores_redondos = a["valores_redondos"].get("percentual")
                p.top1_pct = a["hhi"].get("top1_pct")
                p.zscore_partido = a["z_scores"].get("partido")
                p.zscore_estado = a["z_scores"].get("estado")
                p.risk_score = a["risk_score"].get("score")
                p.risk_nivel = a["risk_score"].get("nivel")
                p.red_flags = a["risk_score"].get("red_flags", [])
                p.n_red_flags = a["risk_score"].get("n_red_flags", 0)
                p.analytics_atualizado = datetime.now()

                # COMMIT a cada deputado
                db.commit()
                
                if i % 10 == 0 or i == len(dados_parciais):
                    print(f"  💾 {i}/{len(dados_parciais)} salvos no banco...", end="\r")

            print(f"\n\n✅ Atualização concluída! {len(dados_parciais)} deputados processados e salvos.")
            
        except Exception as e:
            db.rollback()
            print(f"\n❌ Erro ao salvar no banco: {type(e).__name__}: {e}")
            raise
        finally:
            db.close()


if __name__ == "__main__":
    asyncio.run(atualizar_politicos(ANO_PADRAO))