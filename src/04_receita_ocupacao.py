"""
04_receita_ocupacao.py
Estimadores de ocupação e receita (premissas P1-P16 aprovadas).

E1 - Ocupação por faixa de lead (headline = lead<=15; sensibilidade <=30; curva de estabilização)
E2 - Ritmo de reserva entre capturas 07/01 e 20/01 (janela comparável [20/01, 07/04])
ADR vendido x ADR disponível (P13)
ADR mensal jan..abr (P14) + receita observada dos 91 dias + anualização ilustrativa
Cleaning fee fora da receita líquida (P11); min_nights caveat (P10)

Outputs: outputs/04_*.csv + outputs/04_*.png
"""
from pathlib import Path
import numpy as np, pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data"
OUT = Path(__file__).resolve().parents[1] / "outputs"
ENC = "utf-8-sig"

p = pd.read_csv(DATA / "Price_AV_Itapema.csv", encoding=ENC)
d = pd.read_csv(DATA / "Details_Itapema.csv", encoding=ENC)
m = pd.read_csv(DATA / "Mesh_Ids_Data_Itapema.csv", encoding=ENC)

p["cap"] = pd.to_datetime(p["aquisition_date"], utc=True).dt.tz_localize(None).dt.normalize()
p["date"] = pd.to_datetime(p["date"], errors="coerce")

mesh = m[["airbnb_listing_id", "suburb"]].drop_duplicates("airbnb_listing_id")
d = d.merge(mesh, on="airbnb_listing_id", how="left")

CAP20 = pd.Timestamp("2025-01-20")
CAP7 = pd.Timestamp("2025-01-07")
W0, W1 = pd.Timestamp("2025-01-20"), pd.Timestamp("2025-04-07")
HORIZ = 91  # dias do horizonte de cada captura

# ---------------------------------------------------------------- E1
print("=" * 70)
print("E1 - OCUPACAO POR FAIXA DE LEAD (captura 20/01)")
print("=" * 70)
g20 = p[p["cap"] == CAP20].copy()
g20["lead"] = (g20["date"] - CAP20).dt.days
buckets = [(0, 15), (16, 30), (31, 45), (46, 60), (61, 75), (76, 90)]
labels = ["0-15", "16-30", "31-45", "46-60", "61-75", "76-90"]

n_list = g20["airbnb_listing_id"].nunique()
linhas_e1 = []
for (b0, b1), lb in zip(buckets, labels):
    total = n_list * (b1 - b0 + 1)
    avail = int(((g20["lead"] >= b0) & (g20["lead"] <= b1)).sum())
    occ = 1 - avail / total
    linhas_e1.append((lb, avail, total, occ))
    print(f"  lead {lb:5s}: {avail:5d} dias disponiveis / {total:5d}   ocupacao={occ:.3f}")
e1 = pd.DataFrame(linhas_e1, columns=["lead", "avail", "total", "ocupacao"])
e1.to_csv(OUT / "04_e1_lead.csv", index=False, encoding=ENC)

occ_15 = e1.loc[e1["lead"] == "0-15", "ocupacao"].iloc[0]
occ_30 = 1 - e1.loc[e1["lead"].isin(["0-15", "16-30"]), ["avail", "total"]].sum().pipe(
    lambda s: s["avail"] / s["total"]
)
print(f"\n  HEADLINE ocupacao realizada (lead<=15): {occ_15:.3f}")
print(f"  SENSIBILIDADE (lead<=30): {occ_30:.3f}")

# delta da curva: apontar o repique no fim (2025: Pascoa = 20/04 -> leads 76-90)
print("  dinâmica entre buckets (delta de ocupacao):")
for i in range(1, len(e1)):
    dd = e1["ocupacao"].iloc[i] - e1["ocupacao"].iloc[i-1]
    nota = "  <-- Semana Santa (06-20/04)" if e1['lead'].iloc[i] == "76-90" else ""
    print(f"    {e1['lead'].iloc[i-1]} -> {e1['lead'].iloc[i]}: {dd:+.3f}{nota}")
