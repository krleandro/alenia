#!/usr/bin/env python3
"""
Hiperlinks Automáticos do Códice de Alenia (Biblioteca Hiperconectada)
Conecta automaticamente códigos canônicos em todos os tomos HTML:
  - H01–H64  → Herbário de Seleni (10_Herbario_de_Seleni.html#hXX)
  - C01–C44  → Pratos das Cozinhas de Alenia (12_Cozinhas_de_Alenia.html#cXX)
  - A01–A26  → Animais das Cozinhas de Alenia (12_Cozinhas_de_Alenia.html#aXX)
  - B01–B06  → Complementos Agrícolas da Despensa (12_Cozinhas_de_Alenia.html#bXX)
  - T001–T100 → Crônica das Terras e das Marés (11_Cronica_das_Terras_e_das_Mares.html#tXXX)
  - Tomo I–XII → Navegação direta entre os 12 tomos oficiais da biblioteca
"""
import html
import os
import re

CODEX_CSS = r"""
/* =====================================================
   HIPERLINKS DO CÓDICE DE ALENIA (H / C / A / B / T / TOMOS)
   ===================================================== */
.codex-anchor {
    display: inline-block;
    width: 0;
    height: 0;
    overflow: hidden;
    vertical-align: top;
    scroll-margin-top: 78px;
}
a.codex-ref {
    display: inline-block;
    font-family: 'Cinzel', Georgia, serif;
    font-size: 0.84em;
    font-weight: 700;
    letter-spacing: 0.04em;
    line-height: 1.25;
    padding: 0 5px;
    border-radius: 2px;
    text-decoration: none !important;
    border: 1px solid transparent;
    transition: background 0.14s ease, border-color 0.14s ease, color 0.14s ease, transform 0.12s ease;
    vertical-align: baseline;
    white-space: nowrap;
}
a.codex-ref:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 6px rgba(42, 26, 12, 0.16);
}
a.codex-ref.codex-h {
    background: rgba(31, 81, 86, 0.11);
    border-color: rgba(31, 81, 86, 0.34);
    color: #164044;
}
a.codex-ref.codex-h:hover {
    background: #1f5156;
    border-color: #163b3f;
    color: #f7f1e3;
}
a.codex-ref.codex-c {
    background: rgba(122, 31, 29, 0.10);
    border-color: rgba(122, 31, 29, 0.34);
    color: #6b1b19;
}
a.codex-ref.codex-c:hover {
    background: #7a1f1d;
    border-color: #531312;
    color: #fff6e0;
}
a.codex-ref.codex-a {
    background: rgba(138, 92, 38, 0.12);
    border-color: rgba(138, 92, 38, 0.38);
    color: #5b3a15;
}
a.codex-ref.codex-a:hover {
    background: #7a4f1f;
    border-color: #533412;
    color: #fff6e0;
}
a.codex-ref.codex-b {
    background: rgba(94, 108, 38, 0.12);
    border-color: rgba(94, 108, 38, 0.38);
    color: #3d4816;
}
a.codex-ref.codex-b:hover {
    background: #53621f;
    border-color: #384214;
    color: #fff6e0;
}
a.codex-ref.codex-t {
    background: rgba(154, 123, 59, 0.15);
    border-color: rgba(154, 123, 59, 0.46);
    color: #563f14;
}
a.codex-ref.codex-t:hover {
    background: #8a6c2f;
    border-color: #624b1d;
    color: #fff6e0;
}
a.codex-ref.codex-n {
    background: rgba(88, 36, 72, 0.11);
    border-color: rgba(88, 36, 72, 0.36);
    color: #4c1b3d;
}
a.codex-ref.codex-n:hover {
    background: #5c224a;
    border-color: #3f1532;
    color: #fff6e0;
}
a.codex-ref.codex-e {
    background: rgba(27, 73, 101, 0.12);
    border-color: rgba(27, 73, 101, 0.38);
    color: #163b52;
}
a.codex-ref.codex-e:hover {
    background: #1b4965;
    border-color: #113044;
    color: #f7f1e3;
}
a.codex-ref.codex-m {
    background: rgba(107, 68, 35, 0.13);
    border-color: rgba(107, 68, 35, 0.40);
    color: #4d2e14;
}
a.codex-ref.codex-m:hover {
    background: #6b4423;
    border-color: #4a2e16;
    color: #fff6e0;
}
a.codex-ref.codex-f {
    background: rgba(122, 31, 29, 0.11);
    border-color: rgba(122, 31, 29, 0.38);
    color: #6b1b19;
}
a.codex-ref.codex-f:hover {
    background: #7a1f1d;
    border-color: #531312;
    color: #fff6e0;
}
a.codex-ref.codex-d {
    background: rgba(46, 90, 68, 0.12);
    border-color: rgba(46, 90, 68, 0.38);
    color: #1e4431;
}
a.codex-ref.codex-d:hover {
    background: #2e5a44;
    border-color: #1d3b2c;
    color: #f7f1e3;
}
a.codex-ref.codex-g {
    background: rgba(92, 64, 40, 0.13);
    border-color: rgba(92, 64, 40, 0.40);
    color: #462f1b;
}
a.codex-ref.codex-g:hover {
    background: #5c4028;
    border-color: #3d2a19;
    color: #fff6e0;
}
a.codex-ref.codex-s {
    background: rgba(138, 36, 32, 0.11);
    border-color: rgba(138, 36, 32, 0.38);
    color: #6b1b19;
}
a.codex-ref.codex-s:hover {
    background: #7a1f1d;
    border-color: #531312;
    color: #fff6e0;
}
a.codex-ref.codex-v {
    background: rgba(138, 100, 34, 0.14);
    border-color: rgba(138, 100, 34, 0.42);
    color: #5a3e10;
}
a.codex-ref.codex-v:hover {
    background: #7d5b24;
    border-color: #563e17;
    color: #fff8e6;
}
a.codex-ref.codex-u {
    background: rgba(41, 56, 69, 0.13);
    border-color: rgba(41, 56, 69, 0.42);
    color: #1f2d38;
}
a.codex-ref.codex-u:hover {
    background: #293845;
    border-color: #19242d;
    color: #f7f1e3;
}
a.codex-ref.codex-p {
    background: rgba(90, 66, 40, 0.12);
    border-color: rgba(90, 66, 40, 0.38);
    color: #45311c;
}
a.codex-ref.codex-p:hover {
    background: #5a4228;
    border-color: #3d2c1a;
    color: #fff6e0;
}
a.codex-ref.codex-tome {
    font-family: inherit;
    font-size: inherit;
    font-weight: 600;
    letter-spacing: normal;
    padding: 0 2px;
    background: transparent;
    border: none;
    border-bottom: 1px dotted rgba(122, 31, 29, 0.55);
    border-radius: 0;
    color: #6b1b19;
}
a.codex-ref.codex-tome:hover {
    transform: none;
    box-shadow: none;
    border-bottom-style: solid;
    background: rgba(154, 123, 59, 0.14);
    color: #4f1110;
}

/* Inside tag pills keep links crisp and compact */
.cul-tag a.codex-ref,
.casas-tag a.codex-ref,
.feitos-tag a.codex-ref,
.nav-tag a.codex-ref {
    font-size: 1em;
    padding: 0 4px;
    margin: 0 1px;
}

/* Destaque temporário ao saltar para uma ficha / planta / prato / animal */
@keyframes codexTargetPulse {
    0%   { background-color: rgba(205, 162, 74, 0.42); box-shadow: 0 0 0 4px rgba(154, 123, 59, 0.32); }
    65%  { background-color: rgba(205, 162, 74, 0.22); box-shadow: 0 0 0 2px rgba(154, 123, 59, 0.18); }
    100% { background-color: transparent; box-shadow: none; }
}
.codex-target-flash {
    animation: codexTargetPulse 2.1s ease-out;
    border-radius: 3px;
}
tr[id] { scroll-margin-top: 84px; }
@media print {
    a.codex-ref {
        background: none !important;
        border: none !important;
        padding: 0 !important;
        color: inherit !important;
    }
}
"""

