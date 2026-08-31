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
- **Sazonalidade = só ADR por mês** (jan 828 → fev 763 → mar 652 → abr 573). Alta (jan–fev) = 796; ombro (mar–abr) = 612 → **fator do restante do ano = 0,77**.
  - **Sobre "o ranking independe do fator":** na **receita bruta** o fator é um multiplicador uniforme (`rec_an = rec_91d × (1 + 0,77×274/91)`), logo **o ranking bruto não depende dele**. No **yield líquido**, porém, o fator interage com os custos fixos por célula (condomínio/IPTU) e reordena marginalmente (ex.: Centro-2Q ↔ Tabuleiro-2Q trocam de 3º/4º quando se adota fator 0,60) — a independência vale para o bruto, **não para o líquido**.
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
- **Deduções:** condomínio (mediana só entre reportados >0, ×12) + IPTU (mediana real >0) + **custo operacional 10%** da receita bruta (manutenção/vacância/overhead).
- **Correção de dupla retirada (cleaning_fee):** `cleaning_fee` é **pass-through** (cobrado do hóspede, repassado à limpeza) e está **fora da receita** (P11). Logo o custo operacional **não inclui limpeza** — reduzi a taxa de 15% (que incluía limpeza) para **10%**. Removida a dupla dedução.
- **Administração (−20% da receita bruta):** apenas na coluna de sensibilidade `yield_liq_adm`.
- **Custos de aquisição NÃO modelados** (ITBI ~2–3%, corretagem, registro, mobília/equipagem, reformas, ramp-up): **tornam o yield otimista** — premissa declarada; o retorno real é menor que o reportado.
- **n≥30 em ambos os lados = conclusiva; n entre 10–29 em ambos = indicativo (marcado `*`); n<10 ou sem preço = NC.**
- **0Q (studio) incluído** na tabela; só apartamentos (oferta e compra).

### Yield por **bairro × quartos** (apartamento; ADR/ocupação por célula; `*` = indicativo; op 10%)

> **Receita recalculada por célula (fórmula final):**
> `receita_91d = ADR_célula × 91 × (0,408 × occ_le15_célula ÷ occ_le15_global)` com `occ_le15_global = 0,776`
> **Anual = receita_91d + ADR_célula × 0,77 × 274 × occ_forward_célula** — o fator sazonal **escala o ADR da célula**, não o substitui. **Yield líquido = (receita_anual × 0,90 − condomínio − IPTU) ÷ preço** (op 10%).

| Bairro | Q | n_ab | n_vr | ADR (med) | Ocup. alta | Receita anual bruta | Preço mediano | R$/m² | **Bruto** | **Líquido** | Líq. −20% adm |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Centro | 0 | 0 | 0 | — | — | — | — | — | NC | NC | NC |
| Centro | 1 | 75 | 22 | 455 | 0,81 | 58.679 | 890 mil | 14.574 | 6,59%* | 5,15%* | 3,83%* |
| Centro | 2 | 59 | 89 | 643 | 0,81 | 82.877 | 1,15 mi | 13.068 | 7,21% | 5,88% | 4,44% |
| Centro | 3 | 38 | 438 | 735 | 0,91 | 105.705 | 2,10 mi | 15.789 | 5,03% | 4,12% | 3,11% |
| Centro | 4 | 1 | 436 | 629 | 1,00 | — | 3,90 mi | 18.890 | NC | NC | NC |
| Meia Praia | 1 | 16 | 58 | 484 | 0,91 | 69.613 | 877 mil | 21.250 | 7,93%* | 6,03%* | 4,44%* |
| Meia Praia | 2 | 126 | 244 | 474 | 0,97 | 72.873 | 1,08 mi | 12.929 | 6,78% | 5,45% | 4,10% |
| Meia Praia | 3 | 284 | 1.704 | 693 | 0,88 | 96.213 | 1,88 mi | 14.957 | 5,10% | 4,13% | 3,11% |
| Meia Praia | 4 | 44 | 1.408 | 980 | 0,88 | 136.136 | 3,70 mi | 18.617 | 3,68% | 2,92% | 2,19% |
| **Morretes** | **2** | 43 | 1.044 | 465 | 0,81 | 59.986 | 790 mil | 11.551 | 7,59% | **6,21%** | **4,69%** |
| Tabuleiro dos Oliveiras | 2 | 12 | 106 | 440 | 0,81 | 56.726 | 782 mil | 11.502 | 7,25%* | 5,88%* | 4,43%* |