print("  -> a queda e monotonica ate ~0.19 (61-75); o repique em 76-90 (+0.04) e a Semana Santa,"
      "\n     nao estabilizacao da base. Headline (lead<=15) mede ALTA temporada realizada.")

# ocupacao per-listing no lead<=15 (realizada por imóvel)
# Opcao A (aprovada): incluir os 308 sem datas no lead 0-15 como 1.0 (totalmente ocupados/bloqueados)
avail15 = g20[g20["lead"] <= 15].groupby("airbnb_listing_id")["date"].nunique()
base_n = g20["airbnb_listing_id"].nunique()
com_dado = avail15.index
occ_le15_serie = pd.Series(1.0, index=g20["airbnb_listing_id"].unique())
occ_le15_serie[com_dado] = 1 - avail15.reindex(com_dado) / 16
print(f"\n  ocupacao<=15 por listing (n={base_n} de {base_n}, 308 sem datas no lead curto = 1.0):")
print(f"    media={occ_le15_serie.mean():.3f} mediana={occ_le15_serie.median():.3f}")

# perfil forward de ocupacao na captura (ponderado por dias dos buckets) para a receita 91d
dias_bucket = [16, 15, 15, 15, 15, 15]
fwd_occ = (e1["ocupacao"] * dias_bucket).sum() / sum(dias_bucket)
print(f"  ocupacao forward media dos 91d (peso por bucket): {fwd_occ:.3f}  <- PISO")
print(f"  alta temporada realizada (lead<=15): {occ_15:.3f}  <- medida em paralelo")

# ---------------------------------------------------------------- E2
print("\n" + "=" * 70)
print("E2 - RITMO DE RESERVA 07/01 -> 20/01 (janela comparavel)")
print("=" * 70)

def sets(cap_, w0=W0, w1=W1):
    df = p[(p["cap"] == cap_) & (p["date"] >= w0) & (p["date"] <= w1)]
    return {k: set(map(pd.Timestamp, gg["date"])) for k, gg in df.groupby("airbnb_listing_id")}

s7, s20 = sets(CAP7), sets(CAP20)
base = [k for k in s7 if k in s20]
print(f"base listings (07/01 e 20/01) na janela {W0.date()}..{W1.date()}: {len(base)}")

som = np.array([len(s7[k] - s20[k]) for k in base])
nov = np.array([len(s20[k] - s7[k]) for k in base])
exp = np.array([len(s7[k]) for k in base])
dias = 13
rate = som.sum() / exp.sum() / dias  # data/(listing.dia exposto)
print(f"  datas expostas em 07/01: media={exp.mean():.1f} mediana={np.median(exp):.0f}")
print(f"  SOMEM em {dias} dias: media={som.mean():.2f} mediana={np.median(som):.0f} total={som.sum()}"
      f" ({100*som.sum()/exp.sum():.1f}% do exposto)")
print(f"  NOVAS (novas datas apareceram): total={nov.sum()} media={nov.mean():.2f}")
print(f"  LIQUIDO (som-nov): media={(som-nov).mean():.2f}")
print(f"  listings sem NENHUMA data somando: {100*(som==0).mean():.1f}%")
print(f"  RITMO = {rate:.4f} datas/(listing.dia exposto)")
pd.DataFrame({"listings": [len(base)], "rate_por_dia": [rate],
              "somem_total": [int(som.sum())], "novas_total": [int(nov.sum())],
              "pct_listings_0_somem": [float((som == 0).mean())]}).to_csv(
    OUT / "04_e2_ritmo.csv", index=False, encoding=ENC)

# curva de lead de reserva (somem por lead, relativo a 07/01)
lead_hits = {}
for k in base:
    for dt in s7[k] - s20[k]:
        b = (dt - CAP7).days // 15
        lead_hits[b] = lead_hits.get(b, 0) + 1
print("  somem por lead (dias ate a estadia, 07/01):")
for b in sorted(lead_hits):
    print(f"    lead {b*15:3d}-{b*15+14:3d}: {lead_hits[b]}")

