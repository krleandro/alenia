#!/usr/bin/env python3
"""
Renderizador Editorial Ilustrado do Tomo XVII — Atlas Feudal, Regências e Intrigas de Alenia:
- 22 Domínios e Feudos Canônicos (L01–L22): Coroa em Altavanne, 7 Feudos de Aurora (Merlinport, Dahrma c/ Lavroga,
  Vaarsa, Yõketsu, Altrax, Aeraneas, Cidades Suspensas) e 14 Feudos dos 3 Reinos Vassalos (Corallis, Gaddra, Kalis)
- 8 Frentes Quentes de Litígio e Intriga (Z01–Z08): Voernock (Yõketsu x Vaarsa), Lavroga sob Dahrma, Montes Ferraur
  (Cidades Suspensas x Aeraneas), Pântanos Nebulosos, Grande Concílio, Recifes, Rubecina e Sul Kalita
- Explorador Interativo da Cadeia de Vassalagem & Bônus de Concessão + Sorteador 1d12 de Intrigas
- Caderno Reservado ao Mestre selado em AES-256-GCM e layout A4 PDF limpo (@media print)
"""
import html
import os
import re

FEUDOS_CSS = r"""
/* =====================================================
   TOMO XVII — ATLAS FEUDAL, REGÊNCIAS E INTRIGAS
   ===================================================== */
body.feudos-mode .book-shell {
    padding: 72px 18px 72px;
}
body.feudos-mode:not(.sidebar-hidden) .sidebar-backdrop {
    display: block;
}
body.feudos-mode .book-page {
    max-width: 1180px;
    padding: 34px 42px 58px;
    background: radial-gradient(circle at top center, #faf4e6 0%, #f3e9d4 58%, #eadec3 100%);
    box-shadow:
        0 26px 72px rgba(0, 0, 0, 0.7),
        0 0 0 1px rgba(154, 123, 59, 0.45);
}
body.feudos-mode .book-page::before {
    inset: 10px;
    border: 1px solid rgba(154, 123, 59, 0.34);
}

/* HERO / FRONTISPÍCIO */
.feudos-hero {
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
.feudos-hero-cover {
    margin: 0 !important;
    padding: 6px !important;
    background: #ede1c4 !important;
    border: 1px solid var(--gold) !important;
}
.feudos-hero-cover img {
    width: 100%;
    max-height: 325px;
    object-fit: cover;
    display: block;
    cursor: zoom-in;
}
.feudos-kicker {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 11px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--crimson);
    font-weight: 700;
}
.feudos-title {
    font-family: 'Cinzel', Georgia, serif !important;
    font-size: 30px !important;
    line-height: 1.15 !important;
    margin: 6px 0 8px !important;
    color: #21160d !important;
    border: none !important;
    padding: 0 !important;
}
.feudos-sub {
    font-style: italic;
    font-size: 16.5px;
    color: var(--ink-soft);
    margin: 0 0 12px;
}
.feudos-epigraph {
    font-style: italic;
    font-size: 14.8px;
    color: #36281b;
    border-left: 3px solid var(--crimson);
    padding: 7px 14px;
    margin: 0 0 14px;
    background: rgba(122, 31, 29, 0.06);
}
.feudos-stats {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}
.feudos-stat-pill {
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
.feudos-stat-pill.slate {
    background: rgba(31, 70, 88, 0.11);
    border-color: rgba(31, 70, 88, 0.36);
    color: #183a4a;
}

/* GAVETA EDITORIAL DA PIRÂMIDE */
.feudos-editorial {
    margin: 0 0 24px;
    border: 1px solid rgba(154, 123, 59, 0.54);
    background: rgba(246, 236, 214, 0.78);
    border-radius: 3px;
    scroll-margin-top: 72px;
}
.feudos-editorial > summary {
    cursor: pointer;
    padding: 11px 18px;
    font-family: 'Cinzel', Georgia, serif;
    font-size: 12.5px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--crimson-dark);
    font-weight: 700;
    background: rgba(154, 123, 59, 0.14);
}
.feudos-editorial-inner {
    padding: 18px 22px 12px;
}

/* EXPLORADOR INTERATIVO DA CADEIA FEUDAL */
.feudos-inspector {
    margin: 0 0 26px;
    padding: 20px 22px 22px;
    background: linear-gradient(180deg, #211a14 0%, #17120e 100%);
    color: #f4ebd9;
    border: 2px solid #9a7b3b;
    border-radius: 4px;
    box-shadow: 0 14px 32px rgba(24, 15, 8, 0.32);
    scroll-margin-top: 72px;
}
.feudos-insp-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
    padding-bottom: 12px;
    margin-bottom: 14px;
    border-bottom: 1px solid rgba(217, 185, 106, 0.28);
}
.feudos-insp-kicker {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10.5px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #d9b96a;
    font-weight: 700;
}
.feudos-insp-title {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 19px;
    color: #fff6e3;
    margin: 2px 0 0;
}
.feudos-insp-controls {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 14px;
}
.feudos-realm-tabs,
.feudos-fief-tabs {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}
.feudos-tab-btn {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 11px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 6px 11px;
    background: rgba(255, 248, 232, 0.07);
    color: #dfd2b7;
    border: 1px solid rgba(217, 185, 106, 0.34);
    border-radius: 3px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.14s ease;
}
.feudos-tab-btn:hover {
    background: rgba(217, 185, 106, 0.2);
    color: #fff8e8;
}
.feudos-tab-btn.active {
    background: #8a2420;
    border-color: #e6c677;
    color: #fff9eb;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35);
}
.feudos-insp-card {
    background: rgba(252, 245, 230, 0.96);
    color: #24190e;
    border: 1px solid #b89550;
    border-radius: 3px;
    padding: 16px 18px;
}
.feudos-insp-banner {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    flex-wrap: wrap;
    gap: 8px;
    border-bottom: 1px solid rgba(122, 31, 29, 0.24);
    padding-bottom: 8px;
    margin-bottom: 10px;
}
.feudos-insp-domtitle {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 18px;
    font-weight: 700;
    color: #6b1b19;
}
.feudos-insp-chain {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 11.5px;
    font-weight: 700;
    padding: 3px 9px;
    border-radius: 2px;
    background: rgba(122, 31, 29, 0.11);
    border: 1px solid rgba(122, 31, 29, 0.35);
    color: #5a1513;
}
.feudos-insp-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px 14px;
}
.feudos-insp-box {
    background: rgba(239, 227, 200, 0.65);
    border-left: 3px solid #8a6c2f;
    padding: 8px 11px;
    border-radius: 2px;
}
.feudos-insp-lbl {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10.5px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #6b1b19;
    font-weight: 700;
    margin-bottom: 3px;
}
.feudos-insp-txt {
    font-size: 14.3px;
    line-height: 1.45;
    color: #261b10;
}
.feudos-copy-fb {
    font-size: 12px;
    color: #9de0a8;
    margin-left: 8px;
}

/* TOOLBAR DE FILTROS & SORTEADOR 1D12 */
.feudos-toolbar {
    margin: 14px 0 20px;
    padding: 13px 16px;
    background: #241c15;
    border: 1px solid #9a7b3b;
    border-radius: 4px;
    display: flex;
    flex-direction: column;
    gap: 10px;
}
.feudos-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}
.feudos-pill {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10.8px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 5px 10px;
    border-radius: 3px;
    border: 1px solid rgba(217, 185, 106, 0.36);
    background: rgba(255, 248, 232, 0.07);
    color: #e2d5ba;
    cursor: pointer;
    font-weight: 600;
}
.feudos-pill:hover {
    background: rgba(217, 185, 106, 0.2);
    color: #fff9eb;
}
.feudos-pill.active {
    background: #7a1f1d;
    border-color: #e6c677;
    color: #fff8ea;
}
.feudos-search-row {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
}
.feudos-search {
    flex: 1;
    min-width: 240px;
    padding: 8px 12px;
    border-radius: 3px;
    border: 1px solid #8a6c2f;
    background: #faf3e3;
    color: #22170d;
    font-family: inherit;
    font-size: 14.5px;
}
.feudos-count {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 11px;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    color: #d9b96a;
}
.feudos-empty {
    display: none;
    padding: 18px;
    text-align: center;
    font-style: italic;
    background: rgba(122, 31, 29, 0.08);
    border: 1px dashed var(--crimson);
    margin-bottom: 18px;
}

/* CABEÇALHOS DE GRUPO & PRANCHAS */
.feudos-group {
    margin: 26px 0 30px;
    scroll-margin-top: 72px;
}
.feudos-group-header {
    padding: 12px 18px;
    margin-bottom: 16px;
    border-left: 4px solid var(--crimson);
    background: linear-gradient(90deg, rgba(122, 31, 29, 0.12) 0%, rgba(246, 236, 214, 0.3) 100%);
    border-top: 1px solid rgba(154, 123, 59, 0.35);
    border-bottom: 1px solid rgba(154, 123, 59, 0.35);
}
.feudos-group-header.corallis-hdr {
    border-left-color: #1b4965;
    background: linear-gradient(90deg, rgba(27, 73, 101, 0.13) 0%, rgba(246, 236, 214, 0.3) 100%);
}
.feudos-group-header.gaddra-hdr {
    border-left-color: #8a5c1f;
    background: linear-gradient(90deg, rgba(138, 92, 31, 0.14) 0%, rgba(246, 236, 214, 0.3) 100%);
}
.feudos-group-header.kalis-hdr {
    border-left-color: #293845;
    background: linear-gradient(90deg, rgba(41, 56, 69, 0.14) 0%, rgba(246, 236, 214, 0.3) 100%);
}
.feudos-group-kicker {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10.5px;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--crimson);
    font-weight: 700;
}
.feudos-group-title {
    font-family: 'Cinzel', Georgia, serif !important;
    font-size: 22px !important;
    margin: 3px 0 0 !important;
    border: none !important;
    padding: 0 !important;
    color: #22170d !important;
}
.feudos-wide-plate {
    margin: 14px 0 20px !important;
}
.feudos-wide-plate img {
    width: 100%;
    max-height: 460px;
    object-fit: contain;
    display: block;
    margin: 0 auto;
    cursor: zoom-in;
}

/* CARDS DOS 22 FEUDOS (L01–L22) */
.feudos-card {
    background: rgba(252, 246, 233, 0.9);
    border: 1px solid rgba(154, 123, 59, 0.52);
    border-left: 4px solid var(--crimson);
    border-radius: 3px;
    padding: 16px 20px 14px;
    margin: 0 0 16px;
    box-shadow: 0 4px 14px rgba(42, 26, 12, 0.07);
    scroll-margin-top: 78px;
}
.feudos-card[data-realm="corallis"] { border-left-color: #1b4965; }
.feudos-card[data-realm="gaddra"]   { border-left-color: #8a5c1f; }
.feudos-card[data-realm="kalis"]    { border-left-color: #293845; }

.feudos-card-head {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
    padding-bottom: 8px;
    margin-bottom: 10px;
    border-bottom: 1px dotted rgba(122, 31, 29, 0.35);
}
.feudos-code {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.08em;
    padding: 3px 8px;
    border-radius: 2px;
    background: #7a1f1d;
    color: #fff7e6;
}
.feudos-code.corallis-code { background: #1b4965; }
.feudos-code.gaddra-code   { background: #8a5c1f; }
.feudos-code.kalis-code    { background: #293845; }
.feudos-code.litigio-code  { background: #5a2d18; }

.feudos-card-title {
    font-family: 'Cinzel', Georgia, serif !important;
    font-size: 18.5px !important;
    margin: 0 !important;
    border: none !important;
    padding: 0 !important;
    color: #21160d !important;
}
.feudos-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 10px;
}
.feudos-tag {
    font-size: 12.8px;
    padding: 3px 9px;
    border-radius: 2px;
    background: rgba(154, 123, 59, 0.14);
    border: 1px solid rgba(154, 123, 59, 0.38);
    color: #3a2815;
}

/* GRID DE DISPUTAS E LITÍGIOS (Z01–Z08) */
.feudos-dispute-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 15px;
}
.feudos-dispute-card {
    background: rgba(251, 243, 228, 0.93);
    border: 1px solid rgba(138, 43, 40, 0.42);
    border-top: 3px solid #7a1f1d;
    border-radius: 3px;
    padding: 15px 19px 13px;
    box-shadow: 0 4px 12px rgba(42, 26, 12, 0.07);
    scroll-margin-top: 78px;
}

/* SORTEADOR DE INTRIGA 1D12 */
.feudos-roller-bar {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
    padding: 12px 16px;
    margin: 10px 0 16px;
    background: #231b14;
    color: #f5ecda;
    border: 1px solid #9a7b3b;
    border-radius: 4px;
}
.feudos-roller-out {
    flex: 1;
    min-width: 240px;
    font-size: 14.5px;
    color: #f7eedb;
}
.feudos-roller-out strong {
    color: #f0d283 !important;
}

.feudos-divider {
    margin-top: 28px;
    padding-top: 18px;
    border-top: 2px solid rgba(154, 123, 59, 0.42);
}
.is-hidden {
    display: none !important;
}

@media (max-width: 820px) {
    .feudos-hero {
        grid-template-columns: 1fr;
    }
    .feudos-hero-cover img {
        max-width: 230px;
        margin: 0 auto;
    }
    .feudos-insp-grid {
        grid-template-columns: 1fr;
    }
    body.feudos-mode .book-page {
        padding: 22px 18px 42px;
    }
}

@media print {
    #explorador-feudal,
    .feudos-toolbar,
    .feudos-roller-bar,
    .feudos-empty {
        display: none !important;
    }
    body.feudos-mode .book-shell {
        padding: 0 !important;
    }
    body.feudos-mode .book-page {
        max-width: 100% !important;
        padding: 0 !important;
        box-shadow: none !important;
        background: #fff !important;
    }
    .feudos-hero,
    .feudos-card,
    .feudos-dispute-card,
    .feudos-group-header {
        break-inside: avoid;
        page-break-inside: avoid;
        box-shadow: none !important;
    }
    .is-hidden {
        display: block !important;
    }
}
"""

