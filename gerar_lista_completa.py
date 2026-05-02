import requests, json, os
from dotenv import load_dotenv

load_dotenv("backend/.env")
API_KEY = os.getenv("PORTAL_API_KEY")
headers = {"chave-api-dados": API_KEY}
base_url = "https://api.portaldatransparencia.gov.br/api-de-dados/orgaos-siafi"

# Termos de busca por poder
termos_por_poder = {
    "Executivo": [
        "Presidência da República",
        "Ministério",
        "Controladoria-Geral da União",
        "Advocacia-Geral da União",
        "Banco Central",
        "Casa Civil",
        "Secretaria",
        "Gabinete de Segurança Institucional",
        "Agência Espacial Brasileira",
        "Agência Nacional",
    ],
    "Legislativo": [
        "Câmara dos Deputados",
        "Senado Federal",
        "Tribunal de Contas da União",
        "Congresso Nacional",
    ],
    "Judiciário": [
        "Supremo Tribunal Federal",
        "Superior Tribunal de Justiça",
        "Conselho Nacional de Justiça",
        "Tribunal Regional Federal",
        "Justiça Federal",
        "Tribunal Superior do Trabalho",
        "Tribunal Superior Eleitoral",
        "Superior Tribunal Militar",
    ],
    "Autonomo": [
        "Ministério Público da União",
        "Defensoria Pública da União",
    ]
}

orgaos_unicos = {}  # {codigo: nome}

for poder, termos in termos_por_poder.items():
    for termo in termos:
        pagina = 1
        while True:
            resp = requests.get(
                base_url,
                params={"descricao": termo, "pagina": pagina, "itens": 100},
                headers=headers,
                timeout=30
            )
            resp.raise_for_status()
            dados = resp.json()
            if not dados:
                break
            for item in dados:
                cod = item["codigo"]
                nome = item["descricao"]
                if cod != "00000" and "CODIGO INVALIDO" not in nome:
                    orgaos_unicos[cod] = nome
            if len(dados) < 100:
                break
            pagina += 1

# Converte para lista e ordena
lista_final = [{"codigo": k, "nome": v} for k, v in sorted(orgaos_unicos.items())]

with open("backend/orgaos_superiores.json", "w", encoding="utf-8") as f:
    json.dump(lista_final, f, ensure_ascii=False, indent=2)

print(f"{len(lista_final)} órgãos superiores salvos (Executivo, Legislativo, Judiciário, Autonomo).")