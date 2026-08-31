"""
06_robustez_cenarios.py
Refaz o ranking de yield sob estresse e compara com o base (secao 05).

Cenarios:
  BASE  : occ_fwd = 0.408 x (occ_le15_cel/occ_global); fator sazonal 0.77; sem adm
  A     : ocupacao 20% menor (occ_fwd x 0.8)
  B     : fator sazonal 0.60 (em vez de 0.77)
  C     : taxa de administracao 20% deduzida da receita bruta
  COMB  : A + B + C (tudo junto)

Custos: condominio (mediana >0 x12) + IPTU (mediana >0) + operacional 15% da receita bruta.
Cenarios A/B/C isolados mantem as demais premissas do base; COMB aplica os tres.
Saidas: outputs/06_cenarios_yield.csv
"""
from pathlib import Path
import numpy as np, pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data"
OUT = Path(__file__).resolve().parents[1] / "outputs"
ENC = "utf-8-sig"

MIN_N, IND_N = 30, 10
OP_PCT = 0.15
H, REST = 91, 274
F_SAZ_BASE = 0.77
F_SAZ_PES = 0.60

rec = pd.read_csv(OUT / "04_receita.csv", encoding=ENC)
d = pd.read_csv(DATA / "Details_Itapema.csv", encoding=ENC)[["airbnb_listing_id", "listing_type", "number_of_bedrooms"]]
m = pd.read_csv(DATA / "Mesh_Ids_Data_Itapema.csv", encoding=ENC)[["airbnb_listing_id", "suburb"]].drop_duplicates("airbnb_listing_id")
a = rec.merge(d, on="airbnb_listing_id", how="left").merge(m, on="airbnb_listing_id", how="left")
a = a[a["listing_type"] == "apartamento"].copy()
a["bairro"] = a["suburb"].astype(str).str.strip().str.title()
a["q"] = pd.to_numeric(a["number_of_bedrooms"], errors="coerce").fillna(0).clip(0, 4).astype(int)

GLOBAL_OCC = a["occ_le15"].mean()

v = pd.read_csv(DATA / "VivaReal_Itapema.csv", encoding=ENC)
v = v[v["listing_type"] == "apartamento"].copy()
v["bairro"] = v["suburb"].astype(str).str.strip().str.title()
v["q"] = pd.to_numeric(v["bedrooms"], errors="coerce").fillna(0).clip(0, 4).astype(int)
v["sp"] = pd.to_numeric(v["sale_price"], errors="coerce")
v["condo"] = pd.to_numeric(v["monthly_condo_fee"], errors="coerce")
v["iptu"] = pd.to_numeric(v["yearly_iptu"], errors="coerce")

ar = a.groupby(["bairro", "q"]).agg(
    n_ab=("adr", "count"), adr=("adr", "median"), occ=("occ_le15", "median"),
).reset_index()
vr = v.groupby(["bairro", "q"]).agg(
    n_vr=("sp", "count"), preco=("sp", "median"),
    condo=("condo", lambda s: s[s > 0].median()), iptu=("iptu", lambda s: s[s > 0].median()),
).reset_index()

c = ar.merge(vr, on=["bairro", "q"], how="inner")
c = c[(c["n_ab"] >= MIN_N) | (c["n_vr"] >= MIN_N)]  # concorre a mostrar; filtro de conclusivo abaixo

def yield_net(preco, rec_bruta, condo_fixo, adm_pct=0.0):
    rec_liq = rec_bruta * (1 - adm_pct) - condo_fixo - rec_bruta * OP_PCT
    return rec_liq / preco

rows = []
for _, r in c.iterrows():
    if r["preco"] <= 0 or pd.isna(r["preco"]) or pd.isna(r["adr"]):
        rows.append({"bairro": r["bairro"], "q": int(r["q"]), "n_ab": r["n_ab"], "n_vr": r["n_vr"],
                     "adr": r["adr"], "occ_alta": r["occ"], "preco": r["preco"],
                     "status": "NC"})
        continue
    conclusivo = r["n_ab"] >= MIN_N and r["n_vr"] >= MIN_N
    indicativo = not conclusivo and r["n_ab"] >= IND_N and r["n_vr"] >= IND_N
    if not (conclusivo or indicativo):
        rows.append({"bairro": r["bairro"], "q": int(r["q"]), "n_ab": r["n_ab"], "n_vr": r["n_vr"],
                     "adr": r["adr"], "occ_alta": r["occ"], "preco": r["preco"], "status": "NC"})
        continue

    occ_f = 0.408 * (r["occ"] / GLOBAL_OCC)
    condo_fixo = (r["condo"] if pd.notna(r["condo"]) else 0) * 12 + (r["iptu"] if pd.notna(r["iptu"]) else 0)

    rec91_base = r["adr"] * H * occ_f
    rec_an_base = rec91_base + r["adr"] * F_SAZ_BASE * REST * occ_f
    rec_an_A = (r["adr"] * H * occ_f * 0.8) + r["adr"] * F_SAZ_BASE * REST * (occ_f * 0.8)
    rec_an_B = (r["adr"] * H * occ_f) + r["adr"] * F_SAZ_PES * REST * occ_f
    rec_an_C = rec_an_base  # receita igual; adm deduzida no yield
    rec_an_COMB = (r["adr"] * H * occ_f * 0.8) + r["adr"] * F_SAZ_PES * REST * (occ_f * 0.8)

    rows.append({
        "bairro": r["bairro"], "q": int(r["q"]), "n_ab": r["n_ab"], "n_vr": r["n_vr"],
        "adr": r["adr"], "occ_alta": r["occ"], "preco": r["preco"], "status": "OK" if conclusivo else "IND",
        "yl_base": yield_net(r["preco"], rec_an_base, condo_fixo, 0.0),
        "yl_A_occ80": yield_net(r["preco"], rec_an_A, condo_fixo, 0.0),
        "yl_B_f60": yield_net(r["preco"], rec_an_B, condo_fixo, 0.0),
        "yl_C_adm20": yield_net(r["preco"], rec_an_C, condo_fixo, 0.20),
        "yl_COMB": yield_net(r["preco"], rec_an_COMB, condo_fixo, 0.20),
    })