TOMO_ROMAN_MAP = {
    "I": ("01_Livro_de_Regras.html", "Tomo I — Livro de Regras"),
    "II": ("02_Livro_do_Cenario.html", "Tomo II — Guia de Cenário"),
    "III": ("03_Catalogo_de_Kits.html", "Tomo III — Catálogo de Kits"),
    "IV": ("04_Bestiario_de_Alenia.html", "Tomo IV — Bestiário de Alenia"),
    "V": ("05_Onomastica_e_Toponimia.html", "Tomo V — Onomástica e Toponímia"),
    "VI": ("06_Guia_do_Jogador.html", "Tomo VI — Guia do Jogador"),
    "VII": ("07_Aventura_Inicial.html", "Tomo VII — Aventura Inicial"),
    "VIII": ("08_Acervo_Oculto_de_Sellene.html", "Tomo VIII — Acervo Oculto de Sellene"),
    "IX": ("09_Catalogo_de_Equipamentos.html", "Tomo IX — Equipamentos e Ofícios"),
    "X": ("10_Herbario_de_Seleni.html", "Tomo X — Herbário de Seleni"),
    "XI": ("11_Cronica_das_Terras_e_das_Mares.html", "Tomo XI — Crônica das Terras e das Marés"),
    "XII": ("12_Cozinhas_de_Alenia.html", "Tomo XII — Cozinhas de Alenia"),
    "XIII": ("13_Grandes_Nomes_e_Feitos_de_Alenia.html", "Tomo XIII — Grandes Nomes e Feitos de Alenia"),
    "XIV": ("14_Mares_Frotas_e_Navegacao.html", "Tomo XIV — Mares, Frotas e Navegação de Alenia"),
    "XV": ("15_Casas_Nobres_e_Fortificacoes.html", "Tomo XV — Casas Nobres, Feudos e Fortificações"),
    "XVI": ("16_Feitos_de_Fe_Status_e_Submundo.html", "Tomo XVI — O Peso do Nome, do Voto e da Sombra"),
}

