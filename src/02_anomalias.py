"""
02_anomalias.py
Detecta anomalias que podem enviesar a análise e PROPÕE tratamento
(apenas diagnóstico — não altera dados). Gera outputs/02_anomalias.csv
e imprime resumo no console.

Áreas checadas:
  A. Preços zerados, negativos ou absurdos (Price_AV, VivaReal, cleaning_fee)
  B. Coordenadas fora / inconsistentes com Itapema (Mesh, Details)
  C. Listings sem atividade: number_of_reviews=0, sem star_rating, is_new_listing
  D. Áreas / dormitórios inconsistentes no VivaReal e Details
"""
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data"
OUT = Path(__file__).resolve().parents[1] / "outputs"

ENC = "utf-8-sig"
d = pd.read_csv(DATA / "Details_Itapema.csv", encoding=ENC)
m = pd.read_csv(DATA / "Mesh_Ids_Data_Itapema.csv", encoding=ENC)
p = pd.read_csv(DATA / "Price_AV_Itapema.csv", encoding=ENC)
v = pd.read_csv(DATA / "VivaReal_Itapema.csv", encoding=ENC)

print("=" * 70)
print("A. PREÇOS ZERADOS, NEGATIVOS OU ABSURDOS")
print("=" * 70)

# Price_AV
prices = pd.to_numeric(p["price"], errors="coerce")
print("\nPrice_AV.price:")
print(f"  min={prices.min():.2f}  max={prices.max():.2f}  median={prices.median():.2f}")
print(f"  zerados: {(prices == 0).sum()}  negativos: {(prices < 0).sum()}  nulos: {prices.isna().sum()}")
# absurdos: acima de p99.5 ou abaixo de p0.5
q99 = prices.quantile(0.995); q01 = prices.quantile(0.005)
print(f"  p0.5={q01:.2f}  p99.5={q99:.2f}")
print(f"  acima de p99.5: {(prices > q99).sum()}  abaixo de p0.5: {(prices < q01).sum()}")
print(prices.describe().to_string())

# VivaReal sale_price e rental_price
print("\nVivaReal.sale_price:")
sp = pd.to_numeric(v["sale_price"], errors="coerce")
print(f"  nulos={sp.isna().sum()}  zerados={(sp == 0).sum()}  negativos={(sp < 0).sum()}")
print(f"  min={sp.min():.2f}  max={sp.max():.2f}  median={sp.median():.2f}")
print(sp.describe().to_string())

print("\nVivaReal.rental_price:")
rp = pd.to_numeric(v["rental_price"], errors="coerce")
print(f"  nulos={rp.isna().sum()}  zerados={(rp == 0).sum()}")
print(f"  min={rp.min():.2f}  max={rp.max():.2f}  median={rp.median():.2f}")

# Details cleaning_fee
print("\nDetails.cleaning_fee:")
cf = pd.to_numeric(d["cleaning_fee"], errors="coerce")
print(f"  nulos={cf.isna().sum()}  zerados={(cf == 0).sum()}  max={cf.max():.2f}  median={cf.median():.2f}")

print()
print("=" * 70)
print("B. COORDENADAS FORA / INCONSISTENTES COM ITAPEMA")
print("=" * 70)

# Bounds aproximados de Itapema (SC): ~ lat -27.20 a -26.99, lon -48.66 a -48.55
LAT_MIN, LAT_MAX = -27.25, -26.95
LON_MIN, LON_MAX = -48.70, -48.50

for label, df in [("Mesh", m), ("Details", d)]:
    lat = pd.to_numeric(df["latitude"], errors="coerce")
    lon = pd.to_numeric(df["longitude"], errors="coerce")
    fora = ((lat < LAT_MIN) | (lat > LAT_MAX) | (lon < LON_MIN) | (lon > LON_MAX))
    n_fora = fora.sum()
    print(f"\n{label}: {len(df)} linhas | fora do box Itapema: {n_fora} ({100*n_fora/len(df):.2f}%)")
    bad = df.loc[fora, ["airbnb_listing_id", "latitude", "longitude"]]
    print(bad.head(10).to_string(index=False))
    seg = df.loc[~fora]
    if len(seg):
        print(f"  dentro: lat [{seg['latitude'].min():.4f},{seg['latitude'].max():.4f}] lon [{seg['longitude'].min():.4f},{seg['longitude'].max():.4f}]")
    print(f"  lat nulos: {lat.isna().sum()}  lon nulos: {lon.isna().sum()}")

