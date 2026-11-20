#!/usr/bin/env python3
"""
Gerador Editorial HTML Autocontido com Criptografia AES-256-GCM para Área do Mestre — Alenia RPG (v2.0)
- Copia os 6 mapas para livros_html/assets/
- Criptografa com PBKDF2-HMAC-SHA256 + AES-256-GCM (Web Crypto API) todo conteúdo restrito ao Mestre:
  * Tomo IV (Bestiário completo + sumário)
  * Tomo VII (Aventura Inicial completa + sumário)
  * Seção 7 do Livro do Cenário (Segredos do Regente das Cinzas & Simbionte da Comunhão)
  * Os mesmos blocos dentro do Compêndio Completo
- A senha é lida via variável de ambiente ALENIA_GM_PASSWORD e NUNCA é gravada nos arquivos gerados.
"""
import base64
import html
import json
import os
import re
import shutil

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT_DIR, "livros_html")
ASSETS_DIR = os.path.join(OUT_DIR, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

EDITION_LABEL = "Edição Revisada v2.0 • RRPG Firecast"
PBKDF2_ITERS = 120000

GM_PASSWORD = os.environ.get("ALENIA_GM_PASSWORD", "")

BOOKS = [
    {
        "src": "01_Livro_de_Regras.md",
        "out": "01_Livro_de_Regras.html",
        "num": "TOMO I",
        "short": "Regras",
        "title": "Livro de Regras",
        "subtitle": "Sistema d20 Sombrio • Dados de Vida, Procedimentos, Preços & Rituais",
        "epigraph": "“O aço quebra, os reis sangram e o mar engole até os mais sábios.”",
        "desc": "Regras revisadas v2.0: 4d6, Atributos Especiais por Feitos, DV por Kit (1d6–1d12), perícias recalibradas (+3/+8/+12 com travas), Defesa situacional, Múltiplas Ações blindadas, procedimentos de mesa, preços e rituais.",
        "cover_map": None,
        "gm_only": False,
    },
    {
        "src": "02_Guia_de_Cenario_Alenia.md",
        "out": "02_Livro_do_Cenario.html",
        "num": "TOMO II",
        "short": "Cenário",
        "title": "Livro do Cenário & Atlas",
        "subtitle": "Crises Ativas, Facções, Religiões, Viagens & 6 Mapas Ilustrados",
        "epigraph": "“Ao norte, além de Thanatos e do Mar das Cinzas, só existe o que os mapas se recusam a nomear.”",
        "desc": "Presente histórico com 6 crises ativas, 6 facções, economia do adamante, vida civil em Kalis e Gaddra, tabela de viagens, religiões, cronologia, 6 mapas embutidos e seção selada exclusiva do Mestre.",
        "cover_map": "assets/alenia_mapa_mundi_atualizado.jpg",
        "gm_only": False,
    },
    {
        "src": "03_Catalogo_de_Kits.md",
        "out": "03_Catalogo_de_Kits.html",
        "num": "TOMO III",
        "short": "36 Kits",
        "title": "Catálogo de Kits Universais",
        "subtitle": "36 Ofícios de Exploradores • Dados de Vida & Habilidades Calibradas",
        "epigraph": "“Em Alenia, nenhum explorador sobrevive apenas pelo sangue — mas pelo ofício que carrega nas mãos.”",
        "desc": "Todos os 36 Kits Universais (+ Sem Kit) com Dado de Vida (1d6 a 1d12), multiplicadores de Inteligência recalibrados, troca de ofício em campanha e habilidades equilibradas para exploração.",
        "cover_map": None,
        "gm_only": False,
    },
    {
        "src": "04_Bestiario_Alenia.md",
        "out": "04_Bestiario_de_Alenia.html",
        "num": "TOMO IV • MESTRE",
        "short": "🔒 Bestiário",
        "title": "Bestiário & Ameaças",
        "subtitle": "Acesso Restrito ao Mestre • Fichas, Táticas & Segredos",
        "epigraph": "“A maioria das feras que matam viajantes usa botas de couro e fala sua própria língua.”",
        "desc": "🔒 Área Restrita ao Mestre: fichas completas de inimigos, feras e ameaças ocultas de Alenia protegidas por criptografia AES-256.",
        "cover_map": None,
        "gm_only": True,
    },
    {
        "src": "05_Onomastica_e_Toponimia_Alenia.md",
        "out": "05_Onomastica_e_Toponimia.html",
        "num": "TOMO V",
        "short": "Onomástica",
        "title": "Onomástica & Toponímia",
        "subtitle": "Tendências Fonéticas, Substratos Históricos, Casas Nobres & Etimologia",
        "epigraph": "“A verossimilhança de um cenário medieval nasce da coesão invisível entre os nomes que habitam esse território.”",
        "desc": "As 5 Fichas Matriz culturais de Alenia, separação entre língua local, tradução vernácula e substrato herdado, sobrenomes de bastardos, casas nobres e etimologia do atlas.",
        "cover_map": None,
        "gm_only": False,
    },
    {
        "src": "06_Guia_do_Jogador_e_Referencia_Rapida.md",
        "out": "06_Guia_do_Jogador.html",
        "num": "TOMO VI",
        "short": "Guia Jogador",
        "title": "Guia do Jogador & Escudo",
        "subtitle": "Criação em 6 Passos & Referência Rápida de Mesa",
        "epigraph": "“Cinco minutos de leitura para colocar seu explorador na estrada.”",
        "desc": "Resumo direto do mundo para jogadores novos, criação passo a passo no Firecast e tabela de consulta rápida para combate, moribundo, cura, exaustão e preços.",
        "cover_map": None,
        "gm_only": False,
    },
    {
        "src": "07_Aventura_Inicial_Cinzas_no_Estuario.md",
        "out": "07_Aventura_Inicial.html",
        "num": "TOMO VII • MESTRE",
        "short": "🔒 Aventura",
        "title": "Aventura Inicial",
        "subtitle": "Acesso Restrito ao Mestre • Bastidores, Cenas & Segredos",
        "epigraph": "“Nem tudo o que a bruma devolve deveria ser encontrado.”",
        "desc": "🔒 Área Restrita ao Mestre: aventura introdutória completa, bastidores da trama, encontros e desfechos protegidos por criptografia AES-256.",
        "cover_map": None,
        "gm_only": True,
    },
]

CHAPTER_MAPS = {
    "1. Visão Geral de Alenia": (
        "assets/alenia_mapa_mundi_atualizado.jpg",
        "Prancha I — Mapa-Múndi de Alenia (48 Topônimos Oficiais)"
    ),
    "2. Reino Capital de Aurora": (
        "assets/mapa_regional_aurora.jpg",
        "Prancha II — Mapa Regional do Reino de Aurora & Conselho das Copas"
    ),
    "3. Liga Talassocrática de Corallis": (
        "assets/mapa_regional_corallis.jpg",
        "Prancha III — Mapa Regional de Corallis & Mar dos Corais"
    ),
    "4. Confederação Tribal de Gaddra": (
        "assets/mapa_regional_gaddra.jpg",
        "Prancha IV — Mapa Regional da Confederação Tribal de Gaddra"
    ),
    "5. Despotado Velado de Kalis": (
        "assets/mapa_regional_kalis.jpg",
        "Prancha V — Mapa Regional do Despotado de Kalis, Mar Intransponível & Ilha das Safiras"
    ),
    "6. Incognito": (
        "assets/mapa_regional_incognito.jpg",
        "Prancha VI — Mapa Regional de Incognito, Ilha de Thanatos & Mar das Cinzas"
    ),
}

# Seções específicas (por prefixo de H2 ou H3) que são seladas para o Mestre mesmo dentro de tomos públicos
GM_SECTION_H2_PREFIXES = (
    "7. A Grande Ameaça:",
)
GM_SECTION_H3_PREFIXES = (
    "O Simbionte da Comunhão",
)


def encrypt_payload(plaintext: str, password: str) -> str:
    salt = os.urandom(16)
    iv = os.urandom(12)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERS,
    )
    key = kdf.derive(password.encode("utf-8"))
    ct = AESGCM(key).encrypt(iv, plaintext.encode("utf-8"), None)
    obj = {
        "v": 1,
        "it": PBKDF2_ITERS,
        "s": base64.b64encode(salt).decode("ascii"),
        "i": base64.b64encode(iv).decode("ascii"),
        "c": base64.b64encode(ct).decode("ascii"),
    }
    return json.dumps(obj, separators=(",", ":"))


