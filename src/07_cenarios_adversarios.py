"""
07_cenarios_adversarios.py
Cenarios adicionais de estresse sobre a base corrigida (op 10%, cleaning pass-through).

  BASE : receita piso anualizada = ADR x 91 x occ_fwd + ADR x 0.77 x 274 x occ_fwd (occ_fwd=0.408 x occ_alta/occ_global)
  S1   : EXCLUi os 308 listings imputados como ocupacao 1,0 (sem datas no lead<=15).
         Recalcula occ_global e occ_alta das celulas SOBRE o subconjunto nao-imputado.
  S2   : ADR das noites vendidas (+9%, P13) -> ADR x 1.09
  S3   : PISO ABSOLUTO = receita dos 91 dias / preco (sem nenhuma receita de inverno)

Para cada cenario, reporta o ranking e VEREDITO de robustez:
  (a) compactos (1-2Q) vs media de grandes (3-4Q)  -> alvo ~1,43x
  (b) compactos vs 4Q isolado                      -> alvo ~2x
  (c) Centro-1Q acima de todos os 3Q/4Q
  (d) Morretes-2Q no topo

Saidas: outputs/07_cenarios_adversarios.csv
"""
from pathlib import Path
import numpy as np, pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data"
OUT = Path(__file__).resolve().parents[1] / "outputs"
ENC = "utf-8-sig"

MIN_N, IND_N = 30, 10
OP_PCT = 0.10
H, REST = 91, 274
F_SAZ = 0.77
ADR_PREMIUM = 1.09  # P13: noite vendida +9% vs disponivel

rec = pd.read_csv(OUT / "04_receita.csv", encoding=ENC)
d = pd.read_csv(DATA / "Details_Itapema.csv", encoding=ENC)[["airbnb_listing_id", "listing_type", "number_of_bedrooms"]]
m = pd.read_csv(DATA / "Mesh_Ids_Data_Itapema.csv", encoding=ENC)[["airbnb_listing_id", "suburb"]].drop_duplicates("airbnb_listing_id")
a = rec.merge(d, on="airbnb_listing_id", how="left").merge(m, on="airbnb_listing_id", how="left")
a = a[a["listing_type"] == "apartamento"].copy()
a["bairro"] = a["suburb"].astype(str).str.strip().str.title()
a["q"] = pd.to_numeric(a["number_of_bedrooms"], errors="coerce").fillna(0).clip(0, 4).astype(int)

nb308 = int(a["airbnb_listing_id"].nunique() - (a["occ_le15"] < 1.0).sum())
print(f"airbnb apartamento: n={a['airbnb_listing_id'].nunique()} | imputados occ=1.0: {nb308}")

v = pd.read_csv(DATA / "VivaReal_Itapema.csv", encoding=ENC)
v = v[v["listing_type"] == "apartamento"].copy()
v["bairro"] = v["suburb"].astype(str).str.strip().str.title()
v["q"] = pd.to_numeric(v["bedrooms"], errors="coerce").fillna(0).clip(0, 4).astype(int)
v["sp"] = pd.to_numeric(v["sale_price"], errors="coerce")
v["condo"] = pd.to_numeric(v["monthly_condo_fee"], errors="coerce")
v["iptu"] = pd.to_numeric(v["yearly_iptu"], errors="coerce")

# subset sem imputados (para S1)
a_nimp = a[a["occ_le15"] < 1.0].copy()

vr = v.groupby(["bairro", "q"]).agg(
    n_vr=("sp", "count"), preco=("sp", "median"),
    condo=("condo", lambda s: s[s > 0].median()), iptu=("iptu", lambda s: s[s > 0].median()),
).reset_index()


def agg_sets(df):
    return {
        "n_ab": df.groupby(["bairro", "q"]).size(),
        "adr": df.groupby(["bairro", "q"])["adr"].median(),
        "occ": df.groupby(["bairro", "q"])["occ_le15"].median(),
    }


base = agg_sets(a)
nimp = agg_sets(a_nimp)
GLOBAL_OCC_BASE = a["occ_le15"].mean()
GLOBAL_OCC_NIMP = a_nimp["occ_le15"].mean()
print(f"occ_global: base(all)={GLOBAL_OCC_BASE:.4f} | sem_cuec308={GLOBAL_OCC_NIMP:.4f}")