# Book index prefix inside Alenia_Compendio_Completo.html (matches id_prefix=f"t{idx+1}-")
COMPENDIUM_PREFIX = {
    "H": "t10-",
    "T": "t11-",
    "C": "t12-",
    "A": "t12-",
    "B": "t12-",
    "N": "t13-",
    "E": "t14-",
    "M": "t14-",
    "F": "t15-",
    "D": "t15-",
    "G": "t15-",
    "S": "t16-",
    "V": "t16-",
    "U": "t16-",
    "P": "t16-",
}

# Target HTML file for each codex family
FAMILY_FILE = {
    "H": "10_Herbario_de_Seleni.html",
    "T": "11_Cronica_das_Terras_e_das_Mares.html",
    "C": "12_Cozinhas_de_Alenia.html",
    "A": "12_Cozinhas_de_Alenia.html",
    "B": "12_Cozinhas_de_Alenia.html",
    "N": "13_Grandes_Nomes_e_Feitos_de_Alenia.html",
    "E": "14_Mares_Frotas_e_Navegacao.html",
    "M": "14_Mares_Frotas_e_Navegacao.html",
    "F": "15_Casas_Nobres_e_Fortificacoes.html",
    "D": "15_Casas_Nobres_e_Fortificacoes.html",
    "G": "15_Casas_Nobres_e_Fortificacoes.html",
    "S": "16_Feitos_de_Fe_Status_e_Submundo.html",
    "V": "16_Feitos_de_Fe_Status_e_Submundo.html",
    "U": "16_Feitos_de_Fe_Status_e_Submundo.html",
    "P": "16_Feitos_de_Fe_Status_e_Submundo.html",
}

FAMILY_LABEL = {
    "H": "Herbário de Seleni",
    "C": "Prato das Cozinhas",
    "A": "Fauna das Cozinhas",
    "B": "Despensa Agrícola",
    "T": "Crônica de Alenia",
    "N": "Grandes Nomes de Alenia",
    "E": "Embarcação de Alenia",
    "M": "Arsenal Marítimo",
    "F": "Fortificação Senhorial",
    "D": "Defesa / Obra de Feudo",
    "G": "Guarnição e Corte",
    "S": "Trilha de Status",
    "V": "Trilha de Fé Verdadeira",
    "U": "Trilha de Submundo",
    "P": "Feito / Provação de Campanha",
}