FEUDOS_JS = r"""
(function () {
    const FIEFS_DATA = [
        { code: "L01", realm: "aurora", short: "L01 Altavanne (Coroa)", title: "L01 · Domínio Régio de Altavanne e Pontáuria", chain: "Ápice Imperial — Coroa Solar de Alenia", lord: "Alto Rei Severor III (N003) / Regente Valora Valerion (N004) • Casa Valerion (Sub-feudo: Pontáuria, N018)", dispute: "Z05: Sucessão Contestada e Grande Concílio em Altavanne", bonus: "+1 em Etiqueta e Persuasão perante magistrados reais; -10% na contratação de Senescal (G11) e Mestre de Armas (G12).", hook: "Todos os 7 Feudos de Aurora e os 3 Regentes Vassalos respondem a Altavanne." },
        { code: "L02", realm: "aurora", short: "L02 Merlinport", title: "L02 · Feudo de Merlinport", chain: "Casa do PJ → Feudo de Merlinport → Altavanne (L01)", lord: "Lorde Marcus Scutauria (N014) • Casa Scutauria (Lady Serina N013 na Balança)", dispute: "Z04: Corredor fluvial dos Pântanos Nebulosos, Torre de Specula e tarifas de guerra", bonus: "-20% no custo de Armazéns e Cais (D14) e +15 PP/mês adicionais por cada D14 ativo.", hook: "Sustenta Valora enquanto o comércio continuar aberto; vigia espiões de Kalis e despertos no cais." },
        { code: "L03", realm: "aurora", short: "L03 Dahrma (+Lavroga)", title: "L03 · Feudo de Dahrma (Suserano de Lavroga)", chain: "Casa do PJ / Lavroga → Feudo de Dahrma → Altavanne (L01)", lord: "Lorde Lorian Montavalle (N012) • Casa Montavalle (Sub-vassalo: Castelão Galeran de Lavroga)", dispute: "Z02: Dahrma controla Lavroga — tensão pelas taxas sobre mós de moinho e cantaria", bonus: "+15 PP/mês adicionais na 1ª Aldeia Arrendada (D09) e -15% no custo de Moinhos (D10).", hook: "Maior celeiro de Aurora; Leonastis tenta seduzir Lavroga prometendo emancipá-la de Dahrma." },
        { code: "L04", realm: "aurora", short: "L04 Vaarsa", title: "L04 · Feudo de Vaarsa", chain: "Casa do PJ → Feudo de Vaarsa → Altavanne (L01)", lord: "Marechal Lucian Leonastis (N006) • Casa Leonastis", dispute: "Z01: Disputa o Pântano de Voernock contra Yõketsu (L05) | Z07: Passo de Rubecina", bonus: "-15% no custo inicial de Soldados Regulares (G02) e Infantes Pesados (G04); +1 Moral em cerco.", hook: "Lidera a ala marcial que exige o Grande Concílio e quer cercar o leste através de Voernock." },
        { code: "L05", realm: "aurora", short: "L05 Yõketsu", title: "L05 · Feudo de Yõketsu", chain: "Casa do PJ → Feudo de Yõketsu → Altavanne (L01)", lord: "Senhor Feudal (Kenshu) Kenshin Tsurumaru • Casa Tsurumaru", dispute: "Z01: Disputa o Pântano de Voernock contra Vaarsa (L04)", bonus: "+1 no Índice de Defesa de tropas leves/arqueiros (G02/G03) e -15% manutenção naval costeira.", hook: "Enclave oriental sob o Foral das Garças; seu voto no Concílio depende da fronteira de Voernock." },
        { code: "L06", realm: "aurora", short: "L06 Altrax", title: "L06 · Feudo de Altrax", chain: "Casa do PJ → Feudo de Altrax → Altavanne (L01)", lord: "Castelã Aurelia d'Altrax (N016) • Casa d'Altrax (Primo: Cassian N017 nos Selos)", dispute: "Z04: Pântanos Nebulosos, Torre de Specula e desaparecimento de Cadwyn (N025)", bonus: "Reforma de ruínas custa 40% do preço novo (em vez de 45%) e +2 em alertas de patrulha.", hook: "Guarda ressentimento antigo da promessa recuada de 356 EF; recusa tutelas da capital e de Vaarsa." },
        { code: "L07", realm: "aurora", short: "L07 Aeraneas", title: "L07 · Feudo de Aeraneas", chain: "Casa do PJ → Feudo de Aeraneas → Altavanne (L01)", lord: "Grão-Lorde Aurelian Ferraris (N015) • Casa Ferraris", dispute: "Z03: Disputa os Montes Ferraur contra as Cidades Suspensas (L08) + Greve mineira", bonus: "Forja Senhorial (D12) pela metade do preço (750 PP) e +20 PP/mês extras com Mestre Ferreiro (G10).", hook: "Coração do adamante paralisado após 40 mortes; prospecções a leste inflamam os Montes Ferraur." },
        { code: "L08", realm: "aurora", short: "L08 Cidades Suspensas", title: "L08 · Feudo das Cidades Suspensas (e Vergod)", chain: "Casa do PJ → Feudo das Cidades Suspensas → Altavanne (L01)", lord: "Senhora-Guardiã Aerwen ferch Taldor (N024) • Conselho das Copas", dispute: "Z03: Disputa os Montes Ferraur contra Aeraneas (L07) por nascentes e mineração ilegal", bonus: "-25% no custo de Motas (F03) e Ervanários (D15); Físico/Herbalista (G13) dobra cataplasmas.", hook: "Reconhecido perante a Coroa pelo Foral de Vergod; exige o retorno de Cadwyn (N025)." },

        { code: "L09", realm: "corallis", short: "L09 Alineus (Regente)", title: "L09 · Feudo-Sede de Alineus", chain: "Feudo-Sede do Arconte-Regente Corardo della Rocca → Altavanne (L01)", lord: "Arconte-Regente Corardo della Rocca (N021) • Casa della Rocca", dispute: "Z06: Guerra tarifária dos recifes contra Baldbella (L10) e O Ferro Velho (N026)", bonus: "-15% em reparos/compra naval e +15 PP/mês em Cais Mercantil (D14).", hook: "Governa Corallis em nome de Altavanne enquanto financia expedição discreta a Thanatos." },
        { code: "L10", realm: "corallis", short: "L10 Baldbella", title: "L10 · Feudo Mercantil de Baldbella", chain: "Casa do PJ → Baldbella → Regente della Rocca (L09) → Altavanne (L01)", lord: "Síndico-Patrício Valerio Corvella • Casa Corvella", dispute: "Z06: Boicote das taxas de pilotagem e salvamento contra Alineus", bonus: "+50% teto de crédito em Cera Azul e -30% no salário de Físico Cirurgião (G13).", hook: "Ameaça apelar direto a Altavanne pedindo a troca do Regente se perder tarifas dos recifes." },
        { code: "L11", realm: "corallis", short: "L11 Stoneforge", title: "L11 · Feudo Forjador de Stoneforge", chain: "Casa do PJ → Stoneforge → Regente della Rocca (L09) → Altavanne (L01)", lord: "Mestre-Barão Orso Rupefori • Casa Rupefori", dispute: "Escassez crítica de pontas de adamante devido à greve em Aeraneas (L07)", bonus: "-20% no custo de Balistas (D05) e Trabucos (D06) e +1 nos tiros de muralha.", hook: "Oficinas tentadas a comprar adamante recuperado sem selo vindo de O Ferro Velho." },
        { code: "L12", realm: "corallis", short: "L12 Biemont & Portocala", title: "L12 · Feudo Bancário de Biemont e Portocala", chain: "Casa do PJ → Biemont → Regente della Rocca (L09) → Altavanne (L01)", lord: "Dama Lorenza Falcenzo (N086) • Casa Falcenzo", dispute: "Z06: Compra de hipotecas navais e trato velado com sucateiros do sul", bonus: "Juros bancários reduzidos pela metade e +20 PP/mês em Estalagens/Cais (D11/D14).", hook: "Usa seguros marítimos para transformar dívidas de armadores em poder político." },
        { code: "L13", realm: "corallis", short: "L13 Sellene & Claramar", title: "L13 · Claustro-Feudo de Sellene e Claramar", chain: "Sellene → Regente della Rocca (L09) [Civil] & Altavanne (L01) [Acervo]", lord: "Arquimestre Matteo dal Pelago (N031) • Academia de Sellene", dispute: "Pressão sobre o Acervo Oculto e corrida secreta por registros de Thanatos", bonus: "+2 em Contraespionagem documental, História e Investigação da Casa.", hook: "Dupla lealdade delicada entre o Conselho da Liga e o juramento secreto ao Alto Rei." },

        { code: "L14", realm: "gaddra", short: "L14 Naasar (Regente)", title: "L14 · Emirado-Sede de Naasar e Lago Bayd", chain: "Sede do Regente das Dunas Qasir Zaharid → Altavanne (L01)", lord: "Regente das Dunas Qasir Zaharid (N022) • Clã Zaharid", dispute: "Z07: Assassinato do Árbitro (N068) e risco de bloqueio na Rota do Sal", bonus: "-30% no custo de Cisterna Abobadada (D07) e proteção hídrica em Naasar.", hook: "Controla o aquífero profundo e o sal de Bayd entre Altavanne e as tribos livres." },
        { code: "L15", realm: "gaddra", short: "L15 OX", title: "L15 · Feudo das Arenas e Coudelarias de OX", chain: "Casa do PJ → OX → Regente Qasir Zaharid (L14) → Altavanne (L01)", lord: "Emir Khalur al-Shams • Clã al-Shams", dispute: "Venda ambígua de montarias tanto a Vaarsa quanto a clãs rebeldes", bonus: "-25% no custo de Coudelaria (D16) e -5 PP/mês extras por tropa montada (G05/G06).", hook: "Coração equestre e mercantil do interior árido; joga nos dois tabuleiros da fronteira." },
        { code: "L16", realm: "gaddra", short: "L16 Qal-Zahar & Suq-Ramad", title: "L16 · Feudo Costeiro de Qal-Zahar e Suq-Ramad", chain: "Casa do PJ → Qal-Zahar → Regente Qasir Zaharid (L14) → Altavanne (L01)", lord: "Senhor Tarik ibn Sahir • Clã Sahirid", dispute: "Z07: Lucra com o desvio marítimo caso o Passo de Rubecina feche", bonus: "+20 PP/mês em Estalagem/Feitoria (D11) ou Cais Costeiro (D14).", hook: "Porta marítima do Mar de Zahar e sede da grande feira sazonal do sul." },
        { code: "L17", realm: "gaddra", short: "L17 Vargheim", title: "L17 · Marca Montanhesa de Vargheim", chain: "Casa do PJ → Vargheim → Regente Qasir Zaharid (L14) → Altavanne (L01)", lord: "Chefe-Vigia Halvor Sangue-Seco • Clã Sangue-Seco", dispute: "Z07: Clãs da escarpa exigem fechar o Passo de Rubecina contra Aurora", bonus: "+1 Moral permanente na guarnição e +2 em Intimidação/combate montanhoso.", hook: "Vassalagem por um fio: qualquer faísca na fronteira detona guerra contra Vaarsa (L04)." },

        { code: "L18", realm: "kalis", short: "L18 Kalgard (Regente)", title: "L18 · Feudo-Sede da Cidadela de Kalgard", chain: "Sede do Déspota-Regente Grimrik Ulscold → Altavanne (L01)", lord: "Déspota-Regente Grimrik Ulscold (N023) • Casa Ulscold", dispute: "Z08: Tensão silenciosa com Dobalbek/Fugong e corrida por Thanatos", bonus: "+2 em Contraespionagem da Casa e -25% no salário de Mestre de Sussurros (G14).", hook: "Remete madeira negra em dia a Altavanne para governar Kalis sem interferência externa." },
        { code: "L19", realm: "kalis", short: "L19 Kragstad", title: "L19 · Feudo Naval de Kragstad", chain: "Casa do PJ → Kragstad → Déspota Grimrik Ulscold (L18) → Altavanne (L01)", lord: "Lorde-Vigia Torvald von Kragstad • Casa von Kragstad (N083)", dispute: "Atrito militar contra corsários de Ravena e operações sujas do Véu", bonus: "-15% no custo de Forte Costeiro (F07) e defesas de muralha (D02–D05).", hook: "Principal escudo naval do norte kalita; exige honra marítima acima de intrigas." },
        { code: "L20", realm: "kalis", short: "L20 Drakenhall", title: "L20 · Feudo Judicial e Florestal de Drakenhall", chain: "Casa do PJ → Drakenhall → Déspota Grimrik Ulscold (L18) → Altavanne (L01)", lord: "Jarl Borhild Hrafngard (N082) • Casa Hrafngard", dispute: "Controle dos estoques de madeira negra naval que sustentam o tributo régio", bonus: "-25% no custo de Serrarias (D13) e +20 PP/mês em exportação madeireira.", hook: "Sem as vigas de Hrafngard nem Kalgard paga Altavanne nem Dobalbek lança navios." },
        { code: "L21", realm: "kalis", short: "L21 Dobalbek", title: "L21 · Feudo Portuário e Bancário de Dobalbek", chain: "Casa do PJ → Dobalbek → Déspota Grimrik Ulscold (L18) → Altavanne (L01)", lord: "Dama-Chanceler Freydis Drakenvorn (N084) • Casa Drakenvorn", dispute: "Z08: Pressão mercantil por comércio aberto com Aurora versus vigilância estatal", bonus: "Taxa de Talhas Cifradas reduzida à metade (4%) e -15% em Cais/Estaleiros (D14).", hook: "Ponte financeira e marítima voltada diretamente para a costa leste de Aurora." },
        { code: "L22", realm: "kalis", short: "L22 Fugong & Kalima", title: "L22 · Feudo Vidreiro e Alquímico de Fugong e Kalima", chain: "Casa do PJ → Fugong → Déspota Grimrik Ulscold (L18) → Altavanne (L01)", lord: "Intendente-Senhor Ragnar Skoldhavn • Casa Skoldhavn", dispute: "Z08: Oposição mercantil a Kalgard e contrabando com a Ilha das Safiras", bonus: "+25 PP/mês em Oficinas/Ervanários alquímicos (D12/D15).", hook: "Fornos de vidro escuro temperado (N085) cobiçados por mercadores de Corallis." }
    ];

    const INTRIGUES_1D12 = [
        "1 — Marco de Pedra Arrancado na Calada da Noite (Z01 Voernock ou Z03 Ferraur • Investigação/História CD 16).",
        "2 — Comboio Retido por 'Vistoria Sanitária' (Merlinport, Lavroga ou Baldbella • Etiqueta/Barganha + Status CD 17).",
        "3 — Pupilo Nobre Desaparecido na Estrada (Hóspede-garantia entre duas Casas • Sobrevivência/Intuição CD 15).",
        "4 — Dois Forais com Selos Verdadeiros (Vaarsa × Yõketsu ou Aeraneas × Cidades Suspensas • História CD 18).",
        "5 — Emissário do Regente Pede Segredo contra Altavanne — ou vice-versa (Corallis, Gaddra ou Kalis).",
        "6 — Duelo de Campeões no Juízo do Dia (Barões contratam campeão externo • Armas Brancas + Status S02+).",
        "7 — Casamento Político Sabotado às Vésperas da Aliança (Carta ameaça romper a Paz do Teto • CD 16).",
        "8 — Sublevação Fiscal na Sub-castelania (Lavroga Z02 ou Vargheim Z07 recusam entregar cota sem escolta).",
        "9 — Leilão Silencioso de Dívida Nobre (Hipoteca de solar fronteiriço vendida em Biemont/Dobalbek • 500–1.500 PP).",
        "10 — Inspeção Surpresa do Preboste ou da Chama Branca (Revista de paióis, masmorras e livros de pedágio • CD 16).",
        "11 — Sinal Naval Estrangeiro na Costa Fechada (Lanternas escuras entre dois feudos rivais • Navegação/Furtividade CD 15).",
        "12 — Convocação Urgente de Voto ou Estandarte (Arautos rivais exigem resposta formal da Casa em 72 horas!)."
    ];

    let curRealm = "aurora";
    let curCode = "L03";

    const fiefTabsWrap = document.getElementById("feudos-fief-tabs");
    const elTitle = document.getElementById("fd-title");
    const elChain = document.getElementById("fd-chain");
    const elLord = document.getElementById("fd-lord");
    const elDispute = document.getElementById("fd-dispute");
    const elBonus = document.getElementById("fd-bonus");
    const elHook = document.getElementById("fd-hook");
    const btnCopy = document.getElementById("fd-copy");
    const elCopyFb = document.getElementById("fd-copy-fb");

    function renderInspector() {
        if (!fiefTabsWrap || !elTitle) return;
        const realmFiefs = FIEFS_DATA.filter(f => f.realm === curRealm);
        if (!realmFiefs.some(f => f.code === curCode)) {
            curCode = realmFiefs[0].code;
        }
        fiefTabsWrap.innerHTML = realmFiefs.map(f =>
            `<button class="feudos-tab-btn feudos-fief-btn${f.code === curCode ? ' active' : ''}" data-code="${f.code}" type="button">${f.short}</button>`
        ).join("");

        fiefTabsWrap.querySelectorAll(".feudos-fief-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                curCode = btn.getAttribute("data-code");
                renderInspector();
            });
        });

        const cur = FIEFS_DATA.find(f => f.code === curCode) || FIEFS_DATA[0];
        elTitle.textContent = cur.title;
        elChain.textContent = cur.chain;
        elLord.textContent = cur.lord;
        elDispute.textContent = cur.dispute;
        elBonus.textContent = cur.bonus;
        elHook.textContent = cur.hook;
    }

    document.querySelectorAll(".feudos-realm-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".feudos-realm-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            curRealm = btn.getAttribute("data-realm");
            renderInspector();
        });
    });

    if (btnCopy) {
        btnCopy.addEventListener("click", () => {
            const cur = FIEFS_DATA.find(f => f.code === curCode) || FIEFS_DATA[0];
            const summary = `[Alenia RPG • Tomo XVII] ${cur.title} | Cadeia: ${cur.chain} | Senhor: ${cur.lord} | Concessão: ${cur.bonus} | Conflito: ${cur.dispute}`;
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(summary);
            }
            if (elCopyFb) {
                elCopyFb.textContent = "Copiado!";
                setTimeout(() => { elCopyFb.textContent = ""; }, 2000);
            }
        });
    }

    renderInspector();

    // Filter L01-L22 Fief Cards
    let filterRealm = "ALL";
    const fiefSearch = document.getElementById("feudos-search");
    const fiefCount = document.getElementById("feudos-count");
    const fiefEmpty = document.getElementById("feudos-empty");
    const fiefCards = Array.from(document.querySelectorAll(".feudos-card"));
    const fiefGroups = Array.from(document.querySelectorAll(".feudos-realm-group"));

    function applyFiefFilter() {
        const q = (fiefSearch ? fiefSearch.value : "").trim().toLowerCase();
        let vis = 0;
        fiefCards.forEach(c => {
            const rMatch = (filterRealm === "ALL") || (c.getAttribute("data-realm") === filterRealm);
            const sBlob = (c.getAttribute("data-search") || "").toLowerCase();
            const qMatch = !q || sBlob.indexOf(q) !== -1;
            const show = rMatch && qMatch;
            c.classList.toggle("is-hidden", !show);
            if (show) vis++;
        });
        fiefGroups.forEach(g => {
            const anyVis = g.querySelectorAll(".feudos-card:not(.is-hidden)").length > 0;
            g.classList.toggle("is-hidden", !anyVis);
        });
        if (fiefCount) fiefCount.textContent = `Exibindo ${vis} de ${fiefCards.length} domínios e feudos`;
        if (fiefEmpty) fiefEmpty.style.display = (vis === 0) ? "block" : "none";
    }

    document.querySelectorAll(".feudos-realm-pill").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".feudos-realm-pill").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            filterRealm = btn.getAttribute("data-realm");
            applyFiefFilter();
        });
    });
    if (fiefSearch) fiefSearch.addEventListener("input", applyFiefFilter);

    // Filter Z01-Z08 Dispute Cards
    let filterZone = "ALL";
    const dispSearch = document.getElementById("feudos-disp-search");
    const dispCount = document.getElementById("feudos-disp-count");
    const dispEmpty = document.getElementById("feudos-disp-empty");
    const dispCards = Array.from(document.querySelectorAll(".feudos-dispute-card"));

    function applyDispFilter() {
        const q = (dispSearch ? dispSearch.value : "").trim().toLowerCase();
        let vis = 0;
        dispCards.forEach(c => {
            const zMatch = (filterZone === "ALL") || (c.getAttribute("data-scope") === filterZone);
            const sBlob = (c.getAttribute("data-search") || "").toLowerCase();
            const qMatch = !q || sBlob.indexOf(q) !== -1;
            const show = zMatch && qMatch;
            c.classList.toggle("is-hidden", !show);
            if (show) vis++;
        });
        if (dispCount) dispCount.textContent = `Exibindo ${vis} de ${dispCards.length} frentes quentes`;
        if (dispEmpty) dispEmpty.style.display = (vis === 0) ? "block" : "none";
    }

    document.querySelectorAll(".feudos-disp-pill").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".feudos-disp-pill").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            filterZone = btn.getAttribute("data-scope");
            applyDispFilter();
        });
    });
    if (dispSearch) dispSearch.addEventListener("input", applyDispFilter);

    // 1d12 Intrigue Roller
    const btnRoll = document.getElementById("feudos-roll-btn");
    const outRoll = document.getElementById("feudos-roll-out");
    if (btnRoll && outRoll) {
        btnRoll.addEventListener("click", () => {
            const idx = Math.floor(Math.random() * INTRIGUES_1D12.length);
            outRoll.innerHTML = `<strong>🎲 1d12 = ${idx + 1}:</strong> ${INTRIGUES_1D12[idx]}`;
        });
    }
})();
"""