# ------------------------------------------------- ADR vendido x disponivel (P13)
print("\n" + "=" * 70)
print("ADR VENDIDO x ADR DISPONIVEL (P13)")
print("=" * 70)
p7 = p[(p["cap"] == CAP7) & (p["date"] >= W0) & (p["date"] <= W1)]
p20 = p[(p["cap"] == CAP20) & (p["date"] >= W0) & (p["date"] <= W1)]
merg = []
for k in base:
    vend = (s7[k] - s20[k])
    disp = s20[k]
    if vend:
        pv = p7[(p7["airbnb_listing_id"] == k) & (p7["date"].isin(vend))]["price"]
        merg.append(("vendido", pv.mean()))
    if disp:
        pd_ = p20[(p20["airbnb_listing_id"] == k) & (p20["date"].isin(disp))]["price"]
        merg.append(("disponivel", pd_.mean()))
mad = pd.DataFrame(merg, columns=["tipo", "adr"])
print(mad.groupby("tipo")["adr"].agg(["count", "mean", "median"]).round(1).to_string())
mad.groupby("tipo")["adr"].agg(["count", "mean", "median"]).to_csv(
    OUT / "04_adr_vendido_vs_disponivel.csv", encoding=ENC)

# ------------------------------------------------- ADR mensal + receita (P12/P14)
print("\n" + "=" * 70)
print("ADR MENSAL (jan..abr) e RECEITA dos 91 dias")
print("=" * 70)
g20["mes"] = g20["date"].dt.month_name(locale="pt_BR")
g20["mes"] = g20["date"].dt.month.map({1: "jan", 2: "fev", 3: "mar", 4: "abr"})
adr_mensal = g20.groupby("mes")["price"].agg(["count", "mean", "median"])
print(adr_mensal.round(1).to_string())
adr_mensal.to_csv(OUT / "04_adr_mensal.csv", encoding=ENC)

# base para receita: TODOS os listings da captura 20/01 (780)
adr_media = g20.groupby("airbnb_listing_id")["price"].mean()
n_datas = g20.groupby("airbnb_listing_id")["date"].nunique()
rec = pd.DataFrame({
    "airbnb_listing_id": adr_media.index.values,
    "adr": adr_media.values,
    "n_datas_91d": n_datas.reindex(adr_media.index).values,
})
rec["occ_le15"] = occ_le15_serie.reindex(rec["airbnb_listing_id"]).values
rec["occ_forward_piso"] = fwd_occ
rec["receita_91d_piso"] = rec["adr"] * HORIZ * rec["occ_forward_piso"]
rec["receita_91d_teto"] = rec["adr"] * HORIZ * rec["occ_le15"]

# anualizacao ilustrativa (P14): so ADR da sazonalidade, ocupacao por mes conflunde ombro x lead
adr_alta = adr_mensal.loc[["jan", "fev"], "mean"].mean()
adr_ombro = adr_mensal.loc[["mar", "abr"], "mean"].mean()
dias_rest = 365 - HORIZ
for suf, occ_col in [("piso", "occ_forward_piso"), ("teto", "occ_le15")]:
    rec[f"rec_anual_ombro_{suf}"] = rec[f"receita_91d_{suf}"] + adr_ombro * dias_rest * rec[occ_col]
    rec[f"rec_anual_alta_{suf}"] = rec[f"receita_91d_{suf}"] + adr_alta * dias_rest * rec[occ_col]
print(f"\n  ADR alta (jan-fev)={adr_alta:.0f}  ADR ombro (mar-abr)={adr_ombro:.0f}  "
      f"-> fator restante ano={adr_ombro/adr_alta:.2f}")
print(f"  receita 91d PISO (occ_forward={fwd_occ:.3f}): media={rec['receita_91d_piso'].mean():.0f} "
      f"mediana={rec['receita_91d_piso'].median():.0f}")
