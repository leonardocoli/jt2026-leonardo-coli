"""
01_verificacao_chaves.py
Verifica chaves, duplicatas e sobrevivência a cada join entre as 5 tabelas
do desafio (Itapema/SC). Gera:
  - outputs/01_resumo_joins.csv   (chaves + sobrevivência)
  - outputs/01b_duplicatas_price.csv (pares listing,date repetidos)
  - prints com diagrama textual de conexão

Chaves identificadas:
  - Details.airbnb_listing_id <-> Mesh.airbnb_listing_id
  - Details.airbnb_listing_id <-> Price_AV.airbnb_listing_id
  - Details.owner_id          <-> Hosts.owner_id
  - VivaReal: sem chave de anúncio — conecta por bairro/região (suburb)
"""
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data"
OUT = Path(__file__).resolve().parents[1] / "outputs"
OUT.mkdir(exist_ok=True)

ENC = "utf-8-sig"
FILES = {
    "Details": "Details_Itapema.csv",
    "Hosts": "Hosts_ids_Itapema.csv",
    "Mesh": "Mesh_Ids_Data_Itapema.csv",
    "Price_AV": "Price_AV_Itapema.csv",
    "VivaReal": "VivaReal_Itapema.csv",
}
tables = {n: pd.read_csv(DATA / f, encoding=ENC) for n, f in FILES.items()}

for name, df in tables.items():
    print(f"== {name}: {len(df)} linhas, {df.shape[1]} colunas ==")

def check_dup(label, df, col):
    uniq = df[col].nunique()
    dup_rows = df[col].duplicated(keep=False).sum()
    print(f"  [{label}] {col}: únicos={uniq}, linhas em duplicatas={dup_rows}")
    return uniq

print("\n===== Duplicatas nas chaves =====")
d, h, m, p, v = tables["Details"], tables["Hosts"], tables["Mesh"], tables["Price_AV"], tables["VivaReal"]
check_dup("Details", d, "airbnb_listing_id")
check_dup("Details", d, "owner_id")
check_dup("Mesh", m, "airbnb_listing_id")
check_dup("Price_AV", p, "airbnb_listing_id")
check_dup("Hosts", h, "owner_id")
check_dup("VivaReal", v, "listing_id")

# Duplicatas exatas em Price_AV
dups_exatas = p.duplicated(keep=False).sum()
pares = p.groupby(["airbnb_listing_id", "date"]).size()
print(f"\n  Price_AV: duplicatas EXATAS = {dups_exatas}")
print(f"  Price_AV: pares (listing, date) únicos = {pares.size}; linhas = {len(p)}")
print(f"  Price_AV: nº de capturas por par (listing,date):")
for k, val in pares.value_counts().sort_index().items():
    print(f"    {k} capturas: {val} pares")

# Janelas de captura
aq = pd.to_datetime(p["aquisition_date"], utc=True).dt.normalize()
print(f"\n  Price_AV: janelas de captura (dia): {sorted(aq.dropna().astype(str).unique())}")

# Preço varia entre capturas?
variacao = p.groupby(["airbnb_listing_id", "date"], sort=True, as_index=False).agg(
    n_capturas=("price", "size"), n_precos=("price", "nunique")
)
print(f"  Price_AV: pares em que preço varia entre capturas = {(variacao['n_precos']>1).sum()}")

print("\n===== Sobrevivência a cada join (em listings únicos de Details) =====")
detail_ids = set(d["airbnb_listing_id"].dropna().unique())
owner_ids = set(d["owner_id"].dropna().unique())
mesh_ids = set(m["airbnb_listing_id"].dropna().unique())
price_lids = set(p["airbnb_listing_id"].dropna().unique())
host_owners = set(h["owner_id"].dropna().unique())

def surv(label, s):
    n = sum(1 for x in detail_ids if x in s)
    print(f"  {label}: {n}/{len(detail_ids)} ({100*n/len(detail_ids):.1f}%)")
    return n

in_mesh = surv("Details x Mesh     (airbnb_listing_id)", mesh_ids)
in_price = surv("Details x Price_AV (listings com preço)", price_lids)
in_both = surv("Details x (Mesh E Price_AV)", mesh_ids & price_lids)
in_any = surv("Details x (Mesh OU Price_AV)", mesh_ids | price_lids)

matched_owner = sum(1 for o in owner_ids if o in host_owners)
print(f"  Details.owner_id em Hosts: {matched_owner}/{len(owner_ids)} ({100*matched_owner/len(owner_ids):.1f}%)")

print("\n===== Diagrama textual de conexão =====")
print(f"""
                    Itapema/SC — snapshot
                                          |
   +----------------+  airbnb_listing_id  +---------------------+
   |  Mesh (geo)    |<------------------- |      Details        |
   |  {len(mesh_ids)} listings |                    |  {len(detail_ids)} listings (1x1) |
   +----------------+                     +---------------------+
                                              | airbnb_listing_id  | owner_id
                                              v                    v
                              +----------------------+   +------------------+
                              | Price_AV (preço/dia) |   | Hosts (anfitrião)|
                              | {len(price_lids)} listings |   | {len(host_owners)} owners |
                              | {len(p)} linhas (3 capturas)|   | (1x1 por owner)  |
                              +----------------------+   +------------------+
    Sem chave comum:
    VivaReal (compra) {len(v)} anúncios — conecta por suburb/bairro (mercado de compra)
""")

lilas = {
    "Linhas_Details": len(d), "Listings_unicos_Details": len(detail_ids),
    "Listings_em_Mesh": in_mesh, "Listings_em_Price_AV": in_price,
    "Listings_em_Mesh_E_Price": in_both, "Listings_em_Mesh_OU_Price": in_any,
    "Owner_Details_em_Hosts": matched_owner, "Owners_Details_unicos": len(owner_ids),
    "Linhas_Price_AV": len(p), "Pares_Price_AV_unicos": int(len(pares)),
    "Linhas_Hosts": len(h), "Linhas_Mesh": len(m), "Linhas_VivaReal": len(v),
    "Janelas_captura_Price_AV": sorted(aq.dropna().astype(str).unique()).__str__(),
}
(pd.DataFrame([lilas])).to_csv(OUT / "01_resumo_joins.csv", index=False, encoding="utf-8-sig")
print("Escrito: outputs/01_resumo_joins.csv")