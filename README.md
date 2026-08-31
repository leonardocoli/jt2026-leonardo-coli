<LINK_DO_VIDEO_NO_GOOGLE_DRIVE_PENDENTE>

# Hackathon Jovens Talentos AI Builder 2026 — Seazone

**Entrega:** Leonardo Coli · fork de `seazone-tech/jovens-talentos-2026-hackathon-data`, renomeado para `jt2026-leonardo-coli`.

Desafio oficial: [github.com/seazone-tech/jovens-talentos-2026-hackathon-data](https://github.com/seazone-tech/jovens-talentos-2026-hackathon-data)

---

## Como rodar

1. Clone o repositório.
2. Entre em `src/` e rode os scripts/análise (detalhes por script no próprio arquivo).
3. Cada script lê os CSVs de `data/` e grava resultados/figuras em `outputs/`.
4. O dashboard interativo está em `dashboard/` (abra no navegador ou com um servidor estático).

Pré-requisitos: Python 3.11+ e as libs listadas em `src/requirements.txt` (se aplicável).

Requisitos de dados: nenhum download extra — a base já está em `data/` (snapshot oficial do desafio).

---

## Estrutura

```
.
├── README.md                 # este arquivo — link do vídeo na 1ª linha
├── relatorio.md              # análise e recomendação final (inclui posição sobre a tese dos compactos no Centro)
├── data/                     # base oficial do desafio (5 CSVs)
├── src/                      # scripts/consultas/planilhas de apoio
├── outputs/                  # resultados, tabelas e gráficos gerados
├── dashboard/                # dashboard interativo da análise
├── ai-log/                   # conversas com a IA exportadas em texto
└── index.html                # desafio completo (fonte original)
```

---

## Onde está a resposta

- **Recomendação final:** [`relatorio.md`](relatorio.md).
- **Como trabalhei com a IA:** pasta [`ai-log/`](ai-log/) (sessões completas em texto).
- **Dashboard:** [`dashboard/`](dashboard/).

---

## Os dados (`data/`)

Snapshot estático do mercado imobiliário de **Itapema (SC)**, com anúncios de Airbnb e de venda (VivaReal).

| Arquivo | O que tem | Como conecta |
|---|---|---|
| `Details_Itapema.csv` | Cada anúncio de Airbnb: título, reviews, star rating, descrição, host_id, nº de quartos, tipo de imóvel | Base principal dos listings |
| `Hosts_ids_Itapema.csv` | Dados do anfitrião: nº de reviews, anos como host, superhost, taxa de resposta | Liga com Details pelo `owner_id` |
| `Mesh_Ids_Data_Itapema.csv` | Latitude/longitude + bairro de cada anúncio | Liga por listing |
| `Price_AV_Itapema.csv` | Preço por anúncio, por data de estadia e por data de captura | Liga por listing |
| `VivaReal_Itapema.csv` | Anúncios de venda: preço, condomínio, área, vendedor | Mercado de compra |

---

## Regras de avaliação (resumo)

- Repositório **público** (manter até 15/09).
- Recomendação embasada nos dados + posição sobre a tese dos compactos no Centro.
- `ai-log/` com as conversas com a IA em texto (sessão inteira).
- Vídeo de até 3 minutos no Google Drive, sem restrição de acesso.

Mais detalhes no [desafio completo](https://seazone-tech.github.io/jovens-talentos-2026-hackathon-data/) ou no [`index.html`](index.html).