> Ocupação = `occ_le15` (alta temporada realizada, lead≤15; zero datas no lead curto = 1,0). Outras células (Casa Branca, Canto da Praia, Ilhota, Alto São Bento) têm n<10 no lado Airbnb → NC (detalhe em `outputs/05_yield_cross.csv`).

**Sobre o ADR × nº de quartos (confirmação):** **o ADR varia sim com quartos** — mediana global (apartamentos): 1Q 456 → 2Q 489 → 3Q 696 → 4Q 964. O que é verdadeiro é que **1Q e 2Q têm ADR próximos** (456 vs 489, +7%) apesar de preços de compra bem diferentes por localização. A "receita quase igual entre 1Q/2Q" vem de ADR 1Q≈2Q e ocupação semelhante. Não é artefato.

**Leitura (por célula, sem confundir composição com localização):**
- **Top 5 é quase um empate técnico:** Morretes-2Q (6,21%), Meia Praia-1Q (6,03%), Centro-2Q/Tabuleiro-2Q (5,88%) e Meia Praia-2Q (5,45%) — **5,45–6,21% líquido, spread de 0,8 p.p.**, dentro do ruído → ranking posicional pouco informativo; o que separa é o grupo (compactos 1Q/2Q) vs 3Q/4Q.
- **3Q derruba para ~4,1%** e **4Q para ~2,9%** — preço sobe mais que a receita.
- **Centro-1Q (indicativo, n_vr=22): 5,15%** — **não é o pior compacto** (é o mais fraco fora do topo, ADR baixo 455 penalizado pelo fator 0,77), mas **permanece acima de todos os 3Q/4Q**. Tem **só ~22 unidades à venda no bairro → não escala para portfolio**.

#### Mudanças de posição após o recálculo da receita (ranking do yield líquido, op 10%)

**ANTES** (ADR-driven, ocupação fixa 0,408, op 15%): Morretes-2Q → Tab-2Q → Centro-1Q → Meia Praia-1Q → Centro-2Q → Meia Praia-2Q → ...

**DEPOIS** (ocupação por célula + fator sazonal escala ADR da célula + op 10%):

| Célula | occ alta | Rec. ant. | Rec. nova | yl ant | yl dep | rank ant→dep |
|---|---|---|---|---|---|---|
| Morretes-2Q | 0,81 | 85.720 | 59.986 | 8,60% | 6,21% | 1 → 1 (=) |
| **Meia Praia-1Q** | 0,91 | 86.418 | 69.613 | 7,26% | 6,03% | 4 → **2** ⬆ |
| **Tabuleiro-2Q** | 0,81 | 84.781 | 56.726 | 8,57% | 5,88% | 2 → **3** ⬇ |
| **Centro-2Q** | 0,81 | 92.311 | 82.877 | 6,21% | 5,88% | 5 → **3** ⬆ |
| **Meia Praia-2Q** | 0,97 | 86.046 | 72.873 | 6,15% | 5,45% | 6 → **5** ⬆ |
| **Centro-1Q** | 0,81 | 85.343 | 58.679 | 7,36% | 5,15% | 3 → **6** ⬇ |
| Meia Praia-3Q | 0,88 | 94.172 | 96.213 | 3,79% | 4,13% | 7 → 7 (=) |
| Centro-3Q | 0,91 | 95.736 | 105.705 | 3,46% | 4,12% | 8 → 8 (=) |
| Meia Praia-4Q | 0,88 | 104.847 | 136.136 | 2,02% | 2,92% | 9 → 9 (=) |

O recálculo **muda o ranking dentro do bloco de compactos** (Meia Praia-1Q/2Q sobem; Centro-1Q e Tabuleiro caem — ADR baixo é penalizado pelo fator 0,77), mas **não muda a hierarquia estrutural**: compactos ≫ 3Q ≫ 4Q.

#### Tese e contexto do investimento

- **Compactos: SIM** — com a métrica unificada em todo o documento:
  - **vs média de grandes (3Q+4Q):** razão **1,43×** (compactos 6,0% vs grandes 4,1% líquido, medianas);
  - **vs 4Q isolado:** razão **~2,0×** (6,0% vs 3,0%).
  A tese de "apostar em compactos" é **sustentada pelos dados** em ambas as métricas.
