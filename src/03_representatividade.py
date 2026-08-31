"""
03_representatividade.py
Diagnósticos de representatividade antes de qualquer tratamento:
  1. Os 999 listings com preço são representativos dos 4.441?
     (suburb, number_of_bedrooms, listing_type, number_of_reviews)
  2. Listings por captura de Price_AV e sobreposição 07/01 x 20/01
     (subconjunto onde dá para inferir ocupação por desaparecimento de datas)
  3. Intervalo de datas de estadia (min/max) e nº de datas por listing, por captura

Saída: outputs/03_*.csv + prints de diagnóstico.
"""
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data"
OUT = Path(__file__).resolve().parents[1] / "outputs"
OUT.mkdir(exist_ok=True)
ENC = "utf-8-sig"

d = pd.read_csv(DATA / "Details_Itapema.csv", encoding=ENC)
m = pd.read_csv(DATA / "Mesh_Ids_Data_Itapema.csv", encoding=ENC)
p = pd.read_csv(DATA / "Price_AV_Itapema.csv", encoding=ENC)

# janela / captura (normaliza timestamp por dia)
p["captura"] = pd.to_datetime(p["aquisition_date"], errors="coerce", utc=True).dt.normalize()

# join suburb
mesh_sub = m[["airbnb_listing_id", "suburb"]].drop_duplicates("airbnb_listing_id")
d = d.merge(mesh_sub, on="airbnb_listing_id", how="left", validate="one_to_one")

precos_ids = set(p["airbnb_listing_id"])
d["tem_preco"] = d["airbnb_listing_id"].isin(precos_ids)

n_total = len(d)
n_preco = int(d["tem_preco"].sum())
n_sem = n_total - n_preco
print(f"Details: {n_total} | com preço: {n_preco} | sem preço: {n_sem}\n")

def tab(col):
    """% por grupo + chi2 (numpy puro)."""
    ct = pd.crosstab(d[col], d["tem_preco"])
    ct = ct.reindex(columns=[True, False], fill_value=0)  # True primeiro
    pct = ct.div(ct.sum(axis=0), axis=1) * 100
    pct.columns = ["com_preco_%", "sem_preco_%"]
    out = pct.round(1)
    print(f"\n== {col} (% por grupo; com_preco_% = grupo com preço) ==")
    print(out.to_string())
    return ct, out


def chi2_numpy(ct):
    """Chi-quadrado de independência + p-valor, só numpy."""
    import numpy as np

    obs = np.asarray(ct, dtype=float)
    row = obs.sum(axis=1)[:, None]
    col = obs.sum(axis=0)[None, :]
    total = obs.sum()
    if total == 0 or (col.min() == 0):
        return None, None
    exp = (row @ col) / total
    stat = ((obs - exp) ** 2 / exp).sum()
    df = (obs.shape[0] - 1) * (obs.shape[1] - 1)

    # p-valor da chi2 = Q(df/2, stat/2) via gammp (Numerical Recipes)
    def gser(a_, x_, itmax=5000):
        eps = 3e-12
        ap = a_
        s = 1.0 / a_
        d = s
        for _ in range(itmax):
            ap += 1
            d *= x_ / ap
            s += d
            if abs(d) < abs(s) * eps:
                break
        return s * np.exp(-x_ + a_ * np.log(x_) - lgamma(a_))

    def gcf(a_, x_, itmax=500):
        FPMIN = 1e-300
        EPS = 3e-12
        b = x_ + 1 - a_
        c = 1 / FPMIN
        d = 1 / b if b != 0 else FPMIN
        h = d
        for i in range(1, itmax + 1):
            an = -i * (i - a_)
            b += 2
            d = an * d + b
            d = FPMIN if abs(d) < FPMIN else d
            c = b + an / c
            c = FPMIN if abs(c) < FPMIN else c
            d = 1 / d
            de = d * c
            h *= de
            if abs(de - 1) < EPS:
                break
        return np.exp(-x_ + a_ * np.log(x_) - lgamma(a_)) * h

    def gammp(a, x):
        if x < a + 1:
            return 1 - gser(a, x)
        return gcf(a, x)

    p = gammp(df / 2, stat / 2) if stat > 0 else 1.0
    return float(stat), float(p)


def chi(ct, chi2_numpy=chi2_numpy):  # noqa: B008
    import numpy as np
    if ct.shape[0] > 1 and (ct.sum().min() > 0):
        stat, p = chi2_numpy(ct)
        if stat is not None:
            df = (ct.shape[0] - 1) * (ct.shape[1] - 1)
            cramers_v = float(np.sqrt(stat / (ct.to_numpy().sum() * min(ct.shape[0] - 1, ct.shape[1] - 1))))
            return p, stat, df, cramers_v
    return None, None, None, None


