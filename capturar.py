"""Laço de captura e conferência do site (Playwright, Python).

Uso:  python capturar.py            (depois de `npm run build`)

- serve dist/ numa porta livre com http.server
- registra TODA requisição de rede de /, /en/ e /video/ (a lista tem de ser só o próprio host)
- capturas de página inteira nos dois temas em 1440, 1024, 768 e 390 px -> capturas/
- confere a fonte carregada, o clique no vídeo (iframe youtube-nocookie só depois do clique)
- monta uma folha de apresentação por página (quatro larguras, tema escuro) em capturas/
- sai com código 1 se alguma requisição antes do clique for de outro host, se houver iframe antes do clique
  ou se a fonte não carregar
"""
from __future__ import annotations

import json
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parent
DIST = RAIZ / "dist"
CAP = RAIZ / "capturas"
CAP.mkdir(exist_ok=True)

LARGURAS = [1440, 1024, 768, 390]
TEMAS = ["dark", "light"]
PAGINAS = ["/", "/en/", "/video/"]
PREFIXO = {"/": "pt", "/en/": "en", "/video/": "video"}  # nome das capturas: <prefixo>-<tema>-<largura>.png
FOLHA = {"pt": "folha-apresentacao.png", "en": "folha-apresentacao-en.png", "video": "folha-apresentacao-video.png"}


