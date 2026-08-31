# Relatório — Recomendação de Investimento em Itapema (SC)

**Autor:** Leonardo Coli · **Hackathon Jovens Talentos AI Builder 2026 — Seazone**

> Documento em construção. Esta será a recomendação final escrita, com posição sobre a tese
> dos compactos (studio/1 quarto) no Centro.

---

## 1. Objetivo

Recomendar o melhor investimento imobiliário para a Seazone em Itapema (SC), com base no
snapshot de anúncios de Airbnb (oferta de short stay) e VivaReal (mercado de compra).

## 2. Perguntas respondidas

1. Qual o **melhor perfil de imóvel** para investir? (tipologia, nº de quartos, tipo de anúncio)
2. Qual a **melhor localização** em termos de receita?
3. Quais **características explicam** as melhores receitas?
4. Se a Seazone investisse hoje, **o que compraria e por quê?** — com estimativa simples de retorno.

## 3. Metodologia

### 3.1 Premissas de dados e junções (verificação de chaves — script `src/01_verificacao_chaves.py`)

| Tabela | Linhas | Chave | Observações |
|---|---|---|---|
| `Details` | 4.441 | `airbnb_listing_id` (única; 3.057 `owner_id` únicos; listagem com dono com até 112 anúncios) | Base principal dos listings de Airbnb |
| `Mesh` | 4.441 | `airbnb_listing_id` (única) | Geografia (subúrbio/bairro); join 1:1 com Details = **100%** dos listings |
| `Price_AV` | 118.839 | `airbnb_listing_id` + `date` + `aquisition_date` | **Formato longo**: preço por anúncio, por data de estadia e por **data de captura** (3 janelas: 06/01, 07/01 e 20/01/2025). Sem duplicatas exatas. 59.040 pares (listing, date) únicos: 25.452 com 1 captura,  7.377 com 2,  26.211 com 3. Em 15.617 pares o preço **varia entre capturas** → decidir qual janela usar |
| `Hosts` | 4.440 | `owner_id` (3.057 únicos) | Join 1:1 com `Details.owner_id` = **100%** dos owners de Details presentes |
| `VivaReal` | 8.329 | `listing_id` (8.293 únicos; 36 duplicados) | **Sem chave comum** com as tabelas de Airbnb — conecta por `suburb` (bairro), representando o **mercado de compra** |

Sobrevivência por join (em listings únicos de Details, **4.441**):

- `Details x Mesh`: **4.441/4.441 (100%)** — join completo.
- `Details x Price_AV` (listings com preço): **999/4.441 (22,5%)**.
- `Details x (Mesh E Price_AV)`: **999/4.441 (22,5%)**.
- `Details x (Mesh OU Price_AV)`: **4.441/4.441 (100%)** — todo listing tem geo, mas só 22,5% tem preço.
- `Details.owner_id x Hosts`: **100%** dos owners casam.

**Implicações para a análise:** a análise de **receita** (preço) fica restrita aos **999 listings** com preço; a análise de **perfil/localização** pode usar os 4.441 listings com geografia. VivaReal entra pelo bairro para estimar custo de aquisição/retorno.

### 3.2 Representatividade dos 999 listings com preço (diagnóstico — script `src/03_representatividade.py`)

> Escopo: antes de aplicar qualquer tratamento, verificamos se quem tem preço é representativo
> da oferta total (4.441). Outputs em `outputs/03_*`.

#### a) Distribuições: com preço (n=999) vs sem preço (n=3.442)

**`suburb`** — chi² p=4.3e-07, V=0.115 (diferença relevante):

| Bairro | com preço % | sem preço % | dif (pp) |
|---|---|---|---|
| Centro | 20,5 | 13,1 | **+7,4** (super-representado) |
| Morretes | 8,3 | 10,4 | −2,1 |
| Meia Praia | 63,3 | 64,7 | −1,4 |
| Tabuleiro dos Oliveiras | 2,0 | 3,2 | −1,2 |
| Alto São Bento | 0,5 | 1,7 | −1,2 |

**`number_of_bedrooms`** — chi² p=0,31 (sem diferença significativa). Destaques: 1Q 14,4% vs 11,8%; 3Q 40,4% vs 44,1%.

**`listing_type`** — chi² p=6.6e-14, V=0.12 (diferença marcante):

