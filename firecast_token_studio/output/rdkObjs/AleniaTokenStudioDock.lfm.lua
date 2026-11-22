require("firecast.lua");
local __o_rrpgObjs = require("rrpgObjs.lua");
require("rrpgGUI.lua");
require("rrpgDialogs.lua");
require("rrpgLFM.lua");
require("ndb.lua");
require("locale.lua");
local __o_Utils = require("utils.lua");

local function constructNew_frmAleniaTokenStudioDock()
    local obj = GUI.fromHandle(_obj_newObject("form"));
    local self = obj;
    local sheet = nil;

    rawset(obj, "_oldSetNodeObjectFunction", obj.setNodeObject);

    function obj:setNodeObject(nodeObject)
        sheet = nodeObject;
        self.sheet = nodeObject;
        self:_oldSetNodeObjectFunction(nodeObject);
    end;

    function obj:setNodeDatabase(nodeObject)
        self:setNodeObject(nodeObject);
    end;

    _gui_assignInitialParentForForm(obj.handle);
    obj:beginUpdate();
    obj:setName("frmAleniaTokenStudioDock");
    obj:setFormType("tablesDock");
    obj:setDataType("br.com.alenia.token_studio.dock");
    obj:setTitle("Gerador de Tokens");
    obj:setAlign("client");
    obj:setTheme("dark");


local STUDIO_URL = "https://alenia-rpg.onrender.com/gerador_tokens.html";
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
    if sheet.galeria == nil then sheet.galeria = {}; end;
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
    if gal[k] == nil then gal[k] = {}; end;
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
    local msg = "🛡️ [" .. cat .. "] " .. nome .. "\n[§I " .. url .. "]";
    if mesa ~= nil and mesa.activeChat ~= nil then
        mesa.activeChat:enviarMensagem(msg);
    else
        showMessage(msg);
    end;