- **Centro:** **não é o pior compacto** — 5,15% (Centro-1Q) no meio do bloco, acima de todos os 3Q/4Q. Mas **só ~22 unidades 1Q à venda no Centro** → **não escala para portfolio**. Morretes-2Q/Meia Praia-2Q têm oferta ampla no lado da compra (n_vr 1.044 / 244) e yield similar superior.
- **Yield líquido ~6,2% a.a. vs custo de capital:** a renda fixa no Brasil oferece retorno nominal superior (ver fonte da Selic abaixo); o caso de investimento em short stay **depende da valorização do imóvel** somada à operação — não se sustenta apenas pela renda operacional no cenário atual.
- **Fonte do custo de capital:** Selic meta. No intervalo de captura dos dados (jan/2025), o Copom fixava a Selic em **12,25% a.a.** (decisão de dez/2024) e **13,25% a.a.** (decisão de 29/jan/2025). Fonte: Banco Central do Brasil — histórico da taxa Selic, bcb.gov.br/controleinflacao/historicotaxasjuros.
- **Taxa operacional da Seazone:** **premissa a validar** (não inventada). A base usa custo operacional de 10% (sem limpeza, pass-through). Se a Seazone cobra administração (tipicamente +15–25%), a coluna `−20% adm` (sensibilidade) mostra o efeito e o caso ficaria mais frágil.

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

> **Cuidado:** receita PISO é piso conservador; `*` = indicativo (n 10–29 em algum lado). Yield sensível ao custo operacional (10%) e ao missing de condomínio/IPTU (~30% não reporta). Scatter em `outputs/05_scatter_cross.png`.

### 5.1 Robustez do ranking — cenários de estresse (script `src/06_robustez_cenarios.py`)

> Refeito o yield líquido variando **uma premissa por vez** e depois todas juntas (base = op 10%):
> **A**: ocupação 20% menor (`occ_fwd × 0,8`) · **B**: fator sazonal 0,60 (em vez de 0,77) ·
> **C**: taxa de administração 20% deduzida · **COMB**: A+B+C.

**Yield líquido por célula e por cenário (%):**

| Célula | status | Base | A (−20% occ) | B (saz 0,60) | C (−20% adm) | COMB |
|---|---|---|---|---|---|---|
| **Morretes-2Q** | OK | 6,21 | 4,85 | 5,16 | 4,69 | **2,98** |
| Meia Praia-1Q | IND | 6,03 | 4,60 | 4,93 | 4,44 | 2,65 |
| Centro-2Q | OK | 5,88 | 4,58 | 4,88 | 4,44 | 2,80 |
| Tabuleiro-2Q | IND | 5,88 | 4,58 | 4,88 | 4,43 | 2,79 |
| Meia Praia-2Q | OK | 5,45 | 4,23 | 4,51 | 4,10 | 2,56 |
| **Centro-1Q** | IND | 5,15 | 3,96 | 4,23 | 3,83 | 2,34 |
| Centro-3Q | OK | 4,12 | 3,21 | 3,42 | 3,11 | 1,97 |
| Meia Praia-3Q | OK | 4,13 | 3,21 | 3,42 | 3,11 | 1,96 |
| Meia Praia-4Q | OK | 2,92 | 2,26 | 2,41 | 2,19 | 1,35 |

**Robustez (mediana do grupo, %):**

| Cenário | Compactos (1–2Q) | Grandes (3–4Q) | Razão | vs 4Q isolado |
|---|---|---|---|---|
| Base | 5,9 | 4,1 | 1,43× | 2,0× |
| A (−20% occ) | 4,6 | 3,2 | 1,43× | 2,0× |
| B (saz 0,60) | 4,9 | 3,4 | 1,43× | 2,0× |
| C (−20% adm) | 4,4 | 3,1 | 1,43× | 2,0× |
| **COMB (A+B+C)** | **2,7** | **2,0** | **1,39×** | **2,0×** |

**Linha de conclusão sobre robustez:**
1. **O bloco dos compactos (1–2Q) se mantém acima de 3Q/4Q em todos os cenários** — a razão fica em ~1,4× mesmo no pior caso combinado (ocupa −20%, sazonalidade 0,60 e −20% de admin simultâneos). **Esse 1,4× é compactos vs média de grandes (3Q+4Q juntos)**; contra **4Q isolado** a vantagem é **~2,0×** em todos os cenários. O recálculo estressado **não inverte a hierarquia**: nenhum cenário coloca um 3Q/4Q acima de um compacto.
2. **Topo do ranking é estável:** Morretes-2Q fica em 1º em todos os cenários de uma premissa por vez; Centro-2Q/Tabuleiro-2Q brigam por 2º–4º. Centro-3Q e Meia Praia-3Q só "sobem" quando a admin é deduzida — mas **continuam abaixo de todos os compactos**.
3. **Centro-1Q é o mais fraco do bloco de compactos (6º geral)** — mas **permanece acima de todos os 3Q/4Q em todos os cenários**. Em COMB fica 2,34% (vs Meia Praia-1Q 2,65% e Meia Praia-2Q 2,56% do mesmo bloco, e 1,35–1,97% dos 3Q/4Q).
4. **Cenário pessimista combinado ainda é positivo** (2,7% compactos / 2,0% grandes), mas **fina diante de renda fixa (Selic ~12–13%)** — reforça que o caso de investimento **depende da valorização do imóvel**, não do yield operacional isolado.