| Tipo | com preço % | sem preço % |
|---|---|---|
| apartamento | **91,2** | 81,3 |
| casa | 7,0 | 10,8 |
| hotel | 0,1 | 1,2 |
| outros | 1,7 | 6,6 |

**`number_of_reviews`** — o viés mais forte:

| Grupo | n | média | mediana | % zerados |
|---|---|---|---|---|
| com preço | 999 | 27,1 | 16 | 2,2% |
| sem preço | 3.442 | 3,8 | 1 | 44,1% |

**Conclusão de representatividade:** ter preço é um **proxy de listing ativo/anunciante profissional**. O grupo com preço pende para **Centro** e **apartamentos**, e é composto majoritariamente por anúncios **com histórico de reviews**. As conclusões de **receita valem para o segmento ativo**, não para toda a oferta — ao afirmar "melhor localização/perfil", deixar explícito que o universo é o de listings ativos com precificação.

#### b) Capturas de `Price_AV` e subconjunto para inferir ocupação

| Captura | Lines | Listings |
|---|---|---|
| 06/01 | 37.825 | 753 |
| 07/01 | 38.991 | 773 |
| 20/01 | 42.023 | 780 |

Sobreposição de listings: 06∩07 = 642; 06∩20 = 630; **07∩20 = 657** (84,2% da captura de 20/01). Em **todas as 3 capturas** = 628.

**Onde dá para inferir ocupação por desaparecimento de datas:** listings presentes em **07/01 E 20/01 = 657 listings** (66% dos 999 com preço). A inferência se baseia nas datas de estadia que existiam em 07/01 e não aparecem mais em 20/01 (janela de 13 dias entre capturas).

#### c) Datas de estadia por captura

| Captura | Intervalo datas | nº datas/listing (média) | mediana | min | max |
|---|---|---|---|---|---|
| 06/01 | 06/01 → 06/04 | 50,2 | 53 | 2 | 91 |
| 07/01 | 07/01 → 07/04 | 50,4 | 53 | 2 | 91 |
| 20/01 | 20/01 → 20/04 | 53,9 | 58 | 2 | 91 |

Horizonte **fixo de ~3 meses a partir da captura**; cada listing lista entre 2 e 91 datas (média ~50–54).

## 4. Principais achados

### 4.1 Ocupação e receita (script `src/04_receita_ocupacao.py`, outputs `outputs/04_*`)

> Decisão metodológica (P2): `Price_AV` só lista datas **disponíveis**; ausente = indisponível.

#### Ocupação por faixa de lead (captura 20/01, base 780)

| Lead | Disponíveis/Total | Ocupação |
|---|---|---|
| 0–15 | 2.906/12.480 | **0,767** |
| 16–30 | 5.132/11.700 | 0,561 |
| 31–45 | 7.362/11.700 | 0,371 |
| 46–60 | 8.198/11.700 | 0,299 |
| 61–75 | 9.455/11.700 | 0,192 |
| 76–90 | 8.970/11.700 | 0,233 |

- **Alta temporada realizada (lead ≤15): 0,767** — é medida de **alta** (datas próximas da captura, 20/01→04/02), não da média do horizonte.
- **Sensibilidade (lead ≤30): 0,668.**
- **Estabilização:** queda monótona até 0,19 (61–75). O **repique em 76–90 (+0,04) é a Semana Santa (06–20/04)**, não estabilização — anotado no console e figura.
- **Ocupação por listing (lead ≤15):** dos 780, **308 não listam datas no lead curto** (presumivelmente ocupados/bloqueados/full) → tratados como **1,0**. Com isso: **média 0,767, mediana 0,875** (n=780).
- **Piso da ocupação média dos 91 dias:** **0,408** (forward ponderado por bucket, excluindo o repique de feriado). Alta (lead≤15) 0,767 mantida em paralelo.

#### Ritmo de reserva — E2 (07/01→20/01, janela comparável [20/01,07/04], base 654)

- Datas expostas méd. 49,5/listing; **somem 6,38** em 13 dias (12,9% do exposto); aparecem 1,31 → líquido +5,06.
- **35,5% dos listings sem nenhuma data somando** (heterogeneidade).
- Curva de lead de reserva: pico em **lead 15–44 dias** (1.260 + 1.069 somem), pouco em 0–14 (173).
- **Ritmo = 0,0099 datas/(listing·dia exposto)** — usado como pacing/validação, **sem** extrapolação constante para nível.

