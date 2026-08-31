# ai-log/05 — Sessão adversarial (comitê de investimentos cético)

**Data:** 31/08/2026 · **Contexto:** revisão do `relatorio.md` e `outputs/` por um avaliador cético.
**Compromisso:** registrar os 5 ataques mais fortes e, abaixo de cada um, o que foi corrigido
nesta análise (ou por que o ataque não procede / permanece como limitação).

---

## Ataque 1 — "O yield é anualizado com 3 meses de verão e zero dado de inverno; o patamar absoluto é inventado."

O snapshot cobre apenas 20/01–20/04 (verão + ombro) e a fórmula aplica a ocupação piso
(0,408×escala, até 0,43–0,53 por célula) aos 274 dias restantes do ano. Não há nenhuma observação
de mai–dez. O patamar absoluto (5,5–6,2% no base) depende de uma ocupação de inverno pressuposta.

**Corrigido / reconhecido:**
- Foi adicionado o **cenário S3 — piso absoluto = receita dos 91 dias ÷ preço, sem nenhuma receita de inverno** (§5.2 e `src/07_cenarios_adversarios.py`). Nele os compactos caem para **~1,0–1,4%** e 4Q para **0,6%**: confirma literalmente o ataque — **quase todo o yield vem da receita anualizada de inverno**.
- O relatório passa a declarar explicitamente que o caso de investimento **depende da valorização**, não do yield operacional isolado.
- **Permanece como limitação deliberada:** sem série temporal real de mai–dez não é possível estimar a curva de inverno; o fator 0,77 é premissa declarada (e a §8 lista a validação como próximo passo).
- Nota: o ranking *relativo* (compactos ≫ grandes) **sobrevive** ao ataque (razão 1,43× a 2,0× persistente), mas o *patamar* não deve ser usado como "retorno esperado" sem validação.

---

## Ataque 2 — "A 'ocupação' não distingue reserva de calendário bloqueado; 40% dos listings são chutados para ocupação 1,0; o campo min_nights é todo zero."

`occ_le15 = 1 − (datas no lead ≤15)/16`; 300/737 apartamentos (≈41%) sem nenhuma data no lead curto
viram ocupação = 1,0. Isso é proxy de *não disponibilizou calendário* (bloqueio/min-stay/baixa operação),
não de demanda. Sinal corroborante: `min_nights` é 0/0 nos 4.441 listings (dado corrompido) e 35,5%
dos listings não registraram uma única reserva entre capturas.

**Corrigido / reconhecido:**
- Criado o **cenário S1 — exclui os listings imputados como ocupação 1,0** e recalcula ocupação global
  (0,776 → 0,623) e das células só sobre o subconjunto não-imputado.
- **Resultado que muda conclusão:** excluídos os imputados, **Morretes-2Q deixa de ser o topo** —
  Tabuleiro-2Q (7,99%) e Centro-1Q (7,03%) assumem a frente; e a razão compactos/média de grandes
  sobe para 1,77×. Ou seja, o ataque derruba a *afirmação posicional* ("Morretes é o melhor"),
  mas **não** a afirmação estrutural (compactos ≫ grandes; Centro-1Q > 3Q/4Q).
- **Respostas operacionais:** a ocupação passou a ser reportada como **proxy forward** (alta temporada
  realizada), com o caveat explícito no relatório; a imputação de 1,0 foi documentada e testada.
- `min_nights` é mau dado → **não entra em nenhuma métrica** (registrado em §4.2).
- **Não procede (parcial):** o rótulo "ocupação" já era qualificado como *forward/disponibilidade*,
  não demanda realizada; e o piso 0,408 é modularidade conservadora. O ataque permanece válido no
  detalhe (bloqueio ≠ reserva) e é esta a razão para manter a ocupação como **cenário de sensibilidade**.

---

## Ataque 3 — "Inconsistências internas: '2×' vs '1,43×' convivem; 'o ranking independe do fator sazonal' é falso."

