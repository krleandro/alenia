#!/usr/bin/env python3
"""
Renderizador Editorial Criptografado do Tomo XIII — Grandes Nomes e Feitos de Alenia
- Mantém 100% do conteúdo dos 100 perfis (N001–N100) dentro do cofre AES-256-GCM do Mestre
- Preserva e refina a interface interativa: busca acento-insensível, filtro pelos 10 círculos sociais,
  filtro pelas 3 origens de perfil, índice alfabético em 3 colunas, guia de genealogias/homônimos,
  links cruzados automáticos entre nomes de personagens e suporte pronto para retratos ilustrados (npc_NXXX.jpg)
"""
import html
import os
import re

GRANDES_NOMES_CSS = r"""
/* =====================================================
   TOMO XIII — GRANDES NOMES E FEITOS DE ALENIA (MESTRE)
   ===================================================== */
body.names-mode .book-shell {
    padding: 72px 18px 72px;
}
body.names-mode:not(.sidebar-hidden) .sidebar-backdrop {
    display: block;
}
body.names-mode .book-page {
    max-width: 1160px;
    padding: 34px 42px 58px;
    background: radial-gradient(circle at top center, #faf4e6 0%, #f4ead6 58%, #ece0c6 100%);
    box-shadow:
        0 26px 72px rgba(0, 0, 0, 0.7),
        0 0 0 1px rgba(154, 123, 59, 0.45);
    overflow-wrap: anywhere;
}
body.names-mode .book-page::before {
    inset: 10px;
    border: 1px solid rgba(154, 123, 59, 0.34);
}
body.names-mode .cover-page {
    min-height: auto;
    padding: 18px 18px 26px;
    margin-bottom: 18px;
}
/* Quando o cofre do Mestre é destrancado, recolhe a capa duplicada acima do painel interativo */
body.names-mode.vault-unlocked .names-locked-cover {
    display: none;
}

/* HERO EDITORIAL INTERNO (PÓS-DESCRIPTOGRAFIA) */
.names-hero {
    display: grid;
    grid-template-columns: 230px 1fr;
    gap: 26px;
    align-items: center;
    padding: 24px 28px;
    margin-bottom: 22px;
    border: 2px solid var(--crimson);
    outline: 1px solid var(--gold);
    outline-offset: -7px;
    background: radial-gradient(circle at 25% 50%, #fcf8ee 0%, #f2e5cb 100%);
    box-shadow: 0 10px 26px rgba(42, 26, 12, 0.14);
}
.names-hero-cover {
    margin: 0 !important;
    padding: 6px !important;
    background: #efe3c6 !important;
    border: 1px solid var(--gold) !important;
}
.names-hero-cover img {
    width: 100%;
    max-height: 300px;
    object-fit: cover;
    display: block;
    cursor: zoom-in;
}
.names-kicker {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 11px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--crimson);
    font-weight: 700;
}
.names-title {
    font-family: 'Cinzel', Georgia, serif !important;
    font-size: 32px !important;
    line-height: 1.15 !important;
    margin: 6px 0 8px !important;
    color: #24180e !important;
    border: none !important;
    padding: 0 !important;
}
.names-sub {
    font-style: italic;
    font-size: 16.8px;
    color: var(--ink-soft);
    margin: 0 0 12px;
}
.names-epigraph {
    font-style: italic;
    font-size: 15.2px;
    color: #3f3021;
    border-left: 3px solid var(--crimson);
    padding: 7px 14px;
    margin: 0 0 14px;
    background: rgba(154, 123, 59, 0.08);
}
.names-stats {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}
.names-stat-pill {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10.2px;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    padding: 5px 10px;
    border-radius: 2px;
    background: rgba(122, 31, 29, 0.09);
    border: 1px solid rgba(122, 31, 29, 0.34);
    color: var(--crimson-dark);
    font-weight: 600;
}
.names-stat-pill.teal {
    background: rgba(31, 81, 86, 0.1);
    border-color: rgba(31, 81, 86, 0.34);
    color: #1a4347;
}

/* GAVETAS EDITORIAIS (GENEALOGIAS & ÍNDICE ALFABÉTICO) */
.names-editorial {
    margin: 0 0 14px;
    border: 1px solid rgba(154, 123, 59, 0.52);
    background: rgba(246, 236, 214, 0.76);
    border-radius: 3px;
    scroll-margin-top: 72px;
}
.names-editorial > summary {
    cursor: pointer;
    padding: 11px 18px;
    font-family: 'Cinzel', Georgia, serif;
    font-size: 12.5px;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    color: var(--crimson-dark);
    font-weight: 700;
    list-style: none;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.names-editorial > summary::-webkit-details-marker { display: none; }
.names-editorial > summary::after {
    content: "▾ Expandir";
    font-size: 10.5px;
    color: var(--gold);
}
.names-editorial[open] > summary::after { content: "▴ Recolher"; }
.names-editorial-inner {
    padding: 8px 22px 18px;
    border-top: 1px solid rgba(154, 123, 59, 0.28);
}
.names-index {
    columns: 3;
    column-gap: 24px;
    padding: 14px 20px 18px;
    border-top: 1px solid rgba(154, 123, 59, 0.28);
}
.names-index a {
    display: block;
    break-inside: avoid;
    font-size: 14.5px;
    line-height: 1.38;
    margin: 0 0 6px;
    color: #2f2115;
    text-decoration: none;
    padding: 2px 4px;
    border-radius: 2px;
}
.names-index a:hover {
    background: rgba(122, 31, 29, 0.1);
    color: var(--crimson-dark);
}
.names-index .idx-code {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 11px;
    font-weight: 700;
    color: var(--crimson);
    margin-right: 4px;
}

/* BARRA INTERATIVA DE BUSCA & FILTROS */
.names-toolbar {
    background: linear-gradient(180deg, rgba(31, 24, 18, 0.97) 0%, rgba(22, 17, 13, 0.97) 100%);
    border: 1px solid rgba(154, 123, 59, 0.65);
    border-radius: 4px;
    padding: 14px 16px;
    margin: 18px 0 28px;
    box-shadow: 0 10px 26px rgba(0, 0, 0, 0.34);
    color: #efe6d2;
}
.names-controls {
    display: grid;
    grid-template-columns: 1.5fr 1fr 1fr;
    gap: 12px;
    align-items: end;
}
.names-controls label {
    display: flex;
    flex-direction: column;
    gap: 5px;
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--gold-light);
}
.names-controls input,
.names-controls select {
    padding: 8px 11px;
    min-width: 0;
    width: 100%;
    border-radius: 3px;
    border: 1px solid rgba(154, 123, 59, 0.55);
    background: #14100c;
    color: #f7f1e3;
    font-family: 'EB Garamond', Georgia, serif;
    font-size: 15.5px;
}
.names-controls input::placeholder {
    color: #9c8f7a;
    font-style: italic;
}
.names-status-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    margin-top: 10px;
    padding-top: 8px;
    border-top: 1px solid rgba(154, 123, 59, 0.24);
}
.names-count {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10.8px;
    letter-spacing: 0.08em;
    color: var(--gold-light);
    margin: 0;
}
.names-reset-btn {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: 3px;
    border: 1px solid rgba(154, 123, 59, 0.5);
    background: rgba(122, 31, 29, 0.35);
    color: #f7ebd2;
    cursor: pointer;
}
.names-reset-btn:hover { background: var(--crimson); }

/* SEÇÕES POR CÍRCULO SOCIAL */
.names-group {
    margin: 0 0 38px;
    scroll-margin-top: 68px;
}
.names-group-header {
    padding: 13px 18px;
    margin-bottom: 14px;
    background: linear-gradient(90deg, rgba(122, 31, 29, 0.1) 0%, rgba(154, 123, 59, 0.14) 55%, rgba(122, 31, 29, 0.04) 100%);
    border-top: 2px solid var(--crimson);
    border-bottom: 1px solid var(--gold);
    border-left: 4px solid var(--crimson);
}
.names-group-kicker {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--crimson);
    font-weight: 700;
}
.names-group-title {
    font-family: 'Cinzel', Georgia, serif !important;
    font-size: 23px !important;
    color: #24180e !important;
    margin: 2px 0 0 !important;
    border: none !important;
    padding: 0 !important;
}

/* CARTÕES DE PERFIL (N001–N100) + SLOT DE RETRATO PRONTO */
.names-card {
    padding: 20px 22px;
    margin-bottom: 16px;
    background: linear-gradient(180deg, rgba(252, 247, 236, 0.94) 0%, rgba(244, 234, 214, 0.94) 100%);
    border: 1px solid rgba(154, 123, 59, 0.48);
    border-left: 4px solid #6b1d1a;
    border-radius: 3px;
    box-shadow: 0 4px 14px rgba(42, 26, 12, 0.08);
    display: flow-root;
    scroll-margin-top: 74px;
}
.names-card[data-kind="Nome-modelo desenvolvido"] {
    border-left-color: #1f5156;
}
.names-card[data-kind="Nova figura ou papel nomeado"] {
    border-left-color: #7d5c21;
}
.names-card-head {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
    margin-bottom: 6px;
}
.names-code-pill {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.1em;
    padding: 3px 8px;
    border-radius: 2px;
    background: var(--crimson);
    color: #f7f1e3;
}
.names-kind-pill {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 9.8px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 3px 8px;
    border-radius: 2px;
    background: rgba(154, 123, 59, 0.16);
    border: 1px solid rgba(154, 123, 59, 0.45);
    color: #4a351d;
    font-weight: 600;
}
.names-sphere-pill {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 9.8px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 3px 8px;
    border-radius: 2px;
    background: rgba(31, 81, 86, 0.1);
    border: 1px solid rgba(31, 81, 86, 0.32);
    color: #1a4347;
}
.names-card h3 {
    font-family: 'Cinzel', Georgia, serif !important;
    font-size: 22px !important;
    line-height: 1.22 !important;
    color: #22160c !important;
    margin: 4px 0 4px !important;
    border: none !important;
    padding: 0 !important;
}
.names-meta {
    font-style: italic;
    font-size: 14.8px;
    color: #5b4631;
    margin: 0 0 12px;
    padding-bottom: 8px;
    border-bottom: 1px dotted rgba(154, 123, 59, 0.45);
}

/* Slot pronto para os retratos coerentes dos NPCs (npc_N001..N100.jpg) */
.names-portrait {
    float: right;
    width: 230px;
    margin: 0 0 14px 22px !important;
    padding: 5px !important;
    background: #efe3c8 !important;
    border: 1px solid rgba(154, 123, 59, 0.65) !important;
    border-radius: 2px;
    box-shadow: 0 6px 16px rgba(42, 26, 12, 0.16);
}
.names-portrait img {
    width: 100%;
    aspect-ratio: 3 / 4;
    object-fit: cover;
    display: block;
    cursor: zoom-in;
}

.names-card p {
    font-size: 16.3px;
    line-height: 1.56;
    margin: 0 0 9px;
    text-align: left;
}
.names-card p strong {
    color: #5b201b;
}
a.names-person-link {
    color: #5e1917;
    text-decoration: underline;
    text-decoration-style: dotted;
    text-underline-offset: 2px;
    font-weight: 600;
}
a.names-person-link:hover {
    color: var(--crimson);
    background: rgba(154, 123, 59, 0.15);
    text-decoration-style: solid;
}
.names-card-foot {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    margin-top: 12px;
    padding-top: 8px;
    border-top: 1px dotted rgba(154, 123, 59, 0.4);
    font-size: 14px;
    color: var(--ink-soft);
}
.names-back {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10.5px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--crimson);
    text-decoration: none;
}
.names-back:hover { text-decoration: underline; }

.names-empty {
    text-align: center;
    padding: 32px 20px;
    border: 1px dashed var(--gold);
    background: rgba(246, 236, 214, 0.72);
    font-style: italic;
    color: var(--ink-soft);
    margin: 16px 0 28px;
}
.names-mode [hidden] { display: none !important; }
.names-appendix {
    margin-top: 34px;
    padding-top: 20px;
    border-top: 2px solid var(--gold);
}
.names-appendix h2 { scroll-margin-top: 68px; }

@media (max-width: 860px) {
    body.names-mode .book-page { padding: 22px 18px 42px; }
    .names-hero { grid-template-columns: 1fr; text-align: center; padding: 20px; }
    .names-hero-cover { max-width: 220px; margin: 0 auto !important; }
    .names-stats { justify-content: center; }
    .names-controls { grid-template-columns: 1fr; }
    .names-index { columns: 1; }
    .names-portrait { float: none; width: 100%; max-width: 260px; margin: 0 auto 14px !important; }
}
@media print {
    .names-toolbar, .names-back { display: none !important; }
    .names-card { break-inside: avoid; page-break-inside: avoid; }
    .names-index { columns: 2; }
}
"""

