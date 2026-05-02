# backend/routes/gastos.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import httpx
import os
import json
import asyncio
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any

from database import SessionLocal
from models import Politico

router = APIRouter(prefix="/gastos", tags=["Gastos"])

# ---------- Dependência do banco ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- Cache diário (expira à meia-noite) ----------
cache: Dict[str, Any] = {}
CACHE_DATE: Dict[str, date] = {}

def is_cache_valid(key: str) -> bool:
    return key in cache and key in CACHE_DATE and CACHE_DATE[key] == date.today()

def save_cache(key: str, data: Any):
    cache[key] = data
    CACHE_DATE[key] = date.today()
    print(f"[CACHE] ✅ Dados salvos para '{key}' (válido até 23:59:59)")

def get_cache_or_none(key: str) -> Optional[Any]:
    if is_cache_valid(key):
        print(f"[CACHE] ✔️ Usando cache de {CACHE_DATE[key]} para '{key}'")
        return cache[key]
    print(f"[CACHE] ⚠️ Cache expirado/ausente para '{key}'. Buscando dados...")
    return None

# ---------- Carregar lista completa de órgãos do Executivo ----------
ORGAOS_EXECUTIVO: List[Dict[str, str]] = []
try:
    with open("orgaos_superiores.json", "r", encoding="utf-8") as f:
        todos_orgaos = json.load(f)
        ORGAOS_EXECUTIVO = [
            org for org in todos_orgaos
            if org['codigo'].startswith(('2','3'))
            and 'Legislativo' not in org['nome']
            and 'Judiciário' not in org['nome']
            and 'Judici' not in org['nome']
        ]
    print(f"[INIT] Carregados {len(ORGAOS_EXECUTIVO)} órgãos do Executivo.")
except FileNotFoundError:
    print("[INIT] Arquivo 'orgaos_superiores.json' não encontrado. Usando fallback.")
    ORGAOS_EXECUTIVO = []

# Fallback mínimo (caso arquivo não exista)
FALLBACK_ORGAOS = [
    {"codigo": "20000", "nome": "Presidência da República"},
    {"codigo": "25000", "nome": "Ministério da Fazenda"},
    {"codigo": "26000", "nome": "Ministério da Educação"},
    {"codigo": "28000", "nome": "Ministério do Desenvolvimento, Indústria, Comércio e Serviços"},
    {"codigo": "30000", "nome": "Ministério da Justiça e Segurança Pública"},
    {"codigo": "32000", "nome": "Ministério de Minas e Energia"},
    {"codigo": "33000", "nome": "Ministério da Previdência Social"},
    {"codigo": "22000", "nome": "Ministério da Agricultura e Pecuária"},
    {"codigo": "24000", "nome": "Ministério da Ciência, Tecnologia e Inovação"},
    {"codigo": "20105", "nome": "Ministério da Defesa"},
    {"codigo": "20114", "nome": "Advocacia-Geral da União"},
    {"codigo": "37000", "nome": "Controladoria-Geral da União"},
    {"codigo": "29000", "nome": "Defensoria Pública da União"},
]

# ========== FUNÇÃO DE CATEGORIZAÇÃO CORRIGIDA ==========
def categorizar_orgao(nome: str, codigo: str) -> str:
    nome_upper = nome.upper()
    # 1. Prioridade máxima: Presidência ou Gabinetes
    if "PRESIDÊNCIA" in nome_upper or "GABINETE" in nome_upper:
        return "Presidência"
    # 2. Qualquer órgão que contenha "MINISTÉRIO" vai para Ministérios
    if "MINISTÉRIO" in nome_upper:
        return "Ministérios"
    # 3. Autarquias, agências, bancos centrais, etc.
    if any(p in nome_upper for p in ["AGÊNCIA", "BANCO CENTRAL", "SECRETARIA", "ADVOCACIA", "CONTROLADORIA", "DEFENSORIA"]):
        return "Autarquias e Outros"
    # 4. Fundos, polícias, demais órgãos
    return "Outros Órgãos"

def parse_valor(valor_str: str) -> float:
    """Converte string como '2.287.941.886.200,98' para float."""
    if not valor_str:
        return 0.0
    try:
        return float(valor_str.replace('.', '').replace(',', '.'))
    except (ValueError, TypeError):
        return 0.0

