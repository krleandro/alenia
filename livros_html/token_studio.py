#!/usr/bin/env python3
"""
Estúdio Gerador de Tokens HTML5 Canvas — Alenia RPG & Universal VTT (v2.0)
- 18 Molduras Profissionais: 12 Molduras Esculpidas Pintadas à Mão em HD (WebP RGBA inline) + 6 Clássicas/Customizáveis
- Suporte a upload de Moldura Própria (PNG transparente)
- 100% client-side (funciona online no Render e offline via file:// sem CORS taint)
- Drag & drop, upload de arquivo, Ctrl+V da área de transferência, pan/zoom/rotação/espelhar
- Tingimento não-destrutivo de molduras, faixa de nome (com caligrafia direta no pergaminho!) e exportação PNG 512/1024
"""
from token_frames_data import SCULPTED_FRAMES_JSON

TOKEN_STUDIO_CSS = r"""
/* =====================================================
   ESTÚDIO GERADOR DE TOKENS — ALENIA RPG & FIRECAST
   ===================================================== */
body.token-studio-mode .book-shell {
    padding: 68px 18px 56px;
}
body.token-studio-mode:not(.sidebar-hidden) .sidebar-backdrop {
    display: block;
}
body.token-studio-mode .book-page {
    max-width: 1340px;
    padding: 26px 30px 40px;
    background: radial-gradient(circle at top center, #221d18 0%, #171411 65%, #110e0c 100%);
    color: #efe6d2;
    border: 1px solid rgba(154, 123, 59, 0.45);
    box-shadow: 0 26px 70px rgba(0, 0, 0, 0.78);
}
body.token-studio-mode .book-page::before {
    inset: 8px;
    border: 1px solid rgba(154, 123, 59, 0.22);
}
body.token-studio-mode strong {
    color: var(--gold-light);
}

.ts-header {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 14px;
    padding-bottom: 16px;
    margin-bottom: 20px;
    border-bottom: 1px solid rgba(154, 123, 59, 0.38);
}
.ts-kicker {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10.5px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--gold-light);
    font-weight: 700;
}
.ts-title {
    font-family: 'Cinzel', Georgia, serif !important;
    font-size: 27px !important;
    color: #f7f1e3 !important;
    margin: 3px 0 2px !important;
    border: none !important;
    padding: 0 !important;
}
.ts-sub {
    margin: 0;
    font-style: italic;
    font-size: 15px;
    color: #bfb5a2;
}
.ts-header-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    align-items: center;
}
.ts-rpk-link {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10.5px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    text-decoration: none;
    padding: 8px 14px;
    border-radius: 3px;
    background: rgba(154, 123, 59, 0.16);
    border: 1px solid rgba(205, 176, 110, 0.55);
    color: var(--gold-light);
    font-weight: 700;
    transition: all 0.15s ease;
}
.ts-rpk-link:hover {
    background: rgba(154, 123, 59, 0.32);
    color: #fff;
}

.ts-workspace {
    display: grid;
    grid-template-columns: minmax(340px, 490px) 1fr;
    gap: 24px;
    align-items: start;
}

/* LEFT COLUMN: INTERACTIVE PREVIEW STAGE */
.ts-stage-card {
    background: rgba(28, 24, 20, 0.94);
    border: 1px solid rgba(154, 123, 59, 0.42);
    border-radius: 5px;
    padding: 18px;
    position: sticky;
    top: 66px;
}
.ts-canvas-wrap {
    position: relative;
    width: 100%;
    aspect-ratio: 1 / 1;
    max-width: 452px;
    margin: 0 auto 14px;
    border-radius: 6px;
    border: 2px dashed rgba(154, 123, 59, 0.45);
    overflow: hidden;
    cursor: grab;
    user-select: none;
    touch-action: none;
    transition: border-color 0.18s ease, box-shadow 0.18s ease;
}
.ts-canvas-wrap:active { cursor: grabbing; }
.ts-canvas-wrap.drag-over {
    border-color: var(--gold-light);
    border-style: solid;
    box-shadow: 0 0 24px rgba(205, 176, 110, 0.4);
}
.ts-canvas-wrap.bg-checker {
    background-color: #25221e;
    background-image:
        linear-gradient(45deg, #322d27 25%, transparent 25%),
        linear-gradient(-45deg, #322d27 25%, transparent 25%),
        linear-gradient(45deg, transparent 75%, #322d27 75%),
        linear-gradient(-45deg, transparent 75%, #322d27 75%);
    background-size: 24px 24px;
    background-position: 0 0, 0 12px, 12px -12px, -12px 0;
}
.ts-canvas-wrap.bg-dark { background: #101216; }
.ts-canvas-wrap.bg-parchment { background: #e8dcc1; }
.ts-canvas-wrap.bg-map {
    background: radial-gradient(circle at center, #2f3b2c 0%, #1c241b 100%);
}
#token-canvas {
    width: 100%;
    height: 100%;
    display: block;
}
.ts-drop-hint {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(16, 13, 10, 0.78);
    color: var(--gold-light);
    font-family: 'Cinzel', Georgia, serif;
    font-size: 15px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.15s ease;
}
.ts-canvas-wrap.drag-over .ts-drop-hint { opacity: 1; }

.ts-stage-tip {
    text-align: center;
    font-size: 13px;
    font-style: italic;
    color: #aba08d;
    margin: 0 0 12px;
}

.ts-quick-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    justify-content: center;
    margin-bottom: 14px;
}
.ts-btn {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10.5px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 7px 11px;
    border-radius: 3px;
    border: 1px solid rgba(154, 123, 59, 0.45);
    background: rgba(255, 255, 255, 0.05);
    color: #e8decb;
    cursor: pointer;
    transition: all 0.14s ease;
}
.ts-btn:hover {
    background: rgba(154, 123, 59, 0.24);
    border-color: var(--gold-light);
    color: #fff;
}
.ts-btn.active {
    background: rgba(122, 31, 29, 0.78);
    border-color: var(--gold-light);
    color: #fff;
}
.ts-btn-primary {
    background: linear-gradient(180deg, #8f2522 0%, #6d1917 100%);
    border-color: var(--gold-light);
    color: #fff7e6;
    font-weight: 700;
    padding: 10px 14px;
    font-size: 11px;
}
.ts-btn-primary:hover {
    background: linear-gradient(180deg, #a82d2a 0%, #7d1e1c 100%);
    box-shadow: 0 4px 14px rgba(122, 31, 29, 0.45);
}
.ts-btn-gold {
    background: linear-gradient(180deg, #a88642 0%, #7d612a 100%);
    border-color: #e6cc8a;
    color: #16110b;
    font-weight: 700;
    padding: 10px 14px;
    font-size: 11px;
}
.ts-btn-gold:hover {
    background: linear-gradient(180deg, #bfa059 0%, #927333 100%);
    color: #0e0a06;
}

.ts-export-box {
    border-top: 1px solid rgba(154, 123, 59, 0.32);
    padding-top: 14px;
}
.ts-export-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-bottom: 8px;
}
.ts-export-row-2 {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 8px;
    align-items: center;
}
.ts-filename-input {
    width: 100%;
    padding: 7px 10px;
    border-radius: 3px;
    border: 1px solid rgba(154, 123, 59, 0.42);
    background: #13100d;
    color: #f7f1e3;
    font-family: 'EB Garamond', Georgia, serif;
    font-size: 14.5px;
}
.ts-status-toast {
    min-height: 20px;
    margin-top: 8px;
    text-align: center;
    font-size: 13.5px;
    color: #93d6a2;
    font-style: italic;
}

/* RIGHT COLUMN: FRAMES & CUSTOMIZATION PANELS */
.ts-panels {
    display: flex;
    flex-direction: column;
    gap: 16px;
}
.ts-panel {
    background: rgba(28, 24, 20, 0.94);
    border: 1px solid rgba(154, 123, 59, 0.38);
    border-radius: 5px;
    padding: 16px 18px;
}
.ts-panel-title {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 12.5px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--gold-light);
    margin: 0 0 12px;
    padding-bottom: 7px;
    border-bottom: 1px solid rgba(154, 123, 59, 0.25);
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
}
.ts-panel-title span {
    font-family: 'EB Garamond', Georgia, serif;
    font-size: 13px;
    font-style: italic;
    text-transform: none;
    letter-spacing: 0;
    color: #a69c8a;
}

.ts-cat-tabs {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 6px;
    margin-bottom: 12px;
}
.ts-cat-tab {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 5px 10px;
    border-radius: 3px;
    border: 1px solid rgba(154, 123, 59, 0.36);
    background: rgba(255, 255, 255, 0.04);
    color: #cfc4b0;
    cursor: pointer;
    transition: all 0.14s ease;
}
.ts-cat-tab:hover { border-color: var(--gold-light); color: #fff; }
.ts-cat-tab.active {
    background: var(--crimson);
    border-color: var(--gold-light);
    color: #fff6e0;
    font-weight: 700;
}
.ts-cat-tab.upload-custom {
    margin-left: auto;
    background: rgba(31, 81, 86, 0.35);
    border-color: rgba(121, 184, 190, 0.55);
    color: #c8ecef;
}
.ts-cat-tab.upload-custom:hover {
    background: rgba(31, 81, 86, 0.65);
    color: #fff;
}

/* 18-FRAME VISUAL GALLERY */
.ts-frames-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(112px, 1fr));
    gap: 10px;
}
.ts-frame-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 5px;
    padding: 7px 5px 7px;
    border-radius: 4px;
    border: 1px solid rgba(154, 123, 59, 0.28);
    background: rgba(16, 14, 11, 0.78);
    color: #ded5c3;
    cursor: pointer;
    transition: all 0.15s ease;
    text-align: center;
}
.ts-frame-btn.is-hidden { display: none; }
.ts-frame-btn:hover {
    border-color: var(--gold-light);
    background: rgba(154, 123, 59, 0.14);
    transform: translateY(-2px);
}
.ts-frame-btn.active {
    border-color: #e6cc8a;
    background: rgba(122, 31, 29, 0.44);
    box-shadow: 0 0 0 1px #e6cc8a, 0 4px 14px rgba(0, 0, 0, 0.45);
    color: #fff6e0;
}
.ts-frame-thumb {
    width: 82px;
    height: 82px;
    display: block;
}
.ts-frame-name {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 9.2px;
    line-height: 1.25;
    letter-spacing: 0.04em;
    font-weight: 600;
}

/* CONTROLS GRID */
.ts-controls-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px 18px;
}
.ts-field {
    display: flex;
    flex-direction: column;
    gap: 4px;
}
.ts-field.full { grid-column: 1 / -1; }
.ts-field label {
    display: flex;
    justify-content: space-between;
    font-family: 'Cinzel', Georgia, serif;
    font-size: 10px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #cfc4b0;
}
.ts-field label strong {
    color: var(--gold-light);
    font-weight: 700;
}
.ts-field input[type="range"] {
    width: 100%;
    accent-color: #b58d46;
    cursor: pointer;
}
.ts-field input[type="text"] {
    padding: 7px 10px;
    border-radius: 3px;
    border: 1px solid rgba(154, 123, 59, 0.42);
    background: #13100d;
    color: #f7f1e3;
    font-family: 'EB Garamond', Georgia, serif;
    font-size: 15px;
}
.ts-color-row {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 6px;
}
.ts-swatch {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    border: 2px solid rgba(255, 255, 255, 0.25);
    cursor: pointer;
    padding: 0;
    transition: transform 0.12s ease, border-color 0.12s ease;
}
.ts-swatch:hover { transform: scale(1.12); border-color: #fff; }
.ts-swatch.active { border-color: #fff; box-shadow: 0 0 0 2px var(--gold-light); }
.ts-color-input {
    width: 34px;
    height: 26px;
    border: 1px solid rgba(154, 123, 59, 0.55);
    border-radius: 3px;
    background: #13100d;
    cursor: pointer;
    padding: 1px;
}
.ts-check-label {
    display: inline-flex !important;
    align-items: center;
    gap: 7px;
    cursor: pointer;
    text-transform: none !important;
    font-family: 'EB Garamond', Georgia, serif !important;
    font-size: 15px !important;
    letter-spacing: 0 !important;
    color: #e8decb !important;
}
.ts-bg-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    justify-content: center;
    margin-bottom: 10px;
}
.ts-bg-pill {
    font-family: 'Cinzel', Georgia, serif;
    font-size: 9px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 4px 8px;
    border-radius: 2px;
    border: 1px solid rgba(154, 123, 59, 0.32);
    background: transparent;
    color: #b5ab98;
    cursor: pointer;
}
.ts-bg-pill.active {
    background: rgba(154, 123, 59, 0.26);
    border-color: var(--gold-light);
    color: #fff;
}

@media (max-width: 980px) {
    .ts-workspace { grid-template-columns: 1fr; }
    .ts-stage-card { position: static; }
    .ts-controls-grid { grid-template-columns: 1fr; }
}
@media (max-width: 600px) {
    body.token-studio-mode .book-page { padding: 18px 14px 32px; }
    .ts-export-row { grid-template-columns: 1fr; }
}
"""

