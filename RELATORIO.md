<!-- ORIGEM: subagente Claude Code (Fable 5.1) nesta VM, 18/09/2026 20:33-20:52 BRT. Missão: construir o site de marca edgebuildlabs.tech a partir do briefing trabalho/2026-09-18-site-marca-briefing.md, sobre a base blackspike-astro-landing-page (CC BY 4.0). Sem commit, sem push, sem publicação. [EXECUTOR: subagente] até o coordenador conferir. -->

# Site de marca `edgebuildlabs.tech` — relatório de construção

Pasta: `C:/OPERACAO/entregas/site-marca/`. Localhost só; nada publicado.

## O que foi construído

Site estático, Astro 7.3.3 + Tailwind 4.3.3 (os da base), quatro páginas: `/` (PT-BR), `/en/`, `/creditos/`, `/en/creditos/`.
As sete seções do briefing, na ordem, cada uma em um componente:

| Seção | Arquivo | Microinteração (uma por seção) |
|---|---|---|
| Herói: lockup, frase A, subtítulo, um botão | `src/components/HeroSection.astro` | pontos do complementar percorrendo a **junta** do símbolo (canvas 2D, ~26 pontos, desligado em `prefers-reduced-motion`, fora da tela e com aba oculta) |
| Dois caminhos | `CaminhosSection.astro` | cartão sobe 2 px e a borda puxa para o acento |
| Prova de trabalho: dois vídeos, Living World, evidence-contracts | `ProvaSection.astro` + `VideoLite.astro` | botão de play cresce 6 % e ganha halo |
| A escada: `STARTED ≠ COMPLETED ≠ VALIDATED ≠ PASS` | `EscadaSection.astro` | cada degrau entra ao aparecer na tela (`animation-timeline: view()`, só CSS, com `@supports`) |
| Faixa técnica → `edgebuildlabs.github.io` | `FaixaSection.astro` | seta desliza |
| Contato: e-mail, X, issue | `ContatoSection.astro` | sublinhado cresce da esquerda |
| Rodapé: três linhas, crédito, tema | `FooterMain.astro` | — (cabeçalho: o símbolo gira 180° no hover e continua o mesmo símbolo, que é a prova do encaixe) |

Também: `HeaderMain.astro` (lockup, nav por âncora em ≥768 px, troca PT/EN, botão de tema), `BotaoTema.astro`,
`Simbolo.astro` e `Wordmark.astro` (**gerados por script dos SVGs do kit**, caminhos copiados literalmente),
`Site.astro` (monta a página com um dicionário de texto), `Creditos.astro`, `layouts/Layout.astro` (head, canonical,
`hreflang` PT/EN/x-default, OG com a capa do kit, preload da fonte, script de tema antes da primeira pintura).

Texto: `src/data/pt.json` e `src/data/en.json`, mesma estrutura. Tokens: `src/brand/tokens.css` (hex do kit, neutros do
`site-style.css` da tese, `@font-face`). Estilo global: `src/assets/css/global.css`. Capas dos vídeos: `src/assets/posters/`
(quadros extraídos com ffmpeg dos mp4 em `entregas/explicativo-15s/out/ExplicativoV1Wide.mp4` e
`entregas/anuncio-01/out/anuncio-01-16x9.mp4`, 20,05 s e 32,04 s — batem com os dois vídeos do briefing; Astro gera AVIF).

Player "lite" próprio (vanilla, dentro de `VideoLite.astro`): até o clique só existe a capa servida daqui e um botão; no clique
o script cria o iframe `https://www.youtube-nocookie.com/embed/ID?autoplay=1&rel=0`. Zero dependência nova; o `swiper` da base
continua no `package.json` mas não é importado em lugar nenhum (pode ser removido do `package.json` pelo coordenador).

Ferramentas na pasta: `capturar.py` (serve `dist/`, registra rede, capturas, folha) e `conferir.py` (símbolo, wordmark, hex, fonte
contra os arquivos do kit). `README.md` explica onde mexer. `LICENSE-blackspike-CC-BY-4.0.txt` é a licença do tema.

## Como rodar

```
cd C:/OPERACAO/entregas/site-marca
npm install
npm run build
python -m http.server 8765 --directory dist
```

Depois `python conferir.py` e `python capturar.py` regeram a evidência abaixo.

## Aceitação — evidência

### 1. `npm run build` código 0; `dist/` estático `[DEMO]`

Última execução 18/09/2026 20:48: `4 page(s) built in 835ms`, `BUILD_EXIT=0`. Conteúdo de `dist/` (1,9 MB, dos quais 1,64 MB são
as duas cópias da fonte):

```
_astro/Layout.*.css  _astro/Site.*.css  _astro/explicativo-20s.*.avif  _astro/anuncio-32s.*.avif
index.html  en/index.html  creditos/index.html  en/creditos/index.html
favicon.svg  favicon-64.png  icone-800.png  og-2048x1152.png  manifest.json
fonte/OFL.txt  fonte/SourceSerif4-variavel.ttf  fonte/SourceSerif4-variavel.woff2
```