# suburb nao convencionais? (cidade que nao seja Itapema)
print("\nMesh.suburb (nuniques):")
print(m["suburb"].value_counts().head(15).to_string())

print()
print("=" * 70)
print("C. LISTINGS SEM ATIVIDADE / REVIEWS")
print("=" * 70)
print("\nDetails.number_of_reviews:")
rv = pd.to_numeric(d["number_of_reviews"], errors="coerce")
print(f"  nulos={rv.isna().sum()}  zerados={(rv == 0).sum()} ({100*(rv == 0).mean():.1f}%)  max={rv.max()}")
print("\nDetails.star_rating:")
sr = pd.to_numeric(d["star_rating"], errors="coerce")
print(f"  nulos={sr.isna().sum()}  zerados={(sr == 0).sum()}  min={sr.min()}  max={sr.max()}")
print("\nDetails.guest_satisfaction_overall:")
gs = pd.to_numeric(d["guest_satisfaction_overall"], errors="coerce")
print(f"  nulos={gs.isna().sum()}  zerados={(gs == 0).sum()}  min={gs.min()}  max={gs.max()}")
print("\nDetails.is_new_listing:")
print(d["is_new_listing"].value_counts(dropna=False).to_string())
# sem atividade = sem reviews e novo
sem_atv = (rv.fillna(0) == 0)
print(f"  listings com zero reviews: {sem_atv.sum()} ({100*sem_atv.mean():.1f}%)")
print(f"  listings com zero reviews E is_new_listing=True: {(sem_atv & d['is_new_listing'].astype(bool)).sum()}")

print()
print("=" * 70)
print("D. ÁREAS / DORMITÓRIOS INCONSISTENTES (VivaReal e Details)")
print("=" * 70)
ua = pd.to_numeric(v["usable_area"], errors="coerce")
print("\nVivaReal.usable_area:")
print(f"  nulos={ua.isna().sum()}  zerados={(ua == 0).sum()}  negativos={(ua < 0).sum()}")
print(f"  min={ua.min():.2f}  max={ua.max():.2f}  median={ua.median():.2f}")
print(f"  > 300m2: {(ua > 300).sum()}")
print("\nVivaReal.bedrooms:")
bd = pd.to_numeric(v["bedrooms"], errors="coerce")
print(f"  nulos={bd.isna().sum()}  zerados={(bd == 0).sum()}")
print(f"  valores: {bd.value_counts(dropna=False).sort_index().to_string()}")
print("\nVivaReal.bathrooms:")
ba = pd.to_numeric(v["bathrooms"], errors="coerce")
print(f"  nulos={ba.isna().sum()}  zerados={(ba == 0).sum()}  valores acima de 10: {(ba > 10).sum()}")

print("\nDetails.number_of_bedrooms:")
dbd = pd.to_numeric(d["number_of_bedrooms"], errors="coerce")
print(f"  nulos={dbd.isna().sum()}  zerados={(dbd == 0).sum()}")
print(f"  valores: {dbd.value_counts(dropna=False).sort_index().to_string()}")
print("\nDetails.number_of_guests:")
dg = pd.to_numeric(d["number_of_guests"], errors="coerce")
print(f"  nulos={dg.isna().sum()}  zerados={(dg == 0).sum()}  max={dg.max()}")

# inconsistencia: area com 0/1 dormitórios mas muita area, ou area < razoavel
print("\nVivaReal: imóveis com usable_area<=5m2 ou bedrooms>0 com area<8m2:")
sus = v[(ua <= 5) | ((bd > 0) & (ua < 8))]
print(f"  {len(sus)} ocorrências")
print(sus[["listing_id", "sale_price", "usable_area", "bedrooms"]].head(10).to_string(index=False))

# summary output
resumo = {
    "precos_zerados_price": int((prices == 0).sum()),
    "precos_negativos_price": int((prices < 0).sum()),
    "precos_acima_p995_price": int((prices > q99).sum()),
    "sale_price_nulos": int(sp.isna().sum()),
    "sale_price_zero_neg": int(((sp == 0) | (sp < 0)).sum()),
    "coord_fora_mesh": int(fora.sum()) if False else None,
    "review_zero": int(sem_atv.sum()),
    "star_nulos": int(sr.isna().sum()),
    "area_zerada_neg": int(((ua == 0) | (ua < 0)).sum()),
}
# calcular coords fora p/ mesh definitivamente fora do escopo
pd.DataFrame([resumo]).to_csv(OUT / "02_anomalias.csv", index=False, encoding="utf-8-sig")
print(f"\nEscrito: outputs/02_anomalias.csv")