#!/usr/bin/env python3
"""
Renderizador Editorial Ilustrado do Tomo XII — Cozinhas de Alenia
- Preserva o recorte por quadrantes (q0..q3) mostrando a foto individual de cada um dos 32 pratos (C01-C32)
- Integra-se à barra superior, barra lateral (Livros + Sumário) e lightbox oficial da Biblioteca de Alenia
- Filtros por região + busca instantânea por prato, ingrediente, animal (A01-A22) ou código do Herbário (H)
- Grade de 2 colunas para os 22 Animais das Cozinhas + seções de Despensa, Viagem, Cenas e Índice Rápido
"""
import html
import os
import re

CULINARIA_CSS = r"""
/* =====================================================
   TOMO XII — COZINHAS DE ALENIA (GUIA CULINÁRIO ILUSTRADO)
   ===================================================== */
body.culinaria-mode .book-shell {
    padding: 72px 18px 72px;
}
body.culinaria-mode:not(.sidebar-hidden) .sidebar-backdrop {
    display: block;
}
body.culinaria-mode .book-page {
    max-width: 1180px;
    padding: 34px 42px 58px;
    background: radial-gradient(circle at top center, #faf4e6 0%, #f4ead6 58%, #ece0c6 100%);
    box-shadow:
        0 26px 72px rgba(0, 0, 0, 0.7),
        0 0 0 1px rgba(154, 123, 59, 0.45);
}
body.culinaria-mode .book-page::before {
    inset: 10px;
    border: 1px solid rgba(154, 123, 59, 0.34);
}

/* HERO / CAPA EDITORIAL */
.cul-hero {
    display: grid;
    grid-template-columns: 260px 1fr;
    gap: 28px;
    align-items: center;
    padding: 26px 28px;
    margin-bottom: 22px;
    border: 2px solid var(--crimson);
    outline: 1px solid var(--gold);
    outline-offset: -7px;
    background: radial-gradient(circle at 25% 50%, #fcf8ee 0%, #f2e5cb 100%);
    box-shadow: 0 10px 26px rgba(42, 26, 12, 0.14);
}
.cul-hero-cover {
    margin: 0 !important;
    padding: 7px !important;
    background: #efe3c6 !important;
    border: 1px solid var(--gold) !important;
}
.cul-hero-cover img {
    width: 100%;
    max-height: 330px;
    object-fit: cover;
    display: block;
    cursor: zoom-in;
}
.cul-kicker {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 11px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--crimson);
    font-weight: 700;
}
.cul-title {
    font-family: 'Cinzel', Georgia, serif !important;
    font-size: 34px !important;
    line-height: 1.14 !important;
    margin: 6px 0 8px !important;
    color: #24180e !important;
    border: none !important;
    padding: 0 !important;
}
.cul-sub {
    font-style: italic;
    font-size: 17px;
    color: var(--ink-soft);
    margin: 0 0 12px;
}
.cul-epigraph {
    font-style: italic;
    font-size: 15.2px;
    color: #3f3021;
    border-left: 3px solid var(--crimson);
    padding: 7px 14px;
    margin: 0 0 14px;
    background: rgba(154, 123, 59, 0.08);
}
.cul-stats {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}
.cul-stat-pill {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10.5px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 5px 10px;
    border-radius: 2px;
    background: rgba(122, 31, 29, 0.09);
    border: 1px solid rgba(122, 31, 29, 0.34);
    color: var(--crimson-dark);
    font-weight: 600;
}
.cul-stat-pill.teal {
    background: rgba(31, 81, 86, 0.1);
    border-color: rgba(31, 81, 86, 0.34);
    color: #1a4347;
}

/* GUIA INTRODUTÓRIO EXPANSÍVEL */
.cul-intro-details {
    margin: 0 0 22px;
    border: 1px solid rgba(154, 123, 59, 0.52);
    background: rgba(246, 236, 214, 0.72);
    border-radius: 3px;
}
.cul-intro-details > summary {
    cursor: pointer;
    padding: 11px 18px;
    font-family: 'Cinzel', Georgia, serif;
    font-size: 12px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--crimson-dark);
    font-weight: 700;
    list-style: none;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.cul-intro-details > summary::-webkit-details-marker { display: none; }
.cul-intro-details > summary::after {
    content: "▾ Expandir";
    font-size: 10.5px;
    color: var(--gold);
}
.cul-intro-details[open] > summary::after { content: "▴ Recolher"; }
.cul-intro-inner {
    padding: 4px 22px 18px;
    border-top: 1px solid rgba(154, 123, 59, 0.28);
}

/* BARRA DE FILTROS & BUSCA */
.cul-toolbar {
    background: linear-gradient(180deg, rgba(31, 24, 18, 0.97) 0%, rgba(22, 17, 13, 0.97) 100%);
    border: 1px solid rgba(154, 123, 59, 0.65);
    border-radius: 4px;
    padding: 12px 16px;
    margin: 0 0 28px;
    box-shadow: 0 10px 26px rgba(0, 0, 0, 0.34);
    color: #efe6d2;
}
.cul-region-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 10px;
}
.cul-pill {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 5px 10px;
    border-radius: 3px;
    border: 1px solid rgba(154, 123, 59, 0.42);
    background: rgba(255, 255, 255, 0.04);
    color: #ded4c1;
    cursor: pointer;
    transition: all 0.14s ease;
}
.cul-pill:hover {
    border-color: var(--gold-light);
    color: var(--gold-light);
    background: rgba(154, 123, 59, 0.16);
}
.cul-pill.active {
    background: var(--crimson);
    border-color: var(--gold-light);
    color: #fff6e0;
    font-weight: 700;
}
.cul-search-row {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 10px;
}
.cul-search {
    flex: 1 1 260px;
    min-width: 180px;
    padding: 7px 12px;
    border-radius: 3px;
    border: 1px solid rgba(154, 123, 59, 0.55);
    background: #14100c;
    color: #f7f1e3;
    font-family: 'EB Garamond', Georgia, serif;
    font-size: 15.5px;
}
.cul-search::placeholder { color: #9c8f7a; font-style: italic; }
.cul-count {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10.5px;
    letter-spacing: 0.08em;
    color: var(--gold-light);
    white-space: nowrap;
}

/* SEÇÃO REGIONAL */
.cul-region {
    margin: 0 0 42px;
    scroll-margin-top: 68px;
}
.cul-region.is-hidden { display: none; }
.cul-region-header {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 14px;
    padding: 15px 20px;
    margin-bottom: 16px;
    background: linear-gradient(90deg, rgba(122, 31, 29, 0.1) 0%, rgba(154, 123, 59, 0.14) 55%, rgba(122, 31, 29, 0.05) 100%);
    border-top: 2px solid var(--crimson);
    border-bottom: 1px solid var(--gold);
    border-left: 4px solid var(--crimson);
}
.cul-region-kicker {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--crimson);
    font-weight: 700;
}
.cul-region-title {
    font-family: 'Cinzel', Georgia, serif !important;
    font-size: 24px !important;
    color: #24180e !important;
    margin: 2px 0 0 !important;
    border: none !important;
    padding: 0 !important;
}
.cul-plate-btn {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 7px 12px;
    border-radius: 3px;
    border: 1px solid var(--gold);
    background: #2b1e14;
    color: #f3e4be;
    cursor: pointer;
    transition: all 0.15s ease;
}
.cul-plate-btn:hover {
    background: var(--crimson);
    color: #fff;
}
.cul-region-intro {
    margin: 0 0 20px;
    font-size: 16.5px;
    color: #2e241b;
}

/* CARTÃO DE RECEITA COM FOTO INDIVIDUAL EM QUADRANTE */
.cul-recipe {
    border-top: 1px solid rgba(154, 123, 59, 0.45);
    padding: 24px 0 22px;
    display: flow-root;
    scroll-margin-top: 70px;
}
.cul-recipe.is-hidden { display: none; }
.cul-recipe-head {
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    gap: 10px;
    margin-bottom: 10px;
}
.cul-code {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.1em;
    padding: 3px 8px;
    border-radius: 2px;
    background: var(--crimson);
    color: #f7f1e3;
}
.cul-recipe-title {
    font-family: 'Cinzel', Georgia, serif !important;
    font-size: 21px !important;
    color: #24180e !important;
    margin: 0 !important;
    border: none !important;
    padding: 0 !important;
}

/* FOTO DO PRATO (QUADRANTE 2x2 DA PRANCHA HD) */
.cul-food-photo {
    position: relative;
    overflow: hidden;
    aspect-ratio: 3 / 2;
    width: 45%;
    float: right;
    margin: 0 0 18px 28px;
    border: 1px solid var(--gold);
    outline: 1px solid rgba(122, 31, 29, 0.28);
    outline-offset: -4px;
    border-radius: 3px;
    background: #e6d5ba;
    box-shadow: 0 8px 22px rgba(42, 26, 12, 0.2);
    cursor: zoom-in;
}
.cul-food-photo img {
    position: absolute;
    width: 200%;
    height: 200%;
    max-width: none !important;
    object-fit: fill;
    transition: transform 0.28s ease;
}
.cul-food-photo:hover img {
    filter: brightness(1.04);
}
.cul-food-photo.q0 img { left: 0; top: 0; }
.cul-food-photo.q1 img { left: -100%; top: 0; }
.cul-food-photo.q2 img { left: 0; top: -100%; }
.cul-food-photo.q3 img { left: -100%; top: -100%; }
.cul-photo-badge {
    position: absolute;
    right: 8px;
    bottom: 8px;
    font-family: 'Cinzel', Georgia, serif;
    font-size: 9px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 3px 7px;
    background: rgba(20, 15, 11, 0.78);
    color: #f3e4be;
    border: 1px solid rgba(205, 176, 110, 0.55);
    border-radius: 2px;
    pointer-events: none;
}

.cul-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 14px;
}
.cul-tag {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10px;
    letter-spacing: 0.05em;
    padding: 3px 8px;
    border-radius: 2px;
    background: rgba(154, 123, 59, 0.14);
    border: 1px solid rgba(154, 123, 59, 0.42);
    color: #4a351d;
}
.cul-tag.price {
    background: rgba(122, 31, 29, 0.1);
    border-color: rgba(122, 31, 29, 0.35);
    color: var(--crimson-dark);
    font-weight: 700;
}
.cul-tag.herb {
    background: rgba(31, 81, 86, 0.1);
    border-color: rgba(31, 81, 86, 0.34);
    color: #1a4347;
}
.cul-tag a {
    color: inherit;
    text-decoration: underline;
    text-decoration-style: dotted;
    text-underline-offset: 2px;
    font-weight: 700;
}
.cul-tag a:hover {
    color: var(--crimson);
    text-decoration-style: solid;
}
.cul-recipe p {
    margin: 0 0 11px;
    font-size: 16.2px;
    line-height: 1.56;
    text-align: left;
}
.cul-recipe p strong {
    color: #5b201b;
}

/* COMPÊNDIO DE ANIMAIS (2 COLUNAS) */
.cul-animals-section {
    margin-top: 38px;
    padding-top: 22px;
    border-top: 2px solid var(--crimson);
    scroll-margin-top: 68px;
}
.cul-animal-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 18px;
    margin: 18px 0 28px;
}
.cul-animal-card {
    padding: 18px 20px;
    background: linear-gradient(180deg, rgba(252, 246, 234, 0.92) 0%, rgba(243, 233, 212, 0.92) 100%);
    border: 1px solid rgba(154, 123, 59, 0.48);
    border-top: 3px solid #1f5156;
    border-radius: 3px;
    box-shadow: 0 4px 14px rgba(42, 26, 12, 0.08);
    scroll-margin-top: 72px;
}
.cul-animal-card h3 {
    font-family: 'Cinzel', Georgia, serif !important;
    font-size: 17px !important;
    color: #1d3c40 !important;
    margin: 0 0 12px !important;
    padding-bottom: 6px;
    border-bottom: 1px dotted rgba(154, 123, 59, 0.45);
}
.cul-animal-plate {
    margin: 0 0 14px !important;
    padding: 5px !important;
    background: #efe3c8 !important;
    border: 1px solid rgba(154, 123, 59, 0.62) !important;
    border-radius: 2px;
    box-shadow: 0 4px 12px rgba(42, 26, 12, 0.12);
    overflow: hidden;
}
.cul-animal-plate img {
    width: 100%;
    height: auto;
    aspect-ratio: 3 / 2;
    object-fit: cover;
    display: block;
    cursor: zoom-in;
    transition: transform 0.24s ease, filter 0.24s ease;
}
.cul-animal-plate:hover img {
    transform: scale(1.015);
    filter: contrast(1.03);
}
.cul-animal-card p {
    font-size: 15px;
    line-height: 1.48;
    margin: 0 0 8px;
    text-align: left;
}
.cul-animal-card p:last-child { margin-bottom: 0; }

.cul-appendix {
    margin-top: 34px;
    padding-top: 20px;
    border-top: 2px solid var(--gold);
}
.cul-appendix h2 { scroll-margin-top: 68px; }

.cul-empty {
    display: none;
    text-align: center;
    padding: 32px 20px;
    border: 1px dashed var(--gold);
    background: rgba(246, 236, 214, 0.72);
    font-style: italic;
    color: var(--ink-soft);
    margin: 16px 0 28px;
}
.cul-empty.visible { display: block; }

@media (max-width: 860px) {
    body.culinaria-mode .book-page { padding: 22px 18px 42px; }
    .cul-hero { grid-template-columns: 1fr; text-align: center; padding: 20px; }
    .cul-hero-cover { max-width: 240px; margin: 0 auto !important; }
    .cul-stats { justify-content: center; }
    .cul-food-photo { float: none; width: 100%; margin: 0 0 16px; }
    .cul-animal-grid { grid-template-columns: 1fr; }
}
@media print {
    .cul-toolbar, .cul-plate-btn, .cul-photo-badge { display: none !important; }
    .cul-recipe { break-inside: avoid; page-break-inside: avoid; }
    .cul-animal-card { break-inside: avoid; page-break-inside: avoid; }
}
"""