Não há `.js` separado: o Astro embutiu os três scripts (tema, canvas, player) nos HTML.

### 2. Rede: só o próprio host `[DEMO]`

`capturar.py` serve `dist/` com `http.server` em porta livre e registra `page.on("request")` de `/` e `/en/` com movimento ligado e
rolagem até o fim (para as capas `loading="lazy"`). Lista completa, 18/09/2026 20:48 (`capturas/relatorio-captura.json`):

```
/      hosts: ['127.0.0.1:64488']   6 requisições
       http://127.0.0.1:64488/
       http://127.0.0.1:64488/fonte/SourceSerif4-variavel.woff2
       http://127.0.0.1:64488/_astro/Layout.CCKUvLMI.css
       http://127.0.0.1:64488/_astro/Site.ChK7Ujqp.css
       http://127.0.0.1:64488/_astro/explicativo-20s.BvZF9pgv_1emTmJ.avif
       http://127.0.0.1:64488/_astro/anuncio-32s.Bo3SXT4K_Z1g1tzx.avif
/en/   hosts: ['127.0.0.1:64488']   6 requisições (mesmos caminhos, com /en/)
```

Depois do clique no play: `iframes_antes: 0`, `iframe_src: https://www.youtube-nocookie.com/embed/z09-YYVPqCE?autoplay=1&rel=0`, e aí
sim aparecem `youtube-nocookie.com`, `googlevideo.com`, `i.ytimg.com`, `gstatic.com`, `google.com`, `jnn-pa.googleapis.com`,
`yt3.ggpht.com` — é o player do YouTube, só depois do clique, como o briefing prevê. Antes do clique, nada.

`conferir.py` varre HTML e CSS do `dist/` por `https?://`: fora de `<a href>`, `canonical/alternate`, OG e o template do iframe,
sobra só `http://www.w3.org` (xmlns dos SVG inline; não é requisição). PASS.

### 3. Capturas `[DEMO]`

`capturas/` (ignorada pelo git): `pt|en` × `dark|light` × `1440|1024|768|390`, página inteira, `reduced_motion="reduce"`, mais
`pt-dark-creditos-1024.png`. Folha: **`entregas/site-marca/folha-apresentacao.png`** (quatro larguras no escuro, 1440/1024/768 a
50 %, 390 a 70 %). No 390 o corpo é 17 px e o menor texto é o rodapé a 14,4 px; legível sem zoom nas capturas.

### 4. Checklist de oito itens

**Primeira resposta (após a primeira captura, 20:45):**

1. Ponto de vista — uma frase e uma prova; o site diz uma coisa só. OK.
2. Tipografia — uma família (Source Serif 4, variável, `opsz` automático) + mono do sistema para rótulos; hierarquia por tamanho. **Kickers a 0,75 rem em tinta-fraca ficavam ilegíveis no claro; legenda dos vídeos miúda; display a 5,5 rem apertava em 1440.**
3. Cor — três hex do kit + neutros; acento em um lugar por seção. OK.
4. Hierarquia — título enorme, lead, corpo; espaço entre seções `clamp(4.5rem, 10vw, 8.5rem)`. OK.
5. Imagem — **capas dos vídeos não apareciam em 1024/768 e no claro** (era `loading="lazy"` sem rolagem antes da captura, não o site); **play centrado cobria o texto do quadro**.
6. Movimento — uma por seção, todas sob `prefers-reduced-motion`. OK.
7. Mobile — símbolo em cima, cartões empilhados, escada com régua à esquerda, contato com réguas; nav some abaixo de 768 (página curta, sem hambúrguer). OK.
8. "Invisível" — skip link, foco visível, `aria-pressed` no tema, `hreflang`, OG, manifest, tema sem flash. OK.

**Lote de correção (um só, guiado por intenção "que a prova se veja e o pequeno se leia"):** kicker 0,8 rem em tinta-suave;
legenda de vídeo 0,97 rem; display máx. 5 rem; play no canto inferior esquerdo (3,75 rem); capa do explicativo trocada para o
quadro da escada (14 s) e a do anúncio para o título "Living World" (6 s); `capturar.py` rola a página antes de capturar.

**Segunda resposta (20:48):** 2 e 5 resolvidos nas capturas; os demais sem mudança. O que ainda vejo e não mexi: em 1440 o herói
tem quatro linhas de título (é o par de frases quebrando em duas cada; ficaria em três só reduzindo mais a fonte, e preferi o
tamanho); o `≠` mono depende da fonte mono do sistema (renderizou bem no Chromium do Windows; em outro sistema é outra mono).

### 5. Símbolo, wordmark, hex e fonte iguais aos do kit `[DEMO]`

`python conferir.py`, 18/09/2026 20:48 — 22 linhas PASS, RESULTADO PASS:

- os 2 caminhos de `simbolo.svg` estão no HTML (6 ocorrências em `index.html`: cabeçalho, herói e rodapé × 2 caminhos), os 13 caminhos de
  `wordmark.svg` estão no HTML, viewBox `-1 -774 7072 1048` preservado; idem em `/en/`;