t = pd.DataFrame(rows)
t = t[t["status"] != "NC"].copy()
t = t.sort_values("yl_COMB", ascending=False)

# ranks por cenario
for col, tag in [("yl_base", "r_base"), ("yl_A_occ80", "r_A"), ("yl_B_f60", "r_B"),
                 ("yl_C_adm20", "r_C"), ("yl_COMB", "r_COMB")]:
    t[tag] = t[col].rank(ascending=False, method="min").astype(int)

print("GERAL: occ_global_le15 = {:.3f}".format(GLOBAL_OCC))
print("Regras: occ_fwd = 0.408 x occ_alta/occ_global; rec_an = rec_91 + ADR x f_saz x 274 x occ_fwd")
print("A: occ_fwd x0.8 | B: f_saz 0.60 | C: -20% adm | COMB = A+B+C")
print("=" * 150)
show = t[["bairro", "q", "n_ab", "n_vr", "adr", "occ_alta", "preco", "status",
          "yl_base", "yl_A_occ80", "yl_B_f60", "yl_C_adm20", "yl_COMB"]].copy()
show.insert(0, "celula", (show["bairro"] + "-" + show["q"].astype(str) + "Q"))
show["adr"] = show["adr"].round(0); show["occ_alta"] = show["occ_alta"].round(2); show["preco"] = show["preco"].round(0)
for col in ["yl_base", "yl_A_occ80", "yl_B_f60", "yl_C_adm20", "yl_COMB"]:
    show[col] = (show[col] * 100).round(2)
print(show[["celula", "n_ab", "n_vr", "adr", "occ_alta", "preco", "status",
            "yl_base", "yl_A_occ80", "yl_B_f60", "yl_C_adm20", "yl_COMB"]].to_string(index=False))

print()
print("Coluna ranking por cenario (posicao):")
print(t[["celula" if False else "bairro", "q", "status", "r_base", "r_A", "r_B", "r_C", "r_COMB"]]
      .assign(celula=t["bairro"] + "-" + t["q"].astype(str) + "Q")[["celula", "status", "r_base", "r_A", "r_B", "r_C", "r_COMB"]]
      .to_string(index=False))

t.assign(celula=t["bairro"] + "-" + t["q"].astype(str) + "Q").to_csv(OUT / "06_cenarios_yield.csv", index=False, encoding=ENC)
print("\nEscrito: outputs/06_cenarios_yield.csv")

# ---- robustez: compactos 1-2Q vs 3-4Q, e Centro-1Q ----
comps = t[t["q"].isin([1, 2])].copy()
grandes = t[t["q"].isin([3, 4])].copy()
print("\n== ROBUSTEZ ==")
print("Compactos (1-2Q) median de yl por cenario:")
print(comps[["yl_base", "yl_A_occ80", "yl_B_f60", "yl_C_adm20", "yl_COMB"]].median().round(4).to_string())
print("Grandes (3-4Q) median de yl por cenario:")
print(grandes[["yl_base", "yl_A_occ80", "yl_B_f60", "yl_C_adm20", "yl_COMB"]].median().round(4).to_string())
print()
for col in ["yl_base", "yl_A_occ80", "yl_B_f60", "yl_C_adm20", "yl_COMB"]:
    med_comp = comps[col].median(); med_gran = grandes[col].median()
    ratio = med_comp / med_gran
    qual = "mantem ~2x" if ratio >= 1.7 else ("reduz porem mantem>" if ratio > 1.2 else "COLLAPSE")
    print("  {:14s}: compactos {:.1%} vs grandes {:.1%}  (ratio {:.2f}x) -> {}".format(
        col, med_comp, med_gran, ratio, qual))
print()
c1 = t[t["celula"].str.contains("Centro-1")] if "celula" in t.columns else t[(t["bairro"] == "Centro") & (t["q"] == 1)]
print("Centro-1Q por cenario:")
print(c1[["yl_base", "yl_A_occ80", "yl_B_f60", "yl_C_adm20", "yl_COMB"]].round(4).to_string())
otros1 = t[(t["q"] == 1) & (t["bairro"] != "Centro")]
if len(otros1):
    print("Outros 1Q por cenario:")
    print(otros1[["bairro", "yl_base", "yl_A_occ80", "yl_B_f60", "yl_C_adm20", "yl_COMB"]].round(4).to_string())