def build(base_occ, occ_global, adr_mult=1.0):
    rows = []
    keys = base_occ["n_ab"].index
    for (b, q) in keys:
        n_ab = int(base_occ["n_ab"][(b, q)])
        adr = base_occ["adr"][(b, q)]
        occ = base_occ["occ"][(b, q)]
        prow = vr[(vr["bairro"] == b) & (vr["q"] == q)]
        if prow.empty:
            rows.append({"bairro": b, "q": int(q), "status": "NC"}); continue
        n_vr, preco = int(prow["n_vr"].iloc[0]), prow["preco"].iloc[0]
        if n_ab < MIN_N and n_vr < MIN_N:
            rows.append({"bairro": b, "q": int(q), "status": "NC"}); continue
        conclusivo = n_ab >= MIN_N and n_vr >= MIN_N
        ind = (not conclusivo) and n_ab >= IND_N and n_vr >= IND_N
        if not (conclusivo or ind):
            rows.append({"bairro": b, "q": int(q), "status": "NC"}); continue
        condo_fix = (prow["condo"].iloc[0] if pd.notna(prow["condo"].iloc[0]) else 0) * 12
        iptu_fix = prow["iptu"].iloc[0] if pd.notna(prow["iptu"].iloc[0]) else 0
        fix = condo_fix + iptu_fix
        occ_fwd = 0.408 * (occ / occ_global)
        adr_use = adr * adr_mult
        rec91 = adr_use * H * occ_fwd
        rec_an = rec91 + adr_use * F_SAZ * REST * occ_fwd
        yl = (rec_an * (1 - OP_PCT) - fix) / preco if preco > 0 else np.nan
        yl_floor = (rec91 * (1 - OP_PCT) - fix) / preco if preco > 0 else np.nan  # S3: so 91d
        rows.append({"bairro": b, "q": int(q), "status": "OK" if conclusivo else "IND",
                     "n_ab": n_ab, "n_vr": n_vr, "preco": preco, "occup": occ, "occup_fwd": occ_fwd,
                     "yl": yl, "yl_floor": yl_floor})
    return pd.DataFrame(rows)


def verdict(t, tag, use_col="yl"):
    t = t[t["status"] != "NC"].copy()
    t["cel"] = t["bairro"] + "-" + t["q"].astype(int).astype(str) + "Q"
    t["rank"] = t[use_col].rank(ascending=False, method="min").astype(int)
    comp = t[t["q"].isin([1, 2])]
    grand = t[t["q"].isin([3, 4])]
    q4 = t[t["q"] == 4]
    c1 = t[(t["bairro"] == "Centro") & (t["q"] == 1)]
    med_c = comp[use_col].median(); med_g = grand[use_col].median(); med_q4 = q4[use_col].median()
    v_a = med_c / med_g if med_g else np.nan        # compactos vs media de grandes
    v_b = med_c / med_q4 if len(q4) and med_q4 else np.nan  # compactos vs 4Q isolado
    v_c = bool(len(c1) and len(grand) and all(c1[use_col].iloc[0] > g for g in grand[use_col]))
    v_d = bool(len(t) and t.sort_values(use_col, ascending=False).iloc[0]["cel"] == "Morretes-2Q")
    print(f"--- {tag} ---")
    print(f"  yield median: compactos={med_c*100:.2f}% | grandes(3+4Q)={med_g*100:.2f}% | 4Q isolado={med_q4*100:.2f}%")
    print(f"  (a) comp/grandes(media)={v_a:.2f}x  (b) comp/4Q={v_b:.2f}x  (c) Centro-1Q>todos 3/4Q: {v_c}  (d) Morretes-2Q topo: {v_d}")
    out = t[["cel", "status", "n_ab", "n_vr", "preco", "occup", "occup_fwd", use_col, "rank"]].sort_values("rank")
    out[use_col] = (out[use_col] * 100).round(2)
    print(out.to_string(index=False))
    return t, {"a": v_a, "b": v_b, "c": v_c, "d": v_d, "med_c": med_c, "med_g": med_g}


print("\n=== BASE (op 10%, dados completos) ===")
t_base, r_base = verdict(build(base, GLOBAL_OCC_BASE), "BASE")

print("\n=== S1: excluindo os 308 imputados occ=1.0 ===")
t_s1, r_s1 = verdict(build(nimp, GLOBAL_OCC_NIMP), "S1")

print("\n=== S2: ADR vendido +9% ===")
t_s2, r_s2 = verdict(build(base, GLOBAL_OCC_BASE, adr_mult=ADR_PREMIUM), "S2")

print("\n=== S3: PISO ABSOLUTO = receita 91d/preco (sem inverno) ===")
t_s3f, r_s3f = verdict(build(base, GLOBAL_OCC_BASE), "S3", use_col="yl_floor")

# tabela consolidada por celula (yield liquido em cada cenario)
tbl = t_base[["bairro", "q", "status", "n_ab", "n_vr", "preco", "yl"]].merge(
    t_s1[["bairro", "q", "yl"]].rename(columns={"yl": "yl_s1"}), on=["bairro", "q"], how="outer").merge(
    t_s2[["bairro", "q", "yl"]].rename(columns={"yl": "yl_s2"}), on=["bairro", "q"], how="outer").merge(
    t_s3f[["bairro", "q", "yl_floor"]].rename(columns={"yl_floor": "yl_s3"}), on=["bairro", "q"], how="outer")
tbl["cel"] = tbl["bairro"] + "-" + tbl["q"].astype(int).astype(str) + "Q"
tbl = tbl[tbl["status"] != "NC"].sort_values("yl", ascending=False)
for c in ["yl", "yl_s1", "yl_s2", "yl_s3"]:
    tbl[c] = (pd.to_numeric(tbl[c], errors="coerce") * 100).round(2)
pd.set_option("display.width", 200)
print("\n=== TABELA CONSOLIDADA (yield liquido %; op 10%) ===")
print(tbl[["cel", "status", "n_ab", "n_vr", "preco", "yl", "yl_s1", "yl_s2", "yl_s3"]].to_string(index=False))
tbl.to_csv(OUT / "07_cenarios_adversarios.csv", index=False, encoding=ENC)
print("\nEscrito: outputs/07_cenarios_adversarios.csv")