O relatório ora dizia "compactos ~2× o yield dos 3Q/4Q" (comparando o melhor compacto com o pior
grande, cherry-picking), ora 1,43× (medianas). Além disso alegava que "fator uniforme → ranking
independe dele", mas o próprio cenário B (fator 0,60) reordena Tabuleiro-2Q e Centro-2Q.

**Corrigido:**
- **Métricas unificadas em TODO o documento:** compactos vs **média de grandes (3Q+4Q) = 1,43×**;
  compactos vs **4Q isolado = ~2,0×**. As duas métricas são agora usadas consistentemente em §5, §5.1,
  §5.2, §6 e §7.
- **Corrigida a declaração do fator sazonal:** na receita **bruta** o fator é um multiplicador uniforme
  (`rec_an = rec_91d × (1 + f×274/91)`) → o ranking bruto independe dele. No **yield líquido** o fator
  interage com custos fixos (condomínio/IPTU) e **reordena marginalmente** (Centro-2Q ↔ Tabuleiro-2Q
  trocam 3º/4º em fator 0,60). O texto agora distingue os dois casos (§4.1).

---

## Ataque 4 — "O yield casa dois universos na mediana, usa ADR das datas disponíveis (subavaliando o vendido), e tinha dupla retirada do cleaning_fee."

As duas bases não compartilham imóveis; o lado compra usa *asking price* (e ±30% sem condomínio/IPTU);
o lado oferta é o subconjunto ativo/profissional (22,5%) enviesado para Centro. A receita é ADR×occup,
mas o ADR é o das datas ainda disponíveis, enquanto P13 mediu que as noites **vendidas custam +9%**.
E o `cleaning_fee` (receita real do operador) saía da receita e ainda pesava nos 15% de custo operacional.

**Corrigido:**
- **Dupla retirada do cleaning_fee removida:** como `cleaning_fee` é pass-through (fora da receita,
  P11), o custo operacional foi **reduzido de 15% → 10%**, mantendo limpeza *fora* de ambos os lados.
  Todas as tabelas de yield foram **regeneradas** com op 10% (os yields sobem ~0,3–0,4 p.p.).
- **Viés do ADR das noites vendidas testado:** cenário **S2 (ADR × 1,09)** aumenta os yields em ~9%
  uniforme e **não muda o ranking** (multiplicativo) — o uso do ADR disponível subestima o nível,
  não a hierarquia.
- **Universos não reconciliáveis declarado como limitação crítica** (§5), com n dos dois lados sempre
  expostos; as células são "perfil médio", não imóvel×imóvel.

---

## Ataque 5 — "O relatório se auto-refuta contra a renda fixa, não conclui (recomendação 'Pendente'), e omite custos de aquisição."

Yield ~5,8% (base) vs Selic ~12% — o número não sustenta a compra por renda; a seção 7 estava
"Pendente"; e nada de ITBI/corretagem/mobília/ramp-up no yield.

**Corrigido:**
- **Recomendação final escrita** (§7): perfil 2Q em Morretes/Meia Praia como piloto, evitar 3Q/4Q,
  redirecionar a tese "compactos no Centro" → "compactos 2Q em bairros de entrada" (Centro não escala),
  decisão condicionada à validação de ocupação anual, taxa Seazone e custos de aquisição. Veredito da
  tese em §6 com o **caveat** de que "Morretes no topo" não é robusto em S1.
- **Selic com fonte citada:** BCB — Selic meta 12,25% a.a. (dez/2024) e 13,25% a.a. (29/jan/2025),
  dentro do período da captura; ref. bcb.gov.br/controleinflacao/historicotaxasjuros.
- **Custos de aquisição declarados como premissa que torna o yield otimista** (§5).
- **Ainda permanece (limitação honesta):** mesmo com as correções, o yield líquido topo é ~6,2% a.a.
  no base (ou ~2,7–3,0% no pior caso combinado) **abaixo da Selic nominal** — a conclusão que o próprio
  relatório adota é: entrar em modo piloto e o caso econômico **depende de valorização**; o short stay
  sozinho não supera a renda fixa nos números atuais.