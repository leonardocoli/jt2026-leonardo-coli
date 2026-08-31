"""
08_dashboard_data.py
Gera dashboard/data.js (JSON embutido) a partir dos outputs das sessoes 04-07.
Abre offline; usado pelo dashboard/index.html.
"""
from pathlib import Path
import json
import pandas as pd, numpy as np

DATA = Path(__file__).resolve().parents[1] / "data"
OUT = Path(__file__).resolve().parents[1] / "outputs"
DASH = Path(__file__).resolve().parents[1] / "dashboard"
ENC = "utf-8-sig"

rec = pd.read_csv(OUT / "04_receita.csv", encoding=ENC)
d = pd.read_csv(DATA / "Details_Itapema.csv", encoding=ENC)[["airbnb_listing_id", "number_of_reviews", "number_of_bedrooms", "listing_type"]]
m = pd.read_csv(DATA / "Mesh_Ids_Data_Itapema.csv", encoding=ENC)[["airbnb_listing_id", "latitude", "longitude", "suburb"]].drop_duplicates("airbnb_listing_id")
a = rec.merge(d, on="airbnb_listing_id", how="left").merge(m, on="airbnb_listing_id", how="left")
a["bairro"] = a["suburb"].astype(str).str.strip().str.title()

# --- mapa: listings (com preco) por lat/long e receita anual piso ---
mapa = a[["airbnb_listing_id", "latitude", "longitude", "bairro",
          "adr", "occ_le15", "rec_anual_ombro_piso"]].dropna(subset=["latitude", "longitude", "rec_anual_ombro_piso"])
mapa = mapa[(mapa["latitude"] != 0) & (mapa["longitude"] != 0)]

# pontos de contexto: todos os listings do Mesh (sem preco) em cinza
ctx = m[["latitude", "longitude"]].dropna()
ctx = ctx[(ctx["latitude"] != 0) & (ctx["longitude"] != 0)]

D = {}
D["cards"] = {
    "n_listings_total": int(len(d)),
    "n_listings_preco": int(a["airbnb_listing_id"].nunique()),
    "n_map": len(mapa),
    "adr_mediano": round(float(a["adr"].median()), 0),
    "occ_alta": round(float(0.767), 3),
    "occ_piso": round(float(0.408), 3),
    "rec_91d_media": round(float(rec["receita_91d_piso"].mean()), 0),
    "rec_91d_mediana": round(float(rec["receita_91d_piso"].median()), 0),
    "rec_anual_mediana": round(float(a["rec_anual_ombro_piso"].median()), 0),
}
# centroides por bairro a partir do Mesh (todos os listings) para rotulagem estavel
bairros_geo = m[m["suburb"].astype(str).str.strip().str.title() != "None"].copy()
bairros_geo["bairro"] = bairros_geo["suburb"].astype(str).str.strip().str.title()
cent = bairros_geo.groupby("bairro")[["latitude", "longitude"]].mean()
nombre_min = 8  # rotula so bairros com >= 8 listings para nao poluir
contagem = bairros_geo.groupby("bairro").size()
labels_bairro = [
    {"nome": b, "lat": round(float(cent.loc[b, "latitude"]), 4),
     "lon": round(float(cent.loc[b, "longitude"]), 4), "n": int(contagem[b])}
    for b in cent.index if contagem[b] >= nombre_min
]

# --- localizacao por bairro (receita) para substituir o mapa ---
ba = a[a["rec_anual_ombro_piso"].notna()].copy()
ba_rec = ba.groupby("bairro").agg(
    n=("airbnb_listing_id", "count"),
    rec_med=("rec_anual_ombro_piso", "median"),
    adr_med=("adr", "median"),
    occ_med=("occ_le15", "median"),
).reset_index()
ba_rec = ba_rec[ba_rec["n"] >= 5].copy()
ba_rec["rec_total"] = ba_rec["n"] * ba_rec["rec_med"]
ba_rec = ba_rec.sort_values("rec_total", ascending=False)
D["bairros_receita"] = [
    {"bairro": r["bairro"], "n": int(r["n"]),
     "rec_med": round(float(r["rec_med"]), 0),
     "rec_total": round(float(r["rec_total"]), 0),
     "adr_med": round(float(r["adr_med"]), 0),
     "occ_med": round(float(r["occ_med"]), 3)}
    for _, r in ba_rec.iterrows()
]

# --- yields por celula bairro x quartos ---
yc = pd.read_csv(OUT / "05_yield_cross.csv", encoding=ENC)
yc = yc[yc["yield_liq"].notna()].copy()
yc["cel"] = yc["bairro"] + " " + yc["q"].astype(int).astype(str) + "Q"
yc["compact"] = yc["q"].isin([0, 1, 2])
D["yields"] = yc[["cel", "bairro", "q", "n_airbnb", "n_viva", "adr_med", "occ_le15_med",
                  "preco_med", "rec_an_med", "yield_bruto", "yield_liq", "yield_liq_adm",
                  "compact", "indicativo"]].to_dict("records")
# card de yield compacto (mediana das celulas 1-2Q, liquido op10) — mesma fonte da tabela §5
D["cards"]["yield_compacto"] = round(float(yc.loc[yc["compact"], "yield_liq"].median()), 3)

# --- cenarios robustez 06 ---
c6 = pd.read_csv(OUT / "06_cenarios_yield.csv", encoding=ENC)
c6 = c6.sort_values("yl_base", ascending=False)
D["cenarios_06"] = c6[["celula", "status", "yl_base", "yl_A_occ80", "yl_B_f60", "yl_C_adm20", "yl_COMB"]].to_dict("records")

# --- cenarios adversariais 07 ---
c7 = pd.read_csv(OUT / "07_cenarios_adversarios.csv", encoding=ENC)
D["cenarios_07"] = c7.to_dict("records")

D["robustez"] = {
    "compactos_vs_grandes": 1.43,
    "compactos_vs_4q": 2.0,
    "s1_topo_mudou": True,
    "fonte_selic": "BCB — Selic meta 12,25% a.a. (dez/2024) e 13,25% a.a. (29/jan/2025). ref. bcb.gov.br/controleinflacao/historicotaxasjuros",
}

js = "/* Gerado por src/08_dashboard_data.py — dados embutidos (offline) */\n"
js += "window.DASH_DATA = " + json.dumps(D, ensure_ascii=False).replace("NaN", "null") + ";\n"
DASH.mkdir(exist_ok=True)
(DASH / "data.js").write_text(js, encoding="utf-8")

# resumo de diagnostico para conferir
print("cards:", D["cards"])
print("bairros_receita:", len(D["bairros_receita"]))
print("yields:", len(D["yields"]))
print("cenarios06:", len(D["cenarios_06"]), "cenarios07:", len(D["cenarios_07"]))
print("escrito:", DASH / "data.js")