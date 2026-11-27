#!/usr/bin/env python3
"""
Gera a ficha oficial AleniaCasaNobre.lfm (RRPG Firecast SDK 3.7b) — v1.0
Tomo XV — Casas Nobres, Feudos e Fortificações de Alenia:
- Criação nas 5 Matrizes Culturais (Aurora, Corallis, Kalis, Gaddra e Fronteiras Silvanas) + Brasão Clicável
- 10 Fortificações e Sedes Senhoriais (F01–F10): Construção Nova (100%) ou Reforma de Ruína (45% custo, ½ tempo)
- 8 Defesas Sem Pólvora (D01–D08) + 8 Obras Produtivas (D09–D16) com controle automático de Slots
- 14 Tropas, Artífices e Oficiais da Corte (G01–G14) com todas as sinergias oficiais do Padrão Prata
- Giro Mensal automático no Cofre da Casa, Eventos Sazonais (1d12), Combate de Engenhos e 4 Postos de Cerco no Chat
- Atualizador automático integrado via GitHub
"""
import os
import xml.sax.saxutils as sax

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
LFM_PATH = os.path.join(OUT_DIR, "AleniaCasaNobre.lfm")

BG_MAIN = "#121419"
BG_CARD = "#1B1E26"
BG_CARD_ALT = "#212530"
BG_INPUT = "#14171E"
BORDER_GOLD = "#9A7E42"
BORDER_DIM = "#343A4A"
BORDER_CRIMSON = "#8A2B28"
TEXT_MAIN = "#EAE4D6"
TEXT_GOLD = "#D9B96A"
TEXT_MUTED = "#A6AEBF"
TEXT_CRIMSON = "#E5736E"
TEXT_GREEN = "#7FC48C"

DEFENSES_UI = [
    ("D01", "D01 - Fosso Perimetral (Seco/Alagado)", "600 PP | Manut 5 PP | +80 PV, trava arietes 2d"),
    ("D02", "D02 - Portao Duplo & Mata-Caes", "950 PP | Manut 8 PP | +100 PV, +2 LE no portao"),
    ("D03", "D03 - Barbaca Avancada de Flanco", "1.800 PP | Manut 15 PP | +180 PV, +2 Def cerco (F04+)"),
    ("D04", "D04 - Caminho de Ronda Coberto", "1.200 PP | Manut 10 PP | +90 PV, Cobertura +4 arqueiros"),
    ("D05", "D05 - Bateria de Torre (2 Balistas)", "850 PP | Manut 12 PP | Tiro 3d10, alcance 180m (F04+, G07)"),
    ("D06", "D06 - Trabuco Fixo de Contrapeso", "1.400 PP | Manut 18 PP | Tiro 6d10, alcance 300m (F04+, G07)"),
    ("D07", "D07 - Cisterna Abobadada & Celeiro", "1.100 PP | Manut 6 PP | Dobra autonomia cerco p/ 60 dias"),
    ("D08", "D08 - Poterna Secreta & Galeria", "1.300 PP | Manut 5 PP | Sortidas noturnas e evacuacao"),
]

WORKS_UI = [
    ("D09", "D09 - Aldeia Arrendada (Fora Muros)", "2.200 PP | Renda +85 PP/mes | -15% soldo ate 25 tropas"),
    ("D10", "D10 - Moinho Hidraulico / Vento", "1.600 PP | Renda +65 PP/mes | +15 PP extra c/ Aldeia D09"),
    ("D11", "D11 - Estalagem Murada & Pedagio", "1.800 PP | Renda +75 PP/mes | +2 boatos regionais"),
    ("D12", "D12 - Forja Senhorial & Armaria", "1.500 PP | Renda +50 PP/mes | -20% equip inicial c/ G10"),
    ("D13", "D13 - Pedreira ou Serraria", "2.000 PP | Renda +80 PP/mes | -15% custo obras/defesas"),
    ("D14", "D14 - Armazem / Cais Fluvial-Costeiro", "2.400 PP | Renda +110 PP/mes | Atraca ate E05 +15% carga"),
    ("D15", "D15 - Ervanario, Enfermaria & Capela", "1.300 PP | Renda +20 PP/mes | -50% baixas, +2 Fe local"),
    ("D16", "D16 - Coudelaria & Patio Montarias", "1.900 PP | Renda +60 PP/mes | -10 PP/mes em G05 e G06"),
]

TROOPS_UI = [
    ("G01", "G01 - Miliciano e Vigia de Portao", "Inicial 15 PP | 12 PP/mes | Ind.Def +1 | 14 PV, Def 13, +3 (1d8+1)"),
    ("G02", "G02 - Soldado Regular (Lanceiro)", "Inicial 35 PP | 22 PP/mes | Ind.Def +2 | 24 PV, Def 16, +4 (1d8+2)"),
    ("G03", "G03 - Besteiro / Arqueiro Muralha", "Inicial 45 PP | 24 PP/mes | Ind.Def +2.5 | Tiro +4 (1d8)"),
    ("G04", "G04 - Infante Pesado / Sargento", "Inicial 90 PP | 40 PP/mes | Ind.Def +4 | Segura brechas, +6 (1d8+3)"),
    ("G05", "G05 - Patrulheiro Montado", "Inicial 140 PP | 48 PP/mes (38 c/ D16) | Ind.Def +3 | Alerta 2d"),
    ("G06", "G06 - Cavaleiro Juramentado Retido", "Inicial 220 PP | 75 PP/mes (65 c/ D16) | Ind.Def +6 | +8 (1d10+4)"),
    ("G07", "G07 - Artilheiro & Engenheiro", "Inicial 50 PP | 35 PP/mes | Ind.Def +3 | Opera D05 e D06"),
]

STAFF_UI = [
    ("G08", "G08 - Trabalhador Bracal / Servo Livre", "Contrat. 0 PP | 9 PP/mes (3 PC/dia) | 5x reduz tempo obra -10%"),
    ("G09", "G09 - Pedreiro ou Carpinteiro de Obra", "Contrat. 10 PP | 18 PP/mes | -5 PP manut. F04+ (ate 3x), D13"),
    ("G10", "G10 - Mestre Ferreiro & Armeiro", "Contrat. 25 PP | 30 PP/mes | Habilita Forja D12 (-20% equip.)"),
    ("G11", "G11 - Senescal Administrador", "Contrat. 30 PP | 45 PP/mes | +10% em TODA Receita Bruta!"),
    ("G12", "G12 - Mestre de Armas da Casa", "Contrat. 30 PP | 40 PP/mes | +10% Indice Defesa e +1 Moral"),
    ("G13", "G13 - Fisico Cirurgiao / Herbalista", "Contrat. 35 PP | 35 PP/mes | Potencializa D15 + 2 cataplasmas"),
    ("G14", "G14 - Mestre de Sussurros & Olheiro", "Contrat. 40 PP | 50 PP/mes | +3 em Contraespionagem da Casa"),
]


def lua_items_str(lst):
    return "{" + ", ".join("'" + s.replace("'", "\\'") + "'" for s in lst) + "}"


def xml_attr(val: str) -> str:
    return sax.escape(val, {'"': "&quot;"})


