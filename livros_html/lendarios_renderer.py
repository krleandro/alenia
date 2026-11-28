#!/usr/bin/env python3
"""
Renderizador Editorial Ilustrado do Tomo XVIII — Colossos, Presságios e Caças Lendárias de Alenia:
- 12 Soberanos Solitários e Únicos no Mundo (X01–X12), cada qual com gravura renascentista individual e ficha d20 auditada
- Planejador Interativo de Expedição de Caça (Rastro, Astúcia do Soberano, Isca & Contramedida, Troféu & Peso Político)
- Filtros instantâneos por Bioma (Matas/Montanhas/Salares, Mares/Abismos, Furnas/Pântanos) e busca ao vivo
- Destaque visual especial para o Santuário/Tabu Marítimo (X10 — A Manta-Fantasma)
- Caderno Reservado ao Mestre selado em AES-256-GCM e diagramação @media print A4 limpa
"""
import html
import os
import re

LENDARIOS_CSS = r"""
/* =====================================================
   TOMO XVIII — ANIMAIS LENDÁRIOS ÚNICOS DE ALENIA
   ===================================================== */
body.lendarios-mode .book-shell {
    padding: 72px 18px 72px;
}
body.lendarios-mode:not(.sidebar-hidden) .sidebar-backdrop {
    display: block;
}
body.lendarios-mode .book-page {
    max-width: 1180px;
    padding: 34px 42px 58px;
    background: radial-gradient(circle at top center, #faf4e6 0%, #f3e9d4 58%, #eadec3 100%);
    box-shadow:
        0 26px 72px rgba(0, 0, 0, 0.7),
        0 0 0 1px rgba(154, 123, 59, 0.45);
}
body.lendarios-mode .book-page::before {
    inset: 10px;
    border: 1px solid rgba(154, 123, 59, 0.34);
}

/* HERO / FRONTISPÍCIO */
.lend-hero {
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
.lend-hero-cover {
    margin: 0 !important;
    padding: 6px !important;
    background: #ede1c4 !important;
    border: 1px solid var(--gold) !important;
}
.lend-hero-cover img {
    width: 100%;
    max-height: 325px;
    object-fit: cover;
    display: block;
    cursor: zoom-in;
}
.lend-kicker {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 11px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--crimson);
    font-weight: 700;
}
.lend-title {
    font-family: 'Cinzel', Georgia, serif !important;
    font-size: 30px !important;
    line-height: 1.15 !important;
    margin: 6px 0 8px !important;
    color: #21160d !important;
    border: none !important;
    padding: 0 !important;
}
.lend-sub {
    font-style: italic;
    font-size: 16.5px;
    color: var(--ink-soft);
    margin: 0 0 12px;
}
.lend-epigraph {
    font-style: italic;
    font-size: 14.8px;
    color: #36281b;
    border-left: 3px solid var(--crimson);
    padding: 7px 14px;
    margin: 0 0 14px;
    background: rgba(122, 31, 29, 0.06);
}
.lend-stats {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}
.lend-stat-pill {
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
.lend-stat-pill.sea {
    background: rgba(27, 73, 101, 0.11);
    border-color: rgba(27, 73, 101, 0.36);
    color: #163b52;
}
.lend-stat-pill.moss {
    background: rgba(46, 90, 68, 0.12);
    border-color: rgba(46, 90, 68, 0.38);
    color: #1e4431;
}

/* GAVETA DE REGRAS DE CAÇADA */
.lend-editorial {
    margin: 0 0 24px;
    border: 1px solid rgba(154, 123, 59, 0.54);
    background: rgba(246, 236, 214, 0.78);
    border-radius: 3px;
    scroll-margin-top: 72px;
}
.lend-editorial > summary {
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
.lend-editorial-inner {
    padding: 18px 22px 12px;
}

/* PLANEJADOR INTERATIVO DE EXPEDIÇÃO DE CAÇA */
.lend-planner {
    margin: 0 0 26px;
    padding: 20px 22px 22px;
    background: linear-gradient(180deg, #1f1913 0%, #15110d 100%);
    color: #f4ebd9;
    border: 2px solid #9a7b3b;
    border-radius: 4px;
    box-shadow: 0 14px 32px rgba(24, 15, 8, 0.32);
    scroll-margin-top: 72px;
}
.lend-insp-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
    padding-bottom: 12px;
    margin-bottom: 14px;
    border-bottom: 1px solid rgba(217, 185, 106, 0.28);
}
.lend-insp-kicker {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10.5px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #d9b96a;
    font-weight: 700;
}
.lend-insp-title {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 19px;
    color: #fff6e3;
    margin: 2px 0 0;
}
.lend-insp-controls {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 14px;
}
.lend-hab-tabs,
.lend-beast-tabs {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}
.lend-tab-btn {
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
.lend-tab-btn:hover {
    background: rgba(217, 185, 106, 0.2);
    color: #fff8e8;
}
.lend-tab-btn.active {
    background: #7a1f1d;
    border-color: #e6c677;
    color: #fff9eb;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35);
}
.lend-insp-card {
    background: rgba(252, 245, 230, 0.96);
    color: #24190e;
    border: 1px solid #b89550;
    border-radius: 3px;
    padding: 16px 18px;
}
.lend-insp-banner {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    flex-wrap: wrap;
    gap: 8px;
    border-bottom: 1px solid rgba(122, 31, 29, 0.24);
    padding-bottom: 8px;
    margin-bottom: 10px;
}
.lend-insp-beasttitle {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 18px;
    font-weight: 700;
    color: #6b1b19;
}
.lend-insp-metrics {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 11.5px;
    font-weight: 700;
    padding: 3px 9px;
    border-radius: 2px;
    background: rgba(122, 31, 29, 0.11);
    border: 1px solid rgba(122, 31, 29, 0.35);
    color: #5a1513;
}
.lend-insp-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px 14px;
}
.lend-insp-box {
    background: rgba(239, 227, 200, 0.65);
    border-left: 3px solid #8a6c2f;
    padding: 8px 11px;
    border-radius: 2px;
}
.lend-insp-lbl {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10.5px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #6b1b19;
    font-weight: 700;
    margin-bottom: 3px;
}
.lend-insp-txt {
    font-size: 14.3px;
    line-height: 1.45;
    color: #261b10;
}
.lend-copy-fb {
    font-size: 12px;
    color: #9de0a8;
    margin-left: 8px;
}

/* TOOLBAR DE FILTROS */
.lend-toolbar {
    margin: 14px 0 20px;
    padding: 13px 16px;
    background: #241c15;
    border: 1px solid #9a7b3b;
    border-radius: 4px;
    display: flex;
    flex-direction: column;
    gap: 10px;
}
.lend-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}
.lend-pill {
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
.lend-pill:hover {
    background: rgba(217, 185, 106, 0.2);
    color: #fff9eb;
}
.lend-pill.active {
    background: #7a1f1d;
    border-color: #e6c677;
    color: #fff8ea;
}
.lend-search-row {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
}
.lend-search {
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
.lend-count {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 11px;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    color: #d9b96a;
}
.lend-empty {
    display: none;
    padding: 18px;
    text-align: center;
    font-style: italic;
    background: rgba(122, 31, 29, 0.08);
    border: 1px dashed var(--crimson);
    margin-bottom: 18px;
}

/* CABEÇALHOS DE BIOMA & FICHAS ILUSTRADAS (X01–X12) */
.lend-group {
    margin: 26px 0 32px;
    scroll-margin-top: 72px;
}
.lend-group-header {
    padding: 12px 18px;
    margin-bottom: 18px;
    border-left: 4px solid var(--crimson);
    background: linear-gradient(90deg, rgba(122, 31, 29, 0.12) 0%, rgba(246, 236, 214, 0.3) 100%);
    border-top: 1px solid rgba(154, 123, 59, 0.35);
    border-bottom: 1px solid rgba(154, 123, 59, 0.35);
}
.lend-group-header.mares-hdr {
    border-left-color: #1b4965;
    background: linear-gradient(90deg, rgba(27, 73, 101, 0.13) 0%, rgba(246, 236, 214, 0.3) 100%);
}
.lend-group-header.pantanos-hdr {
    border-left-color: #2e5a44;
    background: linear-gradient(90deg, rgba(46, 90, 68, 0.14) 0%, rgba(246, 236, 214, 0.3) 100%);
}
.lend-group-kicker {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10.5px;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--crimson);
    font-weight: 700;
}
.lend-group-title {
    font-family: 'Cinzel', Georgia, serif !important;
    font-size: 22px !important;
    margin: 3px 0 0 !important;
    border: none !important;
    padding: 0 !important;
    color: #22170d !important;
}

.lend-card {
    background: rgba(252, 246, 233, 0.92);
    border: 1px solid rgba(154, 123, 59, 0.56);
    border-left: 5px solid var(--crimson);
    border-radius: 4px;
    padding: 18px 22px 16px;
    margin: 0 0 22px;
    box-shadow: 0 6px 18px rgba(42, 26, 12, 0.08);
    scroll-margin-top: 78px;
}
.lend-card[data-habitat="mares"] {
    border-left-color: #1b4965;
}
.lend-card[data-habitat="pantanos"] {
    border-left-color: #2e5a44;
}
.lend-card.sanctuary-card {
    border-left-color: #1f6f78;
    border-color: rgba(31, 111, 120, 0.55);
    background: radial-gradient(circle at top right, rgba(226, 243, 244, 0.55) 0%, rgba(252, 246, 233, 0.95) 65%);
}

.lend-card-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    flex-wrap: wrap;
    padding-bottom: 9px;
    margin-bottom: 12px;
    border-bottom: 1px dotted rgba(122, 31, 29, 0.36);
}
.lend-head-left {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
}
.lend-code {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 12.5px;
    font-weight: 700;
    letter-spacing: 0.08em;
    padding: 4px 9px;
    border-radius: 2px;
    background: #7a1f1d;
    color: #fff7e6;
}
.lend-code.mares-code    { background: #1b4965; }
.lend-code.pantanos-code { background: #2e5a44; }
.lend-code.tabu-code     { background: #1f6f78; }

.lend-unique-badge {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 3px 8px;
    border-radius: 2px;
    background: rgba(154, 123, 59, 0.18);
    border: 1px solid rgba(154, 123, 59, 0.52);
    color: #563e14;
    font-weight: 700;
}
.lend-card-title {
    font-family: 'Cinzel', Georgia, serif !important;
    font-size: 20px !important;
    margin: 0 !important;
    border: none !important;
    padding: 0 !important;
    color: #21160d !important;
}
.lend-plate {
    margin: 6px 0 14px !important;
    background: #efe3c7 !important;
}
.lend-plate img {
    width: 100%;
    max-height: 430px;
    object-fit: contain;
    display: block;
    margin: 0 auto;
    cursor: zoom-in;
}
.lend-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 12px;
}
.lend-tag {
    font-size: 12.8px;
    padding: 4px 9px;
    border-radius: 2px;
    background: rgba(154, 123, 59, 0.14);
    border: 1px solid rgba(154, 123, 59, 0.38);
    color: #3a2815;
}

.lend-divider {
    margin-top: 28px;
    padding-top: 18px;
    border-top: 2px solid rgba(154, 123, 59, 0.42);
}
.is-hidden {
    display: none !important;
}

@media (max-width: 820px) {
    .lend-hero {
        grid-template-columns: 1fr;
    }
    .lend-hero-cover img {
        max-width: 230px;
        margin: 0 auto;
    }
    .lend-insp-grid {
        grid-template-columns: 1fr;
    }
    body.lendarios-mode .book-page {
        padding: 22px 18px 42px;
    }
}

@media print {
    #planejador-cacada,
    .lend-toolbar,
    .lend-empty {
        display: none !important;
    }
    body.lendarios-mode .book-shell {
        padding: 0 !important;
    }
    body.lendarios-mode .book-page {
        max-width: 100% !important;
        padding: 0 !important;
        box-shadow: none !important;
        background: #fff !important;
    }
    .lend-hero,
    .lend-group-header {
        break-inside: avoid;
        page-break-inside: avoid;
        box-shadow: none !important;
    }
    .lend-card {
        box-shadow: none !important;
        break-inside: auto;
    }
    .lend-card-head,
    .lend-plate {
        break-inside: avoid;
        page-break-inside: avoid;
    }
    .lend-plate img {
        max-height: 290px !important;
    }
    .is-hidden {
        display: block !important;
    }
}
"""