def build_codex_registry(root_dir: str) -> dict:
    """Scan canonical markdown books once to build {code: display_name} lookup tables."""
    reg = {"H": {}, "C": {}, "A": {}, "B": {}, "T": {}, "N": {}, "E": {}, "M": {}, "F": {}, "D": {}, "G": {}, "S": {}, "V": {}, "U": {}, "P": {}, "N_GM": set()}

    # 1. Herbário H01–H64
    herb_path = os.path.join(root_dir, "10_Herbario_de_Seleni.md")
    if os.path.exists(herb_path):
        txt = open(herb_path, "r", encoding="utf-8").read()
        for m in re.finditer(r"^###\s+(H\d{2})\s+[—–-]\s+(.+)$", txt, flags=re.M):
            reg["H"][m.group(1)] = m.group(2).strip()

    # 2. Cozinhas C01–C44, A01–A26, B01–B06
    cul_path = os.path.join(root_dir, "12_Cozinhas_de_Alenia.md")
    if os.path.exists(cul_path):
        txt = open(cul_path, "r", encoding="utf-8").read()
        for m in re.finditer(r"^###\s+(C\d{2})\s+[—–-]\s+(.+)$", txt, flags=re.M):
            reg["C"][m.group(1)] = m.group(2).strip()
        for m in re.finditer(r"^###\s+(A\d{2})\s+[—–-]\s+(.+)$", txt, flags=re.M):
            reg["A"][m.group(1)] = m.group(2).strip()
        for m in re.finditer(r"^\|\s*(B0[1-6])\s*\|\s*([^|]+?)\s*\|", txt, flags=re.M):
            reg["B"][m.group(1)] = m.group(2).strip()

    # 3. Crônica T001–T100
    chr_path = os.path.join(root_dir, "11_Cronica_das_Terras_e_das_Mares.md")
    if os.path.exists(chr_path):
        txt = open(chr_path, "r", encoding="utf-8").read()
        for m in re.finditer(r"^###\s+(T\d{3})\s+[—–-]\s+(.+)$", txt, flags=re.M):
            reg["T"][m.group(1)] = m.group(2).strip()

    # 4. Grandes Nomes N001–N100 (90 public + 10 GM-only in "Memórias e ameaças")
    nom_path = os.path.join(root_dir, "13_Grandes_Nomes_e_Feitos_de_Alenia.md")
    if os.path.exists(nom_path):
        txt = open(nom_path, "r", encoding="utf-8").read()
        cur_h2 = ""
        for ln in txt.splitlines():
            m2 = re.match(r"^##\s+(.+)$", ln.strip())
            if m2:
                cur_h2 = m2.group(1).strip()
                continue
            m3 = re.match(r"^###\s+(N\d{3})\s+[—–-]\s+(.+)$", ln.strip())
            if m3:
                reg["N"][m3.group(1)] = m3.group(2).strip()
                if cur_h2 == "Memórias e ameaças":
                    reg["N_GM"].add(m3.group(1))

    # 5. Navegação E01–E12 & Arsenal Marítimo M01–M18
    nav_path = os.path.join(root_dir, "14_Mares_Frotas_e_Navegacao_de_Alenia.md")
    if os.path.exists(nav_path):
        txt = open(nav_path, "r", encoding="utf-8").read()
        for m in re.finditer(r"^###\s+(E\d{2})\s+[—–-]\s+(.+)$", txt, flags=re.M):
            reg["E"][m.group(1)] = m.group(2).strip()
        for m in re.finditer(r"^###\s+(M\d{2})\s+[—–-]\s+(.+)$", txt, flags=re.M):
            reg["M"][m.group(1)] = m.group(2).strip()

    # 6. Casas Nobres & Feudos F01–F10, D01–D16 & G01–G14
    casas_path = os.path.join(root_dir, "15_Casas_Nobres_Feudos_e_Fortificacoes.md")
    if os.path.exists(casas_path):
        txt = open(casas_path, "r", encoding="utf-8").read()
        for m in re.finditer(r"^###\s+(F\d{2})\s+[—–-]\s+(.+)$", txt, flags=re.M):
            reg["F"][m.group(1)] = re.sub(r"\*+", "", m.group(2)).strip()
        for m in re.finditer(r"^###\s+(D\d{2})\s+[—–-]\s+(.+)$", txt, flags=re.M):
            reg["D"][m.group(1)] = re.sub(r"\*+", "", m.group(2)).strip()
        for m in re.finditer(r"^###\s+(G\d{2})\s+[—–-]\s+(.+)$", txt, flags=re.M):
            reg["G"][m.group(1)] = re.sub(r"\*+", "", m.group(2)).strip()

    # 7. Feitos de Status (S01–S05), Fé Verdadeira (V01–V05), Submundo (U01–U05) & Provações (P01–P30)
    feitos_path = os.path.join(root_dir, "16_Feitos_de_Fe_Status_e_Submundo.md")
    if os.path.exists(feitos_path):
        txt = open(feitos_path, "r", encoding="utf-8").read()
        for fam in ("S", "V", "U"):
            for m in re.finditer(rf"^###\s+({fam}0[1-5])\s+[—–-]\s+(.+)$", txt, flags=re.M):
                reg[fam][m.group(1)] = re.sub(r"\*+", "", m.group(2)).strip()
        for m in re.finditer(r"^###\s+(P\d{2})\s+[—–-]\s+(.+)$", txt, flags=re.M):
            reg["P"][m.group(1)] = re.sub(r"\*+", "", m.group(2)).strip()

    return reg