def porta_livre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def main() -> int:
    porta = porta_livre()
    srv = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(porta), "--bind", "127.0.0.1", "--directory", str(DIST)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{porta}"
    proprio = f"127.0.0.1:{porta}"
    time.sleep(0.8)
    relatorio: dict = {"base": base, "rede": {}, "fonte": {}, "video": {}, "capturas": [], "falhas": []}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()

            # 1) rede: toda requisição das duas páginas, sem tema forçado, movimento ligado (caso real)
            for pag in PAGINAS:
                ctx = browser.new_context(viewport={"width": 1440, "height": 900})
                page = ctx.new_page()
                reqs: list[str] = []
                page.on("request", lambda r: reqs.append(r.url))
                page.goto(base + pag, wait_until="networkidle")
                page.mouse.wheel(0, 20000)  # força lazy-load das capas
                page.wait_for_timeout(1200)
                page.wait_for_load_state("networkidle")
                antes_clique = list(reqs)  # snapshot: o que veio depois do clique no vídeo fica em "video"
                hosts = sorted({urlparse(u).netloc for u in antes_clique})
                relatorio["rede"][pag] = {"requisicoes": antes_clique, "hosts": hosts}
                if hosts != [proprio]:
                    relatorio["falhas"].append(f"{pag}: requisição a outro host antes do clique: {hosts}")

                # fonte servida daqui?
                fonte = page.evaluate(
                    """async () => { await document.fonts.ready;
                        return { check: document.fonts.check('600 24px "Source Serif 4"'),
                                 carregadas: [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family + ' ' + f.weight + ' ' + f.status),
                                 h1: getComputedStyle(document.querySelector('h1')).fontFamily } }"""
                )
                relatorio["fonte"][pag] = fonte
                if not fonte["check"]:
                    relatorio["falhas"].append(f"{pag}: Source Serif 4 não carregou")

                # vídeo: antes do clique nenhum iframe; depois, iframe do youtube-nocookie e requisições só a partir daí
                antes = page.evaluate("document.querySelectorAll('iframe').length")
                n_antes = len(reqs)
                page.click(".video .video-play >> nth=0")
                page.wait_for_timeout(2500)
                src = page.evaluate("document.querySelector('iframe') && document.querySelector('iframe').src")
                depois = sorted({urlparse(u).netloc for u in reqs[n_antes:]})
                relatorio["video"][pag] = {"iframes_antes": antes, "iframe_src": src, "hosts_apos_clique": depois}
                if antes != 0 or not (src or "").startswith("https://www.youtube-nocookie.com/embed/"):
                    relatorio["falhas"].append(f"{pag}: player fora do combinado (iframes antes={antes}, src={src})")
                ctx.close()

            # 2) capturas: dois temas, quatro larguras, movimento desligado
            for tema in TEMAS:
                for w in LARGURAS:
                    ctx = browser.new_context(
                        viewport={"width": w, "height": 900},
                        device_scale_factor=1,
                        reduced_motion="reduce",
                    )
                    ctx.add_init_script(f"try{{localStorage.setItem('ebl-tema','{tema}')}}catch(e){{}}")
                    page = ctx.new_page()
                    for pag in PAGINAS:
                        page.goto(base + pag, wait_until="networkidle")
                        page.evaluate("document.fonts.ready")
                        # rola a página inteira para as capas (loading=lazy) carregarem antes da captura
                        altura = page.evaluate("document.documentElement.scrollHeight")
                        for y in range(0, altura, 600):
                            page.mouse.wheel(0, 600)
                            page.wait_for_timeout(40)
                        page.wait_for_load_state("networkidle")
                        page.evaluate("window.scrollTo(0, 0)")
                        page.wait_for_timeout(400)
                        nome = f"{PREFIXO[pag]}-{tema}-{w}.png"
                        page.screenshot(path=str(CAP / nome), full_page=True)
                        relatorio["capturas"].append(nome)
                    ctx.close()

            # 3) créditos e privacidade, só escuro 1024, para conferir
            ctx = browser.new_context(viewport={"width": 1024, "height": 900}, reduced_motion="reduce")
            page = ctx.new_page()
            for pag, nome in [
                ("/creditos/", "pt-dark-creditos-1024.png"),
                ("/privacidade/", "pt-dark-privacidade-1024.png"),
                ("/en/privacidade/", "en-dark-privacidade-1024.png"),
            ]:
                page.goto(base + pag, wait_until="networkidle")
                page.screenshot(path=str(CAP / nome), full_page=True)
                relatorio["capturas"].append(nome)
            ctx.close()
            browser.close()
    finally:
        srv.terminate()

    # 4) folhas: por página, quatro larguras no escuro, lado a lado, escala 0,5 (390 em 0,7 para ler)
    escalas = {1440: 0.5, 1024: 0.5, 768: 0.5, 390: 0.7}
    relatorio["folhas"] = []
    for pag in PAGINAS:
        prefixo = PREFIXO[pag]
        ims = []
        for w in LARGURAS:
            im = Image.open(CAP / f"{prefixo}-dark-{w}.png").convert("RGB")
            s = escalas[w]
            ims.append((w, im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)))
        gap, topo = 40, 56
        W = sum(i.width for _, i in ims) + gap * (len(ims) + 1)
        H = max(i.height for _, i in ims) + topo + gap
        folha = Image.new("RGB", (W, H), "#0b0b09")
        d = ImageDraw.Draw(folha)
        x = gap
        for w, im in ims:
            d.text((x, 18), f"{pag}  {w} px  (tema escuro, {int(escalas[w]*100)} %)", fill="#b3aca0")
            folha.paste(im, (x, topo))
            d.rectangle([x - 1, topo - 1, x + im.width, topo + im.height], outline="#33302a")
            x += im.width + gap
        folha.save(CAP / FOLHA[prefixo])
        relatorio["folhas"].append(str(CAP / FOLHA[prefixo]))

    (CAP / "relatorio-captura.json").write_text(json.dumps(relatorio, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: relatorio[k] for k in ("rede", "fonte", "video")}, indent=2, ensure_ascii=False))
    print("capturas:", len(relatorio["capturas"]), "| folhas:", ", ".join(relatorio["folhas"]))
    for f in relatorio["falhas"]:
        print("FAIL", f)
    print("RESULTADO:", "FAIL" if relatorio["falhas"] else "PASS")
    return 1 if relatorio["falhas"] else 0


if __name__ == "__main__":
    sys.exit(main())