CULINARIA_JS = r"""
(function() {
    const root = document.getElementById('culinaria-recipes-root');
    if (!root) return;

    const pills = Array.from(document.querySelectorAll('.cul-pill'));
    const searchEl = document.getElementById('cul-search');
    const countEl = document.getElementById('cul-count');
    const emptyEl = document.getElementById('cul-empty');

    let activeRegion = 'ALL';

    function applyFilter() {
        const q = (searchEl ? searchEl.value : '').trim().toLowerCase();
        let shown = 0;

        document.querySelectorAll('.cul-region').forEach(regEl => {
            const regOk = (activeRegion === 'ALL' || regEl.dataset.region === activeRegion);
            let regShown = 0;
            regEl.querySelectorAll('.cul-recipe').forEach(recEl => {
                const hay = (recEl.dataset.search || '').toLowerCase();
                const match = regOk && (!q || hay.includes(q));
                recEl.classList.toggle('is-hidden', !match);
                if (match) { regShown++; shown++; }
            });
            regEl.classList.toggle('is-hidden', regShown === 0);
        });

        if (countEl) countEl.textContent = `Exibindo ${shown} de 32 pratos`;
        if (emptyEl) emptyEl.classList.toggle('visible', shown === 0);
    }

    pills.forEach(p => {
        p.addEventListener('click', () => {
            activeRegion = p.dataset.region;
            pills.forEach(x => x.classList.toggle('active', x === p));
            applyFilter();
            if (activeRegion !== 'ALL') {
                const target = document.querySelector(`.cul-region[data-region="${activeRegion}"]`);
                if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    if (searchEl) searchEl.addEventListener('input', applyFilter);

    // Open full high-res 4-dish plate in Alenia's built-in lightbox when clicking any dish photo or plate button
    function openPlateLightbox(src) {
        const lb = document.getElementById('atlas-lightbox');
        const lbImg = document.getElementById('atlas-lightbox-img');
        if (lb && lbImg && src) {
            lbImg.src = src;
            lb.classList.add('open');
        }
    }

    document.querySelectorAll('.cul-food-photo, .cul-plate-btn').forEach(el => {
        el.addEventListener('click', () => {
            const src = el.dataset.plateSrc || el.querySelector('img')?.src;
            openPlateLightbox(src);
        });
    });

    // Close sidebar drawer on TOC click
    document.querySelectorAll('.toc-list a').forEach(a => {
        a.addEventListener('click', () => {
            document.body.classList.add('sidebar-hidden');
            document.body.classList.remove('sidebar-open-mobile');
        });
    });
})();
"""