def _parse_bold_pairs(line: str):
    """Extract (**Key:** Value) pairs separated by | or end of line."""
    pairs = []
    for chunk in line.split("|"):
        m = re.match(r"^\s*\*\*([^*:]+):\*\*\s*(.+?)\s*$", chunk.strip())
        if m:
            pairs.append((m.group(1).strip(), m.group(2).strip()))
    return pairs


def _build_explorer_html() -> str:
    return """
    <section class="feudos-inspector" id="explorador-feudal" aria-label="Explorador Interativo da Cadeia de Vassalagem">
        <div class="feudos-insp-top">
            <div>
                <div class="feudos-insp-kicker">PAINEL DE POLÍTICA &amp; SUBINFEUDAÇÃO • ANO 418 EF</div>
                <div class="feudos-insp-title">Explorador da Cadeia Feudal, Regências &amp; Cartas de Concessão</div>
            </div>
            <div>
                <a class="feudos-tab-btn" href="https://raw.githubusercontent.com/krleandro/alenia/main/plugins/Alenia_Casa_Nobre.rpk" style="text-decoration:none; display:inline-block;">⬇ Ficha Casa Nobre v1.1 (.rpk)</a>
                <button id="fd-copy" class="feudos-tab-btn active" type="button">📋 Copiar Carta</button>
                <span id="fd-copy-fb" class="feudos-copy-fb" aria-live="polite"></span>
            </div>
        </div>
        <div class="feudos-insp-controls">
            <div class="feudos-realm-tabs">
                <button class="feudos-tab-btn feudos-realm-btn active" data-realm="aurora" type="button">👑 Reino de Aurora (Altavanne + 7 Feudos)</button>
                <button class="feudos-tab-btn feudos-realm-btn" data-realm="corallis" type="button">⚓ Liga de Corallis (Regente → Altavanne)</button>
                <button class="feudos-tab-btn feudos-realm-btn" data-realm="gaddra" type="button">☀ Gaddra (Regente → Altavanne)</button>
                <button class="feudos-tab-btn feudos-realm-btn" data-realm="kalis" type="button">🐺 Kalis (Regente → Altavanne)</button>
            </div>
            <div id="feudos-fief-tabs" class="feudos-fief-tabs"></div>
        </div>
        <div class="feudos-insp-card">
            <div class="feudos-insp-banner">
                <span id="fd-title" class="feudos-insp-domtitle">L03 · Feudo de Dahrma (Suserano de Lavroga)</span>
                <span id="fd-chain" class="feudos-insp-chain">Casa do PJ / Lavroga → Feudo de Dahrma → Altavanne (L01)</span>
            </div>
            <div class="feudos-insp-grid">
                <div class="feudos-insp-box">
                    <div class="feudos-insp-lbl">👑 Senhor Feudal &amp; Linhagem</div>
                    <div id="fd-lord" class="feudos-insp-txt"></div>
                </div>
                <div class="feudos-insp-box">
                    <div class="feudos-insp-lbl">⚔ Sub-feudos &amp; Litígio Ativo</div>
                    <div id="fd-dispute" class="feudos-insp-txt"></div>
                </div>
                <div class="feudos-insp-box">
                    <div class="feudos-insp-lbl">🏰 Bônus de Concessão (Para Casa de PJs — Tomo XV)</div>
                    <div id="fd-bonus" class="feudos-insp-txt"></div>
                </div>
                <div class="feudos-insp-box">
                    <div class="feudos-insp-lbl">🕯 Posição Política &amp; Gancho de Intriga</div>
                    <div id="fd-hook" class="feudos-insp-txt"></div>
                </div>
            </div>
        </div>
    </section>
    """