#### ADR: vendido × disponível (P13)

| | n | ADR médio | Mediana |
|---|---|---|---|
| Disponíveis (sobraram) | 654 | 663,3 | 593,7 |
| **Vendidas (somem)** | 422 | **724,5** | 689,2 |

Noites vendidas ~9% mais caras que as disponíveis → reserva-se em datas premium; usar apenas o disponível subestima o ADR de venda.

#### Receita dos 91 dias (métrica principal) e anualização ilustrativa

| Cenário | Ocupação | Receita 91d média | mediana | Anual ilustrativa (média) |
|---|---|---|---|---|
| **Piso** | forward 0,408 | **R$ 24.260** | R$ 21.155 | R$ 92.707 – R$ 113.217 |
| **Teto** | lead≤15 0,767 | R$ 43.532 | R$ 38.668 | R$ 172.243 – R$ 210.811 |

- **Métrica principal = receita observada dos 91 dias**; anualização é **faixa ilustrativa** (sem fatores inventados).
- **Sazonalidade = só ADR por mês** (jan 828 → fev 763 → mar 652 → abr 573). Alta (jan–fev) = 796; ombro (mar–abr) = 612 → **fator do restante do ano = 0,77**, **uniforme para todos os segmentos** → o ranking independe dele.
- **Limitação:** ocupação por mês NÃO é isolada (ombro confunde com lead) — não a usamos mensalmente.

#### Receita 91d (piso) por segmento — n explícito

**Bairro (n≥30):**

| Bairro | n | Média | Mediana |
|---|---|---|---|
| Meia Praia | 483 | 24.916 | 22.572 |
| Centro | 180 | 21.884 | 19.836 |
| Morretes | 66 | 25.478 | 18.846 |

**Tipo:** apartamento (n=737) 24.100 / 21.262 · casa (n=33) 31.298 / 19.203 · outros (n≤30, não conclusivo).

**Quartos (0–4Q; 5Q+ não conclusivo por n<30):**

| Quartos | n | Média | Mediana |
|---|---|---|---|
| 0 (estúdio) | 7 | 16.428 | 16.081 |
| 1 | 110 | 16.787 | 16.508 |
| 2 | 262 | 20.144 | 17.876 |
| 3 | 340 | 26.296 | 25.845 |
| 4 | 53 | 42.950 | 37.108 |
| 5+ | <30 | — | — (não conclusivo) |

**Outliers:** não excluídos; 5Q+ reportados à parte como não conclusivos.

## 5. Investimento: yield por segmento (Airbnb × VivaReal — script `src/05_yield.py`)

> **Limitação crítica:** as duas bases são de **imóveis diferentes** — não há join por imóvel.
> O yield é de **perfil médio**: compra-se "um imóvel de Q quartos no bairro B" ao preço mediano
> do VivaReal e opera-se short stay à receita mediana PISO dos anúncios Airbnb da mesma célula.

**Premissas do yield:**
- **Base = receita BRUTA** (`rec_anual_ombro_piso`, PISO anualizada, fator 0,77 derivado) — coluna `receita anual` na tabela para auditar o yield.
- **Deduções:** condomínio (mediana só entre reportados >0, ×12) + IPTU (mediana real >0) + **custo operacional 15%** da receita bruta (limpeza/manutenção/vacância).
- **Administração (−20% da receita bruta):** apenas na coluna de sensibilidade `yield_liq_adm`.
- **n≥30 em ambos os lados = conclusiva; n entre 10–29 em ambos = indicativo (marcado `*`); n<10 ou sem preço = NC.**
- **0Q (studio) incluído** na tabela; só apartamentos (oferta e compra).

### Yield por **bairro × quartos** (apartamento; ADR/ocupação por célula; `*` = indicativo)

> **Receita recalculada por célula (fórmula final):**
> `receita_91d = ADR_célula × 91 × (0,408 × occ_le15_célula ÷ occ_le15_global)` com `occ_le15_global = 0,776`
> **Anual = receita_91d + ADR_célula × 0,77 × 274 × occ_forward_célula** — o fator sazonal **escala o ADR da célula**, não o substitui.