# ---------- Consulta a um órgão (com retry, timeout alto e SEM filtro de zero) ----------
async def fetch_orgao(client: httpx.AsyncClient, base_url: str, ano: int,
                      org: Dict[str, str], semaphore: asyncio.Semaphore) -> Optional[Dict[str, Any]]:
    codigo = org["codigo"]
    nome_fallback = org["nome"]
    url = f"{base_url}/api-de-dados/despesas/por-orgao"
    # Buscar muitos itens para garantir que pega tudo (caso haja paginação)
    params = {"ano": ano, "orgaoSuperior": codigo, "pagina": 1, "itens": 1000}

    async with semaphore:
        for tentativa in range(3):  # 3 tentativas
            try:
                await asyncio.sleep(0.5 * tentativa)  # backoff
                resp = await client.get(url, params=params, timeout=90.0, follow_redirects=False)
                if resp.status_code == 302:
                    print(f"[FETCH] {nome_fallback} ({codigo}) -> 302 (chave inválida?)")
                    # Retorna mesmo assim para o órgão aparecer (valor zero)
                    return {
                        "nome": nome_fallback,
                        "categoria": categorizar_orgao(nome_fallback, codigo),
                        "valor": 0.0,
                        "empenhado": "0",
                        "liquidado": "0",
                        "pago": "0"
                    }
                if resp.status_code != 200:
                    print(f"[FETCH] {nome_fallback} ({codigo}) -> HTTP {resp.status_code}")
                    return {
                        "nome": nome_fallback,
                        "categoria": categorizar_orgao(nome_fallback, codigo),
                        "valor": 0.0,
                        "empenhado": "0",
                        "liquidado": "0",
                        "pago": "0"
                    }

                dados = resp.json()
                if not dados:
                    print(f"[FETCH] {nome_fallback} ({codigo}) -> sem dados (lista vazia)")
                    return {
                        "nome": nome_fallback,
                        "categoria": categorizar_orgao(nome_fallback, codigo),
                        "valor": 0.0,
                        "empenhado": "0",
                        "liquidado": "0",
                        "pago": "0"
                    }

                # Soma todos os itens retornados
                total_pago = 0.0
                total_empenhado = 0.0
                total_liquidado = 0.0
                nome_oficial = dados[0].get("orgao", nome_fallback)

                for item in dados:
                    total_pago += parse_valor(item.get("pago", "0"))
                    total_empenhado += parse_valor(item.get("empenhado", "0"))
                    total_liquidado += parse_valor(item.get("liquidado", "0"))

                print(f"[FETCH] {nome_oficial} -> R$ {total_pago:,.2f} pago")
                return {
                    "nome": nome_oficial,
                    "categoria": categorizar_orgao(nome_oficial, codigo),
                    "valor": total_pago,
                    "empenhado": f"{total_empenhado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if total_empenhado else "0",
                    "liquidado": f"{total_liquidado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if total_liquidado else "0",
                    "pago": f"{total_pago:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if total_pago else "0"
                }

            except (httpx.TimeoutException, httpx.ConnectError) as e:
                print(f"[FETCH] Tentativa {tentativa+1} para {nome_fallback} ({codigo}) falhou: {type(e).__name__}")
                if tentativa == 2:
                    print(f"[FETCH] ❌ {nome_fallback} ({codigo}) -> esgotadas as tentativas")
                    return {
                        "nome": nome_fallback,
                        "categoria": categorizar_orgao(nome_fallback, codigo),
                        "valor": 0.0,
                        "empenhado": "0",
                        "liquidado": "0",
                        "pago": "0"
                    }
                continue
            except Exception as e:
                print(f"[FETCH] Erro inesperado para {nome_fallback} ({codigo}): {e}")
                return {
                    "nome": nome_fallback,
                    "categoria": categorizar_orgao(nome_fallback, codigo),
                    "valor": 0.0,
                    "empenhado": "0",
                    "liquidado": "0",
                    "pago": "0"
                }
    return None

# ==================== ENDPOINT EXECUTIVO ====================
@router.get("/resumo-detalhado")
async def get_resumo_gastos_detalhado(ano: int = 2025):
    api_key = os.getenv("PORTAL_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Chave de API não configurada.")

    cache_key = f"resumo_{ano}"
    cached = get_cache_or_none(cache_key)
    if cached is not None:
        return cached

    base_url = "https://api.portaldatransparencia.gov.br"
    headers = {"chave-api-dados": api_key}
    # Usar TODOS os órgãos do Executivo (46 ou mais)
    orgaos = ORGAOS_EXECUTIVO if ORGAOS_EXECUTIVO else FALLBACK_ORGAOS
    print(f"[EXECUTIVO] Iniciando consulta para {len(orgaos)} órgãos (ano {ano})...")

    semaphore = asyncio.Semaphore(3)  # reduzido para evitar sobrecarga
    async with httpx.AsyncClient(
        headers=headers,
        limits=httpx.Limits(max_connections=10),
        timeout=httpx.Timeout(90.0, connect=15.0)
    ) as client:
        tasks = [fetch_orgao(client, base_url, ano, org, semaphore) for org in orgaos]
        resultados = await asyncio.gather(*tasks)

    # resultados nunca será None para nenhum órgão (sempre retorna um dict, mesmo com valor zero)
    detalhes = [r for r in resultados if r is not None]
    print(f"[EXECUTIVO] {len(detalhes)} órgãos processados (incluindo os com valor zero).")

    # Se mesmo assim não tiver nenhum (improvável), tenta ano anterior
    if not detalhes and ano > 2020:
        print(f"[EXECUTIVO] Nenhum dado para {ano}, tentando {ano-1}...")
        return await get_resumo_gastos_detalhado(ano-1)

    # Agrupa por categoria
    categorias = {}
    for org in detalhes:
        cat = org.pop("categoria")
        categorias.setdefault(cat, []).append(org)

    ordem_categorias = ["Presidência", "Ministérios", "Autarquias e Outros", "Outros Órgãos"]
    resultado_categorias = []
    total_geral = 0.0
    for cat in ordem_categorias:
        if cat in categorias:
            itens = sorted(categorias[cat], key=lambda x: x["valor"], reverse=True)
            subtotal = sum(item["valor"] for item in itens)
            total_geral += subtotal
            resultado_categorias.append({
                "nome": cat,
                "valor": round(subtotal, 2),
                "itens": itens
            })

    resposta = {
        "ano": ano,
        "total": round(total_geral, 2),
        "categorias": resultado_categorias
    }
    save_cache(cache_key, resposta)
    return resposta

