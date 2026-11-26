#!/usr/bin/env python3
"""
Renderizador Editorial Ilustrado do Tomo XIV — Mares, Frotas e Navegação de Alenia
- Painel interativo para as 12 Embarcações (E01–E12) com filtro por porte e busca instantânea
- Painel interativo para o Arsenal Marítimo (M01–M18: arpões, redes, armas de convés e artilharia sem pólvora)
- Regras completas de Fisgada, Enredar, Combate Submerso, Postos de Convés e os 4 Mares
- Caderno Reservado ao Mestre selado em AES-256-GCM (PBKDF2 120k)
- Diagramação @media print A4 calibrada (zero imagens lazy pendentes, 2 navios por folha, arsenal em 2 colunas)
"""
import html
import os
import re

NAVEGACAO_CSS = r"""
/* =====================================================
   TOMO XIV — MARES, FROTAS E NAVEGAÇÃO DE ALENIA
   ===================================================== */
body.navegacao-mode .book-shell {
    padding: 72px 18px 72px;
}
body.navegacao-mode:not(.sidebar-hidden) .sidebar-backdrop {
    display: block;
}
body.navegacao-mode .book-page {
    max-width: 1180px;
    padding: 34px 42px 58px;
    background: radial-gradient(circle at top center, #faf4e6 0%, #f3e9d4 58%, #eadec3 100%);
    box-shadow:
        0 26px 72px rgba(0, 0, 0, 0.7),
        0 0 0 1px rgba(154, 123, 59, 0.45);
}
body.navegacao-mode .book-page::before {
    inset: 10px;
    border: 1px solid rgba(154, 123, 59, 0.34);
}

/* HERO / FRONTISPÍCIO NÁUTICO */
.nav-hero {
    display: grid;
    grid-template-columns: 245px 1fr;
    gap: 28px;
    align-items: center;
    padding: 26px 28px;
    margin-bottom: 22px;
    border: 2px solid #1b4965;
    outline: 1px solid var(--gold);
    outline-offset: -7px;
    background: radial-gradient(circle at 25% 50%, #fcf8ee 0%, #efe3c8 100%);
    box-shadow: 0 10px 26px rgba(24, 34, 42, 0.15);
}
.nav-hero-cover {
    margin: 0 !important;
    padding: 6px !important;
    background: #ede1c4 !important;
    border: 1px solid var(--gold) !important;
}
.nav-hero-cover img {
    width: 100%;
    max-height: 320px;
    object-fit: cover;
    display: block;
    cursor: zoom-in;
}
.nav-kicker {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 11px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #1b4965;
    font-weight: 700;
}
.nav-title {
    font-family: 'Cinzel', Georgia, serif !important;
    font-size: 33px !important;
    line-height: 1.14 !important;
    margin: 6px 0 8px !important;
    color: #1f1710 !important;
    border: none !important;
    padding: 0 !important;
}
.nav-sub {
    font-style: italic;
    font-size: 16.8px;
    color: var(--ink-soft);
    margin: 0 0 12px;
}
.nav-epigraph {
    font-style: italic;
    font-size: 15.2px;
    color: #2f261d;
    border-left: 3px solid #1b4965;
    padding: 7px 14px;
    margin: 0 0 14px;
    background: rgba(27, 73, 101, 0.07);
}
.nav-stats {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}
.nav-stat-pill {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10.2px;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    padding: 5px 10px;
    border-radius: 2px;
    background: rgba(27, 73, 101, 0.10);
    border: 1px solid rgba(27, 73, 101, 0.36);
    color: #163b52;
    font-weight: 600;
}
.nav-stat-pill.crimson {
    background: rgba(122, 31, 29, 0.09);
    border-color: rgba(122, 31, 29, 0.34);
    color: var(--crimson-dark);
}

/* GAVETA EDITORIAL DE ESTALEIROS & ESCALAS */
.nav-editorial {
    margin: 0 0 22px;
    border: 1px solid rgba(154, 123, 59, 0.54);
    background: rgba(246, 236, 214, 0.76);
    border-radius: 3px;
    scroll-margin-top: 72px;
}
.nav-editorial > summary {
    cursor: pointer;
    padding: 11px 18px;
    font-family: 'Cinzel', Georgia, serif;
    font-size: 12.2px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #163b52;
    font-weight: 700;
    list-style: none;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.nav-editorial > summary::-webkit-details-marker { display: none; }
.nav-editorial > summary::after {
    content: "▾ Expandir";
    font-size: 10.5px;
    color: var(--gold);
}
.nav-editorial[open] > summary::after { content: "▴ Recolher"; }
.nav-editorial-inner {
    padding: 6px 22px 18px;
    border-top: 1px solid rgba(154, 123, 59, 0.28);
}

/* BARRAS DE FILTRO E BUSCA (FROTA & ARSENAL) */
.nav-toolbar {
    background: linear-gradient(180deg, rgba(24, 29, 34, 0.97) 0%, rgba(17, 20, 24, 0.97) 100%);
    border: 1px solid rgba(154, 123, 59, 0.65);
    border-radius: 4px;
    padding: 12px 16px;
    margin: 14px 0 26px;
    box-shadow: 0 10px 26px rgba(0, 0, 0, 0.32);
    color: #efe6d2;
}
.nav-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 10px;
}
.nav-pill {
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
.nav-pill:hover {
    border-color: var(--gold-light);
    color: var(--gold-light);
    background: rgba(154, 123, 59, 0.16);
}
.nav-pill.active {
    background: #1b4965;
    border-color: var(--gold-light);
    color: #fff8e6;
    font-weight: 700;
}
.nav-pill.arms-pill.active {
    background: var(--crimson);
}
.nav-search-row {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 10px;
}
.nav-search {
    flex: 1 1 260px;
    min-width: 180px;
    padding: 7px 12px;
    border-radius: 3px;
    border: 1px solid rgba(154, 123, 59, 0.55);
    background: #111518;
    color: #f7f1e3;
    font-family: 'EB Garamond', Georgia, serif;
    font-size: 15.5px;
}
.nav-search::placeholder { color: #9aa0a6; font-style: italic; }
.nav-count {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10.5px;
    letter-spacing: 0.08em;
    color: var(--gold-light);
    white-space: nowrap;
}

/* GRUPOS DE EMBARCAÇÕES & CARTÕES DE NAVIO (E01–E12) */
.nav-fleet-group {
    margin: 0 0 36px;
    scroll-margin-top: 68px;
}
.nav-fleet-group.is-hidden { display: none; }
.nav-group-header {
    padding: 13px 18px;
    margin-bottom: 16px;
    background: linear-gradient(90deg, rgba(27, 73, 101, 0.12) 0%, rgba(154, 123, 59, 0.14) 58%, rgba(27, 73, 101, 0.04) 100%);
    border-top: 2px solid #1b4965;
    border-bottom: 1px solid var(--gold);
    border-left: 4px solid #1b4965;
}
.nav-group-header.crimson {
    background: linear-gradient(90deg, rgba(122, 31, 29, 0.11) 0%, rgba(154, 123, 59, 0.14) 58%, rgba(122, 31, 29, 0.04) 100%);
    border-top-color: var(--crimson);
    border-left-color: var(--crimson);
}
.nav-group-kicker {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #1b4965;
    font-weight: 700;
}
.nav-group-header.crimson .nav-group-kicker { color: var(--crimson); }
.nav-group-title {
    font-family: 'Cinzel', Georgia, serif !important;
    font-size: 23px !important;
    color: #201710 !important;
    margin: 2px 0 0 !important;
    border: none !important;
    padding: 0 !important;
}
.nav-group-intro {
    margin: 0 0 16px;
    font-size: 16.2px;
    color: #2e241b;
}

.nav-ship-card {
    padding: 20px 22px;
    margin-bottom: 18px;
    background: linear-gradient(180deg, rgba(252, 247, 236, 0.95) 0%, rgba(243, 233, 212, 0.95) 100%);
    border: 1px solid rgba(154, 123, 59, 0.5);
    border-left: 4px solid #1b4965;
    border-radius: 3px;
    box-shadow: 0 5px 15px rgba(28, 22, 14, 0.09);
    display: flow-root;
    scroll-margin-top: 74px;
}
.nav-ship-card.is-hidden { display: none; }
.nav-ship-head {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
}
.nav-code {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.1em;
    padding: 3px 9px;
    border-radius: 2px;
    background: #1b4965;
    color: #f7f1e3;
}
.nav-code.arm-code { background: var(--crimson); }
.nav-ship-title {
    font-family: 'Cinzel', Georgia, serif !important;
    font-size: 21.5px !important;
    color: #1f160e !important;
    margin: 0 !important;
    border: none !important;
    padding: 0 !important;
}
.nav-ship-plate {
    float: right;
    width: 43%;
    max-width: 420px;
    margin: 0 0 14px 24px !important;
    padding: 5px !important;
    background: #efe3c8 !important;
    border: 1px solid rgba(154, 123, 59, 0.68) !important;
    border-radius: 2px;
    box-shadow: 0 6px 16px rgba(32, 22, 12, 0.15);
}
.nav-ship-plate img {
    width: 100%;
    height: auto;
    aspect-ratio: 3 / 2;
    object-fit: cover;
    display: block;
    cursor: zoom-in;
}
.nav-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 12px;
}
.nav-tag {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 9.8px;
    letter-spacing: 0.04em;
    padding: 3px 8px;
    border-radius: 2px;
    background: rgba(154, 123, 59, 0.14);
    border: 1px solid rgba(154, 123, 59, 0.42);
    color: #48341c;
}
.nav-tag.price {
    background: rgba(122, 31, 29, 0.10);
    border-color: rgba(122, 31, 29, 0.36);
    color: var(--crimson-dark);
    font-weight: 700;
}
.nav-tag.hull {
    background: rgba(27, 73, 101, 0.11);
    border-color: rgba(27, 73, 101, 0.36);
    color: #14384f;
    font-weight: 700;
}
.nav-ship-card p {
    font-size: 16px;
    line-height: 1.54;
    margin: 0 0 9px;
    text-align: left;
}
.nav-ship-card p:last-child { margin-bottom: 0; }

/* ARSENAL MARÍTIMO E ARTILHARIA (M01–M18) */
.nav-arsenal-group {
    margin: 0 0 36px;
    scroll-margin-top: 68px;
}
.nav-arsenal-group.is-hidden { display: none; }
.nav-arsenal-plate {
    margin: 0 0 18px !important;
    padding: 8px 10px 7px !important;
    background: #efe3c8 !important;
    border: 1px solid var(--gold) !important;
    box-shadow: 0 6px 18px rgba(32, 22, 12, 0.14);
}
.nav-arsenal-plate img {
    width: 100%;
    max-height: 390px;
    object-fit: contain;
    display: block;
    margin: 0 auto;
    cursor: zoom-in;
}
.nav-weapon-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
    margin: 14px 0 22px;
}
.nav-weapon-card {
    padding: 16px 18px;
    background: linear-gradient(180deg, rgba(252, 246, 234, 0.94) 0%, rgba(243, 233, 212, 0.94) 100%);
    border: 1px solid rgba(154, 123, 59, 0.48);
    border-top: 3px solid var(--crimson);
    border-radius: 3px;
    box-shadow: 0 4px 12px rgba(34, 22, 12, 0.08);
    scroll-margin-top: 74px;
}
.nav-weapon-card[data-armcat="engine"] {
    border-top-color: #6b4423;
}
.nav-weapon-card.is-hidden { display: none; }
.nav-weapon-head {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
    padding-bottom: 6px;
    border-bottom: 1px dotted rgba(154, 123, 59, 0.45);
}
.nav-weapon-card h3 {
    font-family: 'Cinzel', Georgia, serif !important;
    font-size: 17px !important;
    color: #24170e !important;
    margin: 0 !important;
    border: none !important;
    padding: 0 !important;
}
.nav-weapon-card p {
    font-size: 15.2px;
    line-height: 1.48;
    margin: 0 0 8px;
    text-align: left;
}
.nav-weapon-card p:last-child { margin-bottom: 0; }
.nav-weapon-card ul {
    margin: 4px 0 8px;
    padding-left: 18px;
    font-size: 14.8px;
}

.nav-section-divider {
    margin-top: 36px;
    padding-top: 22px;
    border-top: 2px solid var(--gold);
    scroll-margin-top: 68px;
}
.nav-empty {
    display: none;
    text-align: center;
    padding: 28px 18px;
    border: 1px dashed var(--gold);
    background: rgba(246, 236, 214, 0.72);
    font-style: italic;
    color: var(--ink-soft);
    margin: 12px 0 24px;
}
.nav-empty.visible { display: block; }

@media screen and (max-width: 860px) {
    body.navegacao-mode .book-page { padding: 22px 18px 42px; }
    .nav-hero { grid-template-columns: 1fr; text-align: center; padding: 20px; }
    .nav-hero-cover { max-width: 230px; margin: 0 auto !important; }
    .nav-stats { justify-content: center; }
    .nav-ship-plate { float: none; width: 100%; max-width: none; margin: 0 0 14px !important; }
    .nav-weapon-grid { grid-template-columns: 1fr; }
}

@media print {
    .nav-toolbar,
    .nav-empty,
    .nav-editorial > summary::after {
        display: none !important;
    }
    .nav-hero {
        grid-template-columns: 165px 1fr !important;
        gap: 18px !important;
        text-align: left !important;
        padding: 16px 20px !important;
        margin-bottom: 14px !important;
        box-shadow: none !important;
        break-inside: avoid;
        page-break-inside: avoid;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }
    .nav-hero-cover { max-width: none !important; margin: 0 !important; }
    .nav-hero-cover img { max-height: 220px !important; object-fit: cover !important; }
    .nav-title { font-size: 20.5pt !important; }
    .nav-sub { font-size: 10.2pt !important; margin-bottom: 8px !important; }
    .nav-epigraph { font-size: 9.6pt !important; padding: 6px 12px !important; margin-bottom: 10px !important; }
    .nav-stats { justify-content: flex-start !important; gap: 6px !important; }
    .nav-stat-pill { font-size: 8pt !important; padding: 3px 8px !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .nav-editorial { margin: 0 0 12px !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .nav-editorial > summary { padding: 8px 14px !important; font-size: 10pt !important; }
    .nav-editorial-inner { padding: 4px 16px 12px !important; font-size: 9.6pt; }
    .nav-fleet-group, .nav-arsenal-group { margin: 0 0 20px !important; }
    .nav-group-header {
        padding: 9px 14px !important;
        margin-bottom: 10px !important;
        break-inside: avoid;
        page-break-inside: avoid;
        break-after: avoid;
        page-break-after: avoid;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }
    .nav-group-title { font-size: 15.5pt !important; }
    .nav-ship-card {
        padding: 11px 14px !important;
        margin-bottom: 10px !important;
        box-shadow: none !important;
        break-inside: avoid;
        page-break-inside: avoid;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }
    .nav-ship-head { margin-bottom: 6px !important; gap: 7px !important; }
    .nav-code { font-size: 8.5pt !important; padding: 2px 6px !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .nav-ship-title { font-size: 13.5pt !important; }
    .nav-ship-plate {
        float: right !important;
        width: 195px !important;
        margin: 0 0 8px 14px !important;
        padding: 3px !important;
        box-shadow: none !important;
    }
    .nav-tags { margin-bottom: 6px !important; gap: 4px !important; }
    .nav-tag {
        font-size: 7.8pt !important;
        padding: 2px 6px !important;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }
    .nav-ship-card p { font-size: 9.5pt !important; line-height: 1.37 !important; margin: 0 0 4.5px !important; }
    .nav-arsenal-plate {
        margin: 0 0 10px !important;
        padding: 5px !important;
        box-shadow: none !important;
        break-inside: avoid;
        page-break-inside: avoid;
    }
    .nav-arsenal-plate img { max-height: 105mm !important; }
    .nav-weapon-grid {
        display: grid !important;
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
        gap: 10px !important;
        margin: 8px 0 14px !important;
    }
    .nav-weapon-card {
        padding: 9px 11px !important;
        box-shadow: none !important;
        break-inside: avoid;
        page-break-inside: avoid;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }
    .nav-weapon-card h3 { font-size: 11.2pt !important; }
    .nav-weapon-card p, .nav-weapon-card ul { font-size: 9pt !important; line-height: 1.35 !important; margin-bottom: 4px !important; }
    .nav-section-divider { margin-top: 18px !important; padding-top: 12px !important; }
}
"""