LENDARIOS_JS = r"""
(function () {
    const BEASTS_DATA = [
        { code: "X01", hab: "terras", short: "X01 Cervo-de-Escória", title: "X01 · O Cervo-de-Escória (Galhada-de-Ferro)", metrics: "118 PV • Def 25 Ap / 20 Esq • RD 3 Frontal • Rastro CD 18", cunning: "Jamais pasta a favor do vento; finge mancar para atrair cavaleiros a ladeiras de xisto solto e virar carroças morro abaixo.", prep: "Sal de Bayd + Flor-de-pedra (H16); atrair a desfiladeiro <3m de largura (perde Aparar 25 -> 17) e firmar Lança c/ Travessa.", trophy: "1.800 PP • Galhada forja 2 Pavêses Def +3 ou soma +1 LE e +1 Moral no portão do feudo • Feito até Status S03." },
        { code: "X02", hab: "terras", short: "X02 Velho Kragh", title: "X02 · O Urso-das-Cinzas (Velho Kragh)", metrics: "148 PV • Def 19 Esq • RD 3 (½ Fogo) • Rastro CD 17", cunning: "Reconhece carne envenenada e fossos em trilha; rola matacões de cima do desfiladeiro (4d8) e espera os guardas fugirem.", prep: "Escalar a crista acima dele antes da alvorada (CD 16); isca quente de cordeiro e mel; Lança c/ Travessa contra o peito erguido.", trophy: "2.200 PP • 6 cântaros de Banha de Kragh (tempera 6 armas com +1 dano e ignora 1 RD/LE) • Reabre paz em Rubecina (Z07)." },
        { code: "X03", hab: "terras", short: "X03 Sombra-Salobra", title: "X03 · A Sombra-Salobra (Leão-da-Restinga Albino)", metrics: "96 PV • Def 25 Esq • Furtividade +15 • Rastro CD 20", cunning: "Jamais ruge; estuda a troca das rondas por 2 dias e ataca sob poeira branca o último soldado pesado pelos tornozelos.", prep: "Óculos de vidro escuro de Fugong (N085) contra o reflexo; manequim de armadura com pó de tinturaria (-8 na Furtividade dele!).", trophy: "1.600 PP • Gibão Cor-de-Osso (Def +2, Pen 0, +2 Furtividade em claro/neblina) • Salvo-conduto e Status S03 em Kalis." },
        { code: "X04", hab: "terras", short: "X04 Javali-de-Muralha", title: "X04 · Javali-de-Muralha (Quebra-Piques)", metrics: "132 PV • Def 19 Esq • RD 4 Frontal • Rastro CD 16", cunning: "Avança pela própria haste de lanças comuns sem travessa; faz o 'gancho do varrão' para estripar arqueiros pelas costas e ataca em 0 PV!", prep: "Obrigatório Fosso Estacado + fila dupla de Lanças de Contenção com Travessa (Boar Spears) e bolotas fermentadas.", trophy: "1.500 PP • Couraça Def +3 anti-sangramento + Banquete diplomático para 50 convivas (+3 em acordos em Dahrma/Altavanne)." },
        { code: "X05", hab: "terras", short: "X05 Cão-Rei de Carniça", title: "X05 · O Cão-Rei de Carniça (Soberano Pachycrocuta)", metrics: "108 PV • Def 23 Esq • Quebra-Elmos • Rastro CD 17", cunning: "Manda cães menores na frente para testar laços e fossos; sua risada rouca abala a moral (SAB CD 16) antes do cerco noturno.", prep: "Barreiras de Óleo Incendiário para isolá-lo da matilha comum; paliçada de entrada única com tutano aquecido.", trophy: "1.400 PP • Crânio no estandarte/portão concede +2 permanente em Moral da guarnição (Tomo XV) e +2 Intimidação." },
        { code: "X06", hab: "terras", short: "X06 Águia-Quebra-Ossos", title: "X06 · Águia-Quebra-Ossos (Soberana dos Picos)", metrics: "92 PV • Def 25 Esq • Voo 24m • Rastro CD 18 (Luneta)", cunning: "Mergulha muda com o sol às costas (Percepção CD 20), corta cordas secundárias e arremessa vigias e mulas penhasco abaixo (+12 Empurrar).", prep: "Ancorar todo o grupo à rocha com Pítons e Corrente; lançar Rede Lastrada ou Arpéu no rasante (no chão a Esquiva cai p/ 19!).", trophy: "1.900 PP • 24 Flechas/Virotes Soberanos (+1 longa distância, sem penalidade de vento) • Poupá-la sela aliança com Aerwen (L08)." },

        { code: "X07", hab: "mares", short: "X07 Velho Quilha-Branca", title: "X07 · O Velho Quilha-Branca (Cachalote Cicatrizado)", metrics: "210 PV • Def 16 • RD 4 Naval • Rastro Naval CD 18", cunning: "Mergulha no ponto cego sob o casco e sobe na vertical contra a quilha (4d12+8 ignorando 6 LE!); arrasta barcos arpoados para recifes.", prep: "Navio E06+ com Balista de Fisgada (M09) e 4 barris-boia estanques nos cabos (impedem o mergulho vertical de prumo!).", trophy: "4.200 PP (420 PO!) • Espermacete + 9 kg de Âmbar-Cinza (paga sozinho a reforma inteira de uma Torre F04!) • Status S03->S04." },
        { code: "X08", hab: "mares", short: "X08 Imperatriz Vermelha", title: "X08 · A Imperatriz Vermelha (Lula-Colossal Abissal)", metrics: "168 PV (28 PV/tentáculo) • Def 21/24 • Rastro CD 19", cunning: "Trava primeiro o leme sob a água em noite sem lua, apaga a popa e puxa até 3 marinheiros por vez com ganchos giratórios de 360 graus.", prep: "Redes altas nos bordos, alcatrão quente e guerreiros com machados pesados em Preparar Ação para decepar tentáculos na amurada.", trophy: "2.800 PP • 3 Arpéus Imperiais (+2 Escalada/abordagem) + Tinta Indelével para tratados em Sellene (L13) • Status S03->S04." },
        { code: "X09", hab: "mares", short: "X09 Encouraçado do Recife", title: "X09 · O Encouraçado do Recife (Crocodilo Ancestral)", metrics: "156 PV • Def 18 • RD 4 Dorso (RD 1 Ventre) • CD 19", cunning: "Fica 4h sem respirar idêntico a um banco de coral (Percepção CD 21); deixa os botes da frente passarem para virar a barcaça de carga.", prep: "Sondar bancos com varas ferradas; atrair sobre toras para terra e virar com Polias (Tomo IX) expondo o ventre macio.", trophy: "2.500+ PP • Escudos Torre +1 LE + Gastrólitos de safiras/ouro e o Anel de Sinete perdido que decide a crise dos recifes (Z06)!" },
        { code: "X10", hab: "mares", short: "X10 Manta-Fantasma (Tabu)", title: "X10 · A Manta-Fantasma (Presságio Vivo & Santuário)", metrics: "NÃO-HOSTIL (135 PV, Def 24) • Avistamento CD 14", cunning: "Reconhece cascos pacíficos pelo som; guia navios por recifes mortais à noite (+4 Navegação) e afunda diante de baleeiros.", prep: "JAMAIS MATAR (causa motim imediato, -1 Fé Verdadeira e bloqueio em Corallis)! Nadar desarmado (CD 16) p/ raspar muco sem feri-la.", trophy: "1d3 Frascos de Muco Frio (600 PP cada: luz subaquática de 6m por 30 dias sem chama!) + Feito de Fé/Status ao salvá-la de caçadores." },

        { code: "X11", hab: "pantanos", short: "X11 Salamandra-de-Furna", title: "X11 · Salamandra-de-Furna (Engolidora-de-Tochas)", metrics: "114 PV • Def 23 Esq • RD 2 • Neurotoxina CD 18", cunning: "Cega e fria; ignora pedras jogadas na água e espera o ritmo de botas humanas para apagar a tocha num vácuo de sucção e puxar pro fundo.", prep: "Proibido tocha aberta! Usar Lanterna Blindada vedada ou Muco Frio (X10), luvas grossas, Antídoto (+4) e Cal Virgem Seca.", trophy: "1.800 PP • 4 doses de Bálsamo Sem-Dor (+4 Medicina cirúrgica em Baldbella) OU veneno Água-Muda no Submundo (U03+)." },
        { code: "X12", hab: "pantanos", short: "X12 Serpente-de-Âmbar", title: "X12 · Serpente-de-Âmbar (Sucuri-Real Ancestral)", metrics: "138 PV • Def 20 Esq • Constrição 3d8+6 • Rastro CD 18", cunning: "Sobe horas antes para os galhos acima do canal em Voernock (Z01) para cair sobre o homem do leme; foge por sifão se cortada.", prep: "Para obter o couro de 3.000 PP SEM FUROS: proibido lâminas/flechas! Usar Sonífero + Casca-amarga (H17), Corda de Seda e maças.", trophy: "3.000 PP imaculado (700 PP se furado) • Única Couraça de Escamas de Âmbar (Def +3, Pen 0, +1 Etiqueta/Persuasão nas cortes!)." }
    ];

    let curHab = "terras";
    let curCode = "X01";

    const beastTabsWrap = document.getElementById("lend-beast-tabs");
    const elTitle = document.getElementById("lp-title");
    const elMetrics = document.getElementById("lp-metrics");
    const elCunning = document.getElementById("lp-cunning");
    const elPrep = document.getElementById("lp-prep");
    const elTrophy = document.getElementById("lp-trophy");
    const btnCopy = document.getElementById("lp-copy");
    const elCopyFb = document.getElementById("lp-copy-fb");
    const btnJump = document.getElementById("lp-jump");

    function renderPlanner() {
        if (!beastTabsWrap || !elTitle) return;
        const list = BEASTS_DATA.filter(b => b.hab === curHab);
        if (!list.some(b => b.code === curCode)) {
            curCode = list[0].code;
        }
        beastTabsWrap.innerHTML = list.map(b =>
            `<button class="lend-tab-btn lend-beast-btn${b.code === curCode ? ' active' : ''}" data-code="${b.code}" type="button">${b.short}</button>`
        ).join("");

        beastTabsWrap.querySelectorAll(".lend-beast-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                curCode = btn.getAttribute("data-code");
                renderPlanner();
            });
        });

        const cur = BEASTS_DATA.find(b => b.code === curCode) || BEASTS_DATA[0];
        elTitle.textContent = cur.title;
        elMetrics.textContent = cur.metrics;
        elCunning.textContent = cur.cunning;
        elPrep.textContent = cur.prep;
        elTrophy.textContent = cur.trophy;
        if (btnJump) btnJump.setAttribute("href", "#" + cur.code.toLowerCase());
    }

    document.querySelectorAll(".lend-hab-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".lend-hab-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            curHab = btn.getAttribute("data-hab");
            renderPlanner();
        });
    });

    if (btnCopy) {
        btnCopy.addEventListener("click", () => {
            const cur = BEASTS_DATA.find(b => b.code === curCode) || BEASTS_DATA[0];
            const txt = `[Alenia RPG • Caçada Lendária ${cur.code}] ${cur.title} (${cur.metrics}) | Astúcia: ${cur.cunning} | Preparo: ${cur.prep} | Troféu: ${cur.trophy}`;
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(txt);
            }
            if (elCopyFb) {
                elCopyFb.textContent = "Plano copiado!";
                setTimeout(() => { elCopyFb.textContent = ""; }, 2000);
            }
        });
    }

    renderPlanner();

    // Filter X01-X12 Cards
    let filterHab = "ALL";
    const searchEl = document.getElementById("lend-search");
    const countEl = document.getElementById("lend-count");
    const emptyEl = document.getElementById("lend-empty");
    const cards = Array.from(document.querySelectorAll(".lend-card"));
    const groups = Array.from(document.querySelectorAll(".lend-group"));

    function applyFilter() {
        const q = (searchEl ? searchEl.value : "").trim().toLowerCase();
        let vis = 0;
        cards.forEach(c => {
            const hMatch = (filterHab === "ALL") || (c.getAttribute("data-habitat") === filterHab);
            const sBlob = (c.getAttribute("data-search") || "").toLowerCase();
            const qMatch = !q || sBlob.indexOf(q) !== -1;
            const show = hMatch && qMatch;
            c.classList.toggle("is-hidden", !show);
            if (show) vis++;
        });
        groups.forEach(g => {
            const anyVis = g.querySelectorAll(".lend-card:not(.is-hidden)").length > 0;
            g.classList.toggle("is-hidden", !anyVis);
        });
        if (countEl) countEl.textContent = `Exibindo ${vis} de ${cards.length} exemplares únicos`;
        if (emptyEl) emptyEl.style.display = (vis === 0) ? "block" : "none";
    }

    document.querySelectorAll(".lend-hab-pill").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".lend-hab-pill").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            filterHab = btn.getAttribute("data-habitat");
            applyFilter();
        });
    });
    if (searchEl) searchEl.addEventListener("input", applyFilter);
})();
"""