def build_lua_script() -> str:
    return r"""
local PLUGIN_MODULE_ID = "br.com.alenia.casa_nobre";
local PLUGIN_VERSION = "1.1";
local PLUGIN_RPK_URL = "https://raw.githubusercontent.com/krleandro/alenia/main/plugins/Alenia_Casa_Nobre.rpk";
local BIBLIOTECA_URL = "https://alenia-rpg.onrender.com/17_Feudos_Regencias_e_Intrigas.html";

local DialogsMod = nil;
local InternetMod = nil;
local PluginsMod = nil;
pcall(function() DialogsMod = require("dialogs.lua"); end);
pcall(function() InternetMod = require("internet.lua"); end);
pcall(function() PluginsMod = require("plugins.lua"); end);

local recalcularFeudo = nil;

local CULTURAS = {
    aurora = {
        nome = "1. Reino de Aurora (Feudal)",
        formula = "Casa de/d' [Terra] ou -ion/-aris (ex.: Casa de Specula, Casa Montavalle)",
        bastardo = "Cinza",
        legitimidade = "Carta regia selada em Altavanne (ou subinfeudacao a uma das 6 Grandes Casas) e protecao das rotas."
    },
    corallis = {
        nome = "2. Liga de Corallis (Patricia)",
        formula = "Familia dal/della [Marco] ou Plural -i (ex.: Casa della Rocca, Casa Falcone)",
        bastardo = "Coral",
        legitimidade = "Assento em guilda/camara municipal, solvencia bancaria, posse de navios (Tomo XIV) e patrocinio civico."
    },
    kalis = {
        nome = "3. Despotado de Kalis (Ferro)",
        formula = "Casa von [Rocha/Forte] ou Composto Duro (ex.: Casa von Kragstad)",
        bastardo = "Sombra",
        legitimidade = "Disciplina da guarnicao, cota de madeira negra/minerio entregue sem atraso e vigilancia das costas."
    },
    gaddra = {
        nome = "4. Confederacao de Gaddra (Oasis)",
        formula = "Cla al-[Marco] ou Dinastico -id (ex.: Cla al-Qar, Cla Sahirid)",
        bastardo = "Duna",
        legitimidade = "Controle de cisternas e pocos abertos, fidelidade a Lei da Hospitalidade (3 dias) e mediacao das Asabiyya."
    },
    silvana = {
        nome = "5. Fronteiras Silvanas (Pacto)",
        formula = "Ramo ab/ferch ou Composto Antigo (ex.: Ramo Derwlyn, Casa Caerloch)",
        bastardo = "Bruma",
        legitimidade = "Custodia sustentavel da mata/rio sem corte predatorio, validada pelo Circulo de Ancioes."
    }
};

local VIRTUDES_1D8 = {
    "1. Nome de Ferro Antigo: veteranos aceitam servir a Casa com -15% no soldo inicial.",
    "2. Canteiros Antigos: fundacoes de pedra pre-Forja no terreno reduzem em -10% o custo da 1a muralha/torre.",
    "3. Mesa da Anfitria: fama de jamais negar abrigo honesto; concede +2 contra espionagem externa.",
    "4. Veio de Agua Limpa: nascente interna purissima; imune a seca sazonal e +2 contra surtos hidricos.",
    "5. Carta de Pedagio Antigo: direito legal de cobrar 2 PC a 1 PP por carroca/barcaca sem contestacao.",
    "6. Armaria Preservada: suportes de carvalho guardam armas e cotas suficientes para equipar os primeiros 10 guardas de graca.",
    "7. Vinculo Academico: acordo antigo com Baldbella, Fisico ou escriba cobra -25% de soldo.",
    "8. Foral Fluvial / Costeiro: direito de erguer cais/porto proprio e prioridade de atracacao (E01-E05)."
};

local DIVIDAS_1D8 = {
    "1. Hipoteca em Cera Azul: a sede deve 2.000 PP a Casa Falcone (N086), vencendo em seis meses.",
    "2. Disputa de Divisa: o senhor vizinho reivindica o moinho ou o bosque limitrofe com um foral contraditorio.",
    "3. Parente Exilado ou Perjuro: um tio ou irmao banido cavalga com corsarios de Karstia ou mercenarios rivais.",
    "4. Suspeita da Chama Branca: um inquisidor investiga boatos de reliquias ou ritos antigos sob os alicerces.",
    "5. Sangue Devido: um cla livre ou familia mercante jura que a Casa lhe deve reparacao por uma emboscada passada.",
    "6. Galeria Selada: sob o porao ha um tunel murado as pressas ha um seculo que ninguem ousa reabrir.",
    "7. Vassalos Desconfiados: os aldeoes serviam ao antigo senhor deposto e testam cada decisao dos novos donos.",
    "8. Olhos de Kalgard: a posicao estrategica do feudo atraiu um informante dormente dos Ceifos de Kalis."
};

local EVENTOS_1D12 = {
    { tit = "1 - Seca Amarga ou Geada Negra", ef = "A renda agricola (D09, D10) cai pela metade nos proximos 3 meses, salvo se o feudo tiver Cisterna D07 ou Veio Limpo." },
    { tit = "2 - Bando de Salteadores na Estrada", ef = "Saqueadores cortam a rota; -50 PP/mes ate serem cacados pelos PJs ou expulsos por patrulha montada (G05)." },
    { tit = "3 - Infiltracao ou Sabotagem", ef = "Rival tenta subornar um vigia ou estragar grao. Rolar Contraespionagem (SAB/INT + 3 se tiver G14) CD 14." },
    { tit = "4 - Rixa de Divisa ou Pedagio", ef = "Nobre vizinho ou mercador contesta os marcos de pedra; exige diplomacia (Persuasao/Etiqueta CD 15) ou mostra de forca." },
    { tit = "5 - Surto de Febre nas Cabanas", ef = "Trabalhadores adoecem (Medicina CD 14; automatico se houver Fisico G13 + Ervanario D15); falha custa 40 PP em remedios." },
    { tit = "6-7 - Estacao Estavel e Rotineira", ef = "Lavouras, rondas e feiras seguem em paz; nenhuma alteracao extraordinaria no cofre." },
    { tit = "8 - Caravana Rica Pede Abrigo", ef = "Mercadores de longa rota pagam +1d6 x 20 PP por escolta e pouso seguro e trazem um item raro para venda." },
    { tit = "9 - Artifice Errante Pede Oficina", ef = "Um mestre canteiro, armeiro ou navegador oferece servico com -25% de custo na proxima obra se receber moradia." },
    { tit = "10 - Descoberta no Terreno", ef = "Escavacao ou arauto acha veio de pedra nobre, ruina antiga ou esconderijo esquecido (+1d6 x 30 PP ou gancho de aventura)." },
    { tit = "11 - Colheita e Feira Abundantes", ef = "Todas as obras produtivas (D09-D16) rendem +25% neste trimestre e a moral da guarnicao sobe +1." },
    { tit = "12 - Emissario de Grande Casa ou Liga", ef = "Proposta de alianca formal, casamento politico, contrato de escolta real ou compra garantida de producao (+150 PP + prestigio)." }
};

local FEUDOS_DB = {
    LIVRE = {
        code = "LIVRE",
        nome = "Fronteira Independente / Sem Feudo Suserano Fixo",
        senhor = "Autonomia local ou foral direto aberto",
        cadeia = "Definida na mesa pelo Mestre (sem bonus/encargo regional automatico)",
        litigio = "Livre de obrigacao faccional automatica; sujeito a cobica de vizinhos.",
        bonus = "Regras base do Tomo XV (selecione L01 a L22 para ativar concessoes regionais do Tomo XVII)."
    },
    L01 = {
        code = "L01",
        nome = "L01 - Dominio Regio de Altavanne & Pontauria (Coroa)",
        senhor = "Alto Rei Severor III (N003) / Regente Valora Valerion (N004) — Casa Valerion",
        cadeia = "Apice Imperial — Vassalagem direta ao Paco de Altavanne (Sub-feudo: Pontauria, N018)",
        litigio = "Z05: Sucessao contestada entre Valora Valerion e o Marechal Lucian Leonastis.",
        bonus = "-10% no salario mensal de Senescal (G11) e Mestre de Armas (G12); +1 Etiqueta/Persuasao legal."
    },
    L02 = {
        code = "L02",
        nome = "L02 - Feudo de Merlinport (Aurora -> Altavanne)",
        senhor = "Lorde Marcus Scutauria (N014) — Casa Scutauria",
        cadeia = "Casa do PJ -> Feudo de Merlinport -> Altavanne (L01)",
        litigio = "Z04: Corredor fluvial dos Pantanos Nebulosos, Torre de Specula e tarifas de guerra.",
        bonus = "-20% no custo de Armazem/Cais (D14) e +15 PP/mes extras por cada D14 ativo."
    },
    L03 = {
        code = "L03",
        nome = "L03 - Feudo de Dahrma [Controla Lavroga] (Aurora -> Altavanne)",
        senhor = "Lorde Lorian Montavalle (N012) — Casa Montavalle (Sub-vassalo: Castelao Galeran de Lavroga)",
        cadeia = "Casa do PJ / Lavroga -> Feudo de Dahrma -> Altavanne (L01)",
        litigio = "Z02: Dahrma controla Lavroga — tensao fiscal pelas mos de moinho e cantaria do sudoeste.",
        bonus = "+15 PP/mes adicionais se houver Aldeia (D09) e -15% no custo de Moinhos (D10)."
    },
    L04 = {
        code = "L04",
        nome = "L04 - Feudo de Vaarsa (Aurora -> Altavanne)",
        senhor = "Marechal Lucian Leonastis (N006) — Casa Leonastis",
        cadeia = "Casa do PJ -> Feudo de Vaarsa -> Altavanne (L01)",
        litigio = "Z01: Disputa o Pantano de Voernock contra Yoketsu (L05) | Z07: Passo de Rubecina.",
        bonus = "-15% no equipamento inicial de Regulares (G02) e Infantes Pesados (G04); +1 Moral em cerco."
    },
    L05 = {
        code = "L05",
        nome = "L05 - Feudo de Yoketsu (Aurora -> Altavanne)",
        senhor = "Senhor Feudal (Kenshu) Kenshin Tsurumaru — Casa Tsurumaru",
        cadeia = "Casa do PJ -> Feudo de Yoketsu -> Altavanne (L01)",
        litigio = "Z01: Disputa o Pantano de Voernock contra Vaarsa (L04) por canais, turfa e Casca-amarga (H17).",
        bonus = "+0.5 Indice de Defesa por unidade G02/G03 e +10 PP/mes de comercio costeiro se tiver Cais (D14)."
    },
    L06 = {
        code = "L06",
        nome = "L06 - Feudo de Altrax (Aurora -> Altavanne)",
        senhor = "Castela Aurelia d'Altrax (N016) — Casa d'Altrax",
        cadeia = "Casa do PJ -> Feudo de Altrax -> Altavanne (L01)",
        litigio = "Z04: Pantanos Nebulosos, Specula e sumico do emissario silvano Cadwyn (N025).",
        bonus = "Reerguer Ruina custa 40% do preco novo (em vez de 45%) e +2 em alertas de patrulha."
    },
    L07 = {
        code = "L07",
        nome = "L07 - Feudo de Aeraneas (Aurora -> Altavanne)",
        senhor = "Grao-Lorde Aurelian Ferraris (N015) — Casa Ferraris",
        cadeia = "Casa do PJ -> Feudo de Aeraneas -> Altavanne (L01)",
        litigio = "Z03: Disputa os Montes Ferraur contra as Cidades Suspensas (L08) + Greve nas minas.",
        bonus = "Forja Senhorial (D12) pela metade do preco (750 PP) e +20 PP/mes extras com Mestre Ferreiro (G10)."
    },
    L08 = {
        code = "L08",
        nome = "L08 - Feudo das Cidades Suspensas & Vergod (Aurora -> Altavanne)",
        senhor = "Senhora-Guardia Aerwen ferch Taldor (N024) — Conselho das Copas",
        cadeia = "Casa do PJ -> Feudo das Cidades Suspensas -> Altavanne (L01)",
        litigio = "Z03: Disputa os Montes Ferraur contra Aeraneas (L07) por nascentes e mineracao clandestina.",
        bonus = "-25% no custo de Mota (F03) e Ervanario (D15); Fisico/Herbalista (G13) dobra cataplasmas."
    },
    L09 = {
        code = "L09",
        nome = "L09 - Alineus [Sede da Regencia] (Corallis -> Altavanne)",
        senhor = "Arconte-Regente Corardo della Rocca (N021) — Casa della Rocca",
        cadeia = "Casa do PJ -> Regente della Rocca (Alineus) -> Altavanne (L01)",
        litigio = "Z06: Disputa de tarifas dos recifes contra Baldbella (L10) e O Ferro Velho (N026).",
        bonus = "+15 PP/mes adicionais por Cais/Armazem (D14) e -15% em reparos navais na Liga."
    },
    L10 = {
        code = "L10",
        nome = "L10 - Baldbella (Corallis -> Regente -> Altavanne)",
        senhor = "Sindico-Patricio Valerio Corvella — Casa Corvella",
        cadeia = "Casa do PJ -> Baldbella -> Regente della Rocca (L09) -> Altavanne (L01)",
        litigio = "Z06: Boicote tarifario contra Alineus e ameaca de peticao direta a Altavanne.",
        bonus = "-30% no salario mensal de Fisico Cirurgiao (G13) e +50% teto de credito em Cera Azul."
    },
    L11 = {
        code = "L11",
        nome = "L11 - Stoneforge (Corallis -> Regente -> Altavanne)",
        senhor = "Mestre-Barao Orso Rupefori — Casa Rupefori",
        cadeia = "Casa do PJ -> Stoneforge -> Regente della Rocca (L09) -> Altavanne (L01)",
        litigio = "Falta de pontas de adamante pela greve de Aeraneas empurra oficinas ao mercado negro.",
        bonus = "-20% no custo de Balistas (D05) e Trabucos (D06) e +1 nos disparos de engenhos."
    },
    L12 = {
        code = "L12",
        nome = "L12 - Biemont & Portocala (Corallis -> Regente -> Altavanne)",
        senhor = "Dama Lorenza Falcenzo (N086) — Casa Falcenzo",
        cadeia = "Casa do PJ -> Biemont -> Regente della Rocca (L09) -> Altavanne (L01)",
        litigio = "Z06: Compra de hipotecas de armadores e contatos discretos com O Ferro Velho.",
        bonus = "+20 PP/mes adicionais se houver Estalagem (D11) ou Cais (D14); juros pela metade."
    },
    L13 = {
        code = "L13",
        nome = "L13 - Sellene & Claramar (Corallis -> Regente / Altavanne)",
        senhor = "Arquimestre Matteo dal Pelago (N031) — Academia de Sellene",
        cadeia = "Casa do PJ -> Sellene -> Regente della Rocca (L09) [Civil] & Altavanne (L01) [Acervo]",
        litigio = "Vigilancia sobre o Acervo Oculto e corrida secreta pelos relatos de Thanatos.",
        bonus = "+2 automatico em testes de Contraespionagem da Casa, Historia e Investigacao."
    },
    L14 = {
        code = "L14",
        nome = "L14 - Naasar & Bayd [Sede da Regencia] (Gaddra -> Altavanne)",
        senhor = "Regente das Dunas Qasir Zaharid (N022) — Cla Zaharid",
        cadeia = "Casa do PJ -> Regente Qasir Zaharid (Naasar) -> Altavanne (L01)",
        litigio = "Z07: Assassinato do Arbitro do Sangue (N068) e risco de guerra na Rota do Sal.",
        bonus = "-30% no custo de Cisterna Abobadada (D07) e protecao contra embargo hidrico."
    },
    L15 = {
        code = "L15",
        nome = "L15 - OX (Gaddra -> Regente -> Altavanne)",
        senhor = "Emir Khalur al-Shams — Cla al-Shams",
        cadeia = "Casa do PJ -> OX -> Regente Qasir Zaharid (L14) -> Altavanne (L01)",
        litigio = "Comercio ambiguo de montarias entre compradores de Vaarsa e clas livres.",
        bonus = "-25% no custo de Coudelaria (D16) e -5 PP/mes extras por tropa montada (G05/G06)."
    },
    L16 = {
        code = "L16",
        nome = "L16 - Qal-Zahar & Suq-Ramad (Gaddra -> Regente -> Altavanne)",
        senhor = "Senhor Tarik ibn Sahir — Cla Sahirid",
        cadeia = "Casa do PJ -> Qal-Zahar -> Regente Qasir Zaharid (L14) -> Altavanne (L01)",
        litigio = "Z07: Mercadores locais lucram caso o Passo de Rubecina seja fechado.",
        bonus = "+20 PP/mes adicionais se houver Estalagem/Feira (D11) ou Cais Costeiro (D14)."
    },
    L17 = {
        code = "L17",
        nome = "L17 - Marca de Vargheim (Gaddra -> Regente -> Altavanne)",
        senhor = "Chefe-Vigia Halvor Sangue-Seco — Cla Sangue-Seco",
        cadeia = "Casa do PJ -> Vargheim -> Regente Qasir Zaharid (L14) -> Altavanne (L01)",
        litigio = "Z07: Clas da escarpa pressionam para fechar o Passo de Rubecina contra Vaarsa.",
        bonus = "+1 Moral permanente na guarnicao da fortaleza e +2 em Intimidacao fronteirica."
    },
    L18 = {
        code = "L18",
        nome = "L18 - Cidadela de Kalgard [Regencia] (Kalis -> Altavanne)",
        senhor = "Despota-Regente Grimrik Ulscold (N023) — Casa Ulscold",
        cadeia = "Casa do PJ -> Despota Grimrik Ulscold (Kalgard) -> Altavanne (L01)",
        litigio = "Z08: Tensao com mercadores do sul kalita e busca por segredos de Thanatos.",
        bonus = "+2 automatico em Contraespionagem da Casa e -25% no salario de Mestre de Sussurros (G14)."
    },
    L19 = {
        code = "L19",
        nome = "L19 - Kragstad (Kalis -> Regente -> Altavanne)",
        senhor = "Lorde-Vigia Torvald von Kragstad — Casa von Kragstad (N083)",
        cadeia = "Casa do PJ -> Kragstad -> Despota Grimrik Ulscold (L18) -> Altavanne (L01)",
        litigio = "Combate aos corsarios de Ravena e recusa de operacoes clandestinas desonrosas.",
        bonus = "-15% no custo de Forte Costeiro (F07) e nas defesas de muralha D02 a D05."
    },
    L20 = {
        code = "L20",
        nome = "L20 - Drakenhall (Kalis -> Regente -> Altavanne)",
        senhor = "Jarl Borhild Hrafngard (N082) — Casa Hrafngard",
        cadeia = "Casa do PJ -> Drakenhall -> Despota Grimrik Ulscold (L18) -> Altavanne (L01)",
        litigio = "Controle dos depositos de madeira negra naval usados como alavanca no Conselho.",
        bonus = "-25% no custo de Serrarias/Pedreiras (D13) e +20 PP/mes com D13 ativo."
    },
    L21 = {
        code = "L21",
        nome = "L21 - Dobalbek (Kalis -> Regente -> Altavanne)",
        senhor = "Dama-Chanceler Freydis Drakenvorn (N084) — Casa Drakenvorn",
        cadeia = "Casa do PJ -> Dobalbek -> Despota Grimrik Ulscold (L18) -> Altavanne (L01)",
        litigio = "Z08: Ponte financeira e maritima dividida entre comercio limpo e redes de sombra.",
        bonus = "-15% no custo de Cais/Estaleiros (D14) e +15 PP/mes adicionais se D14 ativo."
    },
    L22 = {
        code = "L22",
        nome = "L22 - Fugong & Kalima (Kalis -> Regente -> Altavanne)",
        senhor = "Intendente-Senhor Ragnar Skoldhavn — Casa Skoldhavn",
        cadeia = "Casa do PJ -> Fugong -> Despota Grimrik Ulscold (L18) -> Altavanne (L01)",
        litigio = "Z08: Oposicao mercantil silenciosa a Kalgard e contrabando com a Ilha das Safiras.",
        bonus = "+25 PP/mes adicionais se houver Forja/Oficina (D12) ou Ervanario Alquimico (D15)."
    }
};

local INTRIGAS_1D12 = {
    { tit = "1 - Marco de Pedra Arrancado a Noite", ef = "Vizinho deslocou marco secular de divisa p/ tomar bosque, turfeira ou moinho (Z01 Voernock / Z03 Ferraur • Investigacao/Historia CD 16)." },
    { tit = "2 - Comboio Retido por Vistoria", ef = "Barcacas de grao, pedra de Lavroga ou sal retidas sob pretexto legal para forcar concessao (Etiqueta/Barganha + Status CD 17)." },
    { tit = "3 - Pupilo Nobre Desaparecido", ef = "Jovem herdeiro enviado como hospede-garantia entre duas Casas sumiu na estrada — sequestro politico ou fuga (Sobrevivencia/Intuicao CD 15)." },
    { tit = "4 - Dois Forais com Selos Reais", ef = "Litigantes exibem cartas legitimas de reis diferentes sobre a mesma ponte ou encosta (Historia CD 18 ou apelacao ao Preboste N018)." },
    { tit = "5 - Proposta Secreta Entre Escaloes", ef = "Enviado do Regente pede segredo contra Altavanne (ou emissario real pede vigilancia sobre o Regente) em troca de isencao de tributo." },
    { tit = "6 - Juizo do Dia (Duelo de Campeoes)", ef = "Barao acusa vizinho de sabotagem sem prova escrita; busca-se campeao para duelo formal (Armas Brancas + Status S02+)." },
    { tit = "7 - Casamento Politico Sabotado", ef = "Carta caluniosa (ou verdadeira!) surge na vespera de alianca matrimonial ameacando romper a Paz do Teto (Persuasao/Submundo CD 16)." },
    { tit = "8 - Sublevacao na Sub-castelania", ef = "Canteiros ou aldeoes (como em Lavroga Z02 ou Vargheim Z07) retem a cota ate receberem escolta contra saqueadores (CD 16)." },
    { tit = "9 - Leilao Silencioso de Hipoteca", ef = "Banqueiro de Biemont (N086) ou Dobalbek (N084) poe a venda divida vencida de um solar estrategico vizinho (500 a 1.500 PP)." },
    { tit = "10 - Inspecao do Preboste ou Chama Branca", ef = "Juizes reais ou inquisidores exigem vistoriar paiois, masmorras e livros de pedagio (Etiqueta/Enganacao/Fe CD 16)." },
    { tit = "11 - Sinal Naval Estrangeiro na Costa", ef = "Pescadores viram lanternas escuras ancorando numa enseada sem cais na divisa de dois feudos (Navegacao/Furtividade CD 15)." },
    { tit = "12 - Convocacao Dupla de Estandarte", ef = "Arautos rivais de Altavanne e de um Grande Lorde batem ao portao no mesmo dia exigindo posicao formal em 72 horas!" }
};


local SEATS = {
    F01 = { code = "F01", nome = "F01 - Entreposto e Feitoria de Estrada", porte = "Sede Inicial (Status 1+)", cost = 1800, months = 2, maint = 25, ideal = 6, maxG = 15, hp = 180, le = 6, defSlots = 1, workSlots = 2, maxVil = 1, benef = "Sustenta Status 2 no local; abriga caravanas e mulas com seguranca contra lobos e pequenos bandos." },
    F02 = { code = "F02", nome = "F02 - Casa-Forte e Solar Urbano Patricio", porte = "Sede Inicial (Status 2+)", cost = 3500, months = 4, maint = 45, ideal = 10, maxG = 25, hp = 260, le = 8, defSlots = 2, workSlots = 2, maxVil = 1, benef = "Reduz em -50% o gasto mensal de Padrao de Vida Confortavel/Abastado na cidade e concede +2 em Etiqueta e Barganha em recepcoes." },
    F03 = { code = "F03", nome = "F03 - Mota com Palicada e Salao Senhorial", porte = "Sede Inicial (Status 2+)", cost = 4800, months = 4, maint = 55, ideal = 18, maxG = 45, hp = 320, le = 7, defSlots = 2, workSlots = 3, maxVil = 1, benef = "Rapida de erguer onde ha floresta; a elevacao da mota concede +2 na Defesa contra investidas terrestres." },
    F04 = { code = "F04", nome = "F04 - Torre de Vigia de Cantaria (Specula)", porte = "Praca Menor (Status 2-3)", cost = 8000, months = 6, maint = 75, ideal = 15, maxG = 35, hp = 450, le = 10, defSlots = 3, workSlots = 2, maxVil = 3, benef = "Enxerga movimentos de tropa a 20 km (+4 Percepcao regional contra surpresa); imune a incendio externo comum (8.000 PP exatos do Tomo I)." },
    F05 = { code = "F05", nome = "F05 - Solar Rural Fortificado e Quinta Murada", porte = "Praca Menor (Status 3+)", cost = 14000, months = 9, maint = 120, ideal = 25, maxG = 60, hp = 580, le = 10, defSlots = 3, workSlots = 5, maxVil = 3, benef = "Equilibra defesa solida com 5 Slots de Obra, sendo a melhor sede de porte medio para gerar superavit economico mensal em prata." },
    F06 = { code = "F06", nome = "F06 - Cacer de Oasis e Cisterna (Gaddra)", porte = "Praca Menor (Status 3+)", cost = 16000, months = 10, maint = 130, ideal = 30, maxG = 75, hp = 640, le = 11, defSlots = 4, workSlots = 4, maxVil = 3, benef = "Inclui reserva hidrica inviolavel (60 dias de cerco no deserto; sitiantes sofrem testes diarios de sede) e atrai caravanas dispostas a pagar pedagio." },
    F07 = { code = "F07", nome = "F07 - Forte Costeiro e Torre de Corrente", porte = "Praca Menor (Status 3+)", cost = 18500, months = 12, maint = 155, ideal = 35, maxG = 85, hp = 720, le = 12, defSlots = 4, workSlots = 4, maxVil = 3, benef = "Abriga ate 2 embarcacoes medias (E01-E08) livres de taxas portuarias; corrente erguida bloqueia o estuario (LE 12, 120 PV)." },
    F08 = { code = "F08", nome = "F08 - Castelo Feudal de Cantaria com Barbaca", porte = "Grande Fortaleza (Status 3-4)", cost = 36000, months = 24, maint = 280, ideal = 70, maxG = 180, hp = 1200, le = 14, defSlots = 6, workSlots = 6, maxVil = 6, benef = "Sustenta Status 4; caso a muralha externa caia, a Torre de Menagem conserva 400 PV proprios e exige segundo assalto separado." },
    F09 = { code = "F09", nome = "F09 - Fortaleza de Escarpa e Rocha Escavada", porte = "Grande Fortaleza (Status 4+)", cost = 65000, months = 36, maint = 420, ideal = 110, maxG = 280, hp = 1650, le = 16, defSlots = 7, workSlots = 5, maxVil = 6, benef = "Imune a Torres de Cerco com rodas e a tuneis de sapa comuns; exercitos invasores perdem vantagem numerica superior a 2:1 nas muralhas." },
    F10 = { code = "F10", nome = "F10 - Cidadela e Paco Senhorial de Grande Casa", porte = "Grande Fortaleza (Status 5)", cost = 110000, months = 48, maint = 750, ideal = 200, maxG = 500, hp = 2400, le = 18, defSlots = 9, workSlots = 9, maxVil = 6, benef = "Sede definitiva de fim de campanha (Lenda/Epico); concede +3 em diplomacia, recepcao de embaixadores e convocacao de vassalos." }
};

local DEFENSES = {
    { id = "D01", nome = "Fosso Perimetral", cost = 600, maint = 5, hp = 80, max = 1, reqF04 = false, reqG07 = false, desc = "Vala de 6m de largura por 4m de profundidade com estacas agucadas ou alagada. Impede aproximacao de Torres de Cerco e Arietes ate ser aterrado (2 dias sob tiro direto)." },
    { id = "D02", nome = "Portao Duplo com Rastrilho e Mata-Caes", cost = 950, maint = 8, hp = 100, max = 1, reqF04 = false, reqG07 = false, desc = "Passagem abobadada com duas portas de carvalho ferrado, grade levadica e aberturas verticais: +100 PV e +2 LE no portao; invasores retidos sofrem oleo/cal/pedras (3d6/rodada)." },
    { id = "D03", nome = "Barbaca Avancada de Flanqueamento", cost = 1800, maint = 15, hp = 180, max = 1, reqF04 = true, reqG07 = false, desc = "Fortim avancado diante da ponte de entrada em angulo quebrado: +180 PV, +2 Defesa no cerco, absorve o 1o assalto inteiro sob fogo cruzado." },
    { id = "D04", nome = "Caminho de Ronda Coberto (Cadafalso)", cost = 1200, maint = 10, hp = 90, max = 1, reqF04 = false, reqG07 = false, desc = "Galeria coberta de carvalho tratado contra fogo no topo da muralha: +90 PV e Cobertura Superior (+4 Defesa) para arqueiros e besteiros da guarnicao." },
    { id = "D05", nome = "Bateria de Torre (2 Balistas de Muralha)", cost = 850, maint = 12, hp = 0, max = 3, reqF04 = true, reqG07 = true, desc = "Par de escorpioes/balistas de torcao de Stoneforge em terraco giratorio. Alcance 180m, Dano 3d10 perfurante (ignora 5 pontos de LE de escudos/mantletes). Exige F04+ e G07." },
    { id = "D06", nome = "Trabuco Fixo de Contrapeso", cost = 1400, maint = 18, hp = 0, max = 3, reqF04 = true, reqG07 = true, desc = "Engenho pesado sem polvora com caixa de 5t de pedra/ferro. Alcance 300m, Dano 6d10 contundente (ignora 8 pontos de LE; recarga 2 turnos) ou potes de alcatrao (3d6 fogo em 3m). Exige F04+ e G07." },
    { id = "D07", nome = "Cisterna Abobadada e Celeiro Selado", cost = 1100, maint = 6, hp = 0, max = 1, reqF04 = false, reqG07 = false, desc = "Reservatorio subterraneo em argamassa hidraulica e silos ventilados com cal: dobra a autonomia sob cerco fechado de 30 para 60 dias e concede +4 vs sabotagem de agua." },
    { id = "D08", nome = "Poterna Secreta e Galeria de Sortida", cost = 1300, maint = 5, hp = 0, max = 1, reqF04 = false, reqG07 = false, desc = "Tunel estreito oculto sob o alicerce saindo atras de afloramento/bosque a 200m (Investigacao externa CD 22): permite Sortidas Noturnas com surpresa, mensageiros e evacuacao." }
};

local WORKS = {
    { id = "D09", nome = "Aldeia Arrendada e Terras de Lavoura", cost = 2200, income = 85, usesSlot = false, max = 6, desc = "20 a 40 familias livres cultivando centeio, trigo, cevada e hortas sob protecao da Casa (fora dos muros): +85 PP/mes, reduz -15% soldo de ate 25 soldados por aldeia e fornece ate 20 milicianos G01 em emergencia." },
    { id = "D10", nome = "Moinho Hidraulico ou de Vento", cost = 1600, income = 65, usesSlot = true, max = 2, desc = "Roda d'agua de carvalho e mos de pedra de Lavroga: +65 PP/mes (+15 PP extras de sinergia agricola se houver pelo menos 1 Aldeia D09, totalizando +80 PP/mes)." },
    { id = "D11", nome = "Estalagem Murada e Posto de Pedagio", cost = 1800, income = 75, usesSlot = true, max = 2, desc = "Pouso seguro de estrada com cocheira, taverna limpa e cancela licenciada: +75 PP/mes e +2 em testes para colher rumores regionais sem sair do feudo." },
    { id = "D12", nome = "Forja Senhorial e Armaria", cost = 1500, income = 50, usesSlot = true, max = 1, desc = "Oficina com fole duplo, bigorna fixa e tempera: +50 PP/mes e, com Mestre Ferreiro G10 residente, reduz em -20% o custo de equipamento inicial de todas as tropas contratadas!" },
    { id = "D13", nome = "Pedreira de Cantaria ou Serraria Hidraulica", cost = 2000, income = 80, usesSlot = true, max = 2, desc = "Extracao organizada de blocos aparelhados e vigas curadas (ideal com G08/G09): +80 PP/mes e reduz em -15% o custo em prata de todas as defesas e obras do dominio!" },
    { id = "D14", nome = "Armazem Mercantil ou Cais Fluvial/Costeiro", cost = 2400, income = 110, usesSlot = true, max = 2, desc = "Trapiche de pedra e madeira com guindaste de carga e balanca aferida: +110 PP/mes, atraca navios ate E05 sem taxa e aumenta em +15% o lucro de cargas dos PJs." },
    { id = "D15", nome = "Ervanario Murado, Enfermaria e Capela", cost = 1300, income = 20, usesSlot = true, max = 1, desc = "Jardim medicinal (H01, H03 do Tomo X), enfermaria de 6 leitos e oratorio: +20 PP/mes, reduz pela metade mortes de feridos pos-cerco e concede +2 (Local Consagrado) para Fe Verdadeira." },
    { id = "D16", nome = "Coudelaria e Patio de Montarias", cost = 1900, income = 60, usesSlot = true, max = 1, desc = "Piquetes cercados, ferradoria e pista de adestramento: +60 PP/mes e reduz em -10 PP/mes a manutencao de cada Patrulheiro Montado (G05) e Cavaleiro Retido (G06)." }
};

local UNITS = {
    { id = "G01", nome = "Miliciano e Vigia de Portao", hire = 15, wage = 12, power = 1.0, troop = true, mounted = false, atk = 3, dmg = "1d8+1", desc = "Moradores jovens treinados para guardar cancelas e tocar o sino (14 PV, Defesa 13, Lanca +3, 1d8+1)." },
    { id = "G02", nome = "Soldado Regular (Lanceiro/Escudeiro)", hire = 35, wage = 22, power = 2.0, troop = true, mounted = false, atk = 4, dmg = "1d8+2", desc = "Espinha dorsal profissional do castelo — Guarda de Cidade do Tomo IV (24 PV, Defesa 16, Proteger Aliado, Lanca +4, 1d8+2)." },
    { id = "G03", nome = "Besteiro ou Arqueiro de Muralha", hire = 45, wage = 24, power = 2.5, troop = true, mounted = false, atk = 4, dmg = "1d8", desc = "Essenciais para manter sitiantes longe do fosso; sobre Caminho de Ronda Coberto (D04) recebem +4 na Defesa." },
    { id = "G04", nome = "Infante Pesado e Sargento Veterano", hire = 90, wage = 40, power = 4.0, troop = true, mounted = false, atk = 6, dmg = "1d8+3", desc = "Veterano calejado de brigantina/malha e escudo pesado capaz de segurar brecha de portao ou comandar 10 regulares." },
    { id = "G05", nome = "Patrulheiro e Batedor Montado", hire = 140, wage = 48, power = 3.0, troop = true, mounted = true, atk = 5, dmg = "1d8+2", desc = "Mantem estradas livres de salteadores (protegendo D09/D11) e garante aviso antecipado de 2 dias sobre colunas hostis." },
    { id = "G06", nome = "Cavaleiro Juramentado Retido", hire = 220, wage = 75, power = 6.0, troop = true, mounted = true, atk = 8, dmg = "1d10+4", desc = "Combatente consagrado (Sor/Dama) vinculado por homenagem: lidera sortidas devastadoras e comanda a praca na ausencia dos PJs." },
    { id = "G07", nome = "Artilheiro e Engenheiro de Muralha", hire = 50, wage = 35, power = 3.0, troop = true, mounted = false, atk = 5, dmg = "3d10", desc = "Especialista treinado em Stoneforge/Lavroga para operar balistas (D05), trabucos (D06) e escorar muros atingidos." },
    { id = "G08", nome = "Trabalhador Bracal / Servo Assalariado", hire = 0, wage = 9, power = 0, troop = false, mounted = false, desc = "3 PC/dia exatos do Tomo I. Cada grupo de 5 trabalhadores extras numa construcao reduz o tempo de obra em -10% (ate -20%)." },
    { id = "G09", nome = "Pedreiro ou Carpinteiro de Obra", hire = 10, wage = 18, power = 0, troop = false, mounted = false, desc = "Mantem telhados e pontes intactos (reduz manutencao estrutural de F04-F10 em -5 PP/mes cada, ate 3x) e opera D13." },
    { id = "G10", nome = "Mestre Ferreiro e Armeiro Residente", hire = 25, wage = 30, power = 0, troop = false, mounted = false, desc = "Requisito para ativar o desconto de -20% em equipamento militar da Forja Senhorial (D12)." },
    { id = "G11", nome = "Senescal e Meirinho Administrador", hire = 30, wage = 45, power = 0, troop = false, mounted = false, desc = "Guarda as chaves do celeiro, julga rixas rurais, escritura contas e AUMENTA EM +10% toda a Receita Bruta do feudo!" },
    { id = "G12", nome = "Mestre de Armas da Casa", hire = 30, wage = 40, power = 0, troop = false, mounted = false, desc = "Veterano instrutor: eleva em +10% o Indice de Defesa total da guarnicao e concede +1 nos testes de Moral em cerco." },
    { id = "G13", nome = "Fisico Cirurgiao ou Herbalista", hire = 35, wage = 35, power = 0, troop = false, mounted = false, desc = "Previne epidemias, potencializa o Ervanario (D15) e entrega gratuitamente aos PJs 2 cataplasmas ou 1 antidoto comum por mes." },
    { id = "G14", nome = "Mestre de Sussurros e Olheiro", hire = 40, wage = 50, power = 0, troop = false, mounted = false, desc = "Coordena estalajadeiros e mensageiros discretos: concede +3 em testes de Contraespionagem contra traidores e sabotadores." }
};

local function num(v, fallback)
    if v == nil then return fallback or 0; end;
    local s = tostring(v):gsub(",", ".");
    local n = tonumber(s);
    if n == nil then return fallback or 0; end;
    return n;
end;

local function fmtInt(n)
    local i = math.floor(math.abs(n) + 0.5);
    local s = tostring(i);
    local out = s:reverse():gsub("(%d%d%d)", "%1."):reverse():gsub("^%.", "");
    if n < 0 then return "-" .. out; end;
    return out;
end;

local function fmtPP(n)
    return fmtInt(n) .. " PP";
end;

local function enviarChatOuMsg(texto)
    local mesa = (sheet ~= nil) and Firecast.getMesaDe(sheet) or nil;
    if mesa ~= nil and mesa.activeChat ~= nil then
        mesa.activeChat:enviarMensagem(texto);
    else
        showMessage(texto);
    end;
end;

local function rolarExpressaoChat(expr, titulo, cdAlvo, sufixoSucesso, sufixoFalha)
    local rolagem = Firecast.interpretarRolagem(expr);
    local mesa = (sheet ~= nil) and Firecast.getMesaDe(sheet) or nil;
    if mesa ~= nil and mesa.activeChat ~= nil then
        mesa.activeChat:rolarDados(rolagem, titulo,
            function(rolado)
                if rolado == nil then return; end;
                local res = rolado.resultado;
                if cdAlvo ~= nil and cdAlvo > 0 then
                    if res >= cdAlvo then
                        mesa.activeChat:enviarMensagem("[SUCESSO! " .. tostring(res) .. " vs CD " .. tostring(cdAlvo) .. "] " .. (sufixoSucesso or "Objetivo alcancado!"));
                    else
                        mesa.activeChat:enviarMensagem("[FALHA: " .. tostring(res) .. " vs CD " .. tostring(cdAlvo) .. "] " .. (sufixoFalha or "Complicacao em cena!"));
                    end;
                elseif sufixoSucesso ~= nil and sufixoSucesso ~= "" then
                    mesa.activeChat:enviarMensagem("Resultado (" .. expr .. "): " .. tostring(res) .. " — " .. sufixoSucesso);
                end;
            end);
    else
        rolagem:rolarLocalmente();
        local res = rolagem.resultado;
        local extra = "";
        if cdAlvo ~= nil and cdAlvo > 0 then
            extra = (res >= cdAlvo) and ("\nSUCESSO vs CD " .. tostring(cdAlvo) .. "! " .. (sufixoSucesso or "")) or ("\nFALHA vs CD " .. tostring(cdAlvo) .. "! " .. (sufixoFalha or ""));
        elseif sufixoSucesso ~= nil and sufixoSucesso ~= "" then
            extra = "\n" .. sufixoSucesso;
        end;
        showMessage(titulo .. "\nRolagem (" .. expr .. "): " .. tostring(res) .. extra);
    end;
end;

local function getItemById(lista, id)
    for i = 1, #lista do
        if lista[i].id == id then return lista[i]; end;
    end;
    return nil;
end;

local function atualizarVisibilidadeBrasao()
    if sheet == nil then return; end;
    if self ~= nil and self.lblBrasaoHint ~= nil then
        local u = tostring(sheet.brasaoUrl or "");
        pcall(function() self.lblBrasaoHint:setVisible(u == ""); end);
    end;
end;

local function definirBrasaoPorURL()
    if sheet == nil then return; end;
    if DialogsMod == nil or type(DialogsMod.inputQuery) ~= "function" then
        showMessage("Clique diretamente dentro do escudo para carregar o brasao da Casa pelo Firecast.");
        return;
    end;
    DialogsMod.inputQuery(
        "Brasao Heraldico da Casa",
        "Cole a URL direta (https://...) do brasao da Casa ou deixe vazio para limpar:",
        tostring(sheet.brasaoUrl or ""),
        function(val)
            sheet.brasaoUrl = tostring(val or ""):gsub("^%s+", ""):gsub("%s+$", "");
            atualizarVisibilidadeBrasao();
        end,
        nil,
        true
    );
end;

local function limparBrasao()
    if sheet == nil then return; end;
    sheet.brasaoUrl = "";
    atualizarVisibilidadeBrasao();
end;

local function calcularDadosFeudo()
    local seatId = tostring(sheet.sedeId or "F04");
    local seat = SEATS[seatId] or SEATS.F04;
    local feudoId = tostring(sheet.feudoSuseranoId or "LIVRE");
    local feudoInfo = FEUDOS_DB[feudoId] or FEUDOS_DB.LIVRE;
    local usarBonusFeudo = (sheet.aplicarBonusFeudo ~= false) and (feudoId ~= "LIVRE");
    local sobEmbargo = (sheet.sobEmbargoVizinho == true);

    local isRuin = (tostring(sheet.modoAquisicao or "ruin") == "ruin");
    local ruinFactor = (usarBonusFeudo and feudoId == "L06") and 0.40 or 0.45;
    local seatBaseMult = isRuin and ruinFactor or 1.0;
    if usarBonusFeudo and feudoId == "L08" and seatId == "F03" then
        seatBaseMult = seatBaseMult * 0.75;
    elseif usarBonusFeudo and feudoId == "L19" and seatId == "F07" then
        seatBaseMult = seatBaseMult * 0.85;
    end;
    local seatCost = math.floor(seat.cost * seatBaseMult + 0.5);

    local qtdD13 = math.max(0, math.floor(num(sheet.qtd_D13, 0)));
    local qtdD12 = math.max(0, math.floor(num(sheet.qtd_D12, 0)));
    local qtdG10 = math.max(0, math.floor(num(sheet.qtd_G10, 0)));
    local qtdD16 = math.max(0, math.floor(num(sheet.qtd_D16, 0)));
    local qtdG11 = math.max(0, math.floor(num(sheet.qtd_G11, 0)));
    local qtdG12 = math.max(0, math.floor(num(sheet.qtd_G12, 0)));
    local qtdG07 = math.max(0, math.floor(num(sheet.qtd_G07, 0)));
    local qtdG08 = math.max(0, math.floor(num(sheet.qtd_G08, 0)));
    local qtdG09 = math.max(0, math.floor(num(sheet.qtd_G09, 0)));

    local temPedreira = (qtdD13 > 0);
    local temForjaAtiva = (qtdD12 > 0 and qtdG10 > 0);
    local temCoudelaria = (qtdD16 > 0);
    local temGestao10 = (qtdG11 > 0) or (sheet.pjAdminMes == true);
    local temMestreArmas = (qtdG12 > 0);

    local defSlotsUsed = 0;
    local defBuild = 0;
    local defMaint = 0;
    local extraHP = 0;
    local avisos = {};

    for i = 1, #DEFENSES do
        local d = DEFENSES[i];
        local q = math.max(0, math.floor(num(sheet["qtd_" .. d.id], 0)));
        defSlotsUsed = defSlotsUsed + q;
        local dUnitCost = d.cost;
        if usarBonusFeudo and feudoId == "L11" and (d.id == "D05" or d.id == "D06") then
            dUnitCost = math.floor(dUnitCost * 0.80 + 0.5);
        elseif usarBonusFeudo and feudoId == "L14" and d.id == "D07" then
            dUnitCost = math.floor(dUnitCost * 0.70 + 0.5);
        elseif usarBonusFeudo and feudoId == "L19" and (d.id == "D02" or d.id == "D03" or d.id == "D04" or d.id == "D05") then
            dUnitCost = math.floor(dUnitCost * 0.85 + 0.5);
        end;
        defBuild = defBuild + q * dUnitCost;
        defMaint = defMaint + q * d.maint;
        extraHP = extraHP + q * d.hp;
        if q > 0 and d.reqF04 and seat.cost < 8000 then
            table.insert(avisos, d.id .. " exige Sede F04+");
        end;
        if q > 0 and d.reqG07 and qtdG07 < 1 then
            table.insert(avisos, d.id .. " exige Artilheiro G07");
        end;
    end;
    if defSlotsUsed > seat.defSlots then
        table.insert(avisos, "Slots de Defesa excedidos (" .. tostring(defSlotsUsed) .. "/" .. tostring(seat.defSlots) .. ")!");
    end;

    local workSlotsUsed = 0;
    local workBuild = 0;
    local rawIncome = 0;
    local rawVillages = math.max(0, math.floor(num(sheet.qtd_D09, 0)));
    local effVillages = math.min(seat.maxVil, rawVillages);
    if rawVillages > seat.maxVil then
        table.insert(avisos, "D09 excede limite do porte (" .. tostring(rawVillages) .. "/" .. tostring(seat.maxVil) .. " aldeias)");
    end;

    for i = 1, #WORKS do
        local w = WORKS[i];
        local q = math.max(0, math.floor(num(sheet["qtd_" .. w.id], 0)));
        if w.usesSlot then workSlotsUsed = workSlotsUsed + q; end;
        local wCost = w.cost;
        if usarBonusFeudo then
            if feudoId == "L02" and w.id == "D14" then wCost = math.floor(wCost * 0.80 + 0.5);
            elseif feudoId == "L03" and w.id == "D10" then wCost = math.floor(wCost * 0.85 + 0.5);
            elseif feudoId == "L07" and w.id == "D12" then wCost = math.floor(wCost * 0.50 + 0.5);
            elseif feudoId == "L08" and w.id == "D15" then wCost = math.floor(wCost * 0.75 + 0.5);
            elseif feudoId == "L15" and w.id == "D16" then wCost = math.floor(wCost * 0.75 + 0.5);
            elseif feudoId == "L20" and w.id == "D13" then wCost = math.floor(wCost * 0.75 + 0.5);
            elseif feudoId == "L21" and w.id == "D14" then wCost = math.floor(wCost * 0.85 + 0.5);
            end;
        end;
        workBuild = workBuild + q * wCost;
        local wInc = w.income;
        if sobEmbargo and (w.id == "D11" or w.id == "D14") then
            wInc = math.floor(wInc * 0.75 + 0.5);
        end;
        if w.id == "D09" then
            rawIncome = rawIncome + effVillages * wInc;
        else
            rawIncome = rawIncome + q * wInc;
        end;
    end;
    if workSlotsUsed > seat.workSlots then
        table.insert(avisos, "Slots de Obra excedidos (" .. tostring(workSlotsUsed) .. "/" .. tostring(seat.workSlots) .. ")!");
    end;
    if qtdD12 > 0 and qtdG10 == 0 then
        table.insert(avisos, "D12 Forja pede Mestre Ferreiro G10 p/ -20% equip.");
    end;

    local qtdD10 = math.max(0, math.floor(num(sheet.qtd_D10, 0)));
    local qtdD11 = math.max(0, math.floor(num(sheet.qtd_D11, 0)));
    local qtdD14 = math.max(0, math.floor(num(sheet.qtd_D14, 0)));
    local qtdD15 = math.max(0, math.floor(num(sheet.qtd_D15, 0)));
    if effVillages > 0 and qtdD10 > 0 then
        rawIncome = rawIncome + 15 * qtdD10;
    end;
    if usarBonusFeudo then
        if (feudoId == "L02" or feudoId == "L09" or feudoId == "L21") and qtdD14 > 0 then
            rawIncome = rawIncome + 15 * qtdD14;
        elseif feudoId == "L03" and effVillages > 0 then
            rawIncome = rawIncome + 15;
        elseif feudoId == "L05" and qtdD14 > 0 then
            rawIncome = rawIncome + 10;
        elseif feudoId == "L07" and temForjaAtiva then
            rawIncome = rawIncome + 20;
        elseif (feudoId == "L12" or feudoId == "L16") and (qtdD11 > 0 or qtdD14 > 0) then
            rawIncome = rawIncome + 20;
        elseif feudoId == "L20" and qtdD13 > 0 then
            rawIncome = rawIncome + 20;
        elseif feudoId == "L22" and (qtdD12 > 0 or qtdD15 > 0) then
            rawIncome = rawIncome + 25;
        end;
    end;
    if sobEmbargo then
        table.insert(avisos, "EMBARGO VIZINHO ATIVO (-25% em D11/D14 e +20% custo de obras)!");
    end;
    local rendaExtra = num(sheet.rendaExtraManual, 0);
    local totalIncome = math.floor((rawIncome + rendaExtra) * (temGestao10 and 1.10 or 1.0) + 0.5);

    local embargoBuildMult = sobEmbargo and 1.20 or 1.0;
    local worksAndDefCost = math.floor((defBuild + workBuild) * (temPedreira and 0.85 or 1.0) * embargoBuildMult + 0.5);

    local troopCount = 0;
    local hireCost = 0;
    local troopWages = 0;
    local staffWages = 0;
    local rawPower = 0;

    for i = 1, #UNITS do
        local u = UNITS[i];
        local q = math.max(0, math.floor(num(sheet["qtd_" .. u.id], 0)));
        if u.troop then
            troopCount = troopCount + q;
            local uHire = temForjaAtiva and math.floor(u.hire * 0.80 + 0.5) or u.hire;
            if usarBonusFeudo and feudoId == "L04" and (u.id == "G02" or u.id == "G04") then
                uHire = math.floor(uHire * 0.85 + 0.5);
            end;
            hireCost = hireCost + q * uHire;
            local uWage = (u.mounted and temCoudelaria) and math.max(0, u.wage - 10) or u.wage;
            if usarBonusFeudo and feudoId == "L15" and u.mounted then
                uWage = math.max(0, uWage - 5);
            end;
            troopWages = troopWages + q * uWage;
            local uPow = u.power;
            if usarBonusFeudo and feudoId == "L05" and (u.id == "G02" or u.id == "G03") then
                uPow = uPow + 0.5;
            end;
            rawPower = rawPower + q * uPow;
        else
            hireCost = hireCost + q * u.hire;
            local sWage = u.wage;
            if usarBonusFeudo then
                if feudoId == "L01" and (u.id == "G11" or u.id == "G12") then sWage = math.floor(sWage * 0.90 + 0.5);
                elseif feudoId == "L10" and u.id == "G13" then sWage = math.floor(sWage * 0.70 + 0.5);
                elseif feudoId == "L18" and u.id == "G14" then sWage = math.floor(sWage * 0.75 + 0.5);
                end;
            end;
            staffWages = staffWages + q * sWage;
        end;
    end;

    if troopCount > seat.maxG then
        table.insert(avisos, "Guarnicao acima do alojamento maximo (" .. tostring(troopCount) .. "/" .. tostring(seat.maxG) .. ")!");
    end;

    if effVillages > 0 and troopCount > 0 then
        local ratio = math.min(1.0, (effVillages * 25.0) / troopCount);
        troopWages = math.floor(troopWages * (1.0 - 0.15 * ratio) + 0.5);
    end;

    local masonDisc = (seat.cost >= 8000) and (math.min(3, qtdG09) * 5) or 0;
    local wallMaint = math.max(10, seat.maint - masonDisc) + defMaint;
    local despesaExtra = num(sheet.despesaExtraManual, 0);
    local totalExpense = wallMaint + troopWages + staffWages + despesaExtra;
    local netBeforeTax = totalIncome - totalExpense;
    local dizimo = 0;
    if sheet.feudoTributario == true and netBeforeTax > 0 then
        dizimo = math.floor(netBeforeTax * 0.10 + 0.5);
    end;
    local netMonthly = netBeforeTax - dizimo;
    local totalInitial = seatCost + worksAndDefCost + hireCost;

    local workerGroups = math.min(2, math.floor(qtdG08 / 5));
    local baseMonths = isRuin and (seat.months * 0.5) or seat.months;
    local buildMonths = math.max(0.5, math.floor(baseMonths * (1.0 - 0.10 * workerGroups) * 10 + 0.5) / 10.0);

    local defPower = math.floor(rawPower * (temMestreArmas and 1.10 or 1.0) * 10 + 0.5) / 10.0;
    local hpMax = seat.hp + extraHP;
    local leBase = seat.le;
    local temD02 = (math.floor(num(sheet.qtd_D02, 0)) > 0);
    local siegeDaysMax = ((math.floor(num(sheet.qtd_D07, 0)) > 0) or (seatId == "F06")) and 60 or 30;

    local atraso = math.max(0, math.min(3, math.floor(num(sheet.mesesAtrasoSoldo, 0))));
    local feudoMoral = (usarBonusFeudo and (feudoId == "L04" or feudoId == "L17")) and 1 or 0;
    local moralBase = (temMestreArmas and 1 or 0) + feudoMoral + num(sheet.moralBonusExtra, 0) - (atraso >= 1 and (atraso * 2) or 0);

    return {
        seat = seat,
        feudoId = feudoId,
        feudoInfo = feudoInfo,
        usarBonusFeudo = usarBonusFeudo,
        isRuin = isRuin,
        seatCost = seatCost,
        worksAndDefCost = worksAndDefCost,
        hireCost = hireCost,
        totalInitial = totalInitial,
        buildMonths = buildMonths,
        defSlotsUsed = defSlotsUsed,
        workSlotsUsed = workSlotsUsed,
        effVillages = effVillages,
        rawVillages = rawVillages,
        troopCount = troopCount,
        wallMaint = wallMaint,
        troopWages = troopWages,
        staffWages = staffWages,
        totalIncome = totalIncome,
        totalExpense = totalExpense,
        dizimo = dizimo,
        netMonthly = netMonthly,
        defPower = defPower,
        hpMax = hpMax,
        leBase = leBase,
        lePortao = leBase + (temD02 and 2 or 0),
        siegeDaysMax = siegeDaysMax,
        moralMod = moralBase,
        atraso = atraso,
        temGestao10 = temGestao10,
        avisos = avisos
    };
end;

recalcularFeudo = function()
    if sheet == nil or sheet._calcLock then return; end;
    sheet._calcLock = true;

    local cultKey = tostring(sheet.culturaCasa or "aurora");
    local cInfo = CULTURAS[cultKey] or CULTURAS.aurora;
    sheet.culturaResumo = "Padrao: " .. cInfo.formula .. "  |  Bastardos: " .. cInfo.bastardo .. "  |  Legitimidade: " .. cInfo.legitimidade;

    local d = calcularDadosFeudo();
    local fInfo = d.feudoInfo;
    sheet.feudoCadeiaTxt = "Senhor: " .. fInfo.senhor .. "  |  Cadeia: " .. fInfo.cadeia .. "  |  Conflito: " .. fInfo.litigio;
    sheet.feudoBonusTxt = "Concessao (" .. fInfo.code .. "): " .. fInfo.bonus;
    local s = d.seat;

    sheet.investimentoTotalTxt = fmtPP(d.totalInitial) .. " (" .. fmtInt(math.floor(d.totalInitial / 10 + 0.5)) .. " PO)";
    sheet.tempoObraTxt = "Obra base: " .. tostring(d.buildMonths) .. " mes(es) | Sede: " .. fmtPP(d.seatCost);

    sheet.receitaMensalTxt = "+" .. fmtPP(d.totalIncome) .. "/mes";
    sheet.despesaMensalTxt = "-" .. fmtPP(d.totalExpense + d.dizimo) .. "/mes";
    local sinal = (d.netMonthly >= 0) and "+" or "";
    sheet.saldoLiquidoTxt = sinal .. fmtInt(d.netMonthly) .. " PP/mes";
    sheet.detalheBalancoTxt = "Muros: " .. tostring(d.wallMaint) .. " | Tropa: " .. tostring(d.troopWages) .. " | Corte: " .. tostring(d.staffWages) .. ((d.dizimo > 0) and (" | Tributo: " .. tostring(d.dizimo)) or "");

    sheet.integridadeMaxCalc = tostring(d.hpMax);
    if sheet.integridadeAtual == nil or tostring(sheet.integridadeAtual) == "" or num(sheet.integridadeAtual, -1) < 0 then
        sheet.integridadeAtual = tostring(d.hpMax);
    end;
    if sheet.diasCercoRestantes == nil or tostring(sheet.diasCercoRestantes) == "" then
        sheet.diasCercoRestantes = tostring(d.siegeDaysMax);
    end;

    local mSign = (d.moralMod >= 0) and "+" or "";
    sheet.resumoMilitarTopo = "Defesa " .. tostring(d.defPower) .. " | LE " .. tostring(d.leBase) .. " (Portao " .. tostring(d.lePortao) .. ") | Cerco " .. tostring(d.siegeDaysMax) .. "d | Moral " .. mSign .. tostring(d.moralMod);

    sheet.sedeResumoCard = s.porte .. "  |  Novo: " .. fmtPP(s.cost) .. "  |  Ruina (45%): " .. fmtPP(math.floor(s.cost * 0.45 + 0.5)) .. "  |  Manut. Base: " .. fmtPP(s.maint) .. "/mes  |  Guarnicao: " .. tostring(s.ideal) .. " ideal (max " .. tostring(s.maxG) .. ")  |  PV Base: " .. tostring(s.hp) .. " (LE " .. tostring(s.le) .. ")  |  Slots: " .. tostring(s.defSlots) .. " Defesa / " .. tostring(s.workSlots) .. " Obra (ate " .. tostring(s.maxVil) .. " Aldeias D09).";
    sheet.sedeBeneficioCard = "Beneficio em Mesa: " .. s.benef;

    sheet.slotsDefesaTxt = "Slots de Defesa: " .. tostring(d.defSlotsUsed) .. " / " .. tostring(s.defSlots);
    sheet.slotsObraTxt = "Slots de Obra: " .. tostring(d.workSlotsUsed) .. " / " .. tostring(s.workSlots) .. "  |  Aldeias D09: " .. tostring(d.rawVillages) .. "/" .. tostring(s.maxVil);
    sheet.efetivoTropaTxt = "Soldados: " .. tostring(d.troopCount) .. " / " .. tostring(s.ideal) .. " ideal (max " .. tostring(s.maxG) .. ")  |  Indice de Defesa: " .. tostring(d.defPower);

    local sinList = {};
    if d.temGestao10 then table.insert(sinList, "+10% Receita (Senescal/PJ)"); end;
    if d.effVillages > 0 and math.floor(num(sheet.qtd_D10, 0)) > 0 then table.insert(sinList, "+15 PP/Moinho (Aldeia+Moinho)"); end;
    if d.effVillages > 0 then table.insert(sinList, "-15% Soldo ate " .. tostring(d.effVillages * 25) .. " soldados (D09)"); end;
    if math.floor(num(sheet.qtd_D13, 0)) > 0 then table.insert(sinList, "-15% Custo Obras/Defesas (D13)"); end;
    if math.floor(num(sheet.qtd_D12, 0)) > 0 and math.floor(num(sheet.qtd_G10, 0)) > 0 then table.insert(sinList, "-20% Equip. Inicial (D12+G10)"); end;
    if math.floor(num(sheet.qtd_D16, 0)) > 0 then table.insert(sinList, "-10 PP/mes Montados (D16)"); end;
    if d.usarBonusFeudo then table.insert(sinList, "Carta Suserana " .. d.feudoId .. " Ativa"); end;
    if d.atraso >= 2 then table.insert(d.avisos, "ALERTA: 2+ meses de soldo atrasado causam desercao de 50%!"); end;

    if #d.avisos > 0 then
        sheet.barraSinergiasAvisos = "ATENCAO: " .. table.concat(d.avisos, "  |  ");
    elseif #sinList > 0 then
        sheet.barraSinergiasAvisos = "Sinergias Ativas: " .. table.concat(sinList, "  •  ");
    else
        sheet.barraSinergiasAvisos = "Dica: Contrate um Senescal (G11) para +10% em toda a Receita e arrende Aldeias (D09) para sustentar a guarnicao.";
    end;

    sheet.pluginVersaoAtual = "v" .. PLUGIN_VERSION;
    if sheet.statusAtualizacao == nil or tostring(sheet.statusAtualizacao) == "" then
        sheet.statusAtualizacao = "Clique no botao acima para checar e instalar atualizacoes automaticamente.";
    end;

    atualizarVisibilidadeBrasao();
    sheet._calcLock = false;
end;

local function ajustarQtd(code, delta, maxLim)
    if sheet == nil then return; end;
    local cur = math.max(0, math.floor(num(sheet["qtd_" .. code], 0)));
    local lim = maxLim or 99;
    if code == "D09" then
        local s = SEATS[tostring(sheet.sedeId or "F04")] or SEATS.F04;
        lim = s.maxVil;
    end;
    local nxt = math.max(0, math.min(lim, cur + delta));
    sheet["qtd_" .. code] = tostring(nxt);
    recalcularFeudo();
end;

local function verDetalhesCodigo(code)
    local item = SEATS[code] or getItemById(DEFENSES, code) or getItemById(WORKS, code) or getItemById(UNITS, code);
    if item == nil then return; end;
    if SEATS[code] ~= nil then
        showMessage(
            item.nome .. "\n" .. item.porte .. "\n\n" ..
            "Preco Novo: " .. fmtPP(item.cost) .. " (" .. fmtInt(math.floor(item.cost / 10)) .. " PO)\n" ..
            "Reforma de Ruina (45%): " .. fmtPP(math.floor(item.cost * 0.45 + 0.5)) .. " (" .. tostring(item.months / 2.0) .. " meses)\n" ..
            "Manutencao Mensal: " .. fmtPP(item.maint) .. "/mes\n" ..
            "Guarnicao: " .. tostring(item.ideal) .. " ideal / " .. tostring(item.maxG) .. " max\n" ..
            "Integridade: " .. tostring(item.hp) .. " PV  |  Limiar Estrutural (LE): " .. tostring(item.le) .. "\n" ..
            "Slots: " .. tostring(item.defSlots) .. " Defesa / " .. tostring(item.workSlots) .. " Obra (ate " .. tostring(item.maxVil) .. " Aldeias D09)\n\n" ..
            item.benef
        );
    else
        showMessage("CATALOGO DO FEUDO — TOMO XV\n\n" .. code .. " — " .. item.nome .. "\n\n" .. tostring(item.desc or ""));
    end;
end;

local function aplicarPreset(tipo)
    if sheet == nil then return; end;
    local todos = {"D01","D02","D03","D04","D05","D06","D07","D08","D09","D10","D11","D12","D13","D14","D15","D16","G01","G02","G03","G04","G05","G06","G07","G08","G09","G10","G11","G12","G13","G14"};
    sheet._calcLock = true;
    for i = 1, #todos do sheet["qtd_" .. todos[i]] = "0"; end;

    if tipo == "torre" then
        sheet.nomeCasa = "Casa de Specula";
        sheet.culturaCasa = "aurora";
        sheet.lemaCasa = "Vigiamos Onde a Cinza Caiu";
        sheet.statusCasa = "2";
        sheet.sedeId = "F04";
        sheet.modoAquisicao = "ruin";
        sheet.qtd_D01 = "1"; sheet.qtd_D02 = "1";
        sheet.qtd_D09 = "2"; sheet.qtd_D10 = "1"; sheet.qtd_D11 = "1";
        sheet.qtd_G01 = "4"; sheet.qtd_G02 = "4"; sheet.qtd_G03 = "4"; sheet.qtd_G11 = "1";
        sheet.integridadeAtual = "630";
        sheet.diasCercoRestantes = "30";
    elseif tipo == "solar" then
        sheet.nomeCasa = "Casa Montavalle do Sul";
        sheet.culturaCasa = "aurora";
        sheet.feudoSuseranoId = "LIVRE";
        sheet.sobEmbargoVizinho = false;
        sheet.lemaCasa = "Raiz na Pedra, Pao na Mesa";
        sheet.statusCasa = "3";
        sheet.sedeId = "F05";
        sheet.modoAquisicao = "new";
        sheet.qtd_D01 = "1"; sheet.qtd_D02 = "1"; sheet.qtd_D07 = "1";
        sheet.qtd_D09 = "3"; sheet.qtd_D10 = "1"; sheet.qtd_D11 = "1"; sheet.qtd_D12 = "1"; sheet.qtd_D14 = "1"; sheet.qtd_D15 = "1";
        sheet.qtd_G01 = "6"; sheet.qtd_G02 = "4"; sheet.qtd_G03 = "4"; sheet.qtd_G05 = "2";
        sheet.qtd_G09 = "1"; sheet.qtd_G10 = "1"; sheet.qtd_G11 = "1"; sheet.qtd_G13 = "1";
        sheet.integridadeAtual = "760";
        sheet.diasCercoRestantes = "60";
    elseif tipo == "voernock" then
        sheet.nomeCasa = "Casa Kawa-Tsurin";
        sheet.culturaCasa = "aurora";
        sheet.feudoSuseranoId = "L05";
        sheet.aplicarBonusFeudo = true;
        sheet.sobEmbargoVizinho = false;
        sheet.suseranoCasa = "Kenshin Tsurumaru (Feudo de Yoketsu -> Altavanne)";
        sheet.regiaoFeudo = "Divisa Sul do Pantano de Voernock (Z01)";
        sheet.lemaCasa = "Neblina Acima da Lamina";
        sheet.statusCasa = "3";
        sheet.sedeId = "F07";
        sheet.modoAquisicao = "ruin";
        sheet.qtd_D01 = "1"; sheet.qtd_D04 = "1";
        sheet.qtd_D09 = "2"; sheet.qtd_D14 = "1"; sheet.qtd_D15 = "1";
        sheet.qtd_G01 = "4"; sheet.qtd_G02 = "4"; sheet.qtd_G03 = "6"; sheet.qtd_G11 = "1";
        sheet.integridadeAtual = "890";
        sheet.diasCercoRestantes = "30";
    end;
    if tipo == "torre" then
        sheet.feudoSuseranoId = "LIVRE";
        sheet.sobEmbargoVizinho = false;
    end;
    sheet._calcLock = false;
    recalcularFeudo();
end;

local function sortearRaizCasa(qual)
    if sheet == nil then return; end;
    local nomeCasa = tostring(sheet.nomeCasa or "Casa Nobre");
    local rolagem = Firecast.interpretarRolagem("1d8");
    local titulo = "[" .. nomeCasa .. "] " .. ((qual == "virtude") and "Virtude Historica da Casa (1d8)" or "Divida ou Ameaca Herdada (1d8)");
    local function aplicar(idx)
        local k = math.max(1, math.min(8, idx));
        if qual == "virtude" then
            sheet.virtudeCasa = VIRTUDES_1D8[k];
            return VIRTUDES_1D8[k];
        else
            sheet.dividaCasa = DIVIDAS_1D8[k];
            return DIVIDAS_1D8[k];
        end;
    end;
    local mesa = Firecast.getMesaDe(sheet);
    if mesa ~= nil and mesa.activeChat ~= nil then
        mesa.activeChat:rolarDados(rolagem, titulo,
            function(rolado)
                if rolado == nil then return; end;
                local txt = aplicar(rolado.resultado);
                mesa.activeChat:enviarMensagem("[" .. nomeCasa .. "] " .. txt);
            end);
    else
        rolagem:rolarLocalmente();
        local txt = aplicar(rolagem.resultado);
        showMessage(titulo .. "\n\n" .. txt);
    end;
end;

local function anunciarCartaFeudo()
    if sheet == nil then return; end;
    local d = calcularDadosFeudo();
    local nome = tostring(sheet.nomeCasa or "Casa Sem Nome");
    local lema = tostring(sheet.lemaCasa or "");
    local cofre = math.floor(num(sheet.cofrePP, 0));
    local sinal = (d.netMonthly >= 0) and "+" or "";
    local msg = "🏰 [CARTA DE FEUDO — " .. nome .. "]" .. ((lema ~= "") and (" (\"" .. lema .. "\")") or "") ..
        " | Suserania: " .. d.feudoInfo.nome ..
        " | Sede: " .. d.seat.nome .. (d.isRuin and " [Ruina Reerguida]" or " [Construcao Nova]") ..
        " | Investimento: " .. fmtPP(d.totalInitial) ..
        " | Balanco Mensal: Receita +" .. fmtPP(d.totalIncome) .. ", Despesa -" .. fmtPP(d.totalExpense + d.dizimo) ..
        " => Saldo " .. sinal .. fmtInt(d.netMonthly) .. " PP/mes" ..
        " | Cofre Atual: " .. fmtPP(cofre) ..
        " | Guarnicao: " .. tostring(d.troopCount) .. " soldados (Defesa " .. tostring(d.defPower) .. ") | PV Fortaleza: " .. tostring(sheet.integridadeAtual or d.hpMax) .. "/" .. tostring(d.hpMax) .. " (LE " .. tostring(d.leBase) .. ").";
    enviarChatOuMsg(msg);
end;

local function virarMesFeudo()
    if sheet == nil then return; end;
    local d = calcularDadosFeudo();
    local nome = tostring(sheet.nomeCasa or "Casa Nobre");
    local cofreAnt = math.floor(num(sheet.cofrePP, 0));
    local cofreNovo = cofreAnt + d.netMonthly;
    local mesAtual = math.max(1, math.floor(num(sheet.mesCampanha, 1)));

    local avisoSoldo = "";
    if cofreNovo < 0 then
        local atr = math.min(3, math.max(0, math.floor(num(sheet.mesesAtrasoSoldo, 0))) + 1);
        sheet.mesesAtrasoSoldo = tostring(atr);
        cofreNovo = 0;
        if atr == 1 then
            avisoSoldo = " ⚠️ COFRE VAZIO (1o mes de atraso: -2 na Moral da guarnicao)!";
        else
            avisoSoldo = " 🚨 COFRE FALIDO (" .. tostring(atr) .. " meses de atraso: metade das tropas pagas deserta e oficinas param)!";
        end;
    else
        if math.floor(num(sheet.mesesAtrasoSoldo, 0)) > 0 then
            sheet.mesesAtrasoSoldo = "0";
            avisoSoldo = " ✅ Soldos em dia regularizados!";
        end;
    end;

    sheet.cofrePP = tostring(cofreNovo);
    sheet.mesCampanha = tostring(mesAtual + 1);
    recalcularFeudo();

    local sinal = (d.netMonthly >= 0) and "+" or "";
    enviarChatOuMsg(
        "📅 [BALANCO DO MES #" .. tostring(mesAtual) .. " — " .. nome .. "] " ..
        "Receita: +" .. fmtPP(d.totalIncome) .. " | Manutencao & Folha: -" .. fmtPP(d.totalExpense + d.dizimo) ..
        " | Saldo: " .. sinal .. fmtInt(d.netMonthly) .. " PP | Cofre da Casa: " .. fmtPP(cofreAnt) .. " -> " .. fmtPP(cofreNovo) .. "." .. avisoSoldo
    );
end;

local function rolarEventoSazonal()
    if sheet == nil then return; end;
    local nome = tostring(sheet.nomeCasa or "Casa Nobre");
    local rolagem = Firecast.interpretarRolagem("1d12");
    local titulo = "[" .. nome .. "] Evento Sazonal de Dominio (1d12)";
    local function resolver(v)
        local ev = nil;
        if v <= 5 then ev = EVENTOS_1D12[v];
        elseif v <= 7 then ev = EVENTOS_1D12[6];
        else ev = EVENTOS_1D12[v - 1]; end;
        sheet.ultimoEventoSazonal = ev.tit .. " — " .. ev.ef;
        return ev;
    end;
    local mesa = Firecast.getMesaDe(sheet);
    if mesa ~= nil and mesa.activeChat ~= nil then
        mesa.activeChat:rolarDados(rolagem, titulo,
            function(rolado)
                if rolado == nil then return; end;
                local ev = resolver(rolado.resultado);
                mesa.activeChat:enviarMensagem("🍂 [" .. ev.tit .. "] " .. ev.ef);
            end);
    else
        rolagem:rolarLocalmente();
        local ev = resolver(rolagem.resultado);
        showMessage(titulo .. "\n\n" .. ev.tit .. "\n" .. ev.ef);
    end;
end;

local function rolarStatusCasa()
    if sheet == nil then return; end;
    local st = math.floor(num(sheet.statusCasa, 1));
    local modExtra = math.floor(num(sheet.modSocialLider, 0));
    local tot = st + modExtra;
    local expr = (tot >= 0) and ("1d20 + " .. tostring(tot)) or ("1d20 - " .. tostring(math.abs(tot)));
    rolarExpressaoChat(expr, "[" .. tostring(sheet.nomeCasa or "Casa Nobre") .. "] Teste de Status & Prestigio da Casa (Status " .. tostring(st) .. ")", 0, "", "");
end;


local function verFichaFeudoSuserano()
    if sheet == nil then return; end;
    local fk = tostring(sheet.feudoSuseranoId or "LIVRE");
    local f = FEUDOS_DB[fk] or FEUDOS_DB.LIVRE;
    showMessage(
        "ATLAS FEUDAL DE ALENIA — TOMO XVII\n\n" ..
        f.nome .. "\n\n" ..
        "Senhor Feudal: " .. f.senhor .. "\n" ..
        "Cadeia ate Altavanne: " .. f.cadeia .. "\n" ..
        "Sub-feudos / Litigio Ativo: " .. f.litigio .. "\n\n" ..
        "Concessao Regional (Tomo XV/XVII):\n" .. f.bonus
    );
end;

local function anunciarVassalagemChat()
    if sheet == nil then return; end;
    local fk = tostring(sheet.feudoSuseranoId or "LIVRE");
    local f = FEUDOS_DB[fk] or FEUDOS_DB.LIVRE;
    local nome = tostring(sheet.nomeCasa or "Casa Nobre");
    local emb = (sheet.sobEmbargoVizinho == true) and " | ⚠️ SOB EMBARGO VIZINHO!" or "";
    enviarChatOuMsg(
        "👑 [CHANCELARIA & SUSERANIA — " .. nome .. "] Dominio vinculado a " .. f.nome ..
        " | Senhor: " .. f.senhor .. " | Cadeia: " .. f.cadeia ..
        " | Frente Politica: " .. f.litigio .. emb
    );
end;

local function rolarIntrigaFeudal()
    if sheet == nil then return; end;
    local nome = tostring(sheet.nomeCasa or "Casa Nobre");
    local fk = tostring(sheet.feudoSuseranoId or "LIVRE");
    local f = FEUDOS_DB[fk] or FEUDOS_DB.LIVRE;
    local rolagem = Firecast.interpretarRolagem("1d12");
    local titulo = "[" .. nome .. " • " .. f.code .. "] Intriga Feudal & Politicagem (1d12 — Tomo XVII)";
    local function resolverIntriga(v)
        local k = math.max(1, math.min(12, v));
        local it = INTRIGAS_1D12[k];
        sheet.ultimoEventoSazonal = "[INTRIGA " .. it.tit .. "] " .. it.ef;
        return it;
    end;
    local mesa = Firecast.getMesaDe(sheet);
    if mesa ~= nil and mesa.activeChat ~= nil then
        mesa.activeChat:rolarDados(rolagem, titulo,
            function(rolado)
                if rolado == nil then return; end;
                local it = resolverIntriga(rolado.resultado);
                mesa.activeChat:enviarMensagem("🗡️ [INTRIGA FEUDAL: " .. it.tit .. "] " .. it.ef);
            end);
    else
        rolagem:rolarLocalmente();
        local it = resolverIntriga(rolagem.resultado);
        showMessage(titulo .. "\n\n" .. it.tit .. "\n" .. it.ef);
    end;
end;

local function rolarContraespionagem()
    if sheet == nil then return; end;
    local temG14 = (math.floor(num(sheet.qtd_G14, 0)) > 0);
    local bonusG14 = temG14 and 3 or 0;
    local fk = tostring(sheet.feudoSuseranoId or "LIVRE");
    local bonusFeudoEsp = ((sheet.aplicarBonusFeudo ~= false) and (fk == "L13" or fk == "L18")) and 2 or 0;
    local mesaBonus = (tostring(sheet.virtudeCasa or ""):find("Mesa da Anfitria") ~= nil) and 2 or 0;
    local modBase = math.floor(num(sheet.modEspionagemCasa, 2)) + bonusG14 + bonusFeudoEsp + mesaBonus;
    local expr = (modBase >= 0) and ("1d20 + " .. tostring(modBase)) or ("1d20 - " .. tostring(math.abs(modBase)));
    rolarExpressaoChat(
        expr,
        "[" .. tostring(sheet.nomeCasa or "Casa Nobre") .. "] Contraespionagem da Casa" .. (temG14 and " [Mestre de Sussurros G14 +3]" or ""),
        14,
        "Infiltradores, subornos ou sabotagens descobertos a tempo!",
        "A conspiracao age nas sombras sem ser detectada."
    );
end;

local function rolarTropa(code)
    if sheet == nil then return; end;
    local u = getItemById(UNITS, code);
    if u == nil or not u.troop then return; end;
    local q = math.floor(num(sheet["qtd_" .. code], 0));
    local nome = tostring(sheet.nomeCasa or "Casa Nobre");
    local exprAtk = "1d20 + " .. tostring(u.atk);
    rolarExpressaoChat(
        exprAtk,
        "[" .. nome .. "] Ataque de " .. u.nome .. " (Efetivo: " .. tostring(q) .. ") — Dano base: " .. u.dmg,
        0,
        "Se acertar, cause " .. u.dmg .. " de dano!",
        ""
    );
end;

local function dispararEngenhoMuralha(qual)
    if sheet == nil then return; end;
    local nome = tostring(sheet.nomeCasa or "Casa Nobre");
    local modPj = math.floor(num(sheet.modCercoEngenho, 5));
    local exprAtk = (modPj >= 0) and ("1d20 + " .. tostring(modPj)) or ("1d20 - " .. tostring(math.abs(modPj)));
    if qual == "balista" then
        rolarExpressaoChat(exprAtk, "[" .. nome .. "] Disparo de Balista de Muralha D05 (Alcance 180m)", 0, "Em acerto, role 3d10 perfurante (ignora 5 pontos de LE de escudos/mantletes)!", "");
        rolarExpressaoChat("3d10", "[" .. nome .. "] Dano da Balista de Muralha (D05)", 0, "Ignora 5 pontos de Limiar Estrutural (LE)!", "");
    else
        rolarExpressaoChat(exprAtk, "[" .. nome .. "] Disparo de Trabuco de Contrapeso D06 (Alcance 300m)", 0, "Em acerto, role 6d10 contundente (ignora 8 pontos de LE; recarga 2 turnos)!", "");
        rolarExpressaoChat("6d10", "[" .. nome .. "] Dano do Trabuco Fixo (D06)", 0, "Ignora 8 pontos de Limiar Estrutural (LE) contra torres/arietes!", "");
    end;
end;

local function aplicarDanoCerco()
    if sheet == nil then return; end;
    local d = calcularDadosFeudo();
    local bruto = math.max(0, math.floor(num(sheet.danoCercoEntrada, 0)));
    if bruto <= 0 then
        showMessage("Informe o dano bruto do engenho inimigo antes de aplicar.");
        return;
    end;
    local noPortao = (sheet.ataqueNoPortao == true);
    local leUsado = noPortao and d.lePortao or d.leBase;
    local efetivo = math.max(0, bruto - leUsado);
    local pvAnt = math.max(0, math.floor(num(sheet.integridadeAtual, d.hpMax)));
    local pvNovo = math.max(0, pvAnt - efetivo);
    sheet.integridadeAtual = tostring(pvNovo);

    local statusMuro = "";
    if pvNovo == 0 then
        statusMuro = " 🚨 BRECHA ABERTA NA FORTIFICACAO!";
    elseif pvNovo <= math.floor(d.hpMax * 0.5) then
        statusMuro = " ⚠️ Muros abaixo de 50% (Brecha Parcial aberta para assalto)!";
    end;

    enviarChatOuMsg(
        "💥 [CERCO — " .. tostring(sheet.nomeCasa or "Fortaleza") .. "] Impacto bruto: " .. tostring(bruto) ..
        " - Limiar Estrutural (LE " .. tostring(leUsado) .. (noPortao and " no Portao" or "") .. ") = " ..
        tostring(efetivo) .. " PV de dano estrutural! Integridade: " .. tostring(pvAnt) .. " -> " .. tostring(pvNovo) .. "/" .. tostring(d.hpMax) .. " PV." .. statusMuro
    );
end;

local function repararFortalezaMax()
    if sheet == nil then return; end;
    local d = calcularDadosFeudo();
    sheet.integridadeAtual = tostring(d.hpMax);
    sheet.diasCercoRestantes = tostring(d.siegeDaysMax);
    enviarChatOuMsg("🔨 [" .. tostring(sheet.nomeCasa or "Fortaleza") .. "] Muralhas reparadas (" .. tostring(d.hpMax) .. " PV) e paiois reabastecidos (" .. tostring(d.siegeDaysMax) .. " dias de cerco).");
end;

local function consumirDiaCerco()
    if sheet == nil then return; end;
    local d = calcularDadosFeudo();
    local dias = math.max(0, math.floor(num(sheet.diasCercoRestantes, d.siegeDaysMax)) - 1);
    sheet.diasCercoRestantes = tostring(dias);
    local alerta = (dias == 0) and " 🚨 SUPRIMENTOS ESGOTADOS! Guarnicao sofre fome e testes de Exaustao diarios!" or "";
    enviarChatOuMsg("⏳ [CERCO — " .. tostring(sheet.nomeCasa or "Fortaleza") .. "] Mais um dia de sitio suportado. Suprimentos restantes: " .. tostring(dias) .. "/" .. tostring(d.siegeDaysMax) .. " dias." .. alerta);
end;

local function rolarPostoCerco(posto)
    if sheet == nil then return; end;
    local d = calcularDadosFeudo();
    local nome = tostring(sheet.nomeCasa or "Casa Nobre");
    if posto == 1 then
        local mod = math.floor(num(sheet.modCercoComandante, 4)) + d.moralMod;
        local expr = (mod >= 0) and ("1d20 + " .. tostring(mod)) or ("1d20 - " .. tostring(math.abs(mod)));
        rolarExpressaoChat(expr, "[POSTO 1: COMANDANTE DA MURALHA — " .. nome .. "]", 14, "A linha segura firme! Guarnicao recebe +2 contra medo/debandada e +1 nos tiros desta rodada!", "A pressao inimiga abala os defensores da muralha.");
    elseif posto == 3 then
        local mod = math.floor(num(sheet.modCercoSortida, 5));
        local temD08 = (math.floor(num(sheet.qtd_D08, 0)) > 0);
        local bonusPot = temD08 and 2 or 0;
        local tot = mod + bonusPot;
        local expr = (tot >= 0) and ("1d20 + " .. tostring(tot)) or ("1d20 - " .. tostring(math.abs(tot)));
        rolarExpressaoChat(expr, "[POSTO 3: LIDER DE SORTIDA NOTURNA — " .. nome .. "]" .. (temD08 and " [Poterna D08 +2]" or ""), 15, "Sortida surpresa alcanca os engenhos inimigos antes da guarda reagir!", "Sentinela inimiga percebe a movimentacao no escuro!");
    elseif posto == 4 then
        local mod = math.floor(num(sheet.modCercoIntendente, 4)) + ((math.floor(num(sheet.qtd_D15, 0)) > 0) and 2 or 0);
        local expr = (mod >= 0) and ("1d20 + " .. tostring(mod)) or ("1d20 - " .. tostring(math.abs(mod)));
        rolarExpressaoChat(expr, "[POSTO 4: INTENDENTE DA PRACA — " .. nome .. "]", 14, "Incendios contidos, feridos estabilizados e panico evitado no patio interno!", "Fumaca, feridos ou panico sobrecarregam o patio interno.");
    end;
end;

local function compararVersoes(vA, vB)
    local function splitNums(s)
        local t = {};
        for n in tostring(s or "0"):gmatch("%d+") do table.insert(t, tonumber(n) or 0); end;
        return t;
    end;
    local a = splitNums(vA);
    local b = splitNums(vB);
    local m = math.max(#a, #b);
    for i = 1, m do
        local na = a[i] or 0;
        local nb = b[i] or 0;
        if na > nb then return 1; end;
        if na < nb then return -1; end;
    end;
    return 0;
end;

local function getVersaoInstalada()
    local ver = PLUGIN_VERSION;
    if PluginsMod ~= nil and type(PluginsMod.getInstalledPlugins) == "function" then
        local ok, lista = pcall(PluginsMod.getInstalledPlugins);
        if ok and type(lista) == "table" then
            for i = 1, #lista do
                local it = lista[i];
                if it ~= nil and it.moduleId == PLUGIN_MODULE_ID and it.version ~= nil and tostring(it.version) ~= "" then
                    ver = tostring(it.version);
                    break;
                end;
            end;
        end;
    end;
    return ver;
end;

local function abrirLinkExterno(url)
    if GUI ~= nil and type(GUI.openInBrowser) == "function" then
        GUI.openInBrowser(url);
    else
        showMessage("Acesse no navegador:\n" .. tostring(url));
    end;
end;

local function verificarEAtualizarPlugin(forcarReinstalacao)
    if sheet == nil then return; end;
    local verLocal = getVersaoInstalada();
    sheet.pluginVersaoAtual = "v" .. verLocal;

    if InternetMod == nil or type(InternetMod.download) ~= "function" then
        sheet.statusAtualizacao = "Modulo de internet indisponivel neste ambiente.";
        showMessage("Baixe a versao mais recente na Biblioteca Online:\n" .. BIBLIOTECA_URL);
        return;
    end;

    sheet.statusAtualizacao = "Verificando atualizacoes oficiais...";
    local urlCheck = PLUGIN_RPK_URL .. "?t=" .. tostring(os.time());

    InternetMod.download(
        urlCheck,
        function(stream, contentType)
            if stream == nil then
                sheet.statusAtualizacao = "Falha: resposta vazia do servidor.";
                return;
            end;
            local details = nil;
            if PluginsMod ~= nil and type(PluginsMod.getRPKDetails) == "function" then
                local okDet, det = pcall(PluginsMod.getRPKDetails, stream);
                if okDet then details = det; end;
            end;
            if details == nil or details.version == nil then
                sheet.statusAtualizacao = "Pacote remoto indisponivel no momento.";
                return;
            end;
            local verRemota = tostring(details.version);
            local cmp = compararVersoes(verRemota, verLocal);

            local function instalarAgora()
                if PluginsMod == nil or type(PluginsMod.installPlugin) ~= "function" then
                    abrirLinkExterno(BIBLIOTECA_URL);
                    return;
                end;
                pcall(function() stream.position = 0; end);
                local okCall, okInst = pcall(PluginsMod.installPlugin, stream, not forcarReinstalacao);
                if okCall and okInst then
                    sheet.pluginVersaoAtual = "v" .. verRemota .. " (reabra)";
                    sheet.statusAtualizacao = "Atualizado para v" .. verRemota .. "! Feche e reabra a ficha.";
                    showMessage("Ficha de Casa Nobre atualizada para v" .. verRemota .. "!\nFeche e reabra a janela da ficha para aplicar.");
                else
                    sheet.statusAtualizacao = "Falha ao instalar automaticamente.";
                end;
            end;

            if cmp > 0 then
                if DialogsMod ~= nil and type(DialogsMod.confirmYesNo) == "function" then
                    DialogsMod.confirmYesNo(
                        "Nova versao v" .. verRemota .. " disponivel (atual: v" .. verLocal .. "). Deseja atualizar agora?",
                        function(sim) if sim then instalarAgora(); end; end
                    );
                else
                    instalarAgora();
                end;
            elseif forcarReinstalacao then
                instalarAgora();
            else
                sheet.statusAtualizacao = "Sua ficha ja esta na versao mais recente (v" .. verLocal .. ").";
                showMessage("Tudo certo! Sua Ficha de Casa Nobre & Feudo ja esta na versao mais recente (v" .. verLocal .. ").");
            end;
        end,
        function(err)
            sheet.statusAtualizacao = "Erro ao verificar atualizacoes: " .. tostring(err);
        end,
        function(down, tot)
            if tot ~= nil and tot > 0 then
                sheet.statusAtualizacao = "Baixando atualizacao... (" .. tostring(math.min(100, math.floor((down / tot) * 100))) .. "%)";
            end;
        end
    );
end;
"""


