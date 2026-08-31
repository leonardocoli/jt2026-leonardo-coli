<LINK_DO_VIDEO_NO_GOOGLE_DRIVE_PENDENTE>

# Hackathon Jovens Talentos AI Builder 2026 — Seazone

**Entrega:** Leonardo Coli · fork de `seazone-tech/jovens-talentos-2026-hackathon-data`, renomeado para `jt2026-leonardo-coli`.

Desafio oficial: [github.com/seazone-tech/jovens-talentos-2026-hackathon-data](https://github.com/seazone-tech/jovens-talentos-2026-hackathon-data)

---

## Como rodar

1. **Dashboard (recomendado):** abra `dashboard/index.html` direto no navegador — é **self-contained**
   (dados embutidos, abre offline, sem servidor). Todos os gráficos e a recomendação numa página.
2. **Análise completa:** rode os scripts de `src/` em ordem numérica (`01_verificacao_chaves.py` →
   `02_anomalias.py` → `03_representatividade.py` → `04_receita_ocupacao.py` → `05_yield.py` →
   `06_robustez_cenarios.py` → `07_cenarios_adversarios.py` → `08_dashboard_data.py`), com Python 3.11+
   e `pandas` + `matplotlib`.
3. Cada script lê os CSVs de `data/` e grava resultados/figuras em `outputs/`.
4. **Relatório:** `relatorio.md` — metodologia, premissas enumeradas (P1–P16), cenários de estresse e
   a recomendação final (§7).

Pré-requisitos: Python 3.11+ / `pandas` / `matplotlib` (só para rodar `src/`; o dashboard não precisa).

Requisitos de dados: nenhum download extra — a base já está em `data/` (snapshot oficial do desafio).

---

## Estrutura

```
.
├── README.md                 # este arquivo — link do vídeo na 1ª linha
├── relatorio.md              # análise, premissas e recomendação final (inclui veredito da tese dos compactos)
├── data/                     # base oficial do desafio (5 CSVs)
├── src/                      # scripts numerados por ordem de execução
├── outputs/                  # resultados, tabelas e gráficos gerados
├── dashboard/                # dashboard self-contained (abre offline) — index.html
├── ai-log/                   # conversas com a IA exportadas em texto (incl. 05-adversarial.md)
└── index.html                # desafio completo (fonte original)
```

---

## Onde está a resposta

- **Recomendação final:** [`relatorio.md`](relatorio.md) §7 — o entregável do desafio.
- **Veredito da tese dos compactos no Centro:** [`relatorio.md`](relatorio.md) §6.
- **Robustez / cenários de estresse:** [`relatorio.md`](relatorio.md) §5.1 e §5.2.
- **Dashboard (gravar o vídeo):** [`dashboard/index.html`](dashboard/index.html) — abre offline.
- **Sessão adversarial (revisão cética):** [`ai-log/05-adversarial.md`](ai-log/05-adversarial.md).

### Sobre o uso de IA

O trabalho foi feito em parceria com um agente de IA (opencode/Claude Code), com as conversas
completas exportadas em texto em [`ai-log/`](ai-log/). A IA participou de todas as fases — formulação
de premissas, scripts numerados, verificação de chaves/anomalias/representatividade, construção de
receita/ocupação e yield, cenários de estresse, dashboard e redação — sempre com decisão e revisão
humana a cada etapa. Hígino do processo: uma rodada adversarial (`ai-log/05-adversarial.md`) listou os
5 ataques mais fortes às premissas e cada um foi corrigido (ex.: dupla retirada do `cleaning_fee`) ou
registrado como limitação honesta.

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