def _parse_bold_pairs(line: str):
    pairs = []
    for chunk in line.split("|"):
        m = re.match(r"^\s*\*\*([^*:]+):\*\*\s*(.+?)\s*$", chunk.strip())
        if m:
            pairs.append((m.group(1).strip(), m.group(2).strip()))
    return pairs


def _build_planner_html() -> str:
    return """
    <section class="lend-planner" id="planejador-cacada" aria-label="Planejador Interativo de Expedição de Caça">
        <div class="lend-insp-top">
            <div>
                <div class="lend-insp-kicker">GABINETE DE CAÇA &amp; NATURALISMO • DOZE EXEMPLARES ÚNICOS NO MUNDO</div>
                <div class="lend-insp-title">Planejador Tático de Rastreio, Isca, Contenção &amp; Troféus</div>
            </div>
            <div>
                <a id="lp-jump" class="lend-tab-btn" href="#x01" style="text-decoration:none; display:inline-block;">📜 Ir à Ficha Completa</a>
                <button id="lp-copy" class="lend-tab-btn active" type="button">📋 Copiar Plano</button>
                <span id="lp-copy-fb" class="lend-copy-fb" aria-live="polite"></span>
            </div>
        </div>
        <div class="lend-insp-controls">
            <div class="lend-hab-tabs">
                <button class="lend-tab-btn lend-hab-btn active" data-hab="terras" type="button">🦌 Matas, Montanhas &amp; Salares (X01–X06)</button>
                <button class="lend-tab-btn lend-hab-btn" data-hab="mares" type="button">🐋 Mares, Recifes &amp; Abismos (X07–X10)</button>
                <button class="lend-tab-btn lend-hab-btn" data-hab="pantanos" type="button">🦎 Furnas &amp; Pântanos (X11–X12)</button>
            </div>
            <div id="lend-beast-tabs" class="lend-beast-tabs"></div>
        </div>
        <div class="lend-insp-card">
            <div class="lend-insp-banner">
                <span id="lp-title" class="lend-insp-beasttitle">X01 · O Cervo-de-Escória (Galhada-de-Ferro)</span>
                <span id="lp-metrics" class="lend-insp-metrics">118 PV • Def 25 Ap / 20 Esq • RD 3 Frontal</span>
            </div>
            <div class="lend-insp-grid">
                <div class="lend-insp-box">
                    <div class="lend-insp-lbl">🧠 Astúcia de Soberano Solitário</div>
                    <div id="lp-cunning" class="lend-insp-txt"></div>
                </div>
                <div class="lend-insp-box">
                    <div class="lend-insp-lbl">🪤 Isca, Terreno &amp; Armamento Obrigatório</div>
                    <div id="lp-prep" class="lend-insp-txt"></div>
                </div>
                <div class="lend-insp-box" style="grid-column: 1 / -1;">
                    <div class="lend-insp-lbl">🏆 Troféu Irrepetível, Ofício Obra-Prima &amp; Peso Político</div>
                    <div id="lp-trophy" class="lend-insp-txt"></div>
                </div>
            </div>
        </div>
    </section>
    """


