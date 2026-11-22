#!/usr/bin/env python3
"""
Gerador Editorial HTML em Formato de Livro Real (Páginas Duplas + Criptografia AES-256-GCM) — Alenia RPG (v2.0)
- Modo Livro (2 páginas com lombada central em desktop, 1 página em telas menores, alternável para 1 Página ou Contínuo)
- Paginação inteligente sem títulos órfãos, navegação por teclado (<- / ->), saltos pelo sumário lateral
- Área do Mestre criptografada em AES-256-GCM (PBKDF2 120k) com re-paginação automática ao destrancar
- Pasta livros_html/ 100% autocontida com mapas em assets/ e CSS @media print A4
"""
import base64
import html
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from token_studio import TOKEN_STUDIO_CSS, TOKEN_STUDIO_HTML, TOKEN_STUDIO_JS
from culinaria_renderer import CULINARIA_CSS, CULINARIA_JS, render_culinaria_page
from grandes_nomes_renderer import GRANDES_NOMES_CSS, GRANDES_NOMES_JS, render_grandes_nomes_secret_payload
from codex_linker import CODEX_CSS, build_codex_registry, link_codex_html

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
        "subtitle": "Sistema d20 Sombrio • 44 Talentos em Árvores, Combate Tático & Rituais",
        "epigraph": "“O aço quebra, os reis sangram e o mar engole até os mais sábios.”",
        "desc": "Regras revisadas v2.0: 4d6, Atributos Especiais por Feitos, DV por Kit (1d6–1d12), graduação livre de perícias (+0, +1, +2...) com grau automático, Defesa situacional, Múltiplas Ações blindadas, 44 Talentos (Marciais, Exploração, Sociais e Mentais com pré-requisitos), preços e rituais.",
        "cover_map": "assets/capa_01_regras.jpg",
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
        "cover_map": "assets/capa_03_kits.jpg",
        "gm_only": False,
    },
    {
        "src": "04_Bestiario_Alenia.md",
        "out": "04_Bestiario_de_Alenia.html",
        "num": "TOMO IV • MESTRE",
        "short": "🔒 Bestiário",
        "title": "Bestiário & Ameaças",
        "subtitle": "Acesso Restrito ao Mestre • 31 Ameaças Auditadas & 31 Pinturas Exclusivas",
        "epigraph": "“A maioria das feras que matam viajantes usa botas de couro e fala sua própria língua.”",
        "desc": "🔒 Área Restrita ao Mestre: 31 fichas completas (humanos, megafauna, terrores marítimos, folclore sombrio, alquimia e agentes ocultos), todas ilustradas com pintura exclusiva e protegidas por criptografia AES-256.",
        "cover_map": "assets/capa_04_bestiario.jpg",
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
        "cover_map": "assets/capa_05_onomastica.jpg",
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
        "cover_map": "assets/capa_06_guia_jogador.jpg",
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
        "cover_map": "assets/capa_07_aventura.jpg",
        "gm_only": True,
    },
    {
        "src": "08_Acervo_Oculto_de_Sellene.md",
        "out": "08_Acervo_Oculto_de_Sellene.html",
        "num": "TOMO VIII • MESTRE",
        "short": "🔒 Acervo Sellene",
        "title": "O Acervo Oculto de Sellene",
        "subtitle": "Domínio Absoluto do Alto Rei • Segredos Proibidos & Névoa Ácida",
        "epigraph": "“Há verdades que não iluminam um reino — apenas o incendeiam.”",
        "desc": "🔒 Área Restrita ao Mestre: câmara subterrânea sob a Academia de Sellene protegida por névoa ácida — 9 dossiês proibidos sobre A Sombra, Ferraur, Incognito, Thanatos, rumores proibidos e os segredos da Coroa (AES-256).",
        "cover_map": "assets/capa_08_acervo_sellene.jpg",
        "gm_only": True,
    },
    {
        "src": "09_Catalogo_de_Equipamentos_e_Oficios.md",
        "out": "09_Catalogo_de_Equipamentos.html",
        "num": "TOMO IX",
        "short": "Equipamentos",
        "title": "Empório & Ofícios",
        "subtitle": "Acampamento, Sobrevivência, Pesca, Forja, Alquimia, Náutica & Carga",
        "epigraph": "“Uma espada boa vence um duelo; mas são corda firme, pederneira seca e sal na mochila que mantêm um explorador vivo até o inverno.”",
        "desc": "Catálogo completo com mais de 120 itens de aventura e ofícios com peso (kg), preço no Padrão Prata e especificações mecânicas: acampamento, sobrevivência, pesca, caça, forja, engenharia sem pólvora, medicina, náutica, subterfúgio, vestuário, montarias e 5 pacotes prontos.",
        "cover_map": "assets/capa_09_equipamentos.jpg",
        "gm_only": False,
    },
    {
        "src": "10_Herbario_de_Seleni.md",
        "out": "10_Herbario_de_Seleni.html",
        "num": "TOMO X",
        "short": "Herbário",
        "title": "Herbário de Seleni",
        "subtitle": "Das Raízes e dos Remédios • 64 Espécies, Pranchas Científicas & Preparações",
        "epigraph": "“Minha mãe conhecia ervas que não tinham nome nos livros. Em Sellene encontrei livros cujos autores jamais haviam tocado as ervas que descreviam.”",
        "desc": "Compêndio ilustrado com pranchas renascentistas científicas por Loreo Seleni: 64 espécies de Alenia (H01–H64) em 8 regiões, graus de evidência, coleta, cultivo, preparações, aplicação às 6 doenças e caderno reservado ao Mestre selado por AES-256.",
        "cover_map": "assets/capa_10_herbario_seleni.jpg",
        "gm_only": False,
    },
    {
        "src": "11_Cronica_das_Terras_e_das_Mares.md",
        "out": "11_Cronica_das_Terras_e_das_Mares.html",
        "num": "TOMO XI",
        "short": "Linha do Tempo",
        "title": "Crônica das Terras e das Marés",
        "subtitle": "Linha do Tempo de Alenia • 100 Acontecimentos em 8 Épocas, Pranchas Históricas & Atlas",
        "epigraph": "“O rei mandou escrever que fundara a cidade. Debaixo da praça onde ergueram sua estátua encontramos três ruas, dois cemitérios e a soleira de uma casa.”",
        "desc": "Linha do tempo ilustrada em pergaminho medieval com 100 acontecimentos (T001–T100) das terras antigas ao Ano 418 EF, 8 pranchas renascentistas científicas, filtros por época e marcos canônicos, atlas de fundações, hidrografia e caderno do Mestre selado por AES-256.",
        "cover_map": "assets/capa_11_cronica_alenia.jpg",
        "gm_only": False,
    },
    {
        "src": "12_Cozinhas_de_Alenia.md",
        "out": "12_Cozinhas_de_Alenia.html",
        "num": "TOMO XII",
        "short": "Culinária",
        "title": "Cozinhas de Alenia",
        "subtitle": "44 Pratos Ilustrados em 8 Tradições Regionais e 3 Cadernos Temáticos, 26 Animais & Despensa do Herbário",
        "epigraph": "“Uma mesa de Alenia revela quem controla a água, quais barcos chegaram ao porto, que caminhos a neve fechou e quem conseguiu guardar grão para o inverno.”",
        "desc": "Guia culinário ilustrado com 44 pratos em 11 pranchas (C01–C44) — incluindo iguarias incomuns, quartéis e sobremesas —, 26 animais ilustrados de pesca, caça e criação (A01–A26), integração direta ao Herbário de Seleni, preços no Padrão Prata, sazonalidade e cenas de mesa.",
        "cover_map": "assets/capa_12_cozinhas_alenia.jpg",
        "gm_only": False,
    },
    {
        "src": "13_Grandes_Nomes_e_Feitos_de_Alenia.md",
        "out": "13_Grandes_Nomes_e_Feitos_de_Alenia.html",
        "num": "TOMO XIII • MESTRE",
        "short": "🔒 Grandes Nomes",
        "title": "Grandes Nomes e Feitos de Alenia",
        "subtitle": "100 Perfis em 10 Círculos Sociais • Linhagens, Origens, Aparências, Personalidades e Legados",
        "epigraph": "“Nem todo nome que mudou o mundo foi gravado numa coroa.”",
        "desc": "Edição secreta do Mestre: 100 perfis biográficos (N001–N100) cruzando os 12 tomos anteriores — 44 personagens desenvolvidos + A Sombra, 19 nomes da onomástica, 36 novas figuras, genealogias, 12 encontros cruzados e segredos da aventura, do Acervo e da Comunhão.",
        "cover_map": "assets/capa_13_grandes_nomes_alenia.jpg",
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

BESTIARY_PLATES = {
    "1. Salteador de Estrada": "assets/b_plate_17.jpg",
    "2. Guarda de Cidade": "assets/b_plate_18.jpg",
    "3. Corsário do Mar dos Corais": "assets/b_plate_19.jpg",
    "4. Guerreiro Tribal de Gaddra": "assets/b_plate_20.jpg",
    "5. Assassino da Floresta Negra": "assets/b_plate_21.jpg",
    "6. Mestre Espadachim": "assets/b_plate_22.jpg",
    "7. Inquisidor da Chama Branca": "assets/b_plate_01.jpg",
    "8. Lobo-das-Brumas": "assets/b_plate_23.jpg",
    "9. Serpente-do-Pântano": "assets/b_plate_24.jpg",
    "10. Escorpião-Gigante das Dunas": "assets/b_plate_25.jpg",
    "11. Urso-de-Rubecina": "assets/b_plate_02.jpg",
    "12. Cervo-de-Galhada-Férrea": "assets/b_plate_03.jpg",
    "13. Abutre-Osso": "assets/b_plate_04.jpg",
    "14. Hiena-de-Sal": "assets/b_plate_05.jpg",
    "15. Cantora-de-Recife": "assets/b_plate_06.jpg",
    "16. Polvo-de-Quilha": "assets/b_plate_07.jpg",
    "17. Verme-de-Maré": "assets/b_plate_08.jpg",
    "18. Leviatã-dos-Recifes": "assets/b_plate_26.jpg",
    "19. O Repetidor": "assets/b_plate_09.jpg",
    "20. Lanterna-de-Turfa": "assets/b_plate_10.jpg",
    "21. Tece-Arame": "assets/b_plate_11.jpg",
    "22. Tronco-de-Sangue": "assets/b_plate_12.jpg",
    "23. Mastim-de-Vitro": "assets/b_plate_13.jpg",
    "24. Ressonante-de-Mina": "assets/b_plate_14.jpg",
    "25. Bando de Corvos-de-Cinzas": "assets/b_plate_15.jpg",
    "26. Errante do Piche": "assets/b_plate_27.jpg",
    "27. Sentinela-de-Laca": "assets/b_plate_16.jpg",
    "28. Sombra das Ruínas Perdidas": "assets/b_plate_28.jpg",
    "29. Hospedeiro em Confluência": "assets/b_plate_29.jpg",
    "30. A Primeira Devolvida": "assets/b_plate_30.jpg",
    "31. O Regente das Cinzas": "assets/b_plate_31.jpg",
}

GM_SECTION_H2_PREFIXES = ("7. A Grande Ameaça:", "Caderno reservado ao mestre")
GM_SECTION_H3_PREFIXES = ("O Simbionte da Comunhão",)


def encrypt_payload(plaintext: str, password: str) -> str:
    salt = os.urandom(16)
    iv = os.urandom(12)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=PBKDF2_ITERS)
    key = kdf.derive(password.encode("utf-8"))
    ct = AESGCM(key).encrypt(iv, plaintext.encode("utf-8"), None)
    return json.dumps({
        "v": 1, "it": PBKDF2_ITERS,
        "s": base64.b64encode(salt).decode("ascii"),
        "i": base64.b64encode(iv).decode("ascii"),
        "c": base64.b64encode(ct).decode("ascii"),
    }, separators=(",", ":"))


CODEX_REGISTRY = None


def get_codex_registry():
    global CODEX_REGISTRY
    if CODEX_REGISTRY is None:
        CODEX_REGISTRY = build_codex_registry(ROOT_DIR)
    return CODEX_REGISTRY