Detalhe em `outputs/06_cenarios_yield.csv`.

### 5.2 Cenários adversariais adicionais (script `src/07_cenarios_adversarios.py`)

> Três ataques extras contra o modelo (base corrigida op 10%), mantendo a mesma fórmula:
> **S1** — **exclui os 300 listings imputados** como ocupação 1,0 (apartamentos sem datas no lead ≤15):
> recalculado `occ_global = 0,623` (era 0,776) e as ocupações das células só sobre o subconjunto não-imputado.
> **S2** — **ADR das noites vendidas (+9%)** (P13) aplicado ao ADR de todas as células.
> **S3** — **piso absoluto = receita dos 91 dias ÷ preço**, sem nenhuma receita de inverno.

**Yield líquido por célula (%):**

| Célula | status | Base | S1 (sem imputados) | S2 (ADR +9%) | S3 (piso 91d) |
|---|---|---|---|---|---|
| **Morretes-2Q** | OK | 6,21 | 6,73 | 6,83 | **1,44** |
| Meia Praia-1Q | IND | 6,03 | — | 6,67 | 1,04 |
| Tabuleiro-2Q | IND | 5,88 | 7,99 | 6,47 | 1,32 |
| Centro-2Q | OK | 5,88 | 6,46 | 6,46 | 1,35 |
| Meia Praia-2Q | OK | 5,45 | 5,61 | 6,00 | 1,19 |
| **Centro-1Q** | IND | 5,15 | 7,03 | 5,68 | 1,00 |
| Meia Praia-3Q | OK | 4,13 | 3,79 | 4,55 | 0,92 |
| Centro-3Q | OK | 4,12 | 4,13 | 4,52 | 0,95 |
| Meia Praia-4Q | OK | 2,92 | 3,63 | 3,22 | 0,61 |

*(em S1 algumas células caíram de status: Meia Praia-1Q/4Q e Centro-3Q ficaram com n<10 no lado Airbnb → sem dado; Morretes-2Q n=30, Tabuleiro-2Q n=10.)*

**Veredito por cenário (as 3 perguntas):**

| Cenário | Compactos vs média de grandes | Compactos vs 4Q isolado | Centro-1Q > todos 3Q/4Q | Morretes-2Q no topo |
|---|---|---|---|---|
| Base | 1,43× | 2,01× | ✅ | ✅ |
| **S1** (sem imputados) | **1,77×** | 1,85× | ✅ | ⚠️ **NÃO** (Tabuleiro-2Q 7,99% e Centro-1Q 7,03% à frente) |
| **S2** (ADR +9%) | 1,43× | 2,01× | ✅ | ✅ |
| **S3** (piso 91d) | 1,36× | 2,06× | ✅ | ✅ |

**Conclusão:**
- **O ranking estrutural sobrevive aos 3 cenários:** compactos seguem acima de 3Q/4Q em todos (razão 1,36–1,77× vs média de grandes; 1,85–2,06× vs 4Q isolado), e **Centro-1Q segue acima de todos os 3Q/4Q** — as duas afirmações centrais da tese são robustas mesmo excluindo os imputados.
- **Porém "Morretes-2Q é o melhor" NÃO é robusto:** excluídos os imputados, **Tabuleiro-2Q e Centro-1Q ultrapassam** (morretes tinha ocupação 0,81 inflada por imputação de 13 anúncios). A conclusão segura é **"algum compacto 2Q está no topo, não necessariamente Morretes"**.
- **Caveat de S1:** a exclusão mantém fixo o piso 0,408 e só renormaliza `occ_cel/occ_global`; um tratamento plenamente consistente rederivaria o próprio piso sobre o subconjunto, mudando níveis absolutos (não a hierarquia).
- **S3 (sem inverno) derruba o patamar para ~1,0–1,4% nos compactos** — **confirma que quase todo o yield vem da receita de inverno anualizada**; sem ela, o retorno operacional é desprezível e o caso depende integralmente da valorização.

Detalhe em `outputs/07_cenarios_adversarios.csv`.

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

**Tese testada:** "apartamentos compactos (studio/1 quarto) na região do Centro seriam a aposta mais eficiente".

**Veredito — PARCIALMENTE, com ajuste de geografia:**

