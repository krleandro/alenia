#!/usr/bin/env python3
"""
Gera a ficha oficial AleniaFicha.lfm (RRPG Firecast SDK 3.7b) — v1.2 (Alinhada à Edição Revisada v2.0)
- Fontes ampliadas (v1.1+)
- Dado de Vida (1d6 / 1d8 / 1d10 / 1d12) por Kit + botão "Subir Nivel (1dX + CON)" no chat
- Perícias recalibradas (Base 1-2, Mult. INT 0.50-1.25, custo 2/7/17, travas Nív. 5/11)
- Trava anti-abuso em Múltiplas Ações Storyteller (limite por grau de treino + bônus >= 0)
- 36 Kits Universais + Sem Kit, 34 Perícias Fixas + Perícias Livres Ilimitadas
"""
import os
import xml.sax.saxutils as sax

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
LFM_PATH = os.path.join(OUT_DIR, "AleniaFicha.lfm")

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

SKILLS = [
    ("per_armas_brancas", "Armas Brancas", "forca", "Combate"),
    ("per_armas_dist", "Armas a Distancia", "destreza", "Combate"),
    ("per_luta_desarm", "Luta Desarmada", "forca", "Combate"),
    ("per_aparar", "Aparar", "forca", "Combate"),
    ("per_esquiva", "Esquiva", "destreza", "Combate"),
    ("per_escudos", "Escudos", "forca", "Combate"),
    ("per_atletismo", "Atletismo", "forca", "Fisicas"),
    ("per_acrobacia", "Acrobacia", "destreza", "Fisicas"),
    ("per_furtividade", "Furtividade", "destreza", "Fisicas"),
    ("per_escalada", "Escalada", "forca", "Fisicas"),
    ("per_natacao", "Natacao", "forca", "Fisicas"),
    ("per_cavalgar", "Cavalgar", "destreza", "Fisicas"),
    ("per_sobrevivencia", "Sobrevivencia", "sabedoria", "Fisicas"),
    ("per_navegacao", "Navegacao e Nautica", "sabedoria", "Fisicas"),
    ("per_percepcao", "Percepcao", "sabedoria", "Subterfugio"),
    ("per_investigacao", "Investigacao", "inteligencia", "Subterfugio"),
    ("per_disfarce", "Disfarce", "carisma", "Subterfugio"),
    ("per_ladinagem", "Ladinagem e Fechaduras", "destreza", "Subterfugio"),
    ("per_prestidig", "Prestidigitacao", "destreza", "Subterfugio"),
    ("per_persuasao", "Persuasao", "carisma", "Sociais"),
    ("per_enganacao", "Enganacao", "carisma", "Sociais"),
    ("per_intimidacao", "Intimidacao", "carisma", "Sociais"),
    ("per_intuicao", "Intuicao", "sabedoria", "Sociais"),
    ("per_etiqueta", "Etiqueta e Corte", "carisma", "Sociais"),
    ("per_barganha", "Barganha e Comercio", "carisma", "Sociais"),
    ("per_medicina", "Medicina e Cirurgia", "inteligencia", "Oficios"),
    ("per_alquimia", "Alquimia e Venenos", "inteligencia", "Oficios"),
    ("per_forja", "Forja e Metalurgia", "inteligencia", "Oficios"),
    ("per_engenharia", "Engenharia e Mecanica", "inteligencia", "Oficios"),
    ("per_herbalismo", "Herbalismo e Natureza", "sabedoria", "Oficios"),
    ("per_historia", "Historia e Lendas", "inteligencia", "Oficios"),
    ("per_geografia", "Geografia e Cartografia", "inteligencia", "Oficios"),
    ("per_idiomas", "Idiomas e Cifras", "inteligencia", "Oficios"),
    ("per_religiao", "Religiao e Ocultismo", "sabedoria", "Oficios"),
]