| Bairro | Q | n_ab | n_vr | ADR (med) | Ocup. alta | Receita anual bruta | Preço mediano | R$/m² | **Bruto** | **Líquido** | Líq. −20% adm |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Centro | 0 | 0 | 0 | — | — | — | — | — | NC | NC | NC |
| Centro | 1 | 75 | 22 | 455 | 0,81 | 58.679 | 890 mil | 14.574 | 6,59%* | 4,82%* | 3,50%* |
| Centro | 2 | 59 | 89 | 643 | 0,81 | 82.877 | 1,15 mi | 13.068 | 7,21% | 5,52% | 4,08% |
| Centro | 3 | 38 | 438 | 735 | 0,91 | 105.705 | 2,10 mi | 15.789 | 5,03% | 3,86% | 2,86% |
| Centro | 4 | 1 | 436 | 629 | 1,00 | — | 3,90 mi | 18.890 | NC | NC | NC |
| Meia Praia | 1 | 16 | 58 | 484 | 0,91 | 69.613 | 877 mil | 21.250 | 7,93%* | 5,63%* | 4,23%* |
| Meia Praia | 2 | 126 | 244 | 474 | 0,97 | 72.873 | 1,08 mi | 12.929 | 6,78% | 5,11% | 3,87% |
| Meia Praia | 3 | 284 | 1.704 | 693 | 0,88 | 96.213 | 1,88 mi | 14.957 | 5,10% | 3,88% | 2,87% |
| Meia Praia | 4 | 44 | 1.408 | 980 | 0,88 | 136.136 | 3,70 mi | 18.617 | 3,68% | 2,74% | 2,01% |
| **Morretes** | **2** | 43 | 1.044 | 465 | 0,81 | 59.986 | 790 mil | 11.551 | 7,59% | **5,83%** | **4,27%** |
| Tabuleiro dos Oliveiras | 2 | 12 | 106 | 440 | 0,81 | 56.726 | 782 mil | 11.502 | 7,25% | 5,52% | 4,08% |

> Ocupação = `occ_le15` (alta temporada realizada, lead≤15; zero datas no lead curto = 1,0). Outras células (Casa Branca, Canto da Praia, Ilhota, Alto São Bento) têm n<10 no lado Airbnb → NC (detalhe em `outputs/05_yield_cross.csv`).

**Sobre o ADR × nº de quartos (confirmação):** **o ADR varia sim com quartos** — mediana global (apartamentos): 1Q 456 → 2Q 489 → 3Q 696 → 4Q 964. O que é verdadeiro é que **1Q e 2Q têm ADR próximos** (456 vs 489, +7%) apesar de preços de compra bem diferentes por localização. A "receita quase igual entre 1Q/2Q" vem de ADR 1Q≈2Q e ocupação semelhante. Não é artefato.

**Leitura (por célula, sem confundir composição com localização):**
- **Top 5 é quase um empate técnico:** Morretes-2Q (5,83%), Meia Praia-1Q (5,63%), Tabuleiro-2Q (5,52%), Centro-2Q (5,52%), Meia Praia-2Q (5,11%) — **5,11–5,83% líquido, spread de 0,7 p.p.**, dentro do ruído → ranking posicional pouco informativo; o que separa é o grupo (compactos 1Q/2Q) vs 3Q/4Q.
- **3Q derruba para 3,9–4,1%** e **4Q para ~2,7%** — preço sobe mais que a receita.
- **Centro-1Q (indicativo, n_vr=22): 4,82%** — **não é o pior compacto**, mas tem ADR baixo (455) que o fator 0,77 penaliza. Compete no bloco dos compactos, porém com **só ~22 unidades à venda no bairro → não escala para portfolio**.

#### Mudanças de posição após o recálculo da receita (ranking do yield líquido)

**ANTES** (ADR-driven, ocupação fixa 0,408): Morretes-2Q → Tab-2Q → Centro-1Q → Meia Praia-1Q → Centro-2Q → Meia Praia-2Q → ...

**DEPOIS** (ocupação por célula + fator sazonal que escala o ADR da célula):

