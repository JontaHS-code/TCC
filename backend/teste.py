# backend/diagnostico_nomes.py
import os, csv

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "dados", "despesas_2023_2026.csv")

# Carregar CSV
with open(CSV_PATH, "r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f, delimiter=";"))

# Mostrar colunas disponíveis
print("Colunas do CSV:")
for col in rows[0].keys():
    print(f"  - '{col}'")

# Mostrar alguns nomes do CSV
print("\nPrimeiros 10 nomes no CSV:")
nomes_csv = set()
for r in rows[:1000]:
    nome = r.get("txNomeParlamentar", "").strip()
    if nome:
        nomes_csv.add(nome)
        if len(nomes_csv) <= 10:
            print(f"  '{nome}'")

# Carregar banco
from database import SessionLocal
from models import Politico

db = SessionLocal()
politicos = db.query(Politico).all()
print(f"\nPrimeiros 10 nomes no BANCO:")
for p in politicos[:10]:
    print(f"  '{p.nome}'")

# Testar correspondência
print("\nTestando correspondência (primeiros 5 do banco):")
for p in politicos[:5]:
    nome_banco = p.nome.upper().strip()
    encontrado = any(r.get("txNomeParlamentar", "").upper().strip() == nome_banco for r in rows)
    print(f"  '{p.nome}' encontrado no CSV? {encontrado}")

db.close()