print(f"  receita 91d TETO (occ_le15={occ_le15_serie.mean():.3f}): media={rec['receita_91d_teto'].mean():.0f} "
f"mediana={rec['receita_91d_teto'].median():.0f}")
print(f"  anual (ilustrativa) PISO media: [{rec['rec_anual_ombro_piso'].mean():.0f}, {rec['rec_anual_alta_piso'].mean():.0f}]")
print(f"  anual (ilustrativa) TETO media: [{rec['rec_anual_ombro_teto'].mean():.0f}, {rec['rec_anual_alta_teto'].mean():.0f}]")
rec.to_csv(OUT / "04_receita.csv", index=False, encoding=ENC)

# receita por segmento (P16: n explicito; 5Q+ aparte como nao conclusivo)
seg = rec.merge(d[["airbnb_listing_id", "suburb", "listing_type", "number_of_bedrooms"]],
                on="airbnb_listing_id", how="left")
for col in ["suburb", "listing_type", "number_of_bedrooms"]:
    t = seg.groupby(col)["receita_91d_piso"].agg(["count", "mean", "median"]).round(0).reset_index()
    t.columns = [col, "n", "receita_91d_piso_media", "receita_91d_piso_mediana"]
    if col == "suburb":
        t = t[t["n"] >= 30]
    if col == "number_of_bedrooms":
        principal = t[t[col] <= 4]
        aparte = t[t[col] > 4]
        print(f"\n  receita 91d piso por {col} (0-4Q; n explicito):")
        print(principal.to_string(index=False))
        print(f"  -> 5Q+ (n<30 por nivel) NAO CONCLUSIVO:")
        print(aparte.to_string(index=False))
        principal.to_csv(OUT / f"04_receita_por_{col}.csv", index=False, encoding=ENC)
        continue
    print(f"\n  receita 91d piso por {col} (n>=30 p/ suburb, n explicito):")
    print(t.to_string(index=False))
    t.to_csv(OUT / f"04_receita_por_{col}.csv", index=False, encoding=ENC)

# ------------------------------------------------- figuras
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"figure.figsize": (9, 4.5), "axes.grid": True, "grid.alpha": 0.3})

# 1. curva ocupacao x lead (com Semana Santa anotada)
plt.figure()
plt.plot(e1["lead"], e1["ocupacao"], marker="o")
plt.axvline(0.5, color="r", ls=":", alpha=0.6); plt.axvline(2.5, color="orange", ls=":", alpha=0.6)
plt.axvline(len(e1) - 0.5, color="purple", ls=":", alpha=0.6)
plt.annotate("Semana Santa\n(06-20/04)", xy=(len(e1) - 1, e1["ocupacao"].iloc[-1]),
             xytext=(len(e1) - 2.2, e1["ocupacao"].iloc[-1] + 0.06), fontsize=8, color="purple")
plt.title("Ocupacao forward por faixa de lead (captura 20/01)")
plt.xlabel("lead (dias)"); plt.ylabel("ocupacao")
plt.xticks(range(len(e1)), e1["lead"])
plt.tight_layout(); plt.savefig(OUT / "04_curva_lead.png", dpi=110); plt.close()

# 2. ADR mensal (ordem cronologica jan..abr)
plt.figure()
ordem = ["jan", "fev", "mar", "abr"]
ax = plt.bar(ordem, adr_mensal.loc[ordem, "mean"])
plt.bar_label(ax, fmt="R$ %.0f")
plt.title("ADR medio mensal (captura 20/01)"); plt.ylabel("R$")
plt.tight_layout(); plt.savefig(OUT / "04_adr_mensal.png", dpi=110); plt.close()

# 3. distribuicao receita 91d por listing (piso e alta em paralelo)
plt.figure()
plt.hist(rec["receita_91d_piso"], bins=40, alpha=0.6, label="PISO (forward 0.408)", edgecolor="white")
plt.hist(rec["receita_91d_teto"], bins=40, alpha=0.4, label="TETO (lead<=15)", edgecolor="white")
plt.title("Distribuicao da receita dos 91 dias por listing (piso vs alta)")
plt.xlabel("R$"); plt.ylabel("listings"); plt.legend()
plt.tight_layout(); plt.savefig(OUT / "04_histor_receita.png", dpi=110); plt.close()

print("\nEscrito: outputs/04_*.csv e outputs/04_*.png")