| Célula | occ alta | Rec. ant. | Rec. nova | yl ant | yl dep | rank ant→dep |
|---|---|---|---|---|---|---|
| Morretes-2Q | 0,81 | 85.720 | 59.986 | 8,60% | 5,83% | 1 → 1 (=) |
| **Meia Praia-1Q** | 0,91 | 86.418 | 69.613 | 7,26% | 5,63% | 4 → **2** ⬆ |
| **Tabuleiro-2Q** | 0,81 | 84.781 | 56.726 | 8,57% | 5,52% | 2 → **3** ⬇ |
| **Centro-2Q** | 0,81 | 92.311 | 82.877 | 6,21% | 5,52% | 5 → **4** ⬆ |
| **Meia Praia-2Q** | 0,97 | 86.046 | 72.873 | 6,15% | 5,11% | 6 → **5** ⬆ |
| **Centro-1Q** | 0,81 | 85.343 | 58.679 | 7,36% | 4,82% | 3 → **6** ⬇ |
| Meia Praia-3Q | 0,88 | 94.172 | 96.213 | 3,79% | 3,88% | 7 → 7 (=) |
| Centro-3Q | 0,91 | 95.736 | 105.705 | 3,46% | 3,86% | 8 → 8 (=) |
| Meia Praia-4Q | 0,88 | 104.847 | 136.136 | 2,02% | 2,74% | 9 → 9 (=) |

O recálculo **muda o ranking dentro do bloco de compactos** (Meia Praia-1Q/2Q sobem; Centro-1Q e Tabuleiro caem — ADR baixo é penalizado pelo fator 0,77), mas **não muda a hierarquia estrutural**: compactos ≫ 3Q ≫ 4Q.

#### Tese e contexto do investimento

- **Compactos: SIM.** 1Q/2Q entregam **~2× o yield** dos 3Q/4Q (5,1–5,8% vs 2,7–3,9% líquido). A tese de "apostar em compactos" é **sustentada pelos dados**.
- **Centro:** **não é o pior compacto** — 4,82% (Centro-1Q) no meio do bloco. Mas **só ~22 unidades 1Q à venda no Centro** → **não escala para portfolio**. Morretes-2Q/Meia Praia-2Q têm oferta ampla no lado da compra (n_vr 1.044 / 244) e yield similar superior.
- **Yield líquido ~5,8% a.a. vs custo de capital:** a renda fixa no Brasil (Selic ~11–13% bruta) oferece retorno nominal superior; o caso de investimento em short stay **depende da valorização do imóvel** somada à operação — não se sustenta apenas pela renda operacional no cenário atual.
- **Taxa operacional da Seazone:** **premissa a validar** (não inventada). Nossa base usa custo operacional de 15% da receita (limpeza/manutenção/vacância). Se a Seazone cobra administração (tipicamente +15–25%), a coluna `−20% adm` (sensibilidade) mostra o efeito e o caso ficaria mais frágil.

#### Por que Morretes-2Q é ~27% mais barato que Meia Praia-2Q (mesma tipologia)?

| | Morretes-2Q | Meia Praia-2Q |
|---|---|---|
| Preço mediano | 790 mil | 1,08 mi (−27%) |
| Área mediana | 69 m² | 85 m² (−19%) |
| R$/m² | 11.551 | 12.929 (−11%) |
| Condomínio mediano | 350 | 500 |
| Vagas de garagem (média) | 1,06 | 1,48 |

- **Metade da diferença é área:** em Meia Praia o 2Q é tipicamente ~85 m²; em Morretes ~69 m².
- **A outra metade é o distrito:** Meia Praia é a **orla** (frente-mar, calçadão, uso de lazer consolidado) → prêmio de ~11% no R$/m²; Morretes é bairro residencial de **segunda linha** (acima da BR-101, mais afastado da areia), com menos garagem/infra de beachfront.
- **Receita quase igual** (~86 mil nos dois): a demanda short-stay premia o preço baixo de Morretes, não penaliza a receita → yield alto.

> **Cuidado:** receita PISO é piso conservador; `*` = indicativo (n 10–29 em algum lado). Yield sensível ao custo operacional (15%) e ao missing de condomínio/IPTU (~30% não reporta). Scatter em `outputs/05_scatter_cross.png`.

### 5.1 Robustez do ranking — cenários de estresse (script `src/06_robustez_cenarios.py`)

> Refeito o yield líquido variando **uma premissa por vez** e depois todas juntas:
> **A**: ocupação 20% menor (`occ_fwd × 0,8`) · **B**: fator sazonal 0,60 (em vez de 0,77) ·
> **C**: taxa de administração 20% deduzida · **COMB**: A+B+C.

