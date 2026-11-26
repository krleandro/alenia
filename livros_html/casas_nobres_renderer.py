#!/usr/bin/env python3
"""
Renderizador Editorial Ilustrado do Tomo XV — Casas Nobres, Feudos e Fortificações de Alenia
- Calculadora Interativa de Casa Nobre & Feudo (Custo Novo vs. Reforma de Ruína 45%, Slots de Defesa e Obra,
  Sinergias de Senescal/Aldeia/Moinho/Pedreira/Forja/Coudelaria, Folha Mensal, Saldo Líquido e exportação de Carta de Feudo)
- Painéis filtráveis para Fortificações (F01–F10), Defesas e Obras (D01–D16) e Guarnição e Corte (G01–G14)
- Caderno Reservado ao Mestre selado em AES-256-GCM (PBKDF2 120k)
- Diagramação @media print A4 calibrada (oculta a calculadora na impressão, 2 fortificações por folha, grades em 2 colunas)
"""
import html
import os
import re

CASAS_NOBRES_CSS = r"""
/* =====================================================
   TOMO XV — CASAS NOBRES, FEUDOS E FORTIFICAÇÕES
   ===================================================== */
body.casas-mode .book-shell {
    padding: 72px 18px 72px;
}
body.casas-mode:not(.sidebar-hidden) .sidebar-backdrop {
    display: block;
}
body.casas-mode .book-page {
    max-width: 1180px;
    padding: 34px 42px 58px;
    background: radial-gradient(circle at top center, #faf4e6 0%, #f3e9d4 58%, #eadec3 100%);
    box-shadow:
        0 26px 72px rgba(0, 0, 0, 0.7),
        0 0 0 1px rgba(154, 123, 59, 0.45);
}
body.casas-mode .book-page::before {
    inset: 10px;
    border: 1px solid rgba(154, 123, 59, 0.34);
}

/* HERO / FRONTISPÍCIO SENHORIAL */
.casas-hero {
    display: grid;
    grid-template-columns: 245px 1fr;
    gap: 28px;
    align-items: center;
    padding: 26px 28px;
    margin-bottom: 22px;
    border: 2px solid var(--crimson);
    outline: 1px solid var(--gold);
    outline-offset: -7px;
    background: radial-gradient(circle at 25% 50%, #fcf8ee 0%, #f1e4c9 100%);
    box-shadow: 0 10px 26px rgba(42, 26, 12, 0.15);
}
.casas-hero-cover {
    margin: 0 !important;
    padding: 6px !important;
    background: #ede1c4 !important;
    border: 1px solid var(--gold) !important;
}
.casas-hero-cover img {
    width: 100%;
    max-height: 320px;
    object-fit: cover;
    display: block;
    cursor: zoom-in;
}
.casas-kicker {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 11px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--crimson);
    font-weight: 700;
}
.casas-title {
    font-family: 'Cinzel', Georgia, serif !important;
    font-size: 32px !important;
    line-height: 1.14 !important;
    margin: 6px 0 8px !important;
    color: #21160d !important;
    border: none !important;
    padding: 0 !important;
}
.casas-sub {
    font-style: italic;
    font-size: 16.8px;
    color: var(--ink-soft);
    margin: 0 0 12px;
}
.casas-epigraph {
    font-style: italic;
    font-size: 15.2px;
    color: #36281b;
    border-left: 3px solid var(--crimson);
    padding: 7px 14px;
    margin: 0 0 14px;
    background: rgba(122, 31, 29, 0.06);
}
.casas-stats {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}
.casas-stat-pill {
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
.casas-stat-pill.slate {
    background: rgba(54, 69, 79, 0.11);
    border-color: rgba(54, 69, 79, 0.36);
    color: #26343d;
}

/* GAVETA DE FUNDAÇÃO & HERÁLDICA */
.casas-editorial {
    margin: 0 0 22px;
    border: 1px solid rgba(154, 123, 59, 0.54);
    background: rgba(246, 236, 214, 0.78);
    border-radius: 3px;
    scroll-margin-top: 72px;
}
.casas-editorial > summary {
    cursor: pointer;
    padding: 11px 18px;
    font-family: 'Cinzel', Georgia, serif;
    font-size: 12.2px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--crimson-dark);
    font-weight: 700;
    list-style: none;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.casas-editorial > summary::-webkit-details-marker { display: none; }
.casas-editorial > summary::after {
    content: "▾ Expandir";
    font-size: 10.5px;
    color: var(--gold);
}
.casas-editorial[open] > summary::after { content: "▴ Recolher"; }
.casas-editorial-inner {
    padding: 8px 22px 18px;
    border-top: 1px solid rgba(154, 123, 59, 0.28);
}

/* =====================================================
   CALCULADORA INTERATIVA DE CASA NOBRE & FEUDO
   ===================================================== */
.feudo-calc-wrap {
    margin: 0 0 32px;
    border: 2px solid var(--gold);
    outline: 1px solid rgba(122, 31, 29, 0.4);
    outline-offset: -5px;
    border-radius: 4px;
    background: linear-gradient(180deg, #1d1814 0%, #14110e 100%);
    color: #efe6d2;
    box-shadow: 0 14px 34px rgba(0, 0, 0, 0.42);
    padding: 20px 22px 22px;
    scroll-margin-top: 70px;
}
.feudo-calc-head {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding-bottom: 12px;
    margin-bottom: 16px;
    border-bottom: 1px solid rgba(154, 123, 59, 0.35);
}
.feudo-calc-kicker {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--gold-light);
    font-weight: 700;
}
.feudo-calc-title {
    font-family: 'Cinzel', Georgia, serif !important;
    font-size: 21px !important;
    color: #f9f2e3 !important;
    margin: 2px 0 0 !important;
    border: none !important;
    padding: 0 !important;
}
.feudo-presets {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}
.feudo-btn {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 6px 11px;
    border-radius: 3px;
    border: 1px solid rgba(154, 123, 59, 0.55);
    background: #2b221a;
    color: #f3e6ca;
    cursor: pointer;
    transition: all 0.14s ease;
}
.feudo-btn:hover {
    background: var(--crimson);
    border-color: var(--gold-light);
    color: #fff;
}
.feudo-btn.primary {
    background: var(--crimson);
    border-color: var(--gold);
    color: #fff8e6;
    font-weight: 700;
}
.feudo-btn.primary:hover { background: #962724; }

.feudo-identity-row {
    display: grid;
    grid-template-columns: 1.2fr 1fr 1.4fr;
    gap: 12px;
    margin-bottom: 14px;
}
.feudo-field {
    display: flex;
    flex-direction: column;
    gap: 4px;
}
.feudo-field label {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 9.8px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--gold-light);
}
.feudo-field input,
.feudo-field select {
    padding: 7px 10px;
    border-radius: 3px;
    border: 1px solid rgba(154, 123, 59, 0.52);
    background: #100d0a;
    color: #f7f1e3;
    font-family: 'EB Garamond', Georgia, serif;
    font-size: 15.5px;
    width: 100%;
}
.feudo-culture-hint {
    font-size: 13.5px;
    font-style: italic;
    color: #c8bda6;
    margin: -4px 0 14px;
}

.feudo-seat-bar {
    display: grid;
    grid-template-columns: 1.6fr 1fr;
    gap: 12px;
    padding: 12px 14px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(154, 123, 59, 0.34);
    border-radius: 3px;
    margin-bottom: 16px;
}

.feudo-columns {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 14px;
    margin-bottom: 16px;
}
.feudo-panel {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(154, 123, 59, 0.34);
    border-radius: 3px;
    padding: 11px 12px;
    display: flex;
    flex-direction: column;
}
.feudo-panel-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 6px;
    padding-bottom: 7px;
    margin-bottom: 8px;
    border-bottom: 1px solid rgba(154, 123, 59, 0.28);
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10.5px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--gold-light);
    font-weight: 700;
}
.feudo-slot-badge {
    font-size: 9.8px;
    padding: 2px 7px;
    border-radius: 2px;
    background: rgba(31, 81, 86, 0.35);
    border: 1px solid rgba(121, 184, 190, 0.45);
    color: #d8f1f3;
}
.feudo-slot-badge.over {
    background: rgba(150, 39, 36, 0.55);
    border-color: #f08a84;
    color: #ffe5e2;
}
.feudo-item-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
    max-height: 310px;
    overflow-y: auto;
    padding-right: 3px;
}
.feudo-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    padding: 5px 7px;
    background: rgba(14, 11, 9, 0.65);
    border: 1px solid rgba(154, 123, 59, 0.22);
    border-radius: 2px;
    font-size: 14px;
}
.feudo-row-info {
    min-width: 0;
    flex: 1 1 auto;
}
.feudo-row-name {
    display: block;
    color: #f5ecda;
    font-weight: 600;
    line-height: 1.2;
}
.feudo-row-sub {
    display: block;
    font-size: 12px;
    color: #b5a992;
}
.feudo-stepper {
    display: flex;
    align-items: center;
    gap: 4px;
    flex-shrink: 0;
}
.feudo-step-btn {
    width: 24px;
    height: 24px;
    border-radius: 2px;
    border: 1px solid rgba(154, 123, 59, 0.5);
    background: #261e17;
    color: #f7f1e3;
    font-weight: 700;
    cursor: pointer;
    line-height: 1;
    padding: 0;
}
.feudo-step-btn:hover { background: var(--crimson); }
.feudo-qty {
    min-width: 22px;
    text-align: center;
    font-family: 'Cinzel', Georgia, serif;
    font-size: 12px;
    font-weight: 700;
    color: var(--gold-light);
}

.feudo-summary-board {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 10px;
    padding-top: 12px;
    border-top: 1px solid rgba(154, 123, 59, 0.35);
}
.feudo-metric {
    background: rgba(12, 10, 8, 0.82);
    border: 1px solid rgba(154, 123, 59, 0.42);
    border-radius: 3px;
    padding: 10px 12px;
}
.feudo-metric-lbl {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 9.5px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #bfb39c;
}
.feudo-metric-val {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 18px;
    font-weight: 700;
    color: #f9f0dc;
    margin: 3px 0 2px;
}
.feudo-metric-val.positive { color: #7fe0a4; }
.feudo-metric-val.negative { color: #f58d86; }
.feudo-metric-sub {
    font-size: 12.5px;
    color: #b7ab95;
    line-height: 1.25;
}
.feudo-copy-feedback {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10.5px;
    color: #7fe0a4;
    margin-left: 8px;
}

/* BARRAS DE FILTRO E CARTÕES DO CATÁLOGO */
.casas-toolbar {
    background: linear-gradient(180deg, rgba(31, 24, 18, 0.97) 0%, rgba(21, 16, 12, 0.97) 100%);
    border: 1px solid rgba(154, 123, 59, 0.65);
    border-radius: 4px;
    padding: 12px 16px;
    margin: 14px 0 26px;
    box-shadow: 0 10px 26px rgba(0, 0, 0, 0.32);
    color: #efe6d2;
}
.casas-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 10px;
}
.casas-pill {
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
.casas-pill:hover {
    border-color: var(--gold-light);
    color: var(--gold-light);
    background: rgba(154, 123, 59, 0.16);
}
.casas-pill.active {
    background: var(--crimson);
    border-color: var(--gold-light);
    color: #fff8e6;
    font-weight: 700;
}
.casas-search-row {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 10px;
}
.casas-search {
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
.casas-search::placeholder { color: #9c8f7a; font-style: italic; }
.casas-count {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10.5px;
    letter-spacing: 0.08em;
    color: var(--gold-light);
    white-space: nowrap;
}

.casas-group {
    margin: 0 0 36px;
    scroll-margin-top: 68px;
}
.casas-group.is-hidden { display: none; }
.casas-group-header {
    padding: 13px 18px;
    margin-bottom: 16px;
    background: linear-gradient(90deg, rgba(122, 31, 29, 0.11) 0%, rgba(154, 123, 59, 0.14) 58%, rgba(122, 31, 29, 0.04) 100%);
    border-top: 2px solid var(--crimson);
    border-bottom: 1px solid var(--gold);
    border-left: 4px solid var(--crimson);
}
.casas-group-header.slate {
    background: linear-gradient(90deg, rgba(46, 62, 72, 0.12) 0%, rgba(154, 123, 59, 0.14) 58%, rgba(46, 62, 72, 0.04) 100%);
    border-top-color: #2e3e48;
    border-left-color: #2e3e48;
}
.casas-group-kicker {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--crimson);
    font-weight: 700;
}
.casas-group-header.slate .casas-group-kicker { color: #2e3e48; }
.casas-group-title {
    font-family: 'Cinzel', Georgia, serif !important;
    font-size: 23px !important;
    color: #201710 !important;
    margin: 2px 0 0 !important;
    border: none !important;
    padding: 0 !important;
}

/* CARTÕES DE FORTIFICAÇÃO (F01–F10) */
.casas-fort-card {
    padding: 20px 22px;
    margin-bottom: 18px;
    background: linear-gradient(180deg, rgba(252, 247, 236, 0.95) 0%, rgba(243, 233, 212, 0.95) 100%);
    border: 1px solid rgba(154, 123, 59, 0.5);
    border-left: 4px solid var(--crimson);
    border-radius: 3px;
    box-shadow: 0 5px 15px rgba(28, 22, 14, 0.09);
    display: flow-root;
    scroll-margin-top: 74px;
}
.casas-fort-card.is-hidden { display: none; }
.casas-fort-head {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
}
.casas-code {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.1em;
    padding: 3px 9px;
    border-radius: 2px;
    background: var(--crimson);
    color: #f7f1e3;
}
.casas-code.work-code { background: #2e5a44; }
.casas-code.def-code { background: #2e3e48; }
.casas-code.unit-code { background: #6b4423; }
.casas-fort-title {
    font-family: 'Cinzel', Georgia, serif !important;
    font-size: 21.5px !important;
    color: #1f160e !important;
    margin: 0 !important;
    border: none !important;
    padding: 0 !important;
}
.casas-fort-plate {
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
.casas-fort-plate img {
    width: 100%;
    height: auto;
    aspect-ratio: 3 / 2;
    object-fit: cover;
    display: block;
    cursor: zoom-in;
}
.casas-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 12px;
}
.casas-tag {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 9.8px;
    letter-spacing: 0.04em;
    padding: 3px 8px;
    border-radius: 2px;
    background: rgba(154, 123, 59, 0.14);
    border: 1px solid rgba(154, 123, 59, 0.42);
    color: #48341c;
}
.casas-tag.price {
    background: rgba(122, 31, 29, 0.10);
    border-color: rgba(122, 31, 29, 0.36);
    color: var(--crimson-dark);
    font-weight: 700;
}
.casas-tag.income {
    background: rgba(34, 96, 62, 0.12);
    border-color: rgba(34, 96, 62, 0.38);
    color: #18492e;
    font-weight: 700;
}
.casas-tag.siege {
    background: rgba(46, 62, 72, 0.12);
    border-color: rgba(46, 62, 72, 0.38);
    color: #213038;
    font-weight: 700;
}
.casas-fort-card p {
    font-size: 16px;
    line-height: 1.54;
    margin: 0 0 9px;
    text-align: left;
}
.casas-fort-card p:last-child { margin-bottom: 0; }

/* GRADES 2 COLUNAS (D01–D16 & G01–G14) */
.casas-wide-plate {
    margin: 0 0 18px !important;
    padding: 8px 10px 7px !important;
    background: #efe3c8 !important;
    border: 1px solid var(--gold) !important;
    box-shadow: 0 6px 18px rgba(32, 22, 12, 0.14);
}
.casas-wide-plate img {
    width: 100%;
    max-height: 390px;
    object-fit: contain;
    display: block;
    margin: 0 auto;
    cursor: zoom-in;
}
.casas-card-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
    margin: 14px 0 22px;
}
.casas-item-card {
    padding: 16px 18px;
    background: linear-gradient(180deg, rgba(252, 246, 234, 0.94) 0%, rgba(243, 233, 212, 0.94) 100%);
    border: 1px solid rgba(154, 123, 59, 0.48);
    border-top: 3px solid #2e3e48;
    border-radius: 3px;
    box-shadow: 0 4px 12px rgba(34, 22, 12, 0.08);
    scroll-margin-top: 74px;
}
.casas-item-card[data-kind="obra"] { border-top-color: #2e5a44; }
.casas-item-card[data-kind="tropa"] { border-top-color: var(--crimson); }
.casas-item-card[data-kind="corte"] { border-top-color: #6b4423; }
.casas-item-card.is-hidden { display: none; }
.casas-item-head {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
    padding-bottom: 6px;
    border-bottom: 1px dotted rgba(154, 123, 59, 0.45);
}
.casas-item-card h3 {
    font-family: 'Cinzel', Georgia, serif !important;
    font-size: 17px !important;
    color: #24170e !important;
    margin: 0 !important;
    border: none !important;
    padding: 0 !important;
}
.casas-item-card p {
    font-size: 15.2px;
    line-height: 1.48;
    margin: 0 0 8px;
    text-align: left;
}
.casas-item-card p:last-child { margin-bottom: 0; }

.casas-divider {
    margin-top: 36px;
    padding-top: 22px;
    border-top: 2px solid var(--gold);
    scroll-margin-top: 68px;
}
.casas-empty {
    display: none;
    text-align: center;
    padding: 28px 18px;
    border: 1px dashed var(--gold);
    background: rgba(246, 236, 214, 0.72);
    font-style: italic;
    color: var(--ink-soft);
    margin: 12px 0 24px;
}
.casas-empty.visible { display: block; }

@media screen and (max-width: 920px) {
    body.casas-mode .book-page { padding: 22px 18px 42px; }
    .casas-hero { grid-template-columns: 1fr; text-align: center; padding: 20px; }
    .casas-hero-cover { max-width: 230px; margin: 0 auto !important; }
    .casas-stats { justify-content: center; }
    .feudo-identity-row,
    .feudo-seat-bar,
    .feudo-columns { grid-template-columns: 1fr; }
    .feudo-summary-board { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .casas-fort-plate { float: none; width: 100%; max-width: none; margin: 0 0 14px !important; }
    .casas-card-grid { grid-template-columns: 1fr; }
}

@media print {
    .feudo-calc-wrap,
    .casas-toolbar,
    .casas-empty,
    .casas-editorial > summary::after {
        display: none !important;
    }
    .casas-hero {
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
    .casas-hero-cover { max-width: none !important; margin: 0 !important; }
    .casas-hero-cover img { max-height: 220px !important; object-fit: cover !important; }
    .casas-title { font-size: 20.5pt !important; }
    .casas-sub { font-size: 10.2pt !important; margin-bottom: 8px !important; }
    .casas-epigraph { font-size: 9.6pt !important; padding: 6px 12px !important; margin-bottom: 10px !important; }
    .casas-stats { justify-content: flex-start !important; gap: 6px !important; }
    .casas-stat-pill { font-size: 8pt !important; padding: 3px 8px !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .casas-editorial { margin: 0 0 12px !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .casas-editorial > summary { padding: 8px 14px !important; font-size: 10pt !important; }
    .casas-editorial-inner { padding: 4px 16px 12px !important; font-size: 9.6pt; }
    .casas-group { margin: 0 0 20px !important; }
    .casas-group-header {
        padding: 9px 14px !important;
        margin-bottom: 10px !important;
        break-inside: avoid;
        page-break-inside: avoid;
        break-after: avoid;
        page-break-after: avoid;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }
    .casas-group > p:first-of-type {
        break-after: avoid;
        page-break-after: avoid;
    }
    .casas-group-title { font-size: 15.5pt !important; }
    .casas-fort-card {
        padding: 11px 14px !important;
        margin-bottom: 10px !important;
        box-shadow: none !important;
        break-inside: avoid;
        page-break-inside: avoid;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }
    .casas-fort-head { margin-bottom: 6px !important; gap: 7px !important; }
    .casas-code { font-size: 8.5pt !important; padding: 2px 6px !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .casas-fort-title { font-size: 13.5pt !important; }
    .casas-fort-plate {
        float: right !important;
        width: 195px !important;
        margin: 0 0 8px 14px !important;
        padding: 3px !important;
        box-shadow: none !important;
    }
    .casas-tags { margin-bottom: 6px !important; gap: 4px !important; }
    .casas-tag {
        font-size: 7.8pt !important;
        padding: 2px 6px !important;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }
    .casas-fort-card p { font-size: 9.5pt !important; line-height: 1.37 !important; margin: 0 0 4.5px !important; }
    .casas-wide-plate {
        margin: 0 0 10px !important;
        padding: 5px !important;
        box-shadow: none !important;
        break-inside: avoid;
        page-break-inside: avoid;
    }
    .casas-wide-plate img { max-height: 105mm !important; }
    .casas-card-grid {
        display: grid !important;
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
        gap: 10px !important;
        margin: 8px 0 14px !important;
    }
    .casas-item-card {
        padding: 9px 11px !important;
        box-shadow: none !important;
        break-inside: avoid;
        page-break-inside: avoid;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }
    .casas-item-card h3 { font-size: 11.2pt !important; }
    .casas-item-card p { font-size: 9pt !important; line-height: 1.35 !important; margin-bottom: 4px !important; }
    .casas-divider { margin-top: 18px !important; padding-top: 12px !important; }
}
"""

