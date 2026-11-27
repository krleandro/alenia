#!/usr/bin/env python3
"""
Renderizador Editorial Ilustrado do Tomo XVI — O Peso do Nome, do Voto e da Sombra:
Feitos de Status (S01–S05), Fé Verdadeira (V01–V05), Submundo (U01–U05) e 30 Provações de Campanha (P01–P30)
- Inspetor Interativo de Mesa por Esfera e Grau (0 a 5) com exportação rápida
- Trilhas ilustradas com filtros e busca instantânea
- Catálogo filtrável dos 30 Feitos e Provações (por Esfera e por Grau 0->1 .. 4->5)
- Caderno Reservado ao Mestre (incluindo Dom Antigo 1–5) selado em AES-256-GCM
- Diagramação @media print A4 limpa (oculta inspetor e barras de filtro na impressão)
"""
import html
import os
import re

FEITOS_CSS = r"""
/* =====================================================
   TOMO XVI — FEITOS DE FÉ VERDADEIRA, STATUS E SUBMUNDO
   ===================================================== */
body.feitos-mode .book-shell {
    padding: 72px 18px 72px;
}
body.feitos-mode:not(.sidebar-hidden) .sidebar-backdrop {
    display: block;
}
body.feitos-mode .book-page {
    max-width: 1180px;
    padding: 34px 42px 58px;
    background: radial-gradient(circle at top center, #faf4e6 0%, #f3e9d4 58%, #eadec3 100%);
    box-shadow:
        0 26px 72px rgba(0, 0, 0, 0.7),
        0 0 0 1px rgba(154, 123, 59, 0.45);
}
body.feitos-mode .book-page::before {
    inset: 10px;
    border: 1px solid rgba(154, 123, 59, 0.34);
}

/* HERO / FRONTISPÍCIO */
.feitos-hero {
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
.feitos-hero-cover {
    margin: 0 !important;
    padding: 6px !important;
    background: #ede1c4 !important;
    border: 1px solid var(--gold) !important;
}
.feitos-hero-cover img {
    width: 100%;
    max-height: 320px;
    object-fit: cover;
    display: block;
    cursor: zoom-in;
}
.feitos-kicker {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 11px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--crimson);
    font-weight: 700;
}
.feitos-title {
    font-family: 'Cinzel', Georgia, serif !important;
    font-size: 31px !important;
    line-height: 1.15 !important;
    margin: 6px 0 8px !important;
    color: #21160d !important;
    border: none !important;
    padding: 0 !important;
}
.feitos-sub {
    font-style: italic;
    font-size: 16.8px;
    color: var(--ink-soft);
    margin: 0 0 12px;
}
.feitos-epigraph {
    font-style: italic;
    font-size: 15px;
    color: #36281b;
    border-left: 3px solid var(--crimson);
    padding: 7px 14px;
    margin: 0 0 14px;
    background: rgba(122, 31, 29, 0.06);
}
.feitos-stats {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}
.feitos-stat-pill {
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
.feitos-stat-pill.slate {
    background: rgba(42, 54, 66, 0.11);
    border-color: rgba(42, 54, 66, 0.36);
    color: #22303c;
}

/* GAVETA EDITORIAL DE LEIS GERAIS */
.feitos-editorial {
    margin: 0 0 24px;
    border: 1px solid rgba(154, 123, 59, 0.54);
    background: rgba(246, 236, 214, 0.78);
    border-radius: 3px;
    scroll-margin-top: 72px;
}
.feitos-editorial > summary {
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
.feitos-editorial > summary::-webkit-details-marker { display: none; }
.feitos-editorial > summary::after {
    content: "▾ Expandir";
    font-size: 10.5px;
    color: var(--gold);
}
.feitos-editorial[open] > summary::after { content: "▴ Recolher"; }
.feitos-editorial-inner {
    padding: 8px 22px 18px;
    border-top: 1px solid rgba(154, 123, 59, 0.28);
}

/* =====================================================
   INSPETOR INTERATIVO DE GRAUS (0 A 5) EM MESA
   ===================================================== */
.feitos-inspetor {
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
.feitos-insp-head {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding-bottom: 12px;
    margin-bottom: 14px;
    border-bottom: 1px solid rgba(154, 123, 59, 0.35);
}
.feitos-insp-kicker {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--gold-light);
    font-weight: 700;
}
.feitos-insp-title {
    font-family: 'Cinzel', Georgia, serif !important;
    font-size: 20.5px !important;
    color: #f9f2e3 !important;
    margin: 2px 0 0 !important;
    border: none !important;
    padding: 0 !important;
}
.feitos-insp-controls {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 14px;
}
.feitos-sphere-tabs,
.feitos-rank-tabs {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}
.feitos-tab-btn {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10.5px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 7px 12px;
    border-radius: 3px;
    border: 1px solid rgba(154, 123, 59, 0.5);
    background: #282018;
    color: #e9dec7;
    cursor: pointer;
    transition: all 0.14s ease;
}
.feitos-tab-btn:hover {
    border-color: var(--gold-light);
    color: #fff;
}
.feitos-tab-btn.active {
    background: var(--crimson);
    border-color: var(--gold-light);
    color: #fff8e6;
    font-weight: 700;
}
.feitos-tab-btn[data-sphere="fe"].active {
    background: #7d5b24;
}
.feitos-tab-btn[data-sphere="submundo"].active {
    background: #293845;
}
.feitos-insp-card {
    background: rgba(12, 10, 8, 0.8);
    border: 1px solid rgba(154, 123, 59, 0.42);
    border-radius: 3px;
    padding: 16px 18px;
}
.feitos-insp-banner {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    padding-bottom: 10px;
    margin-bottom: 12px;
    border-bottom: 1px solid rgba(154, 123, 59, 0.28);
}
.feitos-insp-ranktitle {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 18px;
    font-weight: 700;
    color: var(--gold-light);
}
.feitos-insp-bonus {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 11px;
    padding: 4px 10px;
    border-radius: 2px;
    background: rgba(122, 31, 29, 0.45);
    border: 1px solid var(--gold);
    color: #fff8e6;
}
.feitos-insp-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
}
.feitos-insp-box {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(154, 123, 59, 0.26);
    border-radius: 3px;
    padding: 10px 12px;
}
.feitos-insp-lbl {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 9.8px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--gold-light);
    margin-bottom: 4px;
    font-weight: 700;
}
.feitos-insp-txt {
    font-size: 14.8px;
    line-height: 1.42;
    color: #efe6d2;
}
.feitos-copy-fb {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10.5px;
    color: #7fe0a4;
    margin-left: 8px;
}

/* TOOLBARS & CARTÕES DE GRAU (S01–S05, V01–V05, U01–U05) */
.feitos-toolbar {
    background: linear-gradient(180deg, rgba(31, 24, 18, 0.97) 0%, rgba(21, 16, 12, 0.97) 100%);
    border: 1px solid rgba(154, 123, 59, 0.65);
    border-radius: 4px;
    padding: 12px 16px;
    margin: 14px 0 26px;
    box-shadow: 0 10px 26px rgba(0, 0, 0, 0.32);
    color: #efe6d2;
}
.feitos-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 10px;
}
.feitos-pill {
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
.feitos-pill:hover {
    border-color: var(--gold-light);
    color: var(--gold-light);
    background: rgba(154, 123, 59, 0.16);
}
.feitos-pill.active {
    background: var(--crimson);
    border-color: var(--gold-light);
    color: #fff8e6;
    font-weight: 700;
}
.feitos-search-row {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 10px;
}
.feitos-search {
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
.feitos-search::placeholder { color: #9c8f7a; font-style: italic; }
.feitos-count {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10.5px;
    letter-spacing: 0.08em;
    color: var(--gold-light);
    white-space: nowrap;
}

.feitos-group {
    margin: 0 0 38px;
    scroll-margin-top: 68px;
}
.feitos-group.is-hidden { display: none; }
.feitos-group-header {
    padding: 13px 18px;
    margin-bottom: 16px;
    background: linear-gradient(90deg, rgba(122, 31, 29, 0.12) 0%, rgba(154, 123, 59, 0.14) 58%, rgba(122, 31, 29, 0.04) 100%);
    border-top: 2px solid var(--crimson);
    border-bottom: 1px solid var(--gold);
    border-left: 4px solid var(--crimson);
}
.feitos-group-header.fe-hdr {
    background: linear-gradient(90deg, rgba(138, 100, 34, 0.15) 0%, rgba(154, 123, 59, 0.14) 58%, rgba(138, 100, 34, 0.04) 100%);
    border-top-color: #7d5b24;
    border-left-color: #7d5b24;
}
.feitos-group-header.sub-hdr {
    background: linear-gradient(90deg, rgba(41, 56, 69, 0.15) 0%, rgba(154, 123, 59, 0.14) 58%, rgba(41, 56, 69, 0.04) 100%);
    border-top-color: #293845;
    border-left-color: #293845;
}
.feitos-group-kicker {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--crimson);
    font-weight: 700;
}
.feitos-group-header.fe-hdr .feitos-group-kicker { color: #6e4e1c; }
.feitos-group-header.sub-hdr .feitos-group-kicker { color: #243340; }
.feitos-group-title {
    font-family: 'Cinzel', Georgia, serif !important;
    font-size: 23px !important;
    color: #201710 !important;
    margin: 2px 0 0 !important;
    border: none !important;
    padding: 0 !important;
}

.feitos-wide-plate {
    margin: 0 0 18px !important;
    padding: 8px 10px 7px !important;
    background: #efe3c8 !important;
    border: 1px solid var(--gold) !important;
    box-shadow: 0 6px 18px rgba(32, 22, 12, 0.14);
}
.feitos-wide-plate img {
    width: 100%;
    max-height: 390px;
    object-fit: contain;
    display: block;
    margin: 0 auto;
    cursor: zoom-in;
}

.feitos-rank-card {
    padding: 18px 22px;
    margin-bottom: 16px;
    background: linear-gradient(180deg, rgba(252, 247, 236, 0.96) 0%, rgba(243, 233, 212, 0.96) 100%);
    border: 1px solid rgba(154, 123, 59, 0.5);
    border-left: 4px solid var(--crimson);
    border-radius: 3px;
    box-shadow: 0 5px 15px rgba(28, 22, 14, 0.08);
    scroll-margin-top: 74px;
}
.feitos-rank-card[data-sphere="fe"] { border-left-color: #7d5b24; }
.feitos-rank-card[data-sphere="submundo"] { border-left-color: #293845; }
.feitos-rank-card.is-hidden { display: none; }
.feitos-rank-head {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
}
.feitos-code {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.1em;
    padding: 3px 9px;
    border-radius: 2px;
    background: var(--crimson);
    color: #f7f1e3;
}
.feitos-code.fe-code { background: #7d5b24; }
.feitos-code.sub-code { background: #293845; }
.feitos-code.prov-code { background: #5a4228; }
.feitos-rank-title {
    font-family: 'Cinzel', Georgia, serif !important;
    font-size: 20.5px !important;
    color: #1f160e !important;
    margin: 0 !important;
    border: none !important;
    padding: 0 !important;
}
.feitos-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 10px;
}
.feitos-tag {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 9.8px;
    letter-spacing: 0.04em;
    padding: 3px 8px;
    border-radius: 2px;
    background: rgba(154, 123, 59, 0.14);
    border: 1px solid rgba(154, 123, 59, 0.42);
    color: #48341c;
    font-weight: 600;
}
.feitos-rank-card ul {
    margin: 6px 0 0;
    padding-left: 20px;
}
.feitos-rank-card li {
    margin-bottom: 6px;
    line-height: 1.5;
}

/* CATÁLOGO DOS 30 FEITOS & PROVAÇÕES (P01–P30) */
.feitos-prov-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
    margin: 14px 0 22px;
}
.feitos-prov-card {
    padding: 16px 18px;
    background: linear-gradient(180deg, rgba(252, 246, 234, 0.94) 0%, rgba(243, 233, 212, 0.94) 100%);
    border: 1px solid rgba(154, 123, 59, 0.48);
    border-top: 3px solid var(--crimson);
    border-radius: 3px;
    box-shadow: 0 4px 12px rgba(34, 22, 12, 0.08);
    scroll-margin-top: 74px;
}
.feitos-prov-card[data-sphere="fe"] { border-top-color: #7d5b24; }
.feitos-prov-card[data-sphere="submundo"] { border-top-color: #293845; }
.feitos-prov-card.is-hidden { display: none; }
.feitos-prov-head {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
    padding-bottom: 6px;
    border-bottom: 1px dotted rgba(154, 123, 59, 0.45);
}
.feitos-prov-card h3 {
    font-family: 'Cinzel', Georgia, serif !important;
    font-size: 16.8px !important;
    color: #24170e !important;
    margin: 0 !important;
    border: none !important;
    padding: 0 !important;
}
.feitos-prov-card p {
    font-size: 15.2px;
    line-height: 1.48;
    margin: 0 0 8px;
    text-align: left;
}
.feitos-prov-card p:last-child { margin-bottom: 0; }

.feitos-divider {
    margin-top: 36px;
    padding-top: 22px;
    border-top: 2px solid var(--gold);
    scroll-margin-top: 68px;
}
.feitos-empty {
    display: none;
    text-align: center;
    padding: 28px 18px;
    border: 1px dashed var(--gold);
    background: rgba(246, 236, 214, 0.72);
    font-style: italic;
    color: var(--ink-soft);
    margin: 12px 0 24px;
}
.feitos-empty.visible { display: block; }

@media screen and (max-width: 920px) {
    body.feitos-mode .book-page { padding: 22px 18px 42px; }
    .feitos-hero { grid-template-columns: 1fr; text-align: center; padding: 20px; }
    .feitos-hero-cover { max-width: 230px; margin: 0 auto !important; }
    .feitos-stats { justify-content: center; }
    .feitos-insp-grid,
    .feitos-prov-grid { grid-template-columns: 1fr; }
}

@media print {
    .feitos-inspetor,
    .feitos-toolbar,
    .feitos-empty,
    .feitos-editorial > summary::after {
        display: none !important;
    }
    .feitos-hero {
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
    .feitos-hero-cover { max-width: none !important; margin: 0 !important; }
    .feitos-hero-cover img { max-height: 220px !important; object-fit: cover !important; }
    .feitos-title { font-size: 20pt !important; }
    .feitos-sub { font-size: 10.2pt !important; margin-bottom: 8px !important; }
    .feitos-epigraph { font-size: 9.5pt !important; padding: 6px 12px !important; margin-bottom: 10px !important; }
    .feitos-stat-pill { font-size: 8pt !important; padding: 3px 8px !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .feitos-editorial { margin: 0 0 14px !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .feitos-editorial-inner { padding: 4px 16px 12px !important; font-size: 9.6pt; }
    .feitos-group { margin: 0 0 20px !important; }
    .feitos-group-header {
        padding: 9px 14px !important;
        margin-bottom: 10px !important;
        break-inside: avoid;
        page-break-inside: avoid;
        break-after: avoid;
        page-break-after: avoid;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }
    .feitos-group-title { font-size: 15pt !important; }
    .feitos-wide-plate {
        margin: 0 0 10px !important;
        padding: 5px !important;
        box-shadow: none !important;
        break-inside: avoid;
        page-break-inside: avoid;
    }
    .feitos-wide-plate img { max-height: 102mm !important; }
    .feitos-rank-card {
        padding: 11px 14px !important;
        margin-bottom: 10px !important;
        box-shadow: none !important;
        break-inside: avoid;
        page-break-inside: avoid;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }
    .feitos-rank-title { font-size: 13pt !important; }
    .feitos-rank-card li, .feitos-rank-card p { font-size: 9.4pt !important; line-height: 1.36 !important; margin-bottom: 4px !important; }
    .feitos-prov-grid {
        display: grid !important;
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
        gap: 10px !important;
        margin: 8px 0 14px !important;
    }
    .feitos-prov-card {
        padding: 9px 11px !important;
        box-shadow: none !important;
        break-inside: avoid;
        page-break-inside: avoid;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }
    .feitos-prov-card h3 { font-size: 11pt !important; }
    .feitos-prov-card p { font-size: 9pt !important; line-height: 1.35 !important; margin-bottom: 4px !important; }
    .feitos-code, .feitos-tag { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
}
"""