_TOKEN_RE = re.compile(
    r"\b("
    r"H(?:0[1-9]|[1-5][0-9]|6[0-4])"
    r"|C(?:0[1-9]|[1-3][0-9]|4[0-4])"
    r"|A(?:0[1-9]|1[0-9]|2[0-6])"
    r"|B0[1-6]"
    r"|T(?:0\d{2}|100)"
    r"|N(?:0\d{2}|100)"
    r"|E(?:0[1-9]|1[0-2])"
    r"|M(?:0[1-9]|1[0-8])"
    r"|F(?:0[1-9]|10)"
    r"|D(?:0[1-9]|1[0-6])"
    r"|G(?:0[1-9]|1[0-4])"
    r"|S0[1-5]"
    r"|V0[1-5]"
    r"|U0[1-5]"
    r"|P(?:0[1-9]|[12][0-9]|30)"
    r"|Tomo\s+(?:XVI|XV|XIV|XIII|XII|XI|X|IX|VIII|VII|VI|V|IV|III|II|I)"
    r")\b"
)

_SKIP_TAGS = {"a", "h1", "h2", "h3", "h4", "summary", "script", "style", "title", "textarea", "code", "button", "option", "select", "label"}
_SKIP_CLASSES = {
    "cul-code",
    "tl-code-badge",
    "tl-med-code",
    "cul-stat-pill",
    "chronicle-stat-pill",
    "names-code-pill",
    "names-stat-pill",
    "nav-code",
    "nav-stat-pill",
    "casas-code",
    "casas-stat-pill",
    "feitos-code",
    "feitos-stat-pill",
    "idx-code",
    "book-kicker",
    "cul-kicker",
    "names-kicker",
    "nav-kicker",
    "casas-kicker",
    "casas-group-kicker",
    "feitos-kicker",
    "feitos-group-kicker",
    "feitos-insp-kicker",
    "feudo-calc-kicker",
    "feudo-panel-head",
    "cover-num",
}
_TAG_SPLIT_RE = re.compile(r"(<[^>]+>)")
_VOID_TAGS = {"br", "hr", "img", "input", "meta", "link", "source", "area", "col", "embed", "param", "track", "wbr"}