CASAS_NOBRES_JS = r"""
(function() {
    const STORAGE_KEY = 'alenia_feudo_calc_v1';

    const CULTURES = {
        aurora: "Fórmula: Casa de/d' [Terra] ou -ion/-aris (ex.: Casa de Specula) • Bastardos: Cinza • Legitimidade: Foral Real ou Grande Casa.",
        corallis: "Fórmula: Família dal/della [Marco] ou -i (ex.: Casa della Torre) • Bastardos: Coral • Legitimidade: Câmara da Liga & Solvência.",
        kalis: "Fórmula: Casa von [Rocha/Forte] ou Composto Duro (ex.: Casa von Jarngard) • Bastardos: Sombra • Legitimidade: Disciplina & Cota.",
        gaddra: "Fórmula: Clã al-[Marco] ou -id (ex.: Clã al-Qar) • Bastardos: Duna • Legitimidade: Poços Abertos & Lei da Hospitalidade.",
        silvana: "Fórmula: Ramo/Linhagem ab/ferch ou Composto Antigo (ex.: Ramo Derwlyn) • Bastardos: Bruma • Legitimidade: Pacto das Matas."
    };

    const SEATS = {
        F01: { name: "F01 — Entreposto de Estrada", cost: 1800, months: 2, maint: 25, ideal: 6, maxG: 15, hp: 180, le: 6, defSlots: 1, workSlots: 2, maxVillages: 1 },
        F02: { name: "F02 — Solar Urbano Patrício", cost: 3500, months: 4, maint: 45, ideal: 10, maxG: 25, hp: 260, le: 8, defSlots: 2, workSlots: 2, maxVillages: 1 },
        F03: { name: "F03 — Mota e Paliçada", cost: 4800, months: 4, maint: 55, ideal: 18, maxG: 45, hp: 320, le: 7, defSlots: 2, workSlots: 3, maxVillages: 1 },
        F04: { name: "F04 — Torre de Vigia (Specula)", cost: 8000, months: 6, maint: 75, ideal: 15, maxG: 35, hp: 450, le: 10, defSlots: 3, workSlots: 2, maxVillages: 3 },
        F05: { name: "F05 — Solar Rural Fortificado", cost: 14000, months: 9, maint: 120, ideal: 25, maxG: 60, hp: 580, le: 10, defSlots: 3, workSlots: 5, maxVillages: 3 },
        F06: { name: "F06 — Cácer de Oásis (Gaddra)", cost: 16000, months: 10, maint: 130, ideal: 30, maxG: 75, hp: 640, le: 11, defSlots: 4, workSlots: 4, maxVillages: 3 },
        F07: { name: "F07 — Forte Costeiro / Corrente", cost: 18500, months: 12, maint: 155, ideal: 35, maxG: 85, hp: 720, le: 12, defSlots: 4, workSlots: 4, maxVillages: 3 },
        F08: { name: "F08 — Castelo de Cantaria", cost: 36000, months: 24, maint: 280, ideal: 70, maxG: 180, hp: 1200, le: 14, defSlots: 6, workSlots: 6, maxVillages: 6 },
        F09: { name: "F09 — Fortaleza de Escarpa", cost: 65000, months: 36, maint: 420, ideal: 110, maxG: 280, hp: 1650, le: 16, defSlots: 7, workSlots: 5, maxVillages: 6 },
        F10: { name: "F10 — Cidadela de Grande Casa", cost: 110000, months: 48, maint: 750, ideal: 200, maxG: 500, hp: 2400, le: 18, defSlots: 9, workSlots: 9, maxVillages: 6 }
    };

    const DEFENSES = [
        { id: "D01", name: "D01 · Fosso Perimetral", cost: 600, maint: 5, hp: 80, max: 1 },
        { id: "D02", name: "D02 · Portão Duplo & Mata-Cães", cost: 950, maint: 8, hp: 100, max: 1 },
        { id: "D03", name: "D03 · Barbacã Avançada", cost: 1800, maint: 15, hp: 180, max: 1 },
        { id: "D04", name: "D04 · Ronda Coberta", cost: 1200, maint: 10, hp: 90, max: 1 },
        { id: "D05", name: "D05 · Bateria de Torre", cost: 850, maint: 12, hp: 0, max: 3 },
        { id: "D06", name: "D06 · Trabuco Fixo", cost: 1400, maint: 18, hp: 0, max: 3 },
        { id: "D07", name: "D07 · Cisterna & Celeiro Selado", cost: 1100, maint: 6, hp: 0, max: 1 },
        { id: "D08", name: "D08 · Poterna Secreta", cost: 1300, maint: 5, hp: 0, max: 1 }
    ];

    const WORKS = [
        { id: "D09", name: "D09 · Aldeia Arrendada", cost: 2200, income: 85, usesSlot: false, max: 6 },
        { id: "D10", name: "D10 · Moinho", cost: 1600, income: 65, usesSlot: true, max: 2 },
        { id: "D11", name: "D11 · Estalagem & Pedágio", cost: 1800, income: 75, usesSlot: true, max: 2 },
        { id: "D12", name: "D12 · Forja Senhorial", cost: 1500, income: 50, usesSlot: true, max: 1 },
        { id: "D13", name: "D13 · Pedreira / Serraria", cost: 2000, income: 80, usesSlot: true, max: 2 },
        { id: "D14", name: "D14 · Armazém / Cais", cost: 2400, income: 110, usesSlot: true, max: 2 },
        { id: "D15", name: "D15 · Ervanário & Capela", cost: 1300, income: 20, usesSlot: true, max: 1 },
        { id: "D16", name: "D16 · Coudelaria", cost: 1900, income: 60, usesSlot: true, max: 1 }
    ];

    const UNITS = [
        { id: "G01", name: "G01 · Miliciano / Vigia", hire: 15, wage: 12, power: 1, troop: true, mounted: false },
        { id: "G02", name: "G02 · Soldado Regular", hire: 35, wage: 22, power: 2, troop: true, mounted: false },
        { id: "G03", name: "G03 · Besteiro / Arqueiro", hire: 45, wage: 24, power: 2.5, troop: true, mounted: false },
        { id: "G04", name: "G04 · Infante Pesado", hire: 90, wage: 40, power: 4, troop: true, mounted: false },
        { id: "G05", name: "G05 · Patrulheiro Montado", hire: 140, wage: 48, power: 3, troop: true, mounted: true },
        { id: "G06", name: "G06 · Cavaleiro Retido", hire: 220, wage: 75, power: 6, troop: true, mounted: true },
        { id: "G07", name: "G07 · Artilheiro / Engenheiro", hire: 50, wage: 35, power: 3, troop: true, mounted: false },
        { id: "G08", name: "G08 · Trabalhador Braçal", hire: 0, wage: 9, power: 0, troop: false, mounted: false },
        { id: "G09", name: "G09 · Pedreiro / Carpinteiro", hire: 10, wage: 18, power: 0, troop: false, mounted: false },
        { id: "G10", name: "G10 · Mestre Ferreiro", hire: 25, wage: 30, power: 0, troop: false, mounted: false },
        { id: "G11", name: "G11 · Senescal (+10% Renda)", hire: 30, wage: 45, power: 0, troop: false, mounted: false },
        { id: "G12", name: "G12 · Mestre de Armas", hire: 30, wage: 40, power: 0, troop: false, mounted: false },
        { id: "G13", name: "G13 · Físico / Herbalista", hire: 35, wage: 35, power: 0, troop: false, mounted: false },
        { id: "G14", name: "G14 · Mestre de Sussurros", hire: 40, wage: 50, power: 0, troop: false, mounted: false }
    ];

    const defaultState = () => ({
        houseName: "Casa de Specula",
        culture: "aurora",
        motto: "Vigiamos Onde a Cinza Caiu",
        seat: "F04",
        mode: "ruin", // 'new' or 'ruin' (45%)
        counts: { D01: 1, D02: 1, D09: 2, D10: 1, D11: 1, G01: 4, G02: 4, G03: 4, G11: 1 }
    });

    let state = defaultState();
    try {
        const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null');
        if (saved && saved.seat && SEATS[saved.seat]) {
            state = Object.assign(defaultState(), saved);
            state.counts = Object.assign({}, saved.counts || {});
        }
    } catch (_) {}

    function fmtPP(n) {
        return Math.round(n).toLocaleString('pt-BR') + ' PP';
    }

    function initCalculator() {
        const root = document.getElementById('simulador-feudo');
        if (!root) return;

        const nameInp = document.getElementById('fc-name');
        const cultSel = document.getElementById('fc-culture');
        const mottoInp = document.getElementById('fc-motto');
        const seatSel = document.getElementById('fc-seat');
        const modeSel = document.getElementById('fc-mode');
        const hintEl = document.getElementById('fc-culture-hint');

        const defList = document.getElementById('fc-def-list');
        const workList = document.getElementById('fc-work-list');
        const unitList = document.getElementById('fc-unit-list');

        function buildStepperRow(item, subText) {
            const row = document.createElement('div');
            row.className = 'feudo-row';
            row.innerHTML = `
                <div class="feudo-row-info">
                    <span class="feudo-row-name">${item.name}</span>
                    <span class="feudo-row-sub">${subText}</span>
                </div>
                <div class="feudo-stepper">
                    <button type="button" class="feudo-step-btn" data-id="${item.id}" data-delta="-1" aria-label="Diminuir">−</button>
                    <span class="feudo-qty" id="fc-qty-${item.id}">0</span>
                    <button type="button" class="feudo-step-btn" data-id="${item.id}" data-delta="1" aria-label="Aumentar">+</button>
                </div>
            `;
            return row;
        }

        DEFENSES.forEach(d => defList.appendChild(buildStepperRow(d, `${d.cost} PP • Manut. ${d.maint} PP/mês`)));
        WORKS.forEach(w => workList.appendChild(buildStepperRow(w, `${w.cost} PP • Renda +${w.income} PP/mês${w.usesSlot ? '' : ' (Fora dos muros)'}`)));
        UNITS.forEach(u => unitList.appendChild(buildStepperRow(u, `${u.wage} PP/mês${u.hire ? ` • Inicial ${u.hire} PP` : ''}`)));

        function syncInputsFromState() {
            if (nameInp) nameInp.value = state.houseName || '';
            if (cultSel) cultSel.value = state.culture || 'aurora';
            if (mottoInp) mottoInp.value = state.motto || '';
            if (seatSel) seatSel.value = state.seat || 'F04';
            if (modeSel) modeSel.value = state.mode || 'ruin';
        }

        function computeAndRender() {
            const seat = SEATS[state.seat] || SEATS.F04;
            if (hintEl) hintEl.textContent = CULTURES[state.culture] || CULTURES.aurora;

            const isRuin = (state.mode === 'ruin');
            const seatBuildCost = Math.round(seat.cost * (isRuin ? 0.45 : 1));
            const hasQuarry = (state.counts.D13 || 0) > 0;
            const hasForge = (state.counts.D12 || 0) > 0 && (state.counts.G10 || 0) > 0;
            const hasStables = (state.counts.D16 || 0) > 0;
            const hasSeneschal = (state.counts.G11 || 0) > 0;
            const hasMasterAtArms = (state.counts.G12 || 0) > 0;
            const villages = Math.min(seat.maxVillages, state.counts.D09 || 0);

            let defSlotsUsed = 0;
            let defBuildCost = 0;
            let defMaint = 0;
            let extraHP = 0;
            DEFENSES.forEach(d => {
                const q = state.counts[d.id] || 0;
                const el = document.getElementById('fc-qty-' + d.id);
                if (el) el.textContent = String(q);
                defSlotsUsed += q;
                defBuildCost += q * d.cost;
                defMaint += q * d.maint;
                extraHP += q * d.hp;
            });

            let workSlotsUsed = 0;
            let workBuildCost = 0;
            let rawIncome = 0;
            WORKS.forEach(w => {
                const q = state.counts[w.id] || 0;
                const el = document.getElementById('fc-qty-' + w.id);
                if (el) el.textContent = String(q);
                if (w.usesSlot) workSlotsUsed += q;
                workBuildCost += q * w.cost;
                rawIncome += q * w.income;
            });
            // Mill + Village agricultural synergy (+15 PP per mill if at least 1 village)
            if (villages > 0 && (state.counts.D10 || 0) > 0) {
                rawIncome += 15 * (state.counts.D10 || 0);
            }
            const totalIncome = Math.round(rawIncome * (hasSeneschal ? 1.10 : 1.0));

            // Quarry D13 reduces expansion works/defenses cost by 15%
            const worksAndDefCost = Math.round((defBuildCost + workBuildCost) * (hasQuarry ? 0.85 : 1.0));

            let troopCount = 0;
            let hireCost = 0;
            let troopWages = 0;
            let staffWages = 0;
            let rawPower = 0;

            UNITS.forEach(u => {
                const q = state.counts[u.id] || 0;
                const el = document.getElementById('fc-qty-' + u.id);
                if (el) el.textContent = String(q);
                if (u.troop) {
                    troopCount += q;
                    const unitHire = hasForge ? Math.round(u.hire * 0.80) : u.hire;
                    hireCost += q * unitHire;
                    const unitWage = (u.mounted && hasStables) ? Math.max(0, u.wage - 10) : u.wage;
                    troopWages += q * unitWage;
                    rawPower += q * u.power;
                } else {
                    hireCost += q * u.hire;
                    staffWages += q * u.wage;
                }
            });

            // Village D09 reduces garrison upkeep by 15% for up to 25 troops per village
            if (villages > 0 && troopCount > 0) {
                const coveredRatio = Math.min(1, (villages * 25) / troopCount);
                troopWages = Math.round(troopWages * (1 - 0.15 * coveredRatio));
            }

            // Masons G09 reduce structural maintenance (-5 PP each, up to 3, on F04+)
            const masonDiscount = (seat.cost >= 8000) ? Math.min(3, state.counts.G09 || 0) * 5 : 0;
            const totalMaint = Math.max(10, seat.maint - masonDiscount) + defMaint;
            const totalExpense = totalMaint + troopWages + staffWages;
            const netMonthly = totalIncome - totalExpense;
            const totalInitial = seatBuildCost + worksAndDefCost + hireCost;
            const defPower = Math.round(rawPower * (hasMasterAtArms ? 1.10 : 1.0) * 10) / 10;
            const siegeDays = ((state.counts.D07 || 0) > 0 || state.seat === 'F06') ? 60 : 30;
            const buildTimeMonths = isRuin ? (seat.months / 2) : seat.months;

            // Update slot badges
            const defBadge = document.getElementById('fc-def-slots');
            if (defBadge) {
                defBadge.textContent = `${defSlotsUsed} / ${seat.defSlots} slots`;
                defBadge.classList.toggle('over', defSlotsUsed > seat.defSlots);
            }
            const workBadge = document.getElementById('fc-work-slots');
            if (workBadge) {
                workBadge.textContent = `${workSlotsUsed} / ${seat.workSlots} slots`;
                workBadge.classList.toggle('over', workSlotsUsed > seat.workSlots);
            }
            const unitBadge = document.getElementById('fc-unit-slots');
            if (unitBadge) {
                unitBadge.textContent = `${troopCount} / ${seat.ideal} ideal (máx ${seat.maxG})`;
                unitBadge.classList.toggle('over', troopCount > seat.maxG);
            }

            // Update 4 summary cards
            document.getElementById('fc-out-initial').textContent = fmtPP(totalInitial);
            document.getElementById('fc-out-initial-sub').textContent =
                `(${(totalInitial / 10).toLocaleString('pt-BR')} PO) • Obra base: ${buildTimeMonths} ${buildTimeMonths === 1 ? 'mês' : 'meses'}`;

            document.getElementById('fc-out-income').textContent = '+' + fmtPP(totalIncome) + '/mês';
            document.getElementById('fc-out-income-sub').textContent =
                hasSeneschal ? 'Inclui +10% do Senescal (G11)' : 'Contrate Senescal (G11) para +10%';

            document.getElementById('fc-out-expense').textContent = '−' + fmtPP(totalExpense) + '/mês';
            document.getElementById('fc-out-expense-sub').textContent =
                `Muros: ${totalMaint} PP • Tropa: ${troopWages} PP • Corte: ${staffWages} PP`;

            const netEl = document.getElementById('fc-out-net');
            netEl.textContent = (netMonthly >= 0 ? '+' : '−') + fmtPP(Math.abs(netMonthly)) + '/mês';
            netEl.classList.toggle('positive', netMonthly >= 0);
            netEl.classList.toggle('negative', netMonthly < 0);
            document.getElementById('fc-out-net-sub').textContent =
                `Integridade ${seat.hp + extraHP} PV (LE ${seat.le + ((state.counts.D02 || 0) ? 2 : 0)}) • Defesa ${defPower} • Cerco ${siegeDays}d`;

            state._summaryText = [
                `=== ${state.houseName || 'Casa Sem Nome'} (${state.motto || 'Sem lema'}) ===`,
                `Sede: ${seat.name} (${isRuin ? 'Reforma de Ruína 45%' : 'Construção Nova'})`,
                `Investimento Inicial Total: ${fmtPP(totalInitial)} (${(totalInitial / 10).toLocaleString('pt-BR')} PO)`,
                `Balanço Mensal: Receita +${totalIncome} PP | Despesa -${totalExpense} PP | Saldo ${netMonthly >= 0 ? '+' : ''}${netMonthly} PP/mês`,
                `Defesa Militar: ${troopCount} soldados (Índice ${defPower}) | Integridade ${seat.hp + extraHP} PV (LE ${seat.le}) | Suprimentos ${siegeDays} dias`
            ].join('\n');

            try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch (_) {}
        }

        root.addEventListener('click', (e) => {
            const btn = e.target.closest('.feudo-step-btn');
            if (!btn) return;
            const id = btn.dataset.id;
            const delta = parseInt(btn.dataset.delta, 10) || 0;
            const cur = state.counts[id] || 0;
            let maxAllowed = 99;
            const dItem = DEFENSES.find(x => x.id === id);
            const wItem = WORKS.find(x => x.id === id);
            if (dItem) maxAllowed = dItem.max;
            if (wItem) maxAllowed = wItem.id === 'D09' ? (SEATS[state.seat]?.maxVillages || 6) : wItem.max;
            state.counts[id] = Math.max(0, Math.min(maxAllowed, cur + delta));
            computeAndRender();
        });

        [nameInp, cultSel, mottoInp, seatSel, modeSel].forEach(el => {
            if (!el) return;
            el.addEventListener('input', () => {
                state.houseName = nameInp ? nameInp.value : '';
                state.culture = cultSel ? cultSel.value : 'aurora';
                state.motto = mottoInp ? mottoInp.value : '';
                state.seat = seatSel ? seatSel.value : 'F04';
                state.mode = modeSel ? modeSel.value : 'ruin';
                computeAndRender();
            });
        });

        document.getElementById('fc-preset-tower')?.addEventListener('click', () => {
            state = defaultState();
            syncInputsFromState();
            computeAndRender();
        });
        document.getElementById('fc-preset-manor')?.addEventListener('click', () => {
            state = {
                houseName: "Casa Montavalle do Sul",
                culture: "aurora",
                motto: "Raiz na Pedra, Pão na Mesa",
                seat: "F05",
                mode: "new",
                counts: { D01: 1, D02: 1, D07: 1, D09: 3, D10: 1, D11: 1, D12: 1, D14: 1, D15: 1, G01: 6, G02: 4, G03: 4, G05: 2, G09: 1, G10: 1, G11: 1, G13: 1 }
            };
            syncInputsFromState();
            computeAndRender();
        });
        document.getElementById('fc-reset')?.addEventListener('click', () => {
            state.counts = {};
            computeAndRender();
        });
        document.getElementById('fc-copy')?.addEventListener('click', async () => {
            const fb = document.getElementById('fc-copy-fb');
            try {
                await navigator.clipboard.writeText(state._summaryText || '');
                if (fb) { fb.textContent = '✓ Copiado!'; setTimeout(() => { fb.textContent = ''; }, 2200); }
            } catch (_) {
                if (fb) fb.textContent = 'Selecione e copie manualmente';
            }
        });

        syncInputsFromState();
        computeAndRender();
    }

    // Catalog Search & Filter Logic
    function initCatalogFilters() {
        const norm = (s) => (s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();

        // Fortifications filter
        const fortRoot = document.getElementById('casas-forts-root');
        const fortPills = Array.from(document.querySelectorAll('.casas-fort-pill'));
        const fortSearch = document.getElementById('casas-fort-search');
        const fortCount = document.getElementById('casas-fort-count');
        const fortEmpty = document.getElementById('casas-fort-empty');
        let fortTier = 'ALL';

        function applyFortFilter() {
            if (!fortRoot) return;
            const q = norm(fortSearch ? fortSearch.value.trim() : '');
            let shown = 0;
            const all = fortRoot.querySelectorAll('.casas-fort-card');
            fortRoot.querySelectorAll('.casas-group').forEach(grp => {
                const ok = (fortTier === 'ALL' || grp.dataset.tier === fortTier);
                let gShown = 0;
                grp.querySelectorAll('.casas-fort-card').forEach(c => {
                    const m = ok && (!q || norm(c.dataset.search).includes(q));
                    c.classList.toggle('is-hidden', !m);
                    if (m) { gShown++; shown++; }
                });
                grp.classList.toggle('is-hidden', gShown === 0);
            });
            if (fortCount) fortCount.textContent = `Exibindo ${shown} de ${all.length} fortificações`;
            if (fortEmpty) fortEmpty.classList.toggle('visible', shown === 0);
        }

        fortPills.forEach(p => p.addEventListener('click', () => {
            fortTier = p.dataset.tier;
            fortPills.forEach(x => x.classList.toggle('active', x === p));
            applyFortFilter();
        }));
        if (fortSearch) fortSearch.addEventListener('input', applyFortFilter);

        // Domain Works, Defenses & Garrison filter
        const domRoot = document.getElementById('casas-dom-root');
        const domPills = Array.from(document.querySelectorAll('.casas-dom-pill'));
        const domSearch = document.getElementById('casas-dom-search');
        const domCount = document.getElementById('casas-dom-count');
        const domEmpty = document.getElementById('casas-dom-empty');
        let domKind = 'ALL';

        function applyDomFilter() {
            if (!domRoot) return;
            const q = norm(domSearch ? domSearch.value.trim() : '');
            let shown = 0;
            const all = domRoot.querySelectorAll('.casas-item-card');
            domRoot.querySelectorAll('.casas-group').forEach(grp => {
                let gShown = 0;
                grp.querySelectorAll('.casas-item-card').forEach(c => {
                    const kOk = (domKind === 'ALL' || c.dataset.kind === domKind);
                    const m = kOk && (!q || norm(c.dataset.search).includes(q));
                    c.classList.toggle('is-hidden', !m);
                    if (m) { gShown++; shown++; }
                });
                grp.classList.toggle('is-hidden', gShown === 0);
            });
            if (domCount) domCount.textContent = `Exibindo ${shown} de ${all.length} defesas, obras e cargos`;
            if (domEmpty) domEmpty.classList.toggle('visible', shown === 0);
        }

        domPills.forEach(p => p.addEventListener('click', () => {
            domKind = p.dataset.kind;
            domPills.forEach(x => x.classList.toggle('active', x === p));
            applyDomFilter();
        }));
        if (domSearch) domSearch.addEventListener('input', applyDomFilter);

        window.aleniaRevealAnchor = function(id) {
            const el = document.getElementById(id);
            if (!el) return;
            if (el.closest('.casas-fort-card.is-hidden') || el.closest('#casas-forts-root .casas-group.is-hidden')) {
                fortTier = 'ALL';
                fortPills.forEach(x => x.classList.toggle('active', x.dataset.tier === 'ALL'));
                if (fortSearch) fortSearch.value = '';
                applyFortFilter();
            }
            if (el.closest('.casas-item-card.is-hidden') || el.closest('#casas-dom-root .casas-group.is-hidden')) {
                domKind = 'ALL';
                domPills.forEach(x => x.classList.toggle('active', x.dataset.kind === 'ALL'));
                if (domSearch) domSearch.value = '';
                applyDomFilter();
            }
            const det = el.closest('details');
            if (det && !det.open) det.open = true;
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

        const revealForPrint = () => {
            document.querySelectorAll('.casas-group.is-hidden, .casas-fort-card.is-hidden, .casas-item-card.is-hidden').forEach(el => {
                el.classList.remove('is-hidden');
            });
            if (fortEmpty) fortEmpty.classList.remove('visible');
            if (domEmpty) domEmpty.classList.remove('visible');
        };
        const restorePrint = () => {
            applyFortFilter();
            applyDomFilter();
        };
        window.addEventListener('alenia:prepare-print', revealForPrint);
        window.addEventListener('beforeprint', revealForPrint);
        window.addEventListener('alenia:restore-print', restorePrint);
        window.addEventListener('afterprint', restorePrint);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => { initCalculator(); initCatalogFilters(); });
    } else {
        initCalculator();
        initCatalogFilters();
    }
})();
"""