FEITOS_JS = r"""
(function() {
    const INSPECTOR_DATA = {
        status: [
            { rank: 0, code: "Grau 0", title: "Status 0 — Plebeu ou Forasteiro Sem Fiador", bonus: "Bônus Direto: +0", req: "Posição inicial padrão da maioria dos exploradores.", passivo: "Sem privilégios legais especiais; estalagens pedem adiantado e guardas revistam bagagens nos portões.", ativo: "Nenhum privilégio de patente; depende exclusivamente de suas perícias e moedas.", queda: "Já está na base social." },
            { rank: 1, code: "S01", title: "S01 · Grau 1 — Nome Reconhecido", bonus: "Bônus Direto: +1 | Modesto (15 PP/mês)", req: "Serviço comprovado a Cavaleiro/Guilda, defesa pública de vila/navio ou diploma/carta de ofício.", passivo: "Porte legal de armas comuns em cidades muradas; palavra válida em tribunal local; acesso a arquivos e salões inferiores de guilda.", ativo: "1×/sessão (Carta de Apresentação): hospedagem digna por 3 dias, audiência com oficial local ou fiança até 30 PP sem rolagem.", queda: "Ser pego em furto comum, calote público ou briga covarde revoga a carta (volta a 0)." },
            { rank: 2, code: "S02", title: "S02 · Grau 2 — Voz de Salão e Patente (Sor / Dama)", bonus: "Bônus Direto: +2 | Confortável (45 PP/mês)", req: "Consagração de Cavalaria, salvar vida/honra de nobre/patrício ou comandar navio/caravana em crise grave.", passivo: "Julgamento por Pares e direito a resgate (200–500 PP); crédito em Cera Azul até 200 PP sem fiador; habilita sedes F01–F04.", ativo: "1×/sessão (Palavra de Patente): requisita 2–4 guardas locais em emergência pública ou suspende ordem policial menor por 24h (+2 Etiqueta/Persuasão).", queda: "Quebrar juramento de cavalaria, abandonar escoltados ou deixar Letra em Cera Azul protestada." },
            { rank: 3, code: "S03", title: "S03 · Grau 3 — Senhorio, Foral e Cadeira", bonus: "Bônus Direto: +3 | Abastado (150 PP/mês)", req: "Fundar/reerguer Casa Nobre com Foral (Tomo XV), vencer/impedir cerco ou solucionar crise provincial inteira.", passivo: "Baixa Justiça no feudo; tropa própria sob brasão; isenção de pedágios locais; crédito de 800 PP; assento em concílios provinciais (F04–F07).", ativo: "1×/arco (Selo de Senhorio): emite Salvo-Condutos Oficiais para o grupo, requisita cavalos de muda ou audiência em 48h com Grande Lorde/Almirante.", queda: "Perder a sede sem lutar, tiranizar aldeias sob foral ou falir perante o Tesouro." },
            { rank: 4, code: "S04", title: "S04 · Grau 4 — Grande Nome do Domínio", bonus: "Bônus Direto: +4 | Aristocrático (450+ PP/mês)", req: "Mudar o rumo político/militar de um domínio inteiro (evitar guerra civil, salvar capital/Grande Casa, unificar clãs).", passivo: "Alta Justiça; voz nos altos conselhos; crédito estratégico de 3.000 PP; intocável por autoridades menores (F08–F09).", ativo: "1×/arco (Convocação de Estandartes): mobiliza 1 galé de guerra (E09), 20–40 soldados (G02/G03) ou embargo portuário temporário.", queda: "Alta traição comprovada, derrota catastrófica ou ruína provincial." },
            { rank: 5, code: "S05", title: "S05 · Grau 5 — Voz que Move Reinos", bonus: "Bônus Direto: +5 | Soberano / Cidadela F10", req: "Ápice histórico de campanha: deter ameaça existencial continental, assumir Regência/Coroa ou selar pacto entre nações.", passivo: "Autoridade soberana/continental; cria cavaleiros e barões (Status 1–3), legitima bastardos e trata de igual com qualquer governante.", ativo: "1×/campanha (Decreto Histórico): proclama édito, trégua geral ou convocação continental que redesenha o mapa político.", queda: "Abandonar o povo quando o mundo escurece (como Aemilius IV em 356 EF)." }
        ],
        fe: [
            { rank: 0, code: "Grau 0", title: "Fé Verdadeira 0 — Crente Comum, Político ou Cético", bonus: "Bônus Direto: +0", req: "Estado padrão (mesmo para clérigos de carreira sem provação espiritual real).", passivo: "Depende apenas de SAB normal contra o medo e os sussurros de Thanatos.", ativo: "Pode rezar por tradição, mas sem efeito mecânico especial.", queda: "—" },
            { rank: 1, code: "V01", title: "V01 · Grau 1 — Centelha Sincera", bonus: "Bônus Direto: +1 | Plural nas 5 Tradições", req: "Recusar lucro/atalho em cena por fidelidade ao preceito, cuidar de enfermos sob risco ou cumprir voto difícil.", passivo: "+1 contra medo, intimidação e pesadelos; clérigos/anciãos sinceros reconhecem sua honestidade e oferecem abrigo simples.", ativo: "1×/Descanso Longo (Prece da Lareira): 10 min de prece concedem a até 4 aliados +1 no 1º teste contra medo ou Exaustão climática em 24h.", queda: "Mentir invocando o sagrado por ganho egoísta apaga a centelha (volta a 0)." },
            { rank: 2, code: "V02", title: "V02 · Grau 2 — Guardião do Voto", bonus: "Bônus Direto: +2 | Direito de Asilo", req: "Sofrer ferimento, perda ou perseguição por defender inocente/asilo, honrar a Passagem ou conduzir rito menor altruísta.", passivo: "+2 contra terror, ecos de Thanatos e impulsos do Simbionte (Estágio II); invoca Direito de Asilo fazendo guardas hesitarem (+2).", ativo: "1×/Descanso Longo (Vigília de Consolação): 1h velando feridos concede +2 PV extras a até 5 aliados OU +2 no teste de CON contra Doenças.", queda: "Entregar suplicante sob seu asilo ou cobrar prata por socorro espiritual urgente." },
            { rank: 3, code: "V03", title: "V03 · Grau 3 — Pilar Incorruptível", bonus: "Bônus Direto: +3 | Sentido de Profanação", req: "Salvar desconhecidos em quarentena letal, encarar Thanatos/Incognito sem recuar ou interpor-se desarmado contra massacre.", passivo: "+3 contra pavor e Simbionte (Estágios II–III); -3 na CD de extração do Simbionte; pressente profanação/rito de sangue ao cruzar a soleira.", ativo: "1×/sessão (Voz que Acalma a Turba): Ação Principal sem atacar (CD 15) encerra pânico coletivo em 9m e impõe -2 em humanos que tentem atacá-lo.", queda: "Insuflar linchamento de inocentes ou usar autoridade sagrada para enriquecer." },
            { rank: 4, code: "V04", title: "V04 · Grau 4 — Vaso da Vigília", bonus: "Bônus Direto: +4 | Imune a Medo Comum", req: "Oferecer a própria vida/liberdade para salvar comunidade inteira ou purificar foco profanado em vigília completa.", passivo: "Imune a medo mundano (+4 vs sobrenatural/Comunhão); +2 na Moral de fortaleza/navio; presença conta como Local Consagrado (+2).", ativo: "1×/arco (Ainda Não Chegou Minha Hora): em ato altruísta de proteção, permanece de pé e consciente com 1 PV ao falhar contra Golpe Devastador ou cair a 0 PV.", queda: "Soberba espiritual ou cumplicidade com crueldade deliberada." },
            { rank: 5, code: "V05", title: "V05 · Grau 5 — Testemunha da Luz Antiga", bonus: "Bônus Direto: +5 | Incorruptível", req: "Clímax espiritual de campanha: sustentar o voto no coração de Thanatos/Incognito recusando falsa imortalidade ou poder proibido.", passivo: "Imune a possessão, pavor e impulsos da Comunhão (+5); dobra moralmente zelotes e tiranos que ergam a mão sem causa.", ativo: "1×/campanha (Sinal Inesquecível): realiza prodígio sutil histórico (CD 28–30) sem sacrifício de sangue alheio (ex.: despertar hospedeiro em Estágio III–IV).", queda: "Quebrar o voto supremo apaga o atributo para sempre." }
        ],
        submundo: [
            { rank: 0, code: "Grau 0", title: "Submundo 0 — Forasteiro Ingênuo nos Becos", bonus: "Bônus Direto: +0 | Ágio Negro 3×", req: "Estado padrão de quem vive apenas à luz da lei.", passivo: "Paga 3× no mercado negro e corre risco constante de logro ou emboscada ao procurar itens ilegais.", ativo: "Nenhum acesso seguro às redes clandestinas.", queda: "—" },
            { rank: 1, code: "U01", title: "U01 · Grau 1 — Conhecido nos Becos", bonus: "Bônus Direto: +1 | Sinais de Cais", req: "Calar sob interrogatório da guarda, salvar parceiro da patrulha ou quitar dívida difícil nos trapiches.", passivo: "Lê sinais de giz e gírias de porto; acha em 1d4h receptador (50%) e cirurgião discreto sem cair em armadilha amadora.", ativo: "1×/sessão (Porta dos Fundos): obtém esconderijo modesto por 1 noite OU descobre qual guarda aceita suborno padrão (5–15 PP).", queda: "Delatar esconderijo/contato à guarda zera o atributo e põe preço na sua cabeça." },
            { rank: 2, code: "U02", title: "U02 · Grau 2 — Mão de Confiança", bonus: "Bônus Direto: +2 | Ágio Negro 2×", req: "Furar bloqueio/alfândega com carga sensível, desmascarar informante duplo ou executar infiltração limpa.", passivo: "Reduz ágio do Mercado Negro para 2×; receptadores pagam 60%; acesso a falsificadores de guias/cartas (CD 18, 25–50 PP).", ativo: "1×/sessão (Sumir na Neblina): infiltra ou retira o grupo inteiro de cidade murada sem passar pelos portões (20 PP ou 1 favor menor).", queda: "Falhar contrato pago adiantado sem restituir a prata suspende a rede." },
            { rank: 3, code: "U03", title: "U03 · Grau 3 — Nome sob o Capuz", bonus: "Bônus Direto: +3 | Ágio 1,5× & Talhas", req: "Controlar rota clandestina, derrubar chefe rival/preboste corrupto ou negociar operação crítica no Ferro Velho/Dobalbek.", passivo: "Menor ágio do Mercado Negro (1,5×); usa Talhas Cifradas de Kalis sem intermediário; 1 esconderijo fixo por grande porto; +2 c/ G14.", ativo: "1×/arco (Dossiê de Sombra): em 24h obtém sem rolagem 1 segredo concreto sobre NPC não-soberano OU planta pista falsa por 3 dias.", queda: "Dar calote em Talha Cifrada decreta sentença de morte silenciosa." },
            { rank: 4, code: "U04", title: "U04 · Grau 4 — Aranha dos Portos e Cortes", bonus: "Bônus Direto: +4 | Bandeira de Trégua", req: "Golpe clandestino que mude o equilíbrio de uma cidade inteira ou una capitães corsários sob pacto.", passivo: "Ladrões e piratas menores evitam atacar o grupo; acesso a venenos da Ilha das Safiras, selos CD 22 e -15% em estaleiros ocultos.", ativo: "1×/arco (Bandeira de Trégua / Interdição Negra): parlamento inviolável com qualquer facção criminosa OU bloqueia rival no mercado negro por 1 mês.", queda: "Violar sangue sob Bandeira de Trégua une todo o submundo contra você." },
            { rank: 5, code: "U05", title: "U05 · Grau 5 — Lenda Sem Rosto", bonus: "Bônus Direto: +5 | Ouvidos em Toda Parte", req: "Ápice clandestino: controlar teia entre domínios, dobrar célula dos Ceifos de Kalis ou deter segredos que abalam coroas.", passivo: "Nenhum contrato profissional de morte/sabotagem no submundo é aceito contra o grupo sem aviso prévio chegar às suas mãos.", ativo: "1×/campanha (Noite das Portas Abertas): paralisa docas de metrópole, apaga arquivos reais ou resgata alvo de cidadela máxima.", queda: "Qualquer traição ou sinal de fraqueza atrai sucessores letais." }
        ]
    };

    function initInspector() {
        const root = document.getElementById('inspetor-graus');
        if (!root) return;
        let curSphere = 'status';
        let curRank = 3;

        const sphereBtns = Array.from(root.querySelectorAll('.feitos-sphere-btn'));
        const rankBtns = Array.from(root.querySelectorAll('.feitos-rank-btn'));

        function render() {
            const list = INSPECTOR_DATA[curSphere] || INSPECTOR_DATA.status;
            const item = list[curRank] || list[0];
            document.getElementById('fi-title').textContent = item.title;
            document.getElementById('fi-bonus').textContent = item.bonus;
            document.getElementById('fi-req').textContent = item.req;
            document.getElementById('fi-passivo').textContent = item.passivo;
            document.getElementById('fi-ativo').textContent = item.ativo;
            document.getElementById('fi-queda').textContent = item.queda;

            root._copyText = [
                `=== ${item.title} (${item.bonus}) ===`,
                `Feitos Exigidos: ${item.req}`,
                `Efeito Passivo: ${item.passivo}`,
                `Uso Ativo: ${item.ativo}`,
                `Dever / Queda: ${item.queda}`
            ].join('\n');
        }

        sphereBtns.forEach(btn => btn.addEventListener('click', () => {
            curSphere = btn.dataset.sphere;
            sphereBtns.forEach(x => x.classList.toggle('active', x === btn));
            render();
        }));
        rankBtns.forEach(btn => btn.addEventListener('click', () => {
            curRank = parseInt(btn.dataset.rank, 10) || 0;
            rankBtns.forEach(x => x.classList.toggle('active', x === btn));
            render();
        }));
        document.getElementById('fi-copy')?.addEventListener('click', async () => {
            const fb = document.getElementById('fi-copy-fb');
            try {
                await navigator.clipboard.writeText(root._copyText || '');
                if (fb) { fb.textContent = '✓ Copiado!'; setTimeout(() => { fb.textContent = ''; }, 2000); }
            } catch (_) {}
        });

        render();
    }

    function initFilters() {
        const norm = (s) => (s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();

        // Track filter (S01-S05, V01-V05, U01-U05)
        const trkRoot = document.getElementById('feitos-trilhas-root');
        const trkPills = Array.from(document.querySelectorAll('.feitos-trk-pill'));
        const trkSearch = document.getElementById('feitos-trk-search');
        const trkCount = document.getElementById('feitos-trk-count');
        const trkEmpty = document.getElementById('feitos-trk-empty');
        let trkSphere = 'ALL';

        function applyTrkFilter() {
            if (!trkRoot) return;
            const q = norm(trkSearch ? trkSearch.value.trim() : '');
            let shown = 0;
            const all = trkRoot.querySelectorAll('.feitos-rank-card');
            trkRoot.querySelectorAll('.feitos-group').forEach(grp => {
                const ok = (trkSphere === 'ALL' || grp.dataset.sphere === trkSphere);
                let gShown = 0;
                grp.querySelectorAll('.feitos-rank-card').forEach(c => {
                    const m = ok && (!q || norm(c.dataset.search).includes(q));
                    c.classList.toggle('is-hidden', !m);
                    if (m) { gShown++; shown++; }
                });
                grp.classList.toggle('is-hidden', gShown === 0);
            });
            if (trkCount) trkCount.textContent = `Exibindo ${shown} de ${all.length} graus canônicos`;
            if (trkEmpty) trkEmpty.classList.toggle('visible', shown === 0);
        }

        trkPills.forEach(p => p.addEventListener('click', () => {
            trkSphere = p.dataset.sphere;
            trkPills.forEach(x => x.classList.toggle('active', x === p));
            applyTrkFilter();
        }));
        if (trkSearch) trkSearch.addEventListener('input', applyTrkFilter);

        // Provacoes filter (P01-P30)
        const provRoot = document.getElementById('feitos-prov-root');
        const provPills = Array.from(document.querySelectorAll('.feitos-prov-pill'));
        const provDegPills = Array.from(document.querySelectorAll('.feitos-deg-pill'));
        const provSearch = document.getElementById('feitos-prov-search');
        const provCount = document.getElementById('feitos-prov-count');
        const provEmpty = document.getElementById('feitos-prov-empty');
        let provSphere = 'ALL';
        let provDeg = 'ALL';

        function applyProvFilter() {
            if (!provRoot) return;
            const q = norm(provSearch ? provSearch.value.trim() : '');
            let shown = 0;
            const all = provRoot.querySelectorAll('.feitos-prov-card');
            provRoot.querySelectorAll('.feitos-group').forEach(grp => {
                let gShown = 0;
                grp.querySelectorAll('.feitos-prov-card').forEach(c => {
                    const sOk = (provSphere === 'ALL' || c.dataset.sphere === provSphere);
                    const dOk = (provDeg === 'ALL' || c.dataset.deg === provDeg);
                    const m = sOk && dOk && (!q || norm(c.dataset.search).includes(q));
                    c.classList.toggle('is-hidden', !m);
                    if (m) { gShown++; shown++; }
                });
                grp.classList.toggle('is-hidden', gShown === 0);
            });
            if (provCount) provCount.textContent = `Exibindo ${shown} de ${all.length} feitos e provações`;
            if (provEmpty) provEmpty.classList.toggle('visible', shown === 0);
        }

        provPills.forEach(p => p.addEventListener('click', () => {
            provSphere = p.dataset.sphere;
            provPills.forEach(x => x.classList.toggle('active', x === p));
            applyProvFilter();
        }));
        provDegPills.forEach(p => p.addEventListener('click', () => {
            provDeg = p.dataset.deg;
            provDegPills.forEach(x => x.classList.toggle('active', x === p));
            applyProvFilter();
        }));
        if (provSearch) provSearch.addEventListener('input', applyProvFilter);

        window.aleniaRevealAnchor = function(id) {
            const el = document.getElementById(id);
            if (!el) return;
            if (el.closest('.feitos-rank-card.is-hidden') || el.closest('#feitos-trilhas-root .feitos-group.is-hidden')) {
                trkSphere = 'ALL';
                trkPills.forEach(x => x.classList.toggle('active', x.dataset.sphere === 'ALL'));
                if (trkSearch) trkSearch.value = '';
                applyTrkFilter();
            }
            if (el.closest('.feitos-prov-card.is-hidden') || el.closest('#feitos-prov-root .feitos-group.is-hidden')) {
                provSphere = 'ALL';
                provDeg = 'ALL';
                provPills.forEach(x => x.classList.toggle('active', x.dataset.sphere === 'ALL'));
                provDegPills.forEach(x => x.classList.toggle('active', x.dataset.deg === 'ALL'));
                if (provSearch) provSearch.value = '';
                applyProvFilter();
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
            document.querySelectorAll('.feitos-group.is-hidden, .feitos-rank-card.is-hidden, .feitos-prov-card.is-hidden').forEach(el => {
                el.classList.remove('is-hidden');
            });
            if (trkEmpty) trkEmpty.classList.remove('visible');
            if (provEmpty) provEmpty.classList.remove('visible');
        };
        const restorePrint = () => {
            applyTrkFilter();
            applyProvFilter();
        };
        window.addEventListener('alenia:prepare-print', revealForPrint);
        window.addEventListener('beforeprint', revealForPrint);
        window.addEventListener('alenia:restore-print', restorePrint);
        window.addEventListener('afterprint', restorePrint);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => { initInspector(); initFilters(); });
    } else {
        initInspector();
        initFilters();
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


def _build_inspector_html() -> str:
    return """
    <section id="inspetor-graus" class="feitos-inspetor" aria-label="Inspetor Rápido de Graus 0 a 5">
        <div class="feitos-insp-head">
            <div>
                <div class="feitos-insp-kicker">CONSULTA RÁPIDA DE MESA • TOMO XVI &amp; FIRECAST v2.7</div>
                <h2 class="feitos-insp-title">⚖ Inspetor de Graus (0 a 5): Feitos, Privilégios &amp; Quedas</h2>
            </div>
            <div>
                <a class="feitos-tab-btn" href="https://raw.githubusercontent.com/krleandro/alenia/main/plugins/Alenia_RPG_Ficha.rpk" style="text-decoration:none; display:inline-block;">⬇ Ficha Firecast v2.7 (.rpk)</a>
                <button id="fi-copy" class="feitos-tab-btn active" type="button">📋 Copiar Grau</button>
                <span id="fi-copy-fb" class="feitos-copy-fb" aria-live="polite"></span>
            </div>
        </div>
        <div class="feitos-insp-controls">
            <div class="feitos-sphere-tabs">
                <button class="feitos-tab-btn feitos-sphere-btn active" data-sphere="status" type="button">👑 Status (0–5)</button>
                <button class="feitos-tab-btn feitos-sphere-btn" data-sphere="fe" type="button">🕯 Fé Verdadeira (0–5)</button>
                <button class="feitos-tab-btn feitos-sphere-btn" data-sphere="submundo" type="button">🗡 Submundo (0–5)</button>
            </div>
            <div class="feitos-rank-tabs">
                <button class="feitos-tab-btn feitos-rank-btn" data-rank="0" type="button">Grau 0</button>
                <button class="feitos-tab-btn feitos-rank-btn" data-rank="1" type="button">Grau 1</button>
                <button class="feitos-tab-btn feitos-rank-btn" data-rank="2" type="button">Grau 2</button>
                <button class="feitos-tab-btn feitos-rank-btn active" data-rank="3" type="button">Grau 3</button>
                <button class="feitos-tab-btn feitos-rank-btn" data-rank="4" type="button">Grau 4</button>
                <button class="feitos-tab-btn feitos-rank-btn" data-rank="5" type="button">Grau 5</button>
            </div>
        </div>
        <div class="feitos-insp-card">
            <div class="feitos-insp-banner">
                <span id="fi-title" class="feitos-insp-ranktitle">S03 · Grau 3 — Senhorio, Foral e Cadeira</span>
                <span id="fi-bonus" class="feitos-insp-bonus">Bônus Direto: +3</span>
            </div>
            <div class="feitos-insp-grid">
                <div class="feitos-insp-box">
                    <div class="feitos-insp-lbl">✦ Feitos Exigidos para Alcançar</div>
                    <div id="fi-req" class="feitos-insp-txt"></div>
                </div>
                <div class="feitos-insp-box">
                    <div class="feitos-insp-lbl">🛡 Direitos / Firmeza Passiva</div>
                    <div id="fi-passivo" class="feitos-insp-txt"></div>
                </div>
                <div class="feitos-insp-box">
                    <div class="feitos-insp-lbl">⚡ Uso Ativo em Mesa</div>
                    <div id="fi-ativo" class="feitos-insp-txt"></div>
                </div>
                <div class="feitos-insp-box">
                    <div class="feitos-insp-lbl">⚠ Dever Assumido &amp; Gatilho de Queda</div>
                    <div id="fi-queda" class="feitos-insp-txt"></div>
                </div>
            </div>
        </div>
    </section>
    """


def render_feitos_page(bk: dict, md_content: str, helpers: dict):
    """Build interactive illustrated Tomo XVI — Feitos de Fé Verdadeira, Status e Submundo page."""
    inline_md = helpers["inline_md"]
    md_to_html = helpers["md_to_html"]
    img_dim_attrs = helpers["img_dim_attrs"]
    make_gm_gate_block = helpers["make_gm_gate_block"]
    render_toc_items = helpers["render_toc_items"]

    sections = re.split(r"(?=^##\s+)", md_content, flags=re.M)

    laws_sec = ""
    track_secs = []
    prov_intro_md = ""
    prov_secs = []
    gm_sec = ""
    shield_sec = ""

    track_map = {
        "Trilha do Status: o peso do nome nas cinco culturas": ("status", "", "feitos-group-header", "ESFERA I • HONRA PÚBLICA, PATENTES, CRÉDITO E SENHORIO (S01–S05)"),
        "Trilha da Fé Verdadeira: o voto incorruptível": ("fe", "fe-code", "feitos-group-header fe-hdr", "ESFERA II • CONVICÇÃO ESPIRITUAL PLURAL, ASILO E FIRMEZA DIANTE DO HORROR (V01–V05)"),
        "Trilha do Submundo: os fios invisíveis da sombra": ("submundo", "sub-code", "feitos-group-header sub-hdr", "ESFERA III • CONTRABANDO, TALHAS CIFRADAS, CORSAIRISMO E REDES OCULTAS (U01–U05)"),
    }

    prov_map = {
        "Dez feitos exemplares de Status": ("status", "feitos-group-header", "MARCOS DE CAMPANHA • PROVAÇÕES DE STATUS (P01–P10)"),
        "Dez provações exemplares de Fé Verdadeira": ("fe", "feitos-group-header fe-hdr", "MARCOS DE CAMPANHA • PROVAÇÕES DE FÉ VERDADEIRA (P11–P20)"),
        "Dez feitos exemplares de Submundo": ("submundo", "feitos-group-header sub-hdr", "MARCOS DE CAMPANHA • OPERAÇÕES DO SUBMUNDO (P21–P30)"),
    }

    for sec in sections:
        s = sec.strip()
        m_h2 = re.match(r"^##\s+(.+)$", s, flags=re.M)
        if not m_h2:
            continue
        title = m_h2.group(1).strip()
        if title.startswith("Leis gerais"):
            laws_sec = s
        elif title in track_map:
            track_secs.append((title, s))
        elif title.startswith("Catálogo de trinta"):
            prov_intro_md = s
        elif title in prov_map:
            prov_secs.append((title, s))
        elif title.lower().startswith("caderno reservado ao mestre"):
            gm_sec = s
        elif title.startswith("Referência rápida"):
            shield_sec = s

    toc_items = [
        (2, "Leis Gerais dos Feitos, Atrito e Queda", "leis-gerais"),
        (2, "Inspetor Rápido de Graus (0 a 5)", "inspetor-graus"),
    ]

    # 1. Laws & Equilibrium Drawer
    laws_inner, _ = md_to_html(laws_sec, id_prefix="leis-", card_h3=False, inject_maps=False)
    laws_html = f"""
    <details class="feitos-editorial" id="leis-gerais" open>
        <summary>⚖ Os Três Critérios de Evolução, Rolagens, Atrito Entre Esferas &amp; Regras de Mancha e Queda</summary>
        <div class="feitos-editorial-inner">{laws_inner}</div>
    </details>
    """

    # 2. Three Tracks (S01–S05, V01–V05, U01–U05)
    track_groups_html = []
    total_ranks = 0
    for t_title, t_raw in track_secs:
        sp_key, code_cls, hdr_cls, kicker = track_map[t_title]
        grp_id = f"trilha-{sp_key}"
        toc_items.append((2, t_title, grp_id))

        parts = re.split(r"(?=^###\s+[SVU]0[1-5]\s)", t_raw, flags=re.M)
        intro_lines = parts[0].splitlines()[1:]
        plate_html = ""
        intro_md_rest = []
        for ln in intro_lines:
            m_img = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", ln.strip())
            if m_img and not plate_html:
                palt = m_img.group(1).strip() or t_title
                psrc = "assets/" + os.path.basename(m_img.group(2).strip())
                plate_html = (
                    f'<figure class="atlas-plate feitos-wide-plate" title="Clique para ampliar prancha">'
                    f'<img src="{html.escape(psrc, quote=True)}" alt="{html.escape(palt, quote=True)}"{img_dim_attrs(psrc)} decoding="async"/>'
                    f'<figcaption class="atlas-caption">{html.escape(palt)}</figcaption>'
                    f'</figure>'
                )
            else:
                intro_md_rest.append(ln)

        intro_rendered, _ = md_to_html("\n".join(intro_md_rest), id_prefix=f"trk-in-{sp_key}-", card_h3=False, inject_maps=False)

        r_cards = []
        for rblk in parts[1:]:
            rlines = rblk.strip().splitlines()
            if not rlines:
                continue
            m_rh = re.match(r"^###\s+([SVU]0[1-5])\s+[—–-]\s+(.+)$", rlines[0].strip())
            if not m_rh:
                continue
            rcode, rname = m_rh.group(1), m_rh.group(2).strip()
            total_ranks += 1

            tags = []
            body_md_lines = []
            for ln in rlines[1:]:
                st = ln.strip()
                if not st:
                    body_md_lines.append("")
                    continue
                if not body_md_lines and st.startswith("**") and ("Posição:" in st or "Caminhada:" in st or "Reputação:" in st):
                    for k_lbl, v_lbl in _parse_bold_pairs(st):
                        tags.append(f'<span class="feitos-tag">{html.escape(k_lbl)}: {inline_md(v_lbl)}</span>')
                else:
                    body_md_lines.append(ln)

            rbody_html, _ = md_to_html("\n".join(body_md_lines), id_prefix=f"rk-{rcode.lower()}-", card_h3=False, inject_maps=False)
            s_blob = html.escape(f"{rcode} {rname} {t_title} {' '.join(rlines[1:])}", quote=True)
            c_cls = f"feitos-code {code_cls}".strip()
            r_cards.append(f"""
            <article class="feitos-rank-card" id="{rcode.lower()}" data-sphere="{sp_key}" data-search="{s_blob}">
                <div class="feitos-rank-head">
                    <span class="{c_cls}">{html.escape(rcode)}</span>
                    <h3 class="feitos-rank-title">{html.escape(rname)}</h3>
                </div>
                <div class="feitos-tags">{"".join(tags)}</div>
                {rbody_html}
            </article>
            """)

        track_groups_html.append(f"""
        <section class="feitos-group" id="{grp_id}" data-sphere="{sp_key}">
            <header class="{hdr_cls}">
                <div class="feitos-group-kicker">{kicker}</div>
                <h2 class="feitos-group-title">{html.escape(t_title)}</h2>
            </header>
            {plate_html}
            {intro_rendered}
            {"".join(r_cards)}
        </section>
        """)

    # 3. 30 Exemplary Feats & Ordeals (P01–P30)
    prov_intro_html = ""
    if prov_intro_md:
        prov_intro_html, _ = md_to_html(prov_intro_md, id_prefix="prov-top-", card_h3=False, inject_maps=False)

    prov_groups_html = []
    total_provs = 0
    for p_title, p_raw in prov_secs:
        sp_key, hdr_cls, kicker = prov_map[p_title]
        p_id = f"catalogo-{sp_key}"
        toc_items.append((2, p_title, p_id))

        p_parts = re.split(r"(?=^###\s+P\d{2}\s)", p_raw, flags=re.M)
        p_cards = []
        for pblk in p_parts[1:]:
            plines = [ln.strip() for ln in pblk.strip().splitlines() if ln.strip()]
            if not plines:
                continue
            m_ph = re.match(r"^###\s+(P\d{2})\s+[—–-]\s+(.+)$", plines[0])
            if not m_ph:
                continue
            pcode, pname = m_ph.group(1), m_ph.group(2).strip()
            total_provs += 1

            ptags = []
            pbody = []
            deg_key = "1"
            for idx_l, pl in enumerate(plines[1:]):
                if idx_l == 0 and pl.startswith("**"):
                    m_deg = re.search(r"→\s*([1-5])", pl)
                    if m_deg:
                        deg_key = m_deg.group(1)
                    for k_lbl, v_lbl in _parse_bold_pairs(pl):
                        ptags.append(f'<span class="feitos-tag">{html.escape(k_lbl)}: {inline_md(v_lbl)}</span>')
                else:
                    pbody.append(pl)

            pbody_html, _ = md_to_html("\n\n".join(pbody), id_prefix=f"pv-{pcode.lower()}-", card_h3=False, inject_maps=False)
            psearch = html.escape(f"{pcode} {pname} {p_title} {' '.join(plines[1:])}", quote=True)
            p_cards.append(f"""
            <article class="feitos-prov-card" id="{pcode.lower()}" data-sphere="{sp_key}" data-deg="{deg_key}" data-search="{psearch}">
                <div class="feitos-prov-head">
                    <span class="feitos-code prov-code">{html.escape(pcode)}</span>
                    <h3>{html.escape(pname)}</h3>
                </div>
                <div class="feitos-tags">{"".join(ptags)}</div>
                {pbody_html}
            </article>
            """)

        prov_groups_html.append(f"""
        <section class="feitos-group" id="{p_id}">
            <header class="{hdr_cls}">
                <div class="feitos-group-kicker">{kicker}</div>
                <h2 class="feitos-group-title">{html.escape(p_title)}</h2>
            </header>
            <div class="feitos-prov-grid">{"".join(p_cards)}</div>
        </section>
        """)

    # 4. Sealed GM Vault (includes Dom Antigo 1–5)
    gm_html = ""
    if gm_sec:
        gm_rendered, gm_toc = md_to_html(gm_sec, id_prefix="feitos-gm-", card_h3=False, inject_maps=False)
        gm_html = (
            '<div class="feitos-divider">'
            + make_gm_gate_block(
                "Caderno Reservado ao Mestre — Arbitragem, Dom Antigo (1–5) e Segredos",
                "Contém a progressão oculta de Dom Antigo (1 a 5), bastidores da Chama Branca, ganchos de 418 EF e guia de arbitragem. Insira a senha para revelar.",
                gm_rendered,
                render_toc_items(gm_toc),
                codex_file=bk["out"],
                compendium_mode=False,
            )
            + '</div>'
        )

    # 5. Quick Reference Shield
    shield_html = ""
    if shield_sec:
        sh_inner, sh_toc = md_to_html(shield_sec, id_prefix="feitos-ref-", card_h3=False, inject_maps=False)
        shield_html = f'<section class="feitos-divider">{sh_inner}</section>'
        toc_items.extend(sh_toc)

    trk_toolbar = f"""
    <div class="feitos-toolbar" role="region" aria-label="Filtros das Trilhas 1 a 5">
        <div class="feitos-pills">
            <button class="feitos-pill feitos-trk-pill active" data-sphere="ALL" type="button">Todas as Trilhas ({total_ranks})</button>
            <button class="feitos-pill feitos-trk-pill" data-sphere="status" type="button">👑 Status (S01–S05)</button>
            <button class="feitos-pill feitos-trk-pill" data-sphere="fe" type="button">🕯 Fé Verdadeira (V01–V05)</button>
            <button class="feitos-pill feitos-trk-pill" data-sphere="submundo" type="button">🗡 Submundo (U01–U05)</button>
        </div>
        <div class="feitos-search-row">
            <input id="feitos-trk-search" class="feitos-search" type="search" placeholder="Buscar grau, título cultural (Sor, Arconte, Xeique), Simbionte, Talha Cifrada, crédito..." aria-label="Buscar nas trilhas"/>
            <span id="feitos-trk-count" class="feitos-count">Exibindo {total_ranks} de {total_ranks} graus canônicos</span>
        </div>
    </div>
    <div id="feitos-trk-empty" class="feitos-empty">Nenhum grau corresponde aos filtros atuais.</div>
    """

    prov_toolbar = f"""
    <div class="feitos-toolbar" role="region" aria-label="Filtros dos 30 Feitos e Provações">
        <div class="feitos-pills">
            <button class="feitos-pill feitos-prov-pill active" data-sphere="ALL" type="button">Todas as Esferas ({total_provs})</button>
            <button class="feitos-pill feitos-prov-pill" data-sphere="status" type="button">👑 Status (10)</button>
            <button class="feitos-pill feitos-prov-pill" data-sphere="fe" type="button">🕯 Fé Verdadeira (10)</button>
            <button class="feitos-pill feitos-prov-pill" data-sphere="submundo" type="button">🗡 Submundo (10)</button>
        </div>
        <div class="feitos-pills">
            <button class="feitos-pill feitos-deg-pill active" data-deg="ALL" type="button">Todos os Degraus</button>
            <button class="feitos-pill feitos-deg-pill" data-deg="1" type="button">Grau 0 → 1</button>
            <button class="feitos-pill feitos-deg-pill" data-deg="2" type="button">Grau 1 → 2</button>
            <button class="feitos-pill feitos-deg-pill" data-deg="3" type="button">Grau 2 → 3</button>
            <button class="feitos-pill feitos-deg-pill" data-deg="4" type="button">Grau 3 → 4</button>
            <button class="feitos-pill feitos-deg-pill" data-deg="5" type="button">Grau 4 → 5</button>
        </div>
        <div class="feitos-search-row">
            <input id="feitos-prov-search" class="feitos-search" type="search" placeholder="Buscar feito exemplar (Ferraur, Ferro Velho, Ravena, Thanatos, Gaddra, P01–P30)..." aria-label="Buscar feitos exemplares"/>
            <span id="feitos-prov-count" class="feitos-count">Exibindo {total_provs} de {total_provs} feitos e provações</span>
        </div>
    </div>
    <div id="feitos-prov-empty" class="feitos-empty">Nenhum feito ou provação corresponde aos filtros atuais.</div>
    """

    hero_html = f"""
    <section class="feitos-hero">
        <figure class="atlas-plate feitos-hero-cover">
            <img src="{bk['cover_map']}" alt="Capa — {html.escape(bk['title'])}"{img_dim_attrs(bk['cover_map'])} decoding="async"/>
        </figure>
        <div>
            <div class="feitos-kicker">ALENIA RPG • {html.escape(bk['num'])} • EVOLUÇÃO POR FEITOS (GRAUS 1 A 5)</div>
            <h1 class="feitos-title">{html.escape(bk['title'])}</h1>
            <p class="feitos-sub">Regras completas de progressão, privilégios, provações e quedas de Status, Fé Verdadeira e Submundo nas cinco culturas de Alenia (Ano 418 EF).</p>
            <blockquote class="feitos-epigraph">
                “O ouro compra um cavalo, uma espada e até o silêncio de um estalajadeiro por uma noite. Mas existem três moedas neste continente que nenhum cofre cunha: o nome que abre um portão sem desembainhar o aço, a prece que não treme diante da bruma, e o sinal a giz que impede uma garganta de ser cortada no beco.”
            </blockquote>
            <div class="feitos-stats">
                <span class="feitos-stat-pill">👑 Status 1–5 (S01–S05)</span>
                <span class="feitos-stat-pill slate">🕯 Fé Verdadeira 1–5 (V01–V05)</span>
                <span class="feitos-stat-pill">🗡 Submundo 1–5 (U01–U05)</span>
                <span class="feitos-stat-pill slate">📜 {total_provs} Provações (P01–P{total_provs:02d})</span>
            </div>
        </div>
    </section>
    """

    full_body = (
        hero_html
        + laws_html
        + _build_inspector_html()
        + trk_toolbar
        + f'<div id="feitos-trilhas-root">{"".join(track_groups_html)}</div>'
        + f'<div class="feitos-divider">{prov_intro_html}</div>'
        + prov_toolbar
        + f'<div id="feitos-prov-root">{"".join(prov_groups_html)}</div>'
        + gm_html
        + shield_html
    )
    return full_body, toc_items