def lgamma(x):
    """ln(gamma(x)) via aproximação de Lanczos."""
    import numpy as np
    g = 7
    c = [0.99999999999980993, 676.5203681218851, -1259.1392167224028,
         771.32342877765313, -176.61502916214059, 12.507343278686905,
         -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7]
    z = np.asarray(x, dtype=float)
    if z < 0.5:
        v = np.pi / (np.sin(np.pi * z) * np.exp(lgamma(1 - z)))
        return v
    z -= 1
    x = c[0]
    for i in range(1, g + 2):
        x += c[i] / (z + i)
    t = z + g + 0.5
    return 0.5 * np.log(2 * np.pi) + (z + 0.5) * np.log(t) - t + np.log(x)


colunas_cat = ["suburb", "number_of_bedrooms", "listing_type"]
for col in colunas_cat:
    ct, out = tab(col)
    pv, stat, df, cv = chi(ct)
    if pv is not None:
        print(f"  chi2: stat={stat:.1f} df={df} p={pv:.4g} Cramer's V={cv:.3f}")
    else:
        print("  chi2 indisponível (categoria única ou grupo vazio)")
    # destaque: maiores diferenças relativas
    dif = (out["com_preco_%"] - out["sem_preco_%"]).abs().sort_values(ascending=False).head(5)
    print(f"  maiores diferenças (pp): {dict(dif.round(1))}")
    (out.reset_index()).to_csv(OUT / f"03_{col}_por_grupo.csv", index=False, encoding=ENC)

# number_of_reviews: binned + resumo
print("\n== number_of_reviews (com preço vs sem preço) ==")
for g in [True, False]:
    s = d.loc[d["tem_preco"] == g, "number_of_reviews"]
    label = "com preço" if g else "sem preço"
    print(f"  {label}: n={len(s)} media={s.mean():.1f} mediana={s.median():.0f} "
          f"%zero={(s == 0).mean() * 100:.1f} max={s.max()}")
bins = [-1, 0, 5, 20, 100, s.max() + 1]
lab = ["0", "1-5", "6-20", "21-100", ">100"]
d["rev_bin"] = pd.cut(d["number_of_reviews"], bins=bins, labels=lab)
ct, out = tab("rev_bin")
out.reset_index().to_csv(OUT / "03_reviews_por_grupo.csv", index=False, encoding=ENC)

print("\n==========================================")
print("CAPTURAS DE PRICE_AV")
print("==========================================")
cap_resumo = p.groupby("captura").agg(
    linhas=("price", "size"),
    listings=("airbnb_listing_id", "nunique"),
).sort_index()
print(cap_resumo.to_string())
cap_resumo.to_csv(OUT / "03_capturas_resumo.csv", encoding=ENC)

sets = {cap: set(g["airbnb_listing_id"]) for cap, g in p.groupby("captura")}
caps = sorted(sets)
print("\nSobreposição de listings entre capturas:")
for i in range(len(caps)):
    for j in range(i + 1, len(caps)):
        a, b = caps[i], caps[j]
        inter = len(sets[a] & sets[b])
        print(f"  {a.date()} E {b.date()}: {inter} listings"
              f" ({100 * inter / len(sets[b]):.1f}% da captura mais recente {b.date()})")

todos = set()
for c in caps:
    todos |= sets[c]
tripla = set.intersection(*sets.values())
print(f"\n  em TODAS as 3 capturas: {len(tripla)}")
# captura 07/01 = caps[1], 20/01 = caps[2]  (ordem cronológica)
set0701, set2001 = sets[caps[1]], sets[caps[2]]
print(f"  07/01 E 20/01 (nao necessariamente em 06/01): {len(set0701 & set2001)}")

# ---- Ocupação por desaparecimento ----
print("\nSubconjunto para inferir ocupação por desaparecimento de datas")
print("= listings presentes na captura 07/01 E na 20/01:")
sub_oc = set0701 & set2001
print(f"  {len(sub_oc)} listings")

# ---- intervalo de datas de estadia e nº de datas por listing por captura ----
print("\n==========================================")
print("DATAS DE ESTADIA POR CAPTURA")
print("==========================================")
p["date"] = pd.to_datetime(p["date"], errors="coerce")
contagem = p.groupby(["captura", "airbnb_listing_id"]).agg(
    n_datas=("date", "nunique"),
    d_min=("date", "min"),
    d_max=("date", "max"),
).reset_index()

for cap, g in contagem.groupby("captura"):
    print(f"\n-- Captura {cap.date()} | listings={len(g)}")
    print(f"  intervalo de datas de estadia: {g['d_min'].min().date()} a {g['d_max'].max().date()}")
    print(f"  nº datas por listing: media={g['n_datas'].mean():.1f} "
          f"mediana={g['n_datas'].median():.0f} min={g['n_datas'].min()} max={g['n_datas'].max()}")
    dist = g["n_datas"].value_counts().sort_index()
    print("  distribuição nº de datas (top 15):")
    print("   " + dist.head(15).to_string().replace("\n", "\n   "))

contagem.to_csv(OUT / "03_datas_por_listing_por_captura.csv", index=False, encoding=ENC)
print(f"\nEscrito: outputs/03_*.csv")