def _parse_bold_pairs(line: str):
    pairs = []
    matches = list(re.finditer(r"\*\*([^*:]+):\*\*\s*", line))
    for i, m in enumerate(matches):
        key = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(line)
        val = line[start:end].strip().rstrip(".·").strip()
        if val:
            pairs.append((key, val))
    return pairs


def _build_calculator_html() -> str:
    return """
    <section id="simulador-feudo" class="feudo-calc-wrap" aria-label="Calculadora Interativa de Casa Nobre e Feudo">
        <div class="feudo-calc-head">
            <div>
                <div class="feudo-calc-kicker">FERRAMENTA INTERATIVA DE MESA • PADRÃO PRATA</div>
                <h2 class="feudo-calc-title">🏰 Construtor e Orçamento de Casa Nobre &amp; Feudo</h2>
            </div>
            <div class="feudo-presets">
                <button id="fc-preset-tower" class="feudo-btn" type="button">Exemplo: Torre Reerguida</button>
                <button id="fc-preset-manor" class="feudo-btn" type="button">Exemplo: Solar Baronial</button>
                <button id="fc-reset" class="feudo-btn" type="button">↺ Zerar</button>
                <button id="fc-copy" class="feudo-btn primary" type="button">📋 Copiar Carta do Feudo</button>
                <span id="fc-copy-fb" class="feudo-copy-feedback" aria-live="polite"></span>
            </div>
        </div>
        <div class="feudo-identity-row">
            <div class="feudo-field">
                <label for="fc-name">Nome da Casa / Dinastia / Clã</label>
                <input id="fc-name" type="text" placeholder="Ex.: Casa de Specula"/>
            </div>
            <div class="feudo-field">
                <label for="fc-culture">Tradição Cultural (Tomo V)</label>
                <select id="fc-culture">
                    <option value="aurora">1. Reino de Aurora (Feudal)</option>
                    <option value="corallis">2. Liga de Corallis (Patrícia)</option>
                    <option value="kalis">3. Despotado de Kalis (Ferro)</option>
                    <option value="gaddra">4. Confederação de Gaddra (Oásis)</option>
                    <option value="silvana">5. Fronteiras Silvanas (Pacto)</option>
                </select>
            </div>
            <div class="feudo-field">
                <label for="fc-motto">Lema Heráldico</label>
                <input id="fc-motto" type="text" placeholder="Ex.: Vigiamos Onde a Cinza Caiu"/>
            </div>
        </div>
        <p id="fc-culture-hint" class="feudo-culture-hint"></p>
        <div class="feudo-seat-bar">
            <div class="feudo-field">
                <label for="fc-seat">Sede Senhorial / Fortificação Principal (F01–F10)</label>
                <select id="fc-seat">
                    <option value="F01">F01 — Entreposto e Feitoria de Estrada (Novo 1.800 PP / Ruína 810 PP)</option>
                    <option value="F02">F02 — Casa-Forte e Solar Urbano Patrício (Novo 3.500 PP / Ruína 1.575 PP)</option>
                    <option value="F03">F03 — Mota com Paliçada e Salão Senhorial (Novo 4.800 PP / Ruína 2.160 PP)</option>
                    <option value="F04">F04 — Torre de Vigia de Cantaria (Novo 8.000 PP / Ruína 3.600 PP)</option>
                    <option value="F05">F05 — Solar Rural Fortificado e Quinta Murada (Novo 14.000 PP / Ruína 6.300 PP)</option>
                    <option value="F06">F06 — Cácer de Oásis e Cisterna — Gaddra (Novo 16.000 PP / Ruína 7.200 PP)</option>
                    <option value="F07">F07 — Forte Costeiro e Torre de Corrente (Novo 18.500 PP / Ruína 8.325 PP)</option>
                    <option value="F08">F08 — Castelo Feudal de Cantaria (Novo 36.000 PP / Ruína 16.200 PP)</option>
                    <option value="F09">F09 — Fortaleza de Escarpa e Rocha Escavada (Novo 65.000 PP / Ruína 29.250 PP)</option>
                    <option value="F10">F10 — Cidadela e Paço de Grande Casa (Novo 110.000 PP / Ruína 49.500 PP)</option>
                </select>
            </div>
            <div class="feudo-field">
                <label for="fc-mode">Modo de Aquisição da Sede</label>
                <select id="fc-mode">
                    <option value="ruin">Reerguer Ruína Concedida (45% do custo • ½ tempo)</option>
                    <option value="new">Construção Nova do Zero (100% do custo)</option>
                </select>
            </div>
        </div>
        <div class="feudo-columns">
            <div class="feudo-panel">
                <div class="feudo-panel-head">
                    <span>🛡 Defesas (D01–D08)</span>
                    <span id="fc-def-slots" class="feudo-slot-badge">0 / 3 slots</span>
                </div>
                <div id="fc-def-list" class="feudo-item-list"></div>
            </div>
            <div class="feudo-panel">
                <div class="feudo-panel-head">
                    <span>🌾 Obras &amp; Renda (D09–D16)</span>
                    <span id="fc-work-slots" class="feudo-slot-badge">0 / 2 slots</span>
                </div>
                <div id="fc-work-list" class="feudo-item-list"></div>
            </div>
            <div class="feudo-panel">
                <div class="feudo-panel-head">
                    <span>⚔ Tropa &amp; Corte (G01–G14)</span>
                    <span id="fc-unit-slots" class="feudo-slot-badge">0 / 15 ideal</span>
                </div>
                <div id="fc-unit-list" class="feudo-item-list"></div>
            </div>
        </div>
        <div class="feudo-summary-board">
            <div class="feudo-metric">
                <div class="feudo-metric-lbl">Investimento Inicial</div>
                <div id="fc-out-initial" class="feudo-metric-val">0 PP</div>
                <div id="fc-out-initial-sub" class="feudo-metric-sub">Sede + Obras + Equipamento</div>
            </div>
            <div class="feudo-metric">
                <div class="feudo-metric-lbl">Receita Bruta Mensal</div>
                <div id="fc-out-income" class="feudo-metric-val positive">+0 PP/mês</div>
                <div id="fc-out-income-sub" class="feudo-metric-sub">Obras produtivas e terras</div>
            </div>
            <div class="feudo-metric">
                <div class="feudo-metric-lbl">Manutenção &amp; Folha</div>
                <div id="fc-out-expense" class="feudo-metric-val">−0 PP/mês</div>
                <div id="fc-out-expense-sub" class="feudo-metric-sub">Muros + Guarnição + Corte</div>
            </div>
            <div class="feudo-metric">
                <div class="feudo-metric-lbl">Saldo Líquido no Cofre</div>
                <div id="fc-out-net" class="feudo-metric-val">+0 PP/mês</div>
                <div id="fc-out-net-sub" class="feudo-metric-sub">Integridade &amp; Defesa</div>
            </div>
        </div>
    </section>
    """