GRANDES_NOMES_JS = r"""
(function() {
    let bound = false;

    function initNamesUI() {
        const root = document.getElementById('names-root');
        if (!root || bound) return;
        bound = true;
        document.body.classList.add('vault-unlocked');

        const cards = Array.from(root.querySelectorAll('.names-card'));
        const q = document.getElementById('names-query');
        const sphere = document.getElementById('names-sphere');
        const kind = document.getElementById('names-kind');
        const countEl = document.getElementById('names-count');
        const emptyEl = document.getElementById('names-empty');
        const resetBtn = document.getElementById('names-reset');

        const norm = (s) => (s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();

        function applyFilter() {
            const query = norm(q ? q.value.trim() : '');
            const sv = sphere ? sphere.value : '';
            const kv = kind ? kind.value : '';
            let count = 0;

            cards.forEach(c => {
                const hide = Boolean(
                    (sv && c.dataset.sphere !== sv) ||
                    (kv && c.dataset.kind !== kv) ||
                    (query && !norm(c.dataset.search).includes(query))
                );
                c.hidden = hide;
                if (!hide) count++;
            });

            root.querySelectorAll('.names-group').forEach(g => {
                const anyVis = Array.from(g.querySelectorAll('.names-card')).some(c => !c.hidden);
                g.hidden = !anyVis;
            });

            if (countEl) countEl.textContent = `Exibindo ${count} de ${cards.length} perfis`;
            if (emptyEl) emptyEl.hidden = (count !== 0);
            if (resetBtn) resetBtn.hidden = !(query || sv || kv);
        }

        if (q) q.addEventListener('input', applyFilter);
        if (sphere) sphere.addEventListener('change', applyFilter);
        if (kind) kind.addEventListener('change', applyFilter);
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                if (q) q.value = '';
                if (sphere) sphere.value = '';
                if (kind) kind.value = '';
                applyFilter();
            });
        }

        window.aleniaRevealAnchor = function(id) {
            const target = document.getElementById(id);
            if (!target) return;
            const card = target.classList.contains('names-card') ? target : target.closest('.names-card');
            if (card && card.hidden) {
                if (q) q.value = '';
                if (sphere) sphere.value = '';
                if (kind) kind.value = '';
                applyFilter();
            }
            const details = target.closest('details');
            if (details && !details.open) details.open = true;
        };

        // Bind newly unlocked images inside .atlas-plate to the global lightbox
        document.querySelectorAll('.gm-unlocked-content .atlas-plate img').forEach(img => {
            img.addEventListener('click', () => {
                const lb = document.getElementById('atlas-lightbox');
                const lbImg = document.getElementById('atlas-lightbox-img');
                if (lb && lbImg) {
                    lbImg.src = img.src;
                    lb.classList.add('open');
                }
            });
        });

        // Close sidebar drawer when clicking TOC items
        document.querySelectorAll('.toc-list a').forEach(a => {
            a.addEventListener('click', () => {
                document.body.classList.add('sidebar-hidden');
                document.body.classList.remove('sidebar-open-mobile');
            });
        });

        applyFilter();

        if (window.location.hash) {
            const hid = decodeURIComponent(window.location.hash.slice(1));
            window.aleniaRevealAnchor(hid);
            const el = document.getElementById(hid);
            if (el) setTimeout(() => el.scrollIntoView({ behavior: 'smooth', block: 'start' }), 90);
        }

        window.addEventListener('beforeprint', () => {
            root.querySelectorAll('[hidden]').forEach(e => { e.dataset.printHidden = '1'; e.hidden = false; });
        });
        window.addEventListener('afterprint', () => {
            root.querySelectorAll('[data-print-hidden]').forEach(e => { delete e.dataset.printHidden; });
            applyFilter();
        });
    }

    document.addEventListener('alenia:gm-unlocked', initNamesUI);
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initNamesUI);
    } else {
        initNamesUI();
    }
})();
"""