TOKEN_STUDIO_HTML = r"""
<section class="ts-header">
    <div>
        <div class="ts-kicker">ALENIA RPG &amp; UNIVERSAL VTT • ESTÚDIO DE TOKENS v2.0</div>
        <h1 class="ts-title">Gerador de Tokens</h1>
        <p class="ts-sub">12 molduras esculpidas pintadas à mão em HD + 6 molduras clássicas/customizáveis. Enquadre sua arte na hora e baixe o PNG transparente pronto para o Firecast.</p>
    </div>
    <div class="ts-header-actions">
        <a class="ts-rpk-link" href="https://raw.githubusercontent.com/krleandro/alenia/main/plugins/Alenia_Token_Studio.rpk">⬇ Baixar Plugin Firecast (Token Studio .rpk)</a>
    </div>
</section>

<div class="ts-workspace">
    <!-- ESQUERDA: PRÉVIA INTERATIVA & EXPORTAÇÃO -->
    <div class="ts-stage-card">
        <div id="ts-canvas-wrap" class="ts-canvas-wrap bg-checker" title="Arraste para mover a imagem • Roda do mouse para zoom • Solte um arquivo aqui">
            <canvas id="token-canvas" width="1024" height="1024"></canvas>
            <div class="ts-drop-hint">Solte a imagem aqui</div>
        </div>

        <div class="ts-bg-pills" role="group" aria-label="Fundo da bancada de prévia">
            <button class="ts-bg-pill active" data-bg="bg-checker" type="button">Transparente</button>
            <button class="ts-bg-pill" data-bg="bg-dark" type="button">Escuro</button>
            <button class="ts-bg-pill" data-bg="bg-map" type="button">Mapa</button>
            <button class="ts-bg-pill" data-bg="bg-parchment" type="button">Pergaminho</button>
        </div>

        <p class="ts-stage-tip">Arraste a arte para reposicionar · Roda do mouse para zoom · <strong>Ctrl+V</strong> para colar imagem</p>

        <input id="ts-file-input" type="file" accept="image/*" style="display:none;"/>
        <input id="ts-custom-frame-input" type="file" accept="image/png,image/webp" style="display:none;"/>
        <div class="ts-quick-bar">
            <button id="ts-btn-upload" class="ts-btn ts-btn-gold" type="button">📁 Escolher Imagem</button>
            <button id="ts-btn-flip" class="ts-btn" type="button" title="Espelhar horizontalmente">⇄ Espelhar</button>
            <button id="ts-btn-center" class="ts-btn" type="button" title="Centralizar imagem">◎ Centralizar</button>
            <button id="ts-btn-fit" class="ts-btn" type="button" title="Ajustar zoom automático">⛶ Ajustar</button>
        </div>

        <div class="ts-export-box">
            <div class="ts-export-row">
                <button id="ts-export-512" class="ts-btn ts-btn-primary" type="button">⬇ Baixar PNG 512×512</button>
                <button id="ts-export-1024" class="ts-btn ts-btn-gold" type="button">⬇ Baixar PNG 1024×1024</button>
            </div>
            <div class="ts-export-row-2">
                <input id="ts-filename" class="ts-filename-input" type="text" value="token_alenia" placeholder="Nome do arquivo (sem .png)" aria-label="Nome do arquivo de saída"/>
                <button id="ts-btn-copy" class="ts-btn" type="button" title="Copiar PNG transparente para área de transferência">📋 Copiar PNG</button>
            </div>
            <div id="ts-status" class="ts-status-toast" aria-live="polite"></div>
        </div>
    </div>

    <!-- DIREITA: 18 MOLDURAS + AJUSTES -->
    <div class="ts-panels">
        <div class="ts-panel">
            <div class="ts-panel-title">
                1. Escolha a Moldura
                <span>12 esculpidas pintadas à mão + 6 clássicas</span>
            </div>
            <div class="ts-cat-tabs" role="tablist">
                <button class="ts-cat-tab active" data-cat="ALL" type="button">Todas (18)</button>
                <button class="ts-cat-tab" data-cat="Esculpida" type="button">✦ Esculpidas HD (12)</button>
                <button class="ts-cat-tab" data-cat="Classica" type="button">◎ Clássicas &amp; Livres (6)</button>
                <button id="ts-btn-custom-frame" class="ts-cat-tab upload-custom" type="button" title="Carregar sua própria moldura PNG transparente">+ Subir Moldura PNG</button>
            </div>
            <div id="ts-frames-grid" class="ts-frames-grid"></div>
        </div>

        <div class="ts-panel">
            <div class="ts-panel-title">
                2. Enquadramento &amp; Iluminação da Arte
                <span>Ajuste fino</span>
            </div>
            <div class="ts-controls-grid">
                <div class="ts-field">
                    <label for="ts-zoom">Zoom <strong id="ts-zoom-val">100%</strong></label>
                    <input id="ts-zoom" type="range" min="40" max="350" value="100" step="1"/>
                </div>
                <div class="ts-field">
                    <label for="ts-rotate">Rotação <strong id="ts-rotate-val">0°</strong></label>
                    <input id="ts-rotate" type="range" min="-180" max="180" value="0" step="1"/>
                </div>
                <div class="ts-field">
                    <label for="ts-shadow">Sombra Interna 3D <strong id="ts-shadow-val">45%</strong></label>
                    <input id="ts-shadow" type="range" min="0" max="100" value="45" step="1"/>
                </div>
                <div class="ts-field">
                    <label for="ts-thickness"><span id="ts-thickness-lbl">Escala da Moldura</span> <strong id="ts-thickness-val">100%</strong></label>
                    <input id="ts-thickness" type="range" min="70" max="140" value="100" step="2"/>
                </div>
                <div class="ts-field full">
                    <label>Fundo Interno da Arte (para PNGs com transparência)</label>
                    <div class="ts-color-row">
                        <label class="ts-check-label">
                            <input id="ts-bg-transparent" type="checkbox"/> Fundo interno transparente
                        </label>
                        <input id="ts-inner-bg" class="ts-color-input" type="color" value="#17191f" title="Cor de fundo atrás do personagem"/>
                    </div>
                </div>
            </div>
        </div>

        <div class="ts-panel">
            <div class="ts-panel-title">
                3. Tingimento da Moldura &amp; Faixa de Nome
                <span>Opcional</span>
            </div>
            <div class="ts-controls-grid">
                <div class="ts-field full">
                    <label>Cor / Tingimento da Moldura <strong id="ts-accent-label">Cor Original</strong></label>
                    <div class="ts-color-row" id="ts-swatches">
                        <button class="ts-btn" id="ts-reset-tint" type="button" style="padding:4px 8px; font-size:9.5px;">↺ Original</button>
                        <button class="ts-swatch" data-color="#d4af57" style="background:#d4af57" title="Ouro Real" type="button"></button>
                        <button class="ts-swatch" data-color="#b52424" style="background:#b52424" title="Carmesim / Inimigo" type="button"></button>
                        <button class="ts-swatch" data-color="#289488" style="background:#289488" title="Turquesa / Aliado" type="button"></button>
                        <button class="ts-swatch" data-color="#4e79c7" style="background:#4e79c7" title="Azul Adamante" type="button"></button>
                        <button class="ts-swatch" data-color="#8452b5" style="background:#8452b5" title="Púrpura Arcano" type="button"></button>
                        <button class="ts-swatch" data-color="#3c9c50" style="background:#3c9c50" title="Verde Silvano" type="button"></button>
                        <button class="ts-swatch" data-color="#c4c9d4" style="background:#c4c9d4" title="Prata" type="button"></button>
                        <button class="ts-swatch" data-color="#323640" style="background:#323640" title="Ferro Negro" type="button"></button>
                        <input id="ts-custom-color" class="ts-color-input" type="color" value="#d4af57" title="Escolher cor livre"/>
                    </div>
                </div>
                <div class="ts-field">
                    <label for="ts-banner-text">Faixa de Nome na Base</label>
                    <input id="ts-banner-text" type="text" maxlength="24" placeholder="Ex.: Severor, Guarda 1 (opcional)"/>
                </div>
                <div class="ts-field">
                    <label for="ts-banner-color">Cor da Faixa (Exceto Pergaminho)</label>
                    <div class="ts-color-row">
                        <input id="ts-banner-color" class="ts-color-input" type="color" value="#5e1715"/>
                        <span style="font-size:13px; color:#aba08d; font-style:italic;">Na moldura Pergaminho, escreve direto na fita</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
"""