def make_gm_gate_block(label: str, subtitle: str, encrypted_body_html: str, encrypted_toc_html: str = "") -> str:
    if not GM_PASSWORD:
        return encrypted_body_html
    payload_obj = {"html": encrypted_body_html, "toc": encrypted_toc_html}
    cipher_json = encrypt_payload(json.dumps(payload_obj, ensure_ascii=False), GM_PASSWORD)
    safe_cipher = cipher_json.replace("</", "<\\/")
    return f"""
    <div class="gm-vault" data-locked="true">
        <script type="application/json" class="gm-cipher">{safe_cipher}</script>
        <div class="gm-gate-box">
            <div class="gm-seal-icon">🔒</div>
            <div class="gm-gate-kicker">SELO DO MESTRE • CONTEÚDO CRIPTOGRAFADO</div>
            <h2 class="gm-gate-title">{html.escape(label)}</h2>
            <p class="gm-gate-desc">{html.escape(subtitle)}</p>
            <form class="gm-unlock-form">
                <input type="password" class="gm-pwd-input" placeholder="Digite a senha do Mestre..." autocomplete="current-password" required />
                <button type="submit" class="gm-unlock-btn">Destrancar Selo</button>
            </form>
            <div class="gm-gate-error" aria-live="polite"></div>
        </div>
        <div class="gm-unlocked-content"></div>
    </div>
    """


SHARED_CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700;800&family=EB+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,600&display=swap');