def make_gm_gate_block(label: str, subtitle: str, encrypted_body_html: str, encrypted_toc_html: str = "", codex_file: str = "", compendium_mode: bool = False) -> str:
    if codex_file:
        encrypted_body_html = link_codex_html(
            encrypted_body_html,
            codex_file,
            get_codex_registry(),
            compendium_mode=compendium_mode,
            allow_gm_names=True,
        )
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
    --desk: #171411;
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
    --sidebar-w: 274px;
    --topbar-h: 52px;
    --footbar-h: 56px;
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; background: var(--desk); color: var(--ink); }
body {
    margin: 0;
    font-family: 'EB Garamond', 'Palatino Linotype', 'Book Antiqua', Georgia, serif;
    font-size: 16.5px;
    line-height: 1.56;
    background: radial-gradient(circle at top, #2a241d 0%, #171411 60%, #0e0c0a 100%);
    min-height: 100vh;
}

/* TOP BAR — ULTRA-CLEAN SINGLE ROW ON ALL MONITORS */
.topbar {
    position: fixed; top: 0; left: 0; right: 0; height: var(--topbar-h);
    background: rgba(18, 15, 12, 0.97);
    border-bottom: 1px solid rgba(154, 123, 59, 0.45);
    display: flex; align-items: center; justify-content: space-between; gap: 10px;
    padding: 0 14px; z-index: 1000; backdrop-filter: blur(8px);
}
.topbar-left {
    display: flex; align-items: center; gap: 8px; min-width: 0; overflow: hidden;
}
.topbar-brand {
    font-family: 'Cinzel', Georgia, serif; font-weight: 700; font-size: 14px;
    letter-spacing: 0.14em; color: var(--gold-light); text-decoration: none; white-space: nowrap;
    margin-left: 4px;
}
.topbar-current {
    font-family: 'EB Garamond', Georgia, serif; font-style: italic; font-size: 14.5px;
    color: #bfb5a2; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    padding-left: 8px; border-left: 1px solid rgba(154, 123, 59, 0.35);
}
.topbar-nav { display: flex; align-items: center; gap: 6px; flex-wrap: nowrap; flex-shrink: 0; }
.topbar-nav a, .btn-print, .btn-lock, .btn-toc-toggle {
    font-family: 'Cinzel', Georgia, serif; font-size: 10.5px; letter-spacing: 0.06em;
    text-transform: uppercase; color: #ded5c3; text-decoration: none; white-space: nowrap;
    padding: 6px 10px; border-radius: 3px; border: 1px solid transparent;
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
.btn-toc-toggle { border-color: rgba(154, 123, 59, 0.42); color: #e8decb; background: rgba(154, 123, 59, 0.09); }
.btn-toc-toggle:hover, .btn-toc-toggle.active { color: var(--gold-light); border-color: var(--gold); background: rgba(154, 123, 59, 0.22); }

/* UNIFIED SIDEBAR (LIBRARY NAVIGATION + VOLUME TOC) */
.sidebar {
    position: fixed; top: var(--topbar-h); left: 0; bottom: 0; width: var(--sidebar-w);
    background: rgba(19, 16, 14, 0.985); border-right: 1px solid rgba(154, 123, 59, 0.42);
    padding: 12px 12px 24px; overflow-y: auto; z-index: 960;
    transition: transform 0.22s ease;
    box-shadow: 8px 0 32px rgba(0, 0, 0, 0.58);
    scrollbar-width: thin;
    scrollbar-color: rgba(154, 123, 59, 0.35) transparent;
}
body.book-mode .sidebar { bottom: var(--footbar-h); }
body.sidebar-hidden .sidebar { transform: translateX(-100%); box-shadow: none; }
body.sidebar-hidden .book-shell { margin-left: 0; }

.sidebar-backdrop {
    display: none; position: fixed; top: var(--topbar-h); left: 0; right: 0; bottom: 0;
    background: rgba(8, 6, 5, 0.52); z-index: 940; backdrop-filter: blur(1px);
}
body.book-mode:not(.sidebar-hidden) .sidebar-backdrop { display: block; }

.sidebar-tabs {
    display: flex; gap: 4px; margin-bottom: 12px; padding-bottom: 10px;
    border-bottom: 1px solid rgba(154, 123, 59, 0.35);
}
.sidebar-tab {
    flex: 1 1 0; font-family: 'Cinzel', Georgia, serif; font-size: 10px; letter-spacing: 0.08em;
    text-transform: uppercase; padding: 6px 6px; border-radius: 3px; cursor: pointer;
    border: 1px solid rgba(154, 123, 59, 0.32); background: rgba(255, 255, 255, 0.03);
    color: #bfb5a2; transition: all 0.15s ease; text-align: center;
}
.sidebar-tab:hover { color: var(--gold-light); border-color: rgba(154, 123, 59, 0.6); }
.sidebar-tab.active {
    background: rgba(122, 31, 29, 0.72); border-color: var(--gold); color: #f7f1e3; font-weight: 700;
}
.sidebar-pane { display: none; }
.sidebar-pane.active { display: block; }

.sidebar-title {
    font-family: 'Cinzel', Georgia, serif; font-size: 10.5px; letter-spacing: 0.14em;
    text-transform: uppercase; color: var(--gold-light);
    border-bottom: 1px solid rgba(154, 123, 59, 0.32); padding-bottom: 7px; margin: 0 0 10px 0;
}
.lib-group-label {
    font-family: 'Cinzel', Georgia, serif; font-size: 9.5px; letter-spacing: 0.15em;
    text-transform: uppercase; color: var(--gold); margin: 12px 0 5px 6px; opacity: 0.9;
}
.lib-group-label:first-child { margin-top: 2px; }
.lib-list { list-style: none; padding: 0; margin: 0; }
.lib-list li { margin: 2px 0; }
.lib-link {
    display: flex; align-items: center; gap: 8px; text-decoration: none;
    color: #dfd6c4; font-size: 14.5px; line-height: 1.3; padding: 6px 9px;
    border-radius: 3px; border-left: 2px solid transparent; transition: all 0.14s ease;
}
.lib-link:hover {
    color: var(--gold-light); background: rgba(154, 123, 59, 0.14); border-left-color: rgba(205, 176, 110, 0.6);
}
.lib-link.active {
    color: #fff6e0; background: rgba(122, 31, 29, 0.55); border-left-color: var(--gold-light); font-weight: 600;
}
.lib-link.gm-link { color: #e2cfa8; }
.lib-num {
    font-family: 'Cinzel', Georgia, serif; font-size: 9.5px; letter-spacing: 0.06em;
    color: var(--gold-light); min-width: 24px; opacity: 0.85;
}
.toc-list { list-style: none; padding: 0; margin: 0; }
.toc-list li { margin: 2px 0; }
.toc-list a {
    display: block; text-decoration: none; color: #cfc6b4; font-size: 14px;
    line-height: 1.32; padding: 5px 8px; border-radius: 3px; border-left: 2px solid transparent;
}
.toc-list a:hover, .toc-list a.toc-active {
    color: var(--gold-light); background: rgba(154, 123, 59, 0.14); border-left-color: var(--gold);
}
.toc-h2 a { font-weight: 600; color: #e8decb; margin-top: 5px; }
.toc-h3 a { padding-left: 16px; font-size: 13px; color: #b5ab98; }

/* =====================================================
   HARDCOVER BOOK READER MODE (DEFAULT ON ALL TOMES)
   ===================================================== */
body.book-mode {
    overflow: hidden;
}

.reader-stage {
    margin-left: 0;
    margin-top: var(--topbar-h);
    height: calc(100vh - var(--topbar-h) - var(--footbar-h));
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 6px 46px;
    position: relative;
}

/* Source container hidden when in paginated book-mode, visible in scroll-mode or print */
body.book-mode .book-shell { display: none; }
body.scroll-mode .reader-stage,
body.scroll-mode .reader-footer-bar .pager-controls,
body.scroll-mode .font-scale-group { display: none; }
body.scroll-mode { overflow: auto; }
body.scroll-mode .book-shell { padding-bottom: 84px; }

/* Book Hardcover Leather Binding + Double Page Spread */
.hardcover-wrap {
    display: flex;
    align-items: stretch;
    justify-content: center;
    background: linear-gradient(135deg, #3c2218 0%, #26140e 50%, #3a2016 100%);
    padding: 6px 8px;
    border-radius: 7px;
    border: 1px solid rgba(154, 123, 59, 0.55);
    box-shadow:
        0 26px 70px rgba(0, 0, 0, 0.78),
        0 6px 18px rgba(0, 0, 0, 0.55),
        inset 0 0 0 1px rgba(205, 176, 110, 0.22);
    max-width: 100%;
    max-height: 100%;
    position: relative;
}

.book-spread {
    display: flex;
    align-items: stretch;
    justify-content: center;
    gap: 0;
    position: relative;
    perspective: 2600px;
    transform-style: preserve-3d;
}

/* =====================================================
   3D PHYSICAL PAGE-TURN ANIMATION
   ===================================================== */
.flip-sheet {
    position: absolute;
    top: 0;
    height: 100%;
    z-index: 30;
    transform-style: preserve-3d;
    pointer-events: none;
    will-change: transform;
}
.flip-sheet.flip-next {
    left: 50%;
    width: 50%;
    transform-origin: left center;
    animation: turnPageNext 560ms cubic-bezier(0.42, 0.04, 0.22, 1) forwards;
}
.flip-sheet.flip-prev {
    left: 0;
    width: 50%;
    transform-origin: right center;
    animation: turnPagePrev 560ms cubic-bezier(0.42, 0.04, 0.22, 1) forwards;
}
.flip-sheet.flip-single-next {
    left: 0;
    width: 100%;
    transform-origin: left center;
    animation: turnSingleNext 480ms cubic-bezier(0.42, 0.04, 0.22, 1) forwards;
}
.flip-sheet.flip-single-prev {
    left: 0;
    width: 100%;
    transform-origin: left center;
    animation: turnSinglePrev 480ms cubic-bezier(0.42, 0.04, 0.22, 1) forwards;
}

.flip-face {
    position: absolute;
    inset: 0;
    backface-visibility: hidden;
    -webkit-backface-visibility: hidden;
    overflow: hidden;
}
.flip-face > .leaf {
    width: 100% !important;
    height: 100% !important;
}
.flip-face::before {
    content: "";
    position: absolute;
    inset: 0;
    z-index: 4;
    pointer-events: none;
    opacity: 0;
}
.flip-sheet.flip-next .flip-front::before {
    background: linear-gradient(90deg, rgba(24,16,8,0.28) 0%, rgba(24,16,8,0.08) 45%, rgba(255,250,235,0.16) 100%);
    animation: shadeFrontHalf 560ms ease-in-out forwards;
}
.flip-sheet.flip-next .flip-back::before {
    background: linear-gradient(270deg, rgba(24,16,8,0.28) 0%, rgba(24,16,8,0.08) 45%, rgba(255,250,235,0.16) 100%);
    animation: shadeBackHalf 560ms ease-in-out forwards;
}
.flip-sheet.flip-prev .flip-front::before {
    background: linear-gradient(270deg, rgba(24,16,8,0.28) 0%, rgba(24,16,8,0.08) 45%, rgba(255,250,235,0.16) 100%);
    animation: shadeFrontHalf 560ms ease-in-out forwards;
}
.flip-sheet.flip-prev .flip-back::before {
    background: linear-gradient(90deg, rgba(24,16,8,0.28) 0%, rgba(24,16,8,0.08) 45%, rgba(255,250,235,0.16) 100%);
    animation: shadeBackHalf 560ms ease-in-out forwards;
}
.flip-back.flip-back-next { transform: rotateY(180deg); }
.flip-back.flip-back-prev { transform: rotateY(-180deg); }

.flip-cast-shadow {
    position: absolute;
    top: 0;
    bottom: 0;
    width: 50%;
    z-index: 20;
    pointer-events: none;
}
.flip-cast-shadow.shadow-next {
    right: 0;
    background: linear-gradient(90deg, rgba(22, 14, 7, 0.36) 0%, rgba(22, 14, 7, 0.12) 45%, transparent 100%);
    animation: castShadowSweep 560ms ease-in-out forwards;
}
.flip-cast-shadow.shadow-prev {
    left: 0;
    background: linear-gradient(270deg, rgba(22, 14, 7, 0.36) 0%, rgba(22, 14, 7, 0.12) 45%, transparent 100%);
    animation: castShadowSweep 560ms ease-in-out forwards;
}

@keyframes turnPageNext {
    0%   { transform: rotateY(0deg); box-shadow: -2px 0 8px rgba(0,0,0,0.08); }
    45%  { box-shadow: -22px 10px 36px rgba(15, 9, 4, 0.42); }
    55%  { box-shadow: 22px 10px 36px rgba(15, 9, 4, 0.42); }
    100% { transform: rotateY(-180deg); box-shadow: 2px 0 8px rgba(0,0,0,0.06); }
}
@keyframes turnPagePrev {
    0%   { transform: rotateY(0deg); box-shadow: 2px 0 8px rgba(0,0,0,0.08); }
    45%  { box-shadow: 22px 10px 36px rgba(15, 9, 4, 0.42); }
    55%  { box-shadow: -22px 10px 36px rgba(15, 9, 4, 0.42); }
    100% { transform: rotateY(180deg); box-shadow: -2px 0 8px rgba(0,0,0,0.06); }
}
@keyframes turnSingleNext {
    0%   { transform: rotateY(0deg); opacity: 1; box-shadow: 0 8px 24px rgba(0,0,0,0.22); }
    72%  { opacity: 0.94; box-shadow: -20px 10px 34px rgba(0,0,0,0.42); }
    100% { transform: rotateY(-108deg); opacity: 0; }
}
@keyframes turnSinglePrev {
    0%   { transform: rotateY(-102deg); opacity: 0.12; box-shadow: -20px 10px 34px rgba(0,0,0,0.42); }
    35%  { opacity: 0.96; }
    100% { transform: rotateY(0deg); opacity: 1; box-shadow: 0 8px 20px rgba(0,0,0,0.12); }
}
@keyframes shadeFrontHalf {
    0%   { opacity: 0; }
    48%  { opacity: 1; }
    52%  { opacity: 0; }
    100% { opacity: 0; }
}
@keyframes shadeBackHalf {
    0%   { opacity: 0; }
    48%  { opacity: 0; }
    52%  { opacity: 1; }
    100% { opacity: 0; }
}
@keyframes castShadowSweep {
    0%   { opacity: 0.78; }
    50%  { opacity: 0.35; }
    100% { opacity: 0; }
}

.book-spread.anim-cover-open {
    animation: coverOpenSwing 500ms cubic-bezier(0.22, 0.85, 0.32, 1) forwards;
}
.book-spread.anim-cover-close {
    animation: coverCloseSwing 440ms cubic-bezier(0.22, 0.85, 0.32, 1) forwards;
}
@keyframes coverOpenSwing {
    0%   { opacity: 0.35; transform: scale(0.95) rotateY(-12deg); }
    100% { opacity: 1; transform: scale(1) rotateY(0deg); }
}
@keyframes coverCloseSwing {
    0%   { opacity: 0.4; transform: scale(1.03) rotateY(14deg); }
    100% { opacity: 1; transform: scale(1) rotateY(0deg); }
}

/* Interactive tactile page corners */
.leaf-corner-btn {
    position: absolute;
    bottom: 0;
    width: 44px;
    height: 44px;
    border: none;
    padding: 0;
    cursor: pointer;
    z-index: 12;
    background: transparent;
    transition: all 0.2s ease;
}
.leaf-corner-next {
    right: 0;
    background: linear-gradient(315deg, rgba(154,123,59,0.22) 0%, rgba(154,123,59,0.12) 28%, transparent 50%);
}
.leaf-corner-next:hover {
    width: 58px;
    height: 58px;
    background: linear-gradient(315deg, #d7c7a7 0%, #efe6d3 36%, rgba(90,62,32,0.24) 48%, transparent 52%);
}
.leaf-corner-prev {
    left: 0;
    background: linear-gradient(45deg, rgba(154,123,59,0.22) 0%, rgba(154,123,59,0.12) 28%, transparent 50%);
}
.leaf-corner-prev:hover {
    width: 58px;
    height: 58px;
    background: linear-gradient(45deg, #d7c7a7 0%, #efe6d3 36%, rgba(90,62,32,0.24) 48%, transparent 52%);
}

.leaf {
    width: var(--leaf-w, 660px);
    height: var(--leaf-h, 780px);
    background: var(--vellum);
    color: var(--ink);
    position: relative;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    border: 1px solid #c9ba9a;
}

.leaf.leaf-left {
    border-radius: 3px 0 0 3px;
    border-right: none;
    background: linear-gradient(90deg, #f3ecdc 0%, #f8f2e4 7%, #f8f2e4 91%, #e7dcc4 98%, #d7c7a7 100%);
    box-shadow: inset -16px 0 24px -12px rgba(45, 30, 15, 0.34);
}

.leaf.leaf-right {
    border-radius: 0 3px 3px 0;
    border-left: 1px solid rgba(72, 52, 32, 0.22);
    background: linear-gradient(90deg, #d8c8a9 0%, #e9dec7 3%, #f8f2e4 10%, #f8f2e4 93%, #f1e8d6 100%);
    box-shadow: inset 16px 0 24px -12px rgba(45, 30, 15, 0.34);
}

.leaf.leaf-single {
    border-radius: 3px;
    background: linear-gradient(90deg, #efe6d4 0%, #f8f2e4 5%, #f8f2e4 95%, #efe6d4 100%);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.35);
}

.leaf::after {
    content: "";
    position: absolute;
    inset: 9px;
    border: 1px solid rgba(154, 123, 59, 0.26);
    pointer-events: none;
}

.leaf-header {
    height: 30px;
    padding: 8px 34px 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--ink-soft);
    opacity: 0.8;
    flex-shrink: 0;
}

.leaf-body {
    flex: 1 1 auto;
    min-height: 0;
    padding: 10px 34px 10px;
    overflow: hidden;
    font-size: calc(17.5px * var(--font-scale, 1));
    line-height: 1.54;
}
.leaf-body h1.book-h1 { font-size: calc(24px * var(--font-scale, 1)); }
.leaf-body h2 { font-size: calc(19.5px * var(--font-scale, 1)); margin: 14px 0 8px; }
.leaf-body h3 { font-size: calc(16px * var(--font-scale, 1)); margin: 12px 0 6px; }
.leaf-body .table-wrap { overflow-x: hidden; margin: 8px 0 11px; }
.leaf-body table { width: 100%; font-size: calc(13.8px * var(--font-scale, 1)); line-height: 1.35; border-collapse: collapse; }
.leaf-body thead th { padding: 5px 6px; font-size: calc(10px * var(--font-scale, 1)); overflow-wrap: break-word; }
.leaf-body tbody td { padding: 5px 6px; overflow-wrap: break-word; word-break: normal; }
.leaf-body table.table-dense { font-size: calc(12.2px * var(--font-scale, 1)); line-height: 1.3; }
.leaf-body table.table-dense thead th { padding: 4px 5px; font-size: calc(9.3px * var(--font-scale, 1)); }
.leaf-body table.table-dense tbody td { padding: 4px 5px; }
.leaf-body table.table-ultra-dense { font-size: calc(11.1px * var(--font-scale, 1)); line-height: 1.25; }
.leaf-body table.table-ultra-dense thead th { padding: 3.5px 4px; font-size: calc(8.6px * var(--font-scale, 1)); letter-spacing: 0.04em; }
.leaf-body table.table-ultra-dense tbody td { padding: 3.5px 4px; }
.leaf-body .nowrap-cell { white-space: nowrap; }
.leaf-body blockquote.bq-cont { margin-top: 4px; border-left-style: dashed; }
.leaf-body .callout { font-size: calc(16px * var(--font-scale, 1)); }
.leaf-body .entry-card { font-size: calc(14.2px * var(--font-scale, 1)); line-height: 1.36; padding: 9px 12px 7px; margin: 6px 0 8px; }
.leaf-body .entry-card.entry-card-cont { border-top-style: dashed; border-top-width: 2px; }
.leaf-body .entry-card h3 { font-size: calc(15.5px * var(--font-scale, 1)); margin: 0 0 5px; padding-bottom: 3px; }
.leaf-body .entry-card p { margin-bottom: 5px; }
.leaf-body .entry-card ul { margin: 3px 0 4px; padding-left: 17px; }
.leaf-body .entry-card li { margin-bottom: 2.5px; }
.leaf-body .atlas-plate { margin: 8px 0 10px; padding: 6px; }
.leaf-body .atlas-plate img { max-height: calc(var(--leaf-h, 760px) * 0.48); width: auto; max-width: 100%; height: auto; margin: 0 auto; }
.leaf-body .atlas-plate.creature-plate { margin: 5px 0 7px; padding: 4px; background: #e8dec7; border: 1px solid var(--gold); box-shadow: 0 4px 12px rgba(0,0,0,0.16); }
.leaf-body .atlas-plate.creature-plate img { width: 100%; aspect-ratio: 16 / 9; max-height: min(250px, calc(var(--leaf-h, 760px) * 0.27)); object-fit: cover; display: block; border: 1px solid #3c3124; cursor: zoom-in; }
.creature-plate { margin: 7px 0 9px; padding: 5px; background: #e8dec7; border: 1px solid var(--gold); box-shadow: 0 4px 12px rgba(0,0,0,0.16); }
.creature-plate img { width: 100%; aspect-ratio: 16 / 9; max-height: 280px; object-fit: cover; display: block; border: 1px solid #3c3124; cursor: zoom-in; }

.leaf-footer {
    height: 30px;
    padding: 0 34px 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Cinzel', Georgia, serif;
    font-size: 11.5px;
    letter-spacing: 0.12em;
    color: var(--ink-soft);
    flex-shrink: 0;
}

.leaf.leaf-blank {
    background: linear-gradient(90deg, #e5dac3 0%, #f2ead8 14%, #f4ede0 100%);
}
.leaf-blank-ornament {
    margin: auto;
    font-family: 'Cinzel', Georgia, serif;
    color: rgba(154, 123, 59, 0.38);
    font-size: 28px;
    letter-spacing: 0.2em;
}

/* Side floating turn arrows */
.side-turn-btn {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    width: 34px;
    height: 70px;
    background: rgba(20, 17, 14, 0.85);
    color: var(--gold-light);
    border: 1px solid rgba(154, 123, 59, 0.5);
    border-radius: 4px;
    font-size: 24px;
    line-height: 1;
    cursor: pointer;
    z-index: 50;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.16s ease;
}
.side-turn-btn:hover:not(:disabled) {
    background: var(--crimson);
    color: #fff;
    border-color: var(--gold-light);
}
.side-turn-btn:disabled { opacity: 0.22; cursor: default; }
.side-turn-prev { left: 6px; }
.side-turn-next { right: 6px; }

.font-scale-group {
    display: flex;
    align-items: center;
    gap: 4px;
}
.font-scale-label {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10px;
    color: #bfb5a2;
    min-width: 38px;
    text-align: center;
}

/* BOTTOM READER BAR */
.reader-footer-bar {
    position: fixed;
    left: 0; right: 0; bottom: 0;
    height: var(--footbar-h);
    background: rgba(18, 15, 12, 0.97);
    border-top: 1px solid rgba(154, 123, 59, 0.4);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 18px;
    z-index: 1000;
    gap: 12px;
}

.pager-controls {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 0 auto;
}

.pager-btn {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 11px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 7px 14px;
    background: #231e19;
    color: #ede4d1;
    border: 1px solid rgba(154, 123, 59, 0.5);
    border-radius: 3px;
    cursor: pointer;
    transition: all 0.15s;
}
.pager-btn:hover:not(:disabled) { background: var(--crimson); color: #fff; border-color: var(--gold-light); }
.pager-btn:disabled { opacity: 0.35; cursor: default; }

.pager-status {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 12px;
    letter-spacing: 0.08em;
    color: var(--gold-light);
    min-width: 150px;
    text-align: center;
}

.pager-jump {
    width: 58px;
    padding: 5px 6px;
    text-align: center;
    font-family: 'Cinzel', Georgia, serif;
    font-size: 12px;
    background: #12100d;
    color: #f7f1e3;
    border: 1px solid rgba(154, 123, 59, 0.5);
    border-radius: 3px;
}

.view-mode-group {
    display: flex;
    align-items: center;
    gap: 4px;
}

.mode-btn {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 6px 9px;
    background: transparent;
    color: #bfb5a2;
    border: 1px solid rgba(154, 123, 59, 0.3);
    border-radius: 3px;
    cursor: pointer;
}
.mode-btn.active, .mode-btn:hover {
    background: rgba(154, 123, 59, 0.2);
    color: var(--gold-light);
    border-color: var(--gold);
}

/* SCROLL / PORTAL LAYOUT */
.book-shell { margin-left: var(--sidebar-w); padding: 78px 26px 64px; display: flex; justify-content: center; }
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

/* COVER PAGE */
.cover-page {
    min-height: 580px; display: flex; flex-direction: column; justify-content: center; align-items: center;
    text-align: center; padding: 34px 28px; margin-bottom: 42px;
    border: 2px solid var(--crimson); outline: 1px solid var(--gold); outline-offset: -7px;
    background: radial-gradient(circle at center, #fbf7ee 0%, #f3ead6 100%);
    page-break-after: always; break-after: page;
}
.leaf-body .cover-page {
    min-height: 100%;
    height: 100%;
    margin: 0;
    padding: 18px 20px;
    overflow: hidden;
}
.leaf-body .cover-title {
    font-size: clamp(22px, calc(var(--leaf-h, 760px) * 0.044), 36px);
}
.leaf-body .cover-subtitle {
    font-size: clamp(14.5px, calc(var(--leaf-h, 760px) * 0.023), 19px);
    margin: 8px 0 4px;
}
.leaf-body .cover-epigraph {
    font-size: clamp(13.5px, calc(var(--leaf-h, 760px) * 0.021), 17px);
    margin: 10px auto 6px;
}
.leaf-body .cover-thumb {
    max-height: calc(var(--leaf-h, 760px) * 0.34);
    margin: 10px auto;
}
.leaf-body .cover-edition {
    padding-top: 10px;
}
.cover-kicker {
    font-family: 'Cinzel', Georgia, serif; font-size: 11.5px; letter-spacing: 0.24em;
    text-transform: uppercase; color: var(--crimson); margin-bottom: 10px;
}
.cover-rule {
    width: 150px; height: 2px;
    background: linear-gradient(90deg, transparent, var(--gold), var(--crimson), var(--gold), transparent);
    margin: 14px auto;
}
.cover-title {
    font-family: 'Cinzel', Georgia, serif; font-size: 38px; font-weight: 800; line-height: 1.14;
    letter-spacing: 0.08em; color: var(--ink); margin: 0; text-transform: uppercase;
}
.cover-subtitle {
    font-family: 'EB Garamond', Georgia, serif; font-style: italic; font-size: 20px;
    color: var(--ink-soft); margin: 10px 0 6px; max-width: 560px;
}
.cover-epigraph { font-style: italic; font-size: 18px; color: var(--crimson-dark); max-width: 500px; margin: 16px auto 10px; }
.cover-thumb {
    max-width: 100%; max-height: 290px; border: 2px solid var(--gold);
    box-shadow: 0 8px 20px rgba(0,0,0,0.2); margin: 14px auto; border-radius: 2px;
}
.cover-edition {
    margin-top: auto; padding-top: 18px; font-family: 'Cinzel', Georgia, serif;
    font-size: 10px; letter-spacing: 0.2em; text-transform: uppercase; color: var(--ink-soft);
}

/* GM ENCRYPTED VAULT GATE */
.gm-gate-box {
    margin: 16px 0;
    padding: 28px 22px;
    text-align: center;
    background: linear-gradient(180deg, #1d1916 0%, #151210 100%);
    color: #efe6d2;
    border: 2px solid var(--gold);
    outline: 1px solid var(--crimson);
    outline-offset: -6px;
    border-radius: 4px;
    box-shadow: 0 10px 26px rgba(0,0,0,0.32);
}
.gm-vault[data-locked="false"] .gm-gate-box { display: none; }
.gm-seal-icon { font-size: 30px; margin-bottom: 6px; }
.gm-gate-kicker {
    font-family: 'Cinzel', Georgia, serif; font-size: 10.5px; letter-spacing: 0.2em;
    color: var(--gold-light); text-transform: uppercase; margin-bottom: 4px;
}
.gm-gate-title {
    font-family: 'Cinzel', Georgia, serif; font-size: 20px; color: #f7f1e3;
    border: none; margin: 4px 0 8px; padding: 0;
}
.gm-gate-desc {
    text-align: center; color: #cfc6b4; font-style: italic; max-width: 440px; margin: 0 auto 16px; font-size: 15.5px;
}
.gm-unlock-form { display: flex; gap: 8px; justify-content: center; flex-wrap: wrap; max-width: 390px; margin: 0 auto; }
.gm-pwd-input {
    flex: 1 1 180px; padding: 8px 12px; font-family: 'EB Garamond', Georgia, serif; font-size: 16px;
    background: #100e0c; color: #f7f1e3; border: 1px solid var(--gold); border-radius: 3px;
}
.gm-pwd-input:focus { outline: none; border-color: var(--gold-light); box-shadow: 0 0 0 2px rgba(205,176,110,0.28); }
.gm-unlock-btn {
    padding: 8px 16px; font-family: 'Cinzel', Georgia, serif; font-size: 11px; font-weight: 700;
    letter-spacing: 0.1em; text-transform: uppercase; cursor: pointer;
    background: var(--crimson); color: #f7f1e3; border: 1px solid var(--gold); border-radius: 3px;
}
.gm-unlock-btn:hover { background: #962724; }
.gm-gate-error { margin-top: 10px; min-height: 20px; font-size: 14px; color: #f08a84; font-weight: 600; }

/* CONTENT TYPOGRAPHY */
h1, h2, h3, h4 { font-family: 'Cinzel', Georgia, serif; color: var(--crimson); break-after: avoid; page-break-after: avoid; }
h1.book-h1 {
    font-size: 23px; letter-spacing: 0.05em; text-transform: uppercase;
    border-bottom: 2px solid var(--crimson); padding-bottom: 8px; margin: 0 0 16px 0;
}
h2 { font-size: 18px; letter-spacing: 0.04em; margin: 18px 0 10px; padding-bottom: 5px; border-bottom: 1px solid var(--gold); }
h3 { font-size: 15px; letter-spacing: 0.03em; margin: 14px 0 6px; color: #3d2415; }
p { margin: 0 0 10px; text-align: justify; hyphens: auto; }
ul, ol { margin: 4px 0 12px; padding-left: 20px; }
li { margin-bottom: 4px; }
strong { color: #17120d; }
code {
    font-family: Consolas, 'Courier New', monospace; font-size: 0.84em;
    background: rgba(154, 123, 59, 0.14); border: 1px solid rgba(154, 123, 59, 0.28);
    padding: 1px 4px; border-radius: 3px; color: #5b1d18;
}
hr { border: none; height: 1px; background: linear-gradient(90deg, transparent, var(--gold), transparent); margin: 16px 0; }
a { color: var(--crimson); text-decoration: underline; text-decoration-color: rgba(122, 31, 29, 0.35); text-underline-offset: 2px; }

blockquote {
    margin: 12px 0 14px; padding: 10px 15px; background: var(--vellum-card);
    border-left: 3px solid var(--gold); font-style: italic; color: var(--ink-soft); break-inside: avoid;
}
.callout {
    margin: 12px 0; padding: 11px 14px; border-radius: 2px; border: 1px solid var(--border);
    border-left: 4px solid var(--crimson); background: #f2e7d3; color: var(--ink); break-inside: avoid; font-size: 15.5px;
}
.callout-title {
    font-family: 'Cinzel', Georgia, serif; font-size: 11px; font-weight: 700;
    letter-spacing: 0.1em; text-transform: uppercase; color: var(--crimson); margin-bottom: 4px;
}
.callout.warning { border-left-color: #b4691e; background: #f6ecd7; }
.callout.warning .callout-title { color: #8c4d10; }

.formula-box {
    margin: 10px 0 14px; padding: 9px 12px; background: #efe5cf;
    border: 1px solid var(--gold); border-radius: 3px; text-align: center;
    font-size: 16px; font-weight: 600; color: var(--crimson-dark); break-inside: avoid;
}

.table-wrap { width: 100%; overflow-x: auto; margin: 10px 0 14px; }
table { width: 100%; border-collapse: collapse; font-size: 13.8px; line-height: 1.38; border: 1px solid var(--gold); }
thead th {
    font-family: 'Cinzel', Georgia, serif; font-size: 10px; letter-spacing: 0.04em;
    text-transform: uppercase; background: var(--crimson); color: #f7f1e3;
    padding: 7px 7px; border: 1px solid #5f1816; text-align: left;
}
tbody td { padding: 6px 7px; border: 1px solid var(--border); vertical-align: top; }
tbody tr:nth-child(even) { background: var(--vellum-alt); }
tr { break-inside: avoid; }

.atlas-plate {
    margin: 10px 0 14px; padding: 8px; background: #ebe1ca;
    border: 1px solid var(--gold); box-shadow: 0 5px 14px rgba(0,0,0,0.14);
    text-align: center; break-inside: avoid;
}
.atlas-plate img { width: 100%; height: auto; max-height: 460px; object-fit: contain; display: block; border: 1px solid #3c3124; cursor: zoom-in; }
.atlas-caption {
    font-family: 'Cinzel', Georgia, serif; font-size: 10.5px; letter-spacing: 0.07em;
    text-transform: uppercase; color: var(--ink-soft); margin-top: 6px;
}

.entry-card {
    margin: 10px 0 12px; padding: 11px 14px 9px; background: var(--vellum-card);
    border: 1px solid var(--border); border-top: 3px solid var(--crimson); border-radius: 2px; break-inside: avoid;
    font-size: 15.2px;
}
.entry-card h3 { margin-top: 0; color: var(--crimson); border-bottom: 1px solid rgba(154, 123, 59, 0.45); padding-bottom: 4px; }

.lightbox {
    display: none; position: fixed; inset: 0; background: rgba(10, 9, 8, 0.92);
    z-index: 2000; padding: 24px; align-items: center; justify-content: center; cursor: zoom-out;
}
.lightbox.open { display: flex; }
.lightbox img { max-width: 96vw; max-height: 92vh; border: 2px solid var(--gold); box-shadow: 0 20px 60px rgba(0,0,0,0.8); }

/* PORTAL GRID (INDEX.HTML) */
.portal-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 18px; margin: 22px 0 32px; }
.portal-card {
    display: flex; flex-direction: column; background: var(--vellum-card);
    border: 1px solid var(--border); border-top: 4px solid var(--crimson);
    padding: 16px 16px 15px; text-decoration: none; color: var(--ink);
    transition: transform 0.16s ease, box-shadow 0.16s ease;
}
.portal-cover {
    width: 100%; height: 148px; object-fit: cover; display: block;
    border: 1px solid var(--gold); border-radius: 2px; margin-bottom: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.22);
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
    .sidebar { transform: translateX(-100%); }
    body.sidebar-open-mobile .sidebar { transform: translateX(0); box-shadow: 6px 0 30px rgba(0,0,0,0.7); }
    body.sidebar-open-mobile .sidebar-backdrop { display: block; }
    .book-shell, .reader-stage { margin-left: 0; }
    .book-page { padding: 28px 22px 42px; }
    .side-turn-btn { display: none; }
}
@media (max-width: 640px) {
    .topbar-current { display: none; }
    .topbar { padding: 0 10px; }
    .topbar-brand { font-size: 12.5px; letter-spacing: 0.1em; }
    .btn-toc-toggle, .btn-print, .btn-lock { padding: 5px 7px; font-size: 9.5px; }
}

@media (prefers-reduced-motion: reduce) {
    .book-spread, .flip-sheet, .flip-cast-shadow, .flip-face::before { animation: none !important; }
}

@page { size: A4; margin: 16mm 15mm 18mm 15mm; }
@media print {
    html, body { background: #ffffff !important; font-size: 10.8pt; line-height: 1.5; overflow: visible !important; }
    .topbar, .sidebar, .lightbox, .gm-gate-box, .reader-stage, .reader-footer-bar { display: none !important; }
    body.book-mode .book-shell, .book-shell { display: block !important; margin: 0 !important; padding: 0 !important; }
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
    const MODE_KEY = 'alenia_reader_mode';
    const FONT_KEY = 'alenia_font_scale';

    function b64ToBytes(b64) {
        const bin = atob(b64);
        const bytes = new Uint8Array(bin.length);
        for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
        return bytes;
    }

    async function decryptBlock(cipherObj, password) {
        const enc = new TextEncoder();
        const keyMat = await crypto.subtle.importKey('raw', enc.encode(password), { name: 'PBKDF2' }, false, ['deriveKey']);
        const aesKey = await crypto.subtle.deriveKey(
            { name: 'PBKDF2', salt: b64ToBytes(cipherObj.s), iterations: cipherObj.it, hash: 'SHA-256' },
            keyMat, { name: 'AES-GCM', length: 256 }, false, ['decrypt']
        );
        const plainBuf = await crypto.subtle.decrypt(
            { name: 'AES-GCM', iv: b64ToBytes(cipherObj.i) }, aesKey, b64ToBytes(cipherObj.c)
        );
        return JSON.parse(new TextDecoder().decode(plainBuf));
    }

    function tagNowrapCells(root) {
        const reShortNum = /^\s*(?:[+-]?\d+(?:\s*[–\-—]\s*\d+)?|[+-]?\d*d\d+(?:\s*[+-]\s*\d+)?|\d+(?:,\d+)?[×x%]?)\s*$/i;
        (root || document).querySelectorAll('table').forEach(tbl => {
            const cols = tbl.querySelectorAll('thead th').length;
            if (cols >= 6) tbl.classList.add('table-ultra-dense');
            else if (cols === 5) tbl.classList.add('table-dense');
            if (cols <= 4) {
                tbl.querySelectorAll('tbody td').forEach(td => {
                    if (td.children.length === 0 || (td.children.length === 1 && td.firstElementChild.tagName === 'STRONG')) {
                        const txt = (td.textContent || '').trim();
                        if (txt.length > 0 && txt.length <= 10 && reShortNum.test(txt)) {
                            td.classList.add('nowrap-cell');
                        }
                    }
                });
            }
        });
    }

    /* =====================================================
       HARDCOVER BOOK PAGINATOR ENGINE
       ===================================================== */
    const BookReader = {
        enabled: false,
        mode: 'spread', // 'spread' (2 pages), 'single' (1 page), 'scroll'
        pages: [],      // array of HTML strings (one per book page)
        anchorMap: {},  // element id -> page index (0-based)
        currentIdx: 0,  // index of left (or single) page shown
        bookTitle: '',

        fontScale: 1,

        async init() {
            const stage = document.getElementById('reader-stage');
            if (!stage) return; // index.html portal does not paginate
            this.enabled = true;
            this.bookTitle = document.body.dataset.bookTitle || 'Alenia RPG';

            const savedScale = parseFloat(localStorage.getItem(FONT_KEY) || '1');
            if (!isNaN(savedScale) && savedScale >= 0.8 && savedScale <= 1.4) {
                this.fontScale = Math.round(savedScale * 20) / 20;
            }
            this.applyFontScale(this.fontScale, false);

            const savedMode = localStorage.getItem(MODE_KEY);
            if (savedMode === 'spread' || savedMode === 'single' || savedMode === 'scroll') {
                this.mode = savedMode;
            } else {
                this.mode = window.innerWidth >= 1040 ? 'spread' : 'single';
            }

            // Wait briefly for web fonts so initial page count is accurate on first paint
            if (document.fonts && document.fonts.ready) {
                await Promise.race([
                    document.fonts.ready,
                    new Promise(res => setTimeout(res, 1200))
                ]);
            }

            this.bindControls();
            this.applyMode(this.mode, false);

            // Jump directly to URL hash anchor (e.g. 10_Herbario_de_Seleni.html#h24)
            this.lockedHash = (window.location.hash || '').slice(1);
            if (this.lockedHash) {
                this.jumpToAnchor(this.lockedHash, false);
            }

            // Re-paginate cleanly if any map image finishes loading after initial paint
            const source = document.querySelector('.book-page');
            if (source) {
                let imgTimer = null;
                source.querySelectorAll('img').forEach(img => {
                    if (!img.complete) {
                        img.addEventListener('load', () => {
                            clearTimeout(imgTimer);
                            imgTimer = setTimeout(() => {
                                if (this.mode !== 'scroll') {
                                    const prev = this.currentIdx;
                                    this.paginate();
                                    if (this.lockedHash && this.anchorMap[this.lockedHash] !== undefined) {
                                        this.goToPage(this.anchorMap[this.lockedHash], false);
                                    } else {
                                        this.goToPage(Math.min(prev, Math.max(0, this.pages.length - 1)));
                                    }
                                }
                            }, 120);
                        }, { once: true });
                    }
                });
            }

            let resizeTimer = null;
            window.addEventListener('resize', () => {
                clearTimeout(resizeTimer);
                resizeTimer = setTimeout(() => {
                    if (this.mode !== 'scroll') {
                        const prev = this.currentIdx;
                        this.paginate();
                        this.goToPage(Math.min(prev, Math.max(0, this.pages.length - 1)));
                    }
                }, 220);
            });
        },

        applyFontScale(scale, repaginate = true) {
            this.fontScale = Math.max(0.85, Math.min(1.35, Math.round(scale * 20) / 20));
            document.documentElement.style.setProperty('--font-scale', String(this.fontScale));
            const lbl = document.getElementById('font-scale-label');
            if (lbl) lbl.textContent = Math.round(this.fontScale * 100) + '%';
            if (repaginate) {
                localStorage.setItem(FONT_KEY, String(this.fontScale));
                if (this.mode !== 'scroll') {
                    const prev = this.currentIdx;
                    this.paginate();
                    this.goToPage(Math.min(prev, Math.max(0, this.pages.length - 1)));
                }
            }
        },

        effectiveMode() {
            if (this.mode === 'scroll') return 'scroll';
            if (this.mode === 'spread' && window.innerWidth < 1040) return 'single';
            return this.mode;
        },

        computeLeafDimensions() {
            const eff = this.effectiveMode();
            // Full-width book stage (sidebar opens as overlay drawer so book is ALWAYS large & centered!)
            const availW = window.innerWidth - 96;
            const availH = window.innerHeight - 52 - 56 - 16;
            const leafH = Math.max(500, Math.min(1040, availH));
            let leafW;
            if (eff === 'spread') {
                // Generous open hardcover spread filling ~88-94% of desktop viewport
                const maxByAspect = Math.round(leafH * 0.90);
                leafW = Math.min(820, maxByAspect, Math.floor(availW / 2) - 9);
                leafW = Math.max(380, leafW);
            } else {
                const maxByAspect = Math.round(leafH * 0.92);
                leafW = Math.min(880, maxByAspect, Math.max(320, availW));
            }
            document.documentElement.style.setProperty('--leaf-w', leafW + 'px');
            document.documentElement.style.setProperty('--leaf-h', leafH + 'px');
            // 2px border + 30px header + 30px footer + 20px safety breathing room (guarantees ZERO clipping / ZERO scrollbars)
            return { leafW, leafH, bodyH: leafH - 82 };
        },

        collectBlocks(container) {
            const blocks = [];
            function walk(parent) {
                for (const child of Array.from(parent.children)) {
                    if (child.tagName === 'SECTION' && child.classList.contains('tome-divider')) {
                        walk(child);
                    } else if (child.classList.contains('gm-vault') && child.getAttribute('data-locked') === 'false') {
                        const unlocked = child.querySelector('.gm-unlocked-content');
                        if (unlocked) walk(unlocked);
                    } else {
                        blocks.push(child);
                    }
                }
            }
            walk(container);
            return blocks;
        },

        paginate() {
            const source = document.querySelector('.book-page');
            if (!source) return;
            const { leafW, bodyH } = this.computeLeafDimensions();

            // Offscreen measurement leaf matching exact styles & width
            const measurer = document.createElement('div');
            measurer.className = 'leaf leaf-single';
            measurer.style.cssText = `position:fixed; left:-99999px; top:0; width:${leafW}px; height:auto; visibility:hidden; pointer-events:none;`;
            const mBody = document.createElement('div');
            mBody.className = 'leaf-body';
            mBody.style.overflow = 'visible';
            measurer.appendChild(mBody);
            document.body.appendChild(measurer);

            const rawBlocks = this.collectBlocks(source);
            const pages = [];
            const anchorMap = {};

            let curNodes = [];

            const flushPage = () => {
                if (curNodes.length === 0) return;
                const pageIdx = pages.length;
                const wrap = document.createElement('div');
                curNodes.forEach(n => {
                    if (n.id) anchorMap[n.id] = pageIdx;
                    n.querySelectorAll('[id]').forEach(el => { anchorMap[el.id] = pageIdx; });
                    wrap.appendChild(n);
                });
                pages.push(wrap.innerHTML);
                curNodes = [];
                mBody.innerHTML = '';
            };

            const isHeading = (el) => el && /^H[1-4]$/.test(el.tagName);

            const popOrphanHeadings = (allowShortIntro) => {
                const carried = [];
                // Optionally pull a single short intro <p> sitting right under a heading if there's earlier content on the page
                if (
                    allowShortIntro &&
                    curNodes.length >= 3 &&
                    curNodes[curNodes.length - 1].tagName === 'P' &&
                    (curNodes[curNodes.length - 1].textContent || '').trim().length <= 180 &&
                    isHeading(curNodes[curNodes.length - 2])
                ) {
                    carried.unshift(curNodes.pop());
                    if (mBody.lastChild) mBody.removeChild(mBody.lastChild);
                }
                while (curNodes.length > 0 && isHeading(curNodes[curNodes.length - 1])) {
                    carried.unshift(curNodes.pop());
                    if (mBody.lastChild) mBody.removeChild(mBody.lastChild);
                }
                // Never empty the entire page when carrying headings (prevents infinite loops)
                if (curNodes.length === 0 && carried.length > 0) {
                    carried.forEach(node => {
                        curNodes.push(node);
                        mBody.appendChild(node);
                    });
                    return [];
                }
                return carried;
            };

            const restoreCarried = (carried) => {
                carried.forEach(node => {
                    curNodes.push(node);
                    mBody.appendChild(node);
                });
            };

            const placeTableWrap = (tableWrap) => {
                tagNowrapCells(tableWrap);
                const table = tableWrap.querySelector('table');
                const tbody = table ? table.querySelector('tbody') : null;
                const rows = tbody ? Array.from(tbody.querySelectorAll(':scope > tr')) : [];
                if (!table || !tbody || rows.length <= 1) {
                    // Fallback to atomic placement for trivial 0-1 row tables
                    placeAtomic(tableWrap);
                    return;
                }

                // Fast path: whole table fits right now!
                mBody.appendChild(tableWrap);
                if (mBody.scrollHeight <= bodyH) {
                    curNodes.push(tableWrap);
                    return;
                }
                mBody.removeChild(tableWrap);

                const theadOrig = table.querySelector('thead');
                const tblCls = table.className || '';
                const buildChunk = () => {
                    const w = document.createElement('div');
                    w.className = tableWrap.className;
                    const t = document.createElement('table');
                    if (tblCls) t.className = tblCls;
                    if (theadOrig) t.appendChild(theadOrig.cloneNode(true));
                    const tb = document.createElement('tbody');
                    t.appendChild(tb);
                    w.appendChild(t);
                    return { w, tb };
                };

                let rowIdx = 0;
                while (rowIdx < rows.length) {
                    const chunk = buildChunk();
                    mBody.appendChild(chunk.w);
                    let addedHere = 0;

                    while (rowIdx < rows.length) {
                        const rowClone = rows[rowIdx].cloneNode(true);
                        chunk.tb.appendChild(rowClone);
                        if (mBody.scrollHeight > bodyH) {
                            if (addedHere === 0 && curNodes.length === 0) {
                                // Single super-tall row alone on fresh page: keep it so we make forward progress
                                addedHere++;
                                rowIdx++;
                                break;
                            }
                            chunk.tb.removeChild(rowClone);
                            break;
                        }
                        addedHere++;
                        rowIdx++;
                    }

                    // Avoid leaving just 1 lonely row at bottom of a non-empty page if more rows remain
                    if (addedHere === 0 || (addedHere === 1 && rowIdx < rows.length && curNodes.length > 0)) {
                        mBody.removeChild(chunk.w);
                        rowIdx -= addedHere;
                        const carried = popOrphanHeadings(true);
                        flushPage();
                        restoreCarried(carried);
                        continue;
                    }

                    curNodes.push(chunk.w);
                    if (rowIdx < rows.length) {
                        flushPage();
                    }
                }
            };

            const placeList = (listEl) => {
                const items = Array.from(listEl.children).filter(el => el.tagName === 'LI');
                if (items.length <= 1) {
                    placeAtomic(listEl);
                    return;
                }
                mBody.appendChild(listEl);
                if (mBody.scrollHeight <= bodyH) {
                    curNodes.push(listEl);
                    return;
                }
                mBody.removeChild(listEl);

                let idx = 0;
                const baseStart = parseInt(listEl.getAttribute('start') || '1', 10) || 1;
                while (idx < items.length) {
                    const chunk = document.createElement(listEl.tagName);
                    if (listEl.className) chunk.className = listEl.className;
                    if (listEl.tagName === 'OL' && idx > 0) {
                        chunk.setAttribute('start', String(baseStart + idx));
                    }
                    mBody.appendChild(chunk);
                    let addedHere = 0;

                    while (idx < items.length) {
                        const liClone = items[idx].cloneNode(true);
                        chunk.appendChild(liClone);
                        if (mBody.scrollHeight > bodyH) {
                            if (addedHere === 0 && curNodes.length === 0) {
                                addedHere++;
                                idx++;
                                break;
                            }
                            chunk.removeChild(liClone);
                            break;
                        }
                        addedHere++;
                        idx++;
                    }

                    if (addedHere === 0) {
                        mBody.removeChild(chunk);
                        const carried = popOrphanHeadings(true);
                        flushPage();
                        restoreCarried(carried);
                        continue;
                    }

                    curNodes.push(chunk);
                    if (idx < items.length) {
                        flushPage();
                    }
                }
            };

            const placeEntryCard = (cardEl) => {
                // Fast path 1: whole card fits on current page
                mBody.appendChild(cardEl);
                if (mBody.scrollHeight <= bodyH) {
                    curNodes.push(cardEl);
                    return;
                }
                mBody.removeChild(cardEl);

                // Fast path 2: flush current non-empty page and try placing whole card on fresh page
                if (curNodes.length > 0) {
                    const carried = popOrphanHeadings(true);
                    flushPage();
                    restoreCarried(carried);
                    mBody.appendChild(cardEl);
                    if (mBody.scrollHeight <= bodyH) {
                        curNodes.push(cardEl);
                        return;
                    }
                    mBody.removeChild(cardEl);
                }

                // Fallback: card itself is taller than a full page (e.g., epic boss or high font zoom) — split its children cleanly!
                const kids = Array.from(cardEl.children);
                let curCard = document.createElement('div');
                curCard.className = cardEl.className;
                mBody.appendChild(curCard);

                const startContinuationCard = () => {
                    if (curCard.children.length > 0) {
                        curNodes.push(curCard);
                        flushPage();
                    } else if (curCard.parentNode === mBody) {
                        mBody.removeChild(curCard);
                    }
                    curCard = document.createElement('div');
                    curCard.className = cardEl.className + ' entry-card-cont';
                    mBody.appendChild(curCard);
                };

                for (const child of kids) {
                    if (child.tagName === 'UL' || child.tagName === 'OL') {
                        const lis = Array.from(child.children).filter(el => el.tagName === 'LI');
                        let subList = document.createElement(child.tagName);
                        curCard.appendChild(subList);
                        for (const li of lis) {
                            const liClone = li.cloneNode(true);
                            subList.appendChild(liClone);
                            if (mBody.scrollHeight > bodyH && (subList.children.length > 1 || curCard.children.length > 1)) {
                                subList.removeChild(liClone);
                                if (subList.children.length === 0) curCard.removeChild(subList);
                                startContinuationCard();
                                subList = document.createElement(child.tagName);
                                curCard.appendChild(subList);
                                subList.appendChild(liClone);
                            }
                        }
                        if (subList.children.length === 0 && subList.parentNode === curCard) curCard.removeChild(subList);
                    } else {
                        const cClone = child.cloneNode(true);
                        curCard.appendChild(cClone);
                        if (mBody.scrollHeight > bodyH && curCard.children.length > 1) {
                            curCard.removeChild(cClone);
                            startContinuationCard();
                            curCard.appendChild(cClone);
                        }
                    }
                }
                if (curCard.children.length > 0) {
                    curNodes.push(curCard);
                } else if (curCard.parentNode === mBody) {
                    mBody.removeChild(curCard);
                }
            };

            const placeBlockquote = (bqEl) => {
                mBody.appendChild(bqEl);
                if (mBody.scrollHeight <= bodyH) {
                    curNodes.push(bqEl);
                    return;
                }
                mBody.removeChild(bqEl);

                const kids = Array.from(bqEl.children);
                if (kids.length <= 1) {
                    placeAtomic(bqEl);
                    return;
                }

                let idx = 0;
                while (idx < kids.length) {
                    const chunk = document.createElement('blockquote');
                    chunk.className = bqEl.className + (idx > 0 ? ' bq-cont' : '');
                    mBody.appendChild(chunk);
                    let addedHere = 0;

                    while (idx < kids.length) {
                        const cClone = kids[idx].cloneNode(true);
                        chunk.appendChild(cClone);
                        if (mBody.scrollHeight > bodyH) {
                            if (addedHere === 0 && curNodes.length === 0) {
                                addedHere++;
                                idx++;
                                break;
                            }
                            chunk.removeChild(cClone);
                            break;
                        }
                        addedHere++;
                        idx++;
                    }

                    if (addedHere === 0) {
                        mBody.removeChild(chunk);
                        const carried = popOrphanHeadings(true);
                        flushPage();
                        restoreCarried(carried);
                        continue;
                    }

                    curNodes.push(chunk);
                    if (idx < kids.length) {
                        flushPage();
                    }
                }
            };

            const placeAtomic = (clone) => {
                mBody.appendChild(clone);
                if (mBody.scrollHeight > bodyH && curNodes.length > 0) {
                    mBody.removeChild(clone);
                    const carried = popOrphanHeadings(true);
                    flushPage();
                    restoreCarried(carried);
                    curNodes.push(clone);
                    mBody.appendChild(clone);
                } else {
                    curNodes.push(clone);
                }
            };

            for (let idx = 0; idx < rawBlocks.length; idx++) {
                const orig = rawBlocks[idx];
                const clone = orig.cloneNode(true);

                // Cover pages always occupy their own dedicated full page
                if (clone.classList.contains('cover-page')) {
                    flushPage();
                    const pageIdx = pages.length;
                    if (clone.id) anchorMap[clone.id] = pageIdx;
                    pages.push(clone.outerHTML);
                    continue;
                }

                // Skip standalone <hr> at top of a fresh page
                if (clone.tagName === 'HR' && curNodes.length === 0) continue;

                // Start major H1 on a fresh page if current page already has content
                if (clone.tagName === 'H1' && curNodes.length > 0) {
                    flushPage();
                }

                if (clone.classList.contains('table-wrap')) {
                    placeTableWrap(clone);
                } else if (clone.classList.contains('entry-card')) {
                    placeEntryCard(clone);
                } else if (clone.tagName === 'BLOCKQUOTE') {
                    placeBlockquote(clone);
                } else if (clone.tagName === 'UL' || clone.tagName === 'OL') {
                    placeList(clone);
                } else {
                    placeAtomic(clone);
                }
            }
            flushPage();
            document.body.removeChild(measurer);

            this.pages = pages.length > 0 ? pages : ['<p>Volume vazio.</p>'];
            this.anchorMap = anchorMap;
        },

        flipTimer: null,
        pendingCommit: null,

        finishPendingFlip() {
            if (this.flipTimer) {
                clearTimeout(this.flipTimer);
                this.flipTimer = null;
            }
            if (this.pendingCommit) {
                const fn = this.pendingCommit;
                this.pendingCommit = null;
                fn();
            }
        },

        isCoverPage(i) {
            return Boolean(this.pages[i] && this.pages[i].includes('class="cover-page"'));
        },

        normalizeIdx(rawIdx) {
            const total = this.pages.length;
            let idx = Math.max(0, Math.min(rawIdx, total - 1));
            if (this.effectiveMode() === 'spread') {
                if (!(idx === 0 && this.isCoverPage(0))) {
                    if (idx % 2 === 0) idx = Math.max(1, idx - 1);
                }
            }
            return idx;
        },

        makeLeafHtml(pageIdx, sideCls, interactive = true) {
            const total = this.pages.length;
            if (pageIdx < 0 || pageIdx >= total) {
                return `<div class="leaf ${sideCls} leaf-blank"><div class="leaf-blank-ornament">✦</div></div>`;
            }
            const cover = this.isCoverPage(pageIdx);
            const hdr = cover ? '' : `<div class="leaf-header"><span>ALENIA RPG</span><span>${this.bookTitle}</span></div>`;
            const ftr = cover ? '' : `<div class="leaf-footer">— ${pageIdx + 1} —</div>`;
            let corner = '';
            if (interactive) {
                if ((sideCls === 'leaf-right' || sideCls === 'leaf-single') && pageIdx + 1 < total) {
                    corner += '<button class="leaf-corner-btn leaf-corner-next" type="button" title="Virar página (→)" aria-label="Próxima página"></button>';
                }
                if (sideCls === 'leaf-left' || (sideCls === 'leaf-single' && pageIdx > 0)) {
                    corner += '<button class="leaf-corner-btn leaf-corner-prev" type="button" title="Página anterior (←)" aria-label="Página anterior"></button>';
                }
            }
            return `<div class="leaf ${sideCls}">${hdr}<div class="leaf-body">${this.pages[pageIdx]}</div>${ftr}${corner}</div>`;
        },

        updateHud(idx) {
            const eff = this.effectiveMode();
            const total = this.pages.length;
            let statusText = '';
            if (eff === 'spread') {
                if (idx === 0 && this.isCoverPage(0)) {
                    statusText = `Capa • 1 / ${total}`;
                } else {
                    const rNum = Math.min(total, idx + 2);
                    statusText = (idx + 1 < total) ? `Págs. ${idx + 1}–${rNum} de ${total}` : `Pág. ${idx + 1} de ${total}`;
                }
            } else {
                statusText = (idx === 0 && this.isCoverPage(0)) ? `Capa • 1 / ${total}` : `Pág. ${idx + 1} de ${total}`;
            }

            const statusEl = document.getElementById('pager-status');
            if (statusEl) statusEl.textContent = statusText;
            const jumpEl = document.getElementById('pager-jump');
            if (jumpEl) { jumpEl.value = String(idx + 1); jumpEl.max = String(total); }

            const atStart = idx === 0;
            const atEnd = eff === 'spread' ? (idx === 0 ? total <= 1 : idx + 2 >= total) : (idx + 1 >= total);
            document.querySelectorAll('.btn-prev-page').forEach(b => b.disabled = atStart);
            document.querySelectorAll('.btn-next-page').forEach(b => b.disabled = atEnd);

            this.highlightActiveToc(idx, eff === 'spread' ? idx + 1 : idx);
        },

        renderCurrentSpread() {
            this.finishPendingFlip();
            const spreadEl = document.getElementById('book-spread');
            if (!spreadEl) return;
            const eff = this.effectiveMode();
            const idx = this.normalizeIdx(this.currentIdx);
            this.currentIdx = idx;

            spreadEl.classList.remove('anim-cover-open', 'anim-cover-close');
            if (eff === 'spread' && !(idx === 0 && this.isCoverPage(0))) {
                spreadEl.innerHTML = this.makeLeafHtml(idx, 'leaf-left', true) + this.makeLeafHtml(idx + 1, 'leaf-right', true);
            } else {
                spreadEl.innerHTML = this.makeLeafHtml(idx, 'leaf-single', true);
            }
            this.updateHud(idx);
        },

        turnTo(rawTargetIdx, dir) {
            this.finishPendingFlip();
            const spreadEl = document.getElementById('book-spread');
            if (!spreadEl) return;

            const eff = this.effectiveMode();
            const prevIdx = this.normalizeIdx(this.currentIdx);
            const nextIdx = this.normalizeIdx(rawTargetIdx);
            if (nextIdx === prevIdx) return;

            const direction = dir || (nextIdx > prevIdx ? 1 : -1);
            const reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
            if (reduced) {
                this.currentIdx = nextIdx;
                this.renderCurrentSpread();
                return;
            }

            this.currentIdx = nextIdx;
            this.updateHud(nextIdx);

            const prevWasCover = eff === 'spread' && prevIdx === 0 && this.isCoverPage(0);
            const nextIsCover = eff === 'spread' && nextIdx === 0 && this.isCoverPage(0);

            // Case 1: Opening or closing the hardcover cover
            if (prevWasCover || nextIsCover) {
                spreadEl.classList.remove('anim-cover-open', 'anim-cover-close');
                if (nextIsCover) {
                    spreadEl.innerHTML = this.makeLeafHtml(0, 'leaf-single', true);
                } else {
                    spreadEl.innerHTML = this.makeLeafHtml(nextIdx, 'leaf-left', true) + this.makeLeafHtml(nextIdx + 1, 'leaf-right', true);
                }
                void spreadEl.offsetWidth;
                const cls = prevWasCover ? 'anim-cover-open' : 'anim-cover-close';
                spreadEl.classList.add(cls);
                const commit = () => spreadEl.classList.remove(cls);
                this.pendingCommit = commit;
                this.flipTimer = setTimeout(() => { this.flipTimer = null; this.pendingCommit = null; commit(); }, 500);
                return;
            }

            // Case 2: 2-Page Open Spread Physical Double-Sided 3D Flip
            if (eff === 'spread') {
                const isNext = direction > 0;
                const baseLeft = isNext ? prevIdx : nextIdx;
                const baseRight = isNext ? nextIdx + 1 : prevIdx + 1;
                const frontPage = isNext ? prevIdx + 1 : prevIdx;
                const backPage = isNext ? nextIdx : nextIdx + 1;

                const flipCls = isNext ? 'flip-next' : 'flip-prev';
                const frontSide = isNext ? 'leaf-right' : 'leaf-left';
                const backSide = isNext ? 'leaf-left' : 'leaf-right';
                const backFlipCls = isNext ? 'flip-back-next' : 'flip-back-prev';
                const shadowCls = isNext ? 'shadow-next' : 'shadow-prev';

                spreadEl.innerHTML =
                    this.makeLeafHtml(baseLeft, 'leaf-left', false) +
                    this.makeLeafHtml(baseRight, 'leaf-right', false) +
                    `<div class="flip-cast-shadow ${shadowCls}"></div>` +
                    `<div class="flip-sheet ${flipCls}">` +
                        `<div class="flip-face flip-front">${this.makeLeafHtml(frontPage, frontSide, false)}</div>` +
                        `<div class="flip-face flip-back ${backFlipCls}">${this.makeLeafHtml(backPage, backSide, false)}</div>` +
                    `</div>`;

                const commit = () => {
                    spreadEl.innerHTML = this.makeLeafHtml(nextIdx, 'leaf-left', true) + this.makeLeafHtml(nextIdx + 1, 'leaf-right', true);
                };
                this.pendingCommit = commit;
                this.flipTimer = setTimeout(() => { this.flipTimer = null; this.pendingCommit = null; commit(); }, 570);
                return;
            }

            // Case 3: Single-Page 3D Peel / Swing-In
            const isNext = direction > 0;
            const underIdx = isNext ? nextIdx : prevIdx;
            const sheetIdx = isNext ? prevIdx : nextIdx;
            const flipCls = isNext ? 'flip-single-next' : 'flip-single-prev';

            spreadEl.innerHTML =
                this.makeLeafHtml(underIdx, 'leaf-single', false) +
                `<div class="flip-sheet ${flipCls}">` +
                    `<div class="flip-face flip-front">${this.makeLeafHtml(sheetIdx, 'leaf-single', false)}</div>` +
                `</div>`;

            const commit = () => {
                spreadEl.innerHTML = this.makeLeafHtml(nextIdx, 'leaf-single', true);
            };
            this.pendingCommit = commit;
            this.flipTimer = setTimeout(() => { this.flipTimer = null; this.pendingCommit = null; commit(); }, 490);
        },

        highlightActiveToc(pStart, pEnd) {
            document.querySelectorAll('.toc-list a').forEach(a => {
                const href = a.getAttribute('href') || '';
                if (!href.startsWith('#')) return;
                const targetPage = this.anchorMap[href.slice(1)];
                const active = targetPage !== undefined && targetPage >= pStart && targetPage <= pEnd;
                a.classList.toggle('toc-active', active);
            });
        },

        step(dir) {
            if (this.effectiveMode() === 'scroll') return;
            const eff = this.effectiveMode();
            let target = this.currentIdx;
            if (eff === 'spread') {
                if (dir > 0) {
                    if (this.currentIdx === 0) target = 1;
                    else target = Math.min(this.pages.length - 1, this.currentIdx + 2);
                } else {
                    if (this.currentIdx <= 1) target = 0;
                    else target = Math.max(1, this.currentIdx - 2);
                }
            } else {
                target = Math.max(0, Math.min(this.pages.length - 1, this.currentIdx + dir));
            }
            this.turnTo(target, dir);
        },

        goToPage(pageIdx, animate = false) {
            const clamped = Math.max(0, Math.min(this.pages.length - 1, pageIdx));
            if (animate) {
                this.turnTo(clamped);
            } else {
                this.currentIdx = clamped;
                this.renderCurrentSpread();
            }
        },

        applyMode(newMode, persist = true) {
            if (!newMode) return;
            this.finishPendingFlip();
            this.mode = newMode;
            if (persist) localStorage.setItem(MODE_KEY, newMode);
            document.body.classList.toggle('book-mode', newMode !== 'scroll');
            document.body.classList.toggle('scroll-mode', newMode === 'scroll');
            if (newMode === 'scroll' && window.innerWidth > 1020) {
                document.body.classList.remove('sidebar-hidden');
            } else if (newMode !== 'scroll') {
                document.body.classList.add('sidebar-hidden');
            }
            document.querySelectorAll('.mode-btn[data-mode]').forEach(b => {
                b.classList.toggle('active', b.dataset.mode === newMode);
            });
            if (newMode !== 'scroll') {
                this.paginate();
                this.renderCurrentSpread();
            }
        },

        flashAnchorTarget(id) {
            const run = () => {
                const scope = (this.mode !== 'scroll' && document.getElementById('book-spread'))
                    ? document.getElementById('book-spread')
                    : document;
                const el = scope.querySelector(`[id="${CSS.escape(id)}"]`) || document.getElementById(id);
                if (!el) return;
                const target = el.classList.contains('codex-anchor') ? (el.closest('h1,h2,h3,h4,article,tr,section') || el.parentElement) : el;
                if (!target) return;
                target.classList.remove('codex-target-flash');
                void target.offsetWidth;
                target.classList.add('codex-target-flash');
            };
            setTimeout(run, this.mode !== 'scroll' ? 600 : 80);
            setTimeout(run, 60);
        },

        jumpToAnchor(rawId, animate = true) {
            const id = decodeURIComponent((rawId || '').replace(/^#/, ''));
            if (!id) return false;
            if (this.mode !== 'scroll') {
                const pageIdx = this.anchorMap[id];
                if (pageIdx === undefined) return false;
                this.lockedHash = '';
                this.goToPage(pageIdx, animate);
                document.body.classList.add('sidebar-hidden');
                document.body.classList.remove('sidebar-open-mobile');
                this.flashAnchorTarget(id);
                return true;
            }
            const el = document.getElementById(id);
            if (!el) return false;
            const scrollEl = el.classList.contains('codex-anchor') ? (el.closest('h1,h2,h3,h4,article,tr,section') || el) : el;
            scrollEl.scrollIntoView({ behavior: animate ? 'smooth' : 'auto', block: 'start' });
            this.flashAnchorTarget(id);
            return true;
        },

        bindControls() {
            document.querySelectorAll('.btn-prev-page').forEach(b => b.addEventListener('click', () => this.step(-1)));
            document.querySelectorAll('.btn-next-page').forEach(b => b.addEventListener('click', () => this.step(1)));

            // Clickable tactile book page corners
            const spreadEl = document.getElementById('book-spread');
            if (spreadEl) {
                spreadEl.addEventListener('click', (e) => {
                    if (e.target.closest('.leaf-corner-next')) {
                        e.stopPropagation();
                        this.step(1);
                    } else if (e.target.closest('.leaf-corner-prev')) {
                        e.stopPropagation();
                        this.step(-1);
                    }
                });
            }

            const jumpEl = document.getElementById('pager-jump');
            if (jumpEl) {
                jumpEl.addEventListener('change', () => {
                    const n = parseInt(jumpEl.value, 10);
                    if (!isNaN(n)) this.goToPage(n - 1, true);
                });
            }

            document.querySelectorAll('.mode-btn[data-mode]').forEach(b => {
                b.addEventListener('click', () => this.applyMode(b.dataset.mode, true));
            });

            const btnFontDown = document.getElementById('btn-font-down');
            const btnFontUp = document.getElementById('btn-font-up');
            if (btnFontDown) btnFontDown.addEventListener('click', () => this.applyFontScale(this.fontScale - 0.1, true));
            if (btnFontUp) btnFontUp.addEventListener('click', () => this.applyFontScale(this.fontScale + 0.1, true));

            // Keyboard arrow / PageUp / PageDown turning
            document.addEventListener('keydown', (e) => {
                if (this.mode === 'scroll') return;
                if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) return;
                if (e.key === 'ArrowRight' || e.key === 'PageDown') { e.preventDefault(); this.step(1); }
                else if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); this.step(-1); }
            });

            // Intercept ALL in-page anchor clicks (sidebar TOC + codex links inside book pages!)
            document.addEventListener('click', (e) => {
                const a = e.target.closest('a[href^="#"]');
                if (!a) return;
                const id = a.getAttribute('href').slice(1);
                if (!id) return;
                if (this.jumpToAnchor(id, true)) {
                    e.preventDefault();
                    try { history.replaceState(null, '', '#' + id); } catch (_) {}
                }
            });

            window.addEventListener('hashchange', () => {
                const id = (window.location.hash || '').slice(1);
                if (id) this.jumpToAnchor(id, true);
            });
        }
    };

    /* =====================================================
       CODEX ANCHOR CONTROLLER (NON-BOOK PAGES: CULINÁRIA / CRÔNICA)
       ===================================================== */
    (function initScrollCodexNav() {
        if (document.body.classList.contains('has-book-reader')) return;
        function focusCodexHash(rawId, smooth) {
            const id = decodeURIComponent((rawId || '').replace(/^#/, ''));
            if (!id) return false;
            if (typeof window.aleniaRevealAnchor === 'function') {
                window.aleniaRevealAnchor(id);
            }
            const el = document.getElementById(id);
            if (!el) return false;
            const target = el.classList.contains('codex-anchor') ? (el.closest('h1,h2,h3,h4,article,tr,section') || el) : el;
            target.scrollIntoView({ behavior: smooth ? 'smooth' : 'auto', block: 'start' });
            target.classList.remove('codex-target-flash');
            void target.offsetWidth;
            target.classList.add('codex-target-flash');
            return true;
        }
        document.addEventListener('click', (e) => {
            const a = e.target.closest('a[href^="#"]');
            if (!a) return;
            const id = a.getAttribute('href').slice(1);
            if (!id) return;
            if (focusCodexHash(id, true)) {
                e.preventDefault();
                try { history.replaceState(null, '', '#' + id); } catch (_) {}
            }
        });
        window.addEventListener('hashchange', () => focusCodexHash(window.location.hash, true));
        if (window.location.hash) {
            setTimeout(() => focusCodexHash(window.location.hash, false), 120);
        }
    })();

    /* =====================================================
       GLOBAL SIDEBAR NAVIGATION CONTROLLER (ALL PAGES)
       ===================================================== */
    (function initSidebarNav() {
        const isMobile = () => window.innerWidth <= 1020;
        const isOpen = () => isMobile()
            ? document.body.classList.contains('sidebar-open-mobile')
            : !document.body.classList.contains('sidebar-hidden');
        const closeSidebar = () => {
            document.body.classList.add('sidebar-hidden');
            document.body.classList.remove('sidebar-open-mobile');
        };
        const openSidebar = () => {
            if (isMobile()) document.body.classList.add('sidebar-open-mobile');
            else document.body.classList.remove('sidebar-hidden');
        };
        let activeTab = 'lib';
        const setTab = (tab) => {
            const pane = document.getElementById('sidebar-pane-' + tab);
            if (!pane) return;
            activeTab = tab;
            document.querySelectorAll('.sidebar-tab').forEach(b => b.classList.toggle('active', b.dataset.tab === tab));
            document.querySelectorAll('.sidebar-pane').forEach(p => p.classList.toggle('active', p.id === 'sidebar-pane-' + tab));
        };

        const toggleForTab = (tab) => {
            if (isOpen() && (activeTab === tab || !document.getElementById('sidebar-pane-toc'))) {
                closeSidebar();
            } else {
                setTab(tab);
                openSidebar();
            }
        };

        const btnLib = document.getElementById('btn-lib-toggle');
        const btnToc = document.getElementById('btn-toc-toggle');
        if (btnLib) btnLib.addEventListener('click', () => toggleForTab('lib'));
        if (btnToc) btnToc.addEventListener('click', () => toggleForTab('toc'));

        document.querySelectorAll('.sidebar-tab').forEach(b => {
            b.addEventListener('click', () => setTab(b.dataset.tab));
        });

        const backdrop = document.getElementById('sidebar-backdrop');
        if (backdrop) backdrop.addEventListener('click', closeSidebar);

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && isOpen() && (document.body.classList.contains('book-mode') || isMobile())) {
                closeSidebar();
            }
        });
    })();

    /* =====================================================
       GM AES-256-GCM VAULT UNLOCKER (SYNCS WITH BOOK MODE)
       ===================================================== */
    async function unlockAllVaults(password, silent) {
        // Always decrypt the authoritative vaults inside .book-page first!
        const sourceRoot = document.querySelector('.book-page') || document;
        const vaults = sourceRoot.querySelectorAll('.gm-vault[data-locked="true"]');
        let anyUnlocked = false;
        let failed = false;

        for (const v of vaults) {
            const scriptEl = v.querySelector('script.gm-cipher');
            const outEl = v.querySelector('.gm-unlocked-content');
            if (!scriptEl || !outEl) continue;
            try {
                const cipherObj = JSON.parse(scriptEl.textContent);
                const data = await decryptBlock(cipherObj, password);
                outEl.innerHTML = data.html || '';
                v.setAttribute('data-locked', 'false');
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
            }
        }

        if (anyUnlocked) {
            sessionStorage.setItem(SESSION_KEY, password);
            const lockBtn = document.getElementById('btn-lock-gm');
            if (lockBtn) lockBtn.classList.add('visible');
            if (BookReader.enabled && BookReader.mode !== 'scroll') {
                const cur = BookReader.currentIdx;
                BookReader.paginate();
                BookReader.goToPage(cur);
            }
            document.dispatchEvent(new CustomEvent('alenia:gm-unlocked'));
        } else if (failed) {
            if (silent) {
                sessionStorage.removeItem(SESSION_KEY);
            } else {
                document.querySelectorAll('.gm-gate-error').forEach(el => {
                    el.textContent = 'Senha incorreta — o selo do Mestre permanece fechado.';
                });
            }
        }
    }

    // Document-level event delegation (works cleanly across cloned book pages & scroll mode)
    document.addEventListener('submit', async (e) => {
        const form = e.target.closest('.gm-unlock-form');
        if (!form) return;
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

    document.addEventListener('click', (e) => {
        const img = e.target.closest('.atlas-plate img');
        if (!img) return;
        const lb = document.getElementById('atlas-lightbox');
        const lbImg = document.getElementById('atlas-lightbox-img');
        if (lb && lbImg) {
            lbImg.src = img.src;
            lb.classList.add('open');
        }
    });

    document.addEventListener('DOMContentLoaded', async () => {
        const lb = document.getElementById('atlas-lightbox');
        if (lb) {
            lb.addEventListener('click', () => lb.classList.remove('open'));
            document.addEventListener('keydown', (e) => { if (e.key === 'Escape') lb.classList.remove('open'); });
        }

        const lockBtn = document.getElementById('btn-lock-gm');
        if (lockBtn) {
            if (sessionStorage.getItem(SESSION_KEY)) lockBtn.classList.add('visible');
            lockBtn.addEventListener('click', () => {
                sessionStorage.removeItem(SESSION_KEY);
                location.reload();
            });
        }

        // If already unlocked in this session, decrypt BEFORE initial pagination!
        const saved = sessionStorage.getItem(SESSION_KEY);
        if (saved && window.crypto && window.crypto.subtle) {
            await unlockAllVaults(saved, true);
        }

        await BookReader.init();
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
        (os.path.join(ROOT_DIR, "capas", "capa_10_herbario_seleni.jpg"), "capa_10_herbario_seleni.jpg"),
        (os.path.join(ROOT_DIR, "capas", "capa_11_cronica_alenia.jpg"), "capa_11_cronica_alenia.jpg"),
        (os.path.join(ROOT_DIR, "capas", "capa_12_cozinhas_alenia.jpg"), "capa_12_cozinhas_alenia.jpg"),
        (os.path.join(ROOT_DIR, "capas", "capa_13_grandes_nomes_alenia.jpg"), "capa_13_grandes_nomes_alenia.jpg"),
    ]
    for fn in sorted(os.listdir(os.path.join(ROOT_DIR, "ilustracoes"))) if os.path.isdir(os.path.join(ROOT_DIR, "ilustracoes")) else []:
        if fn.lower().endswith((".jpg", ".jpeg", ".png")):
            copies.append((os.path.join(ROOT_DIR, "ilustracoes", fn), fn))
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


_IMG_DIM_CACHE = {}


def img_dim_attrs(src_rel: str) -> str:
    if src_rel in _IMG_DIM_CACHE:
        return _IMG_DIM_CACHE[src_rel]
    out = ""
    try:
        from PIL import Image
        full = os.path.join(OUT_DIR, src_rel.replace("/", os.sep))
        if os.path.exists(full):
            with Image.open(full) as im:
                w, h = im.size
                out = f' width="{w}" height="{h}"'
    except Exception:
        out = ""
    _IMG_DIM_CACHE[src_rel] = out
    return out


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
        "08_Acervo_Oculto_de_Sellene.md": "08_Acervo_Oculto_de_Sellene.html",
        "09_Catalogo_de_Equipamentos_e_Oficios.md": "09_Catalogo_de_Equipamentos.html",
        "10_Herbario_de_Seleni.md": "10_Herbario_de_Seleni.html",
        "11_Cronica_das_Terras_e_das_Mares.md": "11_Cronica_das_Terras_e_das_Mares.html",
        "12_Cozinhas_de_Alenia.md": "12_Cozinhas_de_Alenia.html",
        "13_Grandes_Nomes_e_Feitos_de_Alenia.md": "13_Grandes_Nomes_e_Feitos_de_Alenia.html",
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
                if plain.startswith("Caderno reservado ao mestre"):
                    cur_label = "Caderno Reservado ao Mestre"
                else:
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


def md_to_html(md_text: str, id_prefix: str = "", card_h3: bool = False, inject_maps: bool = False, inject_bestiary_plates: bool = False, toc_start_idx: int = 0):
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
        if not stripped or re.match(r'^<a\s+id="[^"]*">\s*</a>$', stripped, re.I):
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

            codex_span = ""
            if level == 3:
                m_codex = re.match(r"^((?:H\d{2}|C\d{2}|A\d{2}|T\d{3}|N\d{3}))\s+[—–-]\s+", plain_title)
                if m_codex:
                    short_id = f"{id_prefix}{m_codex.group(1).lower()}"
                    codex_span = f'<span id="{short_id}" class="codex-anchor" aria-hidden="true"></span>'

            if level == 1:
                out.append(f'<h1 id="{hid}" class="book-h1">{inline_md(raw_title)}</h1>')
            else:
                out.append(f'<h{level} id="{hid}">{codex_span}{inline_md(raw_title)}</h{level}>')

            if level in (2, 3):
                toc.append((level, plain_title, hid))

            if inject_maps and level == 2:
                for key, (img_rel, cap) in CHAPTER_MAPS.items():
                    if plain_title.startswith(key):
                        out.append(
                            f'<figure class="atlas-plate">'
                            f'<img src="{img_rel}" alt="{html.escape(cap)}"{img_dim_attrs(img_rel)}/>'
                            f'<figcaption class="atlas-caption">{html.escape(cap)}</figcaption>'
                            f'</figure>'
                        )
                        break

            if inject_bestiary_plates and level == 3:
                for key, img_rel in BESTIARY_PLATES.items():
                    if plain_title.startswith(key):
                        out.append(
                            f'<figure class="atlas-plate creature-plate">'
                            f'<img src="{img_rel}" alt="{html.escape(plain_title)}"{img_dim_attrs(img_rel)}/>'
                            f'</figure>'
                        )
                        break
            i += 1
            continue

        m_img = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", stripped)
        if m_img:
            cap = m_img.group(1).strip()
            src_raw = m_img.group(2).strip().replace("\\", "/")
            if src_raw.startswith("ilustracoes/"):
                src_web = "assets/" + src_raw.split("/", 1)[1]
            else:
                src_web = rewrite_link(src_raw)
            cap_html = f'<figcaption class="atlas-caption">{inline_md(cap)}</figcaption>' if cap else ""
            out.append(
                f'<figure class="atlas-plate">'
                f'<img src="{html.escape(src_web, quote=True)}" alt="{html.escape(cap or "Ilustração de Alenia")}"{img_dim_attrs(src_web)}/>'
                f'{cap_html}'
                f'</figure>'
            )
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
            row_prefix = "" if id_prefix == "cul-" else id_prefix
            for r in rows:
                row_id_attr = ""
                if r:
                    m_bcode = re.match(r"^(B0[1-6])$", r[0].strip())
                    if m_bcode:
                        row_id_attr = f' id="{row_prefix}{m_bcode.group(1).lower()}"'
                t_html.append(f"<tr{row_id_attr}>")
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


def render_public_doc_with_sealed_sections(md_content: str, id_prefix: str, card_h3: bool, inject_maps: bool, codex_file: str = "", compendium_mode: bool = False):
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
                    codex_file=codex_file,
                    compendium_mode=compendium_mode,
                )
            )
        else:
            html_parts.append(rendered)
            public_toc.extend(chunk_toc)
    return "\n".join(html_parts), public_toc


def build_topbar(active_file: str, page_title: str, has_toc: bool) -> str:
    left_btns = [
        '<button id="btn-lib-toggle" class="btn-toc-toggle" type="button" title="Abrir/Fechar Menu de Livros">☰ Livros</button>'
    ]
    if has_toc:
        left_btns.append(
            '<button id="btn-toc-toggle" class="btn-toc-toggle" type="button" title="Abrir/Fechar Sumário do Volume">📑 Sumário</button>'
        )
    cur_badge = (
        f'<span class="topbar-current">{html.escape(page_title)}</span>'
        if active_file != "index.html"
        else ""
    )
    right_btns = []
    if active_file != "index.html":
        right_btns.append('<a href="index.html">Estante</a>')
    right_btns.append('<button id="btn-lock-gm" class="btn-lock" type="button" title="Trancar área do Mestre">🔒 Trancar</button>')
    right_btns.append('<button class="btn-print" type="button" onclick="window.print()">Imprimir / PDF</button>')
    return (
        '<header class="topbar">'
        f'<div class="topbar-left">{"".join(left_btns)}'
        '<a class="topbar-brand" href="index.html">✦ ALENIA RPG</a>'
        f'{cur_badge}</div>'
        f'<nav class="topbar-nav">{"".join(right_btns)}</nav>'
        '</header>'
    )


def build_sidebar(active_file: str, toc_items, has_toc: bool) -> str:
    romans = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII"]
    public_items = []
    gm_items = []
    for idx, b in enumerate(BOOKS):
        num = romans[idx] if idx < len(romans) else str(idx + 1)
        is_act = " active" if b["out"] == active_file else ""
        if b["gm_only"]:
            gm_items.append(
                f'<li><a class="lib-link gm-link{is_act}" href="{b["out"]}">'
                f'<span class="lib-num">{num}</span><span>🔒 {html.escape(b["title"])}</span></a></li>'
            )
        else:
            public_items.append(
                f'<li><a class="lib-link{is_act}" href="{b["out"]}">'
                f'<span class="lib-num">{num}</span><span>{html.escape(b["title"])}</span></a></li>'
            )

    home_act = " active" if active_file == "index.html" else ""
    comp_act = " active" if active_file == "Alenia_Compendio_Completo.html" else ""
    tok_act = " active" if active_file == "gerador_tokens.html" else ""
    lib_html = (
        '<div class="lib-group-label">Início</div>'
        '<ul class="lib-list">'
        f'<li><a class="lib-link{home_act}" href="index.html"><span class="lib-num">✦</span><span>Estante Oficial</span></a></li>'
        '</ul>'
        '<div class="lib-group-label">Tomos do Jogador</div>'
        f'<ul class="lib-list">{"".join(public_items)}</ul>'
        '<div class="lib-group-label">Área Restrita do Mestre</div>'
        f'<ul class="lib-list">{"".join(gm_items)}</ul>'
        '<div class="lib-group-label">Ferramentas &amp; VTT</div>'
        '<ul class="lib-list">'
        f'<li><a class="lib-link{tok_act}" href="gerador_tokens.html"><span class="lib-num">⚔</span><span>Gerador de Tokens</span></a></li>'
        '</ul>'
        '<div class="lib-group-label">Volume Único</div>'
        '<ul class="lib-list">'
        f'<li><a class="lib-link{comp_act}" href="Alenia_Compendio_Completo.html"><span class="lib-num">★</span><span>Compêndio Completo</span></a></li>'
        '</ul>'
    )

    if has_toc:
        li_html = render_toc_items(toc_items or [])
        return (
            '<aside class="sidebar" aria-label="Navegação da Biblioteca e Sumário">'
            '<div class="sidebar-tabs">'
            '<button class="sidebar-tab active" data-tab="lib" type="button">📚 Livros</button>'
            '<button class="sidebar-tab" data-tab="toc" type="button">📑 Sumário</button>'
            '</div>'
            f'<div id="sidebar-pane-lib" class="sidebar-pane active">{lib_html}</div>'
            f'<div id="sidebar-pane-toc" class="sidebar-pane">'
            '<div class="sidebar-title">Sumário do Volume</div>'
            f'<ul class="toc-list">{li_html}</ul>'
            '</div>'
            '</aside>'
            '<div id="sidebar-backdrop" class="sidebar-backdrop"></div>'
        )

    return (
        '<aside class="sidebar" aria-label="Navegação da Biblioteca">'
        '<div class="sidebar-title">Biblioteca Oficial</div>'
        f'<div id="sidebar-pane-lib" class="sidebar-pane active">{lib_html}</div>'
        '</aside>'
        '<div id="sidebar-backdrop" class="sidebar-backdrop"></div>'
    )


def build_cover(num: str, title: str, subtitle: str, epigraph: str, cover_map: str = None) -> str:
    img_html = f'<img class="cover-thumb" src="{cover_map}" alt="Ilustração de capa — {html.escape(title)}"/>' if cover_map else ""
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


CHRONICLE_CSS = r"""
/* =====================================================
   TOMO XI — MEDIEVAL PARCHMENT SCROLL TIMELINE
   ===================================================== */
body.chronicle-mode .book-shell {
    padding: 72px 18px 72px;
}
body.chronicle-mode:not(.sidebar-hidden) .sidebar-backdrop {
    display: block;
}
body.chronicle-mode .book-page {
    max-width: 1340px;
    padding: 34px 36px 56px;
    background: radial-gradient(circle at top center, #faf3e2 0%, #f3e7ce 55%, #ebdab7 100%);
    box-shadow:
        0 26px 75px rgba(0, 0, 0, 0.72),
        0 0 0 1px rgba(154, 123, 59, 0.48),
        inset 0 0 42px rgba(132, 92, 42, 0.14);
}
body.chronicle-mode .book-page::before {
    inset: 10px;
    border: 1px solid rgba(154, 123, 59, 0.36);
}

/* HERO / ILLUMINATED MANUSCRIPT TITLE HEADER */
.chronicle-hero {
    display: grid;
    grid-template-columns: 270px 1fr;
    gap: 28px;
    align-items: center;
    padding: 26px 28px;
    margin-bottom: 22px;
    border: 2px solid var(--crimson);
    outline: 1px solid var(--gold);
    outline-offset: -7px;
    background: radial-gradient(circle at 25% 50%, #fbf6ea 0%, #f1e3c4 100%);
    box-shadow: 0 10px 26px rgba(42, 26, 12, 0.14);
}
.chronicle-hero-cover {
    margin: 0 !important;
    padding: 8px !important;
    background: #efe3c6 !important;
    border: 1px solid var(--gold) !important;
}
.chronicle-hero-cover img {
    width: 100%;
    max-height: 290px;
    object-fit: cover;
    display: block;
    cursor: zoom-in;
}
.chronicle-hero-kicker {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 11px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--crimson);
    font-weight: 700;
}
.chronicle-hero-title {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 32px;
    line-height: 1.15;
    margin: 6px 0 8px;
    color: #24180e;
    border: none !important;
    padding: 0 !important;
}
.chronicle-hero-sub {
    font-style: italic;
    font-size: 16.5px;
    color: var(--ink-soft);
    margin: 0 0 12px;
}
.chronicle-hero-epigraph {
    font-style: italic;
    font-size: 15px;
    color: #3f3021;
    border-left: 3px solid var(--crimson);
    padding: 6px 14px;
    margin: 0 0 14px;
    background: rgba(154, 123, 59, 0.08);
}
.chronicle-hero-epigraph span {
    display: block;
    font-style: normal;
    font-size: 13px;
    color: var(--ink-soft);
    margin-top: 3px;
}
.chronicle-stats {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}
.chronicle-stat-pill {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10.5px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 5px 10px;
    border-radius: 2px;
    background: rgba(31, 81, 86, 0.1);
    border: 1px solid rgba(31, 81, 86, 0.35);
    color: #1a4347;
    font-weight: 600;
}
.chronicle-stat-pill.canon {
    background: rgba(122, 31, 29, 0.1);
    border-color: rgba(122, 31, 29, 0.38);
    color: var(--crimson-dark);
}

/* COLLAPSIBLE EDITORIAL GUIDE */
.chronicle-guide {
    margin: 0 0 22px;
    border: 1px solid rgba(154, 123, 59, 0.55);
    background: rgba(246, 236, 212, 0.72);
    border-radius: 3px;
}
.chronicle-guide > summary {
    cursor: pointer;
    padding: 11px 18px;
    font-family: 'Cinzel', Georgia, serif;
    font-size: 12.5px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--crimson-dark);
    font-weight: 700;
    list-style: none;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.chronicle-guide > summary::-webkit-details-marker { display: none; }
.chronicle-guide > summary::after {
    content: "▾ Expandir";
    font-size: 10.5px;
    color: var(--gold);
}
.chronicle-guide[open] > summary::after {
    content: "▴ Recolher";
}
.chronicle-guide-inner {
    padding: 4px 22px 18px;
    border-top: 1px solid rgba(154, 123, 59, 0.3);
}

/* INTERACTIVE FILTER TOOLBAR */
.chronicle-toolbar {
    position: relative;
    z-index: 20;
    background: linear-gradient(180deg, rgba(31, 24, 18, 0.97) 0%, rgba(22, 17, 13, 0.97) 100%);
    border: 1px solid rgba(154, 123, 59, 0.65);
    border-radius: 4px;
    padding: 12px 16px;
    margin: 0 0 28px;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.42);
    color: #efe6d2;
}
.chronicle-era-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 10px;
}
.era-pill {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10.5px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 5px 10px;
    border-radius: 3px;
    border: 1px solid rgba(154, 123, 59, 0.42);
    background: rgba(255, 255, 255, 0.04);
    color: #ded4c1;
    cursor: pointer;
    transition: all 0.15s ease;
}
.era-pill:hover {
    border-color: var(--gold-light);
    color: var(--gold-light);
    background: rgba(154, 123, 59, 0.16);
}
.era-pill.active {
    background: var(--crimson);
    border-color: var(--gold-light);
    color: #fff6e0;
    font-weight: 700;
}
.chronicle-controls-row {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
}
.chronicle-search {
    flex: 1 1 240px;
    min-width: 180px;
    padding: 6px 11px;
    border-radius: 3px;
    border: 1px solid rgba(154, 123, 59, 0.55);
    background: #14100c;
    color: #f7f1e3;
    font-family: 'EB Garamond', Georgia, serif;
    font-size: 15px;
}
.chronicle-search::placeholder { color: #9c8f7a; font-style: italic; }
.chronicle-toggle-btn {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 7px 11px;
    border-radius: 3px;
    border: 1px solid rgba(154, 123, 59, 0.48);
    background: rgba(154, 123, 59, 0.12);
    color: #e6dac4;
    cursor: pointer;
    transition: all 0.15s ease;
}
.chronicle-toggle-btn:hover { border-color: var(--gold-light); color: #fff; }
.chronicle-toggle-btn.active {
    background: #1f5156;
    border-color: #79b8be;
    color: #fff;
    font-weight: 700;
}
.chronicle-toggle-btn.canon-toggle.active {
    background: var(--crimson);
    border-color: var(--gold-light);
}
.chronicle-count {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10.5px;
    letter-spacing: 0.08em;
    color: var(--gold-light);
    margin-left: auto;
    white-space: nowrap;
}

/* ERA BANNER & RENAISSANCE HISTORICAL PLATE */
.chronicle-era {
    margin: 0 0 46px;
    scroll-margin-top: 68px;
}
.chronicle-era.is-hidden { display: none; }

.era-banner {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 14px;
    padding: 16px 22px;
    margin-bottom: 16px;
    background: linear-gradient(90deg, rgba(122, 31, 29, 0.1) 0%, rgba(154, 123, 59, 0.14) 50%, rgba(122, 31, 29, 0.06) 100%);
    border-top: 2px solid var(--crimson);
    border-bottom: 1px solid var(--gold);
    border-left: 4px solid var(--crimson);
}
.era-banner-kicker {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10.5px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--crimson);
    font-weight: 700;
}
.era-banner-title {
    font-family: 'Cinzel', Georgia, serif !important;
    font-size: 24px !important;
    color: #24180e !important;
    margin: 2px 0 3px !important;
    border: none !important;
    padding: 0 !important;
}
.era-banner-summary {
    font-style: italic;
    font-size: 15px;
    color: var(--ink-soft);
    margin: 0;
}
.era-banner-meta {
    text-align: right;
    flex-shrink: 0;
}
.era-period-badge {
    display: inline-block;
    font-family: 'Cinzel', Georgia, serif;
    font-size: 11.5px;
    font-weight: 700;
    letter-spacing: 0.06em;
    color: #f7f1e3;
    background: #2b1e14;
    border: 1px solid var(--gold);
    padding: 5px 12px;
    border-radius: 2px;
}
.era-count-sub {
    display: block;
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10px;
    letter-spacing: 0.08em;
    color: var(--ink-soft);
    margin-top: 4px;
}

.chronicle-plate {
    margin: 0 0 22px !important;
    padding: 12px 14px 10px !important;
    background: linear-gradient(180deg, #f3e6c8 0%, #ead6af 100%) !important;
    border: 1px solid var(--gold) !important;
    outline: 1px solid rgba(122, 31, 29, 0.25);
    outline-offset: -5px;
    box-shadow: 0 8px 22px rgba(42, 26, 12, 0.16);
}
.chronicle-plate img {
    width: 100%;
    max-height: 430px;
    object-fit: contain;
    display: block;
    margin: 0 auto;
    cursor: zoom-in;
    border-radius: 2px;
    mix-blend-mode: multiply;
}
.chronicle-plate figcaption {
    margin-top: 8px;
    font-style: italic;
    font-size: 14px;
    color: #4a3723;
    text-align: center;
}

/* =====================================================
   MEDIEVAL ROLLED PARCHMENT SCROLL STRIP (3–4 EVENTS)
   Inspired by classic rolled medieval manuscript scrolls
   ===================================================== */
.tl-scroll-wrap {
    position: relative;
    display: flex;
    align-items: stretch;
    margin: 0 0 10px;
    filter: drop-shadow(0 12px 22px rgba(32, 19, 8, 0.28));
}
.tl-scroll-wrap.is-hidden { display: none; }

/* Turned Wooden Scroll Rollers + Curled Parchment Edges */
.tl-roller {
    width: 34px;
    flex-shrink: 0;
    position: relative;
    z-index: 3;
    border-radius: 10px;
    background: linear-gradient(
        90deg,
        #9f713b 0%,
        #d8b170 18%,
        #f7e9c7 42%,
        #fdf6e3 54%,
        #d4ac6b 78%,
        #8a5e2d 100%
    );
    border: 1px solid #7d5225;
    box-shadow:
        inset 0 10px 16px rgba(96, 56, 18, 0.32),
        inset 0 -10px 16px rgba(96, 56, 18, 0.34),
        0 4px 12px rgba(20, 11, 4, 0.35);
}
.tl-roller::before,
.tl-roller::after {
    content: "";
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    width: 18px;
    height: 16px;
    background: linear-gradient(90deg, #2d160a 0%, #7a4622 35%, #a16538 52%, #592f15 80%, #241007 100%);
    border: 1px solid #2b1409;
    border-radius: 3px;
}
.tl-roller::before { top: -15px; border-bottom: none; border-radius: 4px 4px 1px 1px; }
.tl-roller::after { bottom: -15px; border-top: none; border-radius: 1px 1px 4px 4px; }
.tl-roller-left { margin-right: -8px; }
.tl-roller-right { margin-left: -8px; }

/* Central Aged Parchment Sheet */
.tl-strip {
    flex: 1 1 auto;
    min-width: 0;
    position: relative;
    padding: 24px 26px 26px;
    background:
        radial-gradient(ellipse at center, #fcf5e3 0%, #f5e7c6 62%, #e6cb99 100%);
    border-top: 2px solid #966a38;
    border-bottom: 2px solid #966a38;
    box-shadow:
        inset 20px 0 24px -12px rgba(98, 59, 20, 0.38),
        inset -20px 0 24px -12px rgba(98, 59, 20, 0.38),
        inset 0 14px 22px -12px rgba(138, 88, 34, 0.28),
        inset 0 -14px 22px -12px rgba(138, 88, 34, 0.32);
}
.tl-strip::before {
    content: "";
    position: absolute;
    inset: 6px 14px;
    border-top: 1px solid rgba(122, 82, 39, 0.32);
    border-bottom: 1px solid rgba(122, 82, 39, 0.32);
    pointer-events: none;
}

.tl-strip-label {
    position: absolute;
    top: 7px;
    right: 20px;
    font-family: 'Cinzel', Georgia, serif;
    font-size: 9.5px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: rgba(94, 62, 28, 0.72);
    pointer-events: none;
}

/* 3-ROW x N-COLUMN HORIZONTAL TIMELINE GRID */
.tl-grid {
    display: grid;
    grid-template-rows: auto 48px auto;
    column-gap: 14px;
    row-gap: 0;
    position: relative;
}
.tl-grid.tl-cols-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
.tl-grid.tl-cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }

.tl-slot { min-width: 0; position: relative; }
.tl-slot.is-hidden { display: none !important; }
.tl-slot-top {
    grid-row: 1;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    align-items: stretch;
    padding-bottom: 20px;
}
.tl-slot-axis {
    grid-row: 2;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
}
.tl-slot-bottom {
    grid-row: 3;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: stretch;
    padding-top: 20px;
}

/* Continuous Sepia Horizontal Axis + Arrows */
.tl-slot-axis::before {
    content: "";
    position: absolute;
    left: -8px;
    right: -8px;
    top: 50%;
    height: 2.5px;
    background: #473019;
    transform: translateY(-50%);
    z-index: 1;
}
.tl-axis-arrow {
    position: absolute;
    right: -13px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 13px;
    line-height: 1;
    color: #473019;
    z-index: 2;
    pointer-events: none;
}
.tl-slot-axis.is-last-vis .tl-axis-arrow {
    right: -4px;
}

/* Circular Timeline Node (Teal-Bronze like reference, Crimson-Gold for Canonical Landmarks) */
.tl-node {
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 35%, #2f7077 0%, #1d4e53 72%, #13363a 100%);
    border: 2.5px solid #f7ecd2;
    box-shadow: 0 0 0 2px #473019, 0 2px 6px rgba(24, 14, 5, 0.35);
    z-index: 3;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #f9eed2;
    font-size: 10px;
    font-weight: 700;
}
.tl-node.is-canon {
    width: 26px;
    height: 26px;
    background: radial-gradient(circle at 35% 35%, #a32c29 0%, #7a1f1d 70%, #4d110f 100%);
    border: 2.5px solid #e7ca82;
    box-shadow: 0 0 0 2px #473019, 0 0 10px rgba(122, 31, 29, 0.35);
}

/* Vertical Ink Stems Connecting Cards & Medallions to the Axis */
.tl-slot-top::after {
    content: "";
    position: absolute;
    left: 50%;
    bottom: -14px;
    width: 2px;
    height: 34px;
    background: #473019;
    transform: translateX(-50%);
    z-index: 1;
}
.tl-slot-bottom::before {
    content: "";
    position: absolute;
    left: 50%;
    top: -14px;
    width: 2px;
    height: 34px;
    background: #473019;
    transform: translateX(-50%);
    z-index: 1;
}
.tl-medallion-slot.tl-slot-top::after { height: 26px; }
.tl-medallion-slot.tl-slot-bottom::before { height: 26px; }

/* Opposite Date & Place Medallion (Balances Above/Below Axis Rhythm) */
.tl-medallion {
    margin: 0 auto;
    max-width: 94%;
    text-align: center;
    padding: 7px 11px;
    background: rgba(252, 245, 228, 0.78);
    border: 1px solid rgba(138, 102, 48, 0.52);
    border-radius: 3px;
    box-shadow: 0 2px 8px rgba(56, 36, 14, 0.1);
}
.tl-medallion.is-canon {
    border-color: rgba(122, 31, 29, 0.55);
    background: rgba(253, 244, 232, 0.92);
}
.tl-med-code {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10px;
    letter-spacing: 0.14em;
    font-weight: 700;
    color: #1f5156;
}
.tl-medallion.is-canon .tl-med-code { color: var(--crimson); }
.tl-med-date {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 12px;
    font-weight: 700;
    color: #2b1d10;
    line-height: 1.25;
    margin: 2px 0;
}
.tl-med-place {
    font-size: 12.5px;
    font-style: italic;
    color: #5c4833;
    line-height: 1.25;
}

/* EVENT CARD */
.tl-card {
    background: linear-gradient(180deg, rgba(255, 250, 238, 0.94) 0%, rgba(247, 237, 214, 0.94) 100%);
    border: 1px solid rgba(132, 98, 48, 0.58);
    border-top: 3px solid #1f5156;
    border-radius: 3px;
    padding: 11px 13px 10px;
    box-shadow: 0 4px 14px rgba(48, 29, 10, 0.12);
    position: relative;
    z-index: 2;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.tl-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(48, 29, 10, 0.2);
}
.tl-card.is-canon {
    border-top-color: var(--crimson);
    border-color: rgba(122, 31, 29, 0.45);
    background: linear-gradient(180deg, rgba(255, 250, 240, 0.98) 0%, rgba(248, 234, 212, 0.96) 100%);
}
.tl-card-head {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 5px;
    margin-bottom: 5px;
}
.tl-code-badge {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 9.5px;
    font-weight: 700;
    letter-spacing: 0.1em;
    padding: 2px 6px;
    border-radius: 2px;
    background: #1f5156;
    color: #f7f1e3;
}
.tl-card.is-canon .tl-code-badge { background: var(--crimson); }
.tl-date-tag {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10.5px;
    font-weight: 700;
    color: #45301a;
}
.tl-canon-pill {
    margin-left: auto;
    font-family: 'Cinzel', Georgia, serif;
    font-size: 8.8px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 2px 6px;
    border-radius: 2px;
    background: rgba(122, 31, 29, 0.12);
    border: 1px solid rgba(122, 31, 29, 0.4);
    color: var(--crimson-dark);
    font-weight: 700;
}
.tl-card-title {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 13.5px;
    font-weight: 700;
    line-height: 1.28;
    color: #21160d;
    margin: 0 0 4px;
}
.tl-card-meta {
    font-size: 12.2px;
    font-style: italic;
    color: #6b543b;
    line-height: 1.3;
    margin: 0 0 7px;
    padding-bottom: 5px;
    border-bottom: 1px dotted rgba(138, 102, 48, 0.4);
}
.tl-card-body {
    font-size: 14px;
    line-height: 1.44;
    color: #261e16;
    margin: 0;
    text-align: left;
}
.tl-card-body p {
    margin: 0 0 6px;
    text-align: left;
}
.tl-card-body p:last-child { margin-bottom: 0; }

/* EXPANDABLE "HERANÇA EM 418" DRAWER */
.tl-legacy {
    margin-top: 8px;
    padding-top: 6px;
    border-top: 1px solid rgba(154, 123, 59, 0.34);
}
.tl-legacy > summary {
    cursor: pointer;
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--crimson-dark);
    font-weight: 700;
    list-style: none;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.tl-legacy > summary::-webkit-details-marker { display: none; }
.tl-legacy > summary::after {
    content: "+";
    font-size: 13px;
    line-height: 1;
    color: var(--gold);
}
.tl-legacy[open] > summary::after { content: "−"; }
.tl-legacy-body {
    margin-top: 6px;
    font-size: 13.4px;
    line-height: 1.42;
    color: #3a2d20;
    background: rgba(154, 123, 59, 0.09);
    padding: 7px 9px;
    border-left: 2px solid var(--gold);
    border-radius: 0 2px 2px 0;
}

/* SUCCESSIVE ROW CONTINUATION CONNECTOR */
.tl-flow-next {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    margin: 2px 0 18px;
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #6b4c28;
}
.tl-flow-next.is-hidden { display: none; }
.tl-flow-next::before,
.tl-flow-next::after {
    content: "";
    flex: 1 1 80px;
    max-width: 240px;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(122, 82, 39, 0.55), transparent);
}

/* EMPTY FILTER STATE */
.chronicle-empty {
    display: none;
    text-align: center;
    padding: 36px 20px;
    border: 1px dashed var(--gold);
    background: rgba(246, 236, 212, 0.7);
    font-style: italic;
    color: var(--ink-soft);
    margin: 20px 0 36px;
}
.chronicle-empty.visible { display: block; }

/* COMPLEMENTARY SECTIONS (IX–XII & GM VAULT) */
.chronicle-appendix {
    margin-top: 44px;
    padding-top: 24px;
    border-top: 2px solid var(--crimson);
}
.chronicle-appendix h2 {
    scroll-margin-top: 130px;
}

/* RESPONSIVE: TABLET & MOBILE VERTICAL PARCHMENT TIMELINE */
@media (max-width: 1060px) {
    body.chronicle-mode .book-page { padding: 24px 18px 46px; }
    .chronicle-hero { grid-template-columns: 1fr; text-align: center; padding: 20px; }
    .chronicle-hero-cover { max-width: 260px; margin: 0 auto !important; }
    .chronicle-stats { justify-content: center; }
    .tl-roller { display: none; }
    .tl-strip {
        padding: 20px 16px 20px 20px;
        border: 1px solid #966a38;
        border-radius: 4px;
    }
    .tl-strip::before { inset: 5px; }
    .tl-grid,
    .tl-grid.tl-cols-3,
    .tl-grid.tl-cols-4 {
        display: flex !important;
        flex-direction: column;
        gap: 14px;
        padding-left: 26px;
        border-left: 2.5px solid #473019;
    }
    .tl-slot-axis,
    .tl-medallion-slot { display: none !important; }
    .tl-card-slot {
        padding: 0 !important;
        grid-column: auto !important;
        grid-row: auto !important;
    }
    .tl-card-slot::before,
    .tl-card-slot::after { display: none !important; }
    .tl-card::before {
        content: "";
        position: absolute;
        left: -36px;
        top: 14px;
        width: 16px;
        height: 16px;
        border-radius: 50%;
        background: #1f5156;
        border: 2px solid #f7ecd2;
        box-shadow: 0 0 0 2px #473019;
    }
    .tl-card.is-canon::before {
        background: var(--crimson);
        border-color: #e7ca82;
    }
    .tl-card::after {
        content: "";
        position: absolute;
        left: -20px;
        top: 21px;
        width: 19px;
        height: 2px;
        background: #473019;
    }
}

@media print {
    .chronicle-toolbar { display: none !important; }
    .tl-roller { display: none !important; }
    .tl-scroll-wrap { filter: none !important; break-inside: avoid; page-break-inside: avoid; }
    .tl-legacy { display: block; }
}
"""

CHRONICLE_JS = r"""
(function() {
    const timelineRoot = document.getElementById('chronicle-timeline');
    if (!timelineRoot) return;

    const eraPills = Array.from(document.querySelectorAll('.era-pill'));
    const searchInput = document.getElementById('chronicle-search');
    const btnCanon = document.getElementById('btn-toggle-canon');
    const btnLegacy = document.getElementById('btn-toggle-legacy');
    const countEl = document.getElementById('chronicle-count');
    const emptyEl = document.getElementById('chronicle-empty');

    let selectedEra = 'ALL';
    let canonOnly = false;
    let legacyOpen = false;

    function applyFilters() {
        const q = (searchInput ? searchInput.value : '').trim().toLowerCase();
        let visibleEvents = 0;

        document.querySelectorAll('.chronicle-era').forEach(eraEl => {
            const eraId = eraEl.dataset.era;
            const eraAllowed = (selectedEra === 'ALL' || selectedEra === eraId);
            if (!eraAllowed) {
                eraEl.classList.add('is-hidden');
                return;
            }

            let eraVisibleCount = 0;
            const wraps = Array.from(eraEl.querySelectorAll('.tl-scroll-wrap'));
            const connectors = Array.from(eraEl.querySelectorAll('.tl-flow-next'));

            wraps.forEach((wrap, wIdx) => {
                const grid = wrap.querySelector('.tl-grid');
                if (!grid) return;
                const codes = (grid.dataset.codes || '').split(',').filter(Boolean);
                const visibleCodes = [];

                codes.forEach(code => {
                    const cardSlot = grid.querySelector(`.tl-card-slot[data-ev="${code}"]`);
                    if (!cardSlot) return;
                    const isCanon = cardSlot.dataset.canon === '1';
                    const hay = (cardSlot.dataset.search || '').toLowerCase();
                    const matchCanon = !canonOnly || isCanon;
                    const matchQuery = !q || hay.includes(q);
                    const show = matchCanon && matchQuery;

                    grid.querySelectorAll(`.tl-slot[data-ev="${code}"]`).forEach(sl => {
                        sl.classList.toggle('is-hidden', !show);
                    });
                    if (show) visibleCodes.push(code);
                });

                if (visibleCodes.length === 0) {
                    wrap.classList.add('is-hidden');
                } else {
                    wrap.classList.remove('is-hidden');
                    eraVisibleCount += visibleCodes.length;
                    grid.style.gridTemplateColumns = `repeat(${visibleCodes.length}, minmax(0, 1fr))`;
                    visibleCodes.forEach((code, colIdx) => {
                        grid.querySelectorAll(`.tl-slot[data-ev="${code}"]`).forEach(sl => {
                            sl.style.gridColumn = String(colIdx + 1);
                            if (sl.classList.contains('tl-slot-axis')) {
                                sl.classList.toggle('is-last-vis', colIdx === visibleCodes.length - 1);
                            }
                        });
                    });
                }

                if (connectors[wIdx]) {
                    connectors[wIdx].classList.toggle('is-hidden', visibleCodes.length === 0);
                }
            });

            // Hide trailing connector after the last visible strip in an era
            let lastVisIdx = -1;
            wraps.forEach((w, idx) => { if (!w.classList.contains('is-hidden')) lastVisIdx = idx; });
            connectors.forEach((c, idx) => {
                if (idx >= lastVisIdx) c.classList.add('is-hidden');
            });

            eraEl.classList.toggle('is-hidden', eraVisibleCount === 0);
            visibleEvents += eraVisibleCount;
        });

        if (countEl) {
            countEl.textContent = `Exibindo ${visibleEvents} de 100 acontecimentos`;
        }
        if (emptyEl) {
            emptyEl.classList.toggle('visible', visibleEvents === 0);
        }
    }

    eraPills.forEach(pill => {
        pill.addEventListener('click', () => {
            selectedEra = pill.dataset.era;
            eraPills.forEach(p => p.classList.toggle('active', p === pill));
            applyFilters();
            if (selectedEra !== 'ALL') {
                const target = document.querySelector(`.chronicle-era[data-era="${selectedEra}"]`);
                if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    if (btnCanon) {
        btnCanon.addEventListener('click', () => {
            canonOnly = !canonOnly;
            btnCanon.classList.toggle('active', canonOnly);
            applyFilters();
        });
    }

    if (btnLegacy) {
        btnLegacy.addEventListener('click', () => {
            legacyOpen = !legacyOpen;
            btnLegacy.classList.toggle('active', legacyOpen);
            btnLegacy.textContent = legacyOpen ? '📜 Recolher Heranças em 418' : '📜 Expandir Heranças em 418';
            document.querySelectorAll('.tl-legacy').forEach(d => { d.open = legacyOpen; });
        });
    }

    if (searchInput) {
        searchInput.addEventListener('input', applyFilters);
    }

    // Close sidebar drawer when clicking TOC links on Chronicle page
    document.querySelectorAll('.toc-list a').forEach(a => {
        a.addEventListener('click', () => {
            document.body.classList.add('sidebar-hidden');
            document.body.classList.remove('sidebar-open-mobile');
        });
    });
})();
"""


def partition_rows_3_4(items):
    """Partition any list into balanced horizontal rows of strictly 3 or 4 items (never 1 or 2)."""
    n = len(items)
    if n <= 4:
        return [items] if items else []
    rem = n % 4
    if rem == 0:
        sizes = [4] * (n // 4)
    elif rem == 3:
        sizes = [4] * (n // 4) + [3]
    elif rem == 2:
        sizes = [4] * (n // 4 - 1) + [3, 3]
    else:  # rem == 1 (n >= 5; for n==5 -> [3,2], for n>=9 -> 4s + [3,3,3])
        if n == 5:
            sizes = [3, 2]
        else:
            sizes = [4] * (n // 4 - 2) + [3, 3, 3]
    rows = []
    pos = 0
    for sz in sizes:
        rows.append(items[pos:pos + sz])
        pos += sz
    return rows


def render_chronicle_timeline_page(bk: dict, md_content: str):
    """Build custom Medieval Parchment Scroll Timeline page for Tomo XI."""
    era_periods = {
        "I": ("Tempos geológicos até cerca de 1800 AF", "Montanhas, bacias, costas, geleiras e solos moldam possibilidades de vida."),
        "II": ("Cerca de 900–1 AF", "Comunidades, migrações, embarcações e mercados antecedem o calendário real."),
        "III": ("1–112 EF", "Altavanne organiza poder, trabalho, rotas e campanhas contra as matas."),
        "IV": ("113–219 EF", "Autonomias negociadas, navegação e instituições de saber."),
        "V": ("220–347 EF", "Crédito, epidemias, guerras kalitas, arquivos e expedições perdidas."),
        "VI": ("348–356 EF", "A Sombra devasta Aurora e destrói a legitimidade do ramo reinante."),
        "VII": ("357–404 EF", "Reconstrução, promessas, água e novas dependências econômicas."),
        "VIII": ("405–418 EF", "O passado converge em crises que os personagens ainda podem mudar."),
    }
    era_romans = ("I", "II", "III", "IV", "V", "VI", "VII", "VIII")

    # Split Markdown by top-level H2 sections
    parts = re.split(r"(?=^##\s+)", md_content, flags=re.M)
    intro_guide_md = ""
    era_sections = []
    appendix_chunks = []

    for part in parts:
        m_h2 = re.match(r"^##\s+(.+)$", part.strip(), flags=re.M)
        if not m_h2:
            continue
        h2_title = m_h2.group(1).strip()
        if h2_title.startswith("Como ler esta história"):
            intro_guide_md = part
        else:
            m_era = re.match(r"^(I|II|III|IV|V|VI|VII|VIII)\s+[—–-]\s+(.+)$", h2_title)
            if m_era:
                era_sections.append((m_era.group(1), m_era.group(2).strip(), part))
            else:
                appendix_chunks.append(part)

    # Parse all 8 Eras and their 100 events
    parsed_eras = []
    total_events = 0
    total_canon = 0

    for roman, era_name, raw_sec in era_sections:
        # Extract era illustration image if present
        m_img = re.search(r"!\[([^\]]*)\]\(([^)]+)\)", raw_sec)
        plate_alt = m_img.group(1).strip() if m_img else ""
        plate_src = ("assets/" + os.path.basename(m_img.group(2).strip())) if m_img else ""

        ev_blocks = re.split(r"(?=^###\s+T\d{3}\s)", raw_sec, flags=re.M)
        events = []
        for blk in ev_blocks[1:]:
            lines = blk.strip().splitlines()
            if not lines:
                continue
            m_eh = re.match(r"^###\s+(T\d{3})\s+[—–-]\s+([^:]+):\s*(.+)$", lines[0].strip())
            if not m_eh:
                continue
            code = m_eh.group(1).strip()
            date_str = m_eh.group(2).strip()
            title_str = m_eh.group(3).strip()

            body_lines = [ln.strip() for ln in lines[1:] if ln.strip()]
            meta_raw = ""
            if body_lines and body_lines[0].startswith("**") and body_lines[0].endswith("**"):
                meta_raw = body_lines.pop(0).strip("*").strip()

            # Split meta_raw into Category · Place · Status
            meta_parts = [p.strip().rstrip(".") for p in meta_raw.split("·")]
            cat_str = meta_parts[0] if len(meta_parts) >= 1 else ""
            place_str = meta_parts[1] if len(meta_parts) >= 2 else ""
            status_str = meta_parts[2] if len(meta_parts) >= 3 else ""
            is_canon = ("marco estabelecido" in meta_raw.lower()) or ("marcos estabelecidos" in meta_raw.lower())

            desc_paras = []
            legacy_label = "Herança em 418"
            legacy_text = ""
            for bl in body_lines:
                m_leg = re.match(r"^\*\*(Herança[^*:]+):\*\*\s*(.+)$", bl)
                if m_leg:
                    legacy_label = m_leg.group(1).strip()
                    legacy_text = m_leg.group(2).strip()
                else:
                    desc_paras.append(bl)

            total_events += 1
            if is_canon:
                total_canon += 1

            events.append({
                "code": code,
                "date": date_str,
                "title": title_str,
                "meta_raw": meta_raw,
                "category": cat_str,
                "place": place_str,
                "status": status_str,
                "is_canon": is_canon,
                "desc_paras": desc_paras,
                "legacy_label": legacy_label,
                "legacy_text": legacy_text,
            })

        parsed_eras.append({
            "roman": roman,
            "name": era_name,
            "id": f"epoca-{roman.lower()}",
            "period": era_periods.get(roman, ("", ""))[0],
            "summary": era_periods.get(roman, ("", ""))[1],
            "plate_src": plate_src,
            "plate_alt": plate_alt,
            "events": events,
        })

    # Build Sidebar TOC
    toc_items = []
    for era in parsed_eras:
        toc_items.append((2, f"{era['roman']} — {era['name']}", era["id"]))

    # Render collapsible Editorial Guide ("Como ler esta história")
    guide_html = ""
    if intro_guide_md:
        guide_inner, _ = md_to_html(intro_guide_md, id_prefix="guia-", card_h3=False, inject_maps=False)
        guide_html = f"""
        <details class="chronicle-guide">
            <summary>📜 Como Ler Esta Crônica — Calendário (AF / EF), Fontes &amp; Tabela das Oito Épocas</summary>
            <div class="chronicle-guide-inner">{guide_inner}</div>
        </details>
        """

    # Build Era Filter Pills
    era_pills = ['<button class="era-pill active" data-era="ALL" type="button">Todas (100)</button>']
    for era in parsed_eras:
        era_pills.append(
            f'<button class="era-pill" data-era="{era["roman"]}" type="button" '
            f'title="{html.escape(era["name"])} ({html.escape(era["period"])})">'
            f'{era["roman"]} · {html.escape(era["name"].split()[0] if len(era["name"]) > 22 else era["name"])} ({len(era["events"])})</button>'
        )
    # Better crisp pill labels
    era_short_labels = {
        "I": "I · Terras Antigas",
        "II": "II · Antes da Coroa",
        "III": "III · A Forja",
        "IV": "IV · Pactos & Portos",
        "V": "V · Livros Fechados",
        "VI": "VI · O Eclipse",
        "VII": "VII · Faixa Negra",
        "VIII": "VIII · Ano 418",
    }
    era_pills = ['<button class="era-pill active" data-era="ALL" type="button">Todas (100)</button>']
    for era in parsed_eras:
        lbl = era_short_labels.get(era["roman"], era["roman"])
        era_pills.append(
            f'<button class="era-pill" data-era="{era["roman"]}" type="button" '
            f'title="{html.escape(era["name"])} — {html.escape(era["period"])}">'
            f'{html.escape(lbl)}</button>'
        )

    # Render Hero Banner
    hero_html = f"""
    <section class="chronicle-hero">
        <figure class="atlas-plate chronicle-hero-cover">
            <img src="{bk['cover_map']}" alt="Capa — {html.escape(bk['title'])}"{img_dim_attrs(bk['cover_map'])}/>
        </figure>
        <div>
            <div class="chronicle-hero-kicker">ALENIA RPG • {html.escape(bk['num'])} • LINHA DO TEMPO ILUSTRADA</div>
            <h1 class="chronicle-hero-title">{html.escape(bk['title'])}</h1>
            <p class="chronicle-hero-sub">Uma história de Alenia: das montanhas anteriores à memória aos conflitos do Ano 418 da Era da Forja.</p>
            <blockquote class="chronicle-hero-epigraph">
                “O rei mandou escrever que fundara a cidade. Debaixo da praça onde ergueram sua estátua encontramos três ruas, dois cemitérios e a soleira de uma casa. Nenhum deles sabia o nome do rei.”
                <span>— Nota atribuída à cartógrafa Benetta de Litore.</span>
            </blockquote>
            <div class="chronicle-stats">
                <span class="chronicle-stat-pill">✦ {total_events} Acontecimentos (T001–T100)</span>
                <span class="chronicle-stat-pill">✦ 8 Épocas em Pergaminho</span>
                <span class="chronicle-stat-pill">✦ 8 Pranchas Renascentistas</span>
                <span class="chronicle-stat-pill canon">★ {total_canon} Marcos Canônicos</span>
            </div>
        </div>
    </section>
    {guide_html}
    <div class="chronicle-toolbar" role="region" aria-label="Filtros da Linha do Tempo">
        <div class="chronicle-era-pills">{"".join(era_pills)}</div>
        <div class="chronicle-controls-row">
            <input id="chronicle-search" class="chronicle-search" type="search" placeholder="Buscar acontecimento, ano, cidade, casa ou personagem..." aria-label="Buscar na linha do tempo"/>
            <button id="btn-toggle-canon" class="chronicle-toggle-btn canon-toggle" type="button">★ Apenas Marcos Canônicos ({total_canon})</button>
            <button id="btn-toggle-legacy" class="chronicle-toggle-btn" type="button">📜 Expandir Heranças em 418</button>
            <span id="chronicle-count" class="chronicle-count">Exibindo {total_events} de {total_events} acontecimentos</span>
        </div>
    </div>
    <div id="chronicle-empty" class="chronicle-empty">Nenhum acontecimento corresponde aos filtros atuais. Limpe a busca ou selecione “Todas”.</div>
    """

    # Render All 8 Eras with Successive 3–4 Event Medieval Scroll Strips
    era_blocks_html = []
    for era in parsed_eras:
        rows = partition_rows_3_4(era["events"])
        plate_html = ""
        if era["plate_src"]:
            plate_html = (
                f'<figure class="atlas-plate chronicle-plate">'
                f'<img src="{html.escape(era["plate_src"], quote=True)}" alt="{html.escape(era["plate_alt"])}"{img_dim_attrs(era["plate_src"])} loading="lazy"/>'
                f'<figcaption>{html.escape(era["plate_alt"])}</figcaption>'
                f'</figure>'
            )

        strips_html = []
        for r_idx, row in enumerate(rows):
            n_cols = len(row)
            codes_csv = ",".join(ev["code"] for ev in row)
            row_range = f"{row[0]['code']} → {row[-1]['code']}"
            slots_html = []

            for c_idx, ev in enumerate(row):
                col_num = c_idx + 1
                is_top_card = (c_idx % 2 == 0)  # Odd cols (1,3) above axis; Even cols (2,4) below axis
                canon_cls = " is-canon" if ev["is_canon"] else ""
                canon_flag = "1" if ev["is_canon"] else "0"
                search_blob = html.escape(
                    f"{ev['code']} {ev['date']} {ev['title']} {ev['meta_raw']} "
                    f"{' '.join(ev['desc_paras'])} {ev['legacy_text']} {era['name']}",
                    quote=True,
                )

                desc_html = "".join(f"<p>{inline_md(p)}</p>" for p in ev["desc_paras"])
                legacy_html = ""
                if ev["legacy_text"]:
                    legacy_html = (
                        f'<details class="tl-legacy">'
                        f'<summary>✦ {html.escape(ev["legacy_label"])}</summary>'
                        f'<div class="tl-legacy-body">{inline_md(ev["legacy_text"])}</div>'
                        f'</details>'
                    )

                canon_badge = '<span class="tl-canon-pill">★ Marco</span>' if ev["is_canon"] else ""
                card_html = (
                    f'<article class="tl-card{canon_cls}" id="{ev["code"].lower()}">'
                    f'<div class="tl-card-head">'
                    f'<span class="tl-code-badge">{html.escape(ev["code"])}</span>'
                    f'<span class="tl-date-tag">{html.escape(ev["date"])}</span>'
                    f'{canon_badge}'
                    f'</div>'
                    f'<h3 class="tl-card-title">{inline_md(ev["title"])}</h3>'
                    f'<div class="tl-card-meta">{html.escape(ev["category"])}'
                    f'{(" · " + html.escape(ev["place"])) if ev["place"] else ""}</div>'
                    f'<div class="tl-card-body">{desc_html}</div>'
                    f'{legacy_html}'
                    f'</article>'
                )

                medallion_html = (
                    f'<div class="tl-medallion{canon_cls}">'
                    f'<div class="tl-med-code">{html.escape(ev["code"])}{" · ★ MARCO" if ev["is_canon"] else ""}</div>'
                    f'<div class="tl-med-date">{html.escape(ev["date"])}</div>'
                    f'<div class="tl-med-place">{html.escape(ev["place"] or ev["category"])}</div>'
                    f'</div>'
                )

                node_sym = "★" if ev["is_canon"] else ""
                last_cls = " is-last-vis" if c_idx == n_cols - 1 else ""
                axis_html = (
                    f'<div class="tl-slot tl-slot-axis{last_cls}" data-ev="{ev["code"]}" style="grid-column:{col_num}">'
                    f'<span class="tl-node{canon_cls}" title="{html.escape(ev["code"] + " — " + ev["date"])}">{node_sym}</span>'
                    f'<span class="tl-axis-arrow" aria-hidden="true">▸</span>'
                    f'</div>'
                )

                if is_top_card:
                    top_slot = (
                        f'<div class="tl-slot tl-slot-top tl-card-slot" data-ev="{ev["code"]}" '
                        f'data-canon="{canon_flag}" data-search="{search_blob}" style="grid-column:{col_num}">'
                        f'{card_html}</div>'
                    )
                    bot_slot = (
                        f'<div class="tl-slot tl-slot-bottom tl-medallion-slot" data-ev="{ev["code"]}" '
                        f'style="grid-column:{col_num}">{medallion_html}</div>'
                    )
                else:
                    top_slot = (
                        f'<div class="tl-slot tl-slot-top tl-medallion-slot" data-ev="{ev["code"]}" '
                        f'style="grid-column:{col_num}">{medallion_html}</div>'
                    )
                    bot_slot = (
                        f'<div class="tl-slot tl-slot-bottom tl-card-slot" data-ev="{ev["code"]}" '
                        f'data-canon="{canon_flag}" data-search="{search_blob}" style="grid-column:{col_num}">'
                        f'{card_html}</div>'
                    )

                slots_html.append(top_slot + axis_html + bot_slot)

            strips_html.append(f"""
            <div class="tl-scroll-wrap" data-row="{r_idx + 1}">
                <div class="tl-roller tl-roller-left" aria-hidden="true"></div>
                <div class="tl-strip">
                    <div class="tl-strip-label">Faixa {r_idx + 1}/{len(rows)} · {html.escape(row_range)}</div>
                    <div class="tl-grid tl-cols-{n_cols}" data-codes="{codes_csv}">
                        {"".join(slots_html)}
                    </div>
                </div>
                <div class="tl-roller tl-roller-right" aria-hidden="true"></div>
            </div>
            """)

            if r_idx < len(rows) - 1:
                nxt_row = rows[r_idx + 1]
                strips_html.append(
                    f'<div class="tl-flow-next">⤵ Segue na faixa abaixo ({nxt_row[0]["code"]} → {nxt_row[-1]["code"]})</div>'
                )

        era_blocks_html.append(f"""
        <section class="chronicle-era" id="{era['id']}" data-era="{era['roman']}">
            <header class="era-banner">
                <div>
                    <div class="era-banner-kicker">ÉPOCA {era['roman']} DE VIII</div>
                    <h2 class="era-banner-title">{html.escape(era['name'])}</h2>
                    <p class="era-banner-summary">{html.escape(era['summary'])}</p>
                </div>
                <div class="era-banner-meta">
                    <span class="era-period-badge">{html.escape(era['period'])}</span>
                    <span class="era-count-sub">{len(era['events'])} acontecimentos · {len(rows)} faixas de pergaminho</span>
                </div>
            </header>
            {plate_html}
            {"".join(strips_html)}
        </section>
        """)

    # Render Complementary Sections (IX, X, XI, AES-256-GCM Caderno Reservado ao Mestre, XII, Fontes)
    appendix_md = "\n\n".join(appendix_chunks)
    appendix_html, appendix_toc = render_public_doc_with_sealed_sections(
        appendix_md, id_prefix="ap-", card_h3=False, inject_maps=False
    )
    toc_items.extend(appendix_toc)

    full_body = (
        hero_html
        + f'<div id="chronicle-timeline">{"".join(era_blocks_html)}</div>'
        + f'<section class="chronicle-appendix">{appendix_html}</section>'
    )
    return full_body, toc_items


def wrap_html_doc(page_title: str, active_file: str, body_html: str, toc_items=None, force_sidebar: bool = False, enable_book_reader: bool = True, extra_css: str = "", extra_js: str = "", body_extra_class: str = "") -> str:
    has_toc = force_sidebar or (toc_items is not None and len(toc_items) > 0)
    sidebar_html = build_sidebar(active_file, toc_items, has_toc)
    shell_cls = "book-shell"

    reader_ui = ""
    classes = []
    if enable_book_reader:
        classes.extend(["book-mode", "sidebar-hidden"])
        reader_ui = """
    <section id="reader-stage" class="reader-stage" aria-label="Leitor em Formato de Livro">
        <button class="side-turn-btn side-turn-prev btn-prev-page" type="button" title="Página Anterior (←)">‹</button>
        <div class="hardcover-wrap">
            <div id="book-spread" class="book-spread"></div>
        </div>
        <button class="side-turn-btn side-turn-next btn-next-page" type="button" title="Próxima Página (→)">›</button>
    </section>
    <footer class="reader-footer-bar">
        <div class="view-mode-group" title="Modo de visualização">
            <button class="mode-btn active" data-mode="spread" type="button">📖 2 Páginas</button>
            <button class="mode-btn" data-mode="single" type="button">📄 1 Página</button>
            <button class="mode-btn" data-mode="scroll" type="button">📜 Contínuo</button>
        </div>
        <div class="pager-controls">
            <button class="pager-btn btn-prev-page" type="button">‹ Anterior</button>
            <span id="pager-status" class="pager-status">Carregando...</span>
            <input id="pager-jump" class="pager-jump" type="number" min="1" value="1" title="Ir para página" aria-label="Número da página"/>
            <button class="pager-btn btn-next-page" type="button">Próxima ›</button>
        </div>
        <div class="font-scale-group" title="Tamanho da letra do livro">
            <button id="btn-font-down" class="mode-btn" type="button" title="Diminuir fonte">A−</button>
            <span id="font-scale-label" class="font-scale-label">100%</span>
            <button id="btn-font-up" class="mode-btn" type="button" title="Aumentar fonte">A+</button>
        </div>
    </footer>
        """
    if body_extra_class:
        classes.extend(body_extra_class.split())
    body_cls = f' class="{" ".join(classes)}"' if classes else ""
    extra_style_tag = f"\n    <style>{extra_css}</style>" if extra_css else ""
    extra_script_tag = f"\n    <script>{extra_js}</script>" if extra_js else ""
    body_html = link_codex_html(
        body_html,
        active_file,
        get_codex_registry(),
        compendium_mode=(active_file == "Alenia_Compendio_Completo.html"),
    )

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>{html.escape(page_title)} — Alenia RPG</title>
    <style>{SHARED_CSS}{CODEX_CSS}</style>{extra_style_tag}
</head>
<body{body_cls} data-book-title="{html.escape(page_title)}">
    {build_topbar(active_file, page_title, has_toc)}
    {sidebar_html}
    {reader_ui}
    <main class="{shell_cls}">
        <article class="book-page">
            {body_html}
        </article>
    </main>
    <div id="atlas-lightbox" class="lightbox" title="Clique ou pressione ESC para fechar">
        <img id="atlas-lightbox-img" src="" alt="Ampliação do Mapa"/>
    </div>
    <script>{SHARED_JS}</script>{extra_script_tag}
</body>
</html>
"""


def main():
    sync_assets()
    if not GM_PASSWORD:
        print("[WARN] ALENIA_GM_PASSWORD nao definida — gerando sem criptografia!")
    else:
        print("[OK] Criptografia AES-256-GCM (PBKDF2 120k) + Modo Livro Real ativos.")

    compendium_parts = [
        build_cover(
            "COMPÊNDIO INTEGRAL",
            "ALENIA RPG",
            "Regras, Cenário & Atlas, 36 Kits, Empório, Herbário, Crônica, Cozinhas & Volumes Selados do Mestre",
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
        inject_bestiary = bk["out"] == "04_Bestiario_de_Alenia.html"
        cover_html = build_cover(bk["num"], bk["title"], bk["subtitle"], bk["epigraph"], bk["cover_map"])

        if bk["gm_only"] and GM_PASSWORD:
            if bk["out"] == "13_Grandes_Nomes_e_Feitos_de_Alenia.html":
                secret_html, secret_toc = render_grandes_nomes_secret_payload(
                    bk,
                    md_content,
                    {
                        "inline_md": inline_md,
                        "md_to_html": md_to_html,
                        "img_dim_attrs": img_dim_attrs,
                        "rewrite_link": rewrite_link,
                    },
                )
                gated = make_gm_gate_block(
                    bk["title"],
                    "Edição secreta do Mestre: 100 perfis biográficos (N001–N100), genealogias, 12 encontros cruzados e segredos da aventura, do Acervo e da Comunhão. Digite a senha para destrancar.",
                    secret_html,
                    render_toc_items(secret_toc),
                    codex_file=bk["out"],
                    compendium_mode=False,
                )
                locked_cover = f'<div class="names-locked-cover">{cover_html}</div>'
                full_doc = wrap_html_doc(
                    bk["title"],
                    bk["out"],
                    locked_cover + "\n" + gated,
                    toc_items=[],
                    force_sidebar=True,
                    enable_book_reader=False,
                    extra_css=GRANDES_NOMES_CSS,
                    extra_js=GRANDES_NOMES_JS,
                    body_extra_class="names-mode sidebar-hidden",
                )
                with open(os.path.join(OUT_DIR, bk["out"]), "w", encoding="utf-8") as f:
                    f.write(full_doc)
                print(f"[OK] {bk['out']:34s} (PAINEL BIOGRAFICO + AES-256-GCM)")
            else:
                secret_html, secret_toc = md_to_html(md_content, id_prefix="", card_h3=card_h3, inject_maps=inject_maps, inject_bestiary_plates=inject_bestiary)
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
                    codex_file=bk["out"],
                    compendium_mode=False,
                )
                full_doc = wrap_html_doc(bk["title"], bk["out"], cover_html + "\n" + gated, toc_items=[], force_sidebar=True, enable_book_reader=True)
                with open(os.path.join(OUT_DIR, bk["out"]), "w", encoding="utf-8") as f:
                    f.write(full_doc)
                print(f"[OK] {bk['out']:34s} (LIVRO + AES-256-GCM)")

            c_secret_html, c_secret_toc = md_to_html(md_content, id_prefix=f"t{idx+1}-", card_h3=card_h3, inject_maps=inject_maps, inject_bestiary_plates=inject_bestiary)
            tome_anchor = f"tomo-{idx+1}"
            compendium_toc.append((2, f"🔒 {bk['num']} — {bk['title']}", tome_anchor))
            c_toc_only_h2 = [(3, lbl, hid) for lvl, lbl, hid in c_secret_toc if lvl == 2]
            c_gated = make_gm_gate_block(
                f"{bk['num']} — {bk['title']}",
                "Volume restrito ao Mestre dentro do Compêndio. Insira a senha para revelar.",
                c_secret_html,
                render_toc_items(c_toc_only_h2),
                codex_file="Alenia_Compendio_Completo.html",
                compendium_mode=True,
            )
            compendium_parts.append(
                f'<section id="{tome_anchor}" class="tome-divider">'
                f'{build_cover(bk["num"], bk["title"], bk["subtitle"], bk["epigraph"], bk["cover_map"])}'
                f'{c_gated}'
                f'</section>'
            )
        elif bk["out"] == "11_Cronica_das_Terras_e_das_Mares.html":
            chronicle_body, chronicle_toc = render_chronicle_timeline_page(bk, md_content)
            full_doc = wrap_html_doc(
                bk["title"],
                bk["out"],
                chronicle_body,
                chronicle_toc,
                force_sidebar=True,
                enable_book_reader=False,
                extra_css=CHRONICLE_CSS,
                extra_js=CHRONICLE_JS,
                body_extra_class="chronicle-mode sidebar-hidden",
            )
            with open(os.path.join(OUT_DIR, bk["out"]), "w", encoding="utf-8") as f:
                f.write(full_doc)
            print(f"[OK] {bk['out']:34s} (PERGAMINHO TIMELINE • {len(chronicle_toc)} secoes)")

            c_inner, c_pub_toc = render_public_doc_with_sealed_sections(md_content, id_prefix=f"t{idx+1}-", card_h3=False, inject_maps=False)
            tome_anchor = f"tomo-{idx+1}"
            compendium_toc.append((2, f"{bk['num']} — {bk['title']}", tome_anchor))
            for lvl, lbl, hid in c_pub_toc:
                if lvl == 2:
                    compendium_toc.append((3, lbl, hid))
            compendium_parts.append(
                f'<section id="{tome_anchor}" class="tome-divider">'
                f'{build_cover(bk["num"], bk["title"], bk["subtitle"], bk["epigraph"], bk["cover_map"])}'
                f'{c_inner}'
                f'</section>'
            )
        elif bk["out"] == "12_Cozinhas_de_Alenia.html":
            cul_body, cul_toc = render_culinaria_page(
                bk,
                md_content,
                {
                    "inline_md": inline_md,
                    "md_to_html": md_to_html,
                    "slugify": slugify,
                    "img_dim_attrs": img_dim_attrs,
                },
            )
            full_doc = wrap_html_doc(
                bk["title"],
                bk["out"],
                cul_body,
                cul_toc,
                force_sidebar=True,
                enable_book_reader=False,
                extra_css=CULINARIA_CSS,
                extra_js=CULINARIA_JS,
                body_extra_class="culinaria-mode sidebar-hidden",
            )
            with open(os.path.join(OUT_DIR, bk["out"]), "w", encoding="utf-8") as f:
                f.write(full_doc)
            print(f"[OK] {bk['out']:34s} (GUIA CULINARIO • {len(cul_toc)} secoes)")

            c_inner, c_pub_toc = render_public_doc_with_sealed_sections(md_content, id_prefix=f"t{idx+1}-", card_h3=False, inject_maps=False)
            tome_anchor = f"tomo-{idx+1}"
            compendium_toc.append((2, f"{bk['num']} — {bk['title']}", tome_anchor))
            for lvl, lbl, hid in c_pub_toc:
                if lvl == 2:
                    compendium_toc.append((3, lbl, hid))
            compendium_parts.append(
                f'<section id="{tome_anchor}" class="tome-divider">'
                f'{build_cover(bk["num"], bk["title"], bk["subtitle"], bk["epigraph"], bk["cover_map"])}'
                f'{c_inner}'
                f'</section>'
            )
        else:
            body_inner, pub_toc = render_public_doc_with_sealed_sections(md_content, id_prefix="", card_h3=card_h3, inject_maps=inject_maps, codex_file=bk["out"], compendium_mode=False)
            full_doc = wrap_html_doc(bk["title"], bk["out"], cover_html + "\n" + body_inner, pub_toc, enable_book_reader=True)
            with open(os.path.join(OUT_DIR, bk["out"]), "w", encoding="utf-8") as f:
                f.write(full_doc)
            print(f"[OK] {bk['out']:34s} (LIVRO • {len(pub_toc)} secoes publicas)")

            c_inner, c_pub_toc = render_public_doc_with_sealed_sections(md_content, id_prefix=f"t{idx+1}-", card_h3=card_h3, inject_maps=inject_maps, codex_file="Alenia_Compendio_Completo.html", compendium_mode=True)
            tome_anchor = f"tomo-{idx+1}"
            compendium_toc.append((2, f"{bk['num']} — {bk['title']}", tome_anchor))
            for lvl, lbl, hid in c_pub_toc:
                if lvl == 2:
                    compendium_toc.append((3, lbl, hid))
            compendium_parts.append(
                f'<section id="{tome_anchor}" class="tome-divider">'
                f'{build_cover(bk["num"], bk["title"], bk["subtitle"], bk["epigraph"], bk["cover_map"])}'
                f'{c_inner}'
                f'</section>'
            )

    comp_html = wrap_html_doc("Compêndio Completo", "Alenia_Compendio_Completo.html", "\n".join(compendium_parts), compendium_toc, enable_book_reader=True)
    with open(os.path.join(OUT_DIR, "Alenia_Compendio_Completo.html"), "w", encoding="utf-8") as f:
        f.write(comp_html)
    print(f"[OK] Alenia_Compendio_Completo.html    (LIVRO • {len(compendium_toc)} entradas publicas)")

    cards = []
    for bk in BOOKS:
        cls = "portal-card gm-card" if bk["gm_only"] else "portal-card"
        if bk["gm_only"]:
            cta = "🔒 Destrancar Livro (Mestre) →"
        elif bk["out"] == "11_Cronica_das_Terras_e_das_Mares.html":
            cta = "📜 Abrir Linha do Tempo →"
        elif bk["out"] == "12_Cozinhas_de_Alenia.html":
            cta = "🍲 Abrir Guia de Culinária →"
        else:
            cta = "Abrir Livro →"
        thumb = f'<img class="portal-cover" src="{bk["cover_map"]}" alt="Capa — {html.escape(bk["title"])}" loading="lazy"/>' if bk["cover_map"] else ""
        cards.append(f"""
        <a class="{cls}" href="{bk['out']}">
            {thumb}
            <div class="portal-kicker">{html.escape(bk['num'])}</div>
            <div class="portal-title">{html.escape(bk['title'])}</div>
            <p class="portal-desc">{html.escape(bk['desc'])}</p>
            <div class="portal-cta">{cta}</div>
        </a>
        """)
    cards.append("""
        <a class="portal-card" href="gerador_tokens.html" style="border-top-color:#1f5156; background:#ece7da;">
            <img class="portal-cover" src="assets/mesa_firecast_alenia.jpg" alt="Gerador de Tokens — Alenia RPG &amp; Firecast" loading="lazy"/>
            <div class="portal-kicker" style="color:#1f5156;">FERRAMENTA VTT • 18 MOLDURAS HD</div>
            <div class="portal-title">Gerador de Tokens</div>
            <p class="portal-desc">Estúdio interativo para criar tokens PNG transparentes (512×512 e 1024×1024): 12 molduras esculpidas pintadas à mão + 6 clássicas/livres + upload de moldura própria.</p>
            <div class="portal-cta" style="color:#1f5156;">⚔ Abrir Estúdio de Tokens →</div>
        </a>
    """)
    cards.append("""
        <a class="portal-card" href="Alenia_Compendio_Completo.html" style="border-top-color:#9a7b3b; background:#efe5cf;">
            <img class="portal-cover" src="assets/alenia_mapa_mundi_atualizado.jpg" alt="Capa — Compêndio Completo" loading="lazy"/>
            <div class="portal-kicker">EDIÇÃO INTEGRAL (PDF MESTRE)</div>
            <div class="portal-title">Compêndio Completo</div>
            <p class="portal-desc">Todos os tomos reunidos em formato de livro folheável com os mapas embutidos — com as áreas do Mestre seladas por senha.</p>
            <div class="portal-cta">Abrir Volume Único →</div>
        </a>
    """)

    index_body = f"""
    <section class="cover-page" style="min-height:auto; page-break-after:auto; break-after:auto; margin-bottom:32px; padding:34px 30px;">
        <div class="cover-kicker">BIBLIOTECA OFICIAL • {EDITION_LABEL}</div>
        <div class="cover-rule"></div>
        <h1 class="cover-title" style="font-size:38px;">ALENIA RPG</h1>
        <div class="cover-subtitle">13 Tomos Ilustrados • Atlas Regional • 36 Kits • Herbário • Crônica • Cozinhas • Grandes Nomes • Estúdio de Tokens • Firecast v2.6</div>
        <div class="cover-rule"></div>
        <div style="margin: 8px 0 4px; display:flex; flex-wrap:wrap; gap:8px; justify-content:center;">
            <a href="https://raw.githubusercontent.com/krleandro/alenia/main/plugins/Alenia_RPG_Ficha.rpk" style="display:inline-block; font-family:'Cinzel',Georgia,serif; font-size:11.5px; letter-spacing:0.09em; text-transform:uppercase; text-decoration:none; background:#7a1f1d; color:#f7f1e3; border:1px solid #9a7b3b; padding:9px 16px; border-radius:3px; font-weight:700;">⬇ Ficha Firecast (v2.6 .rpk)</a>
            <a href="https://raw.githubusercontent.com/krleandro/alenia/main/plugins/Alenia_Token_Studio.rpk" style="display:inline-block; font-family:'Cinzel',Georgia,serif; font-size:11.5px; letter-spacing:0.09em; text-transform:uppercase; text-decoration:none; background:#1f5156; color:#f7f1e3; border:1px solid #9a7b3b; padding:9px 16px; border-radius:3px; font-weight:700;">⬇ Plugin Token Studio (.rpk)</a>
            <a href="gerador_tokens.html" style="display:inline-block; font-family:'Cinzel',Georgia,serif; font-size:11.5px; letter-spacing:0.09em; text-transform:uppercase; text-decoration:none; background:#2b231b; color:#e6cc8a; border:1px solid #9a7b3b; padding:9px 16px; border-radius:3px; font-weight:700;">⚔ Abrir Gerador de Tokens</a>
        </div>
        <figure class="atlas-plate" style="margin:14px 0 0; width:100%;">
            <img src="assets/alenia_mapa_mundi_atualizado.jpg" alt="Mapa-Múndi de Alenia"/>
            <figcaption class="atlas-caption">Clique em qualquer mapa para ampliar em tela cheia</figcaption>
        </figure>
    </section>

    <h2>Estante Oficial (Jogadores &amp; 🔒 Área do Mestre)</h2>
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

    idx_html = wrap_html_doc("Biblioteca Oficial", "index.html", index_body, toc_items=None, enable_book_reader=False)
    with open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(idx_html)
    print("[OK] index.html atualizado.")

    tok_html = wrap_html_doc(
        "Gerador de Tokens",
        "gerador_tokens.html",
        TOKEN_STUDIO_HTML,
        toc_items=None,
        force_sidebar=False,
        enable_book_reader=False,
        extra_css=TOKEN_STUDIO_CSS,
        extra_js=TOKEN_STUDIO_JS,
        body_extra_class="token-studio-mode sidebar-hidden",
    )
    with open(os.path.join(OUT_DIR, "gerador_tokens.html"), "w", encoding="utf-8") as f:
        f.write(tok_html)
    print("[OK] gerador_tokens.html               (ESTUDIO HTML5 CANVAS • 12 MOLDURAS)")


if __name__ == "__main__":
    main()