- `tokens.css` escuro/claro: fundo `#14130f`/`#fbfaf7`, principal `#ece7dd`/`#14130f`, complementar `#d7b174`/`#7a5c2e` — os mesmos
  do README do kit; os cinco hex aparecem no CSS gerado;
- `dist/fonte/SourceSerif4-variavel.ttf` sha256 `97b2d4da6e3cb494…` == `kit/fonte/SourceSerif4[opsz,wght].ttf`;
  `dist/fonte/OFL.txt` sha256 `5f94c3fd3a23131a…` == o do kit; os dois lado a lado;
- `SourceSerif4-variavel.woff2` (428 500 bytes): descomprimido, só `DSIG` e `head` (checksum) diferem do TTF; 1463 glifos iguais;
  `name ID 0` (copyright com RFN "Source") idêntico;
- Playwright: `document.fonts.check('600 24px "Source Serif 4"') = true` e `"Source Serif 4 200 900 loaded"` nas duas páginas,
  carregada de `/fonte/SourceSerif4-variavel.woff2` do próprio host.

### 6. Lighthouse

**Não rodado.** Não há `lighthouse` instalado nesta VM e `npx lighthouse` baixaria pacote novo. Sem número.

## Decisões que tomei sozinho

1. **Fonte servida em WOFF2 sem subset.** Primeiro gerei um subset latino (199 KB), depois li a fonte primária: o binário declara
   `Reserved Font Name "Source"` no `name ID 0` (o `OFL.txt` do google/fonts não declara), e a FAQ do OFL, lida hoje em
   `openfontlicense.org/ofl-faq/`, diz em **2.6** que subset é modificação e não pode usar o RFN, e em **2.2.1** que WOFF/WOFF2 com os
   dados inalterados pode. Descartei o subset; servi o WOFF2 de conversão pura (428 KB) com o TTF original (1,2 MB) como fallback e
   ao lado do OFL. Custo: 428 KB no primeiro acesso, `font-display: swap`, preload. Se o Owner quiser 4× menos, o caminho lícito é
   subset **renomeado** (por exemplo "EBL Serif") — decisão dele.
2. **Arquivos da fonte renomeados** para `SourceSerif4-variavel.*` (bytes idênticos, sha256 no `/creditos/`): evita colchetes na URL.
3. **Capas dos vídeos são quadros dos próprios vídeos**, extraídas localmente; a miniatura do YouTube (`i.ytimg.com`) seria requisição a
   terceiro antes do clique.
4. **Tema escuro é o padrão sem consultar `prefers-color-scheme`**: o kit chama o escuro de principal, e o toggle guarda a escolha em
   `localStorage` (`ebl-tema`), único estado no navegador. Fácil de inverter se o Owner preferir seguir o sistema como a tese faz.
5. **Símbolo e wordmark inline por componente gerado**, não pelo import de SVG do Astro: os SVG do kit têm `<style>` com `:root` que
   sobrescreveria as variáveis do tema claro.
6. **Nav só por âncora e escondida abaixo de 768 px**, sem hambúrguer (menos JS; a página é curta e o herói tem o botão).
7. Removi da base tudo que era do tema (imagens, seções, dialog, newsletter, Inter); o `package.json` mantém o nome da base e o
   `swiper` sem uso — deixei para o coordenador decidir.
8. Herói com frase A, QSOP fora, e-mail público, PT + EN: os padrões do briefing, marcados `[PROP]` no `HeroSection.astro`.

## Marcado `NÃO VERIFICADO` no código (para o Owner decidir)

- `CaminhosSection.astro`: "Duas rodadas de revisão incluídas", "Prazo típico de dias, não semanas", "Roda no seu servidor ou no
  nosso" — texto de partida, sem fonte.
- `ProvaSection.astro`: data de publicação dos dois vídeos no YouTube e o detalhe "narração/trilha feitas com agentes".
- `FooterMain.astro`: a primeira linha presume que o site vai ser servido do mesmo VPS do Living World, como a tese.
- Fatos com data no texto: Living World desde 05/09/2026 (da tese); fonte copiada em 18/09/2026 (do kit).

## O que o Owner deve olhar primeiro

1. **`folha-apresentacao.png`** — as quatro larguras de uma vez; depois `capturas/pt-light-1440.png` para o claro.
2. **O herói**: frase A ou B, e se o símbolo à direita em 1440 (27 rem) está no tamanho que ele quer.
3. **Os três `NÃO VERIFICADO` dos cartões** (revisões, prazo, "seu servidor ou o nosso") — são as únicas frases que prometem algo.
4. **Fonte: 428 KB ou subset renomeado** (decisão 1).
5. Rodar `npm run dev` na pasta e mexer no `pt.json`: as frases são dele.

## Tempos

Início 20:33, fim 20:52 (19 min): leitura, cópia e poda da base, tokens, componentes, PT/EN, build, dois laços de captura, um lote
de correção, conferência, relatório.