**Yield líquido por célula e por cenário (%):**

| Célula | status | Base | A (−20% occ) | B (saz 0,60) | C (−20% adm) | COMB |
|---|---|---|---|---|---|---|
| **Morretes-2Q** | OK | 5,83 | 4,54 | 4,84 | 4,32 | **2,72** |
| **Centro-2Q** | OK | 5,52 | 4,29 | 4,57 | 4,08 | 2,56 |
| Tabuleiro-2Q | IND | 5,52 | 4,29 | 4,57 | 4,07 | 2,54 |
| Meia Praia-1Q | IND | 5,63 | 4,29 | 4,59 | 4,05 | 2,38 |
| Meia Praia-2Q | OK | 5,11 | 3,96 | 4,22 | 3,76 | 2,33 |
| **Centro-1Q** | IND | 4,82 | 3,70 | 3,95 | 3,50 | 2,11 |
| Centro-3Q | OK | 3,86 | 3,01 | 3,20 | 2,86 | 1,80 |
| Meia Praia-3Q | OK | 3,88 | 3,01 | 3,21 | 2,86 | 1,78 |
| Meia Praia-4Q | OK | 2,74 | 2,11 | 2,26 | 2,00 | 1,23 |

**Robustez (mediana do grupo, %):**

| Cenário | Compactos (1–2Q) | Grandes (3–4Q) | Razão |
|---|---|---|---|
| Base | 5,5 | 3,9 | 1,43× |
| A (−20% occ) | 4,3 | 3,0 | 1,42× |
| B (saz 0,60) | 4,6 | 3,2 | 1,43× |
| C (−20% adm) | 4,1 | 2,9 | 1,42× |
| **COMB (A+B+C)** | **2,5** | **1,8** | **1,38×** |

**Linha de conclusão sobre robustez:**
1. **O bloco dos compactos (1–2Q) se mantém acima de 3Q/4Q em todos os cenários** — a razão fica em ~1,4× mesmo no pior caso combinado (ocupa −20%, sazonalidade 0,60 e −20% de admin simultâneos). **Esse 1,4× é compactos vs média de grandes (3Q+4Q juntos)**; contra **4Q isolado** a vantagem sobe para **~2×** (ex.: Base 5,5% vs 2,74% → 2,0×; COMB 2,5% vs 1,23% → 2,0×). O recálculo estressado **não inverte a hierarquia**: nenhum cenário coloca um 3Q/4Q acima de um compacto.
2. **Topo do ranking é estável:** Morretes-2Q fica em 1º em todos os cenários; Centro-2Q/Tabuleiro-2Q brigam por 2º–3º. Centro-3Q e Meia Praia-3Q só "sobem" quando a admin é deduzida (porque têm preço maior e a receita proporcional cai menos) — mas **continuam abaixo de todos os compactos**.
3. **Centro-1Q é o mais fraco do bloco de compactos (6º geral)** — mas **permanece acima de todos os 3Q/4Q em todos os cenários**. Em COMB fica 2,11% (vs Meia Praia-1Q 2,38%, Meia Praia-2Q 2,33% do mesmo bloco, e 1,23–1,80% dos 3Q/4Q).
4. **Cenário pessimista combinado ainda é positivo** (2,5% compactos / 1,8% grandes), mas **fina diante de renda fixa (~11%+ Selic)** — reforça que o caso de investimento **depende da valorização do imóvel**, não do yield operacional isolado.

Detail em `outputs/06_cenarios_yield.csv`.

### 4.2 Anomalias detectadas e tratamentos propostos (diagnóstico — script `src/02_anomalias.py`)

> **Nada foi aplicado aos dados ainda.** Vou esperar aprovação antes de qualquer modificação.

#### A. Preços