def render_lendarios_page(bk: dict, md_content: str, helpers: dict):
    """Build interactive illustrated Tomo XVIII — Animais Lendários de Alenia page."""
    inline_md = helpers["inline_md"]
    md_to_html = helpers["md_to_html"]
    img_dim_attrs = helpers["img_dim_attrs"]
    make_gm_gate_block = helpers["make_gm_gate_block"]
    render_toc_items = helpers["render_toc_items"]

    sections = re.split(r"(?=^##\s+)", md_content, flags=re.M)

    rules_sec = ""
    hab_secs = []
    summary_sec = ""
    gm_sec = ""
    shield_sec = ""

    hab_map = {
        "Terras interiores, matas e montanhas": ("terras", "", "lend-group-header", "BIOMA I • AURORA, GADDRA E KALIS — SEIS SOBERANOS CONTINENTAIS (X01–X06)"),
        "Os mares, recifes e abismos": ("mares", "mares-code", "lend-group-header mares-hdr", "BIOMA II • ROTAS OCEÂNICAS, CORALLIS E FOSSA DAS CINZAS — QUATRO LENDAS DO MAR (X07–X10)"),
        "Pântanos, ruínas e subterrâneos úmidos": ("pantanos", "pantanos-code", "lend-group-header pantanos-hdr", "BIOMA III • CISTERNAS PRÉ-FORJA E PÂNTANO DE VOERNOCK — DOIS SENHORES OCULTOS (X11–X12)"),
    }

    for sec in sections:
        s = sec.strip()
        m_h2 = re.match(r"^##\s+(.+)$", s, flags=re.M)
        if not m_h2:
            continue
        title = m_h2.group(1).strip()
        tl = title.lower()
        if tl.startswith("a arte da grande caçada"):
            rules_sec = s
        elif title in hab_map:
            hab_secs.append((title, s))
        elif tl.startswith("resumo comparativo"):
            summary_sec = s
        elif tl.startswith("caderno reservado ao mestre"):
            gm_sec = s
        elif tl.startswith("escudo de referência"):
            shield_sec = s

    toc_items = [
        (2, "A Arte da Grande Caçada: Rastreio, Contenção e Troféus", "arte-da-cacada"),
        (2, "Planejador Tático de Expedição (X01–X12)", "planejador-cacada"),
    ]

    # 1. Hunting Rules Drawer
    rules_inner, _ = md_to_html(rules_sec, id_prefix="hunt-", card_h3=False, inject_maps=False)
    rules_html = f"""
    <details class="lend-editorial" id="arte-da-cacada" open>
        <summary>🏹 Regras das Três Fases de Caçada, Lança c/ Travessa, Redes Lastradas, Extração &amp; Peso Político</summary>
        <div class="lend-editorial-inner">{rules_inner}</div>
    </details>
    """

    # 2. 12 Illustrated Sovereign Beast Cards
    groups_html = []
    total_beasts = 0
    for h_title, h_raw in hab_secs:
        h_key, code_cls, hdr_cls, kicker = hab_map[h_title]
        grp_id = f"bioma-{h_key}"
        toc_items.append((2, h_title, grp_id))

        parts = re.split(r"(?=^###\s+X(?:0[1-9]|1[0-2])\s)", h_raw, flags=re.M)
        cards = []
        for blk in parts[1:]:
            blines = blk.strip().splitlines()
            if not blines:
                continue
            m_h = re.match(r"^###\s+(X\d{2})\s+[—–-]\s+(.+)$", blines[0].strip())
            if not m_h:
                continue
            xcode, xname = m_h.group(1), re.sub(r"\*+|`", "", m_h.group(2)).strip()
            total_beasts += 1
            toc_items.append((3, f"{xcode} — {xname}", xcode.lower()))

            plate_html = ""
            tags = []
            body_lines = []
            for ln in blines[1:]:
                st = ln.strip()
                if not st:
                    body_lines.append("")
                    continue
                m_img = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", st)
                if m_img and not plate_html:
                    palt = m_img.group(1).strip() or f"{xcode} — {xname}"
                    psrc = "assets/" + os.path.basename(m_img.group(2).strip())
                    plate_html = (
                        f'<figure class="atlas-plate lend-plate" title="Clique para ampliar gravura naturalista">'
                        f'<img src="{html.escape(psrc, quote=True)}" alt="{html.escape(palt, quote=True)}"{img_dim_attrs(psrc)} decoding="async"/>'
                        f'<figcaption class="atlas-caption">{html.escape(palt)}</figcaption>'
                        f'</figure>'
                    )
                elif st.startswith("**Território Único:**") or st.startswith("**Rastreamento:**") or st.startswith("**Avistamento Respeitoso:**"):
                    for k_lbl, v_lbl in _parse_bold_pairs(st):
                        tags.append(f'<span class="lend-tag"><strong>{html.escape(k_lbl)}:</strong> {inline_md(v_lbl)}</span>')
                else:
                    body_lines.append(ln)

            b_html, _ = md_to_html("\n".join(body_lines), id_prefix=f"lg-{xcode.lower()}-", card_h3=False, inject_maps=False)
            s_blob = html.escape(f"{xcode} {xname} {h_title} {' '.join(blines[1:])}", quote=True)
            is_tabu = (xcode == "X10")
            card_cls = "lend-card sanctuary-card" if is_tabu else "lend-card"
            c_cls = "lend-code tabu-code" if is_tabu else f"lend-code {code_cls}".strip()
            badge_txt = "🕊 Presságio Vivo & Tabu Marítimo" if is_tabu else "✦ Indivíduo Único no Mundo"

            cards.append(f"""
            <article class="{card_cls}" id="{xcode.lower()}" data-habitat="{h_key}" data-search="{s_blob}">
                <div class="lend-card-head">
                    <div class="lend-head-left">
                        <span class="{c_cls}">{html.escape(xcode)}</span>
                        <h3 class="lend-card-title">{html.escape(xname)}</h3>
                    </div>
                    <span class="lend-unique-badge">{badge_txt}</span>
                </div>
                <div class="lend-tags">{"".join(tags)}</div>
                {plate_html}
                {b_html}
            </article>
            """)

        groups_html.append(f"""
        <section class="lend-group" id="{grp_id}" data-habitat="{h_key}">
            <header class="{hdr_cls}">
                <div class="lend-group-kicker">{kicker}</div>
                <h2 class="lend-group-title">{html.escape(h_title)}</h2>
            </header>
            {"".join(cards)}
        </section>
        """)

    # 3. Comparative Summary Table
    summary_html = ""
    if summary_sec:
        toc_items.append((2, "Resumo Comparativo de Caça e Troféus (X01–X12)", "resumo-comparativo"))
        sum_inner, _ = md_to_html(summary_sec, id_prefix="sum-x-", card_h3=False, inject_maps=False)
        summary_html = f'<section class="lend-divider" id="resumo-comparativo">{sum_inner}</section>'

    # 4. Sealed GM Vault
    gm_html = ""
    if gm_sec:
        gm_rendered, gm_toc = md_to_html(gm_sec, id_prefix="lend-gm-", card_h3=False, inject_maps=False)
        gm_html = (
            '<div class="lend-divider">'
            + make_gm_gate_block(
                "Caderno Reservado ao Mestre — Segredos dos 12 Soberanos e Consequências Sem Respawn",
                "Contém a ligação oculta do Quilha-Branca com Marella de Claramar, o dono do anel no bucho do Encouraçado, a arca sob a Salamandra-de-Furna e caçadores rivais. Insira a senha para revelar.",
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
        sh_inner, sh_toc = md_to_html(shield_sec, id_prefix="lend-ref-", card_h3=False, inject_maps=False)
        shield_html = f'<section class="lend-divider">{sh_inner}</section>'
        toc_items.extend(sh_toc)

    toolbar_html = f"""
    <div class="lend-toolbar" role="region" aria-label="Filtros dos 12 Animais Lendários">
        <div class="lend-pills">
            <button class="lend-pill lend-hab-pill active" data-habitat="ALL" type="button">Todos os Soberanos ({total_beasts})</button>
            <button class="lend-pill lend-hab-pill" data-habitat="terras" type="button">🦌 Terras, Matas &amp; Montanhas (6)</button>
            <button class="lend-pill lend-hab-pill" data-habitat="mares" type="button">🐋 Mares, Recifes &amp; Abismos (4)</button>
            <button class="lend-pill lend-hab-pill" data-habitat="pantanos" type="button">🦎 Furnas &amp; Pântanos (2)</button>
        </div>
        <div class="lend-search-row">
            <input id="lend-search" class="lend-search" type="search" placeholder="Buscar animal lendário (Kragh, Escória, Quilha-Branca, Manta-Fantasma, Âmbar, Voernock, X01–X12)..." aria-label="Buscar animais lendários"/>
            <span id="lend-count" class="lend-count">Exibindo {total_beasts} de {total_beasts} exemplares únicos</span>
        </div>
    </div>
    <div id="lend-empty" class="lend-empty">Nenhum exemplar lendário corresponde aos filtros atuais.</div>
    """

    hero_html = f"""
    <section class="lend-hero">
        <figure class="atlas-plate lend-hero-cover">
            <img src="{bk['cover_map']}" alt="Capa — {html.escape(bk['title'])}"{img_dim_attrs(bk['cover_map'])} decoding="async"/>
        </figure>
        <div>
            <div class="lend-kicker">ALENIA RPG • {html.escape(bk['num'])} • TRATADO NATURALISTA &amp; GRANDES CAÇADAS</div>
            <h1 class="lend-title">{html.escape(bk['title'])}</h1>
            <p class="lend-sub">Doze soberanos animais absolutamente únicos, solitários e astutos, com gravuras exclusivas, fichas auditadas, táticas de rastreio e troféus políticos.</p>
            <blockquote class="lend-epigraph">
                “Os bichos comuns correm da tocha e caem na primeira cova; estes doze sobreviveram aos reis que puseram preço nas suas cabeças porque aprenderam o cheiro do ferro, o alcance de uma besta e a pressa tola dos homens.”
            </blockquote>
            <div class="lend-stats">
                <span class="lend-stat-pill">🦌 6 Soberanos Continentais (X01–X06)</span>
                <span class="lend-stat-pill sea">🐋 4 Colossos &amp; Presságios do Mar (X07–X10)</span>
                <span class="lend-stat-pill moss">🦎 2 Senhores de Furna &amp; Pântano (X11–X12)</span>
                <span class="lend-stat-pill">🏆 Exemplares Únicos (Zero Respawn)</span>
            </div>
        </div>
    </section>
    """

    full_body = (
        hero_html
        + rules_html
        + _build_planner_html()
        + toolbar_html
        + f'<div id="lend-catalogue-root">{"".join(groups_html)}</div>'
        + summary_html
        + gm_html
        + shield_html
    )
    return full_body, toc_items