def link_codex_html(
    html_str: str,
    current_file: str,
    registry: dict,
    compendium_mode: bool = False,
    allow_gm_names: bool = False,
) -> str:
    """Safely convert canonical codex codes (H/C/A/B/T/N/Tomo) in HTML text nodes into clickable links."""
    if not html_str:
        return html_str

    parts = _TAG_SPLIT_RE.split(html_str)
    out = []
    # Stack tracks tuples: (tag_name, is_skip, self_code_or_none)
    stack = []
    skip_depth = 0
    current_row_self_code = None

    def replace_text(text: str) -> str:
        def repl(m):
            tok = m.group(1)
            # 1. Tomo I–XIII
            if tok.startswith("Tomo "):
                roman = tok.split()[1]
                # Skip Valerius Malakor's fictional old booklet "Tomo I, Preparo de Peixes"
                after = text[m.end():m.end() + 24]
                if roman == "I" and "Preparo de Peixes" in after:
                    return tok
                info = TOMO_ROMAN_MAP.get(roman)
                if not info:
                    return tok
                target_file, label = info
                if not compendium_mode and target_file == current_file:
                    return tok
                if compendium_mode:
                    book_idx = list(TOMO_ROMAN_MAP.keys()).index(roman) + 1
                    href = f"#tomo-{book_idx}" if roman not in ("IV", "VII", "VIII") else target_file
                else:
                    href = target_file
                return (
                    f'<a class="codex-ref codex-tome" href="{href}" '
                    f'title="Abrir {html.escape(label, quote=True)}">{tok}</a>'
                )

            # 2. H / C / A / B / T / N codes
            fam = tok[0]
            if fam == "N" and (tok in registry.get("N_GM", set())) and not allow_gm_names:
                return tok
            if tok not in registry.get(fam, {}):
                return tok
            if current_row_self_code and tok.lower() == current_row_self_code:
                return tok

            name = registry[fam][tok]
            fam_label = FAMILY_LABEL[fam]
            title_attr = html.escape(f"{fam_label} • {tok} — {name}", quote=True)
            code_l = tok.lower()

            if compendium_mode:
                pref = COMPENDIUM_PREFIX[fam]
                href = f"#{pref}{code_l}"
            else:
                target_file = FAMILY_FILE[fam]
                href = f"#{code_l}" if target_file == current_file else f"{target_file}#{code_l}"

            return f'<a class="codex-ref codex-{fam.lower()}" href="{href}" title="{title_attr}">{tok}</a>'

        return _TOKEN_RE.sub(repl, text)

    for part in parts:
        if not part:
            continue
        if part.startswith("<"):
            out.append(part)
            # Ignore comments / doctype
            if part.startswith("<!--") or part.startswith("<!"):
                continue
            m_close = re.match(r"^</\s*([a-zA-Z0-9]+)", part)
            if m_close:
                tag = m_close.group(1).lower()
                # Pop matching tag from stack
                for idx in range(len(stack) - 1, -1, -1):
                    if stack[idx][0] == tag:
                        _, was_skip, was_row_code = stack.pop(idx)
                        if was_skip:
                            skip_depth = max(0, skip_depth - 1)
                        if was_row_code:
                            current_row_self_code = None
                        break
                continue

            m_open = re.match(r"^<\s*([a-zA-Z0-9]+)", part)
            if m_open:
                tag = m_open.group(1).lower()
                if tag in _VOID_TAGS or part.endswith("/>"):
                    continue
                is_skip = tag in _SKIP_TAGS
                if not is_skip:
                    m_cls = re.search(r'\bclass="([^"]*)"', part)
                    if m_cls:
                        cls_set = set(m_cls.group(1).split())
                        if cls_set & _SKIP_CLASSES:
                            is_skip = True
                row_code = None
                if tag == "tr":
                    m_id = re.search(r'\bid="(?:t12-)?(b0[1-6])"', part)
                    if m_id:
                        row_code = m_id.group(1)
                        current_row_self_code = row_code
                if is_skip:
                    skip_depth += 1
                stack.append((tag, is_skip, row_code))
        else:
            if skip_depth > 0:
                out.append(part)
            else:
                out.append(replace_text(part))

    return "".join(out)