def build_lfm():
    cultura_items = "{'1. Reino de Aurora (Feudal)', '2. Liga de Corallis (Patricia)', '3. Despotado de Kalis (Ferro)', '4. Confederacao de Gaddra (Oasis)', '5. Fronteiras Silvanas (Pacto)'}"
    cultura_values = "{'aurora', 'corallis', 'kalis', 'gaddra', 'silvana'}"

    origem_items = "{'Casa Nova Erguida por Feitos (Carta/Foral)', 'Linhagem Antiga em Declinio (Heranca Disputada)', ' Companhia Mercante / Cla Fronteirico'}"
    origem_values = "{'nova_feitos', 'antiga_declinio', 'companhia_cla'}"

    sede_items = (
        "{'F01 - Entreposto de Estrada (Novo 1.800 / Ruina 810 PP)', "
        "'F02 - Solar Urbano Patricio (Novo 3.500 / Ruina 1.575 PP)', "
        "'F03 - Mota e Palicada (Novo 4.800 / Ruina 2.160 PP)', "
        "'F04 - Torre de Vigia Specula (Novo 8.000 / Ruina 3.600 PP)', "
        "'F05 - Solar Rural Fortificado (Novo 14.000 / Ruina 6.300 PP)', "
        "'F06 - Cacer de Oasis Gaddra (Novo 16.000 / Ruina 7.200 PP)', "
        "'F07 - Forte Costeiro e Corrente (Novo 18.500 / Ruina 8.325 PP)', "
        "'F08 - Castelo de Cantaria (Novo 36.000 / Ruina 16.200 PP)', "
        "'F09 - Fortaleza de Escarpa (Novo 65.000 / Ruina 29.250 PP)', "
        "'F10 - Cidadela de Grande Casa (Novo 110.000 / Ruina 49.500 PP)'}"
    )
    sede_values = "{'F01', 'F02', 'F03', 'F04', 'F05', 'F06', 'F07', 'F08', 'F09', 'F10'}"

    modo_items = "{'Reerguer Ruina Concedida (45% Custo | 1/2 Tempo)', 'Construcao Nova do Zero (100% Custo)'}"
    modo_values = "{'ruin', 'new'}"

    feudo_pairs = [
        ("LIVRE", "Fronteira Livre / Sem Feudo Suserano Fixo (Base Tomo XV)"),
        ("L01", "L01 - Altavanne & Pontauria [Coroa Imperial — Casa Valerion]"),
        ("L02", "L02 - Feudo de Merlinport [Aurora -> Altavanne | Marcus Scutauria]"),
        ("L03", "L03 - Feudo de Dahrma + Lavroga [Aurora -> Altavanne | Lorian Montavalle]"),
        ("L04", "L04 - Feudo de Vaarsa [Aurora -> Altavanne | Marechal Leonastis]"),
        ("L05", "L05 - Feudo de Yoketsu [Aurora -> Altavanne | Kenshin Tsurumaru]"),
        ("L06", "L06 - Feudo de Altrax [Aurora -> Altavanne | Aurelia d Altrax]"),
        ("L07", "L07 - Feudo de Aeraneas [Aurora -> Altavanne | Aurelian Ferraris]"),
        ("L08", "L08 - Feudo das Cidades Suspensas [Aurora -> Altavanne | Aerwen]"),
        ("L09", "L09 - Alineus [Corallis — Sede Regente Corardo della Rocca -> Altavanne]"),
        ("L10", "L10 - Baldbella [Corallis -> Regente della Rocca -> Altavanne]"),
        ("L11", "L11 - Stoneforge [Corallis -> Regente della Rocca -> Altavanne]"),
        ("L12", "L12 - Biemont & Portocala [Corallis -> Regente della Rocca -> Altavanne]"),
        ("L13", "L13 - Sellene & Claramar [Corallis -> Regente / Altavanne]"),
        ("L14", "L14 - Naasar & Bayd [Gaddra — Sede Regente Qasir Zaharid -> Altavanne]"),
        ("L15", "L15 - OX [Gaddra -> Regente Qasir Zaharid -> Altavanne]"),
        ("L16", "L16 - Qal-Zahar & Suq-Ramad [Gaddra -> Regente Qasir -> Altavanne]"),
        ("L17", "L17 - Marca de Vargheim [Gaddra -> Regente Qasir -> Altavanne]"),
        ("L18", "L18 - Cidadela de Kalgard [Kalis — Sede Despota Grimrik -> Altavanne]"),
        ("L19", "L19 - Kragstad [Kalis -> Despota Grimrik -> Altavanne]"),
        ("L20", "L20 - Drakenhall [Kalis -> Despota Grimrik -> Altavanne]"),
        ("L21", "L21 - Dobalbek [Kalis -> Despota Grimrik -> Altavanne]"),
        ("L22", "L22 - Fugong & Kalima [Kalis -> Despota Grimrik -> Altavanne]"),
    ]
    feudo_values = lua_items_str([p[0] for p in feudo_pairs])
    feudo_items = lua_items_str([p[1] for p in feudo_pairs])

    def_max_map = {"D01": 1, "D02": 1, "D03": 1, "D04": 1, "D05": 3, "D06": 3, "D07": 1, "D08": 1}
    work_max_map = {"D09": 6, "D10": 2, "D11": 2, "D12": 1, "D13": 2, "D14": 2, "D15": 1, "D16": 1}

    def_rows = []
    for idx, (cid, cname, csub) in enumerate(DEFENSES_UI):
        ty = 64 + idx * 54
        mx = def_max_map[cid]
        def_rows.append(f'''
                            <rectangle left="10" top="{ty}" width="492" height="48" color="{BG_CARD_ALT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                                <label left="8" top="4" width="326" height="20" text="{xml_attr(cname)}" fontColor="{TEXT_MAIN}" fontSize="13" fontStyle="bold"/>
                                <label left="8" top="24" width="326" height="18" text="{xml_attr(csub)}" fontColor="{TEXT_MUTED}" fontSize="11"/>
                                <button left="338" top="9" width="30" height="30" text="-" fontSize="15">
                                    <event name="onClick"><![CDATA[ajustarQtd("{cid}", -1, {mx});]]></event>
                                </button>
                                <edit left="372" top="9" width="42" height="30" field="qtd_{cid}" type="number" horzTextAlign="center" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold"/>
                                <button left="418" top="9" width="30" height="30" text="+" fontSize="15">
                                    <event name="onClick"><![CDATA[ajustarQtd("{cid}", 1, {mx});]]></event>
                                </button>
                                <button left="454" top="9" width="30" height="30" text="?" fontSize="13">
                                    <event name="onClick"><![CDATA[verDetalhesCodigo("{cid}");]]></event>
                                </button>
                            </rectangle>''')

    work_rows = []
    for idx, (cid, cname, csub) in enumerate(WORKS_UI):
        ty = 64 + idx * 54
        mx = work_max_map[cid]
        work_rows.append(f'''
                            <rectangle left="10" top="{ty}" width="492" height="48" color="{BG_CARD_ALT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                                <label left="8" top="4" width="326" height="20" text="{xml_attr(cname)}" fontColor="{TEXT_MAIN}" fontSize="13" fontStyle="bold"/>
                                <label left="8" top="24" width="326" height="18" text="{xml_attr(csub)}" fontColor="{TEXT_GREEN}" fontSize="11"/>
                                <button left="338" top="9" width="30" height="30" text="-" fontSize="15">
                                    <event name="onClick"><![CDATA[ajustarQtd("{cid}", -1, {mx});]]></event>
                                </button>
                                <edit left="372" top="9" width="42" height="30" field="qtd_{cid}" type="number" horzTextAlign="center" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold"/>
                                <button left="418" top="9" width="30" height="30" text="+" fontSize="15">
                                    <event name="onClick"><![CDATA[ajustarQtd("{cid}", 1, {mx});]]></event>
                                </button>
                                <button left="454" top="9" width="30" height="30" text="?" fontSize="13">
                                    <event name="onClick"><![CDATA[verDetalhesCodigo("{cid}");]]></event>
                                </button>
                            </rectangle>''')

    troop_rows = []
    for idx, (cid, cname, csub) in enumerate(TROOPS_UI):
        ty = 64 + idx * 58
        troop_rows.append(f'''
                            <rectangle left="10" top="{ty}" width="492" height="52" color="{BG_CARD_ALT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                                <label left="8" top="4" width="276" height="20" text="{xml_attr(cname)}" fontColor="{TEXT_MAIN}" fontSize="13" fontStyle="bold"/>
                                <label left="8" top="25" width="276" height="20" text="{xml_attr(csub)}" fontColor="{TEXT_MUTED}" fontSize="10"/>
                                <button left="288" top="11" width="28" height="30" text="-" fontSize="15">
                                    <event name="onClick"><![CDATA[ajustarQtd("{cid}", -1, 500);]]></event>
                                </button>
                                <edit left="319" top="11" width="44" height="30" field="qtd_{cid}" type="number" horzTextAlign="center" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold"/>
                                <button left="366" top="11" width="28" height="30" text="+" fontSize="15">
                                    <event name="onClick"><![CDATA[ajustarQtd("{cid}", 1, 500);]]></event>
                                </button>
                                <button left="398" top="11" width="56" height="30" text="Atacar" fontSize="11">
                                    <event name="onClick"><![CDATA[rolarTropa("{cid}");]]></event>
                                </button>
                                <button left="458" top="11" width="28" height="30" text="?" fontSize="12">
                                    <event name="onClick"><![CDATA[verDetalhesCodigo("{cid}");]]></event>
                                </button>
                            </rectangle>''')

    staff_rows = []
    for idx, (cid, cname, csub) in enumerate(STAFF_UI):
        ty = 64 + idx * 58
        extra_btn = ""
        if cid == "G14":
            extra_btn = f'''
                                <button left="398" top="11" width="56" height="30" text="Rolar" fontSize="11">
                                    <event name="onClick"><![CDATA[rolarContraespionagem();]]></event>
                                </button>
                                <button left="458" top="11" width="28" height="30" text="?" fontSize="12">
                                    <event name="onClick"><![CDATA[verDetalhesCodigo("{cid}");]]></event>
                                </button>'''
        else:
            extra_btn = f'''
                                <button left="432" top="11" width="52" height="30" text="Ficha" fontSize="11">
                                    <event name="onClick"><![CDATA[verDetalhesCodigo("{cid}");]]></event>
                                </button>'''
        staff_rows.append(f'''
                            <rectangle left="10" top="{ty}" width="492" height="52" color="{BG_CARD_ALT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                                <label left="8" top="4" width="282" height="20" text="{xml_attr(cname)}" fontColor="{TEXT_MAIN}" fontSize="13" fontStyle="bold"/>
                                <label left="8" top="25" width="282" height="20" text="{xml_attr(csub)}" fontColor="{TEXT_GOLD}" fontSize="10"/>
                                <button left="294" top="11" width="28" height="30" text="-" fontSize="15">
                                    <event name="onClick"><![CDATA[ajustarQtd("{cid}", -1, 99);]]></event>
                                </button>
                                <edit left="325" top="11" width="42" height="30" field="qtd_{cid}" type="number" horzTextAlign="center" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold"/>
                                <button left="370" top="11" width="28" height="30" text="+" fontSize="15">
                                    <event name="onClick"><![CDATA[ajustarQtd("{cid}", 1, 99);]]></event>
                                </button>{extra_btn}
                            </rectangle>''')

    def_fields = [
        "nomeCasa", "lemaCasa", "chefeCasa", "culturaCasa", "statusCasa", "modSocialLider",
        "origemCasa", "suseranoCasa", "regiaoFeudo", "sedeId", "modoAquisicao",
        "cofrePP", "mesCampanha", "mesesAtrasoSoldo", "rendaExtraManual", "despesaExtraManual",
        "pjAdminMes", "feudoTributario", "feudoSuseranoId", "aplicarBonusFeudo", "sobEmbargoVizinho",
        "qtd_D01", "qtd_D02", "qtd_D03", "qtd_D04", "qtd_D05", "qtd_D06", "qtd_D07", "qtd_D08",
        "qtd_D09", "qtd_D10", "qtd_D11", "qtd_D12", "qtd_D13", "qtd_D14", "qtd_D15", "qtd_D16",
        "qtd_G01", "qtd_G02", "qtd_G03", "qtd_G04", "qtd_G05", "qtd_G06", "qtd_G07",
        "qtd_G08", "qtd_G09", "qtd_G10", "qtd_G11", "qtd_G12", "qtd_G13", "qtd_G14",
        "integridadeAtual", "diasCercoRestantes", "danoCercoEntrada", "ataqueNoPortao", "moralBonusExtra",
        "modCercoComandante", "modCercoEngenho", "modCercoSortida", "modCercoIntendente", "modEspionagemCasa",
        "virtudeCasa", "dividaCasa", "brasaoDescricao",
    ]
    def_values = [
        "Casa de Specula", "Vigiamos Onde a Cinza Caiu", "", "aurora", "2", "2",
        "nova_feitos", "Coroa de Aurora / Foral de Fronteira", "Fronteira Norte de Aurora", "F04", "ruin",
        "500", "1", "0", "0", "0",
        "false", "false", "LIVRE", "true", "false",
        "1", "1", "0", "0", "0", "0", "0", "0",
        "2", "1", "1", "0", "0", "0", "0", "0",
        "4", "4", "4", "0", "0", "0", "0",
        "0", "0", "0", "1", "0", "0", "0",
        "630", "30", "25", "false", "0",
        "4", "5", "5", "4", "2",
        "4. Veio de Agua Limpa: nascente interna purissima; imune a seca sazonal e +2 contra surtos hidricos.",
        "2. Disputa de Divisa: o senhor vizinho reivindica o moinho ou o bosque limitrofe com um foral contraditorio.",
        "Campo partido de cinza-ferro e goles, torre de prata acesa em ouro; timbre de corvo vigilante.",
    ]

    recalc_fields = [
        "culturaCasa", "sedeId", "modoAquisicao", "mesesAtrasoSoldo",
        "rendaExtraManual", "despesaExtraManual", "pjAdminMes", "feudoTributario", "feudoSuseranoId", "aplicarBonusFeudo", "sobEmbargoVizinho", "moralBonusExtra",
        "qtd_D01", "qtd_D02", "qtd_D03", "qtd_D04", "qtd_D05", "qtd_D06", "qtd_D07", "qtd_D08",
        "qtd_D09", "qtd_D10", "qtd_D11", "qtd_D12", "qtd_D13", "qtd_D14", "qtd_D15", "qtd_D16",
        "qtd_G01", "qtd_G02", "qtd_G03", "qtd_G04", "qtd_G05", "qtd_G06", "qtd_G07",
        "qtd_G08", "qtd_G09", "qtd_G10", "qtd_G11", "qtd_G12", "qtd_G13", "qtd_G14",
    ]

    lfm = f'''<?xml version="1.0" encoding="UTF-8"?>
<form name="frmAleniaCasaNobre" formType="sheetTemplate" dataType="br.com.alenia.casa_nobre.ficha" title="Alenia RPG - Casa Nobre &amp; Feudo" align="client" theme="dark">
    <script><![CDATA[
{build_lua_script()}
    ]]></script>

    <rectangle align="client" color="{BG_MAIN}">
        <!-- CABECALHO SENHORIAL FIXO -->
        <rectangle align="top" height="162" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="1" margins="{{left=6, right=6, top=6, bottom=4}}" xradius="6" yradius="6">
            <!-- MOLDURA DO BRASAO HERALDICO -->
            <rectangle left="10" top="10" width="114" height="114" color="{BG_INPUT}" strokeColor="{BORDER_GOLD}" strokeSize="2" xradius="6" yradius="6">
                <label name="lblBrasaoHint" left="6" top="26" width="102" height="62" text="BRASAO (Clique p/ enviar)" fontColor="{TEXT_MUTED}" fontSize="11" horzTextAlign="center" vertTextAlign="center" wordWrap="true"/>
                <image align="client" field="brasaoUrl" editable="true" style="autoFit"/>
            </rectangle>
            <button left="10" top="128" width="55" height="24" text="URL" fontSize="11">
                <event name="onClick"><![CDATA[definirBrasaoPorURL();]]></event>
            </button>
            <button left="69" top="128" width="55" height="24" text="Limpar" fontSize="11">
                <event name="onClick"><![CDATA[limparBrasao();]]></event>
            </button>

            <!-- IDENTIDADE DA CASA -->
            <label left="134" top="8" width="380" height="20" text="ALENIA RPG — CASA NOBRE, FEUDOS &amp; INTRIGAS (TOMOS XV &amp; XVII)" fontColor="{TEXT_GOLD}" fontSize="13" fontStyle="bold"/>
            <label left="522" top="8" width="510" height="20" field="resumoMilitarTopo" fontColor="{TEXT_CRIMSON}" fontSize="12" fontStyle="bold" horzTextAlign="trailing"/>

            <label left="134" top="30" width="230" height="16" text="NOME DA CASA / DINASTIA / CLA" fontColor="{TEXT_MUTED}" fontSize="11"/>
            <edit left="134" top="47" width="230" height="34" field="nomeCasa" textPrompt="Ex.: Casa de Specula..." fontColor="{TEXT_MAIN}" fontSize="15" fontStyle="bold"/>

            <label left="372" top="30" width="250" height="16" text="LEMA HERALDICO" fontColor="{TEXT_MUTED}" fontSize="11"/>
            <edit left="372" top="47" width="250" height="34" field="lemaCasa" textPrompt="Palavras do brasao..." fontColor="{TEXT_GOLD}" fontSize="14"/>

            <label left="630" top="30" width="84" height="16" text="STATUS (0-5)" fontColor="{TEXT_GOLD}" fontSize="11" fontStyle="bold" horzTextAlign="center"/>
            <edit left="630" top="47" width="50" height="34" field="statusCasa" type="number" fontColor="{TEXT_GOLD}" fontSize="17" fontStyle="bold" horzTextAlign="center"/>
            <button left="684" top="47" width="76" height="34" text="Status d20" fontSize="11">
                <event name="onClick"><![CDATA[rolarStatusCasa();]]></event>
            </button>

            <label left="768" top="30" width="124" height="16" text="COFRE ATUAL (PP)" fontColor="{TEXT_GOLD}" fontSize="11" fontStyle="bold" horzTextAlign="center"/>
            <edit left="768" top="47" width="124" height="34" field="cofrePP" type="number" fontColor="{TEXT_GREEN}" fontSize="16" fontStyle="bold" horzTextAlign="center"/>

            <button left="900" top="34" width="132" height="24" text="Virar Mes no Cofre" fontSize="11">
                <event name="onClick"><![CDATA[virarMesFeudo();]]></event>
            </button>
            <button left="900" top="62" width="132" height="24" text="Carta no Chat" fontSize="11">
                <event name="onClick"><![CDATA[anunciarCartaFeudo();]]></event>
            </button>

            <!-- 4 CARTAOZINHOS DE ORCAMENTO VIVO NO TOPO -->
            <rectangle left="134" top="90" width="228" height="62" color="{BG_INPUT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                <label left="8" top="4" width="212" height="16" text="INVESTIMENTO INICIAL TOTAL" fontColor="{TEXT_MUTED}" fontSize="10" fontStyle="bold"/>
                <label left="8" top="20" width="212" height="22" field="investimentoTotalTxt" fontColor="{TEXT_MAIN}" fontSize="14" fontStyle="bold"/>
                <label left="8" top="42" width="212" height="16" field="tempoObraTxt" fontColor="{TEXT_MUTED}" fontSize="10"/>
            </rectangle>

            <rectangle left="370" top="90" width="206" height="62" color="{BG_INPUT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                <label left="8" top="4" width="190" height="16" text="RECEITA BRUTA MENSAL" fontColor="{TEXT_MUTED}" fontSize="10" fontStyle="bold"/>
                <label left="8" top="21" width="190" height="24" field="receitaMensalTxt" fontColor="{TEXT_GREEN}" fontSize="15" fontStyle="bold"/>
                <checkBox left="8" top="43" width="190" height="16" field="pjAdminMes" text="PJ gerindo no mes (+10%)" fontColor="{TEXT_MUTED}" fontSize="10"/>
            </rectangle>

            <rectangle left="584" top="90" width="222" height="62" color="{BG_INPUT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                <label left="8" top="4" width="206" height="16" text="MANUTENCAO &amp; FOLHA MENSAL" fontColor="{TEXT_MUTED}" fontSize="10" fontStyle="bold"/>
                <label left="8" top="20" width="206" height="22" field="despesaMensalTxt" fontColor="{TEXT_CRIMSON}" fontSize="15" fontStyle="bold"/>
                <label left="8" top="42" width="206" height="16" field="detalheBalancoTxt" fontColor="{TEXT_MUTED}" fontSize="10"/>
            </rectangle>

            <rectangle left="814" top="90" width="218" height="62" color="{BG_INPUT}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="4" yradius="4">
                <label left="8" top="4" width="202" height="16" text="SALDO LIQUIDO NO COFRE" fontColor="{TEXT_GOLD}" fontSize="10" fontStyle="bold"/>
                <label left="8" top="20" width="202" height="24" field="saldoLiquidoTxt" fontColor="{TEXT_GOLD}" fontSize="16" fontStyle="bold"/>
                <checkBox left="8" top="43" width="202" height="16" field="feudoTributario" text="Vassalo tributario (-10%)" fontColor="{TEXT_MUTED}" fontSize="10"/>
            </rectangle>
        </rectangle>

        <!-- 5 ABAS PRINCIPAIS -->
        <tabControl align="client" margins="{{left=6, right=6, top=0, bottom=6}}">

            <!-- ABA 1: FUNDACAO, SUSERANIA, HERALDICA & SEDE (F01-F10 / L01-L22) -->
            <tab title="1. Casa, Suserania &amp; Sede">
                <scrollBox align="client">
                    <layout left="0" top="0" width="1056" height="966">
                        <!-- BARRA DE MODELOS PRONTOS -->
                        <rectangle left="6" top="6" width="1036" height="54" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="6" yradius="6">
                            <label left="14" top="15" width="232" height="24" text="MODELOS RAPIDOS:" fontColor="{TEXT_GOLD}" fontSize="13" fontStyle="bold"/>
                            <button left="248" top="11" width="194" height="32" text="Torre Specula (F04)" fontSize="12">
                                <event name="onClick"><![CDATA[aplicarPreset("torre");]]></event>
                            </button>
                            <button left="448" top="11" width="194" height="32" text="Solar Baronial (F05)" fontSize="12">
                                <event name="onClick"><![CDATA[aplicarPreset("solar");]]></event>
                            </button>
                            <button left="648" top="11" width="204" height="32" text="Divisa Voernock (L05)" fontSize="12">
                                <event name="onClick"><![CDATA[aplicarPreset("voernock");]]></event>
                            </button>
                            <button left="858" top="11" width="168" height="32" text="Zerar Tudo" fontSize="12">
                                <event name="onClick"><![CDATA[aplicarPreset("zerar");]]></event>
                            </button>
                        </rectangle>

                        <!-- MATRIZ CULTURAL & ORIGEM -->
                        <rectangle left="6" top="68" width="1036" height="184" color="{BG_CARD}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="6" yradius="6">
                            <label left="14" top="10" width="600" height="22" text="MATRIZ CULTURAL (TOMO V), SENHORIO &amp; LEGITIMIDADE" fontColor="{TEXT_GOLD}" fontSize="14" fontStyle="bold"/>

                            <label left="14" top="36" width="280" height="16" text="TRADICAO CULTURAL DA CASA" fontColor="{TEXT_MUTED}" fontSize="11"/>
                            <comboBox left="14" top="54" width="290" height="32" field="culturaCasa" items="{xml_attr(cultura_items)}" values="{xml_attr(cultura_values)}" fontSize="13"/>

                            <label left="316" top="36" width="320" height="16" text="VIA DE ORIGEM DO DOMINIO" fontColor="{TEXT_MUTED}" fontSize="11"/>
                            <comboBox left="316" top="54" width="330" height="32" field="origemCasa" items="{xml_attr(origem_items)}" values="{xml_attr(origem_values)}" fontSize="13"/>

                            <label left="658" top="36" width="260" height="16" text="SENHOR / CHEFE ATUAL DA CASA" fontColor="{TEXT_MUTED}" fontSize="11"/>
                            <edit left="658" top="54" width="260" height="32" field="chefeCasa" textPrompt="PJ ou patriarca/matriarca..." fontSize="13"/>

                            <label left="926" top="36" width="96" height="16" text="MOD. CAR/ETIQ" fontColor="{TEXT_MUTED}" fontSize="10" horzTextAlign="center"/>
                            <edit left="926" top="54" width="96" height="32" field="modSocialLider" type="number" horzTextAlign="center" fontSize="14"/>

                            <label left="14" top="94" width="490" height="16" text="REGIAO / COMARCA / LOCALIZACAO NO ATLAS" fontColor="{TEXT_MUTED}" fontSize="11"/>
                            <edit left="14" top="112" width="490" height="30" field="regiaoFeudo" textPrompt="Ex.: Vale do Dubravia, Costa dos Corais, Oasis Sul..." fontSize="13"/>

                            <label left="518" top="94" width="504" height="16" text="SUSERANO, CONSELHO DAS COPAS OU LIGA MERCANTIL" fontColor="{TEXT_MUTED}" fontSize="11"/>
                            <edit left="518" top="112" width="504" height="30" field="suseranoCasa" textPrompt="Ex.: Casa Montavalle, Liga de Baldbella, Livre..." fontSize="13"/>

                            <label left="14" top="148" width="1008" height="28" field="culturaResumo" fontColor="{TEXT_GOLD}" fontSize="12" wordWrap="true"/>
                        </rectangle>

                        <!-- FEUDO SUSERANO, REGENCIA & POLITICAGEM (TOMO XVII — L01 A L22) -->
                        <rectangle left="6" top="260" width="1036" height="164" color="{BG_CARD}" strokeColor="{BORDER_CRIMSON}" strokeSize="1" xradius="6" yradius="6">
                            <label left="14" top="8" width="540" height="22" text="FEUDO SUSERANO, REGENCIA &amp; POLITICAGEM (TOMO XVII — L01 A L22)" fontColor="{TEXT_GOLD}" fontSize="14" fontStyle="bold"/>
                            <button left="562" top="6" width="142" height="26" text="Ficha do Feudo" fontSize="11">
                                <event name="onClick"><![CDATA[verFichaFeudoSuserano();]]></event>
                            </button>
                            <button left="710" top="6" width="154" height="26" text="Despacho no Chat" fontSize="11">
                                <event name="onClick"><![CDATA[anunciarVassalagemChat();]]></event>
                            </button>
                            <button left="870" top="6" width="152" height="26" text="Intriga 1d12" fontSize="11">
                                <event name="onClick"><![CDATA[rolarIntrigaFeudal();]]></event>
                            </button>

                            <comboBox left="14" top="38" width="604" height="32" field="feudoSuseranoId" items="{xml_attr(feudo_items)}" values="{xml_attr(feudo_values)}" fontSize="12"/>
                            <checkBox left="630" top="38" width="198" height="32" field="aplicarBonusFeudo" text="Ativar Bonus da Carta" fontColor="{TEXT_GREEN}" fontSize="11"/>
                            <checkBox left="834" top="38" width="192" height="32" field="sobEmbargoVizinho" text="Sob Embargo Vizinho" fontColor="{TEXT_CRIMSON}" fontSize="11"/>

                            <rectangle left="14" top="76" width="1008" height="44" color="{BG_INPUT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                                <label left="8" top="2" width="992" height="40" field="feudoCadeiaTxt" fontColor="{TEXT_MAIN}" fontSize="11" vertTextAlign="center" wordWrap="true"/>
                            </rectangle>
                            <label left="14" top="124" width="1008" height="34" field="feudoBonusTxt" fontColor="{TEXT_GOLD}" fontSize="12" vertTextAlign="center" wordWrap="true"/>
                        </rectangle>

                        <!-- SEDE SENHORIAL PRINCIPAL (F01-F10) -->
                        <rectangle left="6" top="432" width="1036" height="202" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="6" yradius="6">
                            <label left="14" top="10" width="680" height="22" text="SEDE SENHORIAL / FORTIFICACAO PRINCIPAL (F01 A F10)" fontColor="{TEXT_GOLD}" fontSize="14" fontStyle="bold"/>
                            <button left="822" top="8" width="200" height="28" text="Ver Ficha Completa da Sede" fontSize="12">
                                <event name="onClick"><![CDATA[verDetalhesCodigo(tostring(sheet.sedeId or "F04"));]]></event>
                            </button>

                            <label left="14" top="38" width="560" height="16" text="ESCOLHA A FORTIFICACAO PRINCIPAL" fontColor="{TEXT_MUTED}" fontSize="11"/>
                            <comboBox left="14" top="56" width="580" height="34" field="sedeId" items="{xml_attr(sede_items)}" values="{xml_attr(sede_values)}" fontSize="13"/>

                            <label left="608" top="38" width="414" height="16" text="MODO DE AQUISICAO / OBRA" fontColor="{TEXT_MUTED}" fontSize="11"/>
                            <comboBox left="608" top="56" width="414" height="34" field="modoAquisicao" items="{xml_attr(modo_items)}" values="{xml_attr(modo_values)}" fontSize="13"/>

                            <rectangle left="14" top="100" width="1008" height="50" color="{BG_INPUT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                                <label left="10" top="4" width="988" height="42" field="sedeResumoCard" fontColor="{TEXT_MAIN}" fontSize="12" vertTextAlign="center" wordWrap="true"/>
                            </rectangle>
                            <label left="14" top="156" width="1008" height="38" field="sedeBeneficioCard" fontColor="{TEXT_GREEN}" fontSize="12" vertTextAlign="center" wordWrap="true"/>
                        </rectangle>

                        <!-- RAIZES DA CASA (1D8) & DESCRICAO DO BRASAO -->
                        <rectangle left="6" top="642" width="1036" height="304" color="{BG_CARD}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="6" yradius="6">
                            <label left="14" top="10" width="520" height="22" text="RAIZES HISTORICAS DA CASA (1D8) &amp; BRASAO D'ARMAS" fontColor="{TEXT_GOLD}" fontSize="14" fontStyle="bold"/>

                            <label left="14" top="38" width="320" height="18" text="VIRTUDE HISTORICA (VANTAGEM INICIAL)" fontColor="{TEXT_GREEN}" fontSize="12" fontStyle="bold"/>
                            <button left="342" top="34" width="156" height="26" text="Sortear Virtude (1d8)" fontSize="11">
                                <event name="onClick"><![CDATA[sortearRaizCasa("virtude");]]></event>
                            </button>
                            <textEditor left="14" top="64" width="484" height="104" field="virtudeCasa" fontSize="13"/>

                            <label left="534" top="38" width="320" height="18" text="DIVIDA, MANCHA OU AMEACA HERDADA" fontColor="{TEXT_CRIMSON}" fontSize="12" fontStyle="bold"/>
                            <button left="866" top="34" width="156" height="26" text="Sortear Divida (1d8)" fontSize="11">
                                <event name="onClick"><![CDATA[sortearRaizCasa("divida");]]></event>
                            </button>
                            <textEditor left="534" top="64" width="488" height="104" field="dividaCasa" fontSize="13"/>

                            <label left="14" top="178" width="1008" height="18" text="DESCRICAO HERALDICA DO ESCUDO (ESMALTES, METAIS, PARTICAO, FIGURA, TIMBRE E SINAL DE BASTARDIA)" fontColor="{TEXT_GOLD}" fontSize="12" fontStyle="bold"/>
                            <textEditor left="14" top="200" width="1008" height="90" field="brasaoDescricao" fontSize="13"/>
                        </rectangle>
                    </layout>
                </scrollBox>
            </tab>

            <!-- ABA 2: DEFESAS (D01-D08) & OBRAS PRODUTIVAS (D09-D16) -->
            <tab title="2. Defesas &amp; Obras (D01-D16)">
                <scrollBox align="client">
                    <layout left="0" top="0" width="1056" height="650">
                        <rectangle left="6" top="6" width="1036" height="42" color="{BG_INPUT}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="5" yradius="5">
                            <label left="12" top="6" width="1012" height="30" field="barraSinergiasAvisos" fontColor="{TEXT_GOLD}" fontSize="12" fontStyle="bold" vertTextAlign="center" wordWrap="true"/>
                        </rectangle>

                        <!-- COLUNA ESQUERDA: DEFESAS D01-D08 -->
                        <rectangle left="6" top="56" width="512" height="506" color="{BG_CARD}" strokeColor="{BORDER_CRIMSON}" strokeSize="1" xradius="6" yradius="6">
                            <label left="12" top="10" width="290" height="22" text="DEFESAS SEM POLVORA (D01-D08)" fontColor="{TEXT_CRIMSON}" fontSize="14" fontStyle="bold"/>
                            <label left="306" top="10" width="194" height="22" field="slotsDefesaTxt" fontColor="{TEXT_GOLD}" fontSize="12" fontStyle="bold" horzTextAlign="trailing"/>
                            <label left="12" top="34" width="488" height="18" text="Cada melhoria ocupa 1 Slot de Defesa. D05 e D06 exigem Sede F04+ e Artilheiro G07." fontColor="{TEXT_MUTED}" fontSize="11"/>
                            {"".join(def_rows)}
                        </rectangle>

                        <!-- COLUNA DIREITA: OBRAS PRODUTIVAS D09-D16 -->
                        <rectangle left="530" top="56" width="512" height="506" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="6" yradius="6">
                            <label left="12" top="10" width="230" height="22" text="OBRAS &amp; RENDA (D09-D16)" fontColor="{TEXT_GREEN}" fontSize="14" fontStyle="bold"/>
                            <label left="244" top="10" width="256" height="22" field="slotsObraTxt" fontColor="{TEXT_GOLD}" fontSize="11" fontStyle="bold" horzTextAlign="trailing"/>
                            <label left="12" top="34" width="488" height="18" text="D09 (Aldeia) fica fora dos muros (nao usa Slot de Obra). D10-D16 usam 1 Slot cada." fontColor="{TEXT_MUTED}" fontSize="11"/>
                            {"".join(work_rows)}
                        </rectangle>

                        <!-- AJUSTES FINOS DE RECEITA / DESPESA EXTRA -->
                        <rectangle left="6" top="570" width="1036" height="66" color="{BG_CARD}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="6" yradius="6">
                            <label left="14" top="22" width="270" height="22" text="RECEITA EXTRA / ACORDOS (+PP/mes):" fontColor="{TEXT_GREEN}" fontSize="12" fontStyle="bold"/>
                            <edit left="286" top="16" width="90" height="34" field="rendaExtraManual" type="number" horzTextAlign="center" fontColor="{TEXT_GREEN}" fontSize="15" fontStyle="bold"/>

                            <label left="410" top="22" width="290" height="22" text="DESPESAS EXTRAS / PENSOES (-PP/mes):" fontColor="{TEXT_CRIMSON}" fontSize="12" fontStyle="bold"/>
                            <edit left="704" top="16" width="90" height="34" field="despesaExtraManual" type="number" horzTextAlign="center" fontColor="{TEXT_CRIMSON}" fontSize="15" fontStyle="bold"/>

                            <label left="816" top="14" width="208" height="38" text="Ex.: tratados comerciais, pensoes familiares ou juros de Falcone." fontColor="{TEXT_MUTED}" fontSize="11" wordWrap="true"/>
                        </rectangle>
                    </layout>
                </scrollBox>
            </tab>

            <!-- ABA 3: GUARNICAO, ARTIFICES & CORTE (G01-G14) -->
            <tab title="3. Guarnicao &amp; Corte (G01-G14)">
                <scrollBox align="client">
                    <layout left="0" top="0" width="1056" height="560">
                        <rectangle left="6" top="6" width="1036" height="52" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="6" yradius="6">
                            <label left="14" top="14" width="530" height="24" field="efetivoTropaTxt" fontColor="{TEXT_GOLD}" fontSize="14" fontStyle="bold"/>
                            <label left="556" top="15" width="196" height="22" text="MESES DE SOLDO ATRASADO:" fontColor="{TEXT_CRIMSON}" fontSize="12" fontStyle="bold"/>
                            <edit left="756" top="10" width="54" height="32" field="mesesAtrasoSoldo" type="number" horzTextAlign="center" fontColor="{TEXT_CRIMSON}" fontSize="15" fontStyle="bold"/>
                            <label left="820" top="8" width="208" height="36" text="1 mes = -2 Moral | 2+ meses = 50% deserta!" fontColor="{TEXT_MUTED}" fontSize="11" wordWrap="true"/>
                        </rectangle>

                        <!-- COLUNA ESQUERDA: TROPAS G01-G07 -->
                        <rectangle left="6" top="66" width="512" height="480" color="{BG_CARD}" strokeColor="{BORDER_CRIMSON}" strokeSize="1" xradius="6" yradius="6">
                            <label left="12" top="10" width="488" height="22" text="TROPAS DE GUARNICAO E PATRULHA (G01-G07)" fontColor="{TEXT_CRIMSON}" fontSize="14" fontStyle="bold"/>
                            <label left="12" top="34" width="488" height="18" text="Clique em [Atacar] para rolar o ataque da unidade no chat da mesa." fontColor="{TEXT_MUTED}" fontSize="11"/>
                            {"".join(troop_rows)}
                        </rectangle>

                        <!-- COLUNA DIREITA: TRABALHADORES E CORTE G08-G14 -->
                        <rectangle left="530" top="66" width="512" height="480" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="6" yradius="6">
                            <label left="12" top="10" width="488" height="22" text="TRABALHADORES, ARTIFICES E CORTE (G08-G14)" fontColor="{TEXT_GOLD}" fontSize="14" fontStyle="bold"/>
                            <label left="12" top="34" width="488" height="18" text="Civis nao contam no limite de alojamento militar. G11 concede +10% Receita!" fontColor="{TEXT_MUTED}" fontSize="11"/>
                            {"".join(staff_rows)}
                        </rectangle>
                    </layout>
                </scrollBox>
            </tab>

            <!-- ABA 4: GESTAO SAZONAL, CERCOS & CRONICA -->
            <tab title="4. Cercos, Eventos &amp; Cronica">
                <scrollBox align="client">
                    <layout left="0" top="0" width="1056" height="820">
                        <!-- GIRO MENSAL & EVENTO SAZONAL 1D12 -->
                        <rectangle left="6" top="6" width="1036" height="126" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="6" yradius="6">
                            <label left="14" top="10" width="480" height="22" text="CALENDARIO DE DOMINIO &amp; EVENTOS SAZONAIS (1D12)" fontColor="{TEXT_GOLD}" fontSize="14" fontStyle="bold"/>

                            <label left="14" top="42" width="118" height="24" text="MES ATUAL #" fontColor="{TEXT_MUTED}" fontSize="12" fontStyle="bold"/>
                            <edit left="132" top="38" width="64" height="32" field="mesCampanha" type="number" horzTextAlign="center" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold"/>

                            <button left="204" top="36" width="188" height="36" text="Virar Mes no Cofre" fontSize="12">
                                <event name="onClick"><![CDATA[virarMesFeudo();]]></event>
                            </button>

                            <button left="400" top="36" width="178" height="36" text="Evento Sazonal (1d12)" fontSize="12">
                                <event name="onClick"><![CDATA[rolarEventoSazonal();]]></event>
                            </button>

                            <button left="586" top="36" width="170" height="36" text="Intriga Feudal (1d12)" fontSize="12">
                                <event name="onClick"><![CDATA[rolarIntrigaFeudal();]]></event>
                            </button>

                            <label left="766" top="42" width="174" height="24" text="MOD. SAB/INT ESPIAO:" fontColor="{TEXT_MUTED}" fontSize="11" fontStyle="bold"/>
                            <edit left="944" top="38" width="78" height="32" field="modEspionagemCasa" type="number" horzTextAlign="center" fontSize="14"/>

                            <rectangle left="14" top="80" width="1008" height="36" color="{BG_INPUT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                                <label left="10" top="2" width="988" height="32" field="ultimoEventoSazonal" text="Role 1d12 uma vez por estacao para verificar colheitas, caravanas, intrigas ou feiras no feudo." fontColor="{TEXT_MAIN}" fontSize="12" vertTextAlign="center" wordWrap="true"/>
                            </rectangle>
                        </rectangle>

                        <!-- PAINEL DE CERCO SEM POLVORA & 4 POSTOS DOS PJS -->
                        <rectangle left="6" top="140" width="1036" height="278" color="{BG_CARD}" strokeColor="{BORDER_CRIMSON}" strokeSize="1" xradius="6" yradius="6">
                            <label left="14" top="10" width="680" height="22" text="PAINEL DE CERCO SEM POLVORA, INTEGRIDADE &amp; 4 POSTOS DOS PJS" fontColor="{TEXT_CRIMSON}" fontSize="14" fontStyle="bold"/>
                            <button left="812" top="8" width="210" height="28" text="Reparar Tudo &amp; Reabastecer" fontSize="12">
                                <event name="onClick"><![CDATA[repararFortalezaMax();]]></event>
                            </button>

                            <label left="14" top="42" width="166" height="18" text="PV ATUAL / MAXIMO" fontColor="{TEXT_MUTED}" fontSize="11" fontStyle="bold"/>
                            <edit left="14" top="62" width="74" height="34" field="integridadeAtual" type="number" horzTextAlign="center" fontColor="{TEXT_MAIN}" fontSize="16" fontStyle="bold"/>
                            <label left="90" top="62" width="16" height="34" text="/" fontColor="{TEXT_MUTED}" fontSize="16" horzTextAlign="center" vertTextAlign="center"/>
                            <rectangle left="108" top="62" width="74" height="34" color="{BG_INPUT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                                <label align="client" field="integridadeMaxCalc" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold" horzTextAlign="center" vertTextAlign="center"/>
                            </rectangle>

                            <label left="198" top="42" width="140" height="18" text="DANO BRUTO SOFRIDO" fontColor="{TEXT_CRIMSON}" fontSize="11" fontStyle="bold"/>
                            <edit left="198" top="62" width="68" height="34" field="danoCercoEntrada" type="number" horzTextAlign="center" fontColor="{TEXT_CRIMSON}" fontSize="15" fontStyle="bold"/>
                            <checkBox left="272" top="62" width="120" height="34" field="ataqueNoPortao" text="No Portao (D02)" fontColor="{TEXT_MAIN}" fontSize="11"/>
                            <button left="396" top="62" width="176" height="34" text="Aplicar Dano (c/ LE)" fontSize="12">
                                <event name="onClick"><![CDATA[aplicarDanoCerco();]]></event>
                            </button>

                            <label left="590" top="42" width="150" height="18" text="DIAS DE SUPRIMENTO" fontColor="{TEXT_GOLD}" fontSize="11" fontStyle="bold"/>
                            <edit left="590" top="62" width="62" height="34" field="diasCercoRestantes" type="number" horzTextAlign="center" fontColor="{TEXT_GOLD}" fontSize="16" fontStyle="bold"/>
                            <button left="658" top="62" width="104" height="34" text="-1 Dia Cerco" fontSize="12">
                                <event name="onClick"><![CDATA[consumirDiaCerco();]]></event>
                            </button>

                            <label left="780" top="42" width="110" height="18" text="BONUS MORAL" fontColor="{TEXT_MUTED}" fontSize="11" fontStyle="bold"/>
                            <edit left="780" top="62" width="62" height="34" field="moralBonusExtra" type="number" horzTextAlign="center" fontSize="15"/>
                            <button left="850" top="62" width="172" height="34" text="Contraespionagem" fontSize="12">
                                <event name="onClick"><![CDATA[rolarContraespionagem();]]></event>
                            </button>

                            <!-- 4 POSTOS DE DEFESA DOS PJS -->
                            <rectangle left="14" top="108" width="498" height="74" color="{BG_CARD_ALT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                                <label left="10" top="6" width="330" height="20" text="1. COMANDANTE DA MURALHA (Persuasao/Intim. CD 14)" fontColor="{TEXT_GOLD}" fontSize="12" fontStyle="bold"/>
                                <label left="10" top="26" width="290" height="18" text="Concede +2 contra medo/debandada e +1 nos tiros." fontColor="{TEXT_MUTED}" fontSize="11"/>
                                <label left="10" top="46" width="76" height="22" text="Mod. PJ:" fontColor="{TEXT_MUTED}" fontSize="11"/>
                                <edit left="76" top="44" width="52" height="24" field="modCercoComandante" type="number" horzTextAlign="center" fontSize="13"/>
                                <button left="342" top="20" width="144" height="40" text="Rolar Comando" fontSize="12">
                                    <event name="onClick"><![CDATA[rolarPostoCerco(1);]]></event>
                                </button>
                            </rectangle>

                            <rectangle left="524" top="108" width="498" height="74" color="{BG_CARD_ALT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                                <label left="10" top="6" width="360" height="20" text="2. MESTRE DE ENGENHOS (Engenharia/Dist.)" fontColor="{TEXT_GOLD}" fontSize="12" fontStyle="bold"/>
                                <label left="10" top="26" width="250" height="18" text="Balista D05 (3d10) ou Trabuco D06 (6d10)." fontColor="{TEXT_MUTED}" fontSize="11"/>
                                <label left="10" top="46" width="76" height="22" text="Mod. PJ:" fontColor="{TEXT_MUTED}" fontSize="11"/>
                                <edit left="76" top="44" width="52" height="24" field="modCercoEngenho" type="number" horzTextAlign="center" fontSize="13"/>
                                <button left="266" top="20" width="108" height="40" text="Balista 3d10" fontSize="12">
                                    <event name="onClick"><![CDATA[dispararEngenhoMuralha("balista");]]></event>
                                </button>
                                <button left="380" top="20" width="108" height="40" text="Trabuco 6d10" fontSize="12">
                                    <event name="onClick"><![CDATA[dispararEngenhoMuralha("trabuco");]]></event>
                                </button>
                            </rectangle>

                            <rectangle left="14" top="190" width="498" height="74" color="{BG_CARD_ALT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                                <label left="10" top="6" width="340" height="20" text="3. LIDER DE SORTIDA NOTURNA (Furtividade CD 15)" fontColor="{TEXT_GOLD}" fontSize="12" fontStyle="bold"/>
                                <label left="10" top="26" width="320" height="18" text="Sabota arietes/torres inimigas (+2 automatico c/ Poterna D08)." fontColor="{TEXT_MUTED}" fontSize="11"/>
                                <label left="10" top="46" width="76" height="22" text="Mod. PJ:" fontColor="{TEXT_MUTED}" fontSize="11"/>
                                <edit left="76" top="44" width="52" height="24" field="modCercoSortida" type="number" horzTextAlign="center" fontSize="13"/>
                                <button left="342" top="20" width="144" height="40" text="Rolar Sortida" fontSize="12">
                                    <event name="onClick"><![CDATA[rolarPostoCerco(3);]]></event>
                                </button>
                            </rectangle>

                            <rectangle left="524" top="190" width="498" height="74" color="{BG_CARD_ALT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                                <label left="10" top="6" width="340" height="20" text="4. INTENDENTE DA PRACA (Medicina/Fe CD 14)" fontColor="{TEXT_GOLD}" fontSize="12" fontStyle="bold"/>
                                <label left="10" top="26" width="320" height="18" text="Apaga incendios, salva feridos e contem panico (+2 c/ D15)." fontColor="{TEXT_MUTED}" fontSize="11"/>
                                <label left="10" top="46" width="76" height="22" text="Mod. PJ:" fontColor="{TEXT_MUTED}" fontSize="11"/>
                                <edit left="76" top="44" width="52" height="24" field="modCercoIntendente" type="number" horzTextAlign="center" fontSize="13"/>
                                <button left="342" top="20" width="144" height="40" text="Rolar Intendencia" fontSize="12">
                                    <event name="onClick"><![CDATA[rolarPostoCerco(4);]]></event>
                                </button>
                            </rectangle>
                        </rectangle>

                        <!-- LIVRO-RAZAO & CRONICA DA LINHAGEM -->
                        <rectangle left="6" top="426" width="512" height="378" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="6" yradius="6">
                            <label left="12" top="10" width="488" height="22" text="LIVRO-RAZAO, TRATADOS, VASSALOS &amp; ROTAS" fontColor="{TEXT_GOLD}" fontSize="14" fontStyle="bold"/>
                            <textEditor left="12" top="38" width="488" height="328" field="livroRazaoNotas" fontSize="13"/>
                        </rectangle>

                        <rectangle left="530" top="426" width="512" height="378" color="{BG_CARD}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="6" yradius="6">
                            <label left="12" top="10" width="488" height="22" text="ARVORE DA FAMILIA, HERDEIROS &amp; CRONICA DA CASA" fontColor="{TEXT_GOLD}" fontSize="14" fontStyle="bold"/>
                            <textEditor left="12" top="38" width="488" height="328" field="cronicaFamiliaNotas" fontSize="13"/>
                        </rectangle>
                    </layout>
                </scrollBox>
            </tab>

            <!-- ABA 5: AUTORIA & ATUALIZACAO -->
            <tab title="5. Autoria &amp; Atualizacao">
                <scrollBox align="client">
                    <layout left="0" top="0" width="1056" height="580">
                        <rectangle left="6" top="6" width="1036" height="176" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="2" xradius="6" yradius="6">
                            <label left="20" top="18" width="996" height="30" text="ALENIA RPG — CASA NOBRE, FEUDOS &amp; INTRIGAS (TOMOS XV &amp; XVII)" fontColor="{TEXT_GOLD}" fontSize="19" fontStyle="bold" horzTextAlign="center"/>
                            <label left="20" top="56" width="996" height="34" text="Plugin desenvolvido por Mestre Carlos" fontColor="{TEXT_MAIN}" fontSize="22" fontStyle="bold" horzTextAlign="center"/>
                            <label left="20" top="98" width="996" height="24" text="5 Matrizes Culturais • 10 Fortificacoes (F01-F10) • 16 Defesas e Obras (D01-D16) • 14 Tropas e Corte (G01-G14) • Cercos" fontColor="{TEXT_MUTED}" fontSize="13" horzTextAlign="center"/>

                            <rectangle left="168" top="130" width="220" height="34" color="{BG_INPUT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                                <label left="8" top="0" width="110" height="34" text="Versao Atual:" fontColor="{TEXT_MUTED}" fontSize="13" vertTextAlign="center"/>
                                <label left="118" top="0" width="94" height="34" field="pluginVersaoAtual" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold" horzTextAlign="center" vertTextAlign="center"/>
                            </rectangle>

                            <rectangle left="404" top="130" width="260" height="34" color="{BG_INPUT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                                <label align="client" text="ID: br.com.alenia.casa_nobre" fontColor="{TEXT_MUTED}" fontSize="13" horzTextAlign="center" vertTextAlign="center"/>
                            </rectangle>

                            <rectangle left="680" top="130" width="190" height="34" color="{BG_INPUT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                                <label align="client" text="Firecast SDK 3.7b" fontColor="{TEXT_GREEN}" fontSize="13" fontStyle="bold" horzTextAlign="center" vertTextAlign="center"/>
                            </rectangle>
                        </rectangle>

                        <rectangle left="6" top="194" width="1036" height="244" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="6" yradius="6">
                            <label left="20" top="14" width="996" height="28" text="ATUALIZACAO AUTOMATICA INTEGRADA" fontColor="{TEXT_GOLD}" fontSize="16" fontStyle="bold" horzTextAlign="center"/>
                            <label left="20" top="44" width="996" height="24" text="Consulta o repositorio oficial de Alenia RPG e instala novas versoes diretamente no Firecast." fontColor="{TEXT_MUTED}" fontSize="14" horzTextAlign="center"/>

                            <button left="248" top="80" width="540" height="50" text="Clique aqui para verificar se ha atualizacoes" fontSize="16">
                                <event name="onClick"><![CDATA[verificarEAtualizarPlugin(false);]]></event>
                            </button>

                            <rectangle left="48" top="142" width="940" height="40" color="{BG_INPUT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                                <label align="client" field="statusAtualizacao" fontColor="{TEXT_GOLD}" fontSize="14" horzTextAlign="center" vertTextAlign="center"/>
                            </rectangle>

                            <button left="168" top="194" width="330" height="36" text="Forcar Reinstalacao Direta" fontSize="14">
                                <event name="onClick"><![CDATA[verificarEAtualizarPlugin(true);]]></event>
                            </button>
                            <button left="538" top="194" width="330" height="36" text="Abrir Atlas Feudal (Tomo XVII)" fontSize="14">
                                <event name="onClick"><![CDATA[abrirLinkExterno(BIBLIOTECA_URL);]]></event>
                            </button>
                        </rectangle>

                        <rectangle left="6" top="450" width="1036" height="114" color="{BG_CARD}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="6" yradius="6">
                            <label left="20" top="14" width="996" height="24" text="RECURSOS DA FICHA v1.1 (TOMOS XV &amp; XVII)" fontColor="{TEXT_GOLD}" fontSize="14" fontStyle="bold"/>
                            <label left="20" top="42" width="996" height="58" text="• Novidades v1.1 (Tomo XVII): Seletor dos 22 Feudos e Regencias Suseranas (L01-L22 — 7 Feudos de Aurora diretos a Altavanne e 14 Feudos sob os 3 Regentes) com bonus regionais de concessao, chave de Embargo Vizinho (-25% D11/D14, +20% obra), modelo pronto de Voernock (L05) e Sorteador de Intrigas Feudais (1d12) no chat!" fontColor="{TEXT_MAIN}" fontSize="13" wordWrap="true"/>
                        </rectangle>
                    </layout>
                </scrollBox>
            </tab>
        </tabControl>
    </rectangle>

    <!-- DATALINKS NA RAIZ DO FORM (REGRA 2 DO SDK 3.7b) -->
    <dataLink fields="{xml_attr(lua_items_str(def_fields))}" defaultValues="{xml_attr(lua_items_str(def_values))}"/>

    <dataLink fields="{xml_attr(lua_items_str(recalc_fields))}">
        <event name="onChange"><![CDATA[recalcularFeudo();]]></event>
    </dataLink>
    <dataLink fields="{{'brasaoUrl'}}">
        <event name="onChange"><![CDATA[atualizarVisibilidadeBrasao();]]></event>
    </dataLink>
</form>
'''
    with open(LFM_PATH, "w", encoding="utf-8") as f:
        f.write(lfm)
    print(f"[OK] AleniaCasaNobre.lfm gerado ({len(lfm)} bytes).")


if __name__ == "__main__":
    build_lfm()
