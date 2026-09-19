"""Confere, por arquivo (não de memória), que o site usa exatamente o kit de identidade.

Uso:  python conferir.py            (depois de `npm run build`)

- os "d" do símbolo e do wordmark no HTML gerado == os do kit (simbolo.svg, wordmark.svg)
- os hex em src/brand/tokens.css == tabela do README do kit
- a fonte em dist/fonte/ tem o sha256 do kit e o OFL.txt está ao lado
- o WOFF2 descomprimido tem as mesmas tabelas do TTF (menos DSIG e head, que o formato altera)
- nenhum HTML/CSS do dist referencia host externo, salvo links <a href> e o iframe criado no clique
"""
from __future__ import annotations

import hashlib
import re
import sys
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
KIT = Path(os.environ.get("KIT_DIR", str(Path(__file__).resolve().parent / "kit")))  # kit de identidade, fora do repositório
DIST = RAIZ / "dist"

ok = True


def marca(cond: bool, msg: str) -> None:
    global ok
    ok = ok and cond
    print(("PASS " if cond else "FAIL ") + msg)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# 1) símbolo e wordmark
kit_simbolo = re.findall(r'<path class="[ab]" d="([^"]+)"', (KIT / "simbolo.svg").read_text(encoding="utf-8"))
kit_wordmark = re.findall(r'<path class="a" d="([^"]+)"', (KIT / "wordmark.svg").read_text(encoding="utf-8"))
html = (DIST / "index.html").read_text(encoding="utf-8")
html_en = (DIST / "en" / "index.html").read_text(encoding="utf-8")
ds = re.findall(r'<path[^>]*? d="([^"]+)"', html)
marca(all(d in ds for d in kit_simbolo), f"símbolo: os 2 caminhos do kit estão no HTML ({sum(ds.count(d) for d in kit_simbolo)} ocorrências)")
marca(all(d in ds for d in kit_wordmark), f"wordmark: os {len(kit_wordmark)} caminhos do kit estão no HTML")
marca(all(d in html_en for d in kit_simbolo + kit_wordmark), "símbolo e wordmark também em /en/")
vb = re.search(r'viewBox="([^"]+)"', (KIT / "wordmark.svg").read_text(encoding="utf-8")).group(1)
marca(f'viewBox="{vb}"' in html, f"wordmark: viewBox do kit ({vb}) preservado")

# 2) hex
readme = (KIT / "README.md").read_text(encoding="utf-8")
tabela = {
    "fundo": ("#14130f", "#fbfaf7"),
    "principal": ("#ece7dd", "#14130f"),
    "complementar": ("#d7b174", "#7a5c2e"),
}
for nome, (esc, cla) in tabela.items():
    marca(esc in readme and cla in readme, f"README do kit contém {nome}: {esc} / {cla}")
tokens = (RAIZ / "src" / "brand" / "tokens.css").read_text(encoding="utf-8")
escuro, claro = tokens.split('html[data-theme="light"] {')
marca("--ebl-fundo: #14130f" in escuro and "--ebl-fundo: #fbfaf7" in claro, "tokens: fundo escuro/claro iguais ao kit")
marca("--ebl-tinta: #ece7dd" in escuro and "--ebl-tinta: #14130f" in claro, "tokens: principal (tinta) escuro/claro iguais ao kit")
marca("--ebl-acento: #d7b174" in escuro and "--ebl-acento: #7a5c2e" in claro, "tokens: complementar (acento) escuro/claro iguais ao kit")
css = "".join(p.read_text(encoding="utf-8") for p in (DIST / "_astro").glob("*.css"))
for hexa in ("#14130f", "#fbfaf7", "#ece7dd", "#d7b174", "#7a5c2e"):
    marca(hexa in css, f"CSS gerado contém {hexa}")

# 3) fonte
ttf = DIST / "fonte" / "SourceSerif4-variavel.ttf"
ofl = DIST / "fonte" / "OFL.txt"
marca(sha(ttf) == sha(KIT / "fonte" / "SourceSerif4[opsz,wght].ttf"), f"TTF servido == TTF do kit (sha256 {sha(ttf)[:16]}…)")
marca(sha(ofl) == sha(KIT / "fonte" / "OFL.txt"), f"OFL.txt servido == OFL do kit (sha256 {sha(ofl)[:16]}…)")
try:
    from fontTools.ttLib import TTFont

    a = TTFont(ttf)
    b = TTFont(DIST / "fonte" / "SourceSerif4-variavel.woff2")
    dif = [t for t in sorted(set(a.keys()) | set(b.keys())) if t != "GlyphOrder" and (a.getTableData(t) if t in a else None) != (b.getTableData(t) if t in b else None)]
    marca(set(dif) <= {"DSIG", "head"}, f"WOFF2: tabelas diferentes do TTF só {dif} (compressão de formato, FAQ OFL 2.2.1)")
    marca(a["name"].getDebugName(0) == b["name"].getDebugName(0), "WOFF2: name ID 0 (copyright/RFN) idêntico")
except ImportError:
    print("SKIP fontTools ausente")
marca("/fonte/SourceSerif4-variavel.woff2" in css and "/fonte/SourceSerif4-variavel.ttf" in css, "CSS aponta para a fonte servida daqui")

# 4) nada externo fora de <a href> e do iframe do clique
externos = set()
for p in list(DIST.rglob("*.html")) + list(DIST.rglob("*.css")):
    txt = p.read_text(encoding="utf-8")
    txt = re.sub(r'<a [^>]*href="https?://[^"]+"', "", txt)
    txt = re.sub(r'<link rel="(canonical|alternate)"[^>]*>', "", txt)
    txt = re.sub(r'<meta property="og:[^"]*" content="https://edgebuildlabs\.tech[^"]*"', "", txt)
    txt = txt.replace("https://www.youtube-nocookie.com/embed/${", "")
    txt = re.sub(r"/\*!.*?\*/", "", txt, flags=re.S)  # comentário de licença do Tailwind no CSS, não é requisição
    externos |= set(re.findall(r'https?://[a-zA-Z0-9.-]+', txt))
# http://www.w3.org é o namespace xmlns dos SVG inline, não é requisição
marca(externos <= {"https://edgebuildlabs.tech", "http://www.w3.org"}, f"HTML/CSS sem host externo além de links e do iframe pós-clique: {sorted(externos)}")

print("\nRESULTADO:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
