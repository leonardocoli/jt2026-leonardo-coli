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

### 4.1 Anomalias detectadas e tratamentos propostos (diagnóstico — script `src/02_anomalias.py`)

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

## 5. Posição sobre a tese dos compactos no Centro

**Pendente.** Os dados sustentam ou refutam a tese de que apartamentos compactos
(studio/1 quarto) no Centro seriam a aposta mais eficiente?

## 6. Recomendação final

_Pendente — resumo defensável da decisão de investimento._

## 7. O que faria com mais uma semana

_Pendente._

---

_Insights, visualizações e código em [`src/`](src/), [`outputs/`](outputs/) e [`dashboard/`](dashboard/).
Conversas com a IA em [`ai-log/`](ai-log/)._