import httpx

url = "https://dadosabertos.camara.leg.br/arquivos/eventosPresencaDeputados/csv/eventosPresencaDeputados-2025.csv"
resp = httpx.get(url, timeout=60)
resp.raise_for_status()

# Mostra as primeiras linhas
linhas = resp.text.splitlines()
print("Total de linhas:", len(linhas))
print("Primeiras 5 linhas:")
for linha in linhas[:5]:
    print(linha)