:root {
    --desk: #171512;
    --vellum: #f7f1e3;
    --vellum-alt: #efe6d2;
    --vellum-card: #f2ead8;
    --ink: #221c16;
    --ink-soft: #4e4336;
    --crimson: #7a1f1d;
    --crimson-dark: #571412;
    --gold: #9a7b3b;
    --gold-light: #cdb06e;
    --border: #cfc2a5;
    --sidebar-w: 280px;
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; background: var(--desk); color: var(--ink); }
body {
    margin: 0;
    font-family: 'EB Garamond', 'Palatino Linotype', 'Book Antiqua', Georgia, serif;
    font-size: 18px;
    line-height: 1.66;
    background: radial-gradient(circle at top, #27221c 0%, #171512 58%, #100e0c 100%);
    min-height: 100vh;
}

.topbar {
    position: fixed; top: 0; left: 0; right: 0; height: 54px;
    background: rgba(18, 16, 13, 0.96);
    border-bottom: 1px solid rgba(154, 123, 59, 0.45);
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 14px; z-index: 1000; backdrop-filter: blur(8px);
}
.topbar-brand {
    font-family: 'Cinzel', Georgia, serif; font-weight: 700; font-size: 14px;
    letter-spacing: 0.14em; color: var(--gold-light); text-decoration: none; white-space: nowrap;
}
.topbar-nav { display: flex; align-items: center; gap: 4px; flex-wrap: wrap; }
.topbar-nav a, .btn-print, .btn-lock {
    font-family: 'Cinzel', Georgia, serif; font-size: 10.5px; letter-spacing: 0.06em;
    text-transform: uppercase; color: #ded5c3; text-decoration: none;
    padding: 5px 8px; border-radius: 3px; border: 1px solid transparent;
    transition: all 0.16s ease; cursor: pointer; background: transparent;
}
.topbar-nav a:hover, .topbar-nav a.active {
    color: var(--gold-light); border-color: rgba(154, 123, 59, 0.55); background: rgba(154, 123, 59, 0.12);
}
.btn-print { background: var(--crimson); border-color: var(--gold); color: #f7f1e3; font-weight: 600; }
.btn-print:hover { background: #922624; color: #fff; }
.btn-lock { display: none; border-color: rgba(205, 176, 110, 0.55); color: var(--gold-light); background: rgba(154, 123, 59, 0.14); }
.btn-lock.visible { display: inline-block; }
.btn-lock:hover { background: rgba(122, 31, 29, 0.65); color: #fff; }

.sidebar {
    position: fixed; top: 54px; left: 0; bottom: 0; width: var(--sidebar-w);
    background: #141210; border-right: 1px solid rgba(154, 123, 59, 0.28);
    padding: 18px 14px 32px; overflow-y: auto; z-index: 900;
}
.sidebar-title {
    font-family: 'Cinzel', Georgia, serif; font-size: 11.5px; letter-spacing: 0.14em;
    text-transform: uppercase; color: var(--gold-light);
    border-bottom: 1px solid rgba(154, 123, 59, 0.35); padding-bottom: 8px; margin: 0 0 12px 0;
}
.toc-list { list-style: none; padding: 0; margin: 0; }
.toc-list li { margin: 2px 0; }
.toc-list a {
    display: block; text-decoration: none; color: #cfc6b4; font-size: 14.5px;
    line-height: 1.35; padding: 5px 8px; border-radius: 3px; border-left: 2px solid transparent;
}
.toc-list a:hover { color: var(--gold-light); background: rgba(154, 123, 59, 0.1); border-left-color: var(--gold); }
.toc-h2 a { font-weight: 600; color: #e8decb; margin-top: 6px; }
.toc-h3 a { padding-left: 16px; font-size: 13.5px; color: #b5ab98; }

.book-shell { margin-left: var(--sidebar-w); padding: 80px 26px 64px; display: flex; justify-content: center; }
.book-shell.no-sidebar { margin-left: 0; }
.book-page {
    width: 100%; max-width: 920px; background: var(--vellum); color: var(--ink);
    padding: 52px 60px 70px;
    box-shadow: 0 24px 65px rgba(0,0,0,0.62), 0 0 0 1px rgba(154, 123, 59, 0.35);
    border-radius: 3px; position: relative;
}
.book-page::before {
    content: ""; position: absolute; inset: 12px;
    border: 1px solid rgba(154, 123, 59, 0.32); pointer-events: none;
}

.cover-page {
    min-height: 760px; display: flex; flex-direction: column; justify-content: center; align-items: center;
    text-align: center; padding: 54px 44px; margin-bottom: 52px;
    border: 2px solid var(--crimson); outline: 1px solid var(--gold); outline-offset: -8px;
    background: radial-gradient(circle at center, #fbf7ee 0%, #f3ead6 100%);
    page-break-after: always; break-after: page;
}
.cover-kicker {
    font-family: 'Cinzel', Georgia, serif; font-size: 13px; letter-spacing: 0.26em;
    text-transform: uppercase; color: var(--crimson); margin-bottom: 14px;
}
.cover-rule {
    width: 180px; height: 2px;
    background: linear-gradient(90deg, transparent, var(--gold), var(--crimson), var(--gold), transparent);
    margin: 18px auto;
}
.cover-title {
    font-family: 'Cinzel', Georgia, serif; font-size: 40px; font-weight: 800; line-height: 1.15;
    letter-spacing: 0.08em; color: var(--ink); margin: 0; text-transform: uppercase;
}
.cover-subtitle {
    font-family: 'EB Garamond', Georgia, serif; font-style: italic; font-size: 21px;
    color: var(--ink-soft); margin: 14px 0 8px; max-width: 640px;
}
.cover-epigraph { font-style: italic; font-size: 18px; color: var(--crimson-dark); max-width: 560px; margin: 24px auto 14px; }
.cover-thumb {
    max-width: 100%; max-height: 310px; border: 2px solid var(--gold);
    box-shadow: 0 10px 26px rgba(0,0,0,0.22); margin: 16px auto; border-radius: 2px;
}
.cover-edition {
    margin-top: auto; padding-top: 26px; font-family: 'Cinzel', Georgia, serif;
    font-size: 11px; letter-spacing: 0.22em; text-transform: uppercase; color: var(--ink-soft);
}

/* GM ENCRYPTED VAULT GATE */
.gm-gate-box {
    margin: 28px 0;
    padding: 36px 28px;
    text-align: center;
    background: linear-gradient(180deg, #1d1916 0%, #151210 100%);
    color: #efe6d2;
    border: 2px solid var(--gold);
    outline: 1px solid var(--crimson);
    outline-offset: -7px;
    border-radius: 4px;
    box-shadow: 0 12px 32px rgba(0,0,0,0.35);
}
.gm-vault[data-locked="false"] .gm-gate-box { display: none; }
.gm-seal-icon { font-size: 36px; margin-bottom: 8px; }
.gm-gate-kicker {
    font-family: 'Cinzel', Georgia, serif; font-size: 11.5px; letter-spacing: 0.22em;
    color: var(--gold-light); text-transform: uppercase; margin-bottom: 6px;
}
.gm-gate-title {
    font-family: 'Cinzel', Georgia, serif; font-size: 24px; color: #f7f1e3;
    border: none; margin: 6px 0 10px; padding: 0;
}
.gm-gate-desc {
    text-align: center; color: #cfc6b4; font-style: italic; max-width: 540px; margin: 0 auto 20px; font-size: 17px;
}
.gm-unlock-form {
    display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; max-width: 440px; margin: 0 auto;
}
.gm-pwd-input {
    flex: 1 1 220px; padding: 10px 14px; font-family: 'EB Garamond', Georgia, serif; font-size: 17px;
    background: #100e0c; color: #f7f1e3; border: 1px solid var(--gold); border-radius: 3px;
}
.gm-pwd-input:focus { outline: none; border-color: var(--gold-light); box-shadow: 0 0 0 2px rgba(205,176,110,0.28); }
.gm-unlock-btn {
    padding: 10px 20px; font-family: 'Cinzel', Georgia, serif; font-size: 12px; font-weight: 700;
    letter-spacing: 0.1em; text-transform: uppercase; cursor: pointer;
    background: var(--crimson); color: #f7f1e3; border: 1px solid var(--gold); border-radius: 3px;
}
.gm-unlock-btn:hover { background: #962724; }
.gm-gate-error {
    margin-top: 12px; min-height: 22px; font-size: 15px; color: #f08a84; font-weight: 600;
}

h1, h2, h3, h4 { font-family: 'Cinzel', Georgia, serif; color: var(--crimson); break-after: avoid; page-break-after: avoid; }
h1.book-h1 {
    font-size: 28px; letter-spacing: 0.05em; text-transform: uppercase;
    border-bottom: 2px solid var(--crimson); padding-bottom: 10px; margin: 0 0 22px 0;
}
h2 { font-size: 21px; letter-spacing: 0.04em; margin: 36px 0 14px; padding-bottom: 6px; border-bottom: 1px solid var(--gold); }
h3 { font-size: 16.5px; letter-spacing: 0.03em; margin: 22px 0 8px; color: #3d2415; }
p { margin: 0 0 13px; text-align: justify; hyphens: auto; }
ul, ol { margin: 6px 0 16px; padding-left: 24px; }
li { margin-bottom: 6px; }
strong { color: #17120d; }
code {
    font-family: Consolas, 'Courier New', monospace; font-size: 0.86em;
    background: rgba(154, 123, 59, 0.14); border: 1px solid rgba(154, 123, 59, 0.28);
    padding: 1px 5px; border-radius: 3px; color: #5b1d18;
}
hr { border: none; height: 1px; background: linear-gradient(90deg, transparent, var(--gold), transparent); margin: 28px 0; }
a { color: var(--crimson); text-decoration: underline; text-decoration-color: rgba(122, 31, 29, 0.35); text-underline-offset: 3px; }

blockquote {
    margin: 18px 0 22px; padding: 14px 20px; background: var(--vellum-card);
    border-left: 4px solid var(--gold); font-style: italic; color: var(--ink-soft); break-inside: avoid;
}
.callout {
    margin: 20px 0; padding: 14px 18px; border-radius: 2px; border: 1px solid var(--border);
    border-left: 5px solid var(--crimson); background: #f2e7d3; color: var(--ink); break-inside: avoid;
}
.callout-title {
    font-family: 'Cinzel', Georgia, serif; font-size: 12px; font-weight: 700;
    letter-spacing: 0.12em; text-transform: uppercase; color: var(--crimson); margin-bottom: 6px;
}
.callout.warning { border-left-color: #b4691e; background: #f6ecd7; }
.callout.warning .callout-title { color: #8c4d10; }

.formula-box {
    margin: 16px 0 20px; padding: 12px 18px; background: #efe5cf;
    border: 1px solid var(--gold); border-radius: 3px; text-align: center;
    font-size: 18.5px; font-weight: 600; color: var(--crimson-dark); break-inside: avoid;
}

.table-wrap { width: 100%; overflow-x: auto; margin: 16px 0 24px; }
table { width: 100%; border-collapse: collapse; font-size: 15.5px; line-height: 1.44; border: 1px solid var(--gold); }
thead th {
    font-family: 'Cinzel', Georgia, serif; font-size: 11.5px; letter-spacing: 0.05em;
    text-transform: uppercase; background: var(--crimson); color: #f7f1e3;
    padding: 9px 9px; border: 1px solid #5f1816; text-align: left;
}
tbody td { padding: 8px 9px; border: 1px solid var(--border); vertical-align: top; }
tbody tr:nth-child(even) { background: var(--vellum-alt); }
tr { break-inside: avoid; }

.atlas-plate {
    margin: 22px 0 28px; padding: 10px; background: #ebe1ca;
    border: 1px solid var(--gold); box-shadow: 0 6px 18px rgba(0,0,0,0.14);
    text-align: center; break-inside: avoid;
}
.atlas-plate img { width: 100%; height: auto; display: block; border: 1px solid #3c3124; cursor: zoom-in; }
.atlas-caption {
    font-family: 'Cinzel', Georgia, serif; font-size: 12px; letter-spacing: 0.08em;
    text-transform: uppercase; color: var(--ink-soft); margin-top: 8px;
}

.entry-card {
    margin: 16px 0 20px; padding: 14px 18px 12px; background: var(--vellum-card);
    border: 1px solid var(--border); border-top: 3px solid var(--crimson); border-radius: 2px; break-inside: avoid;
}
.entry-card h3 { margin-top: 0; color: var(--crimson); border-bottom: 1px solid rgba(154, 123, 59, 0.45); padding-bottom: 5px; }

.lightbox {
    display: none; position: fixed; inset: 0; background: rgba(10, 9, 8, 0.92);
    z-index: 2000; padding: 24px; align-items: center; justify-content: center; cursor: zoom-out;
}
.lightbox.open { display: flex; }
.lightbox img { max-width: 96vw; max-height: 92vh; border: 2px solid var(--gold); box-shadow: 0 20px 60px rgba(0,0,0,0.8); }

.portal-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 18px; margin: 22px 0 32px; }
.portal-card {
    display: flex; flex-direction: column; background: var(--vellum-card);
    border: 1px solid var(--border); border-top: 4px solid var(--crimson);
    padding: 18px 18px 16px; text-decoration: none; color: var(--ink);
    transition: transform 0.16s ease, box-shadow 0.16s ease;
}
.portal-card.gm-card { background: #211c18; color: #efe6d2; border-color: var(--gold); border-top-color: var(--gold); }
.portal-card.gm-card .portal-title { color: #f7f1e3; }
.portal-card.gm-card .portal-desc { color: #c7beac; }
.portal-card.gm-card .portal-kicker, .portal-card.gm-card .portal-cta { color: var(--gold-light); }
.portal-card:hover { transform: translateY(-3px); box-shadow: 0 10px 24px rgba(0,0,0,0.16); border-color: var(--gold); }
.portal-kicker { font-family: 'Cinzel', Georgia, serif; font-size: 11px; letter-spacing: 0.16em; color: var(--crimson); font-weight: 700; }
.portal-title { font-family: 'Cinzel', Georgia, serif; font-size: 18px; font-weight: 700; margin: 6px 0 8px; color: var(--ink); }
.portal-desc { font-size: 15px; color: var(--ink-soft); line-height: 1.48; margin: 0; text-align: left; }
.portal-cta { margin-top: auto; padding-top: 12px; font-family: 'Cinzel', Georgia, serif; font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase; color: var(--crimson); font-weight: 700; }
.tome-divider { page-break-before: always; break-before: page; }

@media (max-width: 1020px) {
    .sidebar { display: none; }
    .book-shell { margin-left: 0; padding: 72px 14px 40px; }
    .book-page { padding: 30px 24px 42px; }
}

@page { size: A4; margin: 16mm 15mm 18mm 15mm; }
@media print {
    html, body { background: #ffffff !important; font-size: 10.8pt; line-height: 1.5; }
    .topbar, .sidebar, .lightbox, .gm-gate-box { display: none !important; }
    .book-shell { margin: 0 !important; padding: 0 !important; display: block !important; }
    .book-page { max-width: none !important; box-shadow: none !important; background: #ffffff !important; padding: 0 !important; border: none !important; }
    .book-page::before { display: none !important; }
    .cover-page { min-height: 245mm; margin: 0; background: #fbf8f1 !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    thead th, .callout, .formula-box, .entry-card, .atlas-plate, tbody tr:nth-child(even) { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    a { color: var(--crimson-dark); text-decoration: none; }
    .atlas-plate img { max-height: 160mm; object-fit: contain; }
}
"""

SHARED_JS = r"""
(function() {
    const SESSION_KEY = 'alenia_gm_unlock_key';

    function b64ToBytes(b64) {
        const bin = atob(b64);
        const bytes = new Uint8Array(bin.length);
        for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
        return bytes;
    }

    async function decryptBlock(cipherObj, password) {
        const enc = new TextEncoder();
        const keyMat = await crypto.subtle.importKey(
            'raw', enc.encode(password), { name: 'PBKDF2' }, false, ['deriveKey']
        );
        const aesKey = await crypto.subtle.deriveKey(
            { name: 'PBKDF2', salt: b64ToBytes(cipherObj.s), iterations: cipherObj.it, hash: 'SHA-256' },
            keyMat,
            { name: 'AES-GCM', length: 256 },
            false,
            ['decrypt']
        );
        const plainBuf = await crypto.subtle.decrypt(
            { name: 'AES-GCM', iv: b64ToBytes(cipherObj.i) },
            aesKey,
            b64ToBytes(cipherObj.c)
        );
        return JSON.parse(new TextDecoder().decode(plainBuf));
    }

    function wireLightbox(root) {
        const lb = document.getElementById('atlas-lightbox');
        const lbImg = document.getElementById('atlas-lightbox-img');
        if (!lb || !lbImg) return;
        (root || document).querySelectorAll('.atlas-plate img').forEach(img => {
            if (img.dataset.lbBound) return;
            img.dataset.lbBound = '1';
            img.addEventListener('click', () => { lbImg.src = img.src; lb.classList.add('open'); });
        });
    }

    async function unlockAllVaults(password, silent) {
        const vaults = document.querySelectorAll('.gm-vault[data-locked="true"]');
        let anyUnlocked = false;
        let failed = false;

        for (const v of vaults) {
            const scriptEl = v.querySelector('script.gm-cipher');
            const errEl = v.querySelector('.gm-gate-error');
            const outEl = v.querySelector('.gm-unlocked-content');
            if (!scriptEl || !outEl) continue;
            try {
                const cipherObj = JSON.parse(scriptEl.textContent);
                const data = await decryptBlock(cipherObj, password);
                outEl.innerHTML = data.html || '';
                v.setAttribute('data-locked', 'false');
                if (errEl) errEl.textContent = '';
                wireLightbox(outEl);
                if (data.toc) {
                    const tocList = document.querySelector('.toc-list');
                    if (tocList) {
                        const tmp = document.createElement('div');
                        tmp.innerHTML = data.toc;
                        while (tmp.firstChild) tocList.appendChild(tmp.firstChild);
                    }
                }
                anyUnlocked = true;
            } catch (e) {
                failed = true;
                if (!silent && errEl) errEl.textContent = 'Senha incorreta — o selo do Mestre permanece fechado.';
            }
        }

        if (anyUnlocked) {
            sessionStorage.setItem(SESSION_KEY, password);
            const lockBtn = document.getElementById('btn-lock-gm');
            if (lockBtn) lockBtn.classList.add('visible');
        } else if (failed && silent) {
            sessionStorage.removeItem(SESSION_KEY);
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        const lb = document.getElementById('atlas-lightbox');
        if (lb) {
            lb.addEventListener('click', () => lb.classList.remove('open'));
            document.addEventListener('keydown', (e) => { if (e.key === 'Escape') lb.classList.remove('open'); });
        }
        wireLightbox(document);

        const lockBtn = document.getElementById('btn-lock-gm');
        if (lockBtn) {
            if (sessionStorage.getItem(SESSION_KEY)) lockBtn.classList.add('visible');
            lockBtn.addEventListener('click', () => {
                sessionStorage.removeItem(SESSION_KEY);
                location.reload();
            });
        }

        document.querySelectorAll('.gm-unlock-form').forEach(form => {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const input = form.querySelector('.gm-pwd-input');
                const pwd = input ? input.value : '';
                if (!pwd) return;
                if (!window.crypto || !window.crypto.subtle) {
                    const errEl = form.parentElement.querySelector('.gm-gate-error');
                    if (errEl) errEl.textContent = 'Abra por HTTPS (Render) ou localhost para habilitar descriptografia do navegador.';
                    return;
                }
                await unlockAllVaults(pwd, false);
            });
        });

        const saved = sessionStorage.getItem(SESSION_KEY);
        if (saved && window.crypto && window.crypto.subtle) {
            unlockAllVaults(saved, true);
        }
    });
})();
"""


def sync_assets():
    copies = [
        (os.path.join(ROOT_DIR, "mapas", "alenia_mapa_mundi_atualizado.jpg"), "alenia_mapa_mundi_atualizado.jpg"),
        (os.path.join(ROOT_DIR, "mapas", "regionais", "mapa_regional_aurora.jpg"), "mapa_regional_aurora.jpg"),
        (os.path.join(ROOT_DIR, "mapas", "regionais", "mapa_regional_corallis.jpg"), "mapa_regional_corallis.jpg"),
        (os.path.join(ROOT_DIR, "mapas", "regionais", "mapa_regional_gaddra.jpg"), "mapa_regional_gaddra.jpg"),
        (os.path.join(ROOT_DIR, "mapas", "regionais", "mapa_regional_kalis.jpg"), "mapa_regional_kalis.jpg"),
        (os.path.join(ROOT_DIR, "mapas", "regionais", "mapa_regional_incognito.jpg"), "mapa_regional_incognito.jpg"),
    ]
    for src, dst_name in copies:
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(ASSETS_DIR, dst_name))


def slugify(text: str) -> str:
    s = re.sub(r"[^\w\s-]", "", text.lower())
    s = re.sub(r"[\s_-]+", "-", s).strip("-")
    return s or "sec"


def clean_formula(expr: str) -> str:
    s = expr.strip()
    s = re.sub(r"\\text\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\frac\{([^}]*)\}\{([^}]*)\}", r"(\1) / (\2)", s)
    s = s.replace(r"\left\lfloor", "⌊").replace(r"\right\rfloor", "⌋")
    s = s.replace(r"\lfloor", "⌊").replace(r"\rfloor", "⌋")
    s = s.replace(r"\Big(", "(").replace(r"\Big)", ")")
    s = s.replace(r"\times", "×").replace(r"\Delta", "Δ").replace(r"\;", " ")
    s = s.replace(r"\max", "máx").replace(r"\min", "mín")
    return html.escape(s)


def rewrite_link(url: str) -> str:
    if "alenia_mapa_mundi_atualizado" in url:
        return "assets/alenia_mapa_mundi_atualizado.jpg"
    m_reg = re.search(r"(mapa_regional_[a-z]+)\.(?:png|jpg)", url)
    if m_reg:
        return "assets/" + m_reg.group(1) + ".jpg"
    mapping = {
        "01_Livro_de_Regras.md": "01_Livro_de_Regras.html",
        "02_Guia_de_Cenario_Alenia.md": "02_Livro_do_Cenario.html",
        "03_Catalogo_de_Kits.md": "03_Catalogo_de_Kits.html",
        "04_Bestiario_Alenia.md": "04_Bestiario_de_Alenia.html",
        "05_Onomastica_e_Toponimia_Alenia.md": "05_Onomastica_e_Toponimia.html",
        "06_Guia_do_Jogador_e_Referencia_Rapida.md": "06_Guia_do_Jogador.html",
        "07_Aventura_Inicial_Cinzas_no_Estuario.md": "07_Aventura_Inicial.html",
    }
    for k, v in mapping.items():
        if k in url:
            return v
    return url


def inline_md(text: str) -> str:
    code_tokens = []
    def repl_code(m):
        code_tokens.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"@@CODE{len(code_tokens)-1}@@"

    s = re.sub(r"`([^`]+)`", repl_code, text)

    link_tokens = []
    def repl_link(m):
        lbl = inline_md(m.group(1))
        href = html.escape(rewrite_link(m.group(2)), quote=True)
        link_tokens.append(f'<a href="{href}">{lbl}</a>')
        return f"@@LINK{len(link_tokens)-1}@@"

    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", repl_link, s)
    s = html.escape(s)

    s = re.sub(r"\*\*\*([^\n*]+?)\*\*\*", r"<strong><em>\1</em></strong>", s)
    s = re.sub(r"\*\*([^\n]+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*([^\n*]+?)\*", r"<em>\1</em>", s)
    s = re.sub(r"\*\*([^\n]+?)\*\*", r"<strong>\1</strong>", s)

    for idx, tok in enumerate(link_tokens):
        s = s.replace(f"@@LINK{idx}@@", tok)
    for idx, tok in enumerate(code_tokens):
        s = s.replace(f"@@CODE{idx}@@", tok)
    return s


def render_toc_items(toc_items) -> str:
    items_li = []
    for lvl, lbl, hid in toc_items:
        cls = "toc-h2" if lvl == 2 else "toc-h3"
        items_li.append(f'<li class="{cls}"><a href="#{hid}">{html.escape(lbl)}</a></li>')
    return "".join(items_li)


def split_md_with_gm_sections(md_text: str):
    """Splits a public Markdown doc into chunks: (is_gm_secret, label, text)."""
    lines = md_text.splitlines()
    chunks = []
    cur_lines = []
    cur_gm = False
    cur_gm_level = 0
    cur_label = ""

    def flush():
        if cur_lines:
            chunks.append((cur_gm, cur_label, "\n".join(cur_lines)))

    for line in lines:
        s = line.strip()
        m_h = re.match(r"^(#{1,4})\s+(.*)$", s)
        if m_h:
            lvl = len(m_h.group(1))
            plain = re.sub(r"\*+|`", "", m_h.group(2).strip())
            starts_gm = (
                (lvl == 2 and any(plain.startswith(p) for p in GM_SECTION_H2_PREFIXES)) or
                (lvl == 3 and any(plain.startswith(p) for p in GM_SECTION_H3_PREFIXES))
            )
            if starts_gm:
                flush()
                cur_lines = [line]
                cur_gm = True
                cur_gm_level = lvl
                cur_label = "Segredos do Mestre — " + ("A Grande Ameaça" if lvl == 2 else "Regras Ocultas de Campanha")
                continue
            elif cur_gm and lvl <= cur_gm_level:
                flush()
                cur_lines = [line]
                cur_gm = False
                cur_gm_level = 0
                cur_label = ""
                continue
        cur_lines.append(line)
    flush()
    return chunks


def md_to_html(md_text: str, id_prefix: str = "", card_h3: bool = False, inject_maps: bool = False, toc_start_idx: int = 0):
    lines = md_text.splitlines()
    out = []
    toc = []
    i = 0
    n = len(lines)
    in_card = False

    def close_card():
        nonlocal in_card
        if in_card:
            out.append("</div>")
            in_card = False

    while i < n:
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue

        if re.match(r"^---+$", stripped):
            close_card()
            out.append("<hr/>")
            i += 1
            continue

        if stripped.startswith("$$"):
            expr = stripped[2:]
            if expr.endswith("$$") and len(expr) >= 2:
                expr = expr[:-2]
                i += 1
            else:
                buf = [expr]
                i += 1
                while i < n and not lines[i].strip().endswith("$$"):
                    buf.append(lines[i])
                    i += 1
                if i < n:
                    buf.append(lines[i].strip()[:-2])
                    i += 1
                expr = " ".join(buf)
            out.append(f'<div class="formula-box">{clean_formula(expr)}</div>')
            continue

        m_h = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m_h:
            level = len(m_h.group(1))
            raw_title = m_h.group(2).strip()
            plain_title = re.sub(r"\*+|`", "", raw_title)
            hid = f"{id_prefix}{slugify(plain_title)}-{toc_start_idx + len(toc)}"

            if level <= 2:
                close_card()
            elif level == 3 and card_h3:
                close_card()
                out.append('<div class="entry-card">')
                in_card = True

            if level == 1:
                out.append(f'<h1 id="{hid}" class="book-h1">{inline_md(raw_title)}</h1>')
            else:
                out.append(f'<h{level} id="{hid}">{inline_md(raw_title)}</h{level}>')

            if level in (2, 3):
                toc.append((level, plain_title, hid))

            if inject_maps and level == 2:
                for key, (img_rel, cap) in CHAPTER_MAPS.items():
                    if plain_title.startswith(key):
                        out.append(
                            f'<figure class="atlas-plate">'
                            f'<img src="{img_rel}" alt="{html.escape(cap)}" loading="lazy"/>'
                            f'<figcaption class="atlas-caption">{html.escape(cap)}</figcaption>'
                            f'</figure>'
                        )
                        break
            i += 1
            continue

        if stripped.startswith(">"):
            q_lines = []
            while i < n and lines[i].strip().startswith(">"):
                q_lines.append(re.sub(r"^>\s?", "", lines[i].strip()))
                i += 1
            first = q_lines[0] if q_lines else ""
            m_call = re.match(r"^\[!(IMPORTANT|CAUTION|WARNING|NOTE|TIP)\]\s*$", first)
            if m_call:
                ctype = m_call.group(1)
                labels = {
                    "IMPORTANT": "Regra Fundamental",
                    "CAUTION": "Atenção",
                    "WARNING": "Aviso ao Mestre",
                    "NOTE": "Nota",
                    "TIP": "Dica",
                }
                cls = "callout warning" if ctype in ("WARNING", "CAUTION") else "callout"
                body = "<br/>".join(inline_md(ql) for ql in q_lines[1:] if ql.strip())
                out.append(f'<div class="{cls}"><div class="callout-title">{labels[ctype]}</div><div>{body}</div></div>')
            else:
                body = "<br/>".join(inline_md(ql) for ql in q_lines if ql.strip())
                out.append(f"<blockquote>{body}</blockquote>")
            continue

        if "|" in stripped and i + 1 < n and re.match(r"^\s*\|?[\s:\-|\+]+\|?\s*$", lines[i + 1]):
            def split_row(r):
                r = r.strip()
                if r.startswith("|"):
                    r = r[1:]
                if r.endswith("|"):
                    r = r[:-1]
                return [c.strip() for c in r.split("|")]

            headers = split_row(lines[i])
            aligns_raw = split_row(lines[i + 1])
            aligns = []
            for a in aligns_raw:
                if a.startswith(":") and a.endswith(":"):
                    aligns.append("center")
                elif a.endswith(":"):
                    aligns.append("right")
                else:
                    aligns.append("left")

            i += 2
            rows = []
            while i < n and "|" in lines[i] and lines[i].strip():
                rows.append(split_row(lines[i]))
                i += 1

            t_html = ['<div class="table-wrap"><table><thead><tr>']
            for idx_c, hcell in enumerate(headers):
                al = aligns[idx_c] if idx_c < len(aligns) else "left"
                t_html.append(f'<th style="text-align:{al}">{inline_md(hcell)}</th>')
            t_html.append("</tr></thead><tbody>")
            for r in rows:
                t_html.append("<tr>")
                for idx_c, cell in enumerate(r):
                    al = aligns[idx_c] if idx_c < len(aligns) else "left"
                    t_html.append(f'<td style="text-align:{al}">{inline_md(cell)}</td>')
                t_html.append("</tr>")
            t_html.append("</tbody></table></div>")
            out.append("".join(t_html))
            continue

        if re.match(r"^(\s*)([-*]|\d+\.)\s+", line):
            is_ordered = bool(re.match(r"^\s*\d+\.\s+", line))
            tag = "ol" if is_ordered else "ul"
            out.append(f"<{tag}>")
            while i < n and re.match(r"^(\s*)([-*]|\d+\.)\s+", lines[i]):
                m_li = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", lines[i])
                indent = len(m_li.group(1))
                content = m_li.group(3)
                i += 1
                sub_items = []
                while i < n and re.match(r"^(\s+)([-*]|\d+\.)\s+", lines[i]):
                    m_sub = re.match(r"^(\s+)([-*]|\d+\.)\s+(.*)$", lines[i])
                    if len(m_sub.group(1)) > indent:
                        sub_items.append(m_sub.group(3))
                        i += 1
                    else:
                        break
                if sub_items:
                    sub_html = "<ul>" + "".join(f"<li>{inline_md(si)}</li>" for si in sub_items) + "</ul>"
                    out.append(f"<li>{inline_md(content)}{sub_html}</li>")
                else:
                    out.append(f"<li>{inline_md(content)}</li>")
            out.append(f"</{tag}>")
            continue

        p_lines = [stripped]
        i += 1
        while i < n:
            nxt = lines[i].strip()
            if (not nxt or nxt.startswith("#") or nxt.startswith(">") or nxt.startswith("$$")
                    or re.match(r"^---+$", nxt) or re.match(r"^([-*]|\d+\.)\s+", nxt)
                    or ("|" in nxt and i + 1 < n and re.match(r"^\s*\|?[\s:\-|]+\|?\s*$", lines[i + 1]))):
                break
            p_lines.append(nxt)
            i += 1
        out.append(f"<p>{inline_md(' '.join(p_lines))}</p>")

    close_card()
    return "\n".join(out), toc


def render_public_doc_with_sealed_sections(md_content: str, id_prefix: str, card_h3: bool, inject_maps: bool):
    chunks = split_md_with_gm_sections(md_content)
    html_parts = []
    public_toc = []
    idx_counter = 0
    for is_gm, gm_label, text in chunks:
        rendered, chunk_toc = md_to_html(text, id_prefix=id_prefix, card_h3=card_h3, inject_maps=inject_maps, toc_start_idx=idx_counter)
        idx_counter += len(chunk_toc) + 2
        if is_gm and GM_PASSWORD:
            toc_html = render_toc_items(chunk_toc)
            html_parts.append(
                make_gm_gate_block(
                    gm_label,
                    "Esta seção contém segredos de campanha reservados ao Mestre. Insira a senha para revelar.",
                    rendered,
                    toc_html,
                )
            )
        else:
            html_parts.append(rendered)
            public_toc.extend(chunk_toc)
    return "\n".join(html_parts), public_toc


def build_topbar(active_file: str) -> str:
    links = [("index.html", "Biblioteca")] + [(b["out"], b["short"]) for b in BOOKS] + [("Alenia_Compendio_Completo.html", "Compêndio")]
    nav_html = []
    for href, lbl in links:
        cls = ' class="active"' if href == active_file else ""
        nav_html.append(f'<a href="{href}"{cls}>{lbl}</a>')
    nav_html.append('<button id="btn-lock-gm" class="btn-lock" type="button" title="Trancar área do Mestre">🔒 Trancar</button>')
    nav_html.append('<button class="btn-print" type="button" onclick="window.print()">Imprimir / PDF</button>')
    return (
        '<header class="topbar">'
        '<a class="topbar-brand" href="index.html">✦ ALENIA RPG</a>'
        f'<nav class="topbar-nav">{"".join(nav_html)}</nav>'
        '</header>'
    )


def build_cover(num: str, title: str, subtitle: str, epigraph: str, cover_map: str = None) -> str:
    img_html = f'<img class="cover-thumb" src="{cover_map}" alt="Mapa de Alenia"/>' if cover_map else ""
    return f"""
    <section class="cover-page">
        <div class="cover-kicker">ALENIA RPG • {html.escape(num)}</div>
        <div class="cover-rule"></div>
        <h1 class="cover-title">{html.escape(title)}</h1>
        <div class="cover-subtitle">{html.escape(subtitle)}</div>
        <div class="cover-rule"></div>
        {img_html}
        <p class="cover-epigraph">{html.escape(epigraph)}</p>
        <div class="cover-edition">{EDITION_LABEL}</div>
    </section>
    """


def wrap_html_doc(page_title: str, active_file: str, body_html: str, toc_items=None, force_sidebar: bool = False) -> str:
    has_toc = force_sidebar or (toc_items is not None and len(toc_items) > 0)
    sidebar_html = ""
    shell_cls = "book-shell" if has_toc else "book-shell no-sidebar"
    if has_toc:
        li_html = render_toc_items(toc_items or [])
        sidebar_html = (
            '<aside class="sidebar">'
            '<div class="sidebar-title">Sumário do Volume</div>'
            f'<ul class="toc-list">{li_html}</ul>'
            '</aside>'
        )

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>{html.escape(page_title)} — Alenia RPG</title>
    <style>{SHARED_CSS}</style>
</head>
<body>
    {build_topbar(active_file)}
    {sidebar_html}
    <main class="{shell_cls}">
        <article class="book-page">
            {body_html}
        </article>
    </main>
    <div id="atlas-lightbox" class="lightbox" title="Clique ou pressione ESC para fechar">
        <img id="atlas-lightbox-img" src="" alt="Ampliação do Mapa"/>
    </div>
    <script>{SHARED_JS}</script>
</body>
</html>
"""


def main():
    sync_assets()
    if not GM_PASSWORD:
        print("[WARN] ALENIA_GM_PASSWORD nao definida — gerando sem criptografia!")
    else:
        print("[OK] Criptografia AES-256-GCM (PBKDF2 120k) ativa para toda a Area do Mestre.")

    compendium_parts = [
        build_cover(
            "COMPÊNDIO INTEGRAL",
            "ALENIA RPG",
            "Regras, Cenário & Atlas, 36 Kits, Onomástica, Guia do Jogador & Volumes Selados do Mestre",
            "“Cinco terras, um único aço. O volume definitivo para mestres e exploradores de Alenia.”",
            "assets/alenia_mapa_mundi_atualizado.jpg",
        )
    ]
    compendium_toc = []

    for idx, bk in enumerate(BOOKS):
        src_path = os.path.join(ROOT_DIR, bk["src"])
        with open(src_path, "r", encoding="utf-8") as f:
            md_content = f.read()

        card_h3 = bk["out"] in ("03_Catalogo_de_Kits.html", "04_Bestiario_de_Alenia.html")
        inject_maps = bk["out"] == "02_Livro_do_Cenario.html"
        cover_html = build_cover(bk["num"], bk["title"], bk["subtitle"], bk["epigraph"], bk["cover_map"])

        if bk["gm_only"] and GM_PASSWORD:
            secret_html, secret_toc = md_to_html(md_content, id_prefix="", card_h3=card_h3, inject_maps=inject_maps)
            # For Adventure, also include Aurora map inside the encrypted payload so cover stays spoiler-free!
            if bk["out"] == "07_Aventura_Inicial.html":
                secret_html = (
                    '<figure class="atlas-plate"><img src="assets/mapa_regional_aurora.jpg" alt="Mapa Regional de Aurora"/>'
                    '<figcaption class="atlas-caption">Mapa da Região da Aventura — Oeste de Aurora</figcaption></figure>'
                    + secret_html
                )
            gated = make_gm_gate_block(
                bk["title"],
                "Conteúdo restrito ao Mestre (fichas, segredos e bastidores). Digite a senha para descriptografar.",
                secret_html,
                render_toc_items(secret_toc),
            )
            full_doc = wrap_html_doc(bk["title"], bk["out"], cover_html + "\n" + gated, toc_items=[], force_sidebar=True)
            out_path = os.path.join(OUT_DIR, bk["out"])
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(full_doc)
            print(f"[OK] {bk['out']:34s} (CRIPTOGRAFADO AES-256-GCM)")

            # Compendium version (also encrypted!)
            c_secret_html, c_secret_toc = md_to_html(md_content, id_prefix=f"t{idx+1}-", card_h3=card_h3, inject_maps=inject_maps)
            tome_anchor = f"tomo-{idx+1}"
            compendium_toc.append((2, f"🔒 {bk['num']} — {bk['title']}", tome_anchor))
            c_toc_only_h2 = [(3, lbl, hid) for lvl, lbl, hid in c_secret_toc if lvl == 2]
            c_gated = make_gm_gate_block(
                f"{bk['num']} — {bk['title']}",
                "Volume restrito ao Mestre dentro do Compêndio. Insira a senha para revelar.",
                c_secret_html,
                render_toc_items(c_toc_only_h2),
            )
            compendium_parts.append(
                f'<section id="{tome_anchor}" class="tome-divider">'
                f'{build_cover(bk["num"], bk["title"], bk["subtitle"], bk["epigraph"], None)}'
                f'{c_gated}'
                f'</section>'
            )
        else:
            body_inner, pub_toc = render_public_doc_with_sealed_sections(md_content, id_prefix="", card_h3=card_h3, inject_maps=inject_maps)
            full_doc = wrap_html_doc(bk["title"], bk["out"], cover_html + "\n" + body_inner, pub_toc)
            out_path = os.path.join(OUT_DIR, bk["out"])
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(full_doc)
            print(f"[OK] {bk['out']:34s} ({len(pub_toc)} secoes publicas)")

            c_inner, c_pub_toc = render_public_doc_with_sealed_sections(md_content, id_prefix=f"t{idx+1}-", card_h3=card_h3, inject_maps=inject_maps)
            tome_anchor = f"tomo-{idx+1}"
            compendium_toc.append((2, f"{bk['num']} — {bk['title']}", tome_anchor))
            for lvl, lbl, hid in c_pub_toc:
                if lvl == 2:
                    compendium_toc.append((3, lbl, hid))
            compendium_parts.append(
                f'<section id="{tome_anchor}" class="tome-divider">'
                f'{build_cover(bk["num"], bk["title"], bk["subtitle"], bk["epigraph"], None)}'
                f'{c_inner}'
                f'</section>'
            )

    comp_html = wrap_html_doc("Compêndio Completo", "Alenia_Compendio_Completo.html", "\n".join(compendium_parts), compendium_toc)
    with open(os.path.join(OUT_DIR, "Alenia_Compendio_Completo.html"), "w", encoding="utf-8") as f:
        f.write(comp_html)
    print(f"[OK] Alenia_Compendio_Completo.html    ({len(compendium_toc)} entradas publicas no sumario)")

    cards = []
    for bk in BOOKS:
        cls = "portal-card gm-card" if bk["gm_only"] else "portal-card"
        cta = "🔒 Destrancar (Mestre) →" if bk["gm_only"] else "Abrir Tomo →"
        cards.append(f"""
        <a class="{cls}" href="{bk['out']}">
            <div class="portal-kicker">{html.escape(bk['num'])}</div>
            <div class="portal-title">{html.escape(bk['title'])}</div>
            <p class="portal-desc">{html.escape(bk['desc'])}</p>
            <div class="portal-cta">{cta}</div>
        </a>
        """)
    cards.append("""
        <a class="portal-card" href="Alenia_Compendio_Completo.html" style="border-top-color:#9a7b3b; background:#efe5cf;">
            <div class="portal-kicker">EDIÇÃO INTEGRAL (PDF MESTRE)</div>
            <div class="portal-title">Compêndio Completo</div>
            <p class="portal-desc">Todos os tomos reunidos em um único volume contínuo com os mapas embutidos — com as áreas do Mestre seladas por senha.</p>
            <div class="portal-cta">Abrir Volume Único →</div>
        </a>
    """)

    index_body = f"""
    <section class="cover-page" style="min-height:auto; page-break-after:auto; break-after:auto; margin-bottom:32px; padding:34px 30px;">
        <div class="cover-kicker">BIBLIOTECA OFICIAL • {EDITION_LABEL}</div>
        <div class="cover-rule"></div>
        <h1 class="cover-title" style="font-size:38px;">ALENIA RPG</h1>
        <div class="cover-subtitle">7 Tomos • Atlas Ilustrado • 36 Kits • Ficha Firecast v1.2 • Área Selada do Mestre</div>
        <div class="cover-rule"></div>
        <figure class="atlas-plate" style="margin:14px 0 0; width:100%;">
            <img src="assets/alenia_mapa_mundi_atualizado.jpg" alt="Mapa-Múndi de Alenia"/>
            <figcaption class="atlas-caption">Clique em qualquer mapa para ampliar em tela cheia</figcaption>
        </figure>
    </section>

    <h2>Coleção Oficial (Jogadores &amp; 🔒 Área do Mestre)</h2>
    <div class="portal-grid">{"".join(cards)}</div>

    <h2>Galeria de Mapas Regionais</h2>
    <div class="portal-grid">
        <figure class="atlas-plate" style="margin:0;"><img src="assets/mapa_regional_aurora.jpg" alt="Aurora"/><figcaption class="atlas-caption">Reino de Aurora</figcaption></figure>
        <figure class="atlas-plate" style="margin:0;"><img src="assets/mapa_regional_corallis.jpg" alt="Corallis"/><figcaption class="atlas-caption">Corallis &amp; Mar dos Corais</figcaption></figure>
        <figure class="atlas-plate" style="margin:0;"><img src="assets/mapa_regional_gaddra.jpg" alt="Gaddra"/><figcaption class="atlas-caption">Confederação de Gaddra</figcaption></figure>
        <figure class="atlas-plate" style="margin:0;"><img src="assets/mapa_regional_kalis.jpg" alt="Kalis"/><figcaption class="atlas-caption">Despotado de Kalis</figcaption></figure>
        <figure class="atlas-plate" style="margin:0;"><img src="assets/mapa_regional_incognito.jpg" alt="Incognito"/><figcaption class="atlas-caption">Incognito &amp; Mar das Cinzas</figcaption></figure>
    </div>
    """

    idx_html = wrap_html_doc("Biblioteca Oficial", "index.html", index_body, toc_items=None)
    with open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(idx_html)
    print("[OK] index.html atualizado com Selo do Mestre.")


if __name__ == "__main__":
    main()
