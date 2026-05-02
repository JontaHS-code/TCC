# backend/atualizar_palavras_chave.py
"""
Extrai palavras-chave das proposições de TODOS os políticos
diretamente da API da Câmara e salva no banco.
Versão OTIMIZADA: requisições paralelas + cache em disco.
"""
import httpx
import asyncio
import json
import os
from collections import Counter
from datetime import datetime

from database import SessionLocal
from models import Politico

CAMARA_API_URL = "https://dadosabertos.camara.leg.br/api/v2"
HEADERS = {"Accept": "application/json"}

# Cache em disco para não repetir requisições
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "dados", "cache_proposicoes")
os.makedirs(CACHE_DIR, exist_ok=True)

# Temas e palavras associadas (dicionário otimizado: palavra -> tema)
PALAVRA_PARA_TEMA = {}
TEMAS = {
    "Saúde": ["saúde", "hospital", "medicamento", "médico", "médica", "sus", "doença", "paciente", "farmacêutico", "remédio", "vacina", "enfermagem", "psicologia", "tratamento", "cirurgia", "emergência", "ambulância", "posto de saúde", "ubs", "farmacia"],
    "Educação": ["educação", "escola", "universidade", "ensino", "professor", "aluno", "estudante", "pedagogia", "escolar", "fies", "prouni", "enem", "creche", "alfabetização", "merenda", "bolsa de estudos", "aula", "didático"],
    "Segurança": ["segurança", "polícia", "crime", "penal", "prisão", "violência", "arma", "criminal", "policial", "bombeiro", "defesa civil", "homicídio", "assalto", "furto", "tráfico", "drogas", "presídio", "penitenciária"],
    "Economia": ["econômico", "imposto", "tributário", "fiscal", "orçamento", "dívida", "investimento", "mercado", "financeiro", "banco", "moeda", "inflação", "pib", "juros", "taxa", "arrecadação", "gasto público", "reforma tributária"],
    "Trabalho": ["trabalhador", "emprego", "salário", "aposentadoria", "previdência", "sindical", "servidor", "concursado", "clt", "desemprego", "fgts", "décimo terceiro", "férias", "licença", "maternidade", "estágio", "carteira assinada"],
    "Meio Ambiente": ["ambiental", "floresta", "amazônia", "sustentável", "clima", "carbono", "preservação", "desmatamento", "reciclagem", "poluição", "aquecimento global", "energia renovável", "solar", "eólica", "bioma", "fauna", "flora"],
    "Direitos Humanos": ["direitos humanos", "igualdade", "discriminação", "racismo", "feminismo", "mulher", "lgbt", "indígena", "quilombola", "inclusão", "acessibilidade", "pcd", "autismo", "idoso", "criança", "adolescente", "refugiado", "diversidade"],
    "Infraestrutura": ["infraestrutura", "transporte", "rodovia", "ferrovia", "porto", "aeroporto", "saneamento", "energia", "elétrica", "telecomunicação", "internet", "banda larga", "5g", "pavimentação", "asfalto", "mobilidade", "metrô", "ônibus"],
    "Tecnologia": ["tecnologia", "digital", "inovação", "inteligência artificial", "startup", "software", "hardware", "automação", "robótica", "cibersegurança", "blockchain", "internet das coisas", "algoritmo", "aplicativo"],
    "Agropecuária": ["agricultura", "agropecuário", "rural", "produtor", "agronegócio", "plantio", "colheita", "pecuária", "gado", "soja", "milho", "café", "fertilizante", "defensivo", "irrigação", "assentamento", "reforma agrária"],
    "Esporte": ["esporte", "atleta", "olímpico", "futebol", "educação física", "paradesporto", "paralímpico", "campeonato", "estádio", "ginásio", "medalha"],
    "Cultura": ["cultura", "artista", "museu", "cinema", "teatro", "música", "dança", "literatura", "livro", "biblioteca", "patrimônio", "histórico", "folclore", "carnaval"],
    "Turismo": ["turismo", "turístico", "hotel", "pousada", "viajante", "destino", "ecoturismo", "agência de viagem"],
    "Habitação": ["habitação", "moradia", "casa própria", "minha casa", "aluguel social", "sem teto", "urbanização"],
    "Pesca": ["pesca", "pescador", "aquicultura", "peixe", "marisco", "camarão", "oceano"],
    "Minas e Energia": ["mineração", "minério", "petróleo", "gás natural", "hidrelétrica", "usina", "combustível", "gasolina", "etanol", "biodiesel"],
}
for tema, palavras in TEMAS.items():
    for palavra in palavras:
        PALAVRA_PARA_TEMA[palavra] = tema


