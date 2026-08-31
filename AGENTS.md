# AGENTS.md — Hackathon Jovens Talentos AI Builder 2026 (Seazone)

Instruções de trabalho para agentes de IA neste repositório. Criado por Leonardo Coli.

## Desafio

Hackathon de 1 dia da Seazone: recomendar onde e no que investir no mercado imobiliário de
**Itapema (SC)**, usando o snapshot de dados fornecido (anúncios de Airbnb + VivaReal em `data/`).
A Seazone gere short stay no Brasil e usa IA no centro da operação.

Entrega: este repositório forkado e público (`jt2026-leonardo-coli`) com análise, `README.md`
explicando como rodar, `ai-log/` com as conversas com IA em texto e a recomendação final em
`relatorio.md`. Link do vídeo (Drive) na primeira linha do README.

## As 4 perguntas a responder

1. Qual o **melhor perfil de imóvel** para investir na cidade? (tipologia, nº de quartos, tipo de anúncio)
2. Qual a **melhor localização** em termos de receita?
3. Quais **características explicam** as melhores receitas?
4. Se a Seazone investisse hoje, **o que comprar e por quê?** — com estimativa simples de retorno e defesa da decisão.

## Tese interna a confirmar ou refutar

Uma análise preliminar interna (não validada) sugeriu que **apartamentos compactos
(studio/1 quarto) na região do Centro** seriam a aposta mais eficiente para a Seazone.
A recomendação final DEVE tomar posição explícita: os dados sustentam ou refutam essa tese?

## Regras de trabalho

- **Outputs em `outputs/`** — figuras, tabelas e resultados gerados vão para cá (com nomes claros).
- **Scripts numerados em `src/`** — código de análise em arquivos numerados por ordem de execução
  (ex.: `src/01_limpeza.py`, `src/02_analise.py`), o que torna o fluxo reproduzível.
- **Premissas documentadas em `relatorio.md`** — cada critério de "melhor", corte, tratamento de
  dado faltante e suposição de retorno deve estar registrado ali.
- **Responder sempre em português** (pt-BR) ao usuário e nos artefatos.
- **Nunca avançar de fase sem aprovação do usuário** — a cada etapa concluída, apresentar resultado
  e aguardar o OK antes de seguir. Não fazer commits/pushes além do autorizado explicitamente.