def render_grandes_nomes_secret_payload(bk: dict, md_content: str, helpers: dict):
    """
    Parse canonical 13_Grandes_Nomes_e_Feitos_de_Alenia.md into the rich interactive
    Master UI + TOC items (to be sealed inside the AES-256-GCM vault).
    """
    inline_md = helpers["inline_md"]
    md_to_html = helpers["md_to_html"]
    img_dim_attrs = helpers["img_dim_attrs"]
    rewrite_link = helpers["rewrite_link"]

    # Split into H2 sections
    sections = re.split(r"(?=^##\s+)", md_content, flags=re.M)

    intro_secs = []
    group_secs = []
    appendix_secs = []

    known_groups = {
        "Coroa e memória",
        "Portos e regências",
        "Matas e fronteiras",
        "Mares e exploração",
        "Fé e conhecimento",
        "Ofícios e trabalho",
        "Intriga e justiça",
        "Crime e margens",
        "Artes e cotidiano",
        "Memórias e ameaças",
    }

    for sec in sections:
        s = sec.strip()
        m_h2 = re.match(r"^##\s+(.+)$", s, flags=re.M)
        if not m_h2:
            continue
        title = m_h2.group(1).strip()
        if title == "Índice alfabético":
            continue
        elif title in known_groups:
            group_secs.append((title, s))
        elif re.search(r"^###\s+N\d{3}\s", s, flags=re.M):
            group_secs.append((title, s))
        elif not group_secs:
            intro_secs.append(s)
        else:
            appendix_secs.append(s)

    # First pass: extract all 100 profiles so we can build cross-links by character name
    profiles = []
    for g_title, g_raw in group_secs:
        parts = re.split(r"(?=^###\s+N\d{3}\s)", g_raw, flags=re.M)
        for pblk in parts[1:]:
            lines = [ln.strip() for ln in pblk.strip().splitlines() if ln.strip() and not ln.strip().startswith("<a id=")]
            if not lines:
                continue
            m_ph = re.match(r"^###\s+(N\d{3})\s+[—–-]\s+(.+)$", lines[0])
            if not m_ph:
                continue
            code = m_ph.group(1)
            name = m_ph.group(2).strip()
            kind = ""
            period = ""
            portrait_src = ""
            portrait_alt = ""
            fields = []
            base_ref = ""

            for ln in lines[1:]:
                m_img = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", ln)
                if m_img:
                    portrait_alt = m_img.group(1).strip() or f"{code} — {name}"
                    raw_p = m_img.group(2).strip().replace("\\", "/")
                    portrait_src = ("assets/" + os.path.basename(raw_p)) if "ilustracoes/" in raw_p or "assets/" in raw_p else raw_p
                    continue
                if ln.startswith("**Registro:**"):
                    m_rk = re.search(r"\*\*Registro:\*\*\s*([^.*]+)\.\s*\*\*Época:\*\*\s*(.+)$", ln)
                    if m_rk:
                        kind = m_rk.group(1).strip()
                        period = m_rk.group(2).strip()
                    continue
                if ln.startswith("**Base de referência:**"):
                    base_ref = ln.split("**Base de referência:**", 1)[1].strip()
                    continue
                m_fld = re.match(r"^\*\*([^*:]+):\*\*\s*(.+)$", ln)
                if m_fld:
                    fields.append((m_fld.group(1).strip(), m_fld.group(2).strip()))
                else:
                    fields.append(("", ln))

            profiles.append({
                "code": code,
                "name": name,
                "sphere": g_title,
                "kind": kind,
                "period": period,
                "portrait_src": portrait_src,
                "portrait_alt": portrait_alt,
                "fields": fields,
                "base_ref": base_ref,
            })

    # Build exact character-name cross-linker (full names + unambiguous short/regnal aliases)
    name_to_profile = {p["name"]: p for p in profiles}
    unambiguous_aliases = {
        "Severor I": "Severor I Valerion",
        "Severor II": "Severor II Valerion",
        "Severor III": "Severor III Valerion",
        "Aemilius IV": "Aemilius IV Valerion",
        "Regente das Cinzas": "O Regente das Cinzas",
    }
    for alias, target_full in unambiguous_aliases.items():
        if target_full in name_to_profile:
            name_to_profile[alias] = name_to_profile[target_full]

    # Automatically add any first name (>=4 chars, capitalized, not a common word) unique to exactly 1 profile
    first_token_map = {}
    blocked_first_tokens = {"Frei", "Dona", "Dom", "Lorde", "Dama"}
    for p in profiles:
        tok0 = p["name"].split(",")[0].split()[0]
        if len(tok0) >= 4 and tok0[0].isupper() and tok0 not in blocked_first_tokens:
            first_token_map.setdefault(tok0, []).append(p)
    for tok0, plist in first_token_map.items():
        if len(plist) == 1 and tok0 not in name_to_profile:
            name_to_profile[tok0] = plist[0]

    md_file_labels = {
        "01_Livro_de_Regras.md": "Tomo I — Livro de Regras",
        "02_Guia_de_Cenario_Alenia.md": "Tomo II — Guia de Cenário",
        "03_Catalogo_de_Kits.md": "Tomo III — Catálogo de Kits",
        "04_Bestiario_Alenia.md": "Tomo IV — Bestiário",
        "05_Onomastica_e_Toponimia_Alenia.md": "Tomo V — Onomástica",
        "06_Guia_do_Jogador_e_Referencia_Rapida.md": "Tomo VI — Guia do Jogador",
        "07_Aventura_Inicial_Cinzas_no_Estuario.md": "Tomo VII — Aventura Inicial",
        "08_Acervo_Oculto_de_Sellene.md": "Tomo VIII — Acervo de Sellene",
        "09_Catalogo_de_Equipamentos_e_Oficios.md": "Tomo IX — Equipamentos e Ofícios",
        "10_Herbario_de_Seleni.md": "Tomo X — Herbário de Seleni",
        "11_Cronica_das_Terras_e_das_Mares.md": "Tomo XI — Crônica de Alenia",
        "12_Cozinhas_de_Alenia.md": "Tomo XII — Cozinhas de Alenia",
    }

    sorted_names = sorted(name_to_profile.keys(), key=len, reverse=True)
    name_re = re.compile(
        r"(?<![\wÀ-ÿ])(" + "|".join(re.escape(n) for n in sorted_names) + r")(?![\wÀ-ÿ])"
    ) if sorted_names else None

    def link_person_names(raw_text: str, self_code: str = "") -> str:
        """Apply inline_md, then safely link character names outside HTML tags & existing <a> tags."""
        rendered = inline_md(raw_text)
        if not name_re:
            return rendered
        parts = re.split(r"(<[^>]+>)", rendered)
        out = []
        in_a = 0
        for part in parts:
            if part.startswith("<"):
                if re.match(r"^<\s*a\b", part, re.I):
                    in_a += 1
                elif re.match(r"^</\s*a\b", part, re.I):
                    in_a = max(0, in_a - 1)
                out.append(part)
            elif in_a > 0:
                out.append(part)
            else:
                def _sub(m):
                    matched = m.group(1)
                    target = name_to_profile[matched]
                    if target["code"] == self_code:
                        return matched
                    t_attr = html.escape(f'{target["code"]} — {target["name"]} ({target["sphere"]})', quote=True)
                    return f'<a class="names-person-link" href="#{target["code"].lower()}" title="{t_attr}">{matched}</a>'
                out.append(name_re.sub(_sub, part))
        return "".join(out)

    # Render collapsible Editorial Intro
    intro_html, _ = md_to_html("\n\n".join(intro_secs), id_prefix="nomes-intro-", card_h3=False, inject_maps=False)

    # Build 3-column Alphabetical Index
    alpha_links = "".join(
        f'<a href="#{p["code"].lower()}"><span class="idx-code">{p["code"]}</span> {html.escape(p["name"])}</a>'
        for p in sorted(profiles, key=lambda x: x["name"])
    )

    # Counts by sphere & kind for dropdowns
    sphere_counts = {}
    kind_counts = {}
    for p in profiles:
        sphere_counts[p["sphere"]] = sphere_counts.get(p["sphere"], 0) + 1
        if p["kind"]:
            kind_counts[p["kind"]] = kind_counts.get(p["kind"], 0) + 1

    sphere_opts = "".join(
        f'<option value="{html.escape(g, quote=True)}">{html.escape(g)} ({sphere_counts.get(g, 0)})</option>'
        for g, _ in group_secs
    )
    kind_opts = "".join(
        f'<option value="{html.escape(k, quote=True)}">{html.escape(k)} ({cnt})</option>'
        for k, cnt in kind_counts.items()
    )

    toc_items = [(2, "Índice Alfabético (N001–N100)", "indice-nomes")]
    groups_html = []

    for g_idx, (g_title, _) in enumerate(group_secs, 1):
        g_id = f"circulo-{g_idx}"
        toc_items.append((2, f"{g_idx}. {g_title}", g_id))
        g_profiles = [p for p in profiles if p["sphere"] == g_title]
        cards_html = []

        for p in g_profiles:
            search_blob = html.escape(
                f'{p["code"]} {p["name"]} {p["sphere"]} {p["kind"]} {p["period"]} '
                + " ".join(f"{lbl} {val}" for lbl, val in p["fields"]),
                quote=True,
            )
            portrait_html = ""
            if p["portrait_src"]:
                portrait_html = (
                    f'<figure class="atlas-plate names-portrait" title="Clique para ampliar retrato">'
                    f'<img src="{html.escape(p["portrait_src"], quote=True)}" '
                    f'alt="{html.escape(p["portrait_alt"], quote=True)}"{img_dim_attrs(p["portrait_src"])} loading="lazy"/>'
                    f'</figure>'
                )

            f_paras = []
            for lbl, val in p["fields"]:
                if lbl:
                    f_paras.append(f'<p><strong>{html.escape(lbl)}:</strong> {link_person_names(val, p["code"])}</p>')
                else:
                    f_paras.append(f'<p>{link_person_names(val, p["code"])}</p>')

            raw_ref = p["base_ref"]
            for md_fn, nice_lbl in md_file_labels.items():
                raw_ref = raw_ref.replace(f"[{md_fn}](", f"[{nice_lbl}](")
            ref_html = inline_md(raw_ref) if raw_ref else "Criação desta edição."

            cards_html.append(f"""
            <article class="names-card" id="{p['code'].lower()}"
                     data-sphere="{html.escape(p['sphere'], quote=True)}"
                     data-kind="{html.escape(p['kind'], quote=True)}"
                     data-search="{search_blob}">
                <div class="names-card-head">
                    <span class="names-code-pill">{html.escape(p['code'])}</span>
                    <span class="names-kind-pill">{html.escape(p['kind'])}</span>
                    <span class="names-sphere-pill">{html.escape(p['sphere'])}</span>
                </div>
                {portrait_html}
                <h3>{html.escape(p['name'])}</h3>
                <div class="names-meta">{html.escape(p['period'])}</div>
                {"".join(f_paras)}
                <div class="names-card-foot">
                    <span><strong>Base:</strong> {ref_html}</span>
                    <a class="names-back" href="#indice-nomes">↑ Índice alfabético</a>
                </div>
            </article>
            """)

        groups_html.append(f"""
        <section class="names-group" id="{g_id}">
            <header class="names-group-header">
                <div class="names-group-kicker">CÍRCULO SOCIAL {g_idx} DE {len(group_secs)} • {len(g_profiles)} PERFIS</div>
                <h2 class="names-group-title">{html.escape(g_title)}</h2>
            </header>
            {"".join(cards_html)}
        </section>
        """)

    # Render Appendix (Relações, 12 Encontros, Cobertura, Fontes) + cross-link character names in Appendix too!
    ap_md = "\n\n".join(appendix_secs)
    for md_fn, nice_lbl in md_file_labels.items():
        ap_md = ap_md.replace(f"[{md_fn}](", f"[{nice_lbl}](")
    appendix_raw_html, appendix_toc = md_to_html(ap_md, id_prefix="nomes-ap-", card_h3=False, inject_maps=False)
    if name_re:
        ap_parts = re.split(r"(<[^>]+>)", appendix_raw_html)
        ap_out = []
        in_skip = 0
        for part in ap_parts:
            if part.startswith("<"):
                if re.match(r"^<\s*(?:a|h1|h2|h3|h4)\b", part, re.I):
                    in_skip += 1
                elif re.match(r"^</\s*(?:a|h1|h2|h3|h4)\b", part, re.I):
                    in_skip = max(0, in_skip - 1)
                ap_out.append(part)
            elif in_skip > 0:
                ap_out.append(part)
            else:
                ap_out.append(
                    name_re.sub(
                        lambda m: (
                            f'<a class="names-person-link" href="#{name_to_profile[m.group(1)]["code"].lower()}" '
                            f'title="{html.escape(name_to_profile[m.group(1)]["code"] + " — " + name_to_profile[m.group(1)]["name"], quote=True)}">'
                            f'{m.group(1)}</a>'
                        ),
                        part,
                    )
                )
        appendix_raw_html = "".join(ap_out)

    toc_items.extend(appendix_toc)

    hero_html = f"""
    <section class="names-hero">
        <figure class="atlas-plate names-hero-cover">
            <img src="{bk['cover_map']}" alt="Capa — {html.escape(bk['title'])}"{img_dim_attrs(bk['cover_map'])}/>
        </figure>
        <div>
            <div class="names-kicker">ALENIA RPG • {html.escape(bk['num'])} • PROSOPOGRAFIA &amp; BASTIDORES</div>
            <h1 class="names-title">{html.escape(bk['title'])}</h1>
            <p class="names-sub">{len(profiles)} perfis em {len(group_secs)} círculos sociais — linhagens, aparências, contradições, legados e entradas em cena (Ano 418 EF).</p>
            <blockquote class="names-epigraph">
                “Nem todo nome que mudou o mundo foi gravado numa coroa.”
            </blockquote>
            <div class="names-stats">
                <span class="names-stat-pill">👑 {kind_counts.get('Anterior desenvolvido', 45)} Anteriores + A Sombra</span>
                <span class="names-stat-pill">📜 {kind_counts.get('Nome-modelo desenvolvido', 19)} Da Onomástica</span>
                <span class="names-stat-pill teal">✦ {kind_counts.get('Nova figura ou papel nomeado', 36)} Novas Figuras</span>
                <span class="names-stat-pill teal">🔗 12 Encontros Cruzados</span>
            </div>
        </div>
    </section>
    <details class="names-editorial">
        <summary>📜 Critérios, Linhagens, Genealogias, Homônimos &amp; Decisões de Continuidade</summary>
        <div class="names-editorial-inner">{intro_html}</div>
    </details>
    <details class="names-editorial" id="indice-nomes">
        <summary>🔤 Índice Alfabético dos {len(profiles)} Perfis (N001–N{len(profiles):03d})</summary>
        <div class="names-index">{alpha_links}</div>
    </details>
    <div class="names-toolbar" role="region" aria-label="Filtros dos Grandes Nomes de Alenia">
        <div class="names-controls">
            <label>Buscar por nome, lugar, família, ano ou feito
                <input id="names-query" type="search" placeholder="Ex.: Valerion, Seleni, Merlinport, cozinheira, 356..." aria-label="Buscar perfis"/>
            </label>
            <label>Círculo social
                <select id="names-sphere">
                    <option value="">Todos os círculos ({len(profiles)})</option>
                    {sphere_opts}
                </select>
            </label>
            <label>Origem editorial do perfil
                <select id="names-kind">
                    <option value="">Todas as origens ({len(profiles)})</option>
                    {kind_opts}
                </select>
            </label>
        </div>
        <div class="names-status-bar">
            <p id="names-count" class="names-count" role="status">Exibindo {len(profiles)} de {len(profiles)} perfis</p>
            <button id="names-reset" class="names-reset-btn" type="button" hidden>✕ Limpar filtros</button>
        </div>
    </div>
    <div id="names-empty" class="names-empty" hidden>Nenhum perfil corresponde aos filtros atuais. Clique em “Limpar filtros” para exibir todos os 100 nomes.</div>
    <div id="names-root">{"".join(groups_html)}</div>
    <section class="names-appendix">{appendix_raw_html}</section>
    """

    return hero_html, toc_items