NAVEGACAO_JS = r"""
(function() {
    const fleetRoot = document.getElementById('nav-fleet-root');
    const armRoot = document.getElementById('nav-arsenal-root');
    if (!fleetRoot && !armRoot) return;

    const norm = (s) => (s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();

    // 1. Fleet Filter
    const shipPills = Array.from(document.querySelectorAll('.nav-ship-pill'));
    const shipSearch = document.getElementById('nav-ship-search');
    const shipCount = document.getElementById('nav-ship-count');
    const shipEmpty = document.getElementById('nav-ship-empty');
    let activeTier = 'ALL';

    function applyShipFilter() {
        if (!fleetRoot) return;
        const q = norm(shipSearch ? shipSearch.value.trim() : '');
        let shown = 0;
        const allCards = fleetRoot.querySelectorAll('.nav-ship-card');
        fleetRoot.querySelectorAll('.nav-fleet-group').forEach(grp => {
            const tierOk = (activeTier === 'ALL' || grp.dataset.tier === activeTier);
            let grpShown = 0;
            grp.querySelectorAll('.nav-ship-card').forEach(card => {
                const match = tierOk && (!q || norm(card.dataset.search).includes(q));
                card.classList.toggle('is-hidden', !match);
                if (match) { grpShown++; shown++; }
            });
            grp.classList.toggle('is-hidden', grpShown === 0);
        });
        if (shipCount) shipCount.textContent = `Exibindo ${shown} de ${allCards.length} embarcações`;
        if (shipEmpty) shipEmpty.classList.toggle('visible', shown === 0);
    }

    shipPills.forEach(p => {
        p.addEventListener('click', () => {
            activeTier = p.dataset.tier;
            shipPills.forEach(x => x.classList.toggle('active', x === p));
            applyShipFilter();
        });
    });
    if (shipSearch) shipSearch.addEventListener('input', applyShipFilter);

    // 2. Arsenal Filter
    const armPills = Array.from(document.querySelectorAll('.nav-arm-pill'));
    const armSearch = document.getElementById('nav-arm-search');
    const armCount = document.getElementById('nav-arm-count');
    const armEmpty = document.getElementById('nav-arm-empty');
    let activeArmCat = 'ALL';

    function applyArmFilter() {
        if (!armRoot) return;
        const q = norm(armSearch ? armSearch.value.trim() : '');
        let shown = 0;
        const allCards = armRoot.querySelectorAll('.nav-weapon-card');
        armRoot.querySelectorAll('.nav-arsenal-group').forEach(grp => {
            let grpShown = 0;
            grp.querySelectorAll('.nav-weapon-card').forEach(card => {
                const catOk = (activeArmCat === 'ALL' || card.dataset.armcat === activeArmCat);
                const match = catOk && (!q || norm(card.dataset.search).includes(q));
                card.classList.toggle('is-hidden', !match);
                if (match) { grpShown++; shown++; }
            });
            grp.classList.toggle('is-hidden', grpShown === 0);
        });
        if (armCount) armCount.textContent = `Exibindo ${shown} de ${allCards.length} itens do arsenal`;
        if (armEmpty) armEmpty.classList.toggle('visible', shown === 0);
    }

    armPills.forEach(p => {
        p.addEventListener('click', () => {
            activeArmCat = p.dataset.armcat;
            armPills.forEach(x => x.classList.toggle('active', x === p));
            applyArmFilter();
        });
    });
    if (armSearch) armSearch.addEventListener('input', applyArmFilter);

    // 3. Auto-reveal hidden ship/weapon when jumping via #eXX or #mXX anchor
    window.aleniaRevealAnchor = function(id) {
        const el = document.getElementById(id);
        if (!el) return;
        if (el.closest('.nav-ship-card.is-hidden') || el.closest('.nav-fleet-group.is-hidden')) {
            activeTier = 'ALL';
            shipPills.forEach(x => x.classList.toggle('active', x.dataset.tier === 'ALL'));
            if (shipSearch) shipSearch.value = '';
            applyShipFilter();
        }
        if (el.closest('.nav-weapon-card.is-hidden') || el.closest('.nav-arsenal-group.is-hidden')) {
            activeArmCat = 'ALL';
            armPills.forEach(x => x.classList.toggle('active', x.dataset.armcat === 'ALL'));
            if (armSearch) armSearch.value = '';
            applyArmFilter();
        }
        const details = el.closest('details');
        if (details && !details.open) details.open = true;
    };

    if (window.location.hash) {
        const hid = decodeURIComponent(window.location.hash.slice(1));
        window.aleniaRevealAnchor(hid);
        const target = document.getElementById(hid);
        if (target) setTimeout(() => target.scrollIntoView({ behavior: 'smooth', block: 'start' }), 80);
    }

    document.querySelectorAll('.toc-list a').forEach(a => {
        a.addEventListener('click', () => {
            document.body.classList.add('sidebar-hidden');
            document.body.classList.remove('sidebar-open-mobile');
        });
    });

    const revealAllForPrint = () => {
        document.querySelectorAll('.nav-fleet-group.is-hidden, .nav-ship-card.is-hidden, .nav-arsenal-group.is-hidden, .nav-weapon-card.is-hidden').forEach(el => {
            el.classList.remove('is-hidden');
        });
        if (shipEmpty) shipEmpty.classList.remove('visible');
        if (armEmpty) armEmpty.classList.remove('visible');
    };
    const restoreAfterPrint = () => {
        applyShipFilter();
        applyArmFilter();
    };
    window.addEventListener('alenia:prepare-print', revealAllForPrint);
    window.addEventListener('beforeprint', revealAllForPrint);
    window.addEventListener('alenia:restore-print', restoreAfterPrint);
    window.addEventListener('afterprint', restoreAfterPrint);
})();
"""


