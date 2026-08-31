# Roteiro do vídeo — 3 min · Hackathon Jovens Talentos AI Builder 2026 (Seazone)

**Leonardo Coli** · Itapema/SC · entrega `jt2026-leonardo-coli`

Estrutura: uma **rolagem contínua** do `dashboard/index.html`, de cima para baixo,
seguindo a ordem real das seções. Um único corte fora do dashboard (bloco de IA).
~430 palavras faladas ≈ 3 minutos.

Antes de gravar: navegador em tela cheia, zoom 110%, página no topo, sem abas
nem notificações. Role sempre devagar e sempre para baixo.

---

## 0:00–0:25 · Hero
**Tela:** cabeçalho (o chip já mostra "Recomendação: Apto 2Q · Morretes/Meia Praia")
**Enquadramento:** rosto dominante (ou câmera no canto, se sem edição)

> Leonardo Coli. Se a Seazone fosse investir hoje em Itapema, minha recomendação
> é essa aqui: apartamento compacto, um ou dois quartos, em Morretes ou Meia
> Praia — e em modo piloto, não em portfólio. Vou defender as duas coisas: o
> compacto e o piloto.

---

## 0:25–0:42 · Panorama
**Tela:** role até os cards

> A base: dos 4.441 anúncios de Airbnb, 780 têm preço capturado — é sobre eles
> que a receita é estimada. Diária mediana de R$ 570 e ocupação de 77% na alta
> temporada, que eu infiro pelas datas que somem do calendário entre capturas.

---

## 0:42–0:58 · Localização — receita por bairro
**Tela:** barras horizontais por bairro

> Primeiro achado, e ele é contraintuitivo: a receita por imóvel quase não muda
> entre bairros — fica entre 79 e 91 mil ao ano. Meia Praia fatura mais como
> mercado porque tem 483 anúncios, não porque cada imóvel renda mais. Se a
> receita é parecida, o que decide o retorno é o preço de compra.

---

## 0:58–1:28 · Yield líquido por célula (bairro × quartos)
**Tela:** gráfico de barras verticais — o coração da apresentação

> E é o que aparece aqui. A diária vai de R$ 455 num quarto a R$ 980 em quatro
> quartos, pouco mais que o dobro. O preço de compra vai de 890 mil a 3,7
> milhões, mais de quatro vezes. A receita escala menos que o preço. Resultado:
> compacto entre 5,4% e 6,2% líquido ao ano, três quartos em 4,1%, quatro
> quartos em 2,9%. Cerca de duas vezes o retorno.

---

## 1:28–1:40 · Preço de compra × receita anual
**Tela:** dispersão

> A dispersão confirma: conforme o preço de compra sobe no eixo, a receita não
> acompanha na mesma inclinação.

---

## 1:40–2:05 · Robustez — cenários de estresse
**Tela:** as duas tabelas (uma premissa por vez + adversariais S1/S2/S3)

> Testei contra estresse: ocupação 20% menor, sazonalidade pior, taxa de
> administração, tudo combinado, e mais três cenários que saíram de uma revisão
> adversarial. O bloco dos compactos fica acima dos grandes em todos. Mas repare
> no S3: contando só os 91 dias que eu realmente observei, o yield cai para
> cerca de 1%. Três quartos do retorno vêm de um inverno para o qual não tenho
> dado nenhum. É por isso que recomendo piloto.

---

## 2:05–2:35 · Como usei IA
**Tela:** ÚNICO CORTE — rosto na câmera, ou `ai-log/05-adversarial.md` aberto
**Enquadramento:** olhe para a câmera. É o trecho mais pessoal do vídeo.

> Trabalhei por fases, aprovando cada uma. O que importa é onde discordei. Num
> recálculo, a IA anualizou usando diária fixa de R$ 612 para 75% do ano — o que
> inflava justamente os compactos, enviesando a favor da conclusão que eu ia
> publicar. Mandei corrigir e o ranking mudou. Depois abri uma sessão nova, sem
> contexto, pedindo que atacasse minha análise como um comitê cético. Achou
> cinco falhas: corrigi quatro, refutei uma por escrito. Tudo no ai-log.

---

## 2:35–2:55 · Recomendação final + Veredito da tese
**Tela:** volte ao dashboard, nas duas últimas seções

> Sobre a tese interna de studio no Centro: metade se confirma. Compactos, sim.
> Centro, não — rende menos que os outros compactos, e existem zero studios e 22
> unidades de um quarto à venda. Não há estoque para escalar. Com mais uma
> semana, eu calibraria minha estimativa de ocupação contra a base real da
> Seazone, três mil imóveis de verdade para medir meu erro, e fecharia com TIR
> incluindo ITBI e mobília.

---

## 2:55–3:00 · Fecho
**Tela:** rosto

> Compacto, bairro de entrada, piloto antes de escalar. Obrigado.

---

## Notas de gravação

- **Regra de ouro:** ao falar um número, ele precisa estar visível na tela naquele
  instante. Não leia a tela — fale e deixe o dashboard confirmar.
- **Áudio** importa mais que imagem: fone com microfone vence microfone de notebook.
- **Luz** na sua frente, não atrás.
- **Sem edição:** grave em tomada única com Loom ou Win+Alt+R, câmera no canto o
  tempo todo. Com ~20 min de edição: rosto dominante na abertura, no bloco de IA
  e no fecho; tela dominante no resto.
- **Se estourar o tempo:** corte o bloco da dispersão (1:28–1:40) e encurte o
  Panorama. Nunca corte o bloco de IA nem o de "mais uma semana" — são duas das
  três perguntas obrigatórias.

## Checklist de publicação

- [ ] Google Drive com compartilhamento em "qualquer pessoa com o link"
- [ ] Link na **primeira linha** do `README.md`
- [ ] Testar o link do vídeo e o repositório em **aba anônima**
- [ ] `ai-log/` com todas as sessões exportadas em texto
- [ ] Formulário enviado uma única vez, links conferidos antes