# Tuple: (id, nome, dvFaces, perBase, multInt, espField, espVal, periciasIniciais, equip, hab)
KITS = [
    ("sem_kit", "00 - Sem Kit (Livre / Media Padrao)", 8, 1, 0.75, None, 0,
     [],
     "Adaga, roupa de viagem resistente, mochila, cantil, racoes (5 dias) e 25 PP.",
     "Caminho Proprio: Flexibilidade total; comeca com +2 Pontos de Pericia extras no Nivel 1."),

    ("mercenario", "01 - Mercenario (1d10)", 10, 1, 0.75, None, 0,
     ["per_armas_brancas", "per_aparar", "per_sobrevivencia", "per_intimidacao", "per_barganha"],
     "Espada longa, couro batido, capa de estrada, pedra de amolar, mochila e 30 PP.",
     "Sobrevivente de Contrato: +2 em Iniciativa e troca de arma como acao livre 1x/turno."),

    ("cavaleiro", "02 - Cavaleiro (1d10)", 10, 1, 0.75, "esp_status", 1,
     ["per_armas_brancas", "per_aparar", "per_escudos", "per_cavalgar", "per_etiqueta"],
     "Espada longa, escudo medio, cota de malha, tabardo com brasao, sela e 40 PP.",
     "Juramento de Aco: +2 em Cavalgar em combate e +2 na Defesa ao usar Proteger Aliado com escudo."),

    ("soldado", "03 - Soldado / Veterano (1d10)", 10, 1, 0.50, None, 0,
     ["per_armas_brancas", "per_escudos", "per_aparar", "per_atletismo", "per_percepcao"],
     "Lanca de infantaria, espada curta, escudo medio, cota de malha, cantil e 20 PP.",
     "Linha de Frente: Quando adjacente a um aliado, ambos ganham +1 na Defesa corpo a corpo."),

    ("duelista", "04 - Duelista / Esgrimista (1d8)", 8, 1, 0.75, None, 0,
     ["per_armas_brancas", "per_aparar", "per_esquiva", "per_acrobacia", "per_intuicao"],
     "Florete (ou lamina oriental), adaga de aparar, gibao reforcado fino e 35 PP.",
     "Cadencia Letal: Em duelos 1x1, reduz em 1 a penalidade adicional de Multiplas Acoes (min. 0)."),

    ("barbaro", "05 - Barbaro / Berserker (1d12)", 12, 1, 0.50, None, 0,
     ["per_armas_brancas", "per_atletismo", "per_sobrevivencia", "per_intimidacao", "per_escalada"],
     "Machado grande, peles reforcadas (Def +1), trofeu de caca, cantil e 15 PP.",
     "Furia Indomavel: 1x/combate por 3 rodadas: +2 dano corpo a corpo e +3 CON vs Golpe Devastador (-2 Defesa)."),

    ("guarda_costas", "06 - Guarda-Costas / Sentinela (1d10)", 10, 1, 0.50, None, 0,
     ["per_armas_brancas", "per_aparar", "per_escudos", "per_percepcao", "per_intuicao"],
     "Espada longa, escudo torre, brigantina, lanterna de vigia, apito e 25 PP.",
     "Escudo Vivo: Ao usar Proteger Aliado, impoe -2 extra no atacante e pode mover 3m como reacao."),

    ("arqueiro", "07 - Arqueiro / Franco-Atirador (1d8)", 8, 1, 0.75, None, 0,
     ["per_armas_dist", "per_esquiva", "per_furtividade", "per_percepcao", "per_sobrevivencia"],
     "Arco longo (30 flechas), adaga, couro batido, capa camuflada e 25 PP.",
     "Olho de Falcao: Gastando Movimento para mirar parado, ganha +2 no acerto e -1 na Margem de Critico."),

    ("lutador", "08 - Lutador / Pugilista (1d10)", 10, 1, 0.50, None, 0,
     ["per_luta_desarm", "per_esquiva", "per_atletismo", "per_acrobacia", "per_intimidacao"],
     "Bandagens reforcadas/soqueiras de couro, gibao reforcado, unguento e 20 PP.",
     "Punhos de Ferro: Dano desarmado 1d6+FOR, pode aparar golpes leves e ganha +3 para agarrar/derrubar."),

    ("ladino", "09 - Ladino (1d6)", 6, 2, 1.00, None, 0,
     ["per_furtividade", "per_ladinagem", "per_esquiva", "per_percepcao", "per_prestidig", "per_acrobacia"],
     "2 adagas, espada curta, couro batido escuro, gazuas, corda fina (15m) e 25 PP.",
     "Golpe Oportunista: +1d6 dano contra desprevenidos ou flanqueados (+2d6 Lenda, +3d6 Epico; nao multiplica no critico)."),

    ("assassino", "10 - Assassino (1d6)", 6, 2, 0.75, "esp_submundo", 1,
     ["per_armas_brancas", "per_furtividade", "per_alquimia", "per_disfarce", "per_esquiva"],
     "Adaga estilizada, espada curta, capa com capuz, 2 doses veneno fraco, kit disfarce e 30 PP.",
     "Ponto Vital: Contra alvo surpreso, reduz Margem de Critico em 1 e impoe -2 no teste de CON vs Golpe Devastador."),

    ("espiao", "11 - Espiao (1d6)", 6, 2, 1.00, "esp_submundo", 1,
     ["per_disfarce", "per_enganacao", "per_investigacao", "per_intuicao", "per_idiomas", "per_furtividade"],
     "Adaga oculta, kit de disfarce, tintas invisiveis, vestes de 2 estratos e 40 PP.",
     "Rede de Sussurros: Apos 24h na cidade (5 PP em subornos), localiza informante e ganha +3 para apurar segredos."),

    ("contrabandista", "12 - Contrabandista (1d8)", 8, 2, 0.75, "esp_submundo", 1,
     ["per_barganha", "per_enganacao", "per_navegacao", "per_furtividade", "per_esquiva"],
     "Sabre curto, besta leve, capa com bolsos falsos, bau de fundo duplo, mapas e 35 PP.",
     "Passagem Oculta: +3 para esconder cargas em revistas, subornar guardas ou achar saidas discretas."),

    ("cacador_rec", "13 - Cacador de Recompensas (1d8)", 8, 1, 0.75, None, 0,
     ["per_armas_dist", "per_sobrevivencia", "per_investigacao", "per_intimidacao", "per_percepcao"],
     "Besta leve (20 virotes), espada curta, algemas, rede de captura, couro batido e 25 PP.",
     "Presa Marcada: Estudando pistas de 1 alvo por 1h, recebe +2 para rastrea-lo e +1 em ataques contra ele."),

    ("charlatao", "14 - Charlatao / Vigario (1d6)", 6, 2, 1.00, None, 0,
     ["per_enganacao", "per_persuasao", "per_prestidig", "per_disfarce", "per_etiqueta", "per_intuicao"],
     "Adaga escondida, documentos falsos, selos de cera, dados viciados, roupas finas e 40 PP.",
     "Lingua de Prata: 1x por cena social, re-rola um teste falho de Enganacao ou Persuasao."),

    ("saqueador", "15 - Saqueador de Tumbas (1d8)", 8, 2, 0.75, None, 0,
     ["per_ladinagem", "per_escalada", "per_investigacao", "per_historia", "per_percepcao"],
     "Espada curta, pe-de-cabra, lanterna blindada, gazuas, corda 20m com arpeu, giz e 20 PP.",
     "Instinto de Ruina: +3 em Percepcao e Esquiva contra armadilhas mecanicas e desabamentos."),

    ("pirata", "16 - Pirata (1d8)", 8, 1, 0.75, "esp_submundo", 1,
     ["per_armas_brancas", "per_navegacao", "per_escalada", "per_acrobacia", "per_intimidacao"],
     "Sabre/cimitarra, adaga de abordagem, gancho com corda, roupas maritimas, rum e 25 PP.",
     "Abordagem Selvagem: Ignora penalidade de conves/recifes e ganha +2 no ataque no 1o turno de abordagem."),

    ("navegador", "17 - Navegador / Marinheiro (1d8)", 8, 2, 0.75, None, 0,
     ["per_navegacao", "per_geografia", "per_natacao", "per_percepcao", "per_sobrevivencia"],
     "Espada curta, astrolabio/bussola de latao, cartas nauticas, capa impermeavel e 30 PP.",
     "Olho da Tempestade: +3 em Navegacao por recifes e neblina; percebe tempestades horas antes (CD 15)."),

    ("explorador", "18 - Explorador / Cartografo (1d8)", 8, 2, 1.00, None, 0,
     ["per_geografia", "per_sobrevivencia", "per_percepcao", "per_escalada", "per_idiomas"],
     "Espada curta ou arco curto, estojo de cartografia, luneta, botas reforcadas, tenda e 30 PP.",
     "Sem Fronteiras: +4 para nao se perder sob ceu aberto e -25% no tempo de marcha em clima bom (neblina/Incognito exigem teste)."),

    ("patrulheiro", "19 - Patrulheiro / Rastreador (1d8)", 8, 1, 0.75, None, 0,
     ["per_sobrevivencia", "per_armas_dist", "per_furtividade", "per_percepcao", "per_herbalismo"],
     "Arco curto/longo (20 flechas), machadinha, couro batido, lacos de caca, capa e 20 PP.",
     "Cacador das Ermas: Em biomas com fauna/flora (2h, CD 12), sustenta ate 4 viajantes; em desertos, +3 para achar pocos e racoes rendem +50%."),

    ("mercador", "20 - Mercador / Caravaneiro (1d6)", 6, 2, 1.00, "esp_status", 1,
     ["per_barganha", "per_persuasao", "per_idiomas", "per_cavalgar", "per_intuicao"],
     "Besta leve, adaga, livro-razao, balanca portatil, mula com alforjes e 60 PP.",
     "Olhar de Ouro: Estima faixas de valor comuns, +4 contra fraudes e ate 15% de vantagem comercial (reliquias raras exigem teste)."),

    ("domador", "21 - Domador / Cavaleiro de Estrada (1d8)", 8, 1, 0.75, None, 0,
     ["per_cavalgar", "per_sobrevivencia", "per_herbalismo", "per_armas_brancas", "per_percepcao"],
     "Lanca leve ou sabre, couro batido, cavalo treinado (ou cao fiel), arreios e 20 PP.",
     "Elo da Sela: Sua montaria/animal recebe +3 contra panico e +2 na Defesa enquanto guiado por voce."),

    ("ferreiro", "22 - Ferreiro / Armeiro (1d8)", 8, 1, 0.75, None, 0,
     ["per_forja", "per_armas_brancas", "per_atletismo", "per_barganha", "per_engenharia"],
     "Martelo de guerra/forja, avental de couro pesado (Def +2), ferramentas de reparo e 30 PP.",
     "Tempera de Mestre: Em descanso longo, ajusta ate 3 armas/armaduras (+1 dano em armas comuns ate o proximo descanso)."),

    ("alquimista", "23 - Alquimista (1d6)", 6, 2, 1.00, None, 0,
     ["per_alquimia", "per_herbalismo", "per_investigacao", "per_medicina", "per_barganha"],
     "Adaga, bolsa alquimica, 2 frascos de acido (2d4), 2 bombas de fumaca, antidoto e 35 PP.",
     "Preparos de Campanha: Em descanso longo (3 PP/dose), prepara 1+max(0,INT) misturas mundanas (balsamo 1d6, acido 2d4, fumaca, antidoto)."),

    ("medico", "24 - Medico / Cirurgiao (1d6)", 6, 2, 1.00, None, 0,
     ["per_medicina", "per_herbalismo", "per_investigacao", "per_intuicao", "per_alquimia"],
     "Bisturis de aco fino, agulhas e fio cirurgico, alcool, ataduras, balsamos, adaga e 35 PP.",
     "Maos que Salvam: +4 para estabilizar moribundos, estanca sangramento usando Movimento, cura 1d6+max(0,INT) pos-combate e +4 contra sequelas."),

    ("erudito", "25 - Erudito / Historiador (1d6)", 6, 2, 1.25, None, 0,
     ["per_historia", "per_idiomas", "per_geografia", "per_investigacao", "per_religiao", "per_etiqueta"],
     "Bastao ferrado, diarios de viagem, tinteiro, lupas, cartas academicas e 40 PP.",
     "Memoria Enciclopedica: Maior mult. de INT (1.25x); 1x/sessao obtem pista concreta de historia, heraldica ou idioma sem rolar."),

    ("engenheiro", "26 - Engenheiro / Artifice (1d6)", 6, 2, 1.00, None, 0,
     ["per_engenharia", "per_forja", "per_ladinagem", "per_investigacao", "per_armas_dist"],
     "Besta de precisao (sem polvora), ferramentas mecanicas, polias, arames, compasso e 35 PP.",
     "Engenhosidade Mecanica: Constroi e desarma armadilhas, fechaduras e engenhos na metade do tempo com +3."),

    ("herbalista", "27 - Herbalista / Boticario (1d6)", 6, 2, 1.00, None, 0,
     ["per_herbalismo", "per_medicina", "per_sobrevivencia", "per_alquimia", "per_percepcao"],
     "Foice curva/adaga, prensa de ervas, pilao, bolsa de raizes, 3 cataplasmas e 25 PP.",
     "Farmacia Viva: Em matas, pantanos ou oasis (1h, CD 13), prepara 2 cataplasmas ou sonifero leve sem gastar moedas."),

    ("astronomo", "28 - Astronomo / Sabio (1d6)", 6, 2, 1.25, None, 0,
     ["per_geografia", "per_navegacao", "per_historia", "per_percepcao", "per_intuicao"],
     "Bastao/adaga, luneta de latao, astrolabio de bolso, mapas estelares, caderno e 35 PP.",
     "Leitura dos Ceus: +4 em orientacao noturna, previsao de mares e rotas sob ceu limpo (Mar Intransponivel/Incognito permanecem incertos)."),

    ("carpinteiro", "29 - Carpinteiro / Artesao (1d8)", 8, 1, 0.75, None, 0,
     ["per_engenharia", "per_atletismo", "per_sobrevivencia", "per_navegacao", "per_barganha"],
     "Machadinha, serra, pregos, martelo, cordas, gibao reforcado e 25 PP.",
     "Maos de Obra: Repara cascos (+2d6 integridade/hora), carrocas e barricadas dobrando resistencia de fortificacoes."),

    ("nobre", "30 - Nobre (1d6)", 6, 2, 0.75, "esp_status", 2,
     ["per_etiqueta", "per_persuasao", "per_historia", "per_cavalgar", "per_armas_brancas"],
     "Florete ou espada longa fina, anel de sinete, vestes nobres, manto, cavalo e 80 PP.",
     "Peso do Nome: Invoca hospitalidade, audiencias e credito em cidades usando Status sem rolar em pedidos rotineiros."),

    ("diplomata", "31 - Diplomata / Conselheiro (1d6)", 6, 2, 1.00, "esp_status", 1,
     ["per_persuasao", "per_intuicao", "per_etiqueta", "per_enganacao", "per_idiomas"],
     "Adaga discreta, cartas credenciais, pergaminhos e lacres, roupas de corte e 55 PP.",
     "Palavra que Desarma: +3 em Persuasao/Intuicao para firmar treguas ou extrair concessoes politicas."),

    ("bardo", "32 - Bardo / Menestrel (1d6)", 6, 2, 1.00, None, 0,
     ["per_persuasao", "per_enganacao", "per_historia", "per_etiqueta", "per_disfarce", "per_percepcao"],
     "Instrumento musical, adaga ou espada curta, roupas discretas e de apresentacao, caderno e 30 PP.",
     "Cronica de Taverna: Cobre hospedagem simples tocando e recebe +3 para captar boatos e segredos de viajantes."),

    ("sacerdote", "33 - Sacerdote / Clerigo (1d6)", 6, 2, 0.75, "esp_fe", 1,
     ["per_religiao", "per_persuasao", "per_medicina", "per_intuicao", "per_historia"],
     "Cajado ou maca simples, simbolo sagrado autentico, vestes clericais, unguentos e 25 PP.",
     "Conforto da Fe: 1x/descanso, prece sincera concede +2 em testes mentais e contra medo/horror para aliados na cena."),

    ("inquisidor", "34 - Inquisidor (1d8)", 8, 1, 0.75, "esp_fe", 1,
     ["per_intimidacao", "per_investigacao", "per_religiao", "per_intuicao", "per_armas_brancas"],
     "Espada longa ou martelo de guerra, manto com insignia, algemas, couro batido e 30 PP.",
     "Vontade Inabalavel: Soma Fe Verdadeira em testes contra medo, intimidacao, manipulacoes e horrores."),

    ("ermitao", "35 - Ermitao / Sobrevivente (1d8)", 8, 1, 0.75, None, 0,
     ["per_sobrevivencia", "per_herbalismo", "per_percepcao", "per_intuicao", "per_furtividade"],
     "Lanca de caca ou cajado, facao, manto espesso contra frio/chuva, pederneira e 10 PP.",
     "Casca Grossa: +3 em testes contra frio extremo, calor desertico, doencas comuns e niveis de Exaustao."),

    ("dom_antigo", "36 - Tocado pelo Dom Antigo (1d6 | Mestre)", 6, 2, 1.00, "esp_dom", 1,
     ["per_religiao", "per_intuicao", "per_historia", "per_sobrevivencia", "per_percepcao"],
     "Adaga ritualistica antiga, amuleto de origem desconhecida, manto gasto, caderno de visoes e 15 PP.",
     "Ecos do Que Nao Dorme: Visoes/pressagios raros a criterio do Mestre; rituais ancestrais (Secao 10 do Livro de Regras)."),
]