def render_culinaria_page(bk: dict, md_content: str, helpers: dict):
    """Build illustrated Tomo XII — Cozinhas de Alenia page inside Alenia's unified shell."""
    inline_md = helpers["inline_md"]
    md_to_html = helpers["md_to_html"]
    slugify = helpers["slugify"]
    img_dim_attrs = helpers["img_dim_attrs"]

    sections = re.split(r"(?=^##\s+)", md_content, flags=re.M)

    intro_mds = []
    region_secs = []
    animals_sec = None
    appendix_mds = []

    region_short_map = {
        "Aurora e o vale do Aurélio": ("aurora", "Aurora"),
        "Matas silvanas e águas de Vergod": ("silvanos", "Matas Silvanas"),
        "Corallis e o Mar dos Corais": ("corallis", "Corallis"),
        "Gaddra e as mesas de hospitalidade": ("gaddra", "Gaddra"),
        "Kalis e a Floresta Negra": ("kalis", "Kalis"),
        "Ravena e a Ilha das Safiras": ("ilhas", "Ravena & Safiras"),
        "Yõketsu e a costa oriental de Aurora": ("yoketsu", "Yõketsu"),
        "Syleth, Lystra e as provisões do norte": ("norte", "Syleth & Norte"),
    }

    for sec in sections:
        m_h2 = re.match(r"^##\s+(.+)$", sec.strip(), flags=re.M)
        if not m_h2:
            continue
        title = m_h2.group(1).strip()
        if title in (
            "Pratos, ingredientes e animais das terras e dos mares",
            "A tradição de Valerius Malakor",
            "Como ler as fichas",
        ):
            intro_mds.append(sec)
        elif title in region_short_map:
            region_secs.append((title, sec))
        elif title == "Animais das cozinhas de Alenia":
            animals_sec = sec
        else:
            appendix_mds.append(sec)

    toc_items = []
    region_pills = ['<button class="cul-pill active" data-region="ALL" type="button">Todas as Regiões (32)</button>']
    region_blocks_html = []

    for r_idx, (r_title, raw_sec) in enumerate(region_secs, 1):
        r_slug, r_short = region_short_map[r_title]
        r_id = f"regiao-{r_slug}"
        toc_items.append((2, r_title, r_id))
        region_pills.append(
            f'<button class="cul-pill" data-region="{r_slug}" type="button">{html.escape(r_short)} (4)</button>'
        )

        # Extract plate image
        m_img = re.search(r"!\[([^\]]*)\]\(([^)]+)\)", raw_sec)
        plate_src = ("assets/" + os.path.basename(m_img.group(2).strip())) if m_img else ""
        plate_alt = m_img.group(1).strip() if m_img else r_title

        # Split intro vs recipes
        rec_parts = re.split(r"(?=^###\s+C\d{2}\s)", raw_sec, flags=re.M)
        intro_lines = []
        for ln in rec_parts[0].splitlines()[1:]:
            s = ln.strip()
            if not s or s.startswith("![") or s.startswith("Ordem da prancha:"):
                continue
            intro_lines.append(f"<p>{inline_md(s)}</p>")

        recipes_html = []
        for q_idx, rblk in enumerate(rec_parts[1:]):
            lines = [ln.strip() for ln in rblk.strip().splitlines() if ln.strip()]
            if not lines:
                continue
            m_rh = re.match(r"^###\s+(C\d{2})\s+[—–-]\s+(.+)$", lines[0])
            if not m_rh:
                continue
            code = m_rh.group(1)
            dish_name = m_rh.group(2).strip()
            rec_id = code.lower()

            # Parse metadata tags from the 2 metadata lines (**Mesa:**..., **Fauna:**...)
            tags = []
            body_paras = []
            for bl in lines[1:]:
                if bl.startswith("**Mesa:**") or bl.startswith("**Fauna:**"):
                    pairs = re.findall(r"\*\*([^*:]+):\*\*\s*([^.*]+?)(?:\.|$)", bl)
                    for k_lbl, v_lbl in pairs:
                        k_clean = k_lbl.strip()
                        v_clean = v_lbl.strip()
                        if k_clean == "Imagem":
                            continue
                        cls = "cul-tag"
                        val_html = html.escape(v_clean)
                        if "Preço" in k_clean:
                            cls += " price"
                        elif k_clean == "Fauna":
                            cls += " herb"
                            val_html = re.sub(
                                r"\b(A\d{2})\b",
                                lambda m: f'<a href="#{m.group(1).lower()}" title="Ver prancha zoológica {m.group(1)}">{m.group(1)}</a>',
                                val_html,
                            )
                        elif k_clean == "Herbário":
                            cls += " herb"
                        tags.append(f'<span class="{cls}">{html.escape(k_clean)}: {val_html}</span>')
                else:
                    body_paras.append(f"<p>{inline_md(bl)}</p>")

            search_blob = html.escape(
                f"{code} {dish_name} {r_title} {r_short} {' '.join(lines[1:])}",
                quote=True,
            )
            photo_html = ""
            if plate_src:
                photo_html = (
                    f'<figure class="cul-food-photo q{q_idx % 4}" data-plate-src="{html.escape(plate_src, quote=True)}" '
                    f'title="Clique para ampliar a prancha completa ({html.escape(r_short)})">'
                    f'<img src="{html.escape(plate_src, quote=True)}" alt="{html.escape(dish_name)}" loading="lazy"/>'
                    f'<span class="cul-photo-badge">🔍 Prancha {r_idx}</span>'
                    f'</figure>'
                )

            recipes_html.append(f"""
            <article class="cul-recipe" id="{rec_id}" data-search="{search_blob}">
                <div class="cul-recipe-head">
                    <span class="cul-code">{html.escape(code)}</span>
                    <h3 class="cul-recipe-title">{html.escape(dish_name)}</h3>
                </div>
                {photo_html}
                <div class="cul-tags">{"".join(tags)}</div>
                {"".join(body_paras)}
            </article>
            """)

        plate_btn = (
            f'<button class="cul-plate-btn" type="button" data-plate-src="{html.escape(plate_src, quote=True)}">'
            f'🖼 Ver Prancha {r_idx} Completa (4 Pratos)</button>'
            if plate_src else ""
        )

        region_blocks_html.append(f"""
        <section class="cul-region" id="{r_id}" data-region="{r_slug}">
            <header class="cul-region-header">
                <div>
                    <div class="cul-region-kicker">TRADIÇÃO {r_idx} DE 8 • PRANCHA {r_idx}</div>
                    <h2 class="cul-region-title">{html.escape(r_title)}</h2>
                </div>
                {plate_btn}
            </header>
            <div class="cul-region-intro">{"".join(intro_lines)}</div>
            {"".join(recipes_html)}
        </section>
        """)

    # Render collapsible Editorial Intro (3 opening H2 sections)
    intro_html_inner, _ = md_to_html("\n\n".join(intro_mds), id_prefix="intro-", card_h3=False, inject_maps=False)
    intro_box = f"""
    <details class="cul-intro-details">
        <summary>📜 Nota Editorial, Tradição de Valerius Malakor &amp; Como Ler as Fichas</summary>
        <div class="cul-intro-inner">{intro_html_inner}</div>
    </details>
    """

    # Render 22 Animals in a crisp 2-column grid
    animals_html = ""
    if animals_sec:
        an_id = "animais-das-cozinhas"
        toc_items.append((2, "Animais das cozinhas de Alenia (A01–A22)", an_id))
        an_parts = re.split(r"(?=^###\s+A\d{2}\s)", animals_sec, flags=re.M)
        an_intro = "".join(
            f"<p>{inline_md(ln.strip())}</p>"
            for ln in an_parts[0].splitlines()[1:] if ln.strip()
        )
        an_cards = []
        for ablk in an_parts[1:]:
            alines = [ln.strip() for ln in ablk.strip().splitlines() if ln.strip()]
            if not alines:
                continue
            m_ah = re.match(r"^###\s+(A\d{2})\s+[—–-]\s+(.+)$", alines[0])
            if not m_ah:
                continue
            acode, aname = m_ah.group(1), m_ah.group(2).strip()
            aplate_html = ""
            aparas_list = []
            for ln in alines[1:]:
                m_aimg = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", ln)
                if m_aimg:
                    asrc = "assets/" + os.path.basename(m_aimg.group(2).strip())
                    aalt = m_aimg.group(1).strip() or f"{acode} — {aname}"
                    aplate_html = (
                        f'<figure class="atlas-plate cul-animal-plate" '
                        f'title="Clique para ampliar a prancha zoológica de {html.escape(aname, quote=True)}">'
                        f'<img src="{html.escape(asrc, quote=True)}" alt="{html.escape(aalt, quote=True)}"'
                        f'{img_dim_attrs(asrc)} loading="lazy"/>'
                        f'</figure>'
                    )
                else:
                    aparas_list.append(f"<p>{inline_md(ln)}</p>")
            aparas = "".join(aparas_list)
            an_cards.append(
                f'<article class="cul-animal-card" id="{acode.lower()}">'
                f'<h3>{html.escape(acode)} — {html.escape(aname)}</h3>'
                f'{aplate_html}'
                f'{aparas}'
                f'</article>'
            )
        animals_html = f"""
        <section class="cul-animals-section" id="{an_id}">
            <h2>Animais das Cozinhas de Alenia (A01–A22)</h2>
            {an_intro}
            <div class="cul-animal-grid">{"".join(an_cards)}</div>
        </section>
        """

    # Render remaining sections (Despensa, Viagem, Mesas de Campanha, Caderno Antigo, Fontes, Índice Rápido)
    appendix_md = "\n\n".join(appendix_mds)
    # Enhance quick index table dish codes (C01..C32) and animal codes (A01..A22) into clickable anchor links
    appendix_md = re.sub(
        r"^\|\s*(C\d{2})\s*—",
        lambda m: f"| [{m.group(1)}](#{m.group(1).lower()}) —",
        appendix_md,
        flags=re.M,
    )
    appendix_md = re.sub(
        r"\b(A\d{2})\b(?=(?:,\s*A\d{2})*\s*\|)",
        lambda m: f"[{m.group(1)}](#{m.group(1).lower()})",
        appendix_md,
    )
    appendix_html, appendix_toc = md_to_html(appendix_md, id_prefix="cul-", card_h3=False, inject_maps=False)
    toc_items.extend(appendix_toc)

    hero_html = f"""
    <section class="cul-hero">
        <figure class="atlas-plate cul-hero-cover">
            <img src="{bk['cover_map']}" alt="Capa — {html.escape(bk['title'])}"{img_dim_attrs(bk['cover_map'])}/>
        </figure>
        <div>
            <div class="cul-kicker">ALENIA RPG • {html.escape(bk['num'])} • GUIA CULINÁRIO ILUSTRADO</div>
            <h1 class="cul-title">{html.escape(bk['title'])}</h1>
            <p class="cul-sub">Pratos, ingredientes e animais das terras e dos mares — 32 receitas em 8 tradições regionais.</p>
            <blockquote class="cul-epigraph">
                “Uma mesa de Alenia revela quem controla a água, quais barcos chegaram ao porto, que caminhos a neve fechou e quem conseguiu guardar grão para o inverno.”
            </blockquote>
            <div class="cul-stats">
                <span class="cul-stat-pill">🍲 32 Pratos Ilustrados (C01–C32)</span>
                <span class="cul-stat-pill">✦ 8 Tradições Regionais</span>
                <span class="cul-stat-pill teal">🐟 22 Animais Ilustrados (A01–A22)</span>
                <span class="cul-stat-pill teal">🌿 Integrado ao Herbário (H)</span>
            </div>
        </div>
    </section>
    {intro_box}
    <div class="cul-toolbar" role="region" aria-label="Filtros das Cozinhas de Alenia">
        <div class="cul-region-pills">{"".join(region_pills)}</div>
        <div class="cul-search-row">
            <input id="cul-search" class="cul-search" type="search" placeholder="Buscar prato, ingrediente, animal (A01), espécie do Herbário (H24) ou região..." aria-label="Buscar receitas"/>
            <span id="cul-count" class="cul-count">Exibindo 32 de 32 pratos</span>
        </div>
    </div>
    <div id="cul-empty" class="cul-empty">Nenhum prato encontrado para os filtros atuais. Limpe a busca ou selecione “Todas as Regiões”.</div>
    """

    full_body = (
        hero_html
        + f'<div id="culinaria-recipes-root">{"".join(region_blocks_html)}</div>'
        + animals_html
        + f'<section class="cul-appendix">{appendix_html}</section>'
    )
    return full_body, toc_items