end;
    

    obj.rectangle1 = GUI.fromHandle(_obj_newObject("rectangle"));
    obj.rectangle1:setParent(obj);
    obj.rectangle1:setAlign("client");
    obj.rectangle1:setColor("#121419");
    obj.rectangle1:setName("rectangle1");

    obj.scrollBox1 = GUI.fromHandle(_obj_newObject("scrollBox"));
    obj.scrollBox1:setParent(obj.rectangle1);
    obj.scrollBox1:setAlign("client");
    obj.scrollBox1:setName("scrollBox1");

    obj.layout1 = GUI.fromHandle(_obj_newObject("layout"));
    obj.layout1:setParent(obj.scrollBox1);
    obj.layout1:setLeft(0);
    obj.layout1:setTop(0);
    obj.layout1:setWidth(424);
    obj.layout1:setHeight(790);
    obj.layout1:setName("layout1");

    obj.rectangle2 = GUI.fromHandle(_obj_newObject("rectangle"));
    obj.rectangle2:setParent(obj.layout1);
    obj.rectangle2:setLeft(6);
    obj.rectangle2:setTop(6);
    obj.rectangle2:setWidth(412);
    obj.rectangle2:setHeight(122);
    obj.rectangle2:setColor("#1B1E26");
    obj.rectangle2:setStrokeColor("#9A7E42");
    obj.rectangle2:setStrokeSize(1);
    obj.rectangle2:setXradius(6);
    obj.rectangle2:setYradius(6);
    obj.rectangle2:setName("rectangle2");

    obj.label1 = GUI.fromHandle(_obj_newObject("label"));
    obj.label1:setParent(obj.rectangle2);
    obj.label1:setLeft(12);
    obj.label1:setTop(8);
    obj.label1:setWidth(388);
    obj.label1:setHeight(22);
    obj.label1:setText("ALENIA TOKEN STUDIO v1.0");
    obj.label1:setFontColor("#D9B96A");
    obj.label1:setFontSize(15);
    lfm_setPropAsString(obj.label1, "fontStyle", "bold");
    obj.label1:setHorzTextAlign("center");
    obj.label1:setName("label1");

    obj.label2 = GUI.fromHandle(_obj_newObject("label"));
    obj.label2:setParent(obj.rectangle2);
    obj.label2:setLeft(12);
    obj.label2:setTop(30);
    obj.label2:setWidth(388);
    obj.label2:setHeight(32);
    obj.label2:setText("12 molduras HD, zoom/pan/rotacao, faixa de nome e exportacao PNG transparente (512px / 1024px).");
    obj.label2:setFontColor("#A6AEBF");
    obj.label2:setFontSize(11);
    obj.label2:setHorzTextAlign("center");
    obj.label2:setWordWrap(true);
    obj.label2:setName("label2");

    obj.button1 = GUI.fromHandle(_obj_newObject("button"));
    obj.button1:setParent(obj.rectangle2);
    obj.button1:setLeft(12);
    obj.button1:setTop(68);
    obj.button1:setWidth(256);
    obj.button1:setHeight(40);
    obj.button1:setText("Abrir Estudio de Tokens");
    obj.button1:setFontSize(13);
    obj.button1:setName("button1");

    obj.button2 = GUI.fromHandle(_obj_newObject("button"));
    obj.button2:setParent(obj.rectangle2);
    obj.button2:setLeft(274);
    obj.button2:setTop(68);
    obj.button2:setWidth(126);
    obj.button2:setHeight(40);
    obj.button2:setText("Link no Chat");
    obj.button2:setFontSize(12);
    obj.button2:setName("button2");

    obj.rectangle3 = GUI.fromHandle(_obj_newObject("rectangle"));
    obj.rectangle3:setParent(obj.layout1);
    obj.rectangle3:setLeft(6);
    obj.rectangle3:setTop(134);
    obj.rectangle3:setWidth(412);
    obj.rectangle3:setHeight(58);
    obj.rectangle3:setColor("#171B22");
    obj.rectangle3:setStrokeColor("#343A4A");
    obj.rectangle3:setStrokeSize(1);
    obj.rectangle3:setXradius(5);
    obj.rectangle3:setYradius(5);
    obj.rectangle3:setName("rectangle3");

    obj.label3 = GUI.fromHandle(_obj_newObject("label"));
    obj.label3:setParent(obj.rectangle3);
    obj.label3:setLeft(10);
    obj.label3:setTop(6);
    obj.label3:setWidth(392);
    obj.label3:setHeight(46);
    obj.label3:setText("1) Clique em [Abrir Estudio de Tokens] e baixe seu PNG transparente.  2) Clique em qualquer moldura abaixo para subir o PNG ao FireDrive ou arraste direto ao tabuleiro Scene 3.");
    obj.label3:setFontColor("#7FC48C");
    obj.label3:setFontSize(11);
    obj.label3:setWordWrap(true);
    obj.label3:setName("label3");

    obj.rectangle4 = GUI.fromHandle(_obj_newObject("rectangle"));
    obj.rectangle4:setParent(obj.layout1);
    obj.rectangle4:setLeft(6);
    obj.rectangle4:setTop(198);
    obj.rectangle4:setWidth(412);
    obj.rectangle4:setHeight(584);
    obj.rectangle4:setColor("#151820");
    obj.rectangle4:setStrokeColor("#9A7E42");
    obj.rectangle4:setStrokeSize(1);
    obj.rectangle4:setXradius(6);
    obj.rectangle4:setYradius(6);
    obj.rectangle4:setName("rectangle4");

    obj.label4 = GUI.fromHandle(_obj_newObject("label"));
    obj.label4:setParent(obj.rectangle4);
    obj.label4:setLeft(10);
    obj.label4:setTop(10);
    obj.label4:setWidth(194);
    obj.label4:setHeight(24);
    obj.label4:setText("GALERIA DA MESA");
    obj.label4:setFontColor("#D9B96A");
    obj.label4:setFontSize(13);
    lfm_setPropAsString(obj.label4, "fontStyle", "bold");
    obj.label4:setVertTextAlign("center");
    obj.label4:setName("label4");

    obj.button3 = GUI.fromHandle(_obj_newObject("button"));
    obj.button3:setParent(obj.rectangle4);
    obj.button3:setLeft(208);
    obj.button3:setTop(8);
    obj.button3:setWidth(34);
    obj.button3:setHeight(28);
    obj.button3:setText("<");
    obj.button3:setFontSize(12);
    obj.button3:setHint("Pagina anterior");
    obj.button3:setName("button3");

    obj.label5 = GUI.fromHandle(_obj_newObject("label"));
    obj.label5:setParent(obj.rectangle4);
    obj.label5:setLeft(244);
    obj.label5:setTop(10);
    obj.label5:setWidth(96);
    obj.label5:setHeight(24);
    obj.label5:setField("tokPagLabel");
    obj.label5:setFontColor("#EAE4D6");
    obj.label5:setFontSize(11);
    obj.label5:setHorzTextAlign("center");
    obj.label5:setVertTextAlign("center");
    obj.label5:setName("label5");

    obj.button4 = GUI.fromHandle(_obj_newObject("button"));
    obj.button4:setParent(obj.rectangle4);
    obj.button4:setLeft(342);
    obj.button4:setTop(8);
    obj.button4:setWidth(60);
    obj.button4:setHeight(28);
    obj.button4:setText("Prox >");
    obj.button4:setFontSize(11);
    obj.button4:setHint("Proxima pagina (cria nova pagina se necessario)");
    obj.button4:setName("button4");

    obj.rectangle5 = GUI.fromHandle(_obj_newObject("rectangle"));
    obj.rectangle5:setParent(obj.rectangle4);
    obj.rectangle5:setLeft(8);
    obj.rectangle5:setTop(44);
    obj.rectangle5:setWidth(196);
    obj.rectangle5:setHeight(188);
    obj.rectangle5:setColor("#1B1E26");
    obj.rectangle5:setStrokeColor("#343A4A");
    obj.rectangle5:setStrokeSize(1);
    obj.rectangle5:setXradius(5);
    obj.rectangle5:setYradius(5);
    obj.rectangle5:setName("rectangle5");

    obj.rectangle6 = GUI.fromHandle(_obj_newObject("rectangle"));
    obj.rectangle6:setParent(obj.rectangle5);
    obj.rectangle6:setLeft(8);
    obj.rectangle6:setTop(8);
    obj.rectangle6:setWidth(84);
    obj.rectangle6:setHeight(84);
    obj.rectangle6:setColor("#14171E");
    obj.rectangle6:setStrokeColor("#9A7E42");
    obj.rectangle6:setStrokeSize(1);
    obj.rectangle6:setXradius(4);
    obj.rectangle6:setYradius(4);
    obj.rectangle6:setName("rectangle6");

    obj.lblSlotHint1 = GUI.fromHandle(_obj_newObject("label"));
    obj.lblSlotHint1:setParent(obj.rectangle6);
    obj.lblSlotHint1:setLeft(4);
    obj.lblSlotHint1:setTop(26);
    obj.lblSlotHint1:setWidth(76);
    obj.lblSlotHint1:setHeight(32);
    obj.lblSlotHint1:setText("Clique p/ subir PNG");
    obj.lblSlotHint1:setFontColor("#A6AEBF");
    obj.lblSlotHint1:setFontSize(10);
    obj.lblSlotHint1:setHorzTextAlign("center");
    obj.lblSlotHint1:setVertTextAlign("center");
    obj.lblSlotHint1:setWordWrap(true);
    obj.lblSlotHint1:setHitTest(false);
    obj.lblSlotHint1:setName("lblSlotHint1");

    obj.imgSlot1 = GUI.fromHandle(_obj_newObject("image"));
    obj.imgSlot1:setParent(obj.rectangle6);
    obj.imgSlot1:setAlign("client");
    obj.imgSlot1:setField("tok_url_1");
    obj.imgSlot1:setEditable(true);
    obj.imgSlot1:setStyle("autoFit");
    obj.imgSlot1:setCenter(true);
    obj.imgSlot1:setShowProgress(true);
    obj.imgSlot1:setMargins({left=2, right=2, top=2, bottom=2});
    obj.imgSlot1:setCursor("handPoint");
    obj.imgSlot1:setHint("Clique para enviar o PNG do token ao FireDrive");
    obj.imgSlot1:setName("imgSlot1");

    obj.label6 = GUI.fromHandle(_obj_newObject("label"));
    obj.label6:setParent(obj.rectangle5);
    obj.label6:setLeft(98);
    obj.label6:setTop(8);
    obj.label6:setWidth(90);
    obj.label6:setHeight(16);
    obj.label6:setText("Nome do Token");
    obj.label6:setFontColor("#A6AEBF");
    obj.label6:setFontSize(10);
    obj.label6:setName("label6");

    obj.edit1 = GUI.fromHandle(_obj_newObject("edit"));
    obj.edit1:setParent(obj.rectangle5);
    obj.edit1:setLeft(98);
    obj.edit1:setTop(24);
    obj.edit1:setWidth(90);
    obj.edit1:setHeight(26);
    obj.edit1:setField("tok_nome_1");
    obj.edit1:setFontSize(12);
    obj.edit1:setName("edit1");

    obj.label7 = GUI.fromHandle(_obj_newObject("label"));
    obj.label7:setParent(obj.rectangle5);
    obj.label7:setLeft(98);
    obj.label7:setTop(54);
    obj.label7:setWidth(90);
    obj.label7:setHeight(16);
    obj.label7:setText("Categoria");
    obj.label7:setFontColor("#A6AEBF");
    obj.label7:setFontSize(10);
    obj.label7:setName("label7");

    obj.comboBox1 = GUI.fromHandle(_obj_newObject("comboBox"));
    obj.comboBox1:setParent(obj.rectangle5);
    obj.comboBox1:setLeft(98);
    obj.comboBox1:setTop(70);
    obj.comboBox1:setWidth(90);
    obj.comboBox1:setHeight(24);
    obj.comboBox1:setField("tok_cat_1");
    obj.comboBox1:setItems({'PJ', 'NPC', 'Inimigo', 'Chefe', 'Cenario'});
    obj.comboBox1:setValues({'PJ', 'NPC', 'Inimigo', 'Chefe', 'Cenario'});
    obj.comboBox1:setFontSize(11);
    obj.comboBox1:setName("comboBox1");

    obj.label8 = GUI.fromHandle(_obj_newObject("label"));
    obj.label8:setParent(obj.rectangle5);
    obj.label8:setLeft(8);
    obj.label8:setTop(100);
    obj.label8:setWidth(180);
    obj.label8:setHeight(16);
    obj.label8:setText("URL direta (opcional / copiar):");
    obj.label8:setFontColor("#A6AEBF");
    obj.label8:setFontSize(10);
    obj.label8:setName("label8");

    obj.edit2 = GUI.fromHandle(_obj_newObject("edit"));
    obj.edit2:setParent(obj.rectangle5);
    obj.edit2:setLeft(8);
    obj.edit2:setTop(116);
    obj.edit2:setWidth(180);
    obj.edit2:setHeight(24);
    obj.edit2:setField("tok_url_1");
    obj.edit2:setFontSize(10);
    obj.edit2:setName("edit2");

    obj.button5 = GUI.fromHandle(_obj_newObject("button"));
    obj.button5:setParent(obj.rectangle5);
    obj.button5:setLeft(8);
    obj.button5:setTop(148);
    obj.button5:setWidth(72);
    obj.button5:setHeight(30);
    obj.button5:setText("Chat");
    obj.button5:setFontSize(11);
    obj.button5:setHint("Enviar este token no chat da mesa");
    obj.button5:setName("button5");

    obj.button6 = GUI.fromHandle(_obj_newObject("button"));
    obj.button6:setParent(obj.rectangle5);
    obj.button6:setLeft(84);
    obj.button6:setTop(148);
    obj.button6:setWidth(60);
    obj.button6:setHeight(30);
    obj.button6:setText("URL");
    obj.button6:setFontSize(11);
    obj.button6:setHint("Abrir caixa para copiar ou colar URL");
    obj.button6:setName("button6");

    obj.button7 = GUI.fromHandle(_obj_newObject("button"));
    obj.button7:setParent(obj.rectangle5);
    obj.button7:setLeft(148);
    obj.button7:setTop(148);
    obj.button7:setWidth(40);
    obj.button7:setHeight(30);
    obj.button7:setText("X");
    obj.button7:setFontSize(11);
    obj.button7:setHint("Limpar este slot");
    obj.button7:setName("button7");

    obj.rectangle7 = GUI.fromHandle(_obj_newObject("rectangle"));
    obj.rectangle7:setParent(obj.rectangle4);
    obj.rectangle7:setLeft(212);
    obj.rectangle7:setTop(44);
    obj.rectangle7:setWidth(196);
    obj.rectangle7:setHeight(188);
    obj.rectangle7:setColor("#1B1E26");
    obj.rectangle7:setStrokeColor("#343A4A");
    obj.rectangle7:setStrokeSize(1);
    obj.rectangle7:setXradius(5);
    obj.rectangle7:setYradius(5);
    obj.rectangle7:setName("rectangle7");

    obj.rectangle8 = GUI.fromHandle(_obj_newObject("rectangle"));
    obj.rectangle8:setParent(obj.rectangle7);
    obj.rectangle8:setLeft(8);
    obj.rectangle8:setTop(8);
    obj.rectangle8:setWidth(84);
    obj.rectangle8:setHeight(84);
    obj.rectangle8:setColor("#14171E");
    obj.rectangle8:setStrokeColor("#9A7E42");
    obj.rectangle8:setStrokeSize(1);
    obj.rectangle8:setXradius(4);
    obj.rectangle8:setYradius(4);
    obj.rectangle8:setName("rectangle8");

    obj.lblSlotHint2 = GUI.fromHandle(_obj_newObject("label"));
    obj.lblSlotHint2:setParent(obj.rectangle8);
    obj.lblSlotHint2:setLeft(4);
    obj.lblSlotHint2:setTop(26);
    obj.lblSlotHint2:setWidth(76);
    obj.lblSlotHint2:setHeight(32);
    obj.lblSlotHint2:setText("Clique p/ subir PNG");
    obj.lblSlotHint2:setFontColor("#A6AEBF");
    obj.lblSlotHint2:setFontSize(10);
    obj.lblSlotHint2:setHorzTextAlign("center");
    obj.lblSlotHint2:setVertTextAlign("center");
    obj.lblSlotHint2:setWordWrap(true);
    obj.lblSlotHint2:setHitTest(false);
    obj.lblSlotHint2:setName("lblSlotHint2");

    obj.imgSlot2 = GUI.fromHandle(_obj_newObject("image"));
    obj.imgSlot2:setParent(obj.rectangle8);
    obj.imgSlot2:setAlign("client");
    obj.imgSlot2:setField("tok_url_2");
    obj.imgSlot2:setEditable(true);
    obj.imgSlot2:setStyle("autoFit");
    obj.imgSlot2:setCenter(true);
    obj.imgSlot2:setShowProgress(true);
    obj.imgSlot2:setMargins({left=2, right=2, top=2, bottom=2});
    obj.imgSlot2:setCursor("handPoint");
    obj.imgSlot2:setHint("Clique para enviar o PNG do token ao FireDrive");
    obj.imgSlot2:setName("imgSlot2");

    obj.label9 = GUI.fromHandle(_obj_newObject("label"));
    obj.label9:setParent(obj.rectangle7);
    obj.label9:setLeft(98);
    obj.label9:setTop(8);
    obj.label9:setWidth(90);
    obj.label9:setHeight(16);
    obj.label9:setText("Nome do Token");
    obj.label9:setFontColor("#A6AEBF");
    obj.label9:setFontSize(10);
    obj.label9:setName("label9");

    obj.edit3 = GUI.fromHandle(_obj_newObject("edit"));
    obj.edit3:setParent(obj.rectangle7);
    obj.edit3:setLeft(98);
    obj.edit3:setTop(24);
    obj.edit3:setWidth(90);
    obj.edit3:setHeight(26);
    obj.edit3:setField("tok_nome_2");
    obj.edit3:setFontSize(12);
    obj.edit3:setName("edit3");

    obj.label10 = GUI.fromHandle(_obj_newObject("label"));
    obj.label10:setParent(obj.rectangle7);
    obj.label10:setLeft(98);
    obj.label10:setTop(54);
    obj.label10:setWidth(90);
    obj.label10:setHeight(16);
    obj.label10:setText("Categoria");
    obj.label10:setFontColor("#A6AEBF");
    obj.label10:setFontSize(10);
    obj.label10:setName("label10");

    obj.comboBox2 = GUI.fromHandle(_obj_newObject("comboBox"));
    obj.comboBox2:setParent(obj.rectangle7);
    obj.comboBox2:setLeft(98);
    obj.comboBox2:setTop(70);
    obj.comboBox2:setWidth(90);
    obj.comboBox2:setHeight(24);
    obj.comboBox2:setField("tok_cat_2");
    obj.comboBox2:setItems({'PJ', 'NPC', 'Inimigo', 'Chefe', 'Cenario'});
    obj.comboBox2:setValues({'PJ', 'NPC', 'Inimigo', 'Chefe', 'Cenario'});
    obj.comboBox2:setFontSize(11);
    obj.comboBox2:setName("comboBox2");

    obj.label11 = GUI.fromHandle(_obj_newObject("label"));
    obj.label11:setParent(obj.rectangle7);
    obj.label11:setLeft(8);
    obj.label11:setTop(100);
    obj.label11:setWidth(180);
    obj.label11:setHeight(16);
    obj.label11:setText("URL direta (opcional / copiar):");
    obj.label11:setFontColor("#A6AEBF");
    obj.label11:setFontSize(10);
    obj.label11:setName("label11");

    obj.edit4 = GUI.fromHandle(_obj_newObject("edit"));
    obj.edit4:setParent(obj.rectangle7);
    obj.edit4:setLeft(8);
    obj.edit4:setTop(116);
    obj.edit4:setWidth(180);
    obj.edit4:setHeight(24);
    obj.edit4:setField("tok_url_2");
    obj.edit4:setFontSize(10);
    obj.edit4:setName("edit4");

    obj.button8 = GUI.fromHandle(_obj_newObject("button"));
    obj.button8:setParent(obj.rectangle7);
    obj.button8:setLeft(8);
    obj.button8:setTop(148);
    obj.button8:setWidth(72);
    obj.button8:setHeight(30);
    obj.button8:setText("Chat");
    obj.button8:setFontSize(11);
    obj.button8:setHint("Enviar este token no chat da mesa");
    obj.button8:setName("button8");

    obj.button9 = GUI.fromHandle(_obj_newObject("button"));
    obj.button9:setParent(obj.rectangle7);
    obj.button9:setLeft(84);
    obj.button9:setTop(148);
    obj.button9:setWidth(60);
    obj.button9:setHeight(30);
    obj.button9:setText("URL");
    obj.button9:setFontSize(11);
    obj.button9:setHint("Abrir caixa para copiar ou colar URL");
    obj.button9:setName("button9");

    obj.button10 = GUI.fromHandle(_obj_newObject("button"));
    obj.button10:setParent(obj.rectangle7);
    obj.button10:setLeft(148);
    obj.button10:setTop(148);
    obj.button10:setWidth(40);
    obj.button10:setHeight(30);
    obj.button10:setText("X");
    obj.button10:setFontSize(11);
    obj.button10:setHint("Limpar este slot");
    obj.button10:setName("button10");

    obj.rectangle9 = GUI.fromHandle(_obj_newObject("rectangle"));
    obj.rectangle9:setParent(obj.rectangle4);
    obj.rectangle9:setLeft(8);
    obj.rectangle9:setTop(240);
    obj.rectangle9:setWidth(196);
    obj.rectangle9:setHeight(188);
    obj.rectangle9:setColor("#1B1E26");
    obj.rectangle9:setStrokeColor("#343A4A");
    obj.rectangle9:setStrokeSize(1);
    obj.rectangle9:setXradius(5);
    obj.rectangle9:setYradius(5);
    obj.rectangle9:setName("rectangle9");

    obj.rectangle10 = GUI.fromHandle(_obj_newObject("rectangle"));
    obj.rectangle10:setParent(obj.rectangle9);
    obj.rectangle10:setLeft(8);
    obj.rectangle10:setTop(8);
    obj.rectangle10:setWidth(84);
    obj.rectangle10:setHeight(84);
    obj.rectangle10:setColor("#14171E");
    obj.rectangle10:setStrokeColor("#9A7E42");
    obj.rectangle10:setStrokeSize(1);
    obj.rectangle10:setXradius(4);
    obj.rectangle10:setYradius(4);
    obj.rectangle10:setName("rectangle10");

    obj.lblSlotHint3 = GUI.fromHandle(_obj_newObject("label"));
    obj.lblSlotHint3:setParent(obj.rectangle10);
    obj.lblSlotHint3:setLeft(4);
    obj.lblSlotHint3:setTop(26);
    obj.lblSlotHint3:setWidth(76);
    obj.lblSlotHint3:setHeight(32);
    obj.lblSlotHint3:setText("Clique p/ subir PNG");
    obj.lblSlotHint3:setFontColor("#A6AEBF");
    obj.lblSlotHint3:setFontSize(10);
    obj.lblSlotHint3:setHorzTextAlign("center");
    obj.lblSlotHint3:setVertTextAlign("center");
    obj.lblSlotHint3:setWordWrap(true);
    obj.lblSlotHint3:setHitTest(false);
    obj.lblSlotHint3:setName("lblSlotHint3");

    obj.imgSlot3 = GUI.fromHandle(_obj_newObject("image"));
    obj.imgSlot3:setParent(obj.rectangle10);
    obj.imgSlot3:setAlign("client");
    obj.imgSlot3:setField("tok_url_3");
    obj.imgSlot3:setEditable(true);
    obj.imgSlot3:setStyle("autoFit");
    obj.imgSlot3:setCenter(true);
    obj.imgSlot3:setShowProgress(true);
    obj.imgSlot3:setMargins({left=2, right=2, top=2, bottom=2});
    obj.imgSlot3:setCursor("handPoint");
    obj.imgSlot3:setHint("Clique para enviar o PNG do token ao FireDrive");
    obj.imgSlot3:setName("imgSlot3");

    obj.label12 = GUI.fromHandle(_obj_newObject("label"));
    obj.label12:setParent(obj.rectangle9);
    obj.label12:setLeft(98);
    obj.label12:setTop(8);
    obj.label12:setWidth(90);
    obj.label12:setHeight(16);
    obj.label12:setText("Nome do Token");
    obj.label12:setFontColor("#A6AEBF");
    obj.label12:setFontSize(10);
    obj.label12:setName("label12");

    obj.edit5 = GUI.fromHandle(_obj_newObject("edit"));
    obj.edit5:setParent(obj.rectangle9);
    obj.edit5:setLeft(98);
    obj.edit5:setTop(24);
    obj.edit5:setWidth(90);
    obj.edit5:setHeight(26);
    obj.edit5:setField("tok_nome_3");
    obj.edit5:setFontSize(12);
    obj.edit5:setName("edit5");

    obj.label13 = GUI.fromHandle(_obj_newObject("label"));
    obj.label13:setParent(obj.rectangle9);
    obj.label13:setLeft(98);
    obj.label13:setTop(54);
    obj.label13:setWidth(90);
    obj.label13:setHeight(16);
    obj.label13:setText("Categoria");
    obj.label13:setFontColor("#A6AEBF");
    obj.label13:setFontSize(10);
    obj.label13:setName("label13");

    obj.comboBox3 = GUI.fromHandle(_obj_newObject("comboBox"));
    obj.comboBox3:setParent(obj.rectangle9);
    obj.comboBox3:setLeft(98);
    obj.comboBox3:setTop(70);
    obj.comboBox3:setWidth(90);
    obj.comboBox3:setHeight(24);
    obj.comboBox3:setField("tok_cat_3");
    obj.comboBox3:setItems({'PJ', 'NPC', 'Inimigo', 'Chefe', 'Cenario'});
    obj.comboBox3:setValues({'PJ', 'NPC', 'Inimigo', 'Chefe', 'Cenario'});
    obj.comboBox3:setFontSize(11);
    obj.comboBox3:setName("comboBox3");

    obj.label14 = GUI.fromHandle(_obj_newObject("label"));
    obj.label14:setParent(obj.rectangle9);
    obj.label14:setLeft(8);
    obj.label14:setTop(100);
    obj.label14:setWidth(180);
    obj.label14:setHeight(16);
    obj.label14:setText("URL direta (opcional / copiar):");
    obj.label14:setFontColor("#A6AEBF");
    obj.label14:setFontSize(10);
    obj.label14:setName("label14");

    obj.edit6 = GUI.fromHandle(_obj_newObject("edit"));
    obj.edit6:setParent(obj.rectangle9);
    obj.edit6:setLeft(8);
    obj.edit6:setTop(116);
    obj.edit6:setWidth(180);
    obj.edit6:setHeight(24);
    obj.edit6:setField("tok_url_3");
    obj.edit6:setFontSize(10);
    obj.edit6:setName("edit6");

    obj.button11 = GUI.fromHandle(_obj_newObject("button"));
    obj.button11:setParent(obj.rectangle9);
    obj.button11:setLeft(8);
    obj.button11:setTop(148);
    obj.button11:setWidth(72);
    obj.button11:setHeight(30);
    obj.button11:setText("Chat");
    obj.button11:setFontSize(11);
    obj.button11:setHint("Enviar este token no chat da mesa");
    obj.button11:setName("button11");

    obj.button12 = GUI.fromHandle(_obj_newObject("button"));
    obj.button12:setParent(obj.rectangle9);
    obj.button12:setLeft(84);
    obj.button12:setTop(148);
    obj.button12:setWidth(60);
    obj.button12:setHeight(30);
    obj.button12:setText("URL");
    obj.button12:setFontSize(11);
    obj.button12:setHint("Abrir caixa para copiar ou colar URL");
    obj.button12:setName("button12");

    obj.button13 = GUI.fromHandle(_obj_newObject("button"));
    obj.button13:setParent(obj.rectangle9);
    obj.button13:setLeft(148);
    obj.button13:setTop(148);
    obj.button13:setWidth(40);
    obj.button13:setHeight(30);
    obj.button13:setText("X");
    obj.button13:setFontSize(11);
    obj.button13:setHint("Limpar este slot");
    obj.button13:setName("button13");

    obj.rectangle11 = GUI.fromHandle(_obj_newObject("rectangle"));
    obj.rectangle11:setParent(obj.rectangle4);
    obj.rectangle11:setLeft(212);
    obj.rectangle11:setTop(240);
    obj.rectangle11:setWidth(196);
    obj.rectangle11:setHeight(188);
    obj.rectangle11:setColor("#1B1E26");
    obj.rectangle11:setStrokeColor("#343A4A");
    obj.rectangle11:setStrokeSize(1);
    obj.rectangle11:setXradius(5);
    obj.rectangle11:setYradius(5);
    obj.rectangle11:setName("rectangle11");

    obj.rectangle12 = GUI.fromHandle(_obj_newObject("rectangle"));
    obj.rectangle12:setParent(obj.rectangle11);
    obj.rectangle12:setLeft(8);
    obj.rectangle12:setTop(8);
    obj.rectangle12:setWidth(84);
    obj.rectangle12:setHeight(84);
    obj.rectangle12:setColor("#14171E");
    obj.rectangle12:setStrokeColor("#9A7E42");
    obj.rectangle12:setStrokeSize(1);
    obj.rectangle12:setXradius(4);
    obj.rectangle12:setYradius(4);
    obj.rectangle12:setName("rectangle12");

    obj.lblSlotHint4 = GUI.fromHandle(_obj_newObject("label"));
    obj.lblSlotHint4:setParent(obj.rectangle12);
    obj.lblSlotHint4:setLeft(4);
    obj.lblSlotHint4:setTop(26);
    obj.lblSlotHint4:setWidth(76);
    obj.lblSlotHint4:setHeight(32);
    obj.lblSlotHint4:setText("Clique p/ subir PNG");
    obj.lblSlotHint4:setFontColor("#A6AEBF");
    obj.lblSlotHint4:setFontSize(10);
    obj.lblSlotHint4:setHorzTextAlign("center");
    obj.lblSlotHint4:setVertTextAlign("center");
    obj.lblSlotHint4:setWordWrap(true);
    obj.lblSlotHint4:setHitTest(false);
    obj.lblSlotHint4:setName("lblSlotHint4");

    obj.imgSlot4 = GUI.fromHandle(_obj_newObject("image"));
    obj.imgSlot4:setParent(obj.rectangle12);
    obj.imgSlot4:setAlign("client");
    obj.imgSlot4:setField("tok_url_4");
    obj.imgSlot4:setEditable(true);
    obj.imgSlot4:setStyle("autoFit");
    obj.imgSlot4:setCenter(true);
    obj.imgSlot4:setShowProgress(true);
    obj.imgSlot4:setMargins({left=2, right=2, top=2, bottom=2});
    obj.imgSlot4:setCursor("handPoint");
    obj.imgSlot4:setHint("Clique para enviar o PNG do token ao FireDrive");
    obj.imgSlot4:setName("imgSlot4");

    obj.label15 = GUI.fromHandle(_obj_newObject("label"));
    obj.label15:setParent(obj.rectangle11);
    obj.label15:setLeft(98);
    obj.label15:setTop(8);
    obj.label15:setWidth(90);
    obj.label15:setHeight(16);
    obj.label15:setText("Nome do Token");
    obj.label15:setFontColor("#A6AEBF");
    obj.label15:setFontSize(10);
    obj.label15:setName("label15");

    obj.edit7 = GUI.fromHandle(_obj_newObject("edit"));
    obj.edit7:setParent(obj.rectangle11);
    obj.edit7:setLeft(98);
    obj.edit7:setTop(24);
    obj.edit7:setWidth(90);
    obj.edit7:setHeight(26);
    obj.edit7:setField("tok_nome_4");
    obj.edit7:setFontSize(12);
    obj.edit7:setName("edit7");

    obj.label16 = GUI.fromHandle(_obj_newObject("label"));
    obj.label16:setParent(obj.rectangle11);
    obj.label16:setLeft(98);
    obj.label16:setTop(54);
    obj.label16:setWidth(90);
    obj.label16:setHeight(16);
    obj.label16:setText("Categoria");
    obj.label16:setFontColor("#A6AEBF");
    obj.label16:setFontSize(10);
    obj.label16:setName("label16");

    obj.comboBox4 = GUI.fromHandle(_obj_newObject("comboBox"));
    obj.comboBox4:setParent(obj.rectangle11);
    obj.comboBox4:setLeft(98);
    obj.comboBox4:setTop(70);
    obj.comboBox4:setWidth(90);
    obj.comboBox4:setHeight(24);
    obj.comboBox4:setField("tok_cat_4");
    obj.comboBox4:setItems({'PJ', 'NPC', 'Inimigo', 'Chefe', 'Cenario'});
    obj.comboBox4:setValues({'PJ', 'NPC', 'Inimigo', 'Chefe', 'Cenario'});
    obj.comboBox4:setFontSize(11);
    obj.comboBox4:setName("comboBox4");

    obj.label17 = GUI.fromHandle(_obj_newObject("label"));
    obj.label17:setParent(obj.rectangle11);
    obj.label17:setLeft(8);
    obj.label17:setTop(100);
    obj.label17:setWidth(180);
    obj.label17:setHeight(16);
    obj.label17:setText("URL direta (opcional / copiar):");
    obj.label17:setFontColor("#A6AEBF");
    obj.label17:setFontSize(10);
    obj.label17:setName("label17");

    obj.edit8 = GUI.fromHandle(_obj_newObject("edit"));
    obj.edit8:setParent(obj.rectangle11);
    obj.edit8:setLeft(8);
    obj.edit8:setTop(116);
    obj.edit8:setWidth(180);
    obj.edit8:setHeight(24);
    obj.edit8:setField("tok_url_4");
    obj.edit8:setFontSize(10);
    obj.edit8:setName("edit8");

    obj.button14 = GUI.fromHandle(_obj_newObject("button"));
    obj.button14:setParent(obj.rectangle11);
    obj.button14:setLeft(8);
    obj.button14:setTop(148);
    obj.button14:setWidth(72);
    obj.button14:setHeight(30);
    obj.button14:setText("Chat");
    obj.button14:setFontSize(11);
    obj.button14:setHint("Enviar este token no chat da mesa");
    obj.button14:setName("button14");

    obj.button15 = GUI.fromHandle(_obj_newObject("button"));
    obj.button15:setParent(obj.rectangle11);
    obj.button15:setLeft(84);
    obj.button15:setTop(148);
    obj.button15:setWidth(60);
    obj.button15:setHeight(30);
    obj.button15:setText("URL");
    obj.button15:setFontSize(11);
    obj.button15:setHint("Abrir caixa para copiar ou colar URL");
    obj.button15:setName("button15");

    obj.button16 = GUI.fromHandle(_obj_newObject("button"));
    obj.button16:setParent(obj.rectangle11);
    obj.button16:setLeft(148);
    obj.button16:setTop(148);
    obj.button16:setWidth(40);
    obj.button16:setHeight(30);
    obj.button16:setText("X");
    obj.button16:setFontSize(11);
    obj.button16:setHint("Limpar este slot");
    obj.button16:setName("button16");

    obj.rectangle13 = GUI.fromHandle(_obj_newObject("rectangle"));
    obj.rectangle13:setParent(obj.rectangle4);
    obj.rectangle13:setLeft(8);
    obj.rectangle13:setTop(436);
    obj.rectangle13:setWidth(196);
    obj.rectangle13:setHeight(188);
    obj.rectangle13:setColor("#1B1E26");
    obj.rectangle13:setStrokeColor("#343A4A");
    obj.rectangle13:setStrokeSize(1);
    obj.rectangle13:setXradius(5);
    obj.rectangle13:setYradius(5);
    obj.rectangle13:setName("rectangle13");

    obj.rectangle14 = GUI.fromHandle(_obj_newObject("rectangle"));
    obj.rectangle14:setParent(obj.rectangle13);
    obj.rectangle14:setLeft(8);
    obj.rectangle14:setTop(8);
    obj.rectangle14:setWidth(84);
    obj.rectangle14:setHeight(84);
    obj.rectangle14:setColor("#14171E");
    obj.rectangle14:setStrokeColor("#9A7E42");
    obj.rectangle14:setStrokeSize(1);
    obj.rectangle14:setXradius(4);
    obj.rectangle14:setYradius(4);
    obj.rectangle14:setName("rectangle14");

    obj.lblSlotHint5 = GUI.fromHandle(_obj_newObject("label"));
    obj.lblSlotHint5:setParent(obj.rectangle14);
    obj.lblSlotHint5:setLeft(4);
    obj.lblSlotHint5:setTop(26);
    obj.lblSlotHint5:setWidth(76);
    obj.lblSlotHint5:setHeight(32);
    obj.lblSlotHint5:setText("Clique p/ subir PNG");
    obj.lblSlotHint5:setFontColor("#A6AEBF");
    obj.lblSlotHint5:setFontSize(10);
    obj.lblSlotHint5:setHorzTextAlign("center");
    obj.lblSlotHint5:setVertTextAlign("center");
    obj.lblSlotHint5:setWordWrap(true);
    obj.lblSlotHint5:setHitTest(false);
    obj.lblSlotHint5:setName("lblSlotHint5");

    obj.imgSlot5 = GUI.fromHandle(_obj_newObject("image"));
    obj.imgSlot5:setParent(obj.rectangle14);
    obj.imgSlot5:setAlign("client");
    obj.imgSlot5:setField("tok_url_5");
    obj.imgSlot5:setEditable(true);
    obj.imgSlot5:setStyle("autoFit");
    obj.imgSlot5:setCenter(true);
    obj.imgSlot5:setShowProgress(true);
    obj.imgSlot5:setMargins({left=2, right=2, top=2, bottom=2});
    obj.imgSlot5:setCursor("handPoint");
    obj.imgSlot5:setHint("Clique para enviar o PNG do token ao FireDrive");
    obj.imgSlot5:setName("imgSlot5");

    obj.label18 = GUI.fromHandle(_obj_newObject("label"));
    obj.label18:setParent(obj.rectangle13);
    obj.label18:setLeft(98);
    obj.label18:setTop(8);
    obj.label18:setWidth(90);
    obj.label18:setHeight(16);
    obj.label18:setText("Nome do Token");
    obj.label18:setFontColor("#A6AEBF");
    obj.label18:setFontSize(10);
    obj.label18:setName("label18");

    obj.edit9 = GUI.fromHandle(_obj_newObject("edit"));
    obj.edit9:setParent(obj.rectangle13);
    obj.edit9:setLeft(98);
    obj.edit9:setTop(24);
    obj.edit9:setWidth(90);
    obj.edit9:setHeight(26);
    obj.edit9:setField("tok_nome_5");
    obj.edit9:setFontSize(12);
    obj.edit9:setName("edit9");

    obj.label19 = GUI.fromHandle(_obj_newObject("label"));
    obj.label19:setParent(obj.rectangle13);
    obj.label19:setLeft(98);
    obj.label19:setTop(54);
    obj.label19:setWidth(90);
    obj.label19:setHeight(16);
    obj.label19:setText("Categoria");
    obj.label19:setFontColor("#A6AEBF");
    obj.label19:setFontSize(10);
    obj.label19:setName("label19");

    obj.comboBox5 = GUI.fromHandle(_obj_newObject("comboBox"));
    obj.comboBox5:setParent(obj.rectangle13);
    obj.comboBox5:setLeft(98);
    obj.comboBox5:setTop(70);
    obj.comboBox5:setWidth(90);
    obj.comboBox5:setHeight(24);
    obj.comboBox5:setField("tok_cat_5");
    obj.comboBox5:setItems({'PJ', 'NPC', 'Inimigo', 'Chefe', 'Cenario'});
    obj.comboBox5:setValues({'PJ', 'NPC', 'Inimigo', 'Chefe', 'Cenario'});
    obj.comboBox5:setFontSize(11);
    obj.comboBox5:setName("comboBox5");

    obj.label20 = GUI.fromHandle(_obj_newObject("label"));
    obj.label20:setParent(obj.rectangle13);
    obj.label20:setLeft(8);
    obj.label20:setTop(100);
    obj.label20:setWidth(180);
    obj.label20:setHeight(16);
    obj.label20:setText("URL direta (opcional / copiar):");
    obj.label20:setFontColor("#A6AEBF");
    obj.label20:setFontSize(10);
    obj.label20:setName("label20");

    obj.edit10 = GUI.fromHandle(_obj_newObject("edit"));
    obj.edit10:setParent(obj.rectangle13);
    obj.edit10:setLeft(8);
    obj.edit10:setTop(116);
    obj.edit10:setWidth(180);
    obj.edit10:setHeight(24);
    obj.edit10:setField("tok_url_5");
    obj.edit10:setFontSize(10);
    obj.edit10:setName("edit10");

    obj.button17 = GUI.fromHandle(_obj_newObject("button"));
    obj.button17:setParent(obj.rectangle13);
    obj.button17:setLeft(8);
    obj.button17:setTop(148);
    obj.button17:setWidth(72);
    obj.button17:setHeight(30);
    obj.button17:setText("Chat");
    obj.button17:setFontSize(11);
    obj.button17:setHint("Enviar este token no chat da mesa");
    obj.button17:setName("button17");

    obj.button18 = GUI.fromHandle(_obj_newObject("button"));
    obj.button18:setParent(obj.rectangle13);
    obj.button18:setLeft(84);
    obj.button18:setTop(148);
    obj.button18:setWidth(60);
    obj.button18:setHeight(30);
    obj.button18:setText("URL");
    obj.button18:setFontSize(11);
    obj.button18:setHint("Abrir caixa para copiar ou colar URL");
    obj.button18:setName("button18");

    obj.button19 = GUI.fromHandle(_obj_newObject("button"));
    obj.button19:setParent(obj.rectangle13);
    obj.button19:setLeft(148);
    obj.button19:setTop(148);
    obj.button19:setWidth(40);
    obj.button19:setHeight(30);
    obj.button19:setText("X");
    obj.button19:setFontSize(11);
    obj.button19:setHint("Limpar este slot");
    obj.button19:setName("button19");

    obj.rectangle15 = GUI.fromHandle(_obj_newObject("rectangle"));
    obj.rectangle15:setParent(obj.rectangle4);
    obj.rectangle15:setLeft(212);
    obj.rectangle15:setTop(436);
    obj.rectangle15:setWidth(196);
    obj.rectangle15:setHeight(188);
    obj.rectangle15:setColor("#1B1E26");
    obj.rectangle15:setStrokeColor("#343A4A");
    obj.rectangle15:setStrokeSize(1);
    obj.rectangle15:setXradius(5);
    obj.rectangle15:setYradius(5);
    obj.rectangle15:setName("rectangle15");

    obj.rectangle16 = GUI.fromHandle(_obj_newObject("rectangle"));
    obj.rectangle16:setParent(obj.rectangle15);
    obj.rectangle16:setLeft(8);
    obj.rectangle16:setTop(8);
    obj.rectangle16:setWidth(84);
    obj.rectangle16:setHeight(84);
    obj.rectangle16:setColor("#14171E");
    obj.rectangle16:setStrokeColor("#9A7E42");
    obj.rectangle16:setStrokeSize(1);
    obj.rectangle16:setXradius(4);
    obj.rectangle16:setYradius(4);
    obj.rectangle16:setName("rectangle16");

    obj.lblSlotHint6 = GUI.fromHandle(_obj_newObject("label"));
    obj.lblSlotHint6:setParent(obj.rectangle16);
    obj.lblSlotHint6:setLeft(4);
    obj.lblSlotHint6:setTop(26);
    obj.lblSlotHint6:setWidth(76);
    obj.lblSlotHint6:setHeight(32);
    obj.lblSlotHint6:setText("Clique p/ subir PNG");
    obj.lblSlotHint6:setFontColor("#A6AEBF");
    obj.lblSlotHint6:setFontSize(10);
    obj.lblSlotHint6:setHorzTextAlign("center");
    obj.lblSlotHint6:setVertTextAlign("center");
    obj.lblSlotHint6:setWordWrap(true);
    obj.lblSlotHint6:setHitTest(false);
    obj.lblSlotHint6:setName("lblSlotHint6");

    obj.imgSlot6 = GUI.fromHandle(_obj_newObject("image"));
    obj.imgSlot6:setParent(obj.rectangle16);
    obj.imgSlot6:setAlign("client");
    obj.imgSlot6:setField("tok_url_6");
    obj.imgSlot6:setEditable(true);
    obj.imgSlot6:setStyle("autoFit");
    obj.imgSlot6:setCenter(true);
    obj.imgSlot6:setShowProgress(true);
    obj.imgSlot6:setMargins({left=2, right=2, top=2, bottom=2});
    obj.imgSlot6:setCursor("handPoint");
    obj.imgSlot6:setHint("Clique para enviar o PNG do token ao FireDrive");
    obj.imgSlot6:setName("imgSlot6");

    obj.label21 = GUI.fromHandle(_obj_newObject("label"));
    obj.label21:setParent(obj.rectangle15);
    obj.label21:setLeft(98);
    obj.label21:setTop(8);
    obj.label21:setWidth(90);
    obj.label21:setHeight(16);
    obj.label21:setText("Nome do Token");
    obj.label21:setFontColor("#A6AEBF");
    obj.label21:setFontSize(10);
    obj.label21:setName("label21");

    obj.edit11 = GUI.fromHandle(_obj_newObject("edit"));
    obj.edit11:setParent(obj.rectangle15);
    obj.edit11:setLeft(98);
    obj.edit11:setTop(24);
    obj.edit11:setWidth(90);
    obj.edit11:setHeight(26);
    obj.edit11:setField("tok_nome_6");
    obj.edit11:setFontSize(12);
    obj.edit11:setName("edit11");

    obj.label22 = GUI.fromHandle(_obj_newObject("label"));
    obj.label22:setParent(obj.rectangle15);
    obj.label22:setLeft(98);
    obj.label22:setTop(54);
    obj.label22:setWidth(90);
    obj.label22:setHeight(16);
    obj.label22:setText("Categoria");
    obj.label22:setFontColor("#A6AEBF");
    obj.label22:setFontSize(10);
    obj.label22:setName("label22");

    obj.comboBox6 = GUI.fromHandle(_obj_newObject("comboBox"));
    obj.comboBox6:setParent(obj.rectangle15);
    obj.comboBox6:setLeft(98);
    obj.comboBox6:setTop(70);
    obj.comboBox6:setWidth(90);
    obj.comboBox6:setHeight(24);
    obj.comboBox6:setField("tok_cat_6");
    obj.comboBox6:setItems({'PJ', 'NPC', 'Inimigo', 'Chefe', 'Cenario'});
    obj.comboBox6:setValues({'PJ', 'NPC', 'Inimigo', 'Chefe', 'Cenario'});
    obj.comboBox6:setFontSize(11);
    obj.comboBox6:setName("comboBox6");

    obj.label23 = GUI.fromHandle(_obj_newObject("label"));
    obj.label23:setParent(obj.rectangle15);
    obj.label23:setLeft(8);
    obj.label23:setTop(100);
    obj.label23:setWidth(180);
    obj.label23:setHeight(16);
    obj.label23:setText("URL direta (opcional / copiar):");
    obj.label23:setFontColor("#A6AEBF");
    obj.label23:setFontSize(10);
    obj.label23:setName("label23");

    obj.edit12 = GUI.fromHandle(_obj_newObject("edit"));
    obj.edit12:setParent(obj.rectangle15);
    obj.edit12:setLeft(8);
    obj.edit12:setTop(116);
    obj.edit12:setWidth(180);
    obj.edit12:setHeight(24);
    obj.edit12:setField("tok_url_6");
    obj.edit12:setFontSize(10);
    obj.edit12:setName("edit12");

    obj.button20 = GUI.fromHandle(_obj_newObject("button"));
    obj.button20:setParent(obj.rectangle15);
    obj.button20:setLeft(8);
    obj.button20:setTop(148);
    obj.button20:setWidth(72);
    obj.button20:setHeight(30);
    obj.button20:setText("Chat");
    obj.button20:setFontSize(11);
    obj.button20:setHint("Enviar este token no chat da mesa");
    obj.button20:setName("button20");

    obj.button21 = GUI.fromHandle(_obj_newObject("button"));
    obj.button21:setParent(obj.rectangle15);
    obj.button21:setLeft(84);
    obj.button21:setTop(148);
    obj.button21:setWidth(60);
    obj.button21:setHeight(30);
    obj.button21:setText("URL");
    obj.button21:setFontSize(11);
    obj.button21:setHint("Abrir caixa para copiar ou colar URL");
    obj.button21:setName("button21");

    obj.button22 = GUI.fromHandle(_obj_newObject("button"));
    obj.button22:setParent(obj.rectangle15);
    obj.button22:setLeft(148);
    obj.button22:setTop(148);
    obj.button22:setWidth(40);
    obj.button22:setHeight(30);
    obj.button22:setText("X");
    obj.button22:setFontSize(11);
    obj.button22:setHint("Limpar este slot");
    obj.button22:setName("button22");

    obj.dataLink1 = GUI.fromHandle(_obj_newObject("dataLink"));
    obj.dataLink1:setParent(obj);
    obj.dataLink1:setFields({'tokPagAtual', 'tokTotalPags', 'tokPagLabel'});
    obj.dataLink1:setDefaultValues({'1', '1', 'Pagina 1 / 1'});
    obj.dataLink1:setName("dataLink1");

    obj.dataLink2 = GUI.fromHandle(_obj_newObject("dataLink"));
    obj.dataLink2:setParent(obj);
    obj.dataLink2:setFields({'tokPagAtual'});
    obj.dataLink2:setName("dataLink2");

    obj.dataLink3 = GUI.fromHandle(_obj_newObject("dataLink"));
    obj.dataLink3:setParent(obj);
    obj.dataLink3:setFields({'tok_nome_1', 'tok_cat_1', 'tok_url_1'});
    obj.dataLink3:setName("dataLink3");

    obj.dataLink4 = GUI.fromHandle(_obj_newObject("dataLink"));
    obj.dataLink4:setParent(obj);
    obj.dataLink4:setFields({'tok_nome_2', 'tok_cat_2', 'tok_url_2'});
    obj.dataLink4:setName("dataLink4");

    obj.dataLink5 = GUI.fromHandle(_obj_newObject("dataLink"));
    obj.dataLink5:setParent(obj);
    obj.dataLink5:setFields({'tok_nome_3', 'tok_cat_3', 'tok_url_3'});
    obj.dataLink5:setName("dataLink5");

    obj.dataLink6 = GUI.fromHandle(_obj_newObject("dataLink"));
    obj.dataLink6:setParent(obj);
    obj.dataLink6:setFields({'tok_nome_4', 'tok_cat_4', 'tok_url_4'});
    obj.dataLink6:setName("dataLink6");

    obj.dataLink7 = GUI.fromHandle(_obj_newObject("dataLink"));
    obj.dataLink7:setParent(obj);
    obj.dataLink7:setFields({'tok_nome_5', 'tok_cat_5', 'tok_url_5'});
    obj.dataLink7:setName("dataLink7");

    obj.dataLink8 = GUI.fromHandle(_obj_newObject("dataLink"));
    obj.dataLink8:setParent(obj);
    obj.dataLink8:setFields({'tok_nome_6', 'tok_cat_6', 'tok_url_6'});
    obj.dataLink8:setName("dataLink8");

    obj._e_event0 = obj.button1:addEventListener("onClick",
        function (_)
            abrirEstudioWeb();
        end, obj);

    obj._e_event1 = obj.button2:addEventListener("onClick",
        function (_)
            compartilharLinkEstudio();
        end, obj);

    obj._e_event2 = obj.button3:addEventListener("onClick",
        function (_)
            mudarPaginaTokens(-1);
        end, obj);

    obj._e_event3 = obj.button4:addEventListener("onClick",
        function (_)
            mudarPaginaTokens(1);
        end, obj);

    obj._e_event4 = obj.button5:addEventListener("onClick",
        function (_)
            enviarTokenNoChat(1);
        end, obj);

    obj._e_event5 = obj.button6:addEventListener("onClick",
        function (_)
            editarUrlSlot(1);
        end, obj);

    obj._e_event6 = obj.button7:addEventListener("onClick",
        function (_)
            limparSlotToken(1);
        end, obj);

    obj._e_event7 = obj.button8:addEventListener("onClick",
        function (_)
            enviarTokenNoChat(2);
        end, obj);

    obj._e_event8 = obj.button9:addEventListener("onClick",
        function (_)
            editarUrlSlot(2);
        end, obj);

    obj._e_event9 = obj.button10:addEventListener("onClick",
        function (_)
            limparSlotToken(2);
        end, obj);

    obj._e_event10 = obj.button11:addEventListener("onClick",
        function (_)
            enviarTokenNoChat(3);
        end, obj);

    obj._e_event11 = obj.button12:addEventListener("onClick",
        function (_)
            editarUrlSlot(3);
        end, obj);

    obj._e_event12 = obj.button13:addEventListener("onClick",
        function (_)
            limparSlotToken(3);
        end, obj);

    obj._e_event13 = obj.button14:addEventListener("onClick",
        function (_)
            enviarTokenNoChat(4);
        end, obj);

    obj._e_event14 = obj.button15:addEventListener("onClick",
        function (_)
            editarUrlSlot(4);
        end, obj);

    obj._e_event15 = obj.button16:addEventListener("onClick",
        function (_)
            limparSlotToken(4);
        end, obj);

    obj._e_event16 = obj.button17:addEventListener("onClick",
        function (_)
            enviarTokenNoChat(5);
        end, obj);

    obj._e_event17 = obj.button18:addEventListener("onClick",
        function (_)
            editarUrlSlot(5);
        end, obj);

    obj._e_event18 = obj.button19:addEventListener("onClick",
        function (_)
            limparSlotToken(5);
        end, obj);

    obj._e_event19 = obj.button20:addEventListener("onClick",
        function (_)
            enviarTokenNoChat(6);
        end, obj);

    obj._e_event20 = obj.button21:addEventListener("onClick",
        function (_)
            editarUrlSlot(6);
        end, obj);

    obj._e_event21 = obj.button22:addEventListener("onClick",
        function (_)
            limparSlotToken(6);
        end, obj);

    obj._e_event22 = obj.dataLink2:addEventListener("onChange",
        function (_)
            carregarPaginaTokens();
        end, obj);

    obj._e_event23 = obj.dataLink3:addEventListener("onChange",
        function (_)
            aoEditarSlotToken(1);
        end, obj);

    obj._e_event24 = obj.dataLink4:addEventListener("onChange",
        function (_)
            aoEditarSlotToken(2);
        end, obj);

    obj._e_event25 = obj.dataLink5:addEventListener("onChange",
        function (_)
            aoEditarSlotToken(3);
        end, obj);

    obj._e_event26 = obj.dataLink6:addEventListener("onChange",
        function (_)
            aoEditarSlotToken(4);
        end, obj);

    obj._e_event27 = obj.dataLink7:addEventListener("onChange",
        function (_)
            aoEditarSlotToken(5);
        end, obj);

    obj._e_event28 = obj.dataLink8:addEventListener("onChange",
        function (_)
            aoEditarSlotToken(6);
        end, obj);

    function obj:_releaseEvents()
        __o_rrpgObjs.removeEventListenerById(self._e_event28);
        __o_rrpgObjs.removeEventListenerById(self._e_event27);
        __o_rrpgObjs.removeEventListenerById(self._e_event26);
        __o_rrpgObjs.removeEventListenerById(self._e_event25);
        __o_rrpgObjs.removeEventListenerById(self._e_event24);
        __o_rrpgObjs.removeEventListenerById(self._e_event23);
        __o_rrpgObjs.removeEventListenerById(self._e_event22);
        __o_rrpgObjs.removeEventListenerById(self._e_event21);
        __o_rrpgObjs.removeEventListenerById(self._e_event20);
        __o_rrpgObjs.removeEventListenerById(self._e_event19);
        __o_rrpgObjs.removeEventListenerById(self._e_event18);
        __o_rrpgObjs.removeEventListenerById(self._e_event17);
        __o_rrpgObjs.removeEventListenerById(self._e_event16);
        __o_rrpgObjs.removeEventListenerById(self._e_event15);
        __o_rrpgObjs.removeEventListenerById(self._e_event14);
        __o_rrpgObjs.removeEventListenerById(self._e_event13);
        __o_rrpgObjs.removeEventListenerById(self._e_event12);
        __o_rrpgObjs.removeEventListenerById(self._e_event11);
        __o_rrpgObjs.removeEventListenerById(self._e_event10);
        __o_rrpgObjs.removeEventListenerById(self._e_event9);
        __o_rrpgObjs.removeEventListenerById(self._e_event8);
        __o_rrpgObjs.removeEventListenerById(self._e_event7);
        __o_rrpgObjs.removeEventListenerById(self._e_event6);
        __o_rrpgObjs.removeEventListenerById(self._e_event5);
        __o_rrpgObjs.removeEventListenerById(self._e_event4);
        __o_rrpgObjs.removeEventListenerById(self._e_event3);
        __o_rrpgObjs.removeEventListenerById(self._e_event2);
        __o_rrpgObjs.removeEventListenerById(self._e_event1);
        __o_rrpgObjs.removeEventListenerById(self._e_event0);
    end;

    obj._oldLFMDestroy = obj.destroy;

    function obj:destroy()
        self:_releaseEvents();

        if (self.handle ~= 0) and (self.setNodeDatabase ~= nil) then
            self:setNodeDatabase(nil);
        end;

        if self.dataLink8 ~= nil then self.dataLink8:destroy(); self.dataLink8 = nil; end;
        if self.dataLink7 ~= nil then self.dataLink7:destroy(); self.dataLink7 = nil; end;
        if self.dataLink6 ~= nil then self.dataLink6:destroy(); self.dataLink6 = nil; end;
        if self.dataLink5 ~= nil then self.dataLink5:destroy(); self.dataLink5 = nil; end;
        if self.dataLink4 ~= nil then self.dataLink4:destroy(); self.dataLink4 = nil; end;
        if self.dataLink3 ~= nil then self.dataLink3:destroy(); self.dataLink3 = nil; end;
        if self.dataLink2 ~= nil then self.dataLink2:destroy(); self.dataLink2 = nil; end;
        if self.dataLink1 ~= nil then self.dataLink1:destroy(); self.dataLink1 = nil; end;
        if self.button22 ~= nil then self.button22:destroy(); self.button22 = nil; end;
        if self.button21 ~= nil then self.button21:destroy(); self.button21 = nil; end;
        if self.button20 ~= nil then self.button20:destroy(); self.button20 = nil; end;
        if self.edit12 ~= nil then self.edit12:destroy(); self.edit12 = nil; end;
        if self.label23 ~= nil then self.label23:destroy(); self.label23 = nil; end;
        if self.comboBox6 ~= nil then self.comboBox6:destroy(); self.comboBox6 = nil; end;
        if self.label22 ~= nil then self.label22:destroy(); self.label22 = nil; end;
        if self.edit11 ~= nil then self.edit11:destroy(); self.edit11 = nil; end;
        if self.label21 ~= nil then self.label21:destroy(); self.label21 = nil; end;
        if self.imgSlot6 ~= nil then self.imgSlot6:destroy(); self.imgSlot6 = nil; end;
        if self.lblSlotHint6 ~= nil then self.lblSlotHint6:destroy(); self.lblSlotHint6 = nil; end;
        if self.rectangle16 ~= nil then self.rectangle16:destroy(); self.rectangle16 = nil; end;
        if self.rectangle15 ~= nil then self.rectangle15:destroy(); self.rectangle15 = nil; end;
        if self.button19 ~= nil then self.button19:destroy(); self.button19 = nil; end;
        if self.button18 ~= nil then self.button18:destroy(); self.button18 = nil; end;
        if self.button17 ~= nil then self.button17:destroy(); self.button17 = nil; end;
        if self.edit10 ~= nil then self.edit10:destroy(); self.edit10 = nil; end;
        if self.label20 ~= nil then self.label20:destroy(); self.label20 = nil; end;
        if self.comboBox5 ~= nil then self.comboBox5:destroy(); self.comboBox5 = nil; end;
        if self.label19 ~= nil then self.label19:destroy(); self.label19 = nil; end;
        if self.edit9 ~= nil then self.edit9:destroy(); self.edit9 = nil; end;
        if self.label18 ~= nil then self.label18:destroy(); self.label18 = nil; end;
        if self.imgSlot5 ~= nil then self.imgSlot5:destroy(); self.imgSlot5 = nil; end;
        if self.lblSlotHint5 ~= nil then self.lblSlotHint5:destroy(); self.lblSlotHint5 = nil; end;
        if self.rectangle14 ~= nil then self.rectangle14:destroy(); self.rectangle14 = nil; end;
        if self.rectangle13 ~= nil then self.rectangle13:destroy(); self.rectangle13 = nil; end;
        if self.button16 ~= nil then self.button16:destroy(); self.button16 = nil; end;
        if self.button15 ~= nil then self.button15:destroy(); self.button15 = nil; end;
        if self.button14 ~= nil then self.button14:destroy(); self.button14 = nil; end;
        if self.edit8 ~= nil then self.edit8:destroy(); self.edit8 = nil; end;
        if self.label17 ~= nil then self.label17:destroy(); self.label17 = nil; end;
        if self.comboBox4 ~= nil then self.comboBox4:destroy(); self.comboBox4 = nil; end;
        if self.label16 ~= nil then self.label16:destroy(); self.label16 = nil; end;
        if self.edit7 ~= nil then self.edit7:destroy(); self.edit7 = nil; end;
        if self.label15 ~= nil then self.label15:destroy(); self.label15 = nil; end;
        if self.imgSlot4 ~= nil then self.imgSlot4:destroy(); self.imgSlot4 = nil; end;
        if self.lblSlotHint4 ~= nil then self.lblSlotHint4:destroy(); self.lblSlotHint4 = nil; end;
        if self.rectangle12 ~= nil then self.rectangle12:destroy(); self.rectangle12 = nil; end;
        if self.rectangle11 ~= nil then self.rectangle11:destroy(); self.rectangle11 = nil; end;
        if self.button13 ~= nil then self.button13:destroy(); self.button13 = nil; end;
        if self.button12 ~= nil then self.button12:destroy(); self.button12 = nil; end;
        if self.button11 ~= nil then self.button11:destroy(); self.button11 = nil; end;
        if self.edit6 ~= nil then self.edit6:destroy(); self.edit6 = nil; end;
        if self.label14 ~= nil then self.label14:destroy(); self.label14 = nil; end;
        if self.comboBox3 ~= nil then self.comboBox3:destroy(); self.comboBox3 = nil; end;
        if self.label13 ~= nil then self.label13:destroy(); self.label13 = nil; end;
        if self.edit5 ~= nil then self.edit5:destroy(); self.edit5 = nil; end;
        if self.label12 ~= nil then self.label12:destroy(); self.label12 = nil; end;
        if self.imgSlot3 ~= nil then self.imgSlot3:destroy(); self.imgSlot3 = nil; end;
        if self.lblSlotHint3 ~= nil then self.lblSlotHint3:destroy(); self.lblSlotHint3 = nil; end;
        if self.rectangle10 ~= nil then self.rectangle10:destroy(); self.rectangle10 = nil; end;
        if self.rectangle9 ~= nil then self.rectangle9:destroy(); self.rectangle9 = nil; end;
        if self.button10 ~= nil then self.button10:destroy(); self.button10 = nil; end;
        if self.button9 ~= nil then self.button9:destroy(); self.button9 = nil; end;
        if self.button8 ~= nil then self.button8:destroy(); self.button8 = nil; end;
        if self.edit4 ~= nil then self.edit4:destroy(); self.edit4 = nil; end;
        if self.label11 ~= nil then self.label11:destroy(); self.label11 = nil; end;
        if self.comboBox2 ~= nil then self.comboBox2:destroy(); self.comboBox2 = nil; end;
        if self.label10 ~= nil then self.label10:destroy(); self.label10 = nil; end;
        if self.edit3 ~= nil then self.edit3:destroy(); self.edit3 = nil; end;
        if self.label9 ~= nil then self.label9:destroy(); self.label9 = nil; end;
        if self.imgSlot2 ~= nil then self.imgSlot2:destroy(); self.imgSlot2 = nil; end;
        if self.lblSlotHint2 ~= nil then self.lblSlotHint2:destroy(); self.lblSlotHint2 = nil; end;
        if self.rectangle8 ~= nil then self.rectangle8:destroy(); self.rectangle8 = nil; end;
        if self.rectangle7 ~= nil then self.rectangle7:destroy(); self.rectangle7 = nil; end;
        if self.button7 ~= nil then self.button7:destroy(); self.button7 = nil; end;
        if self.button6 ~= nil then self.button6:destroy(); self.button6 = nil; end;
        if self.button5 ~= nil then self.button5:destroy(); self.button5 = nil; end;
        if self.edit2 ~= nil then self.edit2:destroy(); self.edit2 = nil; end;
        if self.label8 ~= nil then self.label8:destroy(); self.label8 = nil; end;
        if self.comboBox1 ~= nil then self.comboBox1:destroy(); self.comboBox1 = nil; end;
        if self.label7 ~= nil then self.label7:destroy(); self.label7 = nil; end;
        if self.edit1 ~= nil then self.edit1:destroy(); self.edit1 = nil; end;
        if self.label6 ~= nil then self.label6:destroy(); self.label6 = nil; end;
        if self.imgSlot1 ~= nil then self.imgSlot1:destroy(); self.imgSlot1 = nil; end;
        if self.lblSlotHint1 ~= nil then self.lblSlotHint1:destroy(); self.lblSlotHint1 = nil; end;
        if self.rectangle6 ~= nil then self.rectangle6:destroy(); self.rectangle6 = nil; end;
        if self.rectangle5 ~= nil then self.rectangle5:destroy(); self.rectangle5 = nil; end;
        if self.button4 ~= nil then self.button4:destroy(); self.button4 = nil; end;
        if self.label5 ~= nil then self.label5:destroy(); self.label5 = nil; end;
        if self.button3 ~= nil then self.button3:destroy(); self.button3 = nil; end;
        if self.label4 ~= nil then self.label4:destroy(); self.label4 = nil; end;
        if self.rectangle4 ~= nil then self.rectangle4:destroy(); self.rectangle4 = nil; end;
        if self.label3 ~= nil then self.label3:destroy(); self.label3 = nil; end;
        if self.rectangle3 ~= nil then self.rectangle3:destroy(); self.rectangle3 = nil; end;
        if self.button2 ~= nil then self.button2:destroy(); self.button2 = nil; end;
        if self.button1 ~= nil then self.button1:destroy(); self.button1 = nil; end;
        if self.label2 ~= nil then self.label2:destroy(); self.label2 = nil; end;
        if self.label1 ~= nil then self.label1:destroy(); self.label1 = nil; end;
        if self.rectangle2 ~= nil then self.rectangle2:destroy(); self.rectangle2 = nil; end;
        if self.layout1 ~= nil then self.layout1:destroy(); self.layout1 = nil; end;
        if self.scrollBox1 ~= nil then self.scrollBox1:destroy(); self.scrollBox1 = nil; end;
        if self.rectangle1 ~= nil then self.rectangle1:destroy(); self.rectangle1 = nil; end;
        self:_oldLFMDestroy();
    end;

    obj:endUpdate();

    return obj;