def render_feudos_page(bk: dict, md_content: str, helpers: dict):
    """Build interactive illustrated Tomo XVII — Atlas Feudal, Regências e Intrigas page."""
    inline_md = helpers["inline_md"]
    md_to_html = helpers["md_to_html"]
    img_dim_attrs = helpers["img_dim_attrs"]
    make_gm_gate_block = helpers["make_gm_gate_block"]
    render_toc_items = helpers["render_toc_items"]

    sections = re.split(r"(?=^##\s+)", md_content, flags=re.M)

    pyramid_sec = ""
    aurora_sec = ""
    vassals_sec = ""
    disputes_sec = ""
    generator_sec = ""
    gm_sec = ""
    shield_sec = ""

    for sec in sections:
        s = sec.strip()
        m_h2 = re.match(r"^##\s+(.+)$", s, flags=re.M)
        if not m_h2:
            continue
        title = m_h2.group(1).strip()
        tl = title.lower()
        if tl.startswith("a pirâmide imperial"):
            pyramid_sec = s
        elif tl.startswith("coroa imperial e os sete"):
            aurora_sec = s
        elif tl.startswith("feudos dos três reinos"):
            vassals_sec = s
        elif tl.startswith("oito frentes quentes"):
            disputes_sec = s
        elif tl.startswith("gerador rápido"):
            generator_sec = s
        elif tl.startswith("caderno reservado ao mestre"):
            gm_sec = s
        elif tl.startswith("escudo de referência"):
            shield_sec = s

    toc_items = [
        (2, "Pirâmide Imperial, Forais e Armas da Politicagem", "piramide-feudal"),
        (2, "Explorador da Cadeia Feudal e Concessões", "explorador-feudal"),
    ]

    # 1. Pyramid & Rules Drawer
    pyr_inner, _ = md_to_html(pyramid_sec, id_prefix="pyr-", card_h3=False, inject_maps=False)
    pyr_html = f"""
    <details class="feudos-editorial" id="piramide-feudal" open>
        <summary>👑 A Dupla Cadeia de Suserania, Subinfeudação, Embargos, Forais Contraditórios &amp; Votos no Concílio</summary>
        <div class="feudos-editorial-inner">{pyr_inner}</div>
    </details>
    """

    def render_fief_cards(raw_block: str, realm_key: str, code_cls: str):
        parts = re.split(r"(?=^###\s+L(?:0[1-9]|1[0-9]|2[0-2])\s)", raw_block, flags=re.M)
        intro_lines = parts[0].splitlines()[1:]
        plate_html = ""
        intro_rest = []
        for ln in intro_lines:
            m_img = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", ln.strip())
            if m_img and not plate_html:
                palt = m_img.group(1).strip()
                psrc = "assets/" + os.path.basename(m_img.group(2).strip())
                plate_html = (
                    f'<figure class="atlas-plate feudos-wide-plate" title="Clique para ampliar prancha">'
                    f'<img src="{html.escape(psrc, quote=True)}" alt="{html.escape(palt, quote=True)}"{img_dim_attrs(psrc)} decoding="async"/>'
                    f'<figcaption class="atlas-caption">{html.escape(palt)}</figcaption>'
                    f'</figure>'
                )
            else:
                intro_rest.append(ln)

        intro_html, _ = md_to_html("\n".join(intro_rest), id_prefix=f"fd-in-{realm_key}-", card_h3=False, inject_maps=False)
        cards = []
        for blk in parts[1:]:
            blines = blk.strip().splitlines()
            if not blines:
                continue
            m_h = re.match(r"^###\s+(L\d{2})\s+[—–-]\s+(.+)$", blines[0].strip())
            if not m_h:
                continue
            lcode, lname = m_h.group(1), re.sub(r"\*+|`", "", m_h.group(2)).strip()
            tags = []
            body_lines = []
            for ln in blines[1:]:
                st = ln.strip()
                if not st:
                    body_lines.append("")
                    continue
                if st.startswith("**Reino e Suserania:**") or st.startswith("**Senhor Feudal (Ano 418):**"):
                    for k_lbl, v_lbl in _parse_bold_pairs(st):
                        tags.append(f'<span class="feudos-tag"><strong>{html.escape(k_lbl)}:</strong> {inline_md(v_lbl)}</span>')
                else:
                    body_lines.append(ln)

            b_html, _ = md_to_html("\n".join(body_lines), id_prefix=f"fd-{lcode.lower()}-", card_h3=False, inject_maps=False)
            s_blob = html.escape(f"{lcode} {lname} {realm_key} {' '.join(blines[1:])}", quote=True)
            c_cls = f"feudos-code {code_cls}".strip()
            cards.append(f"""
            <article class="feudos-card" id="{lcode.lower()}" data-realm="{realm_key}" data-search="{s_blob}">
                <div class="feudos-card-head">
                    <span class="{c_cls}">{html.escape(lcode)}</span>
                    <h3 class="feudos-card-title">{html.escape(lname)}</h3>
                </div>
                <div class="feudos-tags">{"".join(tags)}</div>
                {b_html}
            </article>
            """)
        return plate_html, intro_html, cards

    # 2. Aurora (L01–L08)
    aur_plate, aur_intro, aur_cards = render_fief_cards(aurora_sec, "aurora", "")
    toc_items.append((2, "Coroa Imperial e os 7 Grandes Feudos de Aurora (L01–L08)", "feudos-aurora"))
    aurora_html = f"""
    <section class="feudos-group feudos-realm-group" id="feudos-aurora" data-realm="aurora">
        <header class="feudos-group-header">
            <div class="feudos-group-kicker">VASSALAGEM DIRETA AO TRONO • ALTAVANNE + OS SETE GRANDES FEUDOS (L01–L08)</div>
            <h2 class="feudos-group-title">Coroa Imperial e os Sete Grandes Feudos de Aurora</h2>
        </header>
        {aur_plate}
        {aur_intro}
        {"".join(aur_cards)}
    </section>
    """

    # 3. Three Vassal Realms (Corallis L09–L13, Gaddra L14–L17, Kalis L18–L22)
    vassals_groups_html = []
    if vassals_sec:
        # Split by realm subheaders
        sub_splits = re.split(
            r"(?=^###\s+(?:Liga Talassocrática de Corallis|Confederação Tribal de Gaddra|Despotado Velado de Kalis))",
            vassals_sec,
            flags=re.M,
        )
        top_lines = sub_splits[0].splitlines()[1:]
        v_plate_html = ""
        v_intro_lines = []
        for ln in top_lines:
            m_img = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", ln.strip())
            if m_img and not v_plate_html:
                palt = m_img.group(1).strip()
                psrc = "assets/" + os.path.basename(m_img.group(2).strip())
                v_plate_html = (
                    f'<figure class="atlas-plate feudos-wide-plate" title="Clique para ampliar prancha">'
                    f'<img src="{html.escape(psrc, quote=True)}" alt="{html.escape(palt, quote=True)}"{img_dim_attrs(psrc)} decoding="async"/>'
                    f'<figcaption class="atlas-caption">{html.escape(palt)}</figcaption>'
                    f'</figure>'
                )
            else:
                v_intro_lines.append(ln)
        v_top_intro, _ = md_to_html("\n".join(v_intro_lines), id_prefix="vas-top-", card_h3=False, inject_maps=False)

        realm_meta = [
            ("corallis", "corallis-code", "feudos-group-header corallis-hdr", "FEUDOS → ARCONTE-REGENTE CORARDO DELLA ROCCA (N021) → ALTAVANNE (L09–L13)", "Liga Talassocrática de Corallis"),
            ("gaddra", "gaddra-code", "feudos-group-header gaddra-hdr", "FEUDOS → REGENTE DAS DUNAS QASIR ZAHARID (N022) → ALTAVANNE (L14–L17)", "Confederação Tribal de Gaddra"),
            ("kalis", "kalis-code", "feudos-group-header kalis-hdr", "FEUDOS → DÉSPOTA-REGENTE GRIMRIK ULSCOLD (N023) → ALTAVANNE (L18–L22)", "Despotado Velado de Kalis"),
        ]
        for idx_r, sub_raw in enumerate(sub_splits[1:]):
            if idx_r >= len(realm_meta):
                break
            r_key, c_cls, h_cls, r_kicker, r_title = realm_meta[idx_r]
            _, _, r_cards = render_fief_cards(sub_raw, r_key, c_cls)
            sec_id = f"feudos-{r_key}"
            toc_items.append((2, f"{r_title} (Regência Vassala)", sec_id))
            extra_top = (v_plate_html + v_top_intro) if idx_r == 0 else ""
            vassals_groups_html.append(f"""
            <section class="feudos-group feudos-realm-group" id="{sec_id}" data-realm="{r_key}">
                <header class="{h_cls}">
                    <div class="feudos-group-kicker">{r_kicker}</div>
                    <h2 class="feudos-group-title">{html.escape(r_title)}</h2>
                </header>
                {extra_top}
                {"".join(r_cards)}
            </section>
            """)

    total_fiefs = len(aur_cards) + sum(g.count('class="feudos-card"') for g in vassals_groups_html)

    # 4. Active Disputes Z01–Z08
    disp_html = ""
    total_disps = 0
    if disputes_sec:
        toc_items.append((2, "Oito Frentes Quentes de Disputa e Intriga (Z01–Z08)", "frentes-disputa"))
        z_parts = re.split(r"(?=^###\s+Z0[1-8]\s)", disputes_sec, flags=re.M)
        z_intro_lines = z_parts[0].splitlines()[1:]
        z_plate = ""
        z_rest = []
        for ln in z_intro_lines:
            m_img = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", ln.strip())
            if m_img and not z_plate:
                palt = m_img.group(1).strip()
                psrc = "assets/" + os.path.basename(m_img.group(2).strip())
                z_plate = (
                    f'<figure class="atlas-plate feudos-wide-plate" title="Clique para ampliar prancha">'
                    f'<img src="{html.escape(psrc, quote=True)}" alt="{html.escape(palt, quote=True)}"{img_dim_attrs(psrc)} decoding="async"/>'
                    f'<figcaption class="atlas-caption">{html.escape(palt)}</figcaption>'
                    f'</figure>'
                )
            else:
                z_rest.append(ln)
        z_intro_html, _ = md_to_html("\n".join(z_rest), id_prefix="zn-in-", card_h3=False, inject_maps=False)

        z_cards = []
        for zblk in z_parts[1:]:
            zlines = zblk.strip().splitlines()
            if not zlines:
                continue
            m_z = re.match(r"^###\s+(Z0[1-8])\s+[—–-]\s+(.+)$", zlines[0].strip())
            if not m_z:
                continue
            zcode, zname = m_z.group(1), re.sub(r"\*+|`", "", m_z.group(2)).strip()
            total_disps += 1
            z_num = int(zcode[1:])
            scope = "aurora" if z_num <= 5 else "regencias"
            z_body_html, _ = md_to_html("\n".join(zlines[1:]), id_prefix=f"zn-{zcode.lower()}-", card_h3=False, inject_maps=False)
            z_search = html.escape(f"{zcode} {zname} {' '.join(zlines[1:])}", quote=True)
            z_cards.append(f"""
            <article class="feudos-dispute-card" id="{zcode.lower()}" data-scope="{scope}" data-search="{z_search}">
                <div class="feudos-card-head">
                    <span class="feudos-code litigio-code">{html.escape(zcode)}</span>
                    <h3 class="feudos-card-title">{html.escape(zname)}</h3>
                </div>
                {z_body_html}
            </article>
            """)

        disp_toolbar = f"""
        <div class="feudos-toolbar" role="region" aria-label="Filtros das Frentes de Litígio">
            <div class="feudos-pills">
                <button class="feudos-pill feudos-disp-pill active" data-scope="ALL" type="button">Todas as Frentes ({total_disps})</button>
                <button class="feudos-pill feudos-disp-pill" data-scope="aurora" type="button">⚔ Disputas em Aurora (Voernock, Lavroga, Ferraur, Concílio)</button>
                <button class="feudos-pill feudos-disp-pill" data-scope="regencias" type="button">🌊 Conflitos nas 3 Regências (Corallis, Gaddra, Kalis)</button>
            </div>
            <div class="feudos-search-row">
                <input id="feudos-disp-search" class="feudos-search" type="search" placeholder="Buscar disputa (Voernock, Lavroga, Ferraur, Cadwyn, Rubecina, Ferro Velho, Z01–Z08)..." aria-label="Buscar frentes de disputa"/>
                <span id="feudos-disp-count" class="feudos-count">Exibindo {total_disps} de {total_disps} frentes quentes</span>
            </div>
        </div>
        <div id="feudos-disp-empty" class="feudos-empty">Nenhuma frente de disputa corresponde à busca.</div>
        """

        disp_html = f"""
        <section class="feudos-group feudos-divider" id="frentes-disputa">
            <header class="feudos-group-header">
                <div class="feudos-group-kicker">FRONTEIRAS EM LITÍGIO, SUB-VASSALAGEM E GUERRAS DE FORAL (Z01–Z08)</div>
                <h2 class="feudos-group-title">Oito Frentes Quentes de Disputa Territorial e Intriga</h2>
            </header>
            {z_plate}
            {z_intro_html}
            {disp_toolbar}
            <div class="feudos-dispute-grid">{"".join(z_cards)}</div>
        </section>
        """

    # 5. 1d12 Intrigue Generator
    gen_html = ""
    if generator_sec:
        toc_items.append((2, "Gerador Rápido de Intrigas Feudais (1d12)", "gerador-intrigas"))
        g_inner, _ = md_to_html(generator_sec, id_prefix="gen-int-", card_h3=False, inject_maps=False)
        gen_html = f"""
        <section class="feudos-divider" id="gerador-intrigas">
            <div class="feudos-roller-bar">
                <button id="feudos-roll-btn" class="feudos-tab-btn active" type="button">🎲 Sortear Intriga Feudal (1d12)</button>
                <div id="feudos-roll-out" class="feudos-roller-out">Clique para sortear instantaneamente uma crise política ou diplomática para a sessão.</div>
            </div>
            {g_inner}
        </section>
        """

    # 6. Sealed GM Vault
    gm_html = ""
    if gm_sec:
        gm_rendered, gm_toc = md_to_html(gm_sec, id_prefix="feudos-gm-", card_h3=False, inject_maps=False)
        gm_html = (
            '<div class="feudos-divider">'
            + make_gm_gate_block(
                "Caderno Reservado ao Mestre — Segredos de Voernock, Lavroga, Ferraur e das Regências",
                "Contém as verdades ocultas por trás das disputas Z01–Z03, os planos reservados dos 3 Regentes no Ano 418 EF e conexões com o Acervo e a Comunhão. Insira a senha para revelar.",
                gm_rendered,
                render_toc_items(gm_toc),
                codex_file=bk["out"],
                compendium_mode=False,
            )
            + '</div>'
        )

    # 7. Quick Reference Shield
    shield_html = ""
    if shield_sec:
        sh_inner, sh_toc = md_to_html(shield_sec, id_prefix="feudos-ref-", card_h3=False, inject_maps=False)
        shield_html = f'<section class="feudos-divider">{sh_inner}</section>'
        toc_items.extend(sh_toc)

    fief_toolbar = f"""
    <div class="feudos-toolbar" role="region" aria-label="Filtros dos 22 Domínios e Feudos">
        <div class="feudos-pills">
            <button class="feudos-pill feudos-realm-pill active" data-realm="ALL" type="button">Todos os Domínios ({total_fiefs})</button>
            <button class="feudos-pill feudos-realm-pill" data-realm="aurora" type="button">👑 Aurora (Altavanne + 7 Feudos)</button>
            <button class="feudos-pill feudos-realm-pill" data-realm="corallis" type="button">⚓ Corallis (5 Feudos)</button>
            <button class="feudos-pill feudos-realm-pill" data-realm="gaddra" type="button">☀ Gaddra (4 Feudos)</button>
            <button class="feudos-pill feudos-realm-pill" data-realm="kalis" type="button">🐺 Kalis (5 Feudos)</button>
        </div>
        <div class="feudos-search-row">
            <input id="feudos-search" class="feudos-search" type="search" placeholder="Buscar feudo, senhor feudal (Scutauria, Montavalle, Leonastis, Tsurumaru, Aerwen), Lavroga, Voernock, bônus..." aria-label="Buscar nos feudos"/>
            <span id="feudos-count" class="feudos-count">Exibindo {total_fiefs} de {total_fiefs} domínios e feudos</span>
        </div>
    </div>
    <div id="feudos-empty" class="feudos-empty">Nenhum feudo corresponde aos filtros atuais.</div>
    """

    hero_html = f"""
    <section class="feudos-hero">
        <figure class="atlas-plate feudos-hero-cover">
            <img src="{bk['cover_map']}" alt="Capa — {html.escape(bk['title'])}"{img_dim_attrs(bk['cover_map'])} decoding="async"/>
        </figure>
        <div>
            <div class="feudos-kicker">ALENIA RPG • {html.escape(bk['num'])} • GEOPOLÍTICA, SUSERANIA &amp; INTRIGA</div>
            <h1 class="feudos-title">{html.escape(bk['title'])}</h1>
            <p class="feudos-sub">Os 7 Feudos de Aurora (diretos a Altavanne), os 14 Feudos das 3 Regências Vassalas, sub-feudos e as 8 zonas de litígio do Ano 418 EF.</p>
            <blockquote class="feudos-epigraph">
                “Tire a cunha de Lavroga, represa a água das Cidades Suspensas ou deixe Vaarsa estrangular os canais de Voernock, e você descobrirá depressa que até o trono do Matador da Sombra precisa de quem carregue o grão, o sal e o remo.”
            </blockquote>
            <div class="feudos-stats">
                <span class="feudos-stat-pill">👑 7 Feudos de Aurora → Altavanne</span>
                <span class="feudos-stat-pill slate">🌊 3 Regências → Altavanne (L09–L22)</span>
                <span class="feudos-stat-pill">⚔ 8 Disputas Ativas (Z01–Z08)</span>
                <span class="feudos-stat-pill slate">🏰 Subinfeudação &amp; RPK v1.1</span>
            </div>
        </div>
    </section>
    """

    full_body = (
        hero_html
        + pyr_html
        + _build_explorer_html()
        + fief_toolbar
        + f'<div id="feudos-catalogue-root">{aurora_html}{"".join(vassals_groups_html)}</div>'
        + disp_html
        + gen_html
        + gm_html
        + shield_html
    )
    return full_body, toc_items