def _parse_bold_pairs(line: str):
    """Extract **Key:** Value pairs from metadata lines separated by periods or bullets."""
    pairs = []
    # Split cleanly around **Label:** markers
    matches = list(re.finditer(r"\*\*([^*:]+):\*\*\s*", line))
    for i, m in enumerate(matches):
        key = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(line)
        val = line[start:end].strip().rstrip(".·").strip()
        if val:
            pairs.append((key, val))
    return pairs


def render_navegacao_page(bk: dict, md_content: str, helpers: dict):
    """Build interactive illustrated Tomo XIV — Mares, Frotas e Navegação page."""
    inline_md = helpers["inline_md"]
    md_to_html = helpers["md_to_html"]
    img_dim_attrs = helpers["img_dim_attrs"]
    make_gm_gate_block = helpers["make_gm_gate_block"]
    render_toc_items = helpers["render_toc_items"]

    sections = re.split(r"(?=^##\s+)", md_content, flags=re.M)

    intro_secs = []
    fleet_secs = []
    tactical_rules_sec = ""
    arsenal_secs = []
    tail_public_secs = []
    gm_sec = ""
    shield_sec = ""

    fleet_tier_map = {
        "Embarcações fluviais e costeiras": ("costeira", "Fluviais & Costeiras", "PORTE I • RIOS, ESTUÁRIOS E RECIFES"),
        "Embarcações médias de travessia e corso": ("media", "Médias & Corso", "PORTE II • TRAVESSIA OCEÂNICA E PATRULHA"),
        "Grandes cascos mercantes e de guerra": ("pesada", "Pesadas & Capitânias", "PORTE III • FROTAS DE ESTADO E ALTO-MAR"),
    }

    arsenal_group_map = {
        "Arpões, lanças navais e hastes de convés": ("arpoes", "ARSENAL MARÍTIMO I • FISGADA E ALCANCE"),
        "Redes de captura, abordagem e armas de marinheiro": ("redes_conves", "ARSENAL MARÍTIMO II • ENREDAR, ABORDAGEM E MERGULHO"),
        "Artilharia de convés e engenhos sem pólvora": ("artilharia", "ARSENAL MARÍTIMO III • ENGENHARIA DE STONEFORGE SEM PÓLVORA"),
    }

    for sec in sections:
        s = sec.strip()
        m_h2 = re.match(r"^##\s+(.+)$", s, flags=re.M)
        if not m_h2:
            continue
        title = m_h2.group(1).strip()
        if title in ("Como ler este manual náutico", "A economia dos estaleiros, fretes e contratos do mar"):
            intro_secs.append(s)
        elif title in fleet_tier_map:
            fleet_secs.append((title, s))
        elif title == "Regras de arpões, redes e combate na água":
            tactical_rules_sec = s
        elif title in arsenal_group_map:
            arsenal_secs.append((title, s))
        elif title.lower().startswith("caderno reservado ao mestre"):
            gm_sec = s
        elif title.startswith("Referência rápida"):
            shield_sec = s
        else:
            tail_public_secs.append(s)

    toc_items = [
        (2, "Guia de Estaleiros, Escalas e Fretes", "guia-estaleiros"),
    ]

    # 1. Collapsible Editorial Intro
    intro_inner, _ = md_to_html("\n\n".join(intro_secs), id_prefix="nav-intro-", card_h3=False, inject_maps=False)
    intro_html = f"""
    <details class="nav-editorial" id="guia-estaleiros">
        <summary>🧭 Escalas Navais, Limiar Estrutural, Estaleiros, Soldos, Fretes &amp; Leis de Salvamento</summary>
        <div class="nav-editorial-inner">{intro_inner}</div>
    </details>
    """

    # 2. Parse & Render 12 Vessels (E01–E12) + Fleet Comparative / Upgrade Tables
    fleet_groups_html = []
    fleet_extra_tables_md = []
    total_ships = 0
    tier_counts = {}

    for f_title, f_raw in fleet_secs:
        tier_slug, tier_short, tier_kicker = fleet_tier_map[f_title]
        grp_id = f"frota-{tier_slug}"
        toc_items.append((2, f_title, grp_id))

        # Separate trailing ### tables (Resumo Comparativo / Melhorias) if attached to last fleet H2
        tail_tables = ""
        if "### Resumo Comparativo" in f_raw:
            f_raw, tail_tables = f_raw.split("### Resumo Comparativo", 1)
            fleet_extra_tables_md.append("### Resumo Comparativo" + tail_tables)

        ship_parts = re.split(r"(?=^###\s+E\d{2}\s)", f_raw, flags=re.M)
        grp_intro = "".join(
            f"<p>{inline_md(ln.strip())}</p>"
            for ln in ship_parts[0].splitlines()[1:]
            if ln.strip()
        )

        ship_cards = []
        for sblk in ship_parts[1:]:
            lines = [ln.strip() for ln in sblk.strip().splitlines() if ln.strip()]
            if not lines:
                continue
            m_sh = re.match(r"^###\s+(E\d{2})\s+[—–-]\s+(.+)$", lines[0])
            if not m_sh:
                continue
            code = m_sh.group(1)
            name = m_sh.group(2).strip()
            total_ships += 1
            tier_counts[tier_slug] = tier_counts.get(tier_slug, 0) + 1

            plate_html = ""
            tags_html = []
            body_paras = []

            for ln in lines[1:]:
                m_img = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", ln)
                if m_img:
                    alt = m_img.group(1).strip() or f"{code} — {name}"
                    src = "assets/" + os.path.basename(m_img.group(2).strip())
                    plate_html = (
                        f'<figure class="atlas-plate nav-ship-plate" title="Clique para ampliar prancha naval de {html.escape(name, quote=True)}">'
                        f'<img src="{html.escape(src, quote=True)}" alt="{html.escape(alt, quote=True)}"{img_dim_attrs(src)} decoding="async"/>'
                        f'</figure>'
                    )
                elif any(ln.startswith(pref) for pref in ("**Porte:**", "**Tripulação:**", "**Casco:**")):
                    for k_lbl, v_lbl in _parse_bold_pairs(ln):
                        cls = "nav-tag"
                        if k_lbl in ("Preço", "Manutenção"):
                            cls += " price"
                        elif k_lbl in ("Casco", "Defesa de Manobra", "Limiar Estrutural"):
                            cls += " hull"
                        tags_html.append(f'<span class="{cls}">{html.escape(k_lbl)}: {inline_md(v_lbl)}</span>')
                else:
                    body_paras.append(f"<p>{inline_md(ln)}</p>")

            search_blob = html.escape(f"{code} {name} {f_title} {' '.join(lines[1:])}", quote=True)
            ship_cards.append(f"""
            <article class="nav-ship-card" id="{code.lower()}" data-search="{search_blob}">
                <div class="nav-ship-head">
                    <span class="nav-code">{html.escape(code)}</span>
                    <h3 class="nav-ship-title">{html.escape(name)}</h3>
                </div>
                {plate_html}
                <div class="nav-tags">{"".join(tags_html)}</div>
                {"".join(body_paras)}
            </article>
            """)

        fleet_groups_html.append(f"""
        <section class="nav-fleet-group" id="{grp_id}" data-tier="{tier_slug}">
            <header class="nav-group-header">
                <div class="nav-group-kicker">{tier_kicker}</div>
                <h2 class="nav-group-title">{html.escape(f_title)}</h2>
            </header>
            <div class="nav-group-intro">{grp_intro}</div>
            {"".join(ship_cards)}
        </section>
        """)

    fleet_tables_html = ""
    if fleet_extra_tables_md:
        ft_html, ft_toc = md_to_html("\n\n".join(fleet_extra_tables_md), id_prefix="nav-tab-", card_h3=False, inject_maps=False)
        fleet_tables_html = f'<div class="nav-section-divider">{ft_html}</div>'
        toc_items.extend(ft_toc)

    # 3. Tactical Harpoon, Net & Underwater Rules
    tactical_html = ""
    if tactical_rules_sec:
        th_inner, th_toc = md_to_html(tactical_rules_sec, id_prefix="nav-reg-", card_h3=False, inject_maps=False)
        tactical_html = f'<section class="nav-section-divider">{th_inner}</section>'
        toc_items.extend(th_toc)

    # 4. Parse & Render Maritime Arsenal & Non-Gunpowder Artillery (M01–M18)
    arsenal_groups_html = []
    total_arms = 0
    arm_cat_counts = {"harpoon": 0, "net": 0, "deck": 0, "engine": 0}

    def classify_arm(code_str: str) -> str:
        num = int(code_str[1:])
        if 1 <= num <= 4:
            return "harpoon"
        if 5 <= num <= 8:
            return "net"
        if 9 <= num <= 12:
            return "deck"
        return "engine"

    for a_title, a_raw in arsenal_secs:
        a_slug, a_kicker = arsenal_group_map[a_title]
        a_id = f"arsenal-{a_slug}"
        toc_items.append((2, a_title, a_id))

        # Separate trailing ### Resumo tables if present
        trailing_summary_md = ""
        if "### Resumo" in a_raw:
            a_raw, trailing_summary_md = a_raw.split("### Resumo", 1)
            trailing_summary_md = "### Resumo" + trailing_summary_md

        m_parts = re.split(r"(?=^###\s+M\d{2}\s)", a_raw, flags=re.M)
        group_plate_html = ""
        group_intro_paras = []
        for ln in m_parts[0].splitlines()[1:]:
            s = ln.strip()
            if not s:
                continue
            m_pimg = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", s)
            if m_pimg:
                palt = m_pimg.group(1).strip() or a_title
                psrc = "assets/" + os.path.basename(m_pimg.group(2).strip())
                group_plate_html = (
                    f'<figure class="atlas-plate nav-arsenal-plate" title="Clique para ampliar prancha técnica">'
                    f'<img src="{html.escape(psrc, quote=True)}" alt="{html.escape(palt, quote=True)}"{img_dim_attrs(psrc)} decoding="async"/>'
                    f'<figcaption class="atlas-caption">{html.escape(palt)}</figcaption>'
                    f'</figure>'
                )
            else:
                group_intro_paras.append(f"<p>{inline_md(s)}</p>")

        w_cards = []
        for wblk in m_parts[1:]:
            wlines = [ln.strip() for ln in wblk.strip().splitlines() if ln.strip()]
            if not wlines:
                continue
            m_wh = re.match(r"^###\s+(M\d{2})\s+[—–-]\s+(.+)$", wlines[0])
            if not m_wh:
                continue
            wcode = m_wh.group(1)
            wname = m_wh.group(2).strip()
            total_arms += 1

            arm_cat = classify_arm(wcode)
            arm_cat_counts[arm_cat] = arm_cat_counts.get(arm_cat, 0) + 1

            wtags = []
            body_md_lines = []
            for idx_l, wl in enumerate(wlines[1:]):
                if idx_l == 0 and (wl.startswith("**Categoria:**") or wl.startswith("**Slot:**")):
                    for k_lbl, v_lbl in _parse_bold_pairs(wl):
                        cls = "nav-tag"
                        if k_lbl == "Preço":
                            cls += " price"
                        elif k_lbl in ("Dano", "Alcance", "Alcance Naval", "Slot"):
                            cls += " hull"
                        wtags.append(f'<span class="{cls}">{html.escape(k_lbl)}: {inline_md(v_lbl)}</span>')
                else:
                    body_md_lines.append(wl)

            wbody_html, _ = md_to_html("\n\n".join(body_md_lines), id_prefix=f"w-{wcode.lower()}-", card_h3=False, inject_maps=False)
            wsearch = html.escape(f"{wcode} {wname} {a_title} {' '.join(wlines[1:])}", quote=True)
            w_cards.append(f"""
            <article class="nav-weapon-card" id="{wcode.lower()}" data-armcat="{arm_cat}" data-search="{wsearch}">
                <div class="nav-weapon-head">
                    <span class="nav-code arm-code">{html.escape(wcode)}</span>
                    <h3>{html.escape(wname)}</h3>
                </div>
                <div class="nav-tags">{"".join(wtags)}</div>
                {wbody_html}
            </article>
            """)

        summary_tbl_html = ""
        if trailing_summary_md:
            summary_tbl_html, _ = md_to_html(trailing_summary_md, id_prefix=f"sum-{a_slug}-", card_h3=False, inject_maps=False)

        arsenal_groups_html.append(f"""
        <section class="nav-arsenal-group" id="{a_id}">
            <header class="nav-group-header crimson">
                <div class="nav-group-kicker">{a_kicker}</div>
                <h2 class="nav-group-title">{html.escape(a_title)}</h2>
            </header>
            {"".join(group_intro_paras)}
            {group_plate_html}
            <div class="nav-weapon-grid">{"".join(w_cards)}</div>
            {summary_tbl_html}
        </section>
        """)

    # 5. Naval Combat by Deck Stations & The Four Seas
    tail_html = ""
    if tail_public_secs:
        t_inner, t_toc = md_to_html("\n\n".join(tail_public_secs), id_prefix="nav-mar-", card_h3=False, inject_maps=False)
        tail_html = f'<section class="nav-section-divider">{t_inner}</section>'
        toc_items.extend(t_toc)

    # 6. Encrypted GM Vault ("Caderno reservado ao mestre")
    gm_html = ""
    if gm_sec:
        gm_rendered, gm_toc = md_to_html(gm_sec, id_prefix="nav-gm-", card_h3=False, inject_maps=False)
        gm_html = (
            '<div class="nav-section-divider">'
            + make_gm_gate_block(
                "Caderno Reservado ao Mestre — Segredos dos Mares",
                "Esta seção contém embarcações reservadas, naufrágios disputados e segredos de campanha exclusivos do Mestre. Insira a senha para revelar.",
                gm_rendered,
                render_toc_items(gm_toc),
                codex_file=bk["out"],
                compendium_mode=False,
            )
            + '</div>'
        )

    # 7. Public Quick-Reference Shield Table
    shield_html = ""
    if shield_sec:
        sh_inner, sh_toc = md_to_html(shield_sec, id_prefix="nav-escudo-", card_h3=False, inject_maps=False)
        shield_html = f'<section class="nav-section-divider">{sh_inner}</section>'
        toc_items.extend(sh_toc)

    # Toolbars
    ship_toolbar = f"""
    <div class="nav-toolbar" role="region" aria-label="Filtros de Embarcações de Alenia">
        <div class="nav-pills">
            <button class="nav-pill nav-ship-pill active" data-tier="ALL" type="button">Todas as Embarcações ({total_ships})</button>
            <button class="nav-pill nav-ship-pill" data-tier="costeira" type="button">Fluviais &amp; Costeiras ({tier_counts.get('costeira', 0)})</button>
            <button class="nav-pill nav-ship-pill" data-tier="media" type="button">Médias &amp; Corso ({tier_counts.get('media', 0)})</button>
            <button class="nav-pill nav-ship-pill" data-tier="pesada" type="button">Pesadas &amp; Capitânias ({tier_counts.get('pesada', 0)})</button>
        </div>
        <div class="nav-search-row">
            <input id="nav-ship-search" class="nav-search" type="search" placeholder="Buscar navio, código (E05), região (Corallis, Kalis, Yõketsu), preço ou carga..." aria-label="Buscar embarcações"/>
            <span id="nav-ship-count" class="nav-count">Exibindo {total_ships} de {total_ships} embarcações</span>
        </div>
    </div>
    <div id="nav-ship-empty" class="nav-empty">Nenhuma embarcação corresponde aos filtros atuais. Selecione “Todas as Embarcações” ou limpe a busca.</div>
    """

    arm_toolbar = f"""
    <div class="nav-toolbar" role="region" aria-label="Filtros do Arsenal Marítimo">
        <div class="nav-pills">
            <button class="nav-pill arms-pill nav-arm-pill active" data-armcat="ALL" type="button">Todo o Arsenal ({total_arms})</button>
            <button class="nav-pill arms-pill nav-arm-pill" data-armcat="harpoon" type="button">Arpões &amp; Hastes ({arm_cat_counts.get('harpoon', 0)})</button>
            <button class="nav-pill arms-pill nav-arm-pill" data-armcat="net" type="button">Redes Táticas ({arm_cat_counts.get('net', 0)})</button>
            <button class="nav-pill arms-pill nav-arm-pill" data-armcat="deck" type="button">Convés &amp; Mergulho ({arm_cat_counts.get('deck', 0)})</button>
            <button class="nav-pill arms-pill nav-arm-pill" data-armcat="engine" type="button">Artilharia Sem Pólvora ({arm_cat_counts.get('engine', 0)})</button>
        </div>
        <div class="nav-search-row">
            <input id="nav-arm-search" class="nav-search" type="search" placeholder="Buscar arpão, rede (M06), balista (M15), preço, dano ou propriedade (Fisgada, Enredado)..." aria-label="Buscar armas marítimas"/>
            <span id="nav-arm-count" class="nav-count">Exibindo {total_arms} de {total_arms} itens do arsenal</span>
        </div>
    </div>
    <div id="nav-arm-empty" class="nav-empty">Nenhuma arma ou engenho corresponde aos filtros atuais. Selecione “Todo o Arsenal” ou limpe a busca.</div>
    """

    hero_html = f"""
    <section class="nav-hero">
        <figure class="atlas-plate nav-hero-cover">
            <img src="{bk['cover_map']}" alt="Capa — {html.escape(bk['title'])}"{img_dim_attrs(bk['cover_map'])} decoding="async"/>
        </figure>
        <div>
            <div class="nav-kicker">ALENIA RPG • {html.escape(bk['num'])} • MANUAL DOS MARES E ESTALEIROS</div>
            <h1 class="nav-title">{html.escape(bk['title'])}</h1>
            <p class="nav-sub">Estaleiros, preços no Padrão Prata, arpões, redes de combate, artilharia sem pólvora, postos de convés e perigos das águas (Ano 418 EF).</p>
            <blockquote class="nav-epigraph">
                “Em terra firme, um senhor mede seu poder pelos muros que ergue; no mar, mede-se pela madeira que não apodrece, pelo cabo que não parte na tempestade e pela mão que sabe largar o ferro antes de rasgar a quilha.”
            </blockquote>
            <div class="nav-stats">
                <span class="nav-stat-pill">⛵ {total_ships} Embarcações Ilustradas (E01–E{total_ships:02d})</span>
                <span class="nav-stat-pill crimson">⚓ {total_arms} Arpões, Redes &amp; Engenhos (M01–M{total_arms:02d})</span>
                <span class="nav-stat-pill">🧭 5 Postos de Convés</span>
                <span class="nav-stat-pill crimson">🔒 Caderno do Mestre Selado</span>
            </div>
        </div>
    </section>
    """

    full_body = (
        hero_html
        + intro_html
        + ship_toolbar
        + f'<div id="nav-fleet-root">{"".join(fleet_groups_html)}</div>'
        + fleet_tables_html
        + tactical_html
        + '<div class="nav-section-divider">'
        + arm_toolbar
        + f'<div id="nav-arsenal-root">{"".join(arsenal_groups_html)}</div>'
        + '</div>'
        + tail_html
        + gm_html
        + shield_html
    )
    return full_body, toc_items