def lua_str(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def build_lua_script() -> str:
    kits_lua = ["local KITS = {"]
    for k in KITS:
        kid, kname, dv_faces, per_b, m_int, esp_f, esp_v, per_list, equip, hab = k
        plist = ", ".join(lua_str(p) for p in per_list)
        esp_field_lua = lua_str(esp_f) if esp_f else "nil"
        kits_lua.append(
            f"    [{lua_str(kid)}] = {{ nome={lua_str(kname)}, dv={dv_faces}, perBase={per_b}, multInt={m_int}, "
            f"espField={esp_field_lua}, espVal={esp_v}, pericias={{ {plist} }}, equip={lua_str(equip)}, hab={lua_str(hab)} }},"
        )
    kits_lua.append("};")

    skills_lua = ["local SKILLS = {"]
    for fid, sname, sattr, scat in SKILLS:
        skills_lua.append(f"    {{ field={lua_str(fid)}, nome={lua_str(sname)}, attr={lua_str(sattr)} }},")
    skills_lua.append("};")

    lua = "\n".join(kits_lua) + "\n\n" + "\n".join(skills_lua) + r"""

local recalcularFicha;
local atualizarPaginaCustomSkills;

local function num(v, def)
    local n = tonumber(v);
    if n == nil then return def or 0; end;
    return n;
end;

local function fmtMod(m)
    if m >= 0 then return "+" .. tostring(m); end;
    return tostring(m);
end;

local function getMod(attrField)
    if sheet == nil then return 0; end;
    local raw = sheet[attrField];
    if raw == nil or tostring(raw) == "" then return 0; end;
    local val = tonumber(raw);
    if val == nil then return 0; end;
    return math.floor((val - 10) / 2);
end;

local function getPatamarInfo(nivel)
    if nivel >= 21 then
        return "Epico (2x Per)", 2.0;
    elseif nivel >= 11 then
        return "Lenda (1.5x Per)", 1.5;
    else
        return "Recruta (1x Per)", 1.0;
    end;
end;

local function enviarChatOuMsg(texto)
    local mesa = Firecast.getMesaDe(sheet);
    if mesa ~= nil and mesa.activeChat ~= nil then
        mesa.activeChat:enviarMensagem(texto);
    else
        showMessage(texto);
    end;
end;

local function rolarD20(titulo, modTotal, detalheExtra)
    if sheet == nil then return; end;
    local modStr = "";
    if modTotal >= 0 then
        modStr = " + " .. tostring(modTotal);
    else
        modStr = " - " .. tostring(math.abs(modTotal));
    end;
    local rolagem = Firecast.interpretarRolagem("1d20" .. modStr);
    local nomeChar = sheet.nome or "Explorador";
    local cabecalho = "[" .. nomeChar .. "] " .. titulo;
    local mesa = Firecast.getMesaDe(sheet);
    if mesa ~= nil and mesa.activeChat ~= nil then
        mesa.activeChat:rolarDados(rolagem, cabecalho,
            function(rolado)
                local d20Nat = nil;
                if rolado ~= nil and rolado.ops ~= nil then
                    for i = 1, #rolado.ops do
                        local op = rolado.ops[i];
                        if op.tipo == "dado" and op.resultados ~= nil and #op.resultados >= 1 then
                            d20Nat = op.resultados[1];
                            break;
                        end;
                    end;
                end;
                if d20Nat == 20 then
                    mesa.activeChat:enviarMensagem("[20 NATURAL] Sucesso Critico de " .. nomeChar .. " em " .. titulo .. "!");
                elseif d20Nat == 1 then
                    mesa.activeChat:enviarMensagem("[1 NATURAL] Falha Critica de " .. nomeChar .. " em " .. titulo .. "!");
                elseif detalheExtra ~= nil and detalheExtra ~= "" then
                    mesa.activeChat:enviarMensagem(detalheExtra);
                end;
            end);
    else
        rolagem:rolarLocalmente();
        showMessage(cabecalho .. "\nResultado: " .. tostring(rolagem.resultado));
    end;
end;

local function rolarAtributosIniciais()
    if sheet == nil then return; end;
    local campos = {
        { field="forca", label="FOR" },
        { field="destreza", label="DES" },
        { field="constituicao", label="CON" },
        { field="inteligencia", label="INT" },
        { field="sabedoria", label="SAB" },
        { field="carisma", label="CAR" }
    };
    for i = 1, #campos do
        local v = sheet[campos[i].field];
        if v ~= nil and tostring(v):gsub("%s+", "") ~= "" then
            showMessage("A rolagem inicial 4d6 so funciona quando TODOS os 6 atributos base estiverem vazios! Limpe os campos apenas com permissao do Mestre.");
            return;
        end;
    end;

    math.randomseed(os.time() + math.floor((os.clock() or 0) * 10000));
    local linhas = {};
    local nomeChar = sheet.nome or "Novo Explorador";
    table.insert(linhas, "=== ROLAGEM INICIAL DE ATRIBUTOS (4d6 descarta menor) — " .. nomeChar .. " ===");
    local somaTotal = 0;

    for i = 1, #campos do
        local d = { math.random(1, 6), math.random(1, 6), math.random(1, 6), math.random(1, 6) };
        local menorIdx = 1;
        for j = 2, 4 do
            if d[j] < d[menorIdx] then menorIdx = j; end;
        end;
        local total = (d[1] + d[2] + d[3] + d[4]) - d[menorIdx];
        sheet[campos[i].field] = tostring(total);
        somaTotal = somaTotal + total;
        local mod = math.floor((total - 10) / 2);
        table.insert(linhas, campos[i].label .. ": [" .. d[1] .. ", " .. d[2] .. ", " .. d[3] .. ", " .. d[4] .. "] (descarta " .. d[menorIdx] .. ") => " .. total .. " (" .. fmtMod(mod) .. ")");
    end;
    table.insert(linhas, "Soma dos 6 Atributos: " .. tostring(somaTotal));

    recalcularFicha();
    enviarChatOuMsg(table.concat(linhas, "\n"));
end;

local function rolarSubirNivelPV()
    if sheet == nil then return; end;
    local dv = math.max(4, math.floor(num(sheet.kitDvFaces, 8)));
    local mCon = getMod("constituicao");
    local modStr = "";
    if mCon >= 0 then modStr = " + " .. tostring(mCon);
    else modStr = " - " .. tostring(math.abs(mCon)); end;

    local nomeChar = sheet.nome or "Explorador";
    local expr = "1d" .. tostring(dv) .. modStr;
    local rolagem = Firecast.interpretarRolagem(expr);
    local titulo = "[" .. nomeChar .. "] Subir Nivel — PV (1d" .. tostring(dv) .. modStr .. ")";

    local function aplicarGanho(res)
        local ganho = math.max(1, res);
        local pvM = num(sheet.pvMax, 0) + ganho;
        local pvA = num(sheet.pvAtual, 0) + ganho;
        sheet.pvMax = tostring(pvM);
        sheet.pvAtual = tostring(pvA);
        local niv = math.min(30, math.floor(num(sheet.nivel, 1)) + 1);
        sheet.nivel = tostring(niv);
        recalcularFicha();
    end;

    local mesa = Firecast.getMesaDe(sheet);
    if mesa ~= nil and mesa.activeChat ~= nil then
        mesa.activeChat:rolarDados(rolagem, titulo,
            function(rolado)
                if rolado ~= nil then
                    local ganho = math.max(1, rolado.resultado);
                    aplicarGanho(ganho);
                    mesa.activeChat:enviarMensagem("[" .. nomeChar .. "] Avancou para Nivel " .. tostring(sheet.nivel) .. "! Ganhou +" .. tostring(ganho) .. " PV (Novo PV Max: " .. tostring(sheet.pvMax) .. ").");
                end;
            end);
    else
        rolagem:rolarLocalmente();
        local ganho = math.max(1, rolagem.resultado);
        aplicarGanho(ganho);
        showMessage(titulo .. "\nGanho: +" .. tostring(ganho) .. " PV (Nivel " .. tostring(sheet.nivel) .. ", PV Max: " .. tostring(sheet.pvMax) .. ")");
    end;
end;

-- Graduacao numerica livre (+0, +1, +2, +3...) com classificacao automatica de grau:
-- 0 = Destreinado | 1-2 = Iniciante | 3-7 = Treinado | 8-11 = Especialista (Niv 5+) | 12+ = Mestre (Niv 11+)
local function nomeGrau(grau, nivel)
    local g = math.floor(num(grau, 0));
    local niv = math.floor(num(nivel, 1));
    if g >= 12 then
        if niv < 11 then return "Mestre (N11+)"; end;
        return "Mestre";
    elseif g >= 8 then
        if niv < 5 then return "Espec. (N5+)"; end;
        return "Especialista";
    elseif g >= 3 then
        return "Treinado";
    elseif g >= 1 then
        return "Iniciante";
    else
        return "Destreinado";
    end;
end;

-- Custo progressivo por graduacao: 1-7 = 1 pt cada | 8-11 = 2 pts cada | 12+ = 3 pts cada
local function custoGrau(grau)
    local g = math.max(0, math.floor(num(grau, 0)));
    if g <= 7 then
        return g;
    elseif g <= 11 then
        return 7 + (g - 7) * 2;
    else
        return 15 + (g - 11) * 3;
    end;
end;

recalcularFicha = function()
    if sheet == nil then return; end;

    local mFor = getMod("forca");
    local mDes = getMod("destreza");
    local mCon = getMod("constituicao");
    local mInt = getMod("inteligencia");
    local mSab = getMod("sabedoria");
    local mCar = getMod("carisma");

    sheet.mod_for = fmtMod(mFor);
    sheet.mod_des = fmtMod(mDes);
    sheet.mod_con = fmtMod(mCon);
    sheet.mod_int = fmtMod(mInt);
    sheet.mod_sab = fmtMod(mSab);
    sheet.mod_car = fmtMod(mCar);

    local nivel = math.max(1, math.min(30, math.floor(num(sheet.nivel, 1))));
    local patNome, _ = getPatamarInfo(nivel);
    sheet.patamarTexto = patNome;

    local kitId = sheet.kitSelecionado or "sem_kit";
    local kit = KITS[kitId] or KITS["sem_kit"];

    local dvFaces = math.max(4, math.floor(num(sheet.kitDvFaces, kit.dv)));
    local perBase = num(sheet.kitPerBase, kit.perBase);
    local multInt = num(sheet.kitMultInt, kit.multInt);

    local conRaw = num(sheet.constituicao, 10);
    local intPos = math.max(0, mInt);

    -- PV Medio Sugerido (Niv 1 = DV_Max + CON bruto; Niv 2+ = media fixa ceil(DV/2)+1 + Mod CON, min 1)
    local mediaDv = math.floor(dvFaces / 2) + 1;
    local ganhoFixoPv = math.max(1, mediaDv + mCon);
    local pvCalc = (dvFaces + conRaw) + (nivel - 1) * ganhoFixoPv;

    -- Pericias Recalibradas v2.0 (sem x2 inflado no Niv 1; aplica max(0, Mod INT) uniformemente)
    local perCalc = math.max(2, math.floor(perBase + intPos * multInt));
    for lv = 2, nivel do
        local _, fm = getPatamarInfo(lv);
        local ganhoPer = math.max(1, math.floor((perBase + intPos * multInt) * fm));
        perCalc = perCalc + ganhoPer;
    end;

    local _, proxFm = getPatamarInfo(math.min(30, nivel + 1));
    local proxPer = math.max(1, math.floor((perBase + intPos * multInt) * proxFm));
    local aumentosAttr = math.floor(nivel / 3);

    sheet.pvSugerido = tostring(pvCalc);
    sheet.proxNivelPv = "1d" .. tostring(dvFaces) .. fmtMod(mCon) .. " (fixo +" .. tostring(ganhoFixoPv) .. ")";
    sheet.periciasSugeridas = tostring(perCalc);
    sheet.proxNivelPer = "+" .. tostring(proxPer) .. " pts/niv";
    sheet.aumentosAtributo = tostring(aumentosAttr);

    local pvMax = num(sheet.pvMax, pvCalc);
    if pvMax <= 0 then pvMax = pvCalc; end;
    local limiarDev = math.floor((pvMax * 2) / 3) + 1;
    sheet.limiarDevastador = tostring(limiarDev) .. "+ dano";

    local forRaw = num(sheet.forca, 10);
    sheet.cargaMax = tostring(forRaw * 5) .. " kg";

    -- Desconta 3 pts gratuitos das pericias iniciais (+3) do Kit atual
    local kitGratis = {};
    for i = 1, #kit.pericias do kitGratis[kit.pericias[i]] = true; end;

    local ptsGastos = 0;
    for i = 1, #SKILLS do
        local sk = SKILLS[i];
        local grau = num(sheet[sk.field .. "_grau"], 0);
        local outros = num(sheet[sk.field .. "_outros"], 0);
        local tot = getMod(sk.attr) + grau + outros;
        sheet[sk.field .. "_total"] = fmtMod(tot);
        sheet[sk.field .. "_rank"] = nomeGrau(grau, nivel);
        local c = custoGrau(grau);
        if kitGratis[sk.field] then c = math.max(0, c - 3); end;
        ptsGastos = ptsGastos + c;
    end;

    local pagina = math.max(1, math.floor(num(sheet.customSkillPage, 1)));
    sheet.customSkillPageLabel = "Pag. " .. tostring(pagina);
    if sheet.customSkills ~= nil then
        local filhos = NDB.getChildNodes(sheet.customSkills);
        for i = 1, #filhos do
            ptsGastos = ptsGastos + custoGrau(filhos[i].grau);
        end;
    end;
    sheet.periciasGastas = tostring(ptsGastos);

    atualizarPaginaCustomSkills();

    local armDef = num(sheet.armaduraDef, 0);
    local escDef = num(sheet.escudoDef, 0);
    local defOutros = num(sheet.defesaOutros, 0);
    local trAparar = num(sheet.per_aparar_grau, 0) + num(sheet.per_aparar_outros, 0);
    local trEsquiva = num(sheet.per_esquiva_grau, 0) + num(sheet.per_esquiva_outros, 0);

    sheet.defAparar = tostring(10 + mDes + armDef + escDef + trAparar + defOutros);
    sheet.defEsquiva = tostring(10 + mDes + armDef + escDef + trEsquiva + defOutros);
    sheet.defDesprevenido = tostring(10 + armDef + escDef + defOutros);

    local trPerc = num(sheet.per_percepcao_grau, 0);
    sheet.iniciativaTotal = fmtMod(mDes + math.floor(trPerc / 3) + num(sheet.iniciativaOutros, 0));

    for idx = 1, 4 do
        local aAttr = sheet["arma" .. idx .. "_attr"] or "forca";
        local aPer = sheet["arma" .. idx .. "_per"] or "per_armas_brancas";
        local aExtra = num(sheet["arma" .. idx .. "_extra"], 0);
        local atkTot = getMod(aAttr) + num(sheet[aPer .. "_grau"], 0) + num(sheet[aPer .. "_outros"], 0) + aExtra;
        sheet["arma" .. idx .. "_atk"] = fmtMod(atkTot);
    end;
end;

local function aplicarKitSelecionado()
    if sheet == nil then return; end;
    local kitId = sheet.kitSelecionado or "sem_kit";
    local kit = KITS[kitId] or KITS["sem_kit"];

    sheet.kitNomeAtual = kit.nome;
    sheet.kitDvFaces = tostring(kit.dv);
    sheet.kitPerBase = tostring(kit.perBase);
    sheet.kitMultInt = tostring(kit.multInt);
    sheet.kitHabilidade = kit.hab;

    for i = 1, #kit.pericias do
        local pf = kit.pericias[i] .. "_grau";
        local atual = num(sheet[pf], 0);
        if atual < 3 then
            sheet[pf] = "3";
        end;
    end;

    if kit.espField ~= nil and kit.espVal > 0 then
        local atualEsp = num(sheet[kit.espField], 0);
        if atualEsp < kit.espVal then
            sheet[kit.espField] = tostring(kit.espVal);
        end;
    end;

    local invAtual = sheet.equipamentoMochila or "";
    if invAtual:gsub("%s+", "") == "" then
        sheet.equipamentoMochila = "[Equipamento do Kit - " .. kit.nome .. "]\n" .. kit.equip;
    else
        sheet.equipamentoMochila = invAtual .. "\n\n[Kit Aplicado - " .. kit.nome .. "]\n" .. kit.equip;
    end;

    recalcularFicha();

    if sheet.pvMax == nil or tostring(sheet.pvMax):gsub("%s+", "") == "" or num(sheet.pvMax, 0) <= 0 then
        sheet.pvMax = sheet.pvSugerido;
        sheet.pvAtual = sheet.pvSugerido;
    end;

    showMessage("Kit aplicado: " .. kit.nome .. "\nDado de Vida: 1d" .. tostring(kit.dv) .. " | Pericias Base: " .. tostring(kit.perBase) .. " (Mult INT " .. tostring(kit.multInt) .. "x)");
end;

local function rolarPericia(fieldId, nomePer, attrField)
    if sheet == nil then return; end;
    local g = num(sheet[fieldId .. "_grau"], 0);
    local tot = getMod(attrField) + g + num(sheet[fieldId .. "_outros"], 0);
    local rk = nomeGrau(g, sheet.nivel);
    rolarD20("Pericia: " .. nomePer .. " (+" .. tostring(g) .. " — " .. rk .. ")", tot, "");
end;

local function maxAcoesPorGrau(grau)
    local g = num(grau, 0);
    if g >= 12 then return 4;
    elseif g >= 8 then return 3;
    elseif g >= 3 then return 2;
    else return 1; end;
end;

local function rolarArma(idx)
    if sheet == nil then return; end;
    local nomeArma = sheet["arma" .. idx .. "_nome"];
    if nomeArma == nil or nomeArma == "" then nomeArma = "Arma " .. tostring(idx); end;
    local aAttr = sheet["arma" .. idx .. "_attr"] or "forca";
    local aPer = sheet["arma" .. idx .. "_per"] or "per_armas_brancas";
    local aExtra = num(sheet["arma" .. idx .. "_extra"], 0);
    local margem = num(sheet["arma" .. idx .. "_margem"], 20);
    local mult = num(sheet["arma" .. idx .. "_mult"], 2);
    local nAcoes = math.max(1, math.min(4, math.floor(num(sheet.multiAcoes, 1))));

    local grauPer = num(sheet[aPer .. "_grau"], 0);
    local limiteN = maxAcoesPorGrau(grauPer);
    if nAcoes > limiteN then
        showMessage("Multiplas Acoes bloqueadas pela regra v2.0!\nSeu grau nesta pericia (+" .. tostring(grauPer) .. ") permite no maximo " .. tostring(limiteN) .. " acao(oes) por turno.");
        return;
    end;

    local bonusBase = getMod(aAttr) + grauPer + num(sheet[aPer .. "_outros"], 0) + aExtra;
    local bonusFinal = bonusBase;
    if nAcoes > 1 then
        bonusFinal = math.floor(bonusBase / nAcoes) - nAcoes;
        if bonusFinal < 0 then
            showMessage("Multiplas Acoes bloqueadas (Regra Anti-Abuso v2.0)!\nDividir +" .. tostring(bonusBase) .. " em " .. tostring(nAcoes) .. " acoes resulta em bonus negativo (" .. tostring(bonusFinal) .. "). Reduza o numero de acoes!");
            return;
        end;
    end;

    local nomeChar = sheet.nome or "Explorador";
    local mesa = Firecast.getMesaDe(sheet);

    for k = 1, nAcoes do
        local sufixo = "";
        if nAcoes > 1 then
            sufixo = " (Acao " .. tostring(k) .. "/" .. tostring(nAcoes) .. " — Storyteller)";
        end;
        local modStr = "";
        if bonusFinal >= 0 then modStr = " + " .. tostring(bonusFinal);
        else modStr = " - " .. tostring(math.abs(bonusFinal)); end;

        local rolagem = Firecast.interpretarRolagem("1d20" .. modStr);
        local titulo = "[" .. nomeChar .. "] Ataque com " .. nomeArma .. sufixo;
        if mesa ~= nil and mesa.activeChat ~= nil then
            mesa.activeChat:rolarDados(rolagem, titulo,
                function(rolado)
                    local d20Nat = nil;
                    if rolado ~= nil and rolado.ops ~= nil then
                        for i = 1, #rolado.ops do
                            local op = rolado.ops[i];
                            if op.tipo == "dado" and op.resultados ~= nil and #op.resultados >= 1 then
                                d20Nat = op.resultados[1];
                                break;
                            end;
                        end;
                    end;
                    if d20Nat ~= nil then
                        if d20Nat >= margem then
                            mesa.activeChat:enviarMensagem("[CRITICO! Dado " .. tostring(d20Nat) .. " | Margem " .. tostring(margem) .. "-20] " .. nomeArma .. " multiplica (arma + attr + fixo) por x" .. tostring(mult) .. "!");
                        elseif d20Nat == 1 then
                            mesa.activeChat:enviarMensagem("[FALHA CRITICA! 1 Natural] Abertura tatica ou complicacao com " .. nomeArma .. "!");
                        end;
                    end;
                end);
        else
            rolagem:rolarLocalmente();
            showMessage(titulo .. "\nResultado: " .. tostring(rolagem.resultado));
        end;
    end;
end;

local function rolarDanoArma(idx, isCrit)
    if sheet == nil then return; end;
    local nomeArma = sheet["arma" .. idx .. "_nome"];
    if nomeArma == nil or nomeArma == "" then nomeArma = "Arma " .. tostring(idx); end;
    local dado = sheet["arma" .. idx .. "_dano"];
    if dado == nil or dado == "" then dado = "1d6"; end;
    local aAttr = sheet["arma" .. idx .. "_attr"] or "forca";
    local modDano = getMod(aAttr) + num(sheet["arma" .. idx .. "_danoExtra"], 0);
    local mult = num(sheet["arma" .. idx .. "_mult"], 2);

    local expr = dado;
    if modDano > 0 then expr = expr .. " + " .. tostring(modDano);
    elseif modDano < 0 then expr = expr .. " - " .. tostring(math.abs(modDano)); end;

    if isCrit then
        expr = "(" .. expr .. ") * " .. tostring(mult);
    end;

    local rolagem = Firecast.interpretarRolagem(expr);
    local nomeChar = sheet.nome or "Explorador";
    local tag = isCrit and ("DANO CRITICO (x" .. tostring(mult) .. ") — ") or "Dano — ";
    local titulo = "[" .. nomeChar .. "] " .. tag .. nomeArma;
    local mesa = Firecast.getMesaDe(sheet);
    if mesa ~= nil and mesa.activeChat ~= nil then
        mesa.activeChat:rolarDados(rolagem, titulo,
            function(rolado)
                if rolado ~= nil then
                    mesa.activeChat:enviarMensagem("Lembrete: se o dano (" .. tostring(rolado.resultado) .. ") superar 2/3 do PV Maximo do alvo, ele faz teste de CON ou sofre MORTE INSTANTANEA! (Dados bonus como veneno/Oportunista somam apos o critico.)");
                end;
            end);
    else
        rolagem:rolarLocalmente();
        showMessage(titulo .. "\nResultado: " .. tostring(rolagem.resultado));
    end;
end;

local function acaoDefensiva(modo)
    if sheet == nil then return; end;
    local nomeChar = sheet.nome or "Explorador";
    local maxTreino = math.max(num(sheet.per_aparar_grau, 0), num(sheet.per_esquiva_grau, 0), num(sheet.per_escudos_grau, 0));
    local bonus = 4;
    if maxTreino >= 12 then bonus = 8;
    elseif maxTreino >= 8 then bonus = 6; end;

    if modo == "propria" then
        enviarChatOuMsg("[ACAO DEFENSIVA — " .. nomeChar .. "] Sacrifica seu ataque para DEFESA TOTAL: recebe +" .. tostring(bonus) .. " na Defesa ate o proximo turno e impoe -2 nos ataques corpo a corpo contra si!");
    else
        enviarChatOuMsg("[PROTEGER ALIADO — " .. nomeChar .. "] Sacrifica seu ataque para defender um aliado adjacente: atacantes sofrem -" .. tostring(bonus) .. " no ataque contra o aliado (e " .. nomeChar .. " pode interceptar o golpe)!");
    end;
end;

local function getCustomSlotNode(slotIdx)
    if sheet == nil then return nil; end;
    if sheet.customSkills == nil then sheet.customSkills = {}; end;
    local pagina = math.max(1, math.floor(num(sheet.customSkillPage, 1)));
    local globalIdx = (pagina - 1) * 10 + slotIdx;
    local key = "sk" .. tostring(globalIdx);
    if sheet.customSkills[key] == nil then
        sheet.customSkills[key] = {};
    end;
    return sheet.customSkills[key], globalIdx;
end;

atualizarPaginaCustomSkills = function()
    if sheet == nil then return; end;
    sheet._updatingCustom = true;
    local niv = math.max(1, math.min(30, math.floor(num(sheet.nivel, 1))));
    for i = 1, 10 do
        local node = getCustomSlotNode(i);
        local nome = (node ~= nil and node.nome) or "";
        local attr = (node ~= nil and node.attr) or "inteligencia";
        local grau = (node ~= nil and node.grau) or "0";
        local outros = (node ~= nil and node.outros) or "0";
        sheet["csk" .. i .. "_nome"] = nome;
        sheet["csk" .. i .. "_attr"] = attr;
        sheet["csk" .. i .. "_grau"] = tostring(grau);
        sheet["csk" .. i .. "_rank"] = nomeGrau(grau, niv);
        sheet["csk" .. i .. "_outros"] = tostring(outros);
        local tot = getMod(attr) + num(grau, 0) + num(outros, 0);
        sheet["csk" .. i .. "_total"] = fmtMod(tot);
    end;
    sheet._updatingCustom = false;
end;

local function salvarCustomSlot(slotIdx)
    if sheet == nil or sheet._updatingCustom then return; end;
    local node = getCustomSlotNode(slotIdx);
    if node == nil then return; end;
    local niv = math.max(1, math.min(30, math.floor(num(sheet.nivel, 1))));
    node.nome = sheet["csk" .. slotIdx .. "_nome"] or "";
    node.attr = sheet["csk" .. slotIdx .. "_attr"] or "inteligencia";
    node.grau = sheet["csk" .. slotIdx .. "_grau"] or "0";
    node.outros = sheet["csk" .. slotIdx .. "_outros"] or "0";
    sheet["csk" .. slotIdx .. "_rank"] = nomeGrau(node.grau, niv);
    local tot = getMod(node.attr) + num(node.grau, 0) + num(node.outros, 0);
    sheet["csk" .. slotIdx .. "_total"] = fmtMod(tot);
end;

local function mudarPaginaCustom(delta)
    if sheet == nil then return; end;
    local pag = math.max(1, math.floor(num(sheet.customSkillPage, 1)) + delta);
    sheet.customSkillPage = tostring(pag);
    sheet.customSkillPageLabel = "Pag. " .. tostring(pag);
    atualizarPaginaCustomSkills();
end;

local function rolarCustomSkill(slotIdx)
    if sheet == nil then return; end;
    local nome = sheet["csk" .. slotIdx .. "_nome"];
    if nome == nil or nome == "" then nome = "Pericia Livre #" .. tostring(slotIdx); end;
    local attr = sheet["csk" .. slotIdx .. "_attr"] or "inteligencia";
    local grau = num(sheet["csk" .. slotIdx .. "_grau"], 0);
    local outros = num(sheet["csk" .. slotIdx .. "_outros"], 0);
    local rk = nomeGrau(grau, sheet.nivel);
    rolarD20("Pericia Livre: " .. nome .. " (+" .. tostring(grau) .. " — " .. rk .. ")", getMod(attr) + grau + outros, "");
end;
"""
    return lua


def lua_items_str(lst):
    return "{" + ", ".join("'" + s.replace("'", "\\'") + "'" for s in lst) + "}"


def xml_attr(val: str) -> str:
    return sax.escape(val, {'"': "&quot;"})


def build_lfm() -> str:
    kit_items = lua_items_str([k[1] for k in KITS])
    kit_values = lua_items_str([k[0] for k in KITS])

    dv_items = "{'1d6 (Esp/Erud)', '1d8 (Expl/Hib)', '1d10 (Comb)', '1d12 (Brutal)'}"
    dv_values = "{'6', '8', '10', '12'}"

    grau_items = "{'Destr. (+0)', 'Trein. (+3)', 'Espec. (+8)', 'Mestre (+12)'}"
    grau_values = "{'0', '3', '8', '12'}"

    attr_items = "{'FOR', 'DES', 'CON', 'INT', 'SAB', 'CAR'}"
    attr_values = "{'forca', 'destreza', 'constituicao', 'inteligencia', 'sabedoria', 'carisma'}"

    arma_attr_items = "{'FOR', 'DES'}"
    arma_attr_values = "{'forca', 'destreza'}"

    arma_per_items = "{'Armas Brancas', 'Armas Dist.', 'Desarmada'}"
    arma_per_values = "{'per_armas_brancas', 'per_armas_dist', 'per_luta_desarm'}"

    attrs_def = [
        ("forca", "mod_for", "FORCA", "FOR"),
        ("destreza", "mod_des", "DESTREZA", "DES"),
        ("constituicao", "mod_con", "CONSTITUICAO", "CON"),
        ("inteligencia", "mod_int", "INTELIGENCIA", "INT"),
        ("sabedoria", "mod_sab", "SABEDORIA", "SAB"),
        ("carisma", "mod_car", "CARISMA", "CAR"),
    ]
    attr_xml_blocks = []
    for i, (afield, mfield, alabel, asig) in enumerate(attrs_def):
        left_x = 12 + i * 170
        attr_xml_blocks.append(f'''
            <rectangle left="{left_x}" top="54" width="160" height="126" color="{BG_CARD_ALT}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="6" yradius="6">
                <label left="6" top="6" width="148" height="22" text="{alabel}" fontColor="{TEXT_GOLD}" fontSize="14" fontStyle="bold" horzTextAlign="center"/>
                <edit left="14" top="32" width="66" height="42" field="{afield}" type="number" fontColor="{TEXT_MAIN}" fontSize="22" fontStyle="bold" horzTextAlign="center"/>
                <rectangle left="86" top="32" width="60" height="42" color="{BG_INPUT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                    <label align="client" field="{mfield}" fontColor="{TEXT_GOLD}" fontSize="20" fontStyle="bold" horzTextAlign="center" vertTextAlign="center"/>
                </rectangle>
                <button left="14" top="84" width="132" height="32" text="Rolar {asig}" fontSize="14">
                    <event name="onClick"><![CDATA[rolarD20("Atributo {alabel}", getMod("{afield}"), "");]]></event>
                </button>
            </rectangle>''')

    esp_defs = [
        ("esp_status", "Status", "Nobreza, patente, renome"),
        ("esp_fe", "Fe Verdadeira", "Conviccao plural"),
        ("esp_submundo", "Submundo", "Redes de Kalis/guildas"),
        ("esp_dom", "Dom Antigo", "Rarissimo (Aval Mestre)"),
    ]
    esp_xml_blocks = []
    for i, (efield, elabel, ehint) in enumerate(esp_defs):
        lx = 12 + i * 204
        esp_xml_blocks.append(f'''
            <rectangle left="{lx}" top="46" width="196" height="104" color="{BG_CARD_ALT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="5" yradius="5">
                <label left="6" top="6" width="184" height="22" text="{elabel} (0-5)" fontColor="{TEXT_GOLD}" fontSize="14" fontStyle="bold" horzTextAlign="center"/>
                <label left="4" top="28" width="188" height="18" text="{ehint}" fontColor="{TEXT_MUTED}" fontSize="12" horzTextAlign="center"/>
                <edit left="14" top="54" width="62" height="38" field="{efield}" type="number" fontColor="{TEXT_MAIN}" fontSize="20" fontStyle="bold" horzTextAlign="center"/>
                <button left="84" top="54" width="98" height="38" text="Rolar" fontSize="14">
                    <event name="onClick"><![CDATA[rolarD20("Atributo Especial: {elabel}", num(sheet.{efield}, 0), "");]]></event>
                </button>
            </rectangle>''')

    esp_xml_blocks.append(f'''
            <rectangle left="828" top="46" width="196" height="104" color="{BG_CARD_ALT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="5" yradius="5">
                <edit left="8" top="8" width="180" height="32" field="esp_livre_nome" textPrompt="Especial Livre" fontColor="{TEXT_GOLD}" fontSize="13" horzTextAlign="center"/>
                <edit left="14" top="54" width="62" height="38" field="esp_livre" type="number" fontColor="{TEXT_MAIN}" fontSize="20" fontStyle="bold" horzTextAlign="center"/>
                <button left="84" top="54" width="98" height="38" text="Rolar" fontSize="14">
                    <event name="onClick"><![CDATA[rolarD20("Especial: " .. (sheet.esp_livre_nome or "Livre"), num(sheet.esp_livre, 0), "");]]></event>
                </button>
            </rectangle>''')

    weapon_rows = []
    for idx in range(1, 5):
        ty = 78 + (idx - 1) * 58
        weapon_rows.append(f'''
            <rectangle left="10" top="{ty}" width="1016" height="50" color="{BG_CARD_ALT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                <edit left="6" top="7" width="210" height="36" field="arma{idx}_nome" textPrompt="Arma {idx} (ex: Espada Longa)" fontSize="14"/>
                <comboBox left="222" top="7" width="70" height="36" field="arma{idx}_attr" items="{xml_attr(arma_attr_items)}" values="{xml_attr(arma_attr_values)}" fontSize="13"/>
                <comboBox left="296" top="7" width="136" height="36" field="arma{idx}_per" items="{xml_attr(arma_per_items)}" values="{xml_attr(arma_per_values)}" fontSize="13"/>
                <edit left="436" top="7" width="48" height="36" field="arma{idx}_extra" type="number" horzTextAlign="center" fontSize="14"/>
                <label left="488" top="7" width="54" height="36" field="arma{idx}_atk" fontColor="{TEXT_GOLD}" fontSize="16" fontStyle="bold" horzTextAlign="center" vertTextAlign="center"/>
                <edit left="546" top="7" width="76" height="36" field="arma{idx}_dano" textPrompt="1d8" horzTextAlign="center" fontSize="14"/>
                <edit left="626" top="7" width="46" height="36" field="arma{idx}_danoExtra" type="number" horzTextAlign="center" fontSize="14"/>
                <edit left="676" top="7" width="48" height="36" field="arma{idx}_margem" type="number" horzTextAlign="center" fontSize="14"/>
                <edit left="728" top="7" width="44" height="36" field="arma{idx}_mult" type="number" horzTextAlign="center" fontSize="14"/>
                <button left="778" top="7" width="84" height="36" text="Atacar" fontSize="14">
                    <event name="onClick"><![CDATA[rolarArma({idx});]]></event>
                </button>
                <button left="866" top="7" width="70" height="36" text="Dano" fontSize="13">
                    <event name="onClick"><![CDATA[rolarDanoArma({idx}, false);]]></event>
                </button>
                <button left="940" top="7" width="68" height="36" text="Crit" fontSize="13">
                    <event name="onClick"><![CDATA[rolarDanoArma({idx}, true);]]></event>
                </button>
            </rectangle>''')

    skill_rows = []
    attr_short = {
        "forca": "FOR", "destreza": "DES", "constituicao": "CON",
        "inteligencia": "INT", "sabedoria": "SAB", "carisma": "CAR"
    }
    for i, (fid, sname, sattr, scat) in enumerate(SKILLS):
        col = 0 if i < 17 else 1
        row = i if i < 17 else i - 17
        lx = 10 if col == 0 else 522
        ty = 60 + row * 42
        skill_rows.append(f'''
            <rectangle left="{lx}" top="{ty}" width="504" height="38" color="{BG_CARD_ALT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="3" yradius="3">
                <label left="6" top="4" width="168" height="30" text="{sname}" fontColor="{TEXT_MAIN}" fontSize="13" vertTextAlign="center"/>
                <label left="176" top="4" width="34" height="30" text="{attr_short[sattr]}" fontColor="{TEXT_MUTED}" fontSize="12" horzTextAlign="center" vertTextAlign="center"/>
                <edit left="212" top="4" width="42" height="30" field="{fid}_grau" type="number" horzTextAlign="center" fontColor="{TEXT_MAIN}" fontSize="14" fontStyle="bold"/>
                <rectangle left="256" top="5" width="96" height="28" color="{BG_INPUT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="3" yradius="3">
                    <label align="client" field="{fid}_rank" fontColor="{TEXT_GOLD}" fontSize="11" fontStyle="bold" horzTextAlign="center" vertTextAlign="center"/>
                </rectangle>
                <edit left="356" top="4" width="40" height="30" field="{fid}_outros" type="number" horzTextAlign="center" fontSize="14"/>
                <label left="400" top="4" width="44" height="30" field="{fid}_total" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold" horzTextAlign="center" vertTextAlign="center"/>
                <button left="448" top="4" width="50" height="30" text="d20" fontSize="13">
                    <event name="onClick"><![CDATA[rolarPericia("{fid}", "{sname}", "{sattr}");]]></event>
                </button>
            </rectangle>''')

    custom_rows = []
    for i in range(1, 11):
        col = 0 if i <= 5 else 1
        row = (i - 1) if i <= 5 else (i - 6)
        lx = 10 if col == 0 else 522
        ty = 70 + row * 42
        custom_rows.append(f'''
            <rectangle left="{lx}" top="{ty}" width="504" height="38" color="{BG_CARD_ALT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="3" yradius="3">
                <edit left="4" top="4" width="144" height="30" field="csk{i}_nome" textPrompt="Nova Pericia..." fontSize="13"/>
                <comboBox left="150" top="4" width="60" height="30" field="csk{i}_attr" items="{xml_attr(attr_items)}" values="{xml_attr(attr_values)}" fontSize="12"/>
                <edit left="212" top="4" width="42" height="30" field="csk{i}_grau" type="number" horzTextAlign="center" fontColor="{TEXT_MAIN}" fontSize="14" fontStyle="bold"/>
                <rectangle left="256" top="5" width="96" height="28" color="{BG_INPUT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="3" yradius="3">
                    <label align="client" field="csk{i}_rank" fontColor="{TEXT_GOLD}" fontSize="11" fontStyle="bold" horzTextAlign="center" vertTextAlign="center"/>
                </rectangle>
                <edit left="356" top="4" width="40" height="30" field="csk{i}_outros" type="number" horzTextAlign="center" fontSize="14"/>
                <label left="400" top="4" width="44" height="30" field="csk{i}_total" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold" horzTextAlign="center" vertTextAlign="center"/>
                <button left="448" top="4" width="50" height="30" text="d20" fontSize="13">
                    <event name="onClick"><![CDATA[rolarCustomSkill({i});]]></event>
                </button>
            </rectangle>''')

    recalc_fields = [
        "forca", "destreza", "constituicao", "inteligencia", "sabedoria", "carisma",
        "nivel", "pvMax", "kitSelecionado", "kitDvFaces", "kitPerBase", "kitMultInt",
        "armaduraDef", "escudoDef", "defesaOutros", "iniciativaOutros",
        "esp_status", "esp_fe", "esp_submundo", "esp_dom", "esp_livre"
    ]
    for fid, _, _, _ in SKILLS:
        recalc_fields.append(fid + "_grau")
        recalc_fields.append(fid + "_outros")
    for idx in range(1, 5):
        recalc_fields.extend([f"arma{idx}_attr", f"arma{idx}_per", f"arma{idx}_extra"])

    recalc_fields_lua = lua_items_str(recalc_fields)

    def_fields = [
        "nivel", "kitSelecionado", "kitNomeAtual", "kitDvFaces",
        "kitPerBase", "kitMultInt", "pvAtual", "pvMax", "armaduraDef", "escudoDef",
        "rdEspecial", "defesaOutros", "iniciativaOutros", "multiAcoes",
        "esp_status", "esp_fe", "esp_submundo", "esp_dom", "esp_livre",
        "customSkillPage", "moedasOuro", "moedasPrata", "moedasCobre"
    ]
    def_values = [
        "1", "sem_kit", "00 - Sem Kit (Livre / Media Padrao)", "8",
        "1", "0.75", "18", "18", "0", "0",
        "0", "0", "0", "1",
        "0", "0", "0", "0", "0",
        "1", "0", "25", "0"
    ]
    for idx in range(1, 5):
        def_fields.extend([f"arma{idx}_attr", f"arma{idx}_per", f"arma{idx}_extra", f"arma{idx}_danoExtra", f"arma{idx}_margem", f"arma{idx}_mult"])
        def_values.extend(["forca", "per_armas_brancas", "0", "0", "20", "2"])
    for fid, _, _, _ in SKILLS:
        def_fields.extend([fid + "_grau", fid + "_outros"])
        def_values.extend(["0", "0"])

    custom_datalinks = []
    for i in range(1, 11):
        cfields = lua_items_str([f"csk{i}_nome", f"csk{i}_attr", f"csk{i}_grau", f"csk{i}_outros"])
        custom_datalinks.append(f'''
    <dataLink fields="{xml_attr(cfields)}">
        <event name="onChange"><![CDATA[salvarCustomSlot({i}); recalcularFicha();]]></event>
    </dataLink>''')

    lfm = f'''<?xml version="1.0" encoding="UTF-8"?>
<form name="frmAleniaFicha" formType="sheetTemplate" dataType="br.com.alenia.rpg_oficial.ficha" title="Alenia RPG - Ficha Oficial" align="client" theme="dark">
    <script><![CDATA[
{build_lua_script()}
    ]]></script>

    <rectangle align="client" color="{BG_MAIN}">
        <!-- CABECALHO FIXO AMPLIADO -->
        <rectangle align="top" height="112" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="1" margins="{{left=6, right=6, top=6, bottom=4}}" xradius="6" yradius="6">
            <label left="12" top="6" width="260" height="24" text="ALENIA RPG — FICHA v2.0" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold"/>
            <label left="278" top="6" width="170" height="24" field="patamarTexto" fontColor="{TEXT_CRIMSON}" fontSize="14" fontStyle="bold"/>
            <label left="452" top="6" width="352" height="24" field="kitNomeAtual" fontColor="{TEXT_MUTED}" fontSize="14"/>
            <label left="810" top="6" width="220" height="24" text="Golpe Devastador (&gt;2/3):" fontColor="{TEXT_CRIMSON}" fontSize="13" horzTextAlign="trailing"/>

            <label left="12" top="34" width="240" height="18" text="NOME DO PERSONAGEM" fontColor="{TEXT_MUTED}" fontSize="12"/>
            <edit left="12" top="54" width="246" height="40" field="nome" textPrompt="Nome do explorador..." fontColor="{TEXT_MAIN}" fontSize="16" fontStyle="bold"/>

            <label left="268" top="34" width="240" height="18" text="ORIGEM / CIDADE NATAL" fontColor="{TEXT_MUTED}" fontSize="12"/>
            <edit left="268" top="54" width="236" height="40" field="origem" textPrompt="Altavanne, Baldbella, OX..." fontColor="{TEXT_MAIN}" fontSize="15"/>

            <label left="514" top="34" width="76" height="18" text="NIVEL" fontColor="{TEXT_GOLD}" fontSize="12" fontStyle="bold" horzTextAlign="center"/>
            <edit left="514" top="54" width="76" height="40" field="nivel" type="number" fontColor="{TEXT_GOLD}" fontSize="19" fontStyle="bold" horzTextAlign="center"/>

            <label left="600" top="34" width="164" height="18" text="PV (ATUAL / MAX)" fontColor="{TEXT_CRIMSON}" fontSize="12" fontStyle="bold" horzTextAlign="center"/>
            <edit left="600" top="54" width="74" height="40" field="pvAtual" type="number" fontColor="{TEXT_MAIN}" fontSize="18" fontStyle="bold" horzTextAlign="center"/>
            <label left="674" top="54" width="16" height="40" text="/" fontColor="{TEXT_MUTED}" fontSize="18" horzTextAlign="center" vertTextAlign="center"/>
            <edit left="690" top="54" width="74" height="40" field="pvMax" type="number" fontColor="{TEXT_CRIMSON}" fontSize="18" fontStyle="bold" horzTextAlign="center"/>

            <rectangle left="774" top="54" width="128" height="40" color="{BG_INPUT}" strokeColor="{BORDER_CRIMSON}" strokeSize="1" xradius="4" yradius="4">
                <label align="client" field="limiarDevastador" fontColor="{TEXT_CRIMSON}" fontSize="15" fontStyle="bold" horzTextAlign="center" vertTextAlign="center"/>
            </rectangle>

            <button left="912" top="54" width="118" height="40" text="Iniciativa" fontSize="14">
                <event name="onClick"><![CDATA[rolarD20("Iniciativa", getMod("destreza") + math.floor(num(sheet.per_percepcao_grau, 0) / 3) + num(sheet.iniciativaOutros, 0), "");]]></event>
            </button>
        </rectangle>

        <!-- 5 ABAS PRINCIPAIS -->
        <tabControl align="client" margins="{{left=6, right=6, top=0, bottom=6}}">

            <!-- ABA 1: PRINCIPAL & KIT -->
            <tab title="Principal &amp; Kit">
                <scrollBox align="client">
                    <layout left="0" top="0" width="1056" height="860">
                        <!-- ATRIBUTOS BASE -->
                        <rectangle left="6" top="6" width="1036" height="194" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="6" yradius="6">
                            <label left="12" top="12" width="540" height="26" text="ATRIBUTOS BASE (3 a 18 | Mod = floor((Valor-10)/2))" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold"/>
                            <button left="632" top="10" width="390" height="34" text="Rolar Atributos Iniciais (4d6 descarta menor)" fontSize="14">
                                <event name="onClick"><![CDATA[rolarAtributosIniciais();]]></event>
                            </button>
                            {"".join(attr_xml_blocks)}
                        </rectangle>

                        <!-- ATRIBUTOS ESPECIAIS (FEITOS) -->
                        <rectangle left="6" top="208" width="1036" height="164" color="{BG_CARD}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="6" yradius="6">
                            <label left="12" top="10" width="1010" height="26" text="ATRIBUTOS ESPECIAIS (0 a 5 — NAO SOBEM COM NIVEL, APENAS POR FEITOS)" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold"/>
                            {"".join(esp_xml_blocks)}
                        </rectangle>

                        <!-- SELETOR & AUTOMACAO DE KITS UNIVERSAIS -->
                        <rectangle left="6" top="380" width="1036" height="296" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="6" yradius="6">
                            <label left="12" top="10" width="800" height="26" text="KIT DE PERSONAGEM (36 OFICIOS UNIVERSAIS — DV 1d6 a 1d12)" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold"/>
                            <label left="12" top="44" width="110" height="34" text="Escolher Kit:" fontColor="{TEXT_MAIN}" fontSize="14" vertTextAlign="center"/>
                            <comboBox left="124" top="44" width="470" height="36" field="kitSelecionado" items="{xml_attr(kit_items)}" values="{xml_attr(kit_values)}" fontSize="14"/>
                            <button left="604" top="44" width="150" height="36" text="Aplicar Kit" fontSize="15">
                                <event name="onClick"><![CDATA[aplicarKitSelecionado();]]></event>
                            </button>
                            <button left="762" top="44" width="260" height="36" text="Subir Nivel (Rolar 1dX+CON)" fontSize="14">
                                <event name="onClick"><![CDATA[rolarSubirNivelPV();]]></event>
                            </button>

                            <label left="12" top="92" width="180" height="20" text="Dado de Vida (DV)" fontColor="{TEXT_GOLD}" fontSize="13"/>
                            <comboBox left="12" top="114" width="180" height="34" field="kitDvFaces" items="{xml_attr(dv_items)}" values="{xml_attr(dv_values)}" fontSize="13"/>

                            <label left="204" top="92" width="120" height="20" text="Per. Base/Niv." fontColor="{TEXT_MUTED}" fontSize="13"/>
                            <edit left="204" top="114" width="110" height="34" field="kitPerBase" type="number" horzTextAlign="center" fontSize="15"/>

                            <label left="326" top="92" width="120" height="20" text="Mult. INT (Per.)" fontColor="{TEXT_MUTED}" fontSize="13"/>
                            <edit left="326" top="114" width="110" height="34" field="kitMultInt" horzTextAlign="center" fontSize="15"/>

                            <button left="448" top="114" width="136" height="34" text="Usar PV Medio" fontSize="13">
                                <event name="onClick"><![CDATA[recalcularFicha(); sheet.pvMax = sheet.pvSugerido; sheet.pvAtual = sheet.pvSugerido;]]></event>
                            </button>

                            <label left="596" top="92" width="206" height="20" text="Kit de Lenda (Niv. 11-20)" fontColor="{TEXT_GOLD}" fontSize="13"/>
                            <edit left="596" top="114" width="206" height="34" field="kitLenda" textPrompt="(Futuro — Niv. 11+)" fontSize="14"/>

                            <label left="814" top="92" width="208" height="20" text="Kit Epico (Niv. 21-30)" fontColor="{TEXT_CRIMSON}" fontSize="13"/>
                            <edit left="814" top="114" width="208" height="34" field="kitEpico" textPrompt="(Futuro — Niv. 21+)" fontSize="14"/>

                            <label left="12" top="158" width="460" height="22" text="HABILIDADE EXCLUSIVA DO KIT" fontColor="{TEXT_GOLD}" fontSize="14" fontStyle="bold"/>
                            <textEditor left="12" top="184" width="1010" height="100" field="kitHabilidade" fontSize="14"/>
                        </rectangle>

                        <!-- PAINEL AUTOMATICO DE EVOLUCAO -->
                        <rectangle left="6" top="684" width="1036" height="162" color="{BG_CARD}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="6" yradius="6">
                            <label left="12" top="10" width="1012" height="24" text="EVOLUCAO v2.0 (PV = 1dX+CON/niv | Pericias: Recruta 1x, Lenda 1.5x, Epico 2x | Graduacao: 1-7 [1p], 8-11 [2p, N5+], 12+ [3p, N11+])" fontColor="{TEXT_GOLD}" fontSize="12" fontStyle="bold"/>

                            <rectangle left="12" top="42" width="194" height="106" color="{BG_CARD_ALT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="5" yradius="5">
                                <label left="4" top="8" width="186" height="20" text="PV MEDIO SUGERIDO" fontColor="{TEXT_MUTED}" fontSize="12" fontStyle="bold" horzTextAlign="center"/>
                                <label left="4" top="32" width="186" height="38" field="pvSugerido" fontColor="{TEXT_GREEN}" fontSize="26" fontStyle="bold" horzTextAlign="center"/>
                                <label left="4" top="76" width="186" height="20" field="proxNivelPv" fontColor="{TEXT_MUTED}" fontSize="12" horzTextAlign="center"/>
                            </rectangle>

                            <rectangle left="216" top="42" width="194" height="106" color="{BG_CARD_ALT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="5" yradius="5">
                                <label left="4" top="8" width="186" height="20" text="PTS PERICIA TOTAIS" fontColor="{TEXT_MUTED}" fontSize="12" fontStyle="bold" horzTextAlign="center"/>
                                <label left="4" top="32" width="186" height="38" field="periciasSugeridas" fontColor="{TEXT_GOLD}" fontSize="26" fontStyle="bold" horzTextAlign="center"/>
                                <label left="4" top="76" width="186" height="20" field="proxNivelPer" fontColor="{TEXT_MUTED}" fontSize="13" horzTextAlign="center"/>
                            </rectangle>

                            <rectangle left="420" top="42" width="194" height="106" color="{BG_CARD_ALT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="5" yradius="5">
                                <label left="4" top="8" width="186" height="20" text="PTS PERICIA GASTOS" fontColor="{TEXT_MUTED}" fontSize="12" fontStyle="bold" horzTextAlign="center"/>
                                <label left="4" top="32" width="186" height="38" field="periciasGastas" fontColor="{TEXT_MAIN}" fontSize="26" fontStyle="bold" horzTextAlign="center"/>
                                <label left="4" top="76" width="186" height="20" text="1-7:1p | 8-11:2p | 12+:3p" fontColor="{TEXT_MUTED}" fontSize="11" horzTextAlign="center"/>
                            </rectangle>

                            <rectangle left="624" top="42" width="194" height="106" color="{BG_CARD_ALT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="5" yradius="5">
                                <label left="4" top="8" width="186" height="20" text="AUMENTOS ATTR." fontColor="{TEXT_MUTED}" fontSize="12" fontStyle="bold" horzTextAlign="center"/>
                                <label left="4" top="32" width="186" height="38" field="aumentosAtributo" fontColor="{TEXT_GOLD}" fontSize="26" fontStyle="bold" horzTextAlign="center"/>
                                <label left="4" top="76" width="186" height="20" text="1 pt a cada 3 niveis" fontColor="{TEXT_MUTED}" fontSize="12" horzTextAlign="center"/>
                            </rectangle>

                            <rectangle left="828" top="42" width="196" height="106" color="{BG_CARD_ALT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="5" yradius="5">
                                <label left="4" top="8" width="188" height="20" text="PATAMAR ATUAL" fontColor="{TEXT_MUTED}" fontSize="12" fontStyle="bold" horzTextAlign="center"/>
                                <label left="4" top="36" width="188" height="34" field="patamarTexto" fontColor="{TEXT_CRIMSON}" fontSize="17" fontStyle="bold" horzTextAlign="center"/>
                                <label left="12" top="76" width="90" height="20" text="Iniciativa:" fontColor="{TEXT_MUTED}" fontSize="13" horzTextAlign="leading"/>
                                <label left="96" top="76" width="88" height="20" field="iniciativaTotal" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold" horzTextAlign="trailing"/>
                            </rectangle>
                        </rectangle>
                    </layout>
                </scrollBox>
            </tab>

            <!-- ABA 2: COMBATE & FERIMENTOS -->
            <tab title="Combate &amp; Ferimentos">
                <scrollBox align="client">
                    <layout left="0" top="0" width="1056" height="840">
                        <rectangle left="6" top="6" width="1036" height="204" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="6" yradius="6">
                            <label left="12" top="10" width="1012" height="24" text="DEFESA SITUACIONAL (10 + DES + Armadura + Escudo + Pericia | Armaduras comuns JAMAIS dao RD)" fontColor="{TEXT_GOLD}" fontSize="14" fontStyle="bold"/>

                            <rectangle left="12" top="42" width="180" height="92" color="{BG_CARD_ALT}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="5" yradius="5">
                                <label left="4" top="6" width="172" height="20" text="DEFESA APARAR" fontColor="{TEXT_GOLD}" fontSize="13" fontStyle="bold" horzTextAlign="center"/>
                                <label left="4" top="26" width="172" height="40" field="defAparar" fontColor="{TEXT_MAIN}" fontSize="28" fontStyle="bold" horzTextAlign="center"/>
                                <label left="4" top="68" width="172" height="18" text="Corpo a Corpo" fontColor="{TEXT_MUTED}" fontSize="12" horzTextAlign="center"/>
                            </rectangle>

                            <rectangle left="202" top="42" width="180" height="92" color="{BG_CARD_ALT}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="5" yradius="5">
                                <label left="4" top="6" width="172" height="20" text="DEFESA ESQUIVA" fontColor="{TEXT_GOLD}" fontSize="13" fontStyle="bold" horzTextAlign="center"/>
                                <label left="4" top="26" width="172" height="40" field="defEsquiva" fontColor="{TEXT_MAIN}" fontSize="28" fontStyle="bold" horzTextAlign="center"/>
                                <label left="4" top="68" width="172" height="18" text="Flechas / Projeteis" fontColor="{TEXT_MUTED}" fontSize="12" horzTextAlign="center"/>
                            </rectangle>

                            <rectangle left="392" top="42" width="154" height="92" color="{BG_CARD_ALT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="5" yradius="5">
                                <label left="4" top="6" width="146" height="20" text="DESPREVENIDO" fontColor="{TEXT_MUTED}" fontSize="13" fontStyle="bold" horzTextAlign="center"/>
                                <label left="4" top="26" width="146" height="40" field="defDesprevenido" fontColor="{TEXT_MAIN}" fontSize="26" fontStyle="bold" horzTextAlign="center"/>
                                <label left="4" top="68" width="146" height="18" text="Sem DES / Per." fontColor="{TEXT_MUTED}" fontSize="12" horzTextAlign="center"/>
                            </rectangle>

                            <label left="560" top="46" width="114" height="20" text="Armadura (+Def)" fontColor="{TEXT_MUTED}" fontSize="12"/>
                            <edit left="560" top="70" width="98" height="38" field="armaduraDef" type="number" horzTextAlign="center" fontSize="18"/>

                            <label left="676" top="46" width="104" height="20" text="Escudo (+Def)" fontColor="{TEXT_MUTED}" fontSize="12"/>
                            <edit left="676" top="70" width="94" height="38" field="escudoDef" type="number" horzTextAlign="center" fontSize="18"/>

                            <label left="786" top="46" width="104" height="20" text="Outros (+Def)" fontColor="{TEXT_MUTED}" fontSize="12"/>
                            <edit left="786" top="70" width="94" height="38" field="defesaOutros" type="number" horzTextAlign="center" fontSize="18"/>

                            <label left="894" top="46" width="134" height="20" text="RD Especial (Raro!)" fontColor="{TEXT_CRIMSON}" fontSize="12" fontStyle="bold"/>
                            <edit left="894" top="70" width="126" height="38" field="rdEspecial" type="number" horzTextAlign="center" fontColor="{TEXT_CRIMSON}" fontSize="18" fontStyle="bold"/>

                            <button left="12" top="148" width="248" height="42" text="Defesa Total (Sacrifica Ataque)" fontSize="14">
                                <event name="onClick"><![CDATA[acaoDefensiva("propria");]]></event>
                            </button>
                            <button left="268" top="148" width="260" height="42" text="Proteger Aliado (Sacrifica Ataque)" fontSize="14">
                                <event name="onClick"><![CDATA[acaoDefensiva("aliado");]]></event>
                            </button>
                            <button left="536" top="148" width="318" height="42" text="CON vs Golpe Devastador (&gt;2/3 PV)" fontSize="14">
                                <event name="onClick"><![CDATA[rolarD20("CON contra Golpe Devastador (Morte Instantanea)", getMod("constituicao"), "Limiar de Golpe Devastador deste personagem: " .. (sheet.limiarDevastador or ""));]]></event>
                            </button>
                            <button left="862" top="148" width="160" height="42" text="Moribundo (CON)" fontSize="14">
                                <event name="onClick"><![CDATA[rolarD20("Teste de Moribundo (CD 12 — 3 sucessos estabiliza)", getMod("constituicao"), "");]]></event>
                            </button>
                        </rectangle>

                        <rectangle left="6" top="218" width="1036" height="320" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="6" yradius="6">
                            <label left="12" top="12" width="490" height="26" text="ARSENAL &amp; MULTIPLAS ACOES (Trava: Destr 1 | Tr 2 | Esp 3 | Mst 4)" fontColor="{TEXT_GOLD}" fontSize="14" fontStyle="bold"/>
                            <label left="516" top="12" width="180" height="26" text="Acoes no Turno (N):" fontColor="{TEXT_MAIN}" fontSize="14" horzTextAlign="trailing" vertTextAlign="center"/>
                            <comboBox left="704" top="8" width="318" height="34" field="multiAcoes" items="{{'1 Acao (Bonus Integral)', '2 Acoes (floor(Bonus/2) - 2)', '3 Acoes (floor(Bonus/3) - 3)', '4 Acoes (floor(Bonus/4) - 4)'}}" values="{{'1', '2', '3', '4'}}" fontSize="14"/>

                            <label left="16" top="52" width="210" height="20" text="ARMA" fontColor="{TEXT_MUTED}" fontSize="12" fontStyle="bold"/>
                            <label left="232" top="52" width="70" height="20" text="ATTR" fontColor="{TEXT_MUTED}" fontSize="12" fontStyle="bold" horzTextAlign="center"/>
                            <label left="306" top="52" width="136" height="20" text="PERICIA" fontColor="{TEXT_MUTED}" fontSize="12" fontStyle="bold" horzTextAlign="center"/>
                            <label left="446" top="52" width="48" height="20" text="EXT" fontColor="{TEXT_MUTED}" fontSize="12" fontStyle="bold" horzTextAlign="center"/>
                            <label left="498" top="52" width="54" height="20" text="TOTAL" fontColor="{TEXT_GOLD}" fontSize="12" fontStyle="bold" horzTextAlign="center"/>
                            <label left="556" top="52" width="76" height="20" text="DANO" fontColor="{TEXT_MUTED}" fontSize="12" fontStyle="bold" horzTextAlign="center"/>
                            <label left="636" top="52" width="46" height="20" text="+DMG" fontColor="{TEXT_MUTED}" fontSize="12" fontStyle="bold" horzTextAlign="center"/>
                            <label left="686" top="52" width="48" height="20" text="MARG" fontColor="{TEXT_CRIMSON}" fontSize="12" fontStyle="bold" horzTextAlign="center"/>
                            <label left="738" top="52" width="44" height="20" text="MULT" fontColor="{TEXT_CRIMSON}" fontSize="12" fontStyle="bold" horzTextAlign="center"/>
                            <label left="788" top="52" width="230" height="20" text="ROLAGENS NO CHAT" fontColor="{TEXT_GOLD}" fontSize="12" fontStyle="bold" horzTextAlign="center"/>

                            {"".join(weapon_rows)}
                        </rectangle>

                        <rectangle left="6" top="546" width="1036" height="280" color="{BG_CARD}" strokeColor="{BORDER_CRIMSON}" strokeSize="1" xradius="6" yradius="6">
                            <label left="12" top="10" width="1010" height="24" text="FERIMENTOS GRAVES, EXAUSTAO &amp; CICATRIZES PERMANENTES (Arbitragem Livre do Mestre)" fontColor="{TEXT_CRIMSON}" fontSize="15" fontStyle="bold"/>

                            <label left="12" top="40" width="500" height="20" text="FERIMENTOS ATIVOS / CONDICOES / EXAUSTAO (1-5)" fontColor="{TEXT_MUTED}" fontSize="13"/>
                            <textEditor left="12" top="64" width="500" height="202" field="ferimentosAtivos" fontSize="14"/>

                            <label left="524" top="40" width="500" height="20" text="CICATRIZES &amp; SEQUELAS PERMANENTES (Decisao do Mestre)" fontColor="{TEXT_GOLD}" fontSize="13"/>
                            <textEditor left="524" top="64" width="500" height="202" field="cicatrizesPermanentes" fontSize="14"/>
                        </rectangle>
                    </layout>
                </scrollBox>
            </tab>

            <!-- ABA 3: PERICIAS & TALENTOS -->
            <tab title="Pericias &amp; Talentos">
                <scrollBox align="client">
                    <layout left="0" top="0" width="1056" height="1280">
                        <rectangle left="6" top="6" width="1036" height="784" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="6" yradius="6">
                            <label left="12" top="10" width="710" height="24" text="34 PERICIAS — GRADUACAO LIVRE (0 Destr | 1-2 Inic | 3-7 Trein | 8-11 Espec N5+ | 12+ Mestre N11+)" fontColor="{TEXT_GOLD}" fontSize="13" fontStyle="bold"/>
                            <label left="724" top="10" width="156" height="24" text="Pts Gastos / Sugeridos:" fontColor="{TEXT_MUTED}" fontSize="12" horzTextAlign="trailing" vertTextAlign="center"/>
                            <label left="884" top="10" width="56" height="24" field="periciasGastas" fontColor="{TEXT_MAIN}" fontSize="15" fontStyle="bold" horzTextAlign="center" vertTextAlign="center"/>
                            <label left="940" top="10" width="16" height="24" text="/" fontColor="{TEXT_MUTED}" fontSize="15" horzTextAlign="center" vertTextAlign="center"/>
                            <label left="956" top="10" width="64" height="24" field="periciasSugeridas" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold" horzTextAlign="center" vertTextAlign="center"/>

                            <label left="16" top="38" width="168" height="18" text="PERICIA" fontColor="{TEXT_MUTED}" fontSize="12" fontStyle="bold"/>
                            <label left="186" top="38" width="34" height="18" text="ATTR" fontColor="{TEXT_MUTED}" fontSize="11" fontStyle="bold" horzTextAlign="center"/>
                            <label left="222" top="38" width="42" height="18" text="GRAD" fontColor="{TEXT_GOLD}" fontSize="11" fontStyle="bold" horzTextAlign="center"/>
                            <label left="266" top="38" width="96" height="18" text="GRAU AUTO" fontColor="{TEXT_MUTED}" fontSize="11" fontStyle="bold" horzTextAlign="center"/>
                            <label left="366" top="38" width="40" height="18" text="OUT" fontColor="{TEXT_MUTED}" fontSize="11" fontStyle="bold" horzTextAlign="center"/>
                            <label left="410" top="38" width="44" height="18" text="TOT" fontColor="{TEXT_GOLD}" fontSize="11" fontStyle="bold" horzTextAlign="center"/>

                            <label left="528" top="38" width="168" height="18" text="PERICIA" fontColor="{TEXT_MUTED}" fontSize="12" fontStyle="bold"/>
                            <label left="698" top="38" width="34" height="18" text="ATTR" fontColor="{TEXT_MUTED}" fontSize="11" fontStyle="bold" horzTextAlign="center"/>
                            <label left="734" top="38" width="42" height="18" text="GRAD" fontColor="{TEXT_GOLD}" fontSize="11" fontStyle="bold" horzTextAlign="center"/>
                            <label left="778" top="38" width="96" height="18" text="GRAU AUTO" fontColor="{TEXT_MUTED}" fontSize="11" fontStyle="bold" horzTextAlign="center"/>
                            <label left="878" top="38" width="40" height="18" text="OUT" fontColor="{TEXT_MUTED}" fontSize="11" fontStyle="bold" horzTextAlign="center"/>
                            <label left="922" top="38" width="44" height="18" text="TOT" fontColor="{TEXT_GOLD}" fontSize="11" fontStyle="bold" horzTextAlign="center"/>

                            {"".join(skill_rows)}
                        </rectangle>

                        <rectangle left="6" top="798" width="1036" height="292" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="6" yradius="6">
                            <label left="12" top="10" width="560" height="26" text="PERICIAS LIVRES / PERSONALIZADAS (CRIE QUANTAS QUISER!)" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold"/>
                            <button left="590" top="8" width="136" height="32" text="&lt; Pag. Ant." fontSize="13">
                                <event name="onClick"><![CDATA[mudarPaginaCustom(-1);]]></event>
                            </button>
                            <label left="732" top="10" width="96" height="26" field="customSkillPageLabel" fontColor="{TEXT_GOLD}" fontSize="14" fontStyle="bold" horzTextAlign="center" vertTextAlign="center"/>
                            <button left="834" top="8" width="190" height="32" text="Proxima / +10 Slots &gt;" fontSize="13">
                                <event name="onClick"><![CDATA[mudarPaginaCustom(1);]]></event>
                            </button>
                            <label left="12" top="44" width="1010" height="20" text="Digite qualquer pericia nova (ex: Forja de Adamante, Navegacao nos Corais, Dialeto de Yoketsu) e avance paginas para mais." fontColor="{TEXT_MUTED}" fontSize="12"/>

                            {"".join(custom_rows)}
                        </rectangle>

                        <rectangle left="6" top="1098" width="1036" height="170" color="{BG_CARD}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="6" yradius="6">
                            <label left="12" top="10" width="1010" height="24" text="TALENTOS, MANOBRAS DE COMBATE &amp; ESPECIALIZACOES (Niveis pares ou treino)" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold"/>
                            <textEditor left="12" top="38" width="1012" height="120" field="talentosManobras" fontSize="14"/>
                        </rectangle>
                    </layout>
                </scrollBox>
            </tab>

            <!-- ABA 4: INVENTARIO -->
            <tab title="Inventario">
                <scrollBox align="client">
                    <layout left="0" top="0" width="1056" height="780">
                        <rectangle left="6" top="6" width="1036" height="86" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="6" yradius="6">
                            <label left="14" top="10" width="146" height="20" text="MOEDAS DE OURO" fontColor="{TEXT_GOLD}" fontSize="12" fontStyle="bold"/>
                            <edit left="14" top="34" width="136" height="38" field="moedasOuro" type="number" horzTextAlign="center" fontSize="17"/>

                            <label left="166" top="10" width="146" height="20" text="MOEDAS DE PRATA" fontColor="{TEXT_MAIN}" fontSize="12" fontStyle="bold"/>
                            <edit left="166" top="34" width="136" height="38" field="moedasPrata" type="number" horzTextAlign="center" fontSize="17"/>

                            <label left="318" top="10" width="146" height="20" text="MOEDAS DE COBRE" fontColor="{TEXT_MUTED}" fontSize="12" fontStyle="bold"/>
                            <edit left="318" top="34" width="136" height="38" field="moedasCobre" type="number" horzTextAlign="center" fontSize="17"/>

                            <label left="510" top="10" width="166" height="20" text="CARGA ATUAL (kg)" fontColor="{TEXT_MUTED}" fontSize="12" fontStyle="bold"/>
                            <edit left="510" top="34" width="150" height="38" field="cargaAtual" horzTextAlign="center" fontSize="17"/>

                            <label left="686" top="10" width="260" height="20" text="CAPACIDADE MAXIMA (FOR x 5)" fontColor="{TEXT_GOLD}" fontSize="12" fontStyle="bold"/>
                            <rectangle left="686" top="34" width="180" height="38" color="{BG_INPUT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                                <label align="client" field="cargaMax" fontColor="{TEXT_GOLD}" fontSize="18" fontStyle="bold" horzTextAlign="center" vertTextAlign="center"/>
                            </rectangle>
                        </rectangle>

                        <rectangle left="6" top="100" width="512" height="666" color="{BG_CARD}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="6" yradius="6">
                            <label left="12" top="10" width="488" height="24" text="MOCHILA, EQUIPAMENTO DE KIT &amp; PROVISOES" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold"/>
                            <textEditor left="12" top="40" width="488" height="614" field="equipamentoMochila" fontSize="14"/>
                        </rectangle>

                        <rectangle left="528" top="100" width="514" height="328" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="6" yradius="6">
                            <label left="12" top="10" width="490" height="24" text="ARMADURAS, ADAMANTE &amp; RELIQUIAS RARAS (RD)" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold"/>
                            <textEditor left="12" top="40" width="490" height="276" field="reliquiasAdamante" fontSize="14"/>
                        </rectangle>

                        <rectangle left="528" top="438" width="514" height="328" color="{BG_CARD}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="6" yradius="6">
                            <label left="12" top="10" width="490" height="24" text="ALQUIMIA, VENENOS, ERVAS &amp; FERRAMENTAS" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold"/>
                            <textEditor left="12" top="40" width="490" height="276" field="alquimiaSuprimentos" fontSize="14"/>
                        </rectangle>
                    </layout>
                </scrollBox>
            </tab>

            <!-- ABA 5: HISTORIA & NOTAS -->
            <tab title="Historia &amp; Notas">
                <scrollBox align="client">
                    <layout left="0" top="0" width="1056" height="780">
                        <rectangle left="6" top="6" width="1036" height="106" color="{BG_CARD}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="6" yradius="6">
                            <label left="12" top="8" width="110" height="20" text="IDADE" fontColor="{TEXT_MUTED}" fontSize="12" fontStyle="bold"/>
                            <edit left="12" top="30" width="104" height="34" field="idade" fontSize="15"/>

                            <label left="128" top="8" width="150" height="20" text="ALTURA / PORTE" fontColor="{TEXT_MUTED}" fontSize="12" fontStyle="bold"/>
                            <edit left="128" top="30" width="166" height="34" field="altura" fontSize="15"/>

                            <label left="306" top="8" width="220" height="20" text="RELIGIAO / CREDO" fontColor="{TEXT_MUTED}" fontSize="12" fontStyle="bold"/>
                            <edit left="306" top="30" width="260" height="34" field="religiao" fontSize="15"/>

                            <label left="578" top="8" width="440" height="20" text="OBJETIVO COMO EXPLORADOR EM ALENIA" fontColor="{TEXT_GOLD}" fontSize="12" fontStyle="bold"/>
                            <edit left="578" top="30" width="446" height="34" field="objetivoExplorador" fontSize="15"/>

                            <label left="12" top="72" width="1010" height="22" text="Lembrete: Atributos Especiais (Status, Fe Verdadeira, Submundo, Dom Antigo) evoluem APENAS por Feitos registrados abaixo." fontColor="{TEXT_MUTED}" fontSize="13"/>
                        </rectangle>

                        <rectangle left="6" top="120" width="512" height="320" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="6" yradius="6">
                            <label left="12" top="10" width="488" height="24" text="DIARIO DE FEITOS (EVOLUCAO DE ESPECIAIS)" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold"/>
                            <textEditor left="12" top="40" width="488" height="268" field="registroFeitos" fontSize="14"/>
                        </rectangle>

                        <rectangle left="528" top="120" width="514" height="320" color="{BG_CARD}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="6" yradius="6">
                            <label left="12" top="10" width="490" height="24" text="HISTORIA, APARENCIA &amp; PASSADO" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold"/>
                            <textEditor left="12" top="40" width="490" height="268" field="historiaPersonagem" fontSize="14"/>
                        </rectangle>

                        <rectangle left="6" top="450" width="512" height="316" color="{BG_CARD}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="6" yradius="6">
                            <label left="12" top="10" width="488" height="24" text="CONTATOS, ALIADOS, RIVAIS &amp; ROTAS" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold"/>
                            <textEditor left="12" top="40" width="488" height="264" field="contatosAliados" fontSize="14"/>
                        </rectangle>

                        <rectangle left="528" top="450" width="514" height="316" color="{BG_CARD}" strokeColor="{BORDER_CRIMSON}" strokeSize="1" xradius="6" yradius="6">
                            <label left="12" top="10" width="490" height="24" text="MISTERIOS ANTIGOS, PRESSAGIOS &amp; SEGREDOS" fontColor="{TEXT_CRIMSON}" fontSize="15" fontStyle="bold"/>
                            <textEditor left="12" top="40" width="490" height="264" field="misteriosSegredos" fontSize="14"/>
                        </rectangle>
                    </layout>
                </scrollBox>
            </tab>
        </tabControl>
    </rectangle>

    <!-- DATALINKS NA RAIZ DO FORM (REGRA 2 DO SDK 3.7b) -->
    <dataLink fields="{xml_attr(lua_items_str(def_fields))}" defaultValues="{xml_attr(lua_items_str(def_values))}"/>

    <dataLink fields="{xml_attr(recalc_fields_lua)}">
        <event name="onChange"><![CDATA[recalcularFicha();]]></event>
    </dataLink>
    {"".join(custom_datalinks)}
</form>
'''
    with open(LFM_PATH, "w", encoding="utf-8") as f:
        f.write(lfm)
    print(f"[OK] AleniaFicha.lfm v1.2 gerado ({len(lfm)} bytes, DV 1d6-1d12 + travas v2.0).")


if __name__ == "__main__":
    build_lfm()