def extrair_temas(texto: str) -> set:
    """Extrai temas de um texto usando busca otimizada."""
    texto_lower = texto.lower()
    encontrados = set()
    for palavra, tema in PALAVRA_PARA_TEMA.items():
        if palavra in texto_lower:
            encontrados.add(tema)
    return encontrados


def get_cache_path(dep_id: int) -> str:
    return os.path.join(CACHE_DIR, f"{dep_id}.json")


def load_cache(dep_id: int) -> list | None:
    path = get_cache_path(dep_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_cache(dep_id: int, palavras: list):
    with open(get_cache_path(dep_id), "w", encoding="utf-8") as f:
        json.dump({"palavras": palavras, "data": datetime.now().isoformat()}, f)


async def buscar_proposicoes(client: httpx.AsyncClient, dep_id: int, semaphore: asyncio.Semaphore) -> list:
    """Busca ementas das proposições com controle de concorrência."""
    # Verifica cache primeiro
    cached = load_cache(dep_id)
    if cached:
        return cached["palavras"]

    async with semaphore:
        temas_todas = []
        pagina = 1

        while pagina <= 5:
            try:
                resp = await client.get(
                    f"{CAMARA_API_URL}/proposicoes",
                    params={"idDeputadoAutor": dep_id, "itens": 100, "pagina": pagina, "ordem": "DESC"},
                    timeout=20
                )
                if resp.status_code != 200:
                    break

                dados = resp.json()
                itens = dados.get("dados", [])
                if not itens:
                    break

                for item in itens:
                    ementa = item.get("ementa", "")
                    if ementa:
                        temas_todas.extend(extrair_temas(ementa))

                if len(itens) < 100:
                    break
                pagina += 1
                await asyncio.sleep(0.05)  # delay mínimo entre páginas

            except Exception:
                break

        # Top 6 temas mais frequentes
        contagem = Counter(temas_todas)
        palavras = [tema for tema, _ in contagem.most_common(6)]

        # Salva cache
        if palavras:
            save_cache(dep_id, palavras)

        return palavras


async def main():
    print("=" * 60)
    print("ATUALIZAÇÃO DE PALAVRAS-CHAVE (OTIMIZADO)")
    print("=" * 60)

    db = SessionLocal()
    try:
        politicos = db.query(Politico).all()
        total = len(politicos)
        print(f"\n👥 {total} políticos no banco.\n")

        # Carrega cache primeiro
        do_cache = sum(1 for p in politicos if load_cache(p.id))
        if do_cache:
            print(f"📦 {do_cache} já estão em cache.\n")

        # Semáforo para limitar requisições simultâneas
        semaphore = asyncio.Semaphore(8)  # 8 requisições ao mesmo tempo

        atualizados = 0
        lotes = []
        lote_atual = []

        # Processa em lotes de 50
        async with httpx.AsyncClient(headers=HEADERS, timeout=30) as client:
            for i, p in enumerate(politicos, 1):
                if not p.id:
                    continue

                lote_atual.append((i, p))

                if len(lote_atual) >= 50 or i == total:
                    # Processa o lote em paralelo
                    tarefas = [buscar_proposicoes(client, dep.id, semaphore) for _, dep in lote_atual]
                    resultados = await asyncio.gather(*tarefas)

                    for (idx, politico), palavras in zip(lote_atual, resultados):
                        if palavras:
                            politico.palavras_chave = palavras
                            atualizados += 1

                    db.commit()

                    # Mostra progresso
                    pct = (i / total) * 100
                    print(f"  💾 Lote salvo: {i}/{total} ({pct:.0f}%) • {atualizados} com palavras-chave")

                    lote_atual = []

        print(f"\n✅ Concluído! {atualizados}/{total} políticos com palavras-chave.")
        print(f"   Cache salvo em: {CACHE_DIR}")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Erro: {type(e).__name__}: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())