end;

function newfrmAleniaTokenStudioDock()
    local retObj = nil;
    __o_rrpgObjs.beginObjectsLoading();

    __o_Utils.tryFinally(
      function()
        retObj = constructNew_frmAleniaTokenStudioDock();
      end,
      function()
        __o_rrpgObjs.endObjectsLoading();
      end);

    assert(retObj ~= nil);
    return retObj;
end;

local _frmAleniaTokenStudioDock = {
    newEditor = newfrmAleniaTokenStudioDock,
    new = newfrmAleniaTokenStudioDock,
    name = "frmAleniaTokenStudioDock",
    dataType = "br.com.alenia.token_studio.dock",
    formType = "tablesDock",
    formComponentName = "form",
    cacheMode = "none",
    title = "Gerador de Tokens",
    description = "Gerador de Tokens"};

frmAleniaTokenStudioDock = _frmAleniaTokenStudioDock;
Firecast.registrarForm(_frmAleniaTokenStudioDock);
Firecast.registrarDataType(_frmAleniaTokenStudioDock);
Firecast.registrarSpecialForm(_frmAleniaTokenStudioDock);


if not rawget(_G, "__ALENIA_TOKEN_STUDIO_CMD_V1") and Firecast ~= nil and Firecast.Messaging ~= nil and Firecast.Messaging.listen ~= nil then
    rawset(_G, "__ALENIA_TOKEN_STUDIO_CMD_V1", true);

    Firecast.Messaging.listen("ListChatCommands", function(message)
        local resp = (type(message.response) == "table") and message.response or {};
        table.insert(resp, {comando = "tokens", descricao = "Abre o Estudio Gerador de Tokens (12 molduras PNG transparente) e envia o link no chat"});
        message.response = resp;
    end);

    Firecast.Messaging.listen("HandleChatCommand", function(message)
        local cmd = tostring(message.comando or message.command or ""):lower();
        if cmd ~= "tokens" then return; end;
        local url = "https://alenia-rpg.onrender.com/gerador_tokens.html";
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
        message.response = {handled = true};
    end);
end;
    

return _frmAleniaTokenStudioDock;