"""
01b_duplicatas_price.py
Verifica duplicatas exatas em Price_AV (maior risco de "dados inflados"):
- linhas exatamente duplicadas (airbnb_listing_id + date + price + aquisition_date)
- pares (airbnb_listing_id, date) repetidos com preços diferentes (conflito)
Grava outputs/01b_duplicatas_price.csv
"""
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data"
OUT = Path(__file__).resolve().parents[1] / "outputs"
p = pd.read_csv(DATA / "Price_AV_Itapema.csv", encoding="utf-8-sig")

dups_exatas = p[p.duplicated(keep=False)]
print(f"Price_AV: {len(p)} linhas | duplicatas EXATAS (todas colunas): {len(dups_exatas)}")

chave = ["airbnb_listing_id", "date"]
dup_chave = p[p.duplicated(chave, keep=False)].sort_values(chave)
print(f"Pares (listing, date) repetidos: {len(dup_chave)} linhas | {p.duplicated(chave).sum()} extras")
print("Exemplo dos primeiros pares repetidos:")
cols = ["airbnb_listing_id", "date", "price"]
print(dup_chave[cols].head(10).to_string(index=False))

if len(dup_chave):
    (dup_chave[cols].assign(ocorrencias=dup_chave.groupby(chave)[chave[0]].transform("size"))
     .to_csv(OUT / "01b_duplicatas_price.csv", index=False, encoding="utf-8-sig"))
print("Escrito: outputs/01b_duplicatas_price.csv")