TOKEN_STUDIO_JS = (
    "const SCULPTED_FRAMES_RAW = " + SCULPTED_FRAMES_JSON + ";\n"
    + r"""
(function() {
    const canvas = document.getElementById('token-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const SIZE = 1024;

    const PROCEDURAL_FRAMES = [
        { id: 'ouro_aurora', name: 'Ouro de Aurora', category: 'Classica', kind: 'proc', shape: 'circle', defaultTint: null, palette: ['#f3dc92', '#c89b3c', '#6e4c14', '#7a1f1d'] },
        { id: 'chama_solar', name: 'Chama Solar', category: 'Classica', kind: 'proc', shape: 'circle', defaultTint: null, palette: ['#fce394', '#cf8928', '#7a1f1d', '#f5b841'] },
        { id: 'chefe_ameaca', name: 'Chefe / Elite', category: 'Classica', kind: 'proc', shape: 'circle', defaultTint: null, palette: ['#f5d06e', '#991e1b', '#260808', '#ff7b39'] },
        { id: 'prata_classica', name: 'Prata Clássica', category: 'Classica', kind: 'proc', shape: 'circle', defaultTint: null, palette: ['#f4f7fa', '#9ca5b4', '#3b424f', '#ffffff'] },
        { id: 'hexagonal_tatico', name: 'Hexagonal', category: 'Classica', kind: 'proc', shape: 'hex', defaultTint: null, palette: ['#e5c574', '#8e6b2c', '#3b290f', '#204d54'] },
        { id: 'anel_limpo', name: 'Anel Livre', category: 'Classica', kind: 'proc', shape: 'circle', defaultTint: '#d4af57', palette: ['#f2dc9b', '#d4af57', '#634918', '#ffffff'] },
    ];

    const FRAMES = [
        ...SCULPTED_FRAMES_RAW.map(f => ({
            ...f,
            kind: 'image',
            shape: 'circle',
            imgObj: null,
            loaded: false,
        })),
        ...PROCEDURAL_FRAMES,
    ];

    const state = {
        img: null,
        frameId: FRAMES[0].id,
        category: 'ALL',
        zoom: 1.0,
        offsetX: 0,
        offsetY: 0,
        rotation: 0,
        flipX: false,
        shadow: 0.45,
        thickness: 1.0,
        customTint: null,
        innerBgTransparent: false,
        innerBgColor: '#17191f',
        bannerText: '',
        bannerColor: '#5e1715',
    };

    function hexToRgb(hex) {
        const h = (hex || '#d4af57').replace('#', '');
        const full = h.length === 3 ? h.split('').map(c => c + c).join('') : h;
        const n = parseInt(full, 16);
        return { r: (n >> 16) & 255, g: (n >> 8) & 255, b: n & 255 };
    }
    function mixColor(hex, factor) {
        const { r, g, b } = hexToRgb(hex);
        const f = Math.max(-1, Math.min(1, factor));
        const adj = c => f >= 0 ? Math.round(c + (255 - c) * f) : Math.round(c * (1 + f));
        return `rgb(${adj(r)},${adj(g)},${adj(b)})`;
    }

    // Untainted default sample portrait
    function createSamplePortrait() {
        const sc = document.createElement('canvas');
        sc.width = 768;
        sc.height = 768;
        const c = sc.getContext('2d');
        const bg = c.createRadialGradient(384, 300, 40, 384, 420, 460);
        bg.addColorStop(0, '#5a3a22');
        bg.addColorStop(0.5, '#2b201b');
        bg.addColorStop(1, '#121116');
        c.fillStyle = bg;
        c.fillRect(0, 0, 768, 768);

        const sun = c.createRadialGradient(384, 330, 12, 384, 330, 210);
        sun.addColorStop(0, 'rgba(255, 218, 132, 0.92)');
        sun.addColorStop(0.45, 'rgba(214, 122, 54, 0.45)');
        sun.addColorStop(1, 'rgba(214, 122, 54, 0)');
        c.fillStyle = sun;
        c.fillRect(0, 0, 768, 768);

        c.fillStyle = '#1b171b';
        c.beginPath();
        c.moveTo(0, 520); c.lineTo(130, 390); c.lineTo(260, 460);
        c.lineTo(420, 360); c.lineTo(590, 455); c.lineTo(768, 370);
        c.lineTo(768, 768); c.lineTo(0, 768); c.closePath();
        c.fill();

        c.fillStyle = '#161418';
        c.beginPath();
        c.moveTo(165, 768);
        c.quadraticCurveTo(215, 480, 315, 425);
        c.lineTo(455, 425);
        c.quadraticCurveTo(555, 480, 605, 768);
        c.closePath();
        c.fill();

        const cloak = c.createLinearGradient(250, 430, 520, 720);
        cloak.addColorStop(0, '#8a2320');
        cloak.addColorStop(1, '#3b1111');
        c.fillStyle = cloak;
        c.beginPath();
        c.moveTo(220, 768);
        c.quadraticCurveTo(255, 510, 340, 442);
        c.lineTo(425, 442);
        c.quadraticCurveTo(495, 510, 525, 768);
        c.closePath();
        c.fill();

        const helm = c.createLinearGradient(320, 210, 448, 430);
        helm.addColorStop(0, '#9ba6b5');
        helm.addColorStop(0.5, '#4c5461');
        helm.addColorStop(1, '#1e2229');
        c.fillStyle = helm;
        c.beginPath();
        c.ellipse(384, 316, 74, 96, 0, 0, Math.PI * 2);
        c.fill();

        c.fillStyle = '#0c0d10';
        c.fillRect(326, 304, 116, 16);
        c.strokeStyle = '#d8b464';
        c.lineWidth = 4;
        c.beginPath();
        c.moveTo(384, 224); c.lineTo(384, 408);
        c.stroke();

        return sc;
    }

    const sampleImg = createSamplePortrait();

    function traceHexPath(c, cx, cy, r, keepPath) {
        if (!keepPath) c.beginPath();
        for (let i = 0; i < 6; i++) {
            const a = (Math.PI / 3) * i - Math.PI / 2;
            const x = cx + r * Math.cos(a);
            const y = cy + r * Math.sin(a);
            if (i === 0) c.moveTo(x, y);
            else c.lineTo(x, y);
        }
        c.closePath();
    }

    function getFrameObj(id) {
        return FRAMES.find(f => f.id === id) || FRAMES[0];
    }

    function drawGem(c, x, y, r, color) {
        c.save();
        c.beginPath();
        c.arc(x, y, r + 3.5, 0, Math.PI * 2);
        c.fillStyle = '#2d1e0c';
        c.fill();
        const g = c.createRadialGradient(x - r * 0.35, y - r * 0.35, r * 0.1, x, y, r);
        g.addColorStop(0, '#ffffff');
        g.addColorStop(0.28, mixColor(color, 0.35));
        g.addColorStop(0.75, color);
        g.addColorStop(1, mixColor(color, -0.55));
        c.beginPath();
        c.arc(x, y, r, 0, Math.PI * 2);
        c.fillStyle = g;
        c.fill();
        c.restore();
    }

    function drawRivet(c, x, y, r, lightCol, darkCol) {
        c.save();
        const g = c.createRadialGradient(x - r * 0.35, y - r * 0.35, r * 0.15, x, y, r);
        g.addColorStop(0, lightCol);
        g.addColorStop(0.7, darkCol);
        g.addColorStop(1, '#0e0b08');
        c.beginPath();
        c.arc(x, y, r, 0, Math.PI * 2);
        c.fillStyle = g;
        c.fill();
        c.restore();
    }

    function drawProceduralFrame(c, frame, sz, cfg) {
        const cx = sz / 2;
        const cy = sz / 2;
        const sc = sz / 1024;
        const thick = (cfg.thickness || 1.0);
        const outerR = (frame.id === 'chama_solar' || frame.id === 'chefe_ameaca') ? 470 * sc : 494 * sc;
        const ringW = Math.max(26, Math.min(110, 62 * thick)) * sc;
        const innerR = outerR - ringW;
        const midR = (outerR + innerR) / 2;

        let [cLight, cMid, cDark, cAcc] = frame.palette;
        if (cfg.customTint) {
            cLight = mixColor(cfg.customTint, 0.45);
            cMid = cfg.customTint;
            cDark = mixColor(cfg.customTint, -0.55);
            if (frame.id === 'anel_limpo') cAcc = mixColor(cfg.customTint, 0.72);
        }

        c.save();

        if (frame.shape === 'hex') {
            traceHexPath(c, cx, cy, outerR, false);
            traceHexPath(c, cx, cy, innerR, true);
            const mg = c.createLinearGradient(cx - outerR, cy - outerR, cx + outerR, cy + outerR);
            mg.addColorStop(0, cLight);
            mg.addColorStop(0.28, cMid);
            mg.addColorStop(0.55, cDark);
            mg.addColorStop(0.82, cMid);
            mg.addColorStop(1, cLight);
            c.fillStyle = mg;
            c.fill('evenodd');

            traceHexPath(c, cx, cy, outerR - 2 * sc, false);
            c.strokeStyle = 'rgba(18, 12, 6, 0.85)';
            c.lineWidth = 5 * sc;
            c.stroke();

            traceHexPath(c, cx, cy, midR, false);
            c.strokeStyle = cAcc;
            c.lineWidth = Math.max(4, ringW * 0.22);
            c.stroke();

            traceHexPath(c, cx, cy, innerR + 2 * sc, false);
            c.strokeStyle = cLight;
            c.lineWidth = 4 * sc;
            c.stroke();

            for (let i = 0; i < 6; i++) {
                const a = (Math.PI / 3) * i - Math.PI / 2;
                drawRivet(c, cx + midR * Math.cos(a), cy + midR * Math.sin(a), 11 * sc, cLight, cDark);
            }
            c.restore();
            return;
        }

        if (frame.id === 'chama_solar') {
            const rays = 16;
            for (let i = 0; i < rays; i++) {
                const a = (Math.PI * 2 / rays) * i;
                const tipR = (i % 2 === 0 ? 506 : 492) * sc;
                const spread = (i % 2 === 0 ? 0.085 : 0.06);
                c.beginPath();
                c.moveTo(cx + (outerR - 6 * sc) * Math.cos(a - spread), cy + (outerR - 6 * sc) * Math.sin(a - spread));
                c.lineTo(cx + tipR * Math.cos(a), cy + tipR * Math.sin(a));
                c.lineTo(cx + (outerR - 6 * sc) * Math.cos(a + spread), cy + (outerR - 6 * sc) * Math.sin(a + spread));
                c.closePath();
                c.fillStyle = i % 2 === 0 ? cLight : cMid;
                c.fill();
                c.strokeStyle = cDark;
                c.lineWidth = 2.5 * sc;
                c.stroke();
            }
        } else if (frame.id === 'chefe_ameaca') {
            const spikes = 8;
            for (let i = 0; i < spikes; i++) {
                const a = (Math.PI * 2 / spikes) * i - Math.PI / 2;
                const tipR = 508 * sc;
                c.beginPath();
                c.moveTo(cx + (outerR - 8 * sc) * Math.cos(a - 0.11), cy + (outerR - 8 * sc) * Math.sin(a - 0.11));
                c.lineTo(cx + tipR * Math.cos(a), cy + tipR * Math.sin(a));
                c.lineTo(cx + (outerR - 8 * sc) * Math.cos(a + 0.11), cy + (outerR - 8 * sc) * Math.sin(a + 0.11));
                c.closePath();
                const sg = c.createLinearGradient(cx + outerR * Math.cos(a), cy + outerR * Math.sin(a), cx + tipR * Math.cos(a), cy + tipR * Math.sin(a));
                sg.addColorStop(0, cDark);
                sg.addColorStop(0.55, cMid);
                sg.addColorStop(1, cLight);
                c.fillStyle = sg;
                c.fill();
                c.strokeStyle = '#180505';
                c.lineWidth = 3 * sc;
                c.stroke();
            }
        }

        const mg = c.createLinearGradient(cx - outerR, cy - outerR, cx + outerR, cy + outerR);
        mg.addColorStop(0, cLight);
        mg.addColorStop(0.24, cMid);
        mg.addColorStop(0.5, cDark);
        mg.addColorStop(0.76, cMid);
        mg.addColorStop(1, cLight);

        c.beginPath();
        c.arc(cx, cy, outerR, 0, Math.PI * 2);
        c.arc(cx, cy, innerR, 0, Math.PI * 2, true);
        c.fillStyle = mg;
        c.fill('evenodd');

        const rad = c.createRadialGradient(cx, cy, innerR, cx, cy, outerR);
        rad.addColorStop(0, 'rgba(0,0,0,0.48)');
        rad.addColorStop(0.18, 'rgba(255,255,255,0.28)');
        rad.addColorStop(0.5, 'rgba(255,255,255,0.02)');
        rad.addColorStop(0.84, 'rgba(255,255,255,0.22)');
        rad.addColorStop(1, 'rgba(0,0,0,0.58)');
        c.beginPath();
        c.arc(cx, cy, outerR, 0, Math.PI * 2);
        c.arc(cx, cy, innerR, 0, Math.PI * 2, true);
        c.fillStyle = rad;
        c.fill('evenodd');

        if (frame.id === 'ouro_aurora') {
            c.beginPath();
            c.arc(cx, cy, midR, 0, Math.PI * 2);
            c.strokeStyle = cAcc;
            c.lineWidth = ringW * 0.24;
            c.stroke();
            for (let i = 0; i < 8; i++) {
                const a = (Math.PI / 4) * i;
                if (i % 2 === 0) drawGem(c, cx + midR * Math.cos(a), cy + midR * Math.sin(a), 14 * sc, cAcc);
                else drawRivet(c, cx + midR * Math.cos(a), cy + midR * Math.sin(a), 7.5 * sc, cLight, cDark);
            }
        } else if (frame.id === 'chama_solar') {
            c.beginPath();
            c.arc(cx, cy, midR, 0, Math.PI * 2);
            c.strokeStyle = cDark;
            c.lineWidth = ringW * 0.28;
            c.stroke();
            c.beginPath();
            c.arc(cx, cy, innerR + 4 * sc, 0, Math.PI * 2);
            c.strokeStyle = '#fff0be';
            c.lineWidth = 4 * sc;
            c.stroke();
        } else if (frame.id === 'chefe_ameaca') {
            c.beginPath();
            c.arc(cx, cy, midR, 0, Math.PI * 2);
            c.strokeStyle = '#380908';
            c.lineWidth = ringW * 0.36;
            c.stroke();
            c.beginPath();
            c.arc(cx, cy, innerR + 5 * sc, 0, Math.PI * 2);
            c.strokeStyle = cAcc;
            c.lineWidth = 5 * sc;
            c.stroke();
            for (let i = 0; i < 4; i++) {
                const a = (Math.PI / 2) * i;
                drawGem(c, cx + midR * Math.cos(a), cy + midR * Math.sin(a), 14 * sc, '#ff592b');
            }
        } else if (frame.id === 'prata_classica' || frame.id === 'anel_limpo') {
            c.beginPath();
            c.arc(cx, cy, innerR + 3 * sc, 0, Math.PI * 2);
            c.strokeStyle = 'rgba(255,255,255,0.4)';
            c.lineWidth = 3 * sc;
            c.stroke();
        }

        c.beginPath();
        c.arc(cx, cy, outerR - 1.5 * sc, 0, Math.PI * 2);
        c.strokeStyle = 'rgba(12, 8, 5, 0.82)';
        c.lineWidth = 4 * sc;
        c.stroke();

        c.beginPath();
        c.arc(cx, cy, innerR + 1.5 * sc, 0, Math.PI * 2);
        c.strokeStyle = 'rgba(15, 10, 6, 0.72)';
        c.lineWidth = 4 * sc;
        c.stroke();

        c.restore();
    }

    // Offscreen tinted sculpted frame helper (non-destructive color tint preserving lighting)
    let tintBuf = null;
    function drawSculptedImageFrame(c, frame, sz, cfg) {
        if (!frame.imgObj || !frame.loaded) return;
        if (!cfg.customTint) {
            c.drawImage(frame.imgObj, 0, 0, sz, sz);
            return;
        }
        if (!tintBuf || tintBuf.width !== sz) {
            tintBuf = document.createElement('canvas');
            tintBuf.width = sz;
            tintBuf.height = sz;
        }
        const tc = tintBuf.getContext('2d');
        tc.clearRect(0, 0, sz, sz);
        tc.globalCompositeOperation = 'source-over';
        tc.drawImage(frame.imgObj, 0, 0, sz, sz);
        // Apply color-blend tint strictly inside the sculpted frame's alpha silhouette
        tc.globalCompositeOperation = 'source-atop';
        tc.fillStyle = cfg.customTint;
        tc.globalAlpha = 0.42;
        tc.fillRect(0, 0, sz, sz);
        tc.globalAlpha = 1.0;
        tc.globalCompositeOperation = 'source-over';
        c.drawImage(tintBuf, 0, 0, sz, sz);
    }

    function getImageFrameScale(cfg) {
        const t = (cfg && cfg.thickness !== undefined) ? cfg.thickness : 1.0;
        return 1.0 + (t - 1.0) * 0.55;
    }

    function drawNameBanner(c, text, color, sz, frame, cfg) {
        const clean = (text || '').trim();
        if (!clean) return;
        const sc = sz / 1024;
        const cx = sz / 2;

        // Special mode: write calligraphy directly onto the unfurled parchment scroll banner!
        if (frame && frame.isScrollBanner) {
            const fScale = getImageFrameScale(cfg);
            const y = sz / 2 + (0.706 - 0.5) * sz * fScale;
            const maxW = sz * 0.50 * fScale;
            c.save();
            let fontSize = Math.round(44 * sc * fScale);
            c.font = `700 ${fontSize}px Cinzel, Georgia, serif`;
            while (c.measureText(clean).width > maxW && fontSize > 16 * sc) {
                fontSize -= 2;
                c.font = `700 ${fontSize}px Cinzel, Georgia, serif`;
            }
            c.fillStyle = '#2b1a0c';
            c.textAlign = 'center';
            c.textBaseline = 'middle';
            c.fillText(clean.toUpperCase(), cx, y);
            c.restore();
            return;
        }

        const y = sz * 0.875;
        const w = Math.min(sz * 0.68, Math.max(sz * 0.34, clean.length * 29 * sc + 80 * sc));
        const h = 72 * sc;
        const rx = 18 * sc;

        c.save();
        c.shadowColor = 'rgba(0,0,0,0.72)';
        c.shadowBlur = 18 * sc;
        c.shadowOffsetY = 6 * sc;

        const bg = c.createLinearGradient(cx, y - h / 2, cx, y + h / 2);
        bg.addColorStop(0, mixColor(color, 0.18));
        bg.addColorStop(0.5, color);
        bg.addColorStop(1, mixColor(color, -0.35));
        c.beginPath();
        c.roundRect(cx - w / 2, y - h / 2, w, h, rx);
        c.fillStyle = bg;
        c.fill();

        c.shadowColor = 'transparent';
        c.strokeStyle = '#e5c87b';
        c.lineWidth = 4.5 * sc;
        c.stroke();

        c.beginPath();
        c.roundRect(cx - w / 2 + 6 * sc, y - h / 2 + 6 * sc, w - 12 * sc, h - 12 * sc, rx * 0.65);
        c.strokeStyle = 'rgba(255, 240, 195, 0.35)';
        c.lineWidth = 2 * sc;
        c.stroke();

        let fontSize = Math.round(35 * sc);
        c.font = `700 ${fontSize}px Cinzel, Georgia, serif`;
        while (c.measureText(clean).width > w - 40 * sc && fontSize > 16 * sc) {
            fontSize -= 2;
            c.font = `700 ${fontSize}px Cinzel, Georgia, serif`;
        }
        c.fillStyle = '#fdf5e0';
        c.textAlign = 'center';
        c.textBaseline = 'middle';
        c.shadowColor = 'rgba(0,0,0,0.85)';
        c.shadowBlur = 4 * sc;
        c.fillText(clean.toUpperCase(), cx, y + 2 * sc);
        c.restore();
    }

    function renderTokenToCanvas(targetCanvas, customCfg) {
        const c = targetCanvas.getContext('2d');
        const sz = targetCanvas.width;
        const sc = sz / 1024;
        const cfg = customCfg || state;
        const frame = getFrameObj(cfg.frameId);

        let cx = sz / 2;
        let cy = sz / 2;
        let clipR = sz * 0.44;
        let innerVigR = sz * 0.43;
        const fScale = (frame.kind === 'image') ? getImageFrameScale(cfg) : 1.0;

        if (frame.kind === 'image') {
            cx = sz / 2 + ((frame.cx || 0.5) - 0.5) * sz * fScale;
            cy = sz / 2 + ((frame.cy || 0.5) - 0.5) * sz * fScale;
            clipR = (frame.clipR || 0.31) * sz * fScale;
            innerVigR = clipR * 0.96;
        } else {
            const outerR = (frame.id === 'chama_solar' || frame.id === 'chefe_ameaca') ? 470 * sc : 494 * sc;
            const ringW = Math.max(26, Math.min(110, 62 * (cfg.thickness || 1.0))) * sc;
            clipR = outerR - ringW * 0.5;
            innerVigR = outerR - ringW;
        }

        c.clearRect(0, 0, sz, sz);

        // 1. Clip portrait cleanly behind the frame opening
        c.save();
        if (frame.shape === 'hex') {
            traceHexPath(c, cx, cy, clipR, false);
        } else {
            c.beginPath();
            c.arc(cx, cy, clipR, 0, Math.PI * 2);
            c.closePath();
        }
        c.clip();

        // 2. Solid background inside opening (optional)
        if (!cfg.innerBgTransparent) {
            c.fillStyle = cfg.innerBgColor || '#17191f';
            c.fillRect(0, 0, sz, sz);
        }

        // 3. Draw portrait artwork scaled cleanly to opening diameter
        const img = cfg.img || sampleImg;
        const iw = img.naturalWidth || img.width || 768;
        const ih = img.naturalHeight || img.height || 768;
        const fitDiam = clipR * 2.08;
        const coverScale = (fitDiam / Math.min(iw, ih)) * (cfg.zoom || 1.0);

        c.save();
        c.translate(cx + (cfg.offsetX || 0) * sc, cy + (cfg.offsetY || 0) * sc);
        c.rotate(((cfg.rotation || 0) * Math.PI) / 180);
        if (cfg.flipX) c.scale(-1, 1);
        const dw = iw * coverScale;
        const dh = ih * coverScale;
        c.drawImage(img, -dw / 2, -dh / 2, dw, dh);
        c.restore();

        // 4. Inner 3D depth vignette
        const sh = cfg.shadow !== undefined ? cfg.shadow : 0.45;
        if (sh > 0.01) {
            const vig = c.createRadialGradient(cx, cy, innerVigR * 0.58, cx, cy, innerVigR * 1.04);
            vig.addColorStop(0, 'rgba(0,0,0,0)');
            vig.addColorStop(0.74, `rgba(0,0,0,${(sh * 0.34).toFixed(3)})`);
            vig.addColorStop(1, `rgba(0,0,0,${(sh * 0.90).toFixed(3)})`);
            c.fillStyle = vig;
            c.fillRect(0, 0, sz, sz);
        }
        c.restore();

        // 5. Render Frame Overlay (Sculpted HD PNG/WebP OR Procedural)
        if (frame.kind === 'image') {
            c.save();
            c.translate(sz / 2, sz / 2);
            c.scale(fScale, fScale);
            c.translate(-sz / 2, -sz / 2);
            drawSculptedImageFrame(c, frame, sz, cfg);
            c.restore();
        } else {
            drawProceduralFrame(c, frame, sz, cfg);
        }

        // 6. Optional Name Banner (or Parchment Calligraphy)
        if (cfg.bannerText) {
            drawNameBanner(c, cfg.bannerText, cfg.bannerColor || '#5e1715', sz, frame, cfg);
        }
    }

    function renderMain() {
        renderTokenToCanvas(canvas, state);
    }

    const thumbMap = new Map();
    function renderThumbForFrame(fr) {
        const thumb = thumbMap.get(fr.id);
        if (!thumb) return;
        renderTokenToCanvas(thumb, {
            img: sampleImg,
            frameId: fr.id,
            zoom: 1.0,
            offsetX: 0,
            offsetY: 0,
            rotation: 0,
            flipX: false,
            shadow: 0.42,
            thickness: 1.0,
            customTint: fr.defaultTint || null,
            innerBgTransparent: false,
            innerBgColor: '#17191f',
            bannerText: '',
        });
    }

    function buildFrameGallery() {
        const grid = document.getElementById('ts-frames-grid');
        if (!grid) return;
        grid.innerHTML = '';
        thumbMap.clear();

        FRAMES.forEach(fr => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'ts-frame-btn' + (fr.id === state.frameId ? ' active' : '');
            btn.dataset.frame = fr.id;
            btn.dataset.cat = fr.category;
            if (state.category !== 'ALL' && fr.category !== state.category) {
                btn.classList.add('is-hidden');
            }

            const thumb = document.createElement('canvas');
            thumb.width = 164;
            thumb.height = 164;
            thumb.className = 'ts-frame-thumb';
            thumbMap.set(fr.id, thumb);

            const lbl = document.createElement('span');
            lbl.className = 'ts-frame-name';
            lbl.textContent = fr.name;

            btn.appendChild(thumb);
            btn.appendChild(lbl);
            btn.addEventListener('click', () => {
                state.frameId = fr.id;
                grid.querySelectorAll('.ts-frame-btn').forEach(b => b.classList.toggle('active', b === btn));
                syncControls();
                renderMain();
            });
            grid.appendChild(btn);
            renderThumbForFrame(fr);
        });
    }

    // Preload all 12 sculpted WebP Data URIs cleanly
    FRAMES.forEach(fr => {
        if (fr.kind === 'image' && fr.dataUri) {
            const img = new Image();
            img.onload = () => {
                fr.imgObj = img;
                fr.loaded = true;
                renderThumbForFrame(fr);
                if (state.frameId === fr.id) renderMain();
            };
            img.src = fr.dataUri;
        }
    });

    // Category filter tabs
    document.querySelectorAll('.ts-cat-tab[data-cat]').forEach(tab => {
        tab.addEventListener('click', () => {
            state.category = tab.dataset.cat;
            document.querySelectorAll('.ts-cat-tab[data-cat]').forEach(t => t.classList.toggle('active', t === tab));
            document.querySelectorAll('.ts-frame-btn').forEach(btn => {
                const show = (state.category === 'ALL' || btn.dataset.cat === state.category);
                btn.classList.toggle('is-hidden', !show);
            });
        });
    });

    // Custom user PNG frame upload
    const customFrameInput = document.getElementById('ts-custom-frame-input');
    document.getElementById('ts-btn-custom-frame')?.addEventListener('click', () => customFrameInput?.click());
    customFrameInput?.addEventListener('change', (e) => {
        const f = e.target.files?.[0];
        if (!f) return;
        const reader = new FileReader();
        reader.onload = (ev) => {
            const img = new Image();
            img.onload = () => {
                const cid = 'custom_' + Date.now();
                const fr = {
                    id: cid,
                    name: f.name.replace(/\.[^.]+$/, '').slice(0, 18) || 'Moldura Própria',
                    category: 'Esculpida',
                    kind: 'image',
                    shape: 'circle',
                    cx: 0.5,
                    cy: 0.5,
                    clipR: 0.42,
                    imgObj: img,
                    loaded: true,
                };
                FRAMES.unshift(fr);
                state.frameId = cid;
                state.category = 'ALL';
                document.querySelectorAll('.ts-cat-tab[data-cat]').forEach(t => t.classList.toggle('active', t.dataset.cat === 'ALL'));
                buildFrameGallery();
                renderMain();
                setStatus(`Moldura personalizada "${fr.name}" adicionada!`);
            };
            img.src = ev.target.result;
        };
        reader.readAsDataURL(f);
        e.target.value = '';
    });

    const statusEl = document.getElementById('ts-status');
    let toastTimer = null;
    function setStatus(msg) {
        if (!statusEl) return;
        statusEl.textContent = msg;
        if (toastTimer) clearTimeout(toastTimer);
        toastTimer = setTimeout(() => { statusEl.textContent = ''; }, 4200);
    }

    function loadImageFile(file) {
        if (!file || !file.type.startsWith('image/')) {
            setStatus('Selecione um arquivo de imagem válido (PNG, JPG ou WebP).');
            return;
        }
        const reader = new FileReader();
        reader.onload = (ev) => {
            const img = new Image();
            img.onload = () => {
                state.img = img;
                state.zoom = 1.0;
                state.offsetX = 0;
                state.offsetY = 0;
                state.rotation = 0;
                state.flipX = false;
                syncControls();
                renderMain();
                if (file.name) {
                    const base = file.name.replace(/\.[^.]+$/, '').replace(/[^a-zA-Z0-9_-]+/g, '_');
                    const fnInput = document.getElementById('ts-filename');
                    if (fnInput && base) fnInput.value = 'token_' + base;
                }
                setStatus(`Imagem carregada (${img.naturalWidth}×${img.naturalHeight} px).`);
            };
            img.src = ev.target.result;
        };
        reader.readAsDataURL(file);
    }

    function syncControls() {
        const z = document.getElementById('ts-zoom');
        const zv = document.getElementById('ts-zoom-val');
        if (z) z.value = Math.round(state.zoom * 100);
        if (zv) zv.textContent = Math.round(state.zoom * 100) + '%';

        const r = document.getElementById('ts-rotate');
        const rv = document.getElementById('ts-rotate-val');
        if (r) r.value = Math.round(state.rotation);
        if (rv) rv.textContent = Math.round(state.rotation) + '°';

        const s = document.getElementById('ts-shadow');
        const sv = document.getElementById('ts-shadow-val');
        if (s) s.value = Math.round(state.shadow * 100);
        if (sv) sv.textContent = Math.round(state.shadow * 100) + '%';

        const t = document.getElementById('ts-thickness');
        const tv = document.getElementById('ts-thickness-val');
        const tlbl = document.getElementById('ts-thickness-lbl');
        const curFr = getFrameObj(state.frameId);
        if (tlbl) tlbl.textContent = (curFr.kind === 'image') ? 'Escala da Moldura' : 'Espessura da Moldura';
        if (t) t.value = Math.round(state.thickness * 100);
        if (tv) tv.textContent = Math.round(state.thickness * 100) + '%';

        const flipBtn = document.getElementById('ts-btn-flip');
        if (flipBtn) flipBtn.classList.toggle('active', state.flipX);
    }

    function exportPNG(targetSize, copyOnly) {
        const outCanvas = document.createElement('canvas');
        outCanvas.width = targetSize;
        outCanvas.height = targetSize;
        renderTokenToCanvas(outCanvas, state);

        outCanvas.toBlob(async (blob) => {
            if (!blob) {
                setStatus('Erro ao gerar o PNG.');
                return;
            }
            if (copyOnly) {
                try {
                    if (navigator.clipboard && window.ClipboardItem) {
                        await navigator.clipboard.write([new ClipboardItem({ 'image/png': blob })]);
                        setStatus(`Token ${targetSize}×${targetSize} PNG copiado para a área de transferência!`);
                        return;
                    }
                } catch (e) { /* fallback */ }
                setStatus('Seu navegador bloqueou cópia direta — use o botão Baixar PNG.');
                return;
            }
            const fnInput = document.getElementById('ts-filename');
            const rawName = (fnInput ? fnInput.value : 'token_alenia').trim() || 'token_alenia';
            const cleanName = rawName.replace(/\.png$/i, '').replace(/[^a-zA-Z0-9À-ÿ _-]+/g, '_') + `_${targetSize}px.png`;
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = cleanName;
            document.body.appendChild(a);
            a.click();
            a.remove();
            setTimeout(() => URL.revokeObjectURL(url), 1500);
            setStatus(`✔ Token baixado: ${cleanName} (${Math.round(blob.size / 1024)} KB)`);
        }, 'image/png');
    }

    const fileInput = document.getElementById('ts-file-input');
    const wrap = document.getElementById('ts-canvas-wrap');
    document.getElementById('ts-btn-upload')?.addEventListener('click', () => fileInput?.click());
    fileInput?.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) loadImageFile(e.target.files[0]);
        e.target.value = '';
    });

    if (wrap) {
        ['dragenter', 'dragover'].forEach(ev => wrap.addEventListener(ev, (e) => {
            e.preventDefault(); e.stopPropagation(); wrap.classList.add('drag-over');
        }));
        ['dragleave', 'drop'].forEach(ev => wrap.addEventListener(ev, (e) => {
            e.preventDefault(); e.stopPropagation(); wrap.classList.remove('drag-over');
        }));
        wrap.addEventListener('drop', (e) => {
            const f = e.dataTransfer?.files?.[0];
            if (f) loadImageFile(f);
        });

        let dragging = false;
        let lastX = 0, lastY = 0;
        wrap.addEventListener('pointerdown', (e) => {
            dragging = true;
            lastX = e.clientX;
            lastY = e.clientY;
            wrap.setPointerCapture(e.pointerId);
        });
        wrap.addEventListener('pointermove', (e) => {
            if (!dragging) return;
            const rect = wrap.getBoundingClientRect();
            const ratio = SIZE / rect.width;
            state.offsetX += (e.clientX - lastX) * ratio;
            state.offsetY += (e.clientY - lastY) * ratio;
            lastX = e.clientX;
            lastY = e.clientY;
            renderMain();
        });
        const stopDrag = () => { dragging = false; };
        wrap.addEventListener('pointerup', stopDrag);
        wrap.addEventListener('pointercancel', stopDrag);

        wrap.addEventListener('wheel', (e) => {
            e.preventDefault();
            const delta = e.deltaY < 0 ? 0.06 : -0.06;
            state.zoom = Math.max(0.4, Math.min(3.5, state.zoom + delta));
            syncControls();
            renderMain();
        }, { passive: false });
    }

    document.addEventListener('paste', (e) => {
        const items = e.clipboardData?.items || [];
        for (const it of items) {
            if (it.type && it.type.startsWith('image/')) {
                const file = it.getAsFile();
                if (file) { loadImageFile(file); break; }
            }
        }
    });

    document.getElementById('ts-btn-flip')?.addEventListener('click', () => {
        state.flipX = !state.flipX; syncControls(); renderMain();
    });
    document.getElementById('ts-btn-center')?.addEventListener('click', () => {
        state.offsetX = 0; state.offsetY = 0; renderMain();
    });
    document.getElementById('ts-btn-fit')?.addEventListener('click', () => {
        state.zoom = 1.0; state.offsetX = 0; state.offsetY = 0; state.rotation = 0;
        syncControls(); renderMain();
    });

    document.querySelectorAll('.ts-bg-pill').forEach(pill => {
        pill.addEventListener('click', () => {
            document.querySelectorAll('.ts-bg-pill').forEach(p => p.classList.toggle('active', p === pill));
            if (wrap) {
                wrap.classList.remove('bg-checker', 'bg-dark', 'bg-map', 'bg-parchment');
                wrap.classList.add(pill.dataset.bg);
            }
        });
    });

    document.getElementById('ts-zoom')?.addEventListener('input', (e) => {
        state.zoom = parseInt(e.target.value, 10) / 100; syncControls(); renderMain();
    });
    document.getElementById('ts-rotate')?.addEventListener('input', (e) => {
        state.rotation = parseInt(e.target.value, 10); syncControls(); renderMain();
    });
    document.getElementById('ts-shadow')?.addEventListener('input', (e) => {
        state.shadow = parseInt(e.target.value, 10) / 100; syncControls(); renderMain();
    });
    document.getElementById('ts-thickness')?.addEventListener('input', (e) => {
        state.thickness = parseInt(e.target.value, 10) / 100; syncControls(); renderMain();
    });
    document.getElementById('ts-bg-transparent')?.addEventListener('change', (e) => {
        state.innerBgTransparent = e.target.checked; renderMain();
    });
    document.getElementById('ts-inner-bg')?.addEventListener('input', (e) => {
        state.innerBgColor = e.target.value; renderMain();
    });

    const accentLabel = document.getElementById('ts-accent-label');
    const customColorEl = document.getElementById('ts-custom-color');
    function setCustomTint(hex, label) {
        state.customTint = hex;
        document.querySelectorAll('.ts-swatch').forEach(s => s.classList.toggle('active', hex && s.dataset.color.toLowerCase() === hex.toLowerCase()));
        if (accentLabel) accentLabel.textContent = label || (hex ? hex.toUpperCase() : 'Cor Original');
        if (hex && customColorEl) customColorEl.value = hex;
        renderMain();
    }
    document.getElementById('ts-reset-tint')?.addEventListener('click', () => setCustomTint(null, 'Cor Original'));
    document.querySelectorAll('.ts-swatch').forEach(sw => {
        sw.addEventListener('click', () => setCustomTint(sw.dataset.color, sw.title));
    });
    customColorEl?.addEventListener('input', (e) => setCustomTint(e.target.value, e.target.value.toUpperCase()));

    document.getElementById('ts-banner-text')?.addEventListener('input', (e) => {
        state.bannerText = e.target.value;
        const fnEl = document.getElementById('ts-filename');
        if (fnEl && e.target.value.trim()) {
            fnEl.value = 'token_' + e.target.value.trim().toLowerCase().replace(/[^a-z0-9]+/g, '_');
        }
        renderMain();
    });
    document.getElementById('ts-banner-color')?.addEventListener('input', (e) => {
        state.bannerColor = e.target.value; renderMain();
    });

    document.getElementById('ts-export-512')?.addEventListener('click', () => exportPNG(512, false));
    document.getElementById('ts-export-1024')?.addEventListener('click', () => exportPNG(1024, false));
    document.getElementById('ts-btn-copy')?.addEventListener('click', () => exportPNG(512, true));

    buildFrameGallery();
    syncControls();
    if (document.fonts && document.fonts.ready) {
        document.fonts.ready.then(renderMain);
    }
    renderMain();

    window.__AleniaTokenStudio = { state, FRAMES, renderMain };
})();
"""
)