1. **"Compactos" — CONFIRMADA.** O bloco 1Q/2Q supera o 3Q/4Q em **todos** os cenários testados (base, ocupação −20%, sazonalidade 0,60, adm −20%, excluindo os imputados, ADR +9%, e até no piso absoluto de 91 dias). A razão é **1,43× vs média de grandes** e **~2,0× vs 4Q isolado** — robusta.
2. **"Studio/1 quarto" — FRACA.** Não há **nenhum studio (0Q) à venda como apartamento** no Centro (n_viva=0) e o 1Q tem só **22 unidades** (abaixo do corte conclusivo). O segmento 1Q do Centro existe na oferta (75 anúncios) mas **não escala no lado da compra**.
3. **"Centro" — NÃO É O FOCO DO YIELD.** O Centro não é o pior compacto (5,15%, acima de todos os 3Q/4Q), mas o topo do yield é **Morretes-2Q** (6,21%) e **Meia Praia-1Q** (6,03%) — preços de entrada baixos. **A tese original supervaloriza o Centro**: o mecanismo que gera yield é **preço de compra barato × receita similar** (bairros de segunda linha), não "Centro".
4. **Caveat de robustez:** excluídos os imputados (S1), **Tabuleiro-2Q e Centro-1Q ultrapassam Morretes-2Q** — a afirmação "bairro X é o melhor" é instável; a afirmação "compacto 2Q está no topo do bloco" é estável.

## 7. Recomendação final

**Se a Seazone for investir hoje em Itapema (SC):**

1. **Comprar apartamentos compactos de 2 quartos (2Q)** — o perfil com o melhor yield líquido de forma robusta: **~5,5–6,2% a.a. no cenário-base**, **~1,43× o retorno de 3Q/4Q** e **~2,0× o de 4Q**. Prioridade de bairro: **Morretes e Meia Praia** (oferta ampla no lado da compra, n_vr 1.044 e 244), onde a receita short-stay é praticamente a mesma dos bairros de orla por um **preço 27% menor por m²**.
2. **Evitar 4Q e 3Q como principal aposta** — yield líquido de ~2,9% e ~4,1%: o preço de compra sobe mais que o ADR. 4Q só se o caso depender de valorização unitária alta, não de renda.
3. **Não apostar em studio/1Q no Centro no momento** — não escala: 0 studios e apenas ~22 unidades 1Q à venda; e o yield do Centro-1Q (5,15%), embora acima dos 3Q/4Q, perde para Morretes/Meia Praia com oferta adequada. **A tese original ("compactos no Centro") deve ser redirecionada para "compactos 2Q em bairros de entrada"**.
4. **Condicionar a decisão à validação de premissas:** (i) **curva de ocupação anual** (o yield atual anualiza 3 meses de verão com o piso 0,408 — sem inverno, cai para ~1,0–1,4%; validar mai–dez); (ii) **taxa operacional/administrativa da Seazone** (a coluna −20% reduzi o yield para ~4,7% no topo); (iii) **custos de aquisição não modelados** (ITBI/corretagem/mobília — tornam o yield otimista).
5. **Decisão de investimento de capital:** com yield líquido **~6,2% a.a. vs Selic 12,25%–13,25% a.a.** (BCB, jan/2025), o **short stay sozinho não justifica o custo de oportunidade**. **O caso SÓ fecha com valorização do ativo** (apreciação de ~6–8% a.a. na região) ou com alavancagem favorável. Recomendação prática: **entrar devagar, com 1–2 unidades-piloto compactas 2Q em Morretes/Meia Praia**, validar a ocupação real de inverno num ciclo completo antes de escalar o portfolio.

## 8. O que faria com mais uma semana

- Baixar o histórico completo de preços/ocupabilidade por **série temporal real de reservas** (via API/partners), e não só 3 snapshots em 14 dias — para estimar a curva de demanda de mai–dez com dados, não com fator 0,77 uniforme.
- Cruzar anúncios VivaReal **pré-precificados por unidade** com Airbnb (match por endereço/área/pavimento) para eliminar o viés de "perfil médio".
- Estresse de **taxas de juros/vacância longa** e **cenário de desvalorização** no modelo de yield.
- Validar a taxa operacional real da Seazone (limpeza, mão de obra, software, tributos) via custos de operação de um imóvel-piloto.
- Investigar no VivaReal a **qualidade dos lançamentos** (unidades novas com preço de tabela) vs revenda.

---

_Insights, visualizações e código em [`src/`](src/), [`outputs/`](outputs/) e [`dashboard/`](dashboard/).
Conversas com a IA em [`ai-log/`](ai-log/)._