# ==================== ENDPOINT LEGISLATIVO ====================
@router.get("/legislativo")
async def get_legislativo(ano: int = 2025, db: Session = Depends(get_db)):
    cache_key = f"legislativo_{ano}"
    cached = get_cache_or_none(cache_key)
    if cached is not None:
        return cached

    # Câmara
    total_camara = 0.0
    detalhes_camara = []
    try:
        deputados = db.query(Politico).filter(Politico.cargo == "deputado").all()
        for dep in deputados:
            valor = dep.gasto_total or 0.0
            if valor > 0:
                total_camara += valor
                detalhes_camara.append({"nome": dep.nome, "valor": valor})
        detalhes_camara = sorted(detalhes_camara, key=lambda x: x["valor"], reverse=True)[:10]
        print(f"[LEGISLATIVO] Câmara: {len(deputados)} deputados, total R$ {total_camara:,.2f}")
    except Exception as e:
        print(f"[LEGISLATIVO] Erro Câmara: {e}")

    # Senado
    total_senado = 0.0
    detalhes_senado = []
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get("https://apis.codante.io/senator-expenses/senators")
            if resp.status_code == 200:
                senators = resp.json().get("data", [])
                for sen in senators:
                    sen_id = sen.get("id")
                    if not sen_id:
                        continue
                    resp_exp = await client.get(
                        f"https://apis.codante.io/senator-expenses/senators/{sen_id}/expenses",
                        params={"year": ano}
                    )
                    if resp_exp.status_code == 200:
                        expenses = resp_exp.json().get("data", [])
                        total_sen = sum(float(e.get("value", 0)) for e in expenses)
                        if total_sen > 0:
                            total_senado += total_sen
                            detalhes_senado.append({"nome": sen.get("name"), "valor": total_sen})
                detalhes_senado = sorted(detalhes_senado, key=lambda x: x["valor"], reverse=True)[:10]
                print(f"[LEGISLATIVO] Senado: total R$ {total_senado:,.2f}")
            else:
                print(f"[LEGISLATIVO] API do Senado status {resp.status_code}")
    except Exception as e:
        print(f"[LEGISLATIVO] Erro Senado: {e}")

    total_legislativo = total_camara + total_senado
    resposta = {
        "ano": ano,
        "total": round(total_legislativo, 2),
        "camara": {"total": round(total_camara, 2), "itens": detalhes_camara},
        "senado": {"total": round(total_senado, 2), "itens": detalhes_senado}
    }
    save_cache(cache_key, resposta)
    return resposta

# ==================== ENDPOINTS AUXILIARES ====================
@router.get("/judiciario")
async def get_judiciario():
    return {
        "orgaos": [
            "Supremo Tribunal Federal (STF)",
            "Conselho Nacional de Justiça (CNJ)",
            "Superior Tribunal de Justiça (STJ)",
            "Justiça do Distrito Federal e Territórios",
            "Justiça do Trabalho",
            "Justiça Eleitoral",
            "Justiça Federal",
            "Justiça Militar da União"
        ],
        "mensagem": "Dados orçamentários consolidados disponíveis no CNJ.",
        "fonte": "https://www.cnj.jus.br/transparencia/"
    }

@router.get("/autonomos")
async def get_autonomos():
    return {
        "orgaos": [
            "Tribunal de Contas da União (TCU)",
            "Defensoria Pública da União (DPU)",
            "Ministério Público Federal (MPF)",
            "Ministério Público do Trabalho (MPT)",
            "Ministério Público Militar (MPM)",
            "Ministério Público do Distrito Federal e Territórios (MPDFT)",
            "Escola Superior do Ministério Público da União (ESMPU)"
        ],
        "mensagem": "Cada órgão possui seu próprio portal de transparência.",
        "fonte": "Portais de Transparência individuais"
    }