def render_casas_nobres_page(bk: dict, md_content: str, helpers: dict):
    """Build interactive illustrated Tomo XV — Casas Nobres, Feudos e Fortificações page."""
    inline_md = helpers["inline_md"]
    md_to_html = helpers["md_to_html"]
    img_dim_attrs = helpers["img_dim_attrs"]
    make_gm_gate_block = helpers["make_gm_gate_block"]
    render_toc_items = helpers["render_toc_items"]

    sections = re.split(r"(?=^##\s+)", md_content, flags=re.M)

    intro_secs = []
    fort_intro_md = ""
    fort_secs = []
    dom_secs = []
    tail_secs = []
    gm_sec = ""
    shield_sec = ""

    fort_tier_map = {
        "Sedes iniciais de exploradores e cavaleiros": ("inicial", "Sedes Iniciais", "DEGRAU I • STATUS 1–2 • FEITORIAS, SOLARES E MOTAS"),
        "Praças-fortes menores e castelanias": ("menor", "Praças Menores", "DEGRAU II • STATUS 2–3 • TORRES, QUINTAS MURADAS E CÁCERES"),
        "Castelos, fortalezas de escarpa e cidadelas": ("maior", "Grandes Fortalezas", "DEGRAU III • STATUS 3–5 • CASTELOS DE CANTARIA E CIDADELAS"),
    }

    dom_group_map = {
        "Defesas militares e engenhos de muralha sem pólvora": ("defesa", "def-code", "ENGENHARIA DEFENSIVA • SLOTS DE DEFESA (D01–D08)", ""),
        "Obras produtivas e infraestrutura do feudo": ("obra", "work-code", "ECONOMIA SENHORIAL • GERADORES DE RECEITA MENSAL (D09–D16)", ""),
        "Tropas de guarnição e patrulha": ("tropa", " code-crimson", "FORÇAS PERMANENTES DA CASA • GUARNIÇÃO E CAVALARIA (G01–G07)", "ilustracoes/dominio_04_guarnicao.jpg"),
        "Trabalhadores, artífices e corte doméstica": ("corte", "unit-code", "ADMINISTRAÇÃO E OFÍCIOS • TRABALHADORES E CORTE (G08–G14)", ""),
    }

    for sec in sections:
        s = sec.strip()
        m_h2 = re.match(r"^##\s+(.+)$", s, flags=re.M)
        if not m_h2:
            continue
        title = m_h2.group(1).strip()
        if title in ("Como criar e governar uma casa nobre", "As cinco tradições senhoriais e heráldica de Alenia"):
            intro_secs.append(s)
        elif title == "Fortificações e sedes senhoriais":
            fort_intro_md = s
        elif title in fort_tier_map:
            fort_secs.append((title, s))
        elif title in dom_group_map:
            dom_secs.append((title, s))
        elif title.lower().startswith("caderno reservado ao mestre"):
            gm_sec = s
        elif title.startswith("Referência rápida"):
            shield_sec = s
        else:
            tail_secs.append(s)

    toc_items = [
        (2, "Guia de Fundação e Heráldica (5 Culturas)", "guia-fundacao"),
        (2, "Calculadora de Casa Nobre e Feudo", "simulador-feudo"),
    ]

    # 1. Collapsible Creation & Heraldry Guide (opened by default or expandable)
    intro_inner, _ = md_to_html("\n\n".join(intro_secs), id_prefix="casa-intro-", card_h3=False, inject_maps=False)
    intro_html = f"""
    <details class="casas-editorial" id="guia-fundacao" open>
        <summary>👑 Criação em 6 Passos, As 5 Tradições Culturais, Heráldica &amp; Tabelas de Raízes da Casa</summary>
        <div class="casas-editorial-inner">{intro_inner}</div>
    </details>
    """

    # 2. Fortifications (F01–F10)
    fort_intro_html = ""
    if fort_intro_md:
        fort_intro_html, _ = md_to_html(fort_intro_md, id_prefix="fort-top-", card_h3=False, inject_maps=False)

    fort_groups_html = []
    fort_summary_md = ""
    total_forts = 0
    fort_counts = {}

    for f_title, f_raw in fort_secs:
        t_slug, _, t_kicker = fort_tier_map[f_title]
        grp_id = f"fortes-{t_slug}"
        toc_items.append((2, f_title, grp_id))

        if "### Resumo Comparativo" in f_raw:
            f_raw, tail_tbl = f_raw.split("### Resumo Comparativo", 1)
            fort_summary_md = "### Resumo Comparativo" + tail_tbl

        f_parts = re.split(r"(?=^###\s+F\d{2}\s)", f_raw, flags=re.M)
        grp_intro = "".join(
            f"<p>{inline_md(ln.strip())}</p>"
            for ln in f_parts[0].splitlines()[1:] if ln.strip()
        )

        f_cards = []
        for fblk in f_parts[1:]:
            lines = [ln.strip() for ln in fblk.strip().splitlines() if ln.strip()]
            if not lines:
                continue
            m_fh = re.match(r"^###\s+(F\d{2})\s+[—–-]\s+(.+)$", lines[0])
            if not m_fh:
                continue
            code, name = m_fh.group(1), m_fh.group(2).strip()
            total_forts += 1
            fort_counts[t_slug] = fort_counts.get(t_slug, 0) + 1

            plate_html = ""
            tags_html = []
            body_paras = []
            for ln in lines[1:]:
                m_img = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", ln)
                if m_img:
                    alt = m_img.group(1).strip() or f"{code} — {name}"
                    src = "assets/" + os.path.basename(m_img.group(2).strip())
                    plate_html = (
                        f'<figure class="atlas-plate casas-fort-plate" title="Clique para ampliar planta e perspectiva de {html.escape(name, quote=True)}">'
                        f'<img src="{html.escape(src, quote=True)}" alt="{html.escape(alt, quote=True)}"{img_dim_attrs(src)} decoding="async"/>'
                        f'</figure>'
                    )
                elif any(ln.startswith(p) for p in ("**Porte:**", "**Tempo de obra:**", "**Integridade:**")):
                    for k_lbl, v_lbl in _parse_bold_pairs(ln):
                        cls = "casas-tag"
                        if "Preço" in k_lbl or "Reforma" in k_lbl or k_lbl == "Manutenção":
                            cls += " price"
                        elif k_lbl in ("Integridade", "Limiar Estrutural", "Slots"):
                            cls += " siege"
                        tags_html.append(f'<span class="{cls}">{html.escape(k_lbl)}: {inline_md(v_lbl)}</span>')
                else:
                    body_paras.append(f"<p>{inline_md(ln)}</p>")

            s_blob = html.escape(f"{code} {name} {f_title} {' '.join(lines[1:])}", quote=True)
            f_cards.append(f"""
            <article class="casas-fort-card" id="{code.lower()}" data-search="{s_blob}">
                <div class="casas-fort-head">
                    <span class="casas-code">{html.escape(code)}</span>
                    <h3 class="casas-fort-title">{html.escape(name)}</h3>
                </div>
                {plate_html}
                <div class="casas-tags">{"".join(tags_html)}</div>
                {"".join(body_paras)}
            </article>
            """)

        fort_groups_html.append(f"""
        <section class="casas-group" id="{grp_id}" data-tier="{t_slug}">
            <header class="casas-group-header">
                <div class="casas-group-kicker">{t_kicker}</div>
                <h2 class="casas-group-title">{html.escape(f_title)}</h2>
            </header>
            {grp_intro}
            {"".join(f_cards)}
        </section>
        """)

    fort_summary_html = ""
    if fort_summary_md:
        fort_summary_html, _ = md_to_html(fort_summary_md, id_prefix="fort-sum-", card_h3=False, inject_maps=False)

    # 3. Defenses (D01–D08), Productive Works (D09–D16), Troops (G01–G07) & Staff (G08–G14)
    dom_groups_html = []
    total_dom_items = 0
    dom_counts = {"defesa": 0, "obra": 0, "tropa": 0, "corte": 0}

    for d_title, d_raw in dom_secs:
        kind_key, badge_cls, d_kicker, fallback_plate = dom_group_map[d_title]
        d_id = f"secao-{kind_key}"
        toc_items.append((2, d_title, d_id))

        # Remove duplicate standalone plate if Soldados section had one above
        trailing_tbl_md = ""
        if "### Tabela Resumo" in d_raw:
            d_raw, trailing_tbl_md = d_raw.split("### Tabela Resumo", 1)
            trailing_tbl_md = "### Tabela Resumo" + trailing_tbl_md

        i_parts = re.split(r"(?=^###\s+[DG]\d{2}\s)", d_raw, flags=re.M)
        wide_plate_html = ""
        intro_paras = []
        for ln in i_parts[0].splitlines()[1:]:
            s = ln.strip()
            if not s:
                continue
            m_img = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", s)
            if m_img:
                palt = m_img.group(1).strip() or d_title
                psrc = "assets/" + os.path.basename(m_img.group(2).strip())
                wide_plate_html = (
                    f'<figure class="atlas-plate casas-wide-plate" title="Clique para ampliar prancha">'
                    f'<img src="{html.escape(psrc, quote=True)}" alt="{html.escape(palt, quote=True)}"{img_dim_attrs(psrc)} decoding="async"/>'
                    f'<figcaption class="atlas-caption">{html.escape(palt)}</figcaption>'
                    f'</figure>'
                )
            else:
                intro_paras.append(f"<p>{inline_md(s)}</p>")

        if not wide_plate_html and fallback_plate:
            psrc = "assets/" + os.path.basename(fallback_plate)
            palt = "Prancha IV — Panoplia de Guarnição, Cofre do Senescal e Instrumentos de Vigia e Ofício"
            wide_plate_html = (
                f'<figure class="atlas-plate casas-wide-plate" title="Clique para ampliar prancha">'
                f'<img src="{html.escape(psrc, quote=True)}" alt="{html.escape(palt, quote=True)}"{img_dim_attrs(psrc)} decoding="async"/>'
                f'<figcaption class="atlas-caption">{html.escape(palt)}</figcaption>'
                f'</figure>'
            )

        cards = []
        for iblk in i_parts[1:]:
            ilines = [ln.strip() for ln in iblk.strip().splitlines() if ln.strip()]
            if not ilines:
                continue
            m_ih = re.match(r"^###\s+([DG]\d{2})\s+[—–-]\s+(.+)$", ilines[0])
            if not m_ih:
                continue
            icode, iname = m_ih.group(1), m_ih.group(2).strip()
            total_dom_items += 1
            dom_counts[kind_key] = dom_counts.get(kind_key, 0) + 1

            itags = []
            ibody_lines = []
            for idx_l, il in enumerate(ilines[1:]):
                if idx_l == 0 and il.startswith("**"):
                    for k_lbl, v_lbl in _parse_bold_pairs(il):
                        cls = "casas-tag"
                        if "Receita" in k_lbl:
                            cls += " income"
                        elif any(w in k_lbl for w in ("Custo", "Mensalidade", "Equip", "Contratação")):
                            cls += " price"
                        elif any(w in k_lbl for w in ("Bônus", "Índice", "Alcance")):
                            cls += " siege"
                        itags.append(f'<span class="{cls}">{html.escape(k_lbl)}: {inline_md(v_lbl)}</span>')
                else:
                    ibody_lines.append(il)

            ibody_html, _ = md_to_html("\n\n".join(ibody_lines), id_prefix=f"it-{icode.lower()}-", card_h3=False, inject_maps=False)
            isearch = html.escape(f"{icode} {iname} {d_title} {' '.join(ilines[1:])}", quote=True)
            cards.append(f"""
            <article class="casas-item-card" id="{icode.lower()}" data-kind="{kind_key}" data-search="{isearch}">
                <div class="casas-item-head">
                    <span class="casas-code {badge_cls.strip()}">{html.escape(icode)}</span>
                    <h3>{html.escape(iname)}</h3>
                </div>
                <div class="casas-tags">{"".join(itags)}</div>
                {ibody_html}
            </article>
            """)

        trail_html = ""
        if trailing_tbl_md:
            trail_html, _ = md_to_html(trailing_tbl_md, id_prefix=f"tr-{kind_key}-", card_h3=False, inject_maps=False)

        hdr_cls = "casas-group-header slate" if kind_key in ("defesa", "obra") else "casas-group-header"
        dom_groups_html.append(f"""
        <section class="casas-group" id="{d_id}">
            <header class="{hdr_cls}">
                <div class="casas-group-kicker">{d_kicker}</div>
                <h2 class="casas-group-title">{html.escape(d_title)}</h2>
            </header>
            {"".join(intro_paras)}
            {wide_plate_html}
            <div class="casas-card-grid">{"".join(cards)}</div>
            {trail_html}
        </section>
        """)

    # 4. Monthly Management & Siege Rules
    tail_html = ""
    filtered_tail = [s for s in tail_secs if not s.startswith("## Soldados, especialistas")]
    if filtered_tail:
        t_inner, t_toc = md_to_html("\n\n".join(filtered_tail), id_prefix="casas-cerco-", card_h3=False, inject_maps=False)
        tail_html = f'<section class="casas-divider">{t_inner}</section>'
        toc_items.extend(t_toc)

    # 5. Encrypted GM Vault
    gm_html = ""
    if gm_sec:
        gm_rendered, gm_toc = md_to_html(gm_sec, id_prefix="casas-gm-", card_h3=False, inject_maps=False)
        gm_html = (
            '<div class="casas-divider">'
            + make_gm_gate_block(
                "Caderno Reservado ao Mestre — Intrigas de Feudo e Cercos",
                "Contém orientações políticas para concessão de terras em 418 EF, ganchos ocultos de campanha e estatísticas de fortalezas canônicas. Insira a senha para revelar.",
                gm_rendered,
                render_toc_items(gm_toc),
                codex_file=bk["out"],
                compendium_mode=False,
            )
            + '</div>'
        )

    # 6. Quick Reference Shield
    shield_html = ""
    if shield_sec:
        sh_inner, sh_toc = md_to_html(shield_sec, id_prefix="casas-ref-", card_h3=False, inject_maps=False)
        shield_html = f'<section class="casas-divider">{sh_inner}</section>'
        toc_items.extend(sh_toc)

    fort_toolbar = f"""
    <div class="casas-toolbar" role="region" aria-label="Filtros de Fortificações">
        <div class="casas-pills">
            <button class="casas-pill casas-fort-pill active" data-tier="ALL" type="button">Todas as Sedes ({total_forts})</button>
            <button class="casas-pill casas-fort-pill" data-tier="inicial" type="button">Sedes Iniciais ({fort_counts.get('inicial', 0)})</button>
            <button class="casas-pill casas-fort-pill" data-tier="menor" type="button">Praças Menores ({fort_counts.get('menor', 0)})</button>
            <button class="casas-pill casas-fort-pill" data-tier="maior" type="button">Grandes Castelos ({fort_counts.get('maior', 0)})</button>
        </div>
        <div class="casas-search-row">
            <input id="casas-fort-search" class="casas-search" type="search" placeholder="Buscar castelo, torre (F04), cultura (Gaddra, Corallis), preço ou reforma de ruína..." aria-label="Buscar fortificações"/>
            <span id="casas-fort-count" class="casas-count">Exibindo {total_forts} de {total_forts} fortificações</span>
        </div>
    </div>
    <div id="casas-fort-empty" class="casas-empty">Nenhuma fortificação corresponde aos filtros atuais.</div>
    """

    dom_toolbar = f"""
    <div class="casas-toolbar" role="region" aria-label="Filtros de Defesas, Obras e Guarnição">
        <div class="casas-pills">
            <button class="casas-pill casas-dom-pill active" data-kind="ALL" type="button">Tudo ({total_dom_items})</button>
            <button class="casas-pill casas-dom-pill" data-kind="defesa" type="button">Defesas &amp; Engenhos ({dom_counts.get('defesa', 0)})</button>
            <button class="casas-pill casas-dom-pill" data-kind="obra" type="button">Obras Produtivas ({dom_counts.get('obra', 0)})</button>
            <button class="casas-pill casas-dom-pill" data-kind="tropa" type="button">Soldados &amp; Patrulha ({dom_counts.get('tropa', 0)})</button>
            <button class="casas-pill casas-dom-pill" data-kind="corte" type="button">Trabalhadores &amp; Corte ({dom_counts.get('corte', 0)})</button>
        </div>
        <div class="casas-search-row">
            <input id="casas-dom-search" class="casas-search" type="search" placeholder="Buscar fosso (D01), trabuco (D06), moinho (D10), besteiro (G03), senescal (G11)..." aria-label="Buscar defesas, obras e pessoal"/>
            <span id="casas-dom-count" class="casas-count">Exibindo {total_dom_items} de {total_dom_items} defesas, obras e cargos</span>
        </div>
    </div>
    <div id="casas-dom-empty" class="casas-empty">Nenhum item corresponde aos filtros atuais.</div>
    """

    hero_html = f"""
    <section class="casas-hero">
        <figure class="atlas-plate casas-hero-cover">
            <img src="{bk['cover_map']}" alt="Capa — {html.escape(bk['title'])}"{img_dim_attrs(bk['cover_map'])} decoding="async"/>
        </figure>
        <div>
            <div class="casas-kicker">ALENIA RPG • {html.escape(bk['num'])} • GUIA SENHORIAL, FEUDAL E DE CERCO</div>
            <h1 class="casas-title">{html.escape(bk['title'])}</h1>
            <p class="casas-sub">Criação de Casas Nobres nas 5 culturas, custos de castelos e reforma de ruínas, obras produtivas, soldados, trabalhadores e cerco sem pólvora (Ano 418 EF).</p>
            <blockquote class="casas-epigraph">
                “Qualquer aventureiro com sorte junta um saco de prata; mas erguer uma parede que continue de pé quando você estiver morto, alimentar trinta bocas no inverno e fazer dois vizinhos armados respeitarem o seu selo — isso é fundar uma Casa.”
            </blockquote>
            <div class="casas-stats">
                <span class="casas-stat-pill">🏰 {total_forts} Fortificações Ilustradas (F01–F{total_forts:02d})</span>
                <span class="casas-stat-pill slate">🛡 16 Defesas &amp; Obras (D01–D16)</span>
                <span class="casas-stat-pill">⚔ 14 Tropas &amp; Oficiais (G01–G14)</span>
                <span class="casas-stat-pill slate">🧮 Simulador de Feudo Incluso</span>
            </div>
        </div>
    </section>
    """

    full_body = (
        hero_html
        + intro_html
        + _build_calculator_html()
        + f'<div class="casas-divider">{fort_intro_html}</div>'
        + fort_toolbar
        + f'<div id="casas-forts-root">{"".join(fort_groups_html)}</div>'
        + fort_summary_html
        + '<div class="casas-divider">'
        + dom_toolbar
        + f'<div id="casas-dom-root">{"".join(dom_groups_html)}</div>'
        + '</div>'
        + tail_html
        + gm_html
        + shield_html
    )
    return full_body, toc_items
