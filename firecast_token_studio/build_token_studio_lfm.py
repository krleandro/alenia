#!/usr/bin/env python3
"""
Gera o plugin acoplável (TablesDock) AleniaTokenStudioDock.lfm para RRPG Firecast (SDK 3.7b).
- Funciona em qualquer mesa e sistema de RPG
- Abre o Estúdio Web de Tokens (12 molduras, PNG transparente 512x512 / 1024x1024)
- Galeria de Tokens da Mesa paginada (6 slots/página, ilimitada) com upload nativo FireDrive, envio ao chat e cópia de URL
- Comando global /tokens no chat
"""
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
LFM_PATH = os.path.join(OUT_DIR, "AleniaTokenStudioDock.lfm")

STUDIO_URL = "https://alenia-rpg.onrender.com/gerador_tokens.html"

BG_MAIN = "#121419"
BG_CARD = "#1B1E26"
BG_INPUT = "#14171E"
BORDER_GOLD = "#9A7E42"
BORDER_DIM = "#343A4A"
TEXT_MAIN = "#EAE4D6"
TEXT_GOLD = "#D9B96A"
TEXT_MUTED = "#A6AEBF"
TEXT_GREEN = "#7FC48C"


def build_dock_lfm():
    slots_xml = []
    # 6 slots por pagina (2 colunas x 3 linhas) — largura compacta para TablesDock (~420px+)
    for s in range(1, 7):
        col = (s - 1) % 2
        row = (s - 1) // 2
        x = 8 + col * 204
        y = 44 + row * 196
        slots_xml.append(f'''
                    <rectangle left="{x}" top="{y}" width="196" height="188" color="{BG_CARD}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="5" yradius="5">
                        <rectangle left="8" top="8" width="84" height="84" color="{BG_INPUT}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="4" yradius="4">
                            <label name="lblSlotHint{s}" left="4" top="26" width="76" height="32" text="Clique p/ subir PNG" fontColor="{TEXT_MUTED}" fontSize="10" horzTextAlign="center" vertTextAlign="center" wordWrap="true" hitTest="false"/>
                            <image name="imgSlot{s}" align="client" field="tok_url_{s}" editable="true" style="autoFit" center="true" showProgress="true" margins="{{left=2, right=2, top=2, bottom=2}}" cursor="handPoint" hint="Clique para enviar o PNG do token ao FireDrive"/>
                        </rectangle>
                        <label left="98" top="8" width="90" height="16" text="Nome do Token" fontColor="{TEXT_MUTED}" fontSize="10"/>
                        <edit left="98" top="24" width="90" height="26" field="tok_nome_{s}" fontSize="12"/>
                        <label left="98" top="54" width="90" height="16" text="Categoria" fontColor="{TEXT_MUTED}" fontSize="10"/>
                        <comboBox left="98" top="70" width="90" height="24" field="tok_cat_{s}" items="{{'PJ', 'NPC', 'Inimigo', 'Chefe', 'Cenario'}}" values="{{'PJ', 'NPC', 'Inimigo', 'Chefe', 'Cenario'}}" fontSize="11"/>

                        <label left="8" top="100" width="180" height="16" text="URL direta (opcional / copiar):" fontColor="{TEXT_MUTED}" fontSize="10"/>
                        <edit left="8" top="116" width="180" height="24" field="tok_url_{s}" fontSize="10"/>

                        <button left="8" top="148" width="72" height="30" text="Chat" fontSize="11" hint="Enviar este token no chat da mesa">
                            <event name="onClick"><![CDATA[enviarTokenNoChat({s});]]></event>
                        </button>
                        <button left="84" top="148" width="60" height="30" text="URL" fontSize="11" hint="Abrir caixa para copiar ou colar URL">
                            <event name="onClick"><![CDATA[editarUrlSlot({s});]]></event>
                        </button>
                        <button left="148" top="148" width="40" height="30" text="X" fontSize="11" hint="Limpar este slot">
                            <event name="onClick"><![CDATA[limparSlotToken({s});]]></event>
                        </button>
                    </rectangle>''')

    slot_datalinks = []
    for s in range(1, 7):
        slot_datalinks.append(f'''
    <dataLink fields="{{'tok_nome_{s}', 'tok_cat_{s}', 'tok_url_{s}'}}">
        <event name="onChange"><![CDATA[aoEditarSlotToken({s});]]></event>
    </dataLink>''')

    lfm = f'''<?xml version="1.0" encoding="UTF-8"?>
<form name="frmAleniaTokenStudioDock" formType="tablesDock" dataType="br.com.alenia.token_studio.dock" title="Gerador de Tokens" align="client" theme="dark">
    <script><![CDATA[
local STUDIO_URL = "{STUDIO_URL}";
local DialogsMod = require("rrpgDialogs.lua");
local _syncingSlots = false;

local function abrirEstudioWeb()
    local ok = false;
    if GUI ~= nil and type(GUI.openInBrowser) == "function" then
        ok = pcall(function() GUI.openInBrowser(STUDIO_URL); end);
    end;
    if not ok and System ~= nil and type(System.openURL) == "function" then
        ok = pcall(function() System.openURL(STUDIO_URL); end);
    end;
    if not ok then
        if DialogsMod ~= nil and type(DialogsMod.inputQuery) == "function" then
            DialogsMod.inputQuery("Estudio de Tokens", "Copie o link abaixo e abra no navegador:", STUDIO_URL, function() end);
        else
            showMessage("Abra no navegador: " .. STUDIO_URL);
        end;
    end;
end;

local function compartilharLinkEstudio()
    local mesa = Firecast.getMesaDe(sheet);
    local msg = "⚔️ [Estudio Gerador de Tokens] Crie seu token PNG transparente com 12 molduras: " .. STUDIO_URL;
    if mesa ~= nil and mesa.activeChat ~= nil then
        mesa.activeChat:enviarMensagem(msg);
    else
        showMessage(msg);
    end;
end;

local function ensureGaleria()
    if sheet == nil then return nil; end;
    if sheet.tokPagAtual == nil then sheet.tokPagAtual = 1; end;
    if sheet.tokTotalPags == nil then sheet.tokTotalPags = 1; end;
    if sheet.galeria == nil then sheet.galeria = {{}}; end;
    return sheet.galeria;
end;

local function atualizarHints()
    if sheet == nil or self == nil then return; end;
    for s = 1, 6 do
        local lbl = self["lblSlotHint" .. s];
        if lbl ~= nil then
            local u = tostring(sheet["tok_url_" .. s] or "");
            pcall(function() lbl:setVisible(u == ""); end);
        end;
    end;
end;

local function carregarPaginaTokens()
    if sheet == nil then return; end;
    local gal = ensureGaleria();
    local pag = math.floor(tonumber(sheet.tokPagAtual) or 1);
    if pag < 1 then pag = 1; end;
    local maxPag = math.floor(tonumber(sheet.tokTotalPags) or 1);
    if maxPag < 1 then maxPag = 1; end;
    if pag > maxPag then pag = maxPag; end;
    sheet.tokPagAtual = pag;

    _syncingSlots = true;
    for s = 1, 6 do
        local idx = (pag - 1) * 6 + s;
        local k = "k" .. tostring(idx);
        local item = gal[k];
        if item ~= nil then
            sheet["tok_nome_" .. s] = tostring(item.nome or "");
            sheet["tok_cat_" .. s] = tostring(item.cat or "PJ");
            sheet["tok_url_" .. s] = tostring(item.url or "");
        else
            sheet["tok_nome_" .. s] = "";
            sheet["tok_cat_" .. s] = "PJ";
            sheet["tok_url_" .. s] = "";
        end;
    end;
    sheet.tokPagLabel = "Pagina " .. tostring(pag) .. " / " .. tostring(maxPag);
    _syncingSlots = false;
    atualizarHints();
end;

local function aoEditarSlotToken(s)
    if _syncingSlots or sheet == nil then return; end;
    local gal = ensureGaleria();
    local pag = math.floor(tonumber(sheet.tokPagAtual) or 1);
    if pag < 1 then pag = 1; end;
    local idx = (pag - 1) * 6 + s;
    local k = "k" .. tostring(idx);
    if gal[k] == nil then gal[k] = {{}}; end;
    gal[k].nome = tostring(sheet["tok_nome_" .. s] or "");
    gal[k].cat = tostring(sheet["tok_cat_" .. s] or "PJ");
    gal[k].url = tostring(sheet["tok_url_" .. s] or "");
    atualizarHints();
end;

local function mudarPaginaTokens(delta)
    if sheet == nil then return; end;
    ensureGaleria();
    local pag = (math.floor(tonumber(sheet.tokPagAtual) or 1)) + delta;
    local maxPag = math.floor(tonumber(sheet.tokTotalPags) or 1);
    if pag < 1 then pag = 1; end;
    if pag > maxPag then
        maxPag = pag;
        sheet.tokTotalPags = maxPag;
    end;
    sheet.tokPagAtual = pag;
    carregarPaginaTokens();
end;

local function editarUrlSlot(s)
    if sheet == nil then return; end;
    local atual = tostring(sheet["tok_url_" .. s] or "");
    if DialogsMod ~= nil and type(DialogsMod.inputQuery) == "function" then
        DialogsMod.inputQuery(
            "URL do Token (Slot " .. tostring(s) .. ")",
            "Copie a URL abaixo ou cole uma nova URL direta de imagem:",
            atual,
            function(val)
                local limpo = tostring(val or ""):gsub("^%s+", ""):gsub("%s+$", "");
                sheet["tok_url_" .. s] = limpo;
                aoEditarSlotToken(s);
            end,
            nil,
            true
        );
    else
        showMessage("URL: " .. atual);
    end;
end;

local function limparSlotToken(s)
    if sheet == nil then return; end;
    sheet["tok_nome_" .. s] = "";
    sheet["tok_cat_" .. s] = "PJ";
    sheet["tok_url_" .. s] = "";
    aoEditarSlotToken(s);
end;

local function enviarTokenNoChat(s)
    if sheet == nil then return; end;
    local nome = tostring(sheet["tok_nome_" .. s] or "");
    if nome == "" then nome = "Token #" .. tostring(s); end;
    local cat = tostring(sheet["tok_cat_" .. s] or "PJ");
    local url = tostring(sheet["tok_url_" .. s] or "");
    if url == "" then
        showMessage("Este slot ainda nao possui imagem. Clique na moldura do slot para subir um PNG ou cole a URL.");
        return;
    end;
    local mesa = Firecast.getMesaDe(sheet);
    local msg = "🛡️ [" .. cat .. "] " .. nome .. "\\n[§I " .. url .. "]";
    if mesa ~= nil and mesa.activeChat ~= nil then
        mesa.activeChat:enviarMensagem(msg);
    else
        showMessage(msg);
    end;
end;
    ]]></script>

    <rectangle align="client" color="{BG_MAIN}">
        <scrollBox align="client">
            <layout left="0" top="0" width="424" height="790">
                <!-- CABECALHO -->
                <rectangle left="6" top="6" width="412" height="122" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="6" yradius="6">
                    <label left="12" top="8" width="388" height="22" text="ALENIA TOKEN STUDIO v1.1" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold" horzTextAlign="center"/>
                    <label left="12" top="30" width="388" height="32" text="12 molduras HD, zoom/pan/rotacao, faixa de nome e exportacao PNG transparente (512px / 1024px)." fontColor="{TEXT_MUTED}" fontSize="11" horzTextAlign="center" wordWrap="true"/>
                    <button left="12" top="68" width="256" height="40" text="Abrir Estudio de Tokens" fontSize="13">
                        <event name="onClick"><![CDATA[abrirEstudioWeb();]]></event>
                    </button>
                    <button left="274" top="68" width="126" height="40" text="Link no Chat" fontSize="12">
                        <event name="onClick"><![CDATA[compartilharLinkEstudio();]]></event>
                    </button>
                </rectangle>

                <!-- GUIA RAPIDO -->
                <rectangle left="6" top="134" width="412" height="58" color="#171B22" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="5" yradius="5">
                    <label left="10" top="6" width="392" height="46" text="1) Clique em [Abrir Estudio de Tokens] e baixe seu PNG transparente.  2) Clique em qualquer moldura abaixo para subir o PNG ao FireDrive ou arraste direto ao tabuleiro Scene 3." fontColor="{TEXT_GREEN}" fontSize="11" wordWrap="true"/>
                </rectangle>

                <!-- GALERIA DE TOKENS DA MESA -->
                <rectangle left="6" top="198" width="412" height="584" color="#151820" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="6" yradius="6">
                    <label left="10" top="10" width="194" height="24" text="GALERIA DA MESA" fontColor="{TEXT_GOLD}" fontSize="13" fontStyle="bold" vertTextAlign="center"/>
                    <button left="208" top="8" width="34" height="28" text="&lt;" fontSize="12" hint="Pagina anterior">
                        <event name="onClick"><![CDATA[mudarPaginaTokens(-1);]]></event>
                    </button>
                    <label left="244" top="10" width="96" height="24" field="tokPagLabel" fontColor="{TEXT_MAIN}" fontSize="11" horzTextAlign="center" vertTextAlign="center"/>
                    <button left="342" top="8" width="60" height="28" text="Prox &gt;" fontSize="11" hint="Proxima pagina (cria nova pagina se necessario)">
                        <event name="onClick"><![CDATA[mudarPaginaTokens(1);]]></event>
                    </button>
                    {"".join(slots_xml)}
                </rectangle>
            </layout>
        </scrollBox>
    </rectangle>

    <!-- DATALINKS NA RAIZ DO FORM -->
    <dataLink fields="{{'tokPagAtual', 'tokTotalPags', 'tokPagLabel'}}" defaultValues="{{'1', '1', 'Pagina 1 / 1'}}"/>
    <dataLink fields="{{'tokPagAtual'}}">
        <event name="onChange"><![CDATA[carregarPaginaTokens();]]></event>
    </dataLink>
    {"".join(slot_datalinks)}

    <moduleScript><![CDATA[
if not rawget(_G, "__ALENIA_TOKEN_STUDIO_CMD_V1") and Firecast ~= nil and Firecast.Messaging ~= nil and Firecast.Messaging.listen ~= nil then
    rawset(_G, "__ALENIA_TOKEN_STUDIO_CMD_V1", true);

    Firecast.Messaging.listen("ListChatCommands", function(message)
        local resp = (type(message.response) == "table") and message.response or {{}};
        table.insert(resp, {{comando = "tokens", descricao = "Abre o Estudio Gerador de Tokens (12 molduras PNG transparente) e envia o link no chat"}});
        message.response = resp;
    end);

    Firecast.Messaging.listen("HandleChatCommand", function(message)
        local cmd = tostring(message.comando or message.command or ""):lower();
        if cmd ~= "tokens" then return; end;
        local url = "{STUDIO_URL}";
        local param = tostring(message.parametro or message.parameter or ""):lower();
        local chat = message.chat;
        if param == "ajuda" or param == "help" then
            if chat ~= nil then
                chat:enviarMensagem("⚔️ [Alenia Token Studio] Use /tokens para abrir o gerador (12 molduras HD, PNG transparente 512/1024px) ou abra o painel acoplavel [Gerador de Tokens] na barra lateral da mesa.");
            end;
        else
            pcall(function()
                if GUI ~= nil and type(GUI.openInBrowser) == "function" then
                    GUI.openInBrowser(url);
                end;
            end);
            if chat ~= nil then
                chat:enviarMensagem("⚔️ [Alenia Token Studio] Estudio de Tokens aberto: " .. url);
            end;
        end;
        message.response = {{handled = true}};
    end);
end;
    ]]></moduleScript>
</form>
'''
    with open(LFM_PATH, "w", encoding="utf-8") as f:
        f.write(lfm)
    print(f"[OK] AleniaTokenStudioDock.lfm gerado ({len(lfm)} bytes).")


if __name__ == "__main__":
    build_dock_lfm()