| Anomalia | Ocorrências | Proposta de tratamento | Impacto se ignorar |
|---|---|---|---|
| `Price_AV.price` zerado/negativo | **0** | — | — |
| `Price_AV.price` acima de p99.5 (R$ 3.000) | **557** linhas (0,5%), máx R$ 29.000 | Winsorizar/cortar nos quantis (ex.: p1–p99.5) só para descritivas; ou flag como outlier | Distorce médias de receita e ranking de localização |
| `Price_AV` preço R$ 10.000 (2 listings) e R$ 29.000 (1 listing) | 3 listings em datas específicas | Investigue se é erro de captura; tratar como outlier/excluir desses listings | Infla receita desses listings |
| `VivaReal.sale_price` zerado/negativo | **0** | — | — |
| `VivaReal.sale_price` < R$ 100 mil (provável erro/quartinho) | 2 | Excluir da estimativa de custo de aquisição | Puxa o investimento inicial para baixo |
| `VivaReal.sale_price` > R$ 20 mi (máx R$ 44 mi) | 12 | Excluir ou tratar como outliers no cálculo de preço médio/m² | Infla custo médio do imóvel/m² |
| `VivaReal.rental_price` | 99,9% nulos (8.327); foco em `sale_price` | Usar somente `sale_price` como custo de aquisição | Ignorar `rental_price` sinaliza que o retorno é por short stay (Airbnb), não aluguel |
| `Details.cleaning_fee` zerado | 939 (21%) | Valem 0 (não cobra limpeza) → manter como 0 e considerar `price` sem cleaning fee | Superestimar a receita líquida com diária se dobrar |

#### B. Coordenadas

| Anomalia | Ocorrências | Proposta | Impacto |
|---|---|---|---|
| `Details.latitude/longitude` = **0,0 para 4.441/4.441 (100%)** | Todos | **Usar `Mesh` como fonte de geolocalização** (join por `airbnb_listing_id`, 100% de cobertura e janela lat/lon consistente com Itapema) | Sem isso, é impossível localizar listings (falha total na análise de localização) |
| `Mesh`: 0 coordenadas fora do box Itapema | 0 | Validado | — |
| `Mesh.suburb` = `none` + `Jardim Praiamar` etc. (poucos) | 5 + 5 | Agrupar/sem tratamento (few) | — |

#### C. Listings sem reviews/atividade

| Anomalia | Ocorrências | Proposta | Impacto |
|---|---|---|---|
| `number_of_reviews` = 0 | 1.540 (34,7%) | Separar como **listings sem histórico**; não usá-los para estimar receita/ocupação (sem dados de demanda) | Misturar com os ativos inflaria a base com anúncios "mortos" |
| `star_rating` = 0 (sub-intérprete de "sem avaliação") | 1.540 | Tratar 0 como NA para qualidade; não zerar a média | Distorce ranking de qualidade |
| `guest_satisfaction_overall` = 0 | 1.540 | Idem | Idem |
| `is_new_listing` = True | 731 (16%) | Analisar separadamente (sem histórico) | Confundir "novo anunciante" com baixa demanda |

#### D. Áreas / dormitórios (VivaReal e Details)

| Anomalia | Ocorrências | Proposta | Impacto |
|---|---|---|---|
| `VivaReal.usable_area` = 0 ou < 5m² | 11 + 1 | Excluir da análise de preço/m² | Zera o R$/m² e derruba o custo médio |
| `VivaReal.usable_area` > 500 m² | 138 | Suspeito (possível M² de condomínio); investigar antes de usar em preço/m² | Infla m² e erro no cálculo |
| `VivaReal` sem `bedrooms` informado = 0 | 230 | Tratar 0 como `N/A` (estúdio vs missing) | Confundir estúdio com dado ausente |
| `Details.number_of_bedrooms` = 0 | 56 | Suspeito (estúdio ou erro); validar com `listing_type` | Afeta segmentação compactos vs grandes |

**Decisão estrutural derivada:** usar **`Mesh` como fonte oficial de coords/bairro** e **`Price_AV` apenas para os 999 listings com preço** na análise de receita. Recomendações sobre outliers serão implementadas só após aprovação.

## 6. Posição sobre a tese dos compactos no Centro

**Pendente.** Os dados sustentam ou refutam a tese de que apartamentos compactos
(studio/1 quarto) no Centro seriam a aposta mais eficiente?

## 7. Recomendação final

_Pendente — resumo defensável da decisão de investimento._

## 8. O que faria com mais uma semana

_Pendente._

---

_Insights, visualizações e código em [`src/`](src/), [`outputs/`](outputs/) e [`dashboard/`](dashboard/).
Conversas com a IA em [`ai-log/`](ai-log/)._