"""
05_yield.py
Cruza receita Airbnb (bairro x quartos) com preco de compra VivaReal (bairro x quartos).

LIMITACAO-CHAVE: imoveis diferentes nas duas bases (nao ha join por imovel).
Compra-se "um imovel de Q quartos no bairro B" ao preco mediano VivaReal e opera-se
short stay a receita mediana PISO anual dos anúncios Airbnb da mesma celula.

Base = RECEITA BRUTA (PISO anual, fator 0.77). Deduz: condominio + IPTU + custo op 15%.
Custo de ADMINISTRACAO (-20% da receita bruta) apenas na SENSIBILIDADE.

Celulas com n<30 em QUALQUER lado = NAO CONCLUSIVAS (yields em branco).
0Q (studio) incluido. Apartamento apenas (oferta e compra).

Saidas: outputs/05_yield_cross.csv, outputs/05_scatter_cross.png
"""
from pathlib import Path
import numpy as np, pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data"
OUT = Path(__file__).resolve().parents[1] / "outputs"
ENC = "utf-8-sig"

OP_PCT = 0.15      # custo operacional (limpeza/manutencao/vacancia)
ADM_PCT = 0.20     # administracao - so sensibilidade
MIN_N = 30         # celula conclusiva
IND_N = 10         # abaixo disso = NC (nao conclusivo); entre IND e MIN = indicativo

# ---------- Receita Airbnb ----------
rec = pd.read_csv(OUT / "04_receita.csv", encoding=ENC)
d = pd.read_csv(DATA / "Details_Itapema.csv", encoding=ENC)[["airbnb_listing_id", "listing_type", "number_of_bedrooms"]]
m = pd.read_csv(DATA / "Mesh_Ids_Data_Itapema.csv", encoding=ENC)[["airbnb_listing_id", "suburb"]].drop_duplicates("airbnb_listing_id")
a = rec.merge(d, on="airbnb_listing_id", how="left").merge(m, on="airbnb_listing_id", how="left")
a = a[a["listing_type"] == "apartamento"].copy()
a["bairro"] = a["suburb"].astype(str).str.strip().str.title()
a["q"] = pd.to_numeric(a["number_of_bedrooms"], errors="coerce").fillna(0).clip(0, 4).astype(int)
a["rec_an"] = a["rec_anual_ombro_piso"]

# ---------- Preco VivaReal ----------
v = pd.read_csv(DATA / "VivaReal_Itapema.csv", encoding=ENC)
v = v[v["listing_type"] == "apartamento"].copy()
v["bairro"] = v["suburb"].astype(str).str.strip().str.title()
v["q"] = pd.to_numeric(v["bedrooms"], errors="coerce").fillna(0).clip(0, 4).astype(int)
v["sp"] = pd.to_numeric(v["sale_price"], errors="coerce")
v["area"] = pd.to_numeric(v["usable_area"], errors="coerce")
v["condo"] = pd.to_numeric(v["monthly_condo_fee"], errors="coerce")
v["iptu"] = pd.to_numeric(v["yearly_iptu"], errors="coerce")

# ocupacao global (media occ_le15 no universo das celulas = apartamentos com preco)
GLOBAL_OCC = a["occ_le15"].mean()
H_DAYS, REST_DAYS, ADR_OMBRO = 91, 274, 612.0

# agrega receita por (bairro, q)
ar = a.groupby(["bairro", "q"]).agg(
    n_airbnb=("rec_an", "count"),
    rec_an_old=("rec_an", "median"),          # receita da tabela anterior (ADR-driven, occ 0.408 fixa)
    adr_med=("adr", "median"),
    occ_le15_med=("occ_le15", "median"),
    occ_forward_med=("occ_forward_piso", "median"),
).reset_index()
ADR_OMBRO_F = 0.77  # fator sazonal 90d->resto do ano (ADR ombro/alta = 612/796), escala o ADR da celula

# NOVA receita por celula: receita_91d = ADR x 91 x (0.408 x occ_le15_celula / occ_le15_global)
ar["occ_fwd_cel"] = 0.408 * (ar["occ_le15_med"] / GLOBAL_OCC)
ar["rec_91d_novo"] = ar["adr_med"] * H_DAYS * ar["occ_fwd_cel"]
# anual: 91d + (ADR_mediano_celula x 0.77 x 274 x occ_fwd_celula)  -- fator escala o ADR da celula
ar["rec_an_novo"] = ar["rec_91d_novo"] + ar["adr_med"] * ADR_OMBRO_F * REST_DAYS * ar["occ_fwd_cel"]
ar["rec_an_med"] = ar["rec_an_novo"]  # passa a usar a nova receita como base do yield
# agrega preco por (bairro, q)
vr = v.groupby(["bairro", "q"]).agg(
    n_viva=("sp", "count"), preco_med=("sp", "median"), area_med=("area", "median"),
    rsm2_med=("sp", lambda s: (s / v.loc[s.index, "area"]).median()),
    condo_med=("condo", lambda s: s[s > 0].median()),
    iptu_med=("iptu", lambda s: s[s > 0].median()),
).reset_index()

# grid completo: bairros com presenca no Airbnb (com preco) x q 0..4
bairros = sorted(ar["bairro"].unique())
grid = pd.MultiIndex.from_product([bairros, range(0, 5)], names=["bairro", "q"]).to_frame(index=False)
cross = grid.merge(ar, on=["bairro", "q"], how="left").merge(vr, on=["bairro", "q"], how="left")
cross["n_airbnb"] = cross["n_airbnb"].fillna(0)
cross["n_viva"] = cross["n_viva"].fillna(0)

if len(cross):
    cross["conclusivo"] = (cross["n_airbnb"] >= MIN_N) & (cross["n_viva"] >= MIN_N) & (cross["preco_med"] > 0)
    cross["indicativo"] = (~cross["conclusivo"]) & (cross["n_airbnb"] >= IND_N) & (cross["n_viva"] >= IND_N) & (cross["preco_med"] > 0)
    cross["condo_ano"] = cross["condo_med"].fillna(0) * 12
    cross["iptu_ano"] = cross["iptu_med"].fillna(0)
    cross["custo_cond_iptu"] = cross["condo_ano"] + cross["iptu_ano"]
    cross["custo_op"] = cross["rec_an_med"].fillna(0) * OP_PCT
    cross["rec_liq_an"] = cross["rec_an_med"] - cross["custo_cond_iptu"] - cross["custo_op"]
    ok = cross["conclusivo"] | cross["indicativo"]
    cross["yield_bruto"] = np.where(ok, cross["rec_an_med"] / cross["preco_med"], np.nan)
    cross["yield_liq"] = np.where(ok, cross["rec_liq_an"] / cross["preco_med"], np.nan)
    # sensibilidade: admin -20% da receita bruta
    rec_adm = cross["rec_an_med"] * (1 - ADM_PCT)
    rec_liq_adm = rec_adm - cross["custo_cond_iptu"] - cross["custo_op"]
    cross["yield_liq_adm"] = np.where(ok, rec_liq_adm / cross["preco_med"], np.nan)
    cross = cross.sort_values(["bairro", "q"])

    # ---- comparacao antes/depois do yield liquido (ranking) ----
    ok = cross["conclusivo"] | cross["indicativo"]
    cmp = cross[ok].copy()
    # yield liquid "antes" (receita antiga) e "depois" (nova)
    custo_op_old = cmp["rec_an_old"] * OP_PCT
    rec_liq_old = cmp["rec_an_old"] - cmp["custo_cond_iptu"] - custo_op_old
    cmp["yl_antes"] = rec_liq_old / cmp["preco_med"]
    cmp["yl_depois"] = cmp["rec_liq_an"] / cmp["preco_med"]
    cmp["yb_antes"] = cmp["rec_an_old"] / cmp["preco_med"]
    cmp["yb_depois"] = cmp["rec_an_med"] / cmp["preco_med"]
    cmp["rank_antes"] = cmp["yl_antes"].rank(ascending=False, method="min").astype(int)
    cmp["rank_depois"] = cmp["yl_depois"].rank(ascending=False, method="min").astype(int)
    cmp["mudanca"] = np.where(cmp["rank_antes"] != cmp["rank_depois"],
                              cmp["rank_antes"].astype(str) + ">" + cmp["rank_depois"].astype(str), "=")
    cmp = cmp.sort_values("rank_depois")

    print("=" * 110)
    print("ANTES x DEPOIS - yield (receita antiga ADR-driven vs NEW com ocupacao por celula)")
    print("nova rec_91d = ADR x 91 x (0.408 x occ_le15_celula/occ_le15_global={:.3f})".format(GLOBAL_OCC))
    print("anual = rec_91d + ADR_celula x 0.77 x 274 x occ_fwd_celula (fator escala ADR da celula)")
    print("colunas: rec_an R$ | yb_ant/yb_dep bruto | yl_ant/yl_dep liquido | rank yl ant>dep")
    print("=" * 110)
    c2 = cmp[["bairro", "q", "n_airbnb", "n_viva", "adr_med", "occ_le15_med",
              "rec_an_old", "rec_an_med", "preco_med",
              "yb_antes", "yb_depois", "yl_antes", "yl_depois", "rank_antes", "rank_depois", "mudanca"]].copy()
    for cname in ["adr_med", "rec_an_old", "rec_an_med", "preco_med"]:
        c2[cname] = c2[cname].round(0)
    for cname in ["yb_antes", "yb_depois", "yl_antes", "yl_depois"]:
        c2[cname] = (c2[cname] * 100).round(2)
    c2["occ_le15_med"] = c2["occ_le15_med"].round(2)
    print(c2.to_string(index=False))
    cmp.round(6).to_csv(OUT / "05_yield_antes_depois.csv", index=False, encoding=ENC)

    print("=" * 100)
    print("YIELD POR (BAIRRO x QUARTOS) - apartamento (recalculado)")
    print("Base receita BRUTA PISO recalculada; -condominio -IPTU -op15%; -20% adm so sensibilidade")
    print("n>=30 ambos = concl.; n 10-29 em ambos = indicativo; n<10 ou sem preco = NC")
    print("=" * 100)
    show = cross[["bairro", "q", "n_airbnb", "n_viva", "adr_med", "occ_le15_med",
                  "rec_an_med", "preco_med", "rsm2_med",
                  "yield_bruto", "yield_liq", "yield_liq_adm"]].copy()
    show["sem_dados"] = (show["n_airbnb"] + show["n_viva"]) == 0
    show = show[show["bairro"].isin(bairros)]
    for c in ["preco_med", "rsm2_med", "rec_an_med", "adr_med"]:
        show[c] = show[c].round(0)
    for c in ["yield_bruto", "yield_liq", "yield_liq_adm"]:
        show[c] = np.where(show[c].isna(), "NC", (show[c] * 100).round(2).astype(str) + "%")
    # rotula indicativo
    for i, r in show.iterrows():
        qa = cross.loc[i]
        if qa["indicativo"]:
            show.at[i, "yield_bruto"] = str(show.at[i, "yield_bruto"]) + "*"
            show.at[i, "yield_liq"] = str(show.at[i, "yield_liq"]) + "*"
            show.at[i, "yield_liq_adm"] = str(show.at[i, "yield_liq_adm"]) + "*"
    print(show.to_string(index=False))

    cross.round(4).to_csv(OUT / "05_yield_cross.csv", index=False, encoding=ENC)
    print("\nEscrito: outputs/05_yield_cross.csv")

    # ---------- Scatter preco x receita (conclusivas) ----------
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"figure.figsize": (8.5, 5.5), "axes.grid": True, "grid.alpha": 0.3})
    concl = cross[cross["conclusivo"]]
    plt.figure(); ax = plt.gca()
    sc = ax.scatter(concl["preco_med"], concl["rec_an_med"], s=140,
                    c=concl["yield_liq"] * 100, cmap="viridis")
    plt.colorbar(sc, label="yield líquido (%)")
    for _, r in concl.iterrows():
        ax.annotate(f"{r['bairro']}-{int(r['q'])}Q", (r["preco_med"], r["rec_an_med"]), fontsize=9)
    ax.set_xlabel("preço de compra mediano (R$)")
    ax.set_ylabel("receita anual bruta mediana (R$, PISO)")
    ax.set_title("Preço x Receita por bairro-quartos (cor = yield líquido)")
    plt.tight_layout(); plt.savefig(OUT / "05_scatter_cross.png", dpi=110); plt.close()
    print("Escrito: outputs/05_scatter_cross.png")
else:
    print("Nenhuma célula cruzada com dados.")