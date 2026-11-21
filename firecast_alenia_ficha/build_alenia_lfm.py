#!/usr/bin/env python3
"""
Gera a ficha oficial AleniaFicha.lfm (RRPG Firecast SDK 3.7b) — v1.2 (Alinhada à Edição Revisada v2.0)
- Fontes ampliadas (v1.1+)
- Dado de Vida (1d6 / 1d8 / 1d10 / 1d12) por Kit + botão "Subir Nivel (1dX + CON)" no chat
- Perícias com graduação contínua (+0 a +16), Teto Progressivo por Nível (+4 no Nív. 1 até +16 no Nív. 26–30) e custo progressivo (1/2/3 pts por grad.)
- Trava anti-abuso em Múltiplas Ações Storyteller (limite por grau de treino + bônus >= 0)
- 36 Kits Universais + Sem Kit, 34 Perícias Fixas + Perícias Livres Ilimitadas
"""
import os
import re
import unicodedata
import xml.sax.saxutils as sax

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(OUT_DIR)
LFM_PATH = os.path.join(OUT_DIR, "AleniaFicha.lfm")
TOMO_IX_PATH = os.path.join(ROOT_DIR, "09_Catalogo_de_Equipamentos_e_Oficios.md")
REGRAS_PATH = os.path.join(ROOT_DIR, "01_Livro_de_Regras.md")

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

# Equipamento inicial estruturado para Aplicacao Completa dos 37 Kits
# Cada entrada: pp, armDef, escDef, arma1=(nome,attr,per,dano,margem,mult), arma2=None|(...), itens=[(nome,tipo,qtd,pesoUn,nota)]
KIT_LOADOUTS = {
    "sem_kit": {
        "pp": 25, "armDef": 0, "escDef": 0,
        "arma1": ("Adaga", "destreza", "per_armas_brancas", "1d4", "19", "2"), "arma2": None,
        "itens": [
            ("Adaga", "arma", 1, 0.5, "Dano 1d4+FOR | Crit 19-20/x2 | Leve, Agil, Arremesso 6m"),
            ("Roupas Comuns de Viagem", "equip", 1, 1.5, "Tunica grossa, calcas reforcadas e capa simples"),
            ("Mochila de Couro Reforcado", "equip", 1, 1.5, "Comporta ate 18 kg de carga"),
            ("Cantil de Latao ou Barro (1 L)", "equip", 1, 0.4, "Conserva agua fresca de viagem"),
            ("Racao Seca de Viagem (Dia)", "cons", 5, 0.5, "Consome 1 dia de racao seca (sustenta 1 dia sem Exaustao por fome)."),
        ],
    },
    "mercenario": {
        "pp": 30, "armDef": 2, "escDef": 0,
        "arma1": ("Espada Longa", "forca", "per_armas_brancas", "1d8", "19", "2"), "arma2": None,
        "itens": [
            ("Espada Longa", "arma", 1, 1.5, "Dano 1d8+FOR (1d10 em 2 maos) | Crit 19-20/x2"),
            ("Couro Batido", "armadura", 1, 6.0, "Defesa +2 | Penalidade 0 | Zero RD"),
            ("Capa de Estrada", "equip", 1, 1.0, "Protege contra vento e chuva leve"),
            ("Pedra de Amolar", "equip", 1, 0.3, "Mantem o fio das laminas em campanha"),
            ("Mochila de Couro Reforcado", "equip", 1, 1.5, "Comporta ate 18 kg de carga"),
        ],
    },
    "cavaleiro": {
        "pp": 40, "armDef": 3, "escDef": 2,
        "arma1": ("Espada Longa", "forca", "per_armas_brancas", "1d8", "19", "2"), "arma2": None,
        "itens": [
            ("Espada Longa", "arma", 1, 1.5, "Dano 1d8+FOR (1d10 em 2 maos) | Crit 19-20/x2"),
            ("Escudo Medio", "armadura", 1, 3.5, "Escudo Defesa +2 | Penalidade -1"),
            ("Cota de Malha", "armadura", 1, 12.0, "Defesa +3 | Penalidade -2 | Zero RD"),
            ("Tabardo com Brasao", "equip", 1, 0.6, "Identifica linhagem, ordem ou casa nobre"),
            ("Sela, Freio & Estribos", "equip", 1, 7.0, "Equipamento completo para montaria"),
        ],
    },
    "soldado": {
        "pp": 20, "armDef": 3, "escDef": 2,
        "arma1": ("Lanca de Infantaria", "forca", "per_armas_brancas", "1d8", "20", "3"),
        "arma2": ("Espada Curta", "forca", "per_armas_brancas", "1d6", "19", "2"),
        "itens": [
            ("Lanca de Infantaria", "arma", 1, 2.0, "Dano 1d8+FOR | Crit 20/x3 | Versatil/Alcance"),
            ("Espada Curta", "arma", 1, 1.0, "Dano 1d6+FOR | Crit 19-20/x2 | Leve"),
            ("Escudo Medio", "armadura", 1, 3.5, "Escudo Defesa +2 | Penalidade -1"),
            ("Cota de Malha", "armadura", 1, 12.0, "Defesa +3 | Penalidade -2 | Zero RD"),
            ("Cantil de Latao ou Barro (1 L)", "equip", 1, 0.4, "Agua de marcha militar"),
        ],
    },
    "duelista": {
        "pp": 35, "armDef": 1, "escDef": 0,
        "arma1": ("Florete", "destreza", "per_armas_brancas", "1d6", "18", "2"),
        "arma2": ("Adaga de Aparar", "destreza", "per_armas_brancas", "1d4", "19", "2"),
        "itens": [
            ("Florete", "arma", 1, 1.0, "Dano 1d6+FOR | Crit 18-20/x2 | Agil (DES), Perfurante"),
            ("Adaga de Aparar", "arma", 1, 0.5, "Dano 1d4+FOR | Crit 19-20/x2 | Auxilia aparar em duelo"),
            ("Gibao Reforcado Fino", "armadura", 1, 4.0, "Defesa +1 | Penalidade 0 | Zero RD | Discreto"),
        ],
    },
    "barbaro": {
        "pp": 15, "armDef": 1, "escDef": 0,
        "arma1": ("Machado Grande", "forca", "per_armas_brancas", "1d12", "20", "3"), "arma2": None,
        "itens": [
            ("Machado Grande", "arma", 1, 3.5, "Dano 1d12+FOR | Crit 20/x3 | Duas maos, Pesada"),
            ("Peles Reforcadas", "armadura", 1, 4.0, "Defesa +1 | Zero RD | Protecao contra frio"),
            ("Trofeu de Caca", "equip", 1, 0.5, "Marca de bravura tribal"),
            ("Cantil de Couro", "equip", 1, 0.3, "Odre resistente de viagem"),
        ],
    },
    "guarda_costas": {
        "pp": 25, "armDef": 4, "escDef": 3,
        "arma1": ("Espada Longa", "forca", "per_armas_brancas", "1d8", "19", "2"), "arma2": None,
        "itens": [
            ("Espada Longa", "arma", 1, 1.5, "Dano 1d8+FOR | Crit 19-20/x2"),
            ("Escudo Torre", "armadura", 1, 8.0, "Escudo Defesa +3 | Penalidade -3 | +2 em Proteger Aliado"),
            ("Brigantina / Meia-Placa", "armadura", 1, 16.0, "Defesa +4 | Penalidade -3 | Zero RD"),
            ("Lanterna Comum de Ferro", "equip", 1, 1.0, "Ilumina 9m (+6m penumbra) em vigilia"),
            ("Apito de Osso ou Latao", "equip", 1, 0.1, "Sinal sonoro de alerta ate 250m"),
        ],
    },
    "arqueiro": {
        "pp": 25, "armDef": 2, "escDef": 0,
        "arma1": ("Arco Longo", "destreza", "per_armas_dist", "1d8", "20", "3"),
        "arma2": ("Adaga", "destreza", "per_armas_brancas", "1d4", "19", "2"),
        "itens": [
            ("Arco Longo", "arma", 1, 1.5, "Dano 1d8 | Crit 20/x3 | 2 maos, Alcance 45m (sem +FOR)"),
            ("Flecha (Aljava)", "cons", 30, 0.03, "Dispara 1 flecha de arco longo."),
            ("Adaga", "arma", 1, 0.5, "Dano 1d4+FOR | Crit 19-20/x2 | Defesa proxima"),
            ("Couro Batido", "armadura", 1, 6.0, "Defesa +2 | Penalidade 0 | Zero RD"),
            ("Capa Camuflada", "equip", 1, 1.0, "Ajuda a ocultar silhueta em matas e rochas"),
        ],
    },
    "lutador": {
        "pp": 20, "armDef": 1, "escDef": 0,
        "arma1": ("Punhos de Ferro (Desarmado)", "forca", "per_luta_desarm", "1d6", "20", "2"), "arma2": None,
        "itens": [
            ("Bandagens & Soqueiras de Couro", "equip", 1, 0.4, "Protegem os punhos em combate desarmado (1d6+FOR)"),
            ("Gibao Reforcado", "armadura", 1, 4.0, "Defesa +1 | Penalidade 0 | Zero RD"),
            ("Cataplasma de Ervas", "cons", 1, 0.2, "Aplicado no Descanso Curto/Longo: soma +1d4 PV extras na recuperacao."),
        ],
    },
    "ladino": {
        "pp": 25, "armDef": 2, "escDef": 0,
        "arma1": ("Espada Curta", "destreza", "per_armas_brancas", "1d6", "19", "2"),
        "arma2": ("Adaga", "destreza", "per_armas_brancas", "1d4", "19", "2"),
        "itens": [
            ("Adaga", "arma", 2, 0.5, "Dano 1d4+FOR | Crit 19-20/x2 | Leve, Agil, Arremesso 6m"),
            ("Espada Curta", "arma", 1, 1.0, "Dano 1d6+FOR | Crit 19-20/x2 | Leve, Agil"),
            ("Couro Batido Escuro", "armadura", 1, 6.0, "Defesa +2 | Penalidade 0 | Zero RD"),
            ("Jogo de Gazuas Comum", "equip", 1, 0.4, "Ferramenta base para Ladinagem e Fechaduras"),
            ("Corda de Seda Trancada (15m)", "equip", 1, 2.0, "Suporta 450 kg | +1 em Escalada"),
        ],
    },
    "assassino": {
        "pp": 30, "armDef": 0, "escDef": 0,
        "arma1": ("Adaga Estilizada", "destreza", "per_armas_brancas", "1d4", "19", "2"),
        "arma2": ("Espada Curta", "destreza", "per_armas_brancas", "1d6", "19", "2"),
        "itens": [
            ("Adaga Estilizada", "arma", 1, 0.5, "Dano 1d4+FOR | Crit 19-20/x2 | Agil, discreta"),
            ("Espada Curta", "arma", 1, 1.0, "Dano 1d6+FOR | Crit 19-20/x2 | Agil"),
            ("Capa com Capuz", "equip", 1, 0.8, "Oculta feicoes e armas sob a sombra"),
            ("Veneno Fraco (Dose)", "cons", 2, 0.1, "Aplica veneno na lamina (CON CD 14 ou +1d6 dano venenoso)."),
            ("Estojo de Disfarce & Maquiagem", "equip", 1, 1.5, "Permite alterar rosto, voz e identidade"),
        ],
    },
    "espiao": {
        "pp": 40, "armDef": 0, "escDef": 0,
        "arma1": ("Adaga Oculta", "destreza", "per_armas_brancas", "1d4", "19", "2"), "arma2": None,
        "itens": [
            ("Adaga Oculta", "arma", 1, 0.4, "Dano 1d4+FOR | Crit 19-20/x2 | Escondida sob a manga/bota"),
            ("Estojo de Disfarce & Maquiagem", "equip", 1, 1.5, "Habilita testes complexos de Disfarce"),
            ("Tinta Invisivel (Dose)", "cons", 5, 0.04, "Escreve mensagem secreta revelada apenas sobre chama de vela."),
            ("Vestes de 2 Estratos Sociais", "equip", 2, 1.5, "Traje comum e traje fino para infiltracao"),
        ],
    },
    "contrabandista": {
        "pp": 35, "armDef": 0, "escDef": 0,
        "arma1": ("Sabre Curto", "destreza", "per_armas_brancas", "1d6", "18", "2"),
        "arma2": ("Besta Leve", "destreza", "per_armas_dist", "1d8", "19", "2"),
        "itens": [
            ("Sabre Curto", "arma", 1, 1.1, "Dano 1d6+FOR | Crit 18-20/x2 | Agil (DES)"),
            ("Besta Leve", "arma", 1, 2.5, "Dano 1d8 | Crit 19-20/x2 | Recarga (Movimento)"),
            ("Virote de Besta", "cons", 15, 0.04, "Dispara 1 virote de besta leve."),
            ("Capa com Bolsos Falsos", "equip", 1, 1.0, "Oculta pacotes pequenos em revistas"),
            ("Cartas & Mapas de Rotas", "equip", 1, 0.3, "Mapeia enseadas, portos e passagens discretas"),
        ],
    },
    "cacador_rec": {
        "pp": 25, "armDef": 2, "escDef": 0,
        "arma1": ("Besta Leve", "destreza", "per_armas_dist", "1d8", "19", "2"),
        "arma2": ("Espada Curta", "forca", "per_armas_brancas", "1d6", "19", "2"),
        "itens": [
            ("Besta Leve", "arma", 1, 2.5, "Dano 1d8 | Crit 19-20/x2 | Recarga (Movimento)"),
            ("Virote de Besta", "cons", 20, 0.04, "Dispara 1 virote de besta leve."),
            ("Espada Curta", "arma", 1, 1.0, "Dano 1d6+FOR | Crit 19-20/x2"),
            ("Algemas de Ferro com Chave", "equip", 1, 1.2, "Prendem pulsos (Ladinagem CD 16 / FOR CD 20)"),
            ("Rede de Captura", "equip", 1, 2.0, "Imobiliza alvos vivos sem matar"),
            ("Couro Batido", "armadura", 1, 6.0, "Defesa +2 | Penalidade 0 | Zero RD"),
        ],
    },
    "charlatao": {
        "pp": 40, "armDef": 0, "escDef": 0,
        "arma1": ("Adaga Escondida", "destreza", "per_armas_brancas", "1d4", "19", "2"), "arma2": None,
        "itens": [
            ("Adaga Escondida", "arma", 1, 0.4, "Dano 1d4+FOR | Crit 19-20/x2"),
            ("Documentos Falsos", "equip", 1, 0.2, "Salvo-condutos e cartas de apresentacao forjadas"),
            ("Bastao de Lacre & Selo", "cons", 5, 0.06, "Sela carta ou documento com cera quente."),
            ("Dados Viciados", "equip", 1, 0.1, "+3 em apostas de taverna (Percepcao CD 18 nota)"),
            ("Traje Fino de Corte", "equip", 1, 2.0, "Abre portas em saloes e casas mercantis"),
        ],
    },
    "saqueador": {
        "pp": 20, "armDef": 0, "escDef": 0,
        "arma1": ("Espada Curta", "destreza", "per_armas_brancas", "1d6", "19", "2"), "arma2": None,
        "itens": [
            ("Espada Curta", "arma", 1, 1.0, "Dano 1d6+FOR | Crit 19-20/x2"),
            ("Pe-de-Cabra de Aco", "equip", 1, 2.2, "+2 em FOR/Atletismo para arrombar portas e tampas"),
            ("Lanterna Blindada (Furta-Fogo)", "equip", 1, 1.2, "Fecha luz em Acao Livre ou foca feixe de 15m"),
            ("Jogo de Gazuas Comum", "equip", 1, 0.4, "Abre fechaduras e desarma armadilhas"),
            ("Corda com Arpeu (20m)", "equip", 1, 6.0, "Escalada em ruinas, muralhas e pocos"),
            ("Giz & Po Fino (Porcao)", "cons", 10, 0.03, "Marca caminhos em ruinas ou detecta correntes de ar/armadilhas."),
        ],
    },
    "pirata": {
        "pp": 25, "armDef": 0, "escDef": 0,
        "arma1": ("Sabre / Cimitarra", "destreza", "per_armas_brancas", "1d6", "18", "2"),
        "arma2": ("Adaga de Abordagem", "destreza", "per_armas_brancas", "1d4", "19", "2"),
        "itens": [
            ("Sabre / Cimitarra", "arma", 1, 1.3, "Dano 1d6+FOR | Crit 18-20/x2 | Agil (DES), ideal em conves"),
            ("Adaga de Abordagem", "arma", 1, 0.5, "Dano 1d4+FOR | Crit 19-20/x2"),
            ("Gancho de Abordagem com Corda", "equip", 1, 3.0, "Prende velames e amuradas inimigas"),
            ("Roupas Maritimas", "equip", 1, 1.5, "Resistentes a sal e vento"),
            ("Rum / Destilado (Dose)", "cons", 4, 0.25, "Dose de rum para moral ou limpar ferimentos de emergencia."),
        ],
    },
    "navegador": {
        "pp": 30, "armDef": 0, "escDef": 0,
        "arma1": ("Espada Curta", "destreza", "per_armas_brancas", "1d6", "19", "2"), "arma2": None,
        "itens": [
            ("Espada Curta", "arma", 1, 1.0, "Dano 1d6+FOR | Crit 19-20/x2"),
            ("Astrolabio / Bussola de Latao", "equip", 1, 0.8, "+2 em Navegacao & Nautica em alto-mar"),
            ("Cartas Nauticas Seladas", "equip", 1, 0.3, "Mapeiam correntes, farois e recifes"),
            ("Capa Impermeavel Oleada", "equip", 1, 1.5, "Protege contra chuva forte e mar revolto"),
        ],
    },
    "explorador": {
        "pp": 30, "armDef": 0, "escDef": 0,
        "arma1": ("Espada Curta", "destreza", "per_armas_brancas", "1d6", "19", "2"),
        "arma2": ("Arco Curto", "destreza", "per_armas_dist", "1d6", "20", "3"),
        "itens": [
            ("Espada Curta", "arma", 1, 1.0, "Dano 1d6+FOR | Crit 19-20/x2"),
            ("Estojo de Cartografia", "equip", 1, 0.6, "Pergaminhos, penas, tinta e compasso"),
            ("Luneta Simples", "equip", 1, 0.5, "+2 em Percepcao a longa distancia"),
            ("Botas Reforcadas de Marcha", "equip", 1, 1.2, "Evita penalidades em marchas longas"),
            ("Tenda Simples (1-2 pessoas)", "equip", 1, 4.5, "Abrigo contra vento e chuva"),
        ],
    },
    "patrulheiro": {
        "pp": 20, "armDef": 2, "escDef": 0,
        "arma1": ("Arco Longo", "destreza", "per_armas_dist", "1d8", "20", "3"),
        "arma2": ("Machadinha de Lenhador", "forca", "per_armas_brancas", "1d6", "20", "3"),
        "itens": [
            ("Arco Longo", "arma", 1, 1.5, "Dano 1d8 | Crit 20/x3 | Alcance 45m"),
            ("Flecha (Aljava)", "cons", 20, 0.03, "Dispara 1 flecha de caca/combate."),
            ("Machadinha de Lenhador", "arma", 1, 1.2, "Dano 1d6+FOR | Crit 20/x3 | Ferramenta e arma"),
            ("Couro Batido", "armadura", 1, 6.0, "Defesa +2 | Penalidade 0 | Zero RD"),
            ("Laco de Arame (Armadilha)", "cons", 6, 0.08, "Armadilha discreta para caca miuda (Sobrevivencia CD 13)."),
        ],
    },
    "mercador": {
        "pp": 60, "armDef": 0, "escDef": 0,
        "arma1": ("Besta Leve", "destreza", "per_armas_dist", "1d8", "19", "2"),
        "arma2": ("Adaga", "destreza", "per_armas_brancas", "1d4", "19", "2"),
        "itens": [
            ("Besta Leve", "arma", 1, 2.5, "Dano 1d8 | Crit 19-20/x2 | Defesa de caravana"),
            ("Virote de Besta", "cons", 10, 0.04, "Dispara 1 virote de besta leve."),
            ("Adaga", "arma", 1, 0.5, "Dano 1d4+FOR | Crit 19-20/x2"),
            ("Livro-Razao & Balanca Portatil", "equip", 1, 1.0, "Pesa moedas contra raspagem e registra contratos"),
            ("Mula de Carga com Alforjes", "equip", 1, 0.0, "Carrega ate 180 kg em estradas e montanhas"),
        ],
    },
    "domador": {
        "pp": 20, "armDef": 2, "escDef": 0,
        "arma1": ("Lanca Leve / Sabre", "forca", "per_armas_brancas", "1d8", "20", "3"), "arma2": None,
        "itens": [
            ("Lanca Leve / Sabre", "arma", 1, 1.8, "Dano 1d8+FOR | Ideal para combate montado"),
            ("Couro Batido", "armadura", 1, 6.0, "Defesa +2 | Penalidade 0 | Zero RD"),
            ("Cavalo Treinado (ou Cao Fiel)", "equip", 1, 0.0, "Companheiro animal leal (+3 contra panico, +2 Def guiado)"),
            ("Sela, Freio & Estribos", "equip", 1, 7.0, "Arreios completos de cavalgada"),
        ],
    },
    "ferreiro": {
        "pp": 30, "armDef": 2, "escDef": 0,
        "arma1": ("Martelo de Guerra / Forja", "forca", "per_armas_brancas", "1d8", "20", "3"), "arma2": None,
        "itens": [
            ("Martelo de Guerra / Forja", "arma", 1, 2.2, "Dano 1d8+FOR | Crit 20/x3 | Contundente"),
            ("Avental de Couro Pesado", "armadura", 1, 5.0, "Defesa +2 | Zero RD | Resiste a fagulhas e cortes"),
            ("Ferramentas Portateis de Ferreiro", "equip", 1, 6.0, "Habilita Forja & Metalurgia e Tempera de Mestre"),
        ],
    },
    "alquimista": {
        "pp": 35, "armDef": 0, "escDef": 0,
        "arma1": ("Adaga", "destreza", "per_armas_brancas", "1d4", "19", "2"), "arma2": None,
        "itens": [
            ("Adaga", "arma", 1, 0.5, "Dano 1d4+FOR | Crit 19-20/x2"),
            ("Bolsa Alquimica Completa", "equip", 1, 4.0, "Alambiques, balanca e frascos para Alquimia & Venenos"),
            ("Frasco de Acido Comum", "cons", 2, 0.5, "Arremesso 6m vs Defesa Esquiva sem armadura comum: 2d6 acido."),
            ("Bomba de Fumaca Seca", "cons", 2, 0.4, "Arremesso 6m: nuvem densa de 4,5m de raio por 3 rodadas."),
            ("Antidoto Comum", "cons", 1, 0.2, "+4 em testes de CON contra venenos naturais por 1 hora."),
        ],
    },
    "medico": {
        "pp": 35, "armDef": 0, "escDef": 0,
        "arma1": ("Adaga", "destreza", "per_armas_brancas", "1d4", "19", "2"), "arma2": None,
        "itens": [
            ("Adaga", "arma", 1, 0.5, "Dano 1d4+FOR | Crit 19-20/x2"),
            ("Estojo Medico & Cirurgico", "equip", 1, 2.0, "Bisturis, pincas, agulhas curvas e fios cirurgicos"),
            ("Aguardente Antisseptica (Dose)", "cons", 3, 0.2, "Limpa feridas antes da sutura (+1 em Medicina contra infeccoes)."),
            ("Atadura Limpa & Fio", "cons", 5, 0.08, "Reduz Medicina para CD 12 ao estancar sangramento/estabilizar."),
            ("Cataplasma de Ervas", "cons", 2, 0.2, "Aplicado no Descanso Curto/Longo: soma +1d4 PV extras na recuperacao."),
        ],
    },
    "erudito": {
        "pp": 40, "armDef": 0, "escDef": 0,
        "arma1": ("Bastao Ferrado", "forca", "per_armas_brancas", "1d6", "20", "2"), "arma2": None,
        "itens": [
            ("Bastao Ferrado", "arma", 1, 1.5, "Dano 1d6+FOR | Contundente, apoio de viagem"),
            ("Caderno de Pergaminho, Penas & Tinta", "equip", 1, 0.5, "Diarios de viagem e anotacoes academicas"),
            ("Lupa de Relojoeiro (Sellene)", "equip", 1, 0.1, "+2 em Investigacao e exame de selos/inscricoes"),
            ("Cartas Academicas", "equip", 1, 0.2, "Credenciais da Academia de Sellene ou bibliotecas"),
        ],
    },
    "engenheiro": {
        "pp": 35, "armDef": 0, "escDef": 0,
        "arma1": ("Besta Leve de Precisao", "destreza", "per_armas_dist", "1d8", "19", "2"), "arma2": None,
        "itens": [
            ("Besta Leve de Precisao", "arma", 1, 2.5, "Dano 1d8 | Crit 19-20/x2 | Sem polvora"),
            ("Virote de Besta", "cons", 15, 0.04, "Dispara 1 virote de besta."),
            ("Kit de Engenharia & Mecanica (Stoneforge)", "equip", 1, 4.5, "Chaves, compassos, polias, arames e molas"),
        ],
    },
    "herbalista": {
        "pp": 25, "armDef": 0, "escDef": 0,
        "arma1": ("Foice Curva / Adaga", "destreza", "per_armas_brancas", "1d4", "19", "2"), "arma2": None,
        "itens": [
            ("Foice Curva / Adaga", "arma", 1, 0.5, "Dano 1d4+FOR | Corte preciso de ervas e defesa"),
            ("Prensa de Ervas, Pilao & Almofariz", "equip", 1, 2.0, "Ferramenta base de Herbalismo & Natureza"),
            ("Bolsa de Raizes & Ervas Secas", "equip", 1, 0.8, "Ingredientes naturais para preparos"),
            ("Cataplasma de Ervas", "cons", 3, 0.2, "Aplicado no Descanso Curto/Longo: soma +1d4 PV extras na recuperacao."),
        ],
    },
    "astronomo": {
        "pp": 35, "armDef": 0, "escDef": 0,
        "arma1": ("Bastao / Adaga", "forca", "per_armas_brancas", "1d6", "20", "2"), "arma2": None,
        "itens": [
            ("Bastao / Adaga", "arma", 1, 1.2, "Dano 1d6+FOR | Defesa simples"),
            ("Luneta Simples", "equip", 1, 0.5, "Observacao estelar e vigilancia a longa distancia"),
            ("Astrolabio de Latao", "equip", 1, 0.8, "+2 em Navegacao e leitura celeste"),
            ("Mapas Estelares & Caderno", "equip", 1, 0.5, "Registros de constelacoes e mares"),
        ],
    },
    "carpinteiro": {
        "pp": 25, "armDef": 1, "escDef": 0,
        "arma1": ("Machadinha", "forca", "per_armas_brancas", "1d6", "20", "3"), "arma2": None,
        "itens": [
            ("Machadinha", "arma", 1, 1.2, "Dano 1d6+FOR | Crit 20/x3"),
            ("Gibao Reforcado", "armadura", 1, 4.0, "Defesa +1 | Penalidade 0 | Zero RD"),
            ("Caixa de Ferramentas de Carpinteiro", "equip", 1, 5.0, "Serra, martelo, enxo e formoes"),
            ("Pregos & Cravos (Lote 10 un.)", "cons", 5, 0.2, "Usado em barricadas (+2 resistencia) ou reparos estruturais."),
            ("Corda de Canhamo (15 metros)", "equip", 1, 4.5, "Suporta 350 kg"),
        ],
    },
    "nobre": {
        "pp": 80, "armDef": 0, "escDef": 0,
        "arma1": ("Florete Fino", "destreza", "per_armas_brancas", "1d6", "18", "2"), "arma2": None,
        "itens": [
            ("Florete Fino", "arma", 1, 1.0, "Dano 1d6+FOR | Crit 18-20/x2 | Agil (DES)"),
            ("Anel de Sinete da Casa", "equip", 1, 0.1, "Selo oficial de linhagem nobre"),
            ("Vestes Aristocraticas com Brasao", "equip", 1, 3.0, "Reforca Status 2-5 em cortes de Aurora e Corallis"),
            ("Cavalo de Estrada", "equip", 1, 0.0, "Montaria nobre (carrega 150 kg)"),
        ],
    },
    "diplomata": {
        "pp": 55, "armDef": 0, "escDef": 0,
        "arma1": ("Adaga Discreta", "destreza", "per_armas_brancas", "1d4", "19", "2"), "arma2": None,
        "itens": [
            ("Adaga Discreta", "arma", 1, 0.4, "Dano 1d4+FOR | Crit 19-20/x2"),
            ("Cartas Credenciais & Pergaminhos", "equip", 1, 0.4, "Autorizacao diplomatica oficial"),
            ("Bastao de Lacre & Selo", "cons", 5, 0.06, "Sela tratados e missivas oficiais."),
            ("Traje Fino de Corte", "equip", 1, 2.0, "Vestimenta apropriada para audiencias"),
        ],
    },
    "bardo": {
        "pp": 30, "armDef": 0, "escDef": 0,
        "arma1": ("Espada Curta", "destreza", "per_armas_brancas", "1d6", "19", "2"), "arma2": None,
        "itens": [
            ("Espada Curta", "arma", 1, 1.0, "Dano 1d6+FOR | Crit 19-20/x2 | Agil"),
            ("Instrumento Musical", "equip", 1, 1.5, "Alaude, flauta ou rabeca para Cronica de Taverna"),
            ("Roupas de Apresentacao & Viagem", "equip", 1, 1.8, "Versatil para tavernas e saloes"),
            ("Caderno de Cronicas & Cantigas", "equip", 1, 0.4, "Anotacoes de lendas, nomes e boatos"),
        ],
    },
    "sacerdote": {
        "pp": 25, "armDef": 0, "escDef": 0,
        "arma1": ("Cajado / Maca Simples", "forca", "per_armas_brancas", "1d6", "20", "2"), "arma2": None,
        "itens": [
            ("Cajado / Maca Simples", "arma", 1, 1.5, "Dano 1d6+FOR | Contundente"),
            ("Simbolo Sagrado Autentico", "equip", 1, 0.2, "Foco de devocao e autoridade espiritual"),
            ("Vestes Clericais", "equip", 1, 1.5, "Identificacao da ordem ou credo"),
            ("Cataplasma de Ervas", "cons", 2, 0.2, "Unguento de cura (+1d4 PV extras no descanso)."),
        ],
    },
    "inquisidor": {
        "pp": 30, "armDef": 2, "escDef": 0,
        "arma1": ("Espada Longa", "forca", "per_armas_brancas", "1d8", "19", "2"), "arma2": None,
        "itens": [
            ("Espada Longa", "arma", 1, 1.5, "Dano 1d8+FOR | Crit 19-20/x2"),
            ("Couro Batido", "armadura", 1, 6.0, "Defesa +2 | Penalidade 0 | Zero RD"),
            ("Manto com Insignia da Ordem", "equip", 1, 1.0, "Autoridade de investigacao religiosa"),
            ("Algemas de Ferro com Chave", "equip", 1, 1.2, "Detencao de hereges e suspeitos"),
        ],
    },
    "ermitao": {
        "pp": 10, "armDef": 0, "escDef": 0,
        "arma1": ("Lanca de Caca", "forca", "per_armas_brancas", "1d8", "20", "3"),
        "arma2": ("Facao de Mato", "forca", "per_armas_brancas", "1d6", "19", "2"),
        "itens": [
            ("Lanca de Caca", "arma", 1, 1.8, "Dano 1d8+FOR | Crit 20/x3"),
            ("Facao de Mato (Tercado)", "arma", 1, 1.0, "Dano 1d6+FOR | Abre trilhas e corta lenha"),
            ("Manto de Inverno Forrado de Pele", "equip", 1, 3.0, "+3 em Sobrevivencia contra frio extremo e chuva"),
            ("Pederneira, Aco e Caixa de Isca", "equip", 1, 0.3, "Acende fogueira em 1 minuto"),
        ],
    },
    "dom_antigo": {
        "pp": 15, "armDef": 0, "escDef": 0,
        "arma1": ("Adaga Ritualistica Antiga", "destreza", "per_armas_brancas", "1d4", "19", "2"), "arma2": None,
        "itens": [
            ("Adaga Ritualistica Antiga", "arma", 1, 0.5, "Dano 1d4+FOR | Crit 19-20/x2 | Gravuras desconhecidas"),
            ("Amuleto de Origem Desconhecida", "equip", 1, 0.2, "Reliquia antiga vinculada ao Dom Antigo"),
            ("Manto Gasto de Viajante", "equip", 1, 1.2, "Discreto nas estradas de Alenia"),
            ("Caderno de Visoes & Pressagios", "equip", 1, 0.4, "Registros de sonhos, simbolos e ritos"),
        ],
    },
}


def lua_str(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def ascii_clean(s: str) -> str:
    s = s.replace("*", "").replace("`", "")
    s = s.replace("—", "-").replace("–", "-").replace("×", "x").replace("…", "...").replace("↔", "<->")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", s).strip()


def _parse_price_pc(s: str) -> int:
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*(PO|PP|PC)", s, re.I)
    if not m:
        return 0
    val = float(m.group(1).replace(",", "."))
    unit = m.group(2).upper()
    mult = 100 if unit == "PO" else (10 if unit == "PP" else 1)
    return int(round(val * mult))


def _parse_weight_kg(s: str) -> float:
    if "Carrega" in s or s.strip() in ("-", "0", ""):
        return 0.0
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*kg", s, re.I)
    if not m:
        return 0.0
    return round(float(m.group(1).replace(",", ".")), 2)


def _fmt_price_label(pc: int) -> str:
    if pc >= 100 and pc % 100 == 0:
        return f"{pc // 10} PP ({pc // 100} PO)"
    if pc >= 10 and pc % 10 == 0:
        return f"{pc // 10} PP"
    if pc >= 10:
        return f"{pc} PC ({pc / 10.0:.1f} PP)"
    return f"{pc} PC"


def load_emporio_catalog():
    """Carrega todos os itens compraveis do Tomo IX + Armas e Armaduras do Livro de Regras."""
    cats = [
        ("pacotes", "01 - Pacotes Prontos de Expedicao (~10% desc.)"),
        ("mochilas", "02 - Mochilas, Recipientes & Transporte"),
        ("acampamento", "03 - Acampamento, Fogo & Iluminacao"),
        ("sobrevivencia", "04 - Sobrevivencia, Exploracao & Escalada"),
        ("pesca_caca", "05 - Pesca, Caca & Armadilhas"),
        ("forja_oficios", "06 - Forja, Ferraria, Carpintaria & Oficios"),
        ("alquimia_med", "07 - Medicina, Herbalismo & Alquimia"),
        ("nautica", "08 - Nautica, Navegacao & Cartografia"),
        ("subterfugio", "09 - Subterfugio, Investigacao & Corte"),
        ("vestuario", "10 - Vestuario, Clima & Provisoes"),
        ("montarias", "11 - Montarias, Animais de Carga & Arreios"),
        ("armas", "12 - Armas Comuns (Livro de Regras)"),
        ("armaduras", "13 - Armaduras & Escudos (Defesa | Zero RD)"),
    ]
    items_by_cat = {cid: [] for cid, _ in cats}

    sec_to_cat = {
        "1.": ("mochilas", "mochila"),
        "2.": ("acampamento", "mochila"),
        "3.": ("sobrevivencia", "mochila"),
        "4.": ("pesca_caca", "mochila"),
        "5.": ("forja_oficios", "alquimia"),
        "6.": ("alquimia_med", "alquimia"),
        "7.": ("nautica", "mochila"),
        "8.": ("subterfugio", "mochila"),
        "9.": ("vestuario", "mochila"),
        "10.": ("montarias", "mochila"),
    }

    dual_splits = {
        "Saco de Dormir (La / Pele Forrada)": [
            ("Saco de Dormir (La)", 15, 2.0),
            ("Saco de Dormir (Pele Forrada)", 50, 3.5),
        ],
        "Velas de Sebo (10 un.) / Cera (10 un.)": [
            ("Velas de Sebo (10 un.)", 2, 0.5),
            ("Velas de Cera de Abelha (10 un.)", 8, 0.5),
        ],
        "Luneta Simples / de Precisao (Helmer)": [
            ("Luneta Simples", 350, 0.5),
            ("Luneta de Precisao (Helmer)", 900, 0.5),
        ],
        "Cadeado Comum / de Precisao (Kalis)": [
            ("Cadeado Comum", 40, 0.5),
            ("Cadeado de Precisao (Kalis)", 180, 0.5),
        ],
        "Jogo de Gazuas Comum / de Precisao": [
            ("Jogo de Gazuas Comum", 200, 0.4),
            ("Jogo de Gazuas de Precisao", 750, 0.4),
        ],
        "Dados Comuns / Dados Viciados": [
            ("Dados Comuns", 2, 0.1),
            ("Dados Viciados", 50, 0.1),
        ],
        "Cantil de Vinho Bom / Cerveja Escura": [
            ("Cantil de Vinho Bom", 5, 1.0),
            ("Cantil de Cerveja Escura", 2, 1.0),
        ],
    }

    with open(TOMO_IX_PATH, encoding="utf-8") as f:
        txt = f.read()

    cur_sec = ""
    cur_sub = ""
    for line in txt.splitlines():
        if line.startswith("## "):
            cur_sec = ascii_clean(line[3:])
            cur_sub = ""
        elif line.startswith("### "):
            cur_sub = ascii_clean(line[4:])
        elif line.startswith("| ") and not line.startswith("| :---"):
            cols = [ascii_clean(c) for c in line.strip("|").split("|")]
            if len(cols) < 4:
                continue
            header0 = cols[0]
            if header0 in ("Item", "Animal / Equipamento", "Pacote Pronto", "Recurso / Bonus", "Tipo de Teste"):
                continue
            if not cur_sec or not cur_sec[0].isdigit():
                continue

            prefix = cur_sec.split()[0]
            if prefix not in sec_to_cat:
                continue
            cat_id, dest = sec_to_cat[prefix]
            if "Pacotes Prontos" in cur_sub:
                cat_id = "pacotes"
                dest = "mochila"

            raw_name, raw_price, raw_weight, raw_spec = cols[0], cols[1], cols[2], cols[3]
            if raw_name in dual_splits:
                for sub_name, sub_pc, sub_kg in dual_splits[raw_name]:
                    idx = len(items_by_cat[cat_id]) + 1
                    items_by_cat[cat_id].append({
                        "id": f"{cat_id}_{idx}",
                        "nome": sub_name,
                        "precoPc": sub_pc,
                        "pesoKg": sub_kg,
                        "dest": dest,
                        "spec": raw_spec,
                    })
            else:
                preco_pc = _parse_price_pc(raw_price)
                peso_kg = _parse_weight_kg(raw_weight)
                if preco_pc <= 0:
                    continue
                idx = len(items_by_cat[cat_id]) + 1
                items_by_cat[cat_id].append({
                    "id": f"{cat_id}_{idx}",
                    "nome": raw_name,
                    "precoPc": preco_pc,
                    "pesoKg": peso_kg,
                    "dest": dest,
                    "spec": raw_spec,
                })

    # Armas Comuns (Livro de Regras Secao 9.6)
    armas_comuns = [
        ("Adaga / Punhal", 40, 0.5, "Dano 1d4+FOR | Crit 19-20/x2 | Leve, Agil (FOR/DES), Arremesso 6m"),
        ("Espada Curta", 150, 1.0, "Dano 1d6+FOR | Crit 19-20/x2 | Leve, Agil (FOR/DES)"),
        ("Florete / Estoque", 300, 1.0, "Dano 1d6+FOR | Crit 18-20/x2 | Agil (DES), Perfurante"),
        ("Espada Longa", 250, 1.5, "Dano 1d8+FOR | Crit 19-20/x2 | Versatil (1d10+FOR em 2 maos)"),
        ("Lamina Oriental (Yoketsu)", 550, 1.4, "Dano 1d8+FOR | Crit 18-20/x2 | Agil em 2 maos, corte preciso"),
        ("Cimitarra / Sabre", 250, 1.3, "Dano 1d6+FOR | Crit 18-20/x2 | Agil (DES), ideal em conves/sela"),
        ("Machado de Batalha", 200, 2.0, "Dano 1d8+FOR | Crit 20/x3 | Versatil (1d10+FOR em 2 maos)"),
        ("Machado Grande", 350, 3.5, "Dano 1d12+FOR | Crit 20/x3 | Duas maos, Pesada"),
        ("Montante / Espada Grande", 500, 3.0, "Dano 2d6+FOR | Crit 19-20/x2 | Duas maos, Pesada"),
        ("Lanca / Pique", 100, 2.0, "Dano 1d8+FOR | Crit 20/x3 | Alcance (3m se pique), Versatil"),
        ("Martelo de Guerra", 220, 2.2, "Dano 1d8+FOR | Crit 20/x3 | Contundente"),
        ("Picareta de Guerra", 180, 1.8, "Dano 1d6+FOR | Crit 20/x4 | Perfurante letal"),
        ("Arco Curto", 200, 1.0, "Dano 1d6 | Crit 20/x3 | 2 maos, Alcance 24m (sem +FOR)"),
        ("Arco Longo", 450, 1.5, "Dano 1d8 | Crit 20/x3 | 2 maos, Alcance 45m (sem +FOR)"),
        ("Besta Leve", 350, 2.5, "Dano 1d8 | Crit 19-20/x2 | Recarga (Movimento)"),
        ("Besta Pesada", 750, 4.5, "Dano 1d10 | Crit 19-20/x2 | Recarga (Acao Principal)"),
    ]
    for idx, (nome, pc, kg, spec) in enumerate(armas_comuns, 1):
        items_by_cat["armas"].append({
            "id": f"armas_{idx}",
            "nome": nome,
            "precoPc": pc,
            "pesoKg": kg,
            "dest": "mochila",
            "spec": spec,
        })

    # Armaduras e Escudos (Livro de Regras Secao 9.6 — Defesa, Zero RD)
    armaduras_escudos = [
        ("Gibao Reforcado", 120, 4.0, "Defesa +1 | Penalidade Furt./Acrob. 0 | Zero RD | Discreta para viagem"),
        ("Couro Batido", 250, 6.0, "Defesa +2 | Penalidade Furt./Acrob. 0 | Zero RD | Padrao de exploradores"),
        ("Cota de Malha", 750, 12.0, "Defesa +3 | Penalidade Furt./Acrob. -2 | Zero RD | Boa protecao contra cortes"),
        ("Brigantina / Meia-Placa", 1800, 16.0, "Defesa +4 | Penalidade Furt./Acrob. -3 | Zero RD | Favorita de mercenarios veteranos"),
        ("Placas Completas", 4500, 24.0, "Defesa +5 | Penalidade Furt./Acrob. -5 | Zero RD | Exige FOR 13+"),
        ("Broquel (Escudo Pequeno)", 100, 1.5, "Escudo Defesa +1 | Penalidade 0 | Leve e agil para duelo"),
        ("Escudo Medio", 200, 3.5, "Escudo Defesa +2 | Penalidade -1 | Padrao de infantaria"),
        ("Escudo Torre", 450, 8.0, "Escudo Defesa +3 | Penalidade -3 | +2 extra em Proteger Aliado"),
    ]
    for idx, (nome, pc, kg, spec) in enumerate(armaduras_escudos, 1):
        items_by_cat["armaduras"].append({
            "id": f"armaduras_{idx}",
            "nome": nome,
            "precoPc": pc,
            "pesoKg": kg,
            "dest": "armadura",
            "spec": spec,
        })

    # Classificacao de consumiveis: item_id -> (usos_por_unidade, nome_no_slot, efeito_chat)
    consumiveis_meta = {
        "acampamento_8": (10, "Pavio Encerado", "Queima por 2 min mesmo sob garoa; +3 em testes para acender fogo na chuva."),
        "acampamento_9": (5, "Tocha Comum", "Ilumina 6m claramente (+6m penumbra) por 1 hora."),
        "acampamento_12": (1, "Oleo de Lamparina (Frasco 0,5 L)", "Alimenta lanterna por 6h ou arremesso incendiario (6m, 1d4 fogo/rodada)."),
        "acampamento_13": (10, "Vela de Sebo", "Ilumina raio de 2m por 1 hora."),
        "acampamento_14": (10, "Vela de Cera de Abelha", "Ilumina raio de 2m por 1 hora sem fumaca nem cheiro forte."),
        "sobrevivencia_4": (10, "Piton / Cravo de Escalada", "Cravado em pedra/gelo com martelo; +2 em Escalada e ancora de corda."),
        "pesca_caca_5": (6, "Laco de Arame (Armadilha)", "Armadilha discreta para caca miuda (Sobrevivencia CD 13 durante a noite)."),
        "pesca_caca_7": (5, "Isca Aromatica Seca (Dose)", "+2 em Sobrevivencia para pescar ou atrair presa para armadilha."),
        "pesca_caca_10": (1, "Sal Grosso de Bayd (1 kg)", "Conserva ate 10 kg de carne ou peixe cacado por 3 semanas."),
        "pesca_caca_12": (20, "Flecha (Aljava Impermeavel)", "Dispara 1 flecha protegida contra chuva e umidade."),
        "forja_oficios_4": (1, "Saco de Carvao Mineral (10 kg)", "Sustenta uma forja por 1 dia inteiro de trabalho pesado."),
        "forja_oficios_9": (3, "Cola de Osso & Breu (Dose)", "Veda rachaduras, fixa cabos de ferramentas ou repara equipamento."),
        "forja_oficios_10": (5, "Pregos & Cravos (Lote 10 un.)", "Usado em barricadas (+2 resistencia) ou reparos estruturais."),
        "alquimia_med_3": (5, "Atadura Limpa & Fio", "Reduz Medicina de CD 15 para CD 12 para estancar sangramento/estabilizar."),
        "alquimia_med_4": (1, "Cataplasma de Ervas", "Aplicado no Descanso Curto/Longo: soma +1d4 PV extras na recuperacao."),
        "alquimia_med_5": (3, "Aguardente Antisseptica (Dose)", "Limpa feridas antes da sutura (+1 em Medicina contra infeccoes)."),
        "alquimia_med_8": (1, "Frasco de Acido Comum", "Arremesso 6m vs Defesa Esquiva sem armadura comum: 2d6 acido (ou corroi fechadura/corrente)."),
        "alquimia_med_9": (1, "Bomba de Fumaca Seca", "Arremesso 6m: nuvem densa de 4,5m de raio por 3 rodadas (ocultamento total)."),
        "alquimia_med_10": (1, "Frasco de Oleo Incendiario", "Arremesso 6m: 1d6 fogo imediato + 1d4 fogo/rodada por 2 rodadas ate apagar."),
        "alquimia_med_11": (1, "Antidoto Comum", "+4 em testes de CON contra venenos naturais por 1 hora."),
        "alquimia_med_12": (1, "Calmante / Sonifero Herbal", "Em bebida: alvo testa CON CD 14 ou sofre sono pesado por 2 horas."),
        "alquimia_med_14": (5, "Frasco de Vidro com Rolha", "Usado para coletar amostra de agua, sangue, veneno ou cinzas."),
        "nautica_6": (1, "Kit de Calafetagem", "Repara 2d6 pontos de casco de embarcacao em 1 hora de trabalho."),
        "subterfugio_5": (5, "Bastao de Lacre & Selo", "Sela carta ou documento com cera quente."),
        "subterfugio_6": (5, "Tinta Invisivel (Dose)", "Escreve mensagem secreta revelada apenas sobre chama de vela."),
        "subterfugio_8": (1, "Bolsa de Estrepes (20 pontas)", "Cobre 1,5m x 1,5m; Percepcao CD 14 ou sofre 1d4 dano e metade do deslocamento."),
        "subterfugio_9": (10, "Giz & Po Fino (Porcao)", "Marca caminhos em ruinas ou detecta correntes de ar/mecanismos ocultos."),
        "vestuario_9": (7, "Racao Seca de Viagem (Dia)", "Consome 1 dia de racao seca (sustenta 1 dia de viagem sem Exaustao por fome)."),
        "vestuario_10": (14, "Biscoito Naval & Carne Salgada (Dia)", "Consome 1 dia de provisao naval (sustenta 1 dia em travessia maritima)."),
        "vestuario_11": (4, "Vinho Bom (Dose)", "Eleva moral no acampamento ou quebra o gelo em negociacao."),
        "vestuario_12": (4, "Cerveja Escura (Dose)", "Caneca de cerveja escura para o acampamento."),
        "vestuario_13": (7, "Forragem para Montaria (Dia)", "Alimenta 1 montaria por 1 dia em travessia sem pasto."),
    }

    # Conteudo exato dos 5 Pacotes Prontos (desempacotados automaticamente nos slots!)
    pacotes_conteudo = {
        "pacotes_1": [
            ("mochilas_1", 1), ("acampamento_3", 1), ("acampamento_1", 1), ("mochilas_5", 1),
            ("acampamento_7", 1), ("acampamento_8", 1), ("acampamento_9", 1), ("acampamento_15", 1),
            ("sobrevivencia_11", 1), ("vestuario_9", 1),
        ],
        "pacotes_2": [
            ("mochilas_1", 1), ("mochilas_4", 1), ("acampamento_5", 1), ("acampamento_11", 1),
            ("acampamento_12", 2), ("sobrevivencia_1", 1), ("sobrevivencia_3", 1), ("sobrevivencia_6", 1),
            ("sobrevivencia_10", 1), ("vestuario_6", 1), ("subterfugio_9", 1), ("alquimia_med_3", 1),
            ("vestuario_9", 1),
        ],
        "pacotes_3": [
            ("mochilas_1", 1), ("vestuario_7", 1), ("acampamento_6", 1), ("mochilas_5", 3),
            ("acampamento_7", 1), ("pesca_caca_10", 1), ("pesca_caca_5", 1), ("pesca_caca_9", 1),
            ("alquimia_med_11", 1), ("vestuario_9", 1),
        ],
        "pacotes_4": [
            ("mochilas_4", 1), ("nautica_8", 1), ("pesca_caca_1", 1), ("pesca_caca_2", 1),
            ("pesca_caca_3", 1), ("pesca_caca_4", 1), ("sobrevivencia_1", 1), ("acampamento_10", 1),
            ("acampamento_12", 2), ("pesca_caca_10", 1), ("pesca_caca_9", 1), ("vestuario_10", 1),
        ],
        "pacotes_5": [
            ("mochilas_1", 1), ("forja_oficios_1", 1), ("forja_oficios_2", 1), ("vestuario_8", 1),
            ("sobrevivencia_11", 1), ("forja_oficios_9", 1), ("forja_oficios_10", 1), ("acampamento_7", 1),
            ("acampamento_10", 1), ("acampamento_12", 2), ("mochilas_5", 1), ("vestuario_9", 1),
        ],
    }

    for cid, _ in cats:
        for it in items_by_cat[cid]:
            iid = it["id"]
            if iid in consumiveis_meta:
                usos, snome, efeito = consumiveis_meta[iid]
                it["tipo"] = "cons"
                it["usos"] = usos
                it["slotNome"] = snome
                it["pesoUn"] = round(it["pesoKg"] / float(usos), 3) if it["pesoKg"] > 0 else 0.0
                it["efeito"] = efeito
            else:
                it["tipo"] = "arma" if cid == "armas" else ("armadura" if cid == "armaduras" else "equip")
                it["usos"] = 1
                it["slotNome"] = it["nome"]
                it["pesoUn"] = it["pesoKg"]
                it["efeito"] = it["spec"][:145] + ("..." if len(it["spec"]) > 145 else "")
            if iid in pacotes_conteudo:
                it["pacoteItens"] = pacotes_conteudo[iid]
            else:
                it["pacoteItens"] = []

    return cats, items_by_cat


def load_talentos_catalog():
    """Carrega todos os 44 Talentos oficiais da Secao 8 do Livro de Regras."""
    cats = [
        ("marciais", "1 - Marciais e Taticos (12)"),
        ("sobrevivencia", "2 - Sobrevivencia, Vigor e Exploracao (10)"),
        ("sociais", "3 - Sociais, Intriga e Lideranca (11)"),
        ("mentais", "4 - Mentais, Erudicao e Oficio (11)"),
    ]
    sec_map = {"8.1": "marciais", "8.2": "sobrevivencia", "8.3": "sociais", "8.4": "mentais"}
    items_by_cat = {cid: [] for cid, _ in cats}

    with open(REGRAS_PATH, encoding="utf-8") as f:
        txt = f.read()

    cur_cat = None
    for line in txt.splitlines():
        if line.startswith("### 8."):
            cur_cat = sec_map.get(line[4:7])
        elif line.startswith("## ") and not line.startswith("## 8."):
            cur_cat = None
        elif cur_cat and line.startswith("| ") and not line.startswith("| :---"):
            cols = [ascii_clean(c.replace("→", "->").replace("⌊", "[").replace("⌋", "]").replace("≥", ">=")) for c in line.strip("|").split("|")]
            if len(cols) >= 3 and cols[0] != "Talento":
                idx = len(items_by_cat[cur_cat]) + 1
                items_by_cat[cur_cat].append({
                    "id": f"{cur_cat}_{idx}",
                    "cat": cur_cat,
                    "nome": cols[0],
                    "prereq": cols[1],
                    "efeito": cols[2],
                })
    return cats, items_by_cat


def _fmt_arma_lua(a):
    if not a:
        return "nil"
    nm, at, pe, dn, mg, ml = a
    return f"{{ nome={lua_str(nm)}, attr={lua_str(at)}, per={lua_str(pe)}, dano={lua_str(dn)}, margem={lua_str(mg)}, mult={lua_str(ml)} }}"


def build_lua_script(emporio_cats, emporio_items, talentos_cats, talentos_items) -> str:
    kits_lua = ["local KITS = {"]
    for k in KITS:
        kid, kname, dv_faces, per_b, m_int, esp_f, esp_v, per_list, equip, hab = k
        plist = ", ".join(lua_str(p) for p in per_list)
        esp_field_lua = lua_str(esp_f) if esp_f else "nil"
        ld = KIT_LOADOUTS.get(kid, {"pp": 25, "armDef": 0, "escDef": 0, "arma1": None, "arma2": None, "itens": []})
        itens_parts = [
            f"{{ nome={lua_str(inm)}, tipo={lua_str(itp)}, qtd={iq}, peso={ip}, nota={lua_str(intt)} }}"
            for inm, itp, iq, ip, intt in ld["itens"]
        ]
        kits_lua.append(
            f"    [{lua_str(kid)}] = {{ nome={lua_str(kname)}, dv={dv_faces}, perBase={per_b}, multInt={m_int}, "
            f"espField={esp_field_lua}, espVal={esp_v}, pericias={{ {plist} }}, equip={lua_str(equip)}, hab={lua_str(hab)}, "
            f"pp={ld['pp']}, armDef={ld['armDef']}, escDef={ld['escDef']}, "
            f"arma1={_fmt_arma_lua(ld['arma1'])}, arma2={_fmt_arma_lua(ld['arma2'])}, "
            f"itens={{ {', '.join(itens_parts)} }} }},"
        )
    kits_lua.append("};")

    skills_lua = ["local SKILLS = {"]
    for fid, sname, sattr, scat in SKILLS:
        skills_lua.append(f"    {{ field={lua_str(fid)}, nome={lua_str(sname)}, attr={lua_str(sattr)} }},")
    skills_lua.append("};")

    tal_cats_lua = ["local TALENTOS_CATS = {"]
    for cid, cname in talentos_cats:
        tal_cats_lua.append(f"    [{lua_str(cid)}] = {lua_str(cname)},")
    tal_cats_lua.append("};")

    tal_items_lua = ["local TALENTOS_ITENS = {"]
    for cid, _ in talentos_cats:
        tal_items_lua.append(f"    [{lua_str(cid)}] = {{")
        for t in talentos_items[cid]:
            lbl = f"{t['nome']}  [{t['prereq']}]"
            tal_items_lua.append(
                f"        {{ id={lua_str(t['id'])}, cat={lua_str(cid)}, nome={lua_str(t['nome'])}, "
                f"label={lua_str(lbl)}, prereq={lua_str(t['prereq'])}, efeito={lua_str(t['efeito'])} }},"
            )
        tal_items_lua.append("    },")
    tal_items_lua.append("};")

    emp_cats_lua = ["local EMPORIO_CATS = {"]
    for cid, cname in emporio_cats:
        emp_cats_lua.append(f"    [{lua_str(cid)}] = {lua_str(cname)},")
    emp_cats_lua.append("};")

    emp_items_lua = ["local EMPORIO_ITENS = {"]
    for cid, _ in emporio_cats:
        emp_items_lua.append(f"    [{lua_str(cid)}] = {{")
        for it in emporio_items[cid]:
            tag_cons = " [Cons.]" if it["tipo"] == "cons" else ""
            lbl = (
                f"{it['nome']}{tag_cons}  [{_fmt_price_label(it['precoPc'])} | {it['pesoKg']:.1f} kg]"
                if it["pesoKg"] > 0
                else f"{it['nome']}{tag_cons}  [{_fmt_price_label(it['precoPc'])}]"
            )
            pack_str = ""
            if it["pacoteItens"]:
                pack_parts = [f"{{ id={lua_str(pid)}, qtd={pq} }}" for pid, pq in it["pacoteItens"]]
                pack_str = ", pacoteItens={ " + ", ".join(pack_parts) + " }"
            emp_items_lua.append(
                f"        {{ id={lua_str(it['id'])}, nome={lua_str(it['nome'])}, slotNome={lua_str(it['slotNome'])}, "
                f"label={lua_str(lbl)}, precoPc={it['precoPc']}, pesoKg={it['pesoKg']}, pesoUn={it['pesoUn']}, "
                f"tipo={lua_str(it['tipo'])}, usos={it['usos']}, dest={lua_str(it['dest'])}, "
                f"efeito={lua_str(it['efeito'])}, spec={lua_str(it['spec'])}{pack_str} }},"
            )
        emp_items_lua.append("    },")
    emp_items_lua.append("};")

    emp_index_lua = [
        "local EMPORIO_BY_ID = {};",
        "for _, lista in pairs(EMPORIO_ITENS) do",
        "    for i = 1, #lista do",
        "        EMPORIO_BY_ID[lista[i].id] = lista[i];",
        "    end;",
        "end;",
    ]

    lua = (
        "\n".join(kits_lua)
        + "\n\n"
        + "\n".join(skills_lua)
        + "\n\n"
        + "\n".join(tal_cats_lua)
        + "\n\n"
        + "\n".join(tal_items_lua)
        + "\n\n"
        + "\n".join(emp_cats_lua)
        + "\n\n"
        + "\n".join(emp_items_lua)
        + "\n\n"
        + "\n".join(emp_index_lua)
        + r"""

local okInt, InternetMod = pcall(require, "internet.lua");
if not okInt or InternetMod == nil then InternetMod = Internet or internet; end;
local okPlg, PluginsMod = pcall(require, "plugins.lua");
if not okPlg or PluginsMod == nil then PluginsMod = (Firecast and Firecast.Plugins) or (rrpg and rrpg.Plugins); end;
local okDlg, DialogsMod = pcall(require, "dialogs.lua");
if not okDlg or DialogsMod == nil then DialogsMod = Dialogs or dialogs; end;

local PLUGIN_MODULE_ID = "br.com.alenia.rpg_oficial";
local PLUGIN_VERSION = "2.3";
local PLUGIN_RPK_URL = "https://raw.githubusercontent.com/krleandro/alenia/main/plugins/Alenia_RPG_Ficha.rpk";
local BIBLIOTECA_URL = "https://alenia-rpg.onrender.com";

local _formRef = nil;
local _ultimaCatEmporio = nil;
local _ultimaCatTalento = nil;

-- Catalogo Oficial de Doencas de Alenia (7 campos + automacao de estagios e Exaustao)
local DOENCAS_CATALOGO = {
    febre_cisternas = {
        nome = "Febre das Cisternas (Sede Suja)",
        natureza = "Transmissivel (agua contaminada)",
        ritmo = "Aguda (1x/dia)",
        attr = "constituicao",
        cd = 14,
        exaustao = { 1, 2, 4 },
        efeitos = {
            "Leve: Exaustao 1; precisa dobrar consumo de agua limpa.",
            "Incapacitante: Exaustao 2; NAO recupera PV em Descanso Curto.",
            "Critica: Exaustao 4; desidratacao grave (falha adicional = coma/risco de morte em 24h)."
        },
        exposicao = "Ingerir agua de cisterna, poco ou reservatorio contaminado sem fervura (CON CD 13).",
        incubacao = "1 a 2 dias.",
        sinais = "Sede insaciavel, colicas abdominais severas, febre umida e fraqueza repentina.",
        cuidados = "Agua fervida com sais e infusoes (Herbalismo +2), Medicina (+2), repouso; Alquimia prepara sais/carvao tratado.",
        sequelas = "Casos criticos sem medico: fadiga por 2 semanas (Exaustao exige o dobro de descansos).",
        controle = "Isolar/limpar reservatorio, distribuir agua fervida ou de fonte alternativa."
    },
    tosse_ferraur = {
        nome = "Tosse de Ferraur",
        natureza = "Ocupacional (nao contagiosa)",
        ritmo = "Cronica (1x/semana exposto)",
        attr = "constituicao",
        cd = 13,
        exaustao = { 0, 1, 3 },
        efeitos = {
            "Leve: Tosse noturna; -2 em Atletismo prolongado, corrida e marcha forcada.",
            "Incapacitante: Exaustao 1; exige 1 rodada de folego apos correr ou 3 rodadas de combate.",
            "Critica: Exaustao 3; dor toracica e risco de insuficiencia fatal se voltar a mina."
        },
        exposicao = "Meses em galerias de mina, britagem ou forjas fechadas sem mascara/ventilacao.",
        incubacao = "Gradual (meses; acelera em 2-4 semanas em tuneis fechados).",
        sinais = "Tosse seca ao fim do turno, chiado no peito, escarro escuro (tiras de pano manchadas).",
        cuidados = "Afastar da poeira interrompe o agravamento! Herbalismo/Medicina aliviam crises (+2); Alquimia faz mascaras filtrantes.",
        sequelas = "Estagio Critico deixa -1 permanente em testes de folego/resistencia fisica prolongada.",
        controle = "Chamines de ventilacao, umedecer rocha, turnos reduzidos e mascaras umidas."
    },
    tremor_brumas = {
        nome = "Tremor das Brumas",
        natureza = "Vetorial (insetos de areas alagadas)",
        ritmo = "Aguda/Sazonal (1x/dia em crise)",
        attr = "constituicao",
        cd = 14,
        exaustao = { 1, 2, 4 },
        efeitos = {
            "Leve: Exaustao 1 nos dias de crise; maos tremulas impoem -2 em precisao (Dist./Ladin./Med.).",
            "Incapacitante: Exaustao 2; crises de 2 dias com confusao leve (falsas melhoras).",
            "Critica: Exaustao 4; febre delirante continua (risco de morte em 2 dias sem infusao amarga)."
        },
        exposicao = "Dormir sem rede/protecao em pantanos ou aguas paradas na estacao umida (CON CD 13).",
        incubacao = "4 a 7 dias.",
        sinais = "Calafrios violentos e suor febril alternados com 24-48h de falsa melhora.",
        cuidados = "Herbalismo (casca amarga da mata: +3), Medicina (febre/hidratacao), Alquimia (oleos repelentes e extratos).",
        sequelas = "Sem extrato amargo, recaidas espacadas podem retornar sob Exaustao por 1d4 meses.",
        controle = "Acampar em terreno alto, usar redes, drenar pocas paradas e ouvir guias locais."
    },
    mal_porao = {
        nome = "Mal do Porao (Mancha do Cais)",
        natureza = "Transmissivel (superlotacao/parasitas)",
        ritmo = "Aguda (1x/dia)",
        attr = "constituicao",
        cd = 15,
        exaustao = { 1, 3, 4 },
        efeitos = {
            "Leve: Exaustao 1; febre subita e dores musculares intensas.",
            "Incapacitante: Exaustao 3; manchas/rigidez impoem -2 na Defesa (auto!) e impedem armadura pesada.",
            "Critica: Exaustao 4; -2 na Defesa, delirio e falha adicional reduz a 0 PV (Moribundo!)."
        },
        exposicao = "Contato prolongado com poroes, celas, roupas ou mantas infestadas (CON CD 14).",
        incubacao = "3 a 5 dias.",
        sinais = "Febre alta subita, dores nas costas/pernas e manchas arroxeadas no tronco e bracos.",
        cuidados = "Isolamento limpo + fervura de roupas (sem isso CD +2); Medicina (+2), Alquimia (enxofre/antisseptico), Herbalismo.",
        sequelas = "Fraqueza muscular por 1-2 semanas apos alta; manchas palidas em casos criticos.",
        controle = "Quarentena justa com alimento/diaria, ferver/queimar palha e inspecionar todos os passageiros."
    },
    cinza_pele = {
        nome = "Cinza da Pele",
        natureza = "Cronica (nao contagiosa)",
        ritmo = "Cronica (1x/semana se negligenciada)",
        attr = "constituicao",
        cd = 12,
        exaustao = { 0, 0, 2 },
        efeitos = {
            "Leve: Placas claras/dormencia; estigma social (-2 social com supersticiosos se visivel).",
            "Incapacitante: Perda de tato fino impoe -2 em destreza manual delicada (Ladin./Prestid./Cirurgia).",
            "Critica: Exaustao 2 + infeccoes profundas por feridas nao sentidas (risco de perda de mobilidade)."
        },
        exposicao = "Nao transmissivel por contato comum; surgimento esporadico debatido em Sellene.",
        incubacao = "Lenta (semanas ou meses).",
        sinais = "Placas secas claras/acinzentadas que fissuram e perdem sensibilidade ao toque e a dor.",
        cuidados = "Oleos emolientes (Herbalismo), inspecao diaria de cortes/curativos (Medicina), saboes suaves (Alquimia).",
        sequelas = "Cicatrizes claras permanentes e reducao parcial de tato nas areas afetadas.",
        controle = "NAO exige quarentena — combate a falsos diagnosticos e protecao contra estigma/perseguicao."
    },
    febre_coro = {
        nome = "Febre do Coro (Quadro Anomalo)",
        natureza = "Anomala (debatida — consultar Mestre)",
        ritmo = "Semanal (1x/semana)",
        attr = "sabedoria",
        cd = 14,
        exaustao = { 0, 0, 0 },
        efeitos = {
            "Leve: Sonhos vividos e ecos estranhos; -2 em testes de SAB contra sugestao/influencia.",
            "Incapacitante: Frases/gestos sincronizados com outros afetados; risco de perda de foco (SAB CD 15).",
            "Critica: Estagio Critico — consultar o Mestre imediatamente."
        },
        exposicao = "Determinada pelo Mestre conforme o local ou incidente investigado.",
        incubacao = "3 dias a 2 semanas (frequentemente silenciosa).",
        sinais = "Sono alterado ou tranquilo demais, frases identicas compartilhadas entre desconhecidos e memorias intrusas.",
        cuidados = "Isolamento, ancoras emocionais e acompanhamento conjunto (Medicina + Herbalismo + Alquimia conforme pistas da campanha).",
        sequelas = "Definidas pelo Mestre apos recuperacao.",
        controle = "Investigar a origem real do quadro sem precipitar panico ou perseguicao cega."
    },
    personalizada = {
        nome = "Doenca Personalizada (Mestre)",
        natureza = "Definida pelo Mestre",
        ritmo = "Conforme o Mestre",
        attr = "constituicao",
        cd = 14,
        exaustao = { 1, 2, 4 },
        efeitos = {
            "Leve: Exaustao 1 + sintoma inicial definido pelo Mestre.",
            "Incapacitante: Exaustao 2 + limitacao fisica/mental definida pelo Mestre.",
            "Critica: Exaustao 4 + risco severo sem tratamento."
        },
        exposicao = "Definida pelo Mestre.",
        incubacao = "Definida pelo Mestre.",
        sinais = "Definidos pelo Mestre.",
        cuidados = "Colaboracao de Medico (+2), Herbalista (+2) e Alquimista (+2) ate teto +6.",
        sequelas = "Definidas pelo Mestre.",
        controle = "Definido pelo Mestre."
    }
};

-- Tabela Oficial de XP Acumulada (Niveis 1 a 30)
local XP_TABELA = {
    0, 300, 800, 1500, 2500, 3800, 5500, 7500, 10000, 13000,
    17000, 21500, 26500, 32000, 38000, 45000, 52500, 61000, 70000, 80000,
    92000, 105000, 120000, 136000, 154000, 174000, 196000, 220000, 246000, 275000
};

-- Teto Progressivo de Graduacao por Nivel (Niveis 1 a 30)
-- 1-4: Niv+3 (+4..+7) | 5-10: +8..+11 | 11-20 Lenda: +12..+14 | 21-30 Epico: +15..+16
local TETO_GRAD_POR_NIVEL = {
    4, 5, 6, 7, 8, 9, 9, 10, 10, 11,
    12, 12, 12, 13, 13, 13, 14, 14, 14, 14,
    15, 15, 15, 15, 15, 16, 16, 16, 16, 16
};

-- Padrao de Vida Mensal (em PP — Padrao Prata: 1 PO = 10 PP = 100 PC)
local PADROES_VIDA = {
    miseravel     = { nome="Miseravel",     custo=0,   info="0 PP/mes | Risco de doenca/roubo; -2 Etiqueta/Persuasao" },
    pobre         = { nome="Pobre",         custo=6,   info="6 PP/mes (2 PC/dia) | Albergue coletivo, sobrevivencia basica" },
    modesto       = { nome="Modesto",       custo=15,  info="15 PP/mes (5 PC/dia) | Estalagem simples (Status 0-1)" },
    confortavel   = { nome="Confortavel",   custo=45,  info="45 PP/mes (1,5 PP/dia) | Sustenta Status 2; +1 com mercadores" },
    abastado      = { nome="Abastado",      custo=150, info="150 PP/mes (15 PO) | Sustenta Status 3; abre portas de guildas" },
    aristocratico = { nome="Aristocratico", custo=450, info="450 PP/mes (45 PO) | Sustenta Status 4-5; +2 Etiqueta na corte" }
};

local recalcularFicha;
local atualizarPaginaCustomSkills;
local atualizarPaginaInventario;
local recalcularPesoInventario;
local adicionarOuEmpilharNoInventario;
local atualizarPaginaTalentos;

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
        return "Epico (2x Per)", 2.0, 22;
    elseif nivel >= 11 then
        return "Lenda (1.5x Per)", 1.5, 20;
    else
        return "Recruta (1x Per)", 1.0, 18;
    end;
end;

local function adicionarXP()
    if sheet == nil then return; end;
    local function aplicarXP(valorStr)
        local ganho = math.floor(num(valorStr, 0));
        if ganho == 0 then return; end;
        local xpAntes = math.max(0, math.floor(num(sheet.xpAtual, 0)));
        local xpNovo = math.max(0, xpAntes + ganho);
        sheet.xpAtual = tostring(xpNovo);
        recalcularFicha();
        local niv = math.max(1, math.min(30, math.floor(num(sheet.nivel, 1))));
        local nomeChar = sheet.nome or "Explorador";
        local prox = (niv < 30) and XP_TABELA[niv + 1] or XP_TABELA[30];
        local alerta = "";
        if niv < 30 and xpNovo >= prox then
            alerta = " — PRONTO PARA SUBIR PARA O NIVEL " .. tostring(niv + 1) .. "!";
        end;
        local sinal = (ganho >= 0) and "+" or "";
        enviarChatOuMsg("[" .. nomeChar .. "] XP: " .. sinal .. tostring(ganho) .. " (Total: " .. tostring(xpNovo) .. " / " .. tostring(prox) .. " XP)" .. alerta);
    end;

    if DialogsMod ~= nil and type(DialogsMod.inputQuery) == "function" then
        DialogsMod.inputQuery(
            "Adicionar Experiencia (XP)",
            "Quanto XP o explorador ganhou? (exploracao, armadilhas, vitorias sociais, contratos ou combates):",
            "150",
            function(val) aplicarXP(val); end,
            function() end,
            false
        );
    else
        showMessage("Digite o novo total diretamente no campo XP Atual.");
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

local function executarRolagemD20(titulo, modTotal, detalheExtra, cdUsada)
    if sheet == nil then return; end;
    local cd = math.max(0, math.floor(num(cdUsada, 0)));
    local modStr = "";
    if modTotal >= 0 then
        modStr = " + " .. tostring(modTotal);
    else
        modStr = " - " .. tostring(math.abs(modTotal));
    end;
    local rolagem = Firecast.interpretarRolagem("1d20" .. modStr);
    local nomeChar = sheet.nome or "Explorador";
    local sufixoCD = (cd > 0) and (" [CD " .. tostring(cd) .. "]") or "";
    local cabecalho = "[" .. nomeChar .. "] " .. titulo .. sufixoCD;
    local mesa = Firecast.getMesaDe(sheet);
    if mesa ~= nil and mesa.activeChat ~= nil then
        mesa.activeChat:rolarDados(rolagem, cabecalho,
            function(rolado)
                local d20Nat = nil;
                local total = (rolado ~= nil and rolado.resultado) or 0;
                if rolado ~= nil and rolado.ops ~= nil then
                    for i = 1, #rolado.ops do
                        local op = rolado.ops[i];
                        if op.tipo == "dado" and op.resultados ~= nil and #op.resultados >= 1 then
                            d20Nat = op.resultados[1];
                            break;
                        end;
                    end;
                end;
                local msgRes = "";
                if d20Nat == 20 then
                    msgRes = "[20 NATURAL — SUCESSO CRITICO!] " .. nomeChar .. " em " .. titulo .. " (Total " .. tostring(total) .. (cd > 0 and (" vs CD " .. tostring(cd)) or "") .. ")!";
                elseif d20Nat == 1 then
                    msgRes = "[1 NATURAL — FALHA CRITICA!] " .. nomeChar .. " em " .. titulo .. " (Total " .. tostring(total) .. (cd > 0 and (" vs CD " .. tostring(cd)) or "") .. ")!";
                elseif cd > 0 then
                    local diff = total - cd;
                    if diff >= 0 then
                        msgRes = "[SUCESSO!] " .. nomeChar .. " passou em " .. titulo .. " (" .. tostring(total) .. " vs CD " .. tostring(cd) .. " | margem +" .. tostring(diff) .. ").";
                    else
                        msgRes = "[FALHA!] " .. nomeChar .. " falhou em " .. titulo .. " (" .. tostring(total) .. " vs CD " .. tostring(cd) .. " | faltaram " .. tostring(math.abs(diff)) .. ").";
                    end;
                end;
                if msgRes ~= "" then
                    mesa.activeChat:enviarMensagem(msgRes);
                end;
                if detalheExtra ~= nil and detalheExtra ~= "" then
                    mesa.activeChat:enviarMensagem(detalheExtra);
                end;
            end);
    else
        rolagem:rolarLocalmente();
        local res = rolagem.resultado;
        local statusTxt = "";
        if cd > 0 then
            statusTxt = (res >= cd) and ("\n[SUCESSO! " .. tostring(res) .. " vs CD " .. tostring(cd) .. "]") or ("\n[FALHA! " .. tostring(res) .. " vs CD " .. tostring(cd) .. "]");
        end;
        showMessage(cabecalho .. "\nResultado: " .. tostring(res) .. statusTxt);
    end;
end;

local function rolarD20(titulo, modTotal, detalheExtra, cdFixa)
    if sheet == nil then return; end;
    if cdFixa ~= nil then
        executarRolagemD20(titulo, modTotal, detalheExtra, cdFixa);
        return;
    end;
    if sheet.perguntarCD == true and DialogsMod ~= nil and type(DialogsMod.inputQuery) == "function" then
        local atualCD = tostring(sheet.cdTeste or "15");
        if atualCD == "" or atualCD == "0" then atualCD = "15"; end;
        DialogsMod.inputQuery(
            "Dificuldade do Teste (CD)",
            "Informe a CD para " .. titulo .. " (0 ou vazio = rolagem livre):",
            atualCD,
            function(valorDigitado)
                local cdNum = math.max(0, math.floor(num(valorDigitado, 0)));
                sheet.cdTeste = tostring(cdNum);
                executarRolagemD20(titulo, modTotal, detalheExtra, cdNum);
            end,
            function() end,
            true
        );
    else
        executarRolagemD20(titulo, modTotal, detalheExtra, num(sheet.cdTeste, 0));
    end;
end;

local function temFebreCisternasGrave()
    if sheet == nil then return false; end;
    for idx = 1, 3 do
        local did = tostring(sheet["doenca" .. idx .. "_id"] or "");
        local est = math.floor(num(sheet["doenca" .. idx .. "_est"], 0));
        if did == "febre_cisternas" and est >= 2 then
            return true;
        end;
    end;
    return false;
end;

local function descansoCurto()
    if sheet == nil then return; end;
    if temFebreCisternasGrave() then
        local nomeChar = sheet.nome or "Explorador";
        showMessage("Descanso Curto bloqueado por doenca!\n\nFebre das Cisternas em estagio Incapacitante ou Critico impede recuperar PV em Descanso Curto (regra oficial). Hidrate-se e busque cuidados medicos/Descanso Longo!");
        enviarChatOuMsg("[" .. nomeChar .. "] Tentou Descanso Curto, mas Febre das Cisternas (Incapacitante/Critica) impede a recuperacao de PV!");
        return;
    end;
    local dv = math.max(4, math.floor(num(sheet.kitDvFaces, 8)));
    local mCon = getMod("constituicao");
    local modStr = (mCon >= 0) and (" + " .. tostring(mCon)) or (" - " .. tostring(math.abs(mCon)));
    local expr = "1d" .. tostring(dv) .. modStr;
    local rolagem = Firecast.interpretarRolagem(expr);
    local nomeChar = sheet.nome or "Explorador";
    local titulo = "[" .. nomeChar .. "] Descanso Curto — Recuperar PV (" .. expr .. ")";

    local function aplicarCura(val)
        local cura = math.max(1, val);
        local pvM = math.max(1, num(sheet.pvMax, 1));
        local pvA = num(sheet.pvAtual, 0);
        local novo = math.min(pvM, pvA + cura);
        sheet.pvAtual = tostring(novo);
        return cura, novo, pvM;
    end;

    local mesa = Firecast.getMesaDe(sheet);
    if mesa ~= nil and mesa.activeChat ~= nil then
        mesa.activeChat:rolarDados(rolagem, titulo,
            function(rolado)
                if rolado ~= nil then
                    local cura, novo, pvM = aplicarCura(rolado.resultado);
                    mesa.activeChat:enviarMensagem("[" .. nomeChar .. "] Descanso Curto (1h): recuperou +" .. tostring(cura) .. " PV (PV Atual: " .. tostring(novo) .. "/" .. tostring(pvM) .. ").");
                end;
            end);
    else
        rolagem:rolarLocalmente();
        local cura, novo, pvM = aplicarCura(rolagem.resultado);
        showMessage(titulo .. "\nRecuperou +" .. tostring(cura) .. " PV (" .. tostring(novo) .. "/" .. tostring(pvM) .. ")");
    end;
end;

local function descansoLongo()
    if sheet == nil then return; end;
    local pvM = math.max(1, num(sheet.pvMax, 1));
    local cura = math.ceil(pvM * 0.5);
    local pvA = num(sheet.pvAtual, 0);
    local novo = math.min(pvM, pvA + cura);
    sheet.pvAtual = tostring(novo);
    local exAnt = math.max(0, math.min(5, math.floor(num(sheet.exaustaoNivel, 0))));
    local exMsg = " (sem Exaustao ativa)";
    if exAnt > 0 then
        local exNovo = exAnt - 1;
        sheet.exaustaoNivel = tostring(exNovo);
        exMsg = " e reduziu Exaustao (" .. tostring(exAnt) .. " -> " .. tostring(exNovo) .. ")";
    end;
    recalcularFicha();
    local nomeChar = sheet.nome or "Explorador";
    enviarChatOuMsg("[" .. nomeChar .. "] Descanso Longo (8h em abrigo seguro): recuperou +" .. tostring(cura) .. " PV (50% do PV Max — Atual: " .. tostring(novo) .. "/" .. tostring(pvM) .. ")" .. exMsg .. ".");
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

-- Graduacao numerica livre (+0..+16) com Teto Progressivo por Nivel e classificacao automatica:
-- 0 = Destreinado | 1-2 = Iniciante | 3-7 = Treinado | 8-11 = Especialista (Niv 5+) | 12-16 = Mestre (Niv 11+: +12..+14 Lenda, +15..+16 Epico)
local function getTetoGraduacao(nivel)
    local niv = math.max(1, math.min(30, math.floor(num(nivel, 1))));
    return TETO_GRAD_POR_NIVEL[niv] or 16;
end;

local function grauEfetivo(rawVal, nivel)
    local g = math.max(0, math.floor(num(rawVal, 0)));
    local teto = getTetoGraduacao(nivel);
    if g > teto then return teto, true, g; end;
    return g, false, g;
end;

local function nomeGrau(grau, nivel)
    local g = math.max(0, math.floor(num(grau, 0)));
    local teto = getTetoGraduacao(nivel);
    if g > teto then
        return "TETO +" .. tostring(teto) .. "!";
    elseif g >= 12 then
        return "Mestre";
    elseif g >= 8 then
        return "Especialista";
    elseif g >= 3 then
        return "Treinado";
    elseif g >= 1 then
        return "Iniciante";
    else
        return "Destreinado";
    end;
end;

-- Custo progressivo por graduacao (respeitando o teto maximo absoluto +16 = 30 pts):
-- 1-7 = 1 pt cada | 8-11 = 2 pts cada | 12-16 = 3 pts cada
local function custoGrau(grau)
    local g = math.max(0, math.min(16, math.floor(num(grau, 0))));
    if g <= 7 then
        return g;
    elseif g <= 11 then
        return 7 + (g - 7) * 2;
    else
        return 15 + (g - 11) * 3;
    end;
end;

recalcularFicha = function()
    if sheet == nil or sheet._clampingGrad then return; end;

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
    local tetoGrad = getTetoGraduacao(nivel);
    local mesmoNivel = (sheet._lastNivel == nivel);
    sheet._lastNivel = nivel;

    local patNome, _, tetoAttr = getPatamarInfo(nivel);
    sheet.patamarTexto = patNome;
    sheet.tetoAtributoTexto = "Teto Atrib: " .. tostring(tetoAttr) .. " | Grad: +" .. tostring(tetoGrad);
    sheet.tetoGradTexto = "Teto Grad. Niv. " .. tostring(nivel) .. ": +" .. tostring(tetoGrad);

    local xpAtual = math.max(0, math.floor(num(sheet.xpAtual, 0)));
    if nivel >= 30 then
        sheet.xpProxNivel = "MAX (275000)";
        sheet.xpStatus = "Nivel Maximo Epico alcancado (Niv. 30) | Teto Atributo: 22 (+6)";
    else
        local proxXp = XP_TABELA[nivel + 1] or 275000;
        sheet.xpProxNivel = tostring(proxXp) .. " XP";
        local falta = proxXp - xpAtual;
        if falta <= 0 then
            sheet.xpStatus = "PRONTO PARA SUBIR AO NIVEL " .. tostring(nivel + 1) .. "! Clique em Subir Nivel (1dX+CON).";
        else
            sheet.xpStatus = "Faltam " .. tostring(falta) .. " XP para o Nivel " .. tostring(nivel + 1) .. " | Teto Atributo: " .. tostring(tetoAttr);
        end;
    end;

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

    -- Sistema Monetario (Padrao Prata: 1 PO = 10 PP = 100 PC; 100 moedas fisicas = 1 kg)
    local po = math.max(0, math.floor(num(sheet.moedasOuro, 0)));
    local pp = math.max(0, math.floor(num(sheet.moedasPrata, 0)));
    local pc = math.max(0, math.floor(num(sheet.moedasCobre, 0)));
    local cc = math.max(0, num(sheet.cartasCredito, 0));
    local totalMoedasFisicas = po + pp + pc;
    local pesoMoedasKg = totalMoedasFisicas / 100.0;
    local totalPc = (po * 100) + (pp * 10) + pc + math.floor(cc * 10 + 0.5);
    sheet.patrimonioTotal = string.format("%.1f PP (%.2f PO)", totalPc / 10.0, totalPc / 100.0);
    sheet.pesoMoedas = string.format("%.2f kg (%d m.)", pesoMoedasKg, totalMoedasFisicas);
    local pvKey = sheet.padraoVida or "modesto";
    local pvObj = PADROES_VIDA[pvKey] or PADROES_VIDA["modesto"];
    sheet.padraoVidaInfo = "Sustento: " .. pvObj.info .. " | Peso: 100 moedas = 1 kg (Cartas de Credito = 0 kg).";

    -- Exaustao Oficial (Niveis 0-5) & Doencas Ativas (v2.3)
    local exNiv = math.max(0, math.min(5, math.floor(num(sheet.exaustaoNivel, 0))));
    local penExPer = (exNiv >= 1) and -2 or 0;
    local penExComb = (exNiv >= 3) and -3 or 0;
    local penDoencaDef = 0;
    local doencasAtivasNomes = {};
    for dIdx = 1, 3 do
        local did = tostring(sheet["doenca" .. dIdx .. "_id"] or "");
        local dNome = tostring(sheet["doenca" .. dIdx .. "_nome"] or ""):gsub("^%s+", ""):gsub("%s+$", "");
        local dEst = math.max(0, math.min(3, math.floor(num(sheet["doenca" .. dIdx .. "_est"], 0))));
        local dObj = DOENCAS_CATALOGO[did];
        if dEst > 0 and (dNome ~= "" or dObj ~= nil) then
            local nmShow = (dNome ~= "" and dNome) or (dObj and dObj.nome) or ("Doenca " .. tostring(dIdx));
            local estTxt = (dEst == 1 and "Leve") or (dEst == 2 and "Incapacitante") or "Critica";
            table.insert(doencasAtivasNomes, nmShow .. " (" .. estTxt .. ")");
            if dObj ~= nil and dObj.efeitos ~= nil and dObj.efeitos[dEst] ~= nil then
                sheet["doenca" .. dIdx .. "_efeito"] = dObj.efeitos[dEst];
            end;
            if did == "mal_porao" and dEst >= 2 then
                penDoencaDef = penDoencaDef - 2;
            end;
        elseif dEst == 0 then
            if dNome == "" then
                sheet["doenca" .. dIdx .. "_efeito"] = "Slot livre (selecione uma doenca acima e clique em + Contrair).";
            else
                sheet["doenca" .. dIdx .. "_efeito"] = "Curado / Inativo.";
            end;
        end;
    end;

    local bonusCuidados = 0;
    if sheet.cuidadoMedico == true then bonusCuidados = bonusCuidados + 2; end;
    if sheet.cuidadoHerbalista == true then bonusCuidados = bonusCuidados + 2; end;
    if sheet.cuidadoAlquimista == true then bonusCuidados = bonusCuidados + 2; end;
    bonusCuidados = math.min(6, bonusCuidados);
    sheet.cuidadosResumo = "Bonus Cuidados (3 Oficios): +" .. tostring(bonusCuidados) .. " (teto +6)";

    local exDesc = "Sem Exaustao (0)";
    if exNiv == 1 then exDesc = "EXAUSTAO NIV. 1: -2 em todas as pericias (aplicado automaticamente).";
    elseif exNiv == 2 then exDesc = "EXAUSTAO NIV. 2: -2 em pericias + Deslocamento reduzido a metade (4,5m).";
    elseif exNiv == 3 then exDesc = "EXAUSTAO NIV. 3: -2 pericias | -3 Ataques, Defesas e Resistencias (aplicado!).";
    elseif exNiv == 4 then exDesc = "EXAUSTAO NIV. 4: -2 pericias | -3 Combate | PV MAX A METADE (" .. tostring(math.ceil(pvMax * 0.5)) .. " PV)!";
    elseif exNiv >= 5 then exDesc = "EXAUSTAO NIV. 5: COLAPSO E RISCO DE MORTE IMEDIATA! (Socorro urgente!)"; end;
    if #doencasAtivasNomes > 0 then
        exDesc = exDesc .. "  |  Doencas: " .. table.concat(doencasAtivasNomes, "; ");
    end;
    sheet.exaustaoResumo = exDesc;

    -- Desconta 3 pts gratuitos das pericias iniciais (+3) do Kit atual
    local kitGratis = {};
    for i = 1, #kit.pericias do kitGratis[kit.pericias[i]] = true; end;

    local ajustadas = {};
    local acimaTeto = {};
    local acimaBonusExt = {};
    local ptsGastos = 0;
    for i = 1, #SKILLS do
        local sk = SKILLS[i];
        local rawVal = sheet[sk.field .. "_grau"];
        local gRaw = math.max(0, math.floor(num(rawVal, 0)));
        if gRaw > tetoGrad and mesmoNivel then
            sheet._clampingGrad = true;
            sheet[sk.field .. "_grau"] = tostring(tetoGrad);
            sheet._clampingGrad = false;
            gRaw = tetoGrad;
            table.insert(ajustadas, sk.nome);
        elseif gRaw > tetoGrad then
            table.insert(acimaTeto, sk.nome);
        end;
        local gEf = math.min(gRaw, tetoGrad);
        local outros = num(sheet[sk.field .. "_outros"], 0);
        if outros > 6 then
            table.insert(acimaBonusExt, sk.nome .. " (+" .. tostring(outros) .. ")");
        end;
        local tot = getMod(sk.attr) + gEf + outros + penExPer;
        sheet[sk.field .. "_total"] = fmtMod(tot);
        sheet[sk.field .. "_rank"] = nomeGrau(gRaw, nivel);
        local c = custoGrau(gEf);
        if kitGratis[sk.field] then c = math.max(0, c - 3); end;
        ptsGastos = ptsGastos + c;
    end;

    local pagina = math.max(1, math.floor(num(sheet.customSkillPage, 1)));
    sheet.customSkillPageLabel = "Pag. " .. tostring(pagina);
    if sheet.customSkills ~= nil then
        local filhos = NDB.getChildNodes(sheet.customSkills);
        for i = 1, #filhos do
            local cgEf, excedeu = grauEfetivo(filhos[i].grau, nivel);
            local cNome = (filhos[i].nome and filhos[i].nome ~= "" and filhos[i].nome) or "Pericia Livre";
            if excedeu then
                table.insert(acimaTeto, cNome);
            end;
            local cOut = num(filhos[i].outros, 0);
            if cOut > 6 then
                table.insert(acimaBonusExt, cNome .. " (+" .. tostring(cOut) .. ")");
            end;
            ptsGastos = ptsGastos + custoGrau(cgEf);
        end;
    end;
    sheet.periciasGastas = tostring(ptsGastos);

    if #ajustadas > 0 then
        sheet.avisoTetoGrad = "TRAVA ATIVA: " .. table.concat(ajustadas, ", ") .. " ajustada(s) ao teto do Nivel " .. tostring(nivel) .. " (+" .. tostring(tetoGrad) .. ")!";
    elseif #acimaTeto > 0 then
        sheet.avisoTetoGrad = "ATENCAO: " .. tostring(#acimaTeto) .. " pericia(s) acima do teto do Nivel " .. tostring(nivel) .. " (+" .. tostring(tetoGrad) .. ") — bonus travado em +" .. tostring(tetoGrad) .. " ate ajustar ou subir nivel!";
    else
        sheet.avisoTetoGrad = "Dentro do Teto de Graduacao do Nivel " .. tostring(nivel) .. " (max +" .. tostring(tetoGrad) .. " | Teto Absoluto Alenia: +16 no Niv. 26-30).";
    end;

    if #acimaBonusExt > 0 then
        sheet.avisoBonusExt = "AVISO TETO EXTERNO (+6): Coluna OUT acima de +6 em: " .. table.concat(acimaBonusExt, ", ") .. " (ferramentas nao acumulam; teto externo +6, excecao: Rituais +8).";
    else
        sheet.avisoBonusExt = "Bonus externos (OUT) dentro da regra oficial: apenas maior equipamento aplica | teto combinado +6 (excecao: Preparacao Ritualistica +8).";
    end;

    atualizarPaginaCustomSkills();
    if atualizarPaginaInventario ~= nil then
        atualizarPaginaInventario();
    end;
    if recalcularPesoInventario ~= nil then
        recalcularPesoInventario(false);
    end;
    if atualizarPaginaTalentos ~= nil then
        atualizarPaginaTalentos();
    end;

    local armDef = num(sheet.armaduraDef, 0);
    local escDef = num(sheet.escudoDef, 0);
    local defOutros = num(sheet.defesaOutros, 0) + penExComb + penDoencaDef;
    local trAparar = grauEfetivo(sheet.per_aparar_grau, nivel) + num(sheet.per_aparar_outros, 0);
    local trEsquiva = grauEfetivo(sheet.per_esquiva_grau, nivel) + num(sheet.per_esquiva_outros, 0);

    sheet.defAparar = tostring(10 + mDes + armDef + escDef + trAparar + defOutros);
    sheet.defEsquiva = tostring(10 + mDes + armDef + escDef + trEsquiva + defOutros);
    sheet.defDesprevenido = tostring(10 + armDef + escDef + defOutros);

    local trPerc = grauEfetivo(sheet.per_percepcao_grau, nivel);
    sheet.iniciativaTotal = fmtMod(mDes + math.floor(trPerc / 3) + num(sheet.iniciativaOutros, 0));

    for idx = 1, 4 do
        local aAttr = sheet["arma" .. idx .. "_attr"] or "forca";
        local aPer = sheet["arma" .. idx .. "_per"] or "per_armas_brancas";
        local aExtra = num(sheet["arma" .. idx .. "_extra"], 0);
        local gArma = grauEfetivo(sheet[aPer .. "_grau"], nivel);
        local atkTot = getMod(aAttr) + gArma + num(sheet[aPer .. "_outros"], 0) + aExtra + penExComb;
        sheet["arma" .. idx .. "_atk"] = fmtMod(atkTot);
    end;

    if self ~= nil and self.imgRetrato ~= nil and not sheet._retratoInit then
        sheet._retratoInit = true;
        pcall(function()
            self.imgRetrato:setEditable(true);
            self.imgRetrato:setCenter(true);
        end);
    end;

    sheet.pluginVersaoAtual = "v" .. PLUGIN_VERSION;
    if sheet.statusAtualizacao == nil or tostring(sheet.statusAtualizacao) == "" then
        sheet.statusAtualizacao = "Clique no botao acima para checar e instalar atualizacoes automaticamente.";
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

    recalcularFicha();

    if sheet.pvMax == nil or tostring(sheet.pvMax):gsub("%s+", "") == "" or num(sheet.pvMax, 0) <= 0 then
        sheet.pvMax = sheet.pvSugerido;
        sheet.pvAtual = sheet.pvSugerido;
    end;

    local function preencherEquipamentoInicial()
        -- Moedas iniciais do Kit (Padrao Prata)
        if kit.pp ~= nil and kit.pp > 0 then
            sheet.moedasOuro = "0";
            sheet.moedasPrata = tostring(kit.pp);
            sheet.moedasCobre = "0";
        end;
        -- Armadura & Escudo iniciais na Aba Combate
        if kit.armDef ~= nil then
            sheet.armaduraDef = tostring(kit.armDef);
        end;
        if kit.escDef ~= nil then
            sheet.escudoDef = tostring(kit.escDef);
        end;
        -- Arma 1 e Arma 2 iniciais na Aba Combate
        local function gravarArma(slotNum, aObj)
            if aObj == nil then return; end;
            sheet["arma" .. slotNum .. "_nome"] = aObj.nome;
            sheet["arma" .. slotNum .. "_attr"] = aObj.attr;
            sheet["arma" .. slotNum .. "_per"] = aObj.per;
            sheet["arma" .. slotNum .. "_extra"] = "0";
            sheet["arma" .. slotNum .. "_dano"] = aObj.dano;
            sheet["arma" .. slotNum .. "_danoExtra"] = "0";
            sheet["arma" .. slotNum .. "_margem"] = aObj.margem;
            sheet["arma" .. slotNum .. "_mult"] = aObj.mult;
        end;
        if kit.arma1 ~= nil then gravarArma(1, kit.arma1); end;
        if kit.arma2 ~= nil then gravarArma(2, kit.arma2); end;

        -- Itens & Consumiveis iniciais nos Slots de Inventario
        local qtdItens = 0;
        if kit.itens ~= nil and adicionarOuEmpilharNoInventario ~= nil then
            for j = 1, #kit.itens do
                local it = kit.itens[j];
                adicionarOuEmpilharNoInventario(it.nome, it.tipo or "equip", it.qtd or 1, it.peso or 0, it.nota or "");
                qtdItens = qtdItens + 1;
            end;
            sheet.invPage = "1";
            if atualizarPaginaInventario ~= nil then atualizarPaginaInventario(); end;
            if recalcularPesoInventario ~= nil then recalcularPesoInventario(true); end;
        end;

        recalcularFicha();
        showMessage(
            "Kit completo aplicado: " .. kit.nome .. "\n\n" ..
            "- Dado de Vida: 1d" .. tostring(kit.dv) .. " | Pericias Base: " .. tostring(kit.perBase) .. " (Mult INT " .. tostring(kit.multInt) .. "x)\n" ..
            "- Moedas iniciais definidas: " .. tostring(kit.pp or 0) .. " PP\n" ..
            "- Armadura Def +" .. tostring(kit.armDef or 0) .. " | Escudo Def +" .. tostring(kit.escDef or 0) .. "\n" ..
            "- Arma inicial configurada na Aba Combate" .. (kit.arma2 ~= nil and " (2 armas!)" or "") .. "\n" ..
            "- " .. tostring(qtdItens) .. " itens/consumiveis adicionados aos Slots de Inventario!"
        );
    end;

    local resumoEquip = "Moedas: " .. tostring(kit.pp or 25) .. " PP | Armadura +" .. tostring(kit.armDef or 0) .. " / Escudo +" .. tostring(kit.escDef or 0) ..
        (kit.arma1 ~= nil and (" | Arma: " .. kit.arma1.nome) or "") ..
        (kit.itens ~= nil and (" | " .. tostring(#kit.itens) .. " itens nos Slots") or "");

    if DialogsMod ~= nil and type(DialogsMod.confirmYesNo) == "function" then
        DialogsMod.confirmYesNo(
            "Kit aplicado: " .. kit.nome .. " (DV 1d" .. tostring(kit.dv) .. ").\n\n" ..
            "Deseja tambem preencher automaticamente o equipamento inicial completo do Kit?\n(" .. resumoEquip .. ")\n\n" ..
            "[Sim] = Preenche moedas, arma(s) na Aba Combate, armadura e itens nos Slots\n" ..
            "[Nao] = Aplica apenas DV, pericias iniciais e habilidade do Kit",
            function(sim)
                if sim then
                    preencherEquipamentoInicial();
                else
                    showMessage("Kit aplicado: " .. kit.nome .. "\nDado de Vida: 1d" .. tostring(kit.dv) .. " | Pericias Base: " .. tostring(kit.perBase) .. " (Mult INT " .. tostring(kit.multInt) .. "x)");
                end;
            end
        );
    else
        preencherEquipamentoInicial();
    end;
end;

local function receberDano()
    if sheet == nil then return; end;
    if DialogsMod == nil or type(DialogsMod.inputQuery) ~= "function" then
        showMessage("Edite diretamente o campo PV Atual no cabecalho.");
        return;
    end;
    local rd = math.max(0, math.floor(num(sheet.rdEspecial, 0)));
    local promptRd = (rd > 0) and (" (sua RD Especial de " .. tostring(rd) .. " sera descontada automaticamente)") or "";
    DialogsMod.inputQuery(
        "Receber Dano — Alenia RPG",
        "Digite o dano bruto sofrido neste golpe" .. promptRd .. ":",
        "",
        function(valorStr)
            local limpo = tostring(valorStr or ""):gsub("%s+", "");
            local danoBruto = tonumber(limpo);
            if danoBruto == nil or danoBruto <= 0 then
                showMessage("Informe um valor inteiro positivo de dano (ex: 12).");
                return;
            end;
            danoBruto = math.floor(danoBruto);
            local rdNow = math.max(0, math.floor(num(sheet.rdEspecial, 0)));
            local danoEf = math.max(0, danoBruto - rdNow);
            local pvMax = math.max(1, math.floor(num(sheet.pvMax, 1)));
            local pvAnt = math.floor(num(sheet.pvAtual, pvMax));
            local pvNovo = math.max(0, pvAnt - danoEf);
            sheet.pvAtual = tostring(pvNovo);
            recalcularFicha();

            local limiar = math.floor((pvMax * 2) / 3) + 1;
            local devastador = (danoEf >= limiar);
            local nomeChar = sheet.nome or "Explorador";
            local rdMsg = (rdNow > 0) and (" (RD Especial -" .. tostring(rdNow) .. " -> " .. tostring(danoEf) .. " efetivo)") or "";
            local alertasChat = "";
            local alertasPopup = "";

            if devastador then
                local cdDev = 15 + math.floor((danoEf - limiar) / 2);
                alertasChat = alertasChat .. "  *** GOLPE DEVASTADOR! (>2/3 PV Max: " .. tostring(limiar) .. "+) — Teste de CON CD " .. tostring(cdDev) .. " (Falha = Morte Instantanea | Sucesso = Ferimento Grave!) ***";
                alertasPopup = alertasPopup .. "\n\n[GOLPE DEVASTADOR!]\nEste golpe atingiu/superou " .. tostring(limiar) .. " de dano (>2/3 do seu PV Max)!\nRole imediatamente Teste de CON CD " .. tostring(cdDev) .. ":\n- Falha: Morte Instantanea\n- Sucesso: Sobrevive com Ferimento Grave!";
            end;
            if pvNovo <= 0 then
                alertasChat = alertasChat .. "  [CAIU A 0 PV — INCONSCIENTE / MORIBUNDO! Teste CON CD 12 por turno]";
                alertasPopup = alertasPopup .. "\n\n[CAIU A 0 PV — MORIBUNDO!]\nVoce caiu inconsciente! A cada turno role CON CD 12 (3 sucessos estabiliza / 3 falhas morre).";
            end;

            enviarChatOuMsg(
                "[" .. nomeChar .. "] Recebeu " .. tostring(danoBruto) .. " de dano" .. rdMsg ..
                " | PV: " .. tostring(pvAnt) .. " -> " .. tostring(pvNovo) .. "/" .. tostring(pvMax) .. alertasChat
            );
            if alertasPopup ~= "" then
                showMessage("Dano aplicado: -" .. tostring(danoEf) .. " PV (Atual: " .. tostring(pvNovo) .. "/" .. tostring(pvMax) .. ")" .. alertasPopup);
            end;
        end,
        function() end,
        false
    );
end;

local function rolarPericia(fieldId, nomePer, attrField)
    if sheet == nil then return; end;
    local g = grauEfetivo(sheet[fieldId .. "_grau"], sheet.nivel);
    local exNiv = math.max(0, math.min(5, math.floor(num(sheet.exaustaoNivel, 0))));
    local penEx = (exNiv >= 1) and -2 or 0;
    local tot = getMod(attrField) + g + num(sheet[fieldId .. "_outros"], 0) + penEx;
    local rk = nomeGrau(g, sheet.nivel);
    local notaEx = (penEx < 0) and (" [Exaustao Niv." .. tostring(exNiv) .. ": -2]") or "";
    rolarD20("Pericia: " .. nomePer .. " (+" .. tostring(g) .. " — " .. rk .. ")" .. notaEx, tot, "");
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

    local grauPer = grauEfetivo(sheet[aPer .. "_grau"], sheet.nivel);
    local limiteN = maxAcoesPorGrau(grauPer);
    if nAcoes > limiteN then
        showMessage("Multiplas Acoes bloqueadas pela regra v2.0!\nSeu grau nesta pericia (+" .. tostring(grauPer) .. ") permite no maximo " .. tostring(limiteN) .. " acao(oes) por turno.");
        return;
    end;

    local exNiv = math.max(0, math.min(5, math.floor(num(sheet.exaustaoNivel, 0))));
    local penExComb = (exNiv >= 3) and -3 or 0;
    local bonusBase = getMod(aAttr) + grauPer + num(sheet[aPer .. "_outros"], 0) + aExtra + penExComb;
    local bonusFinal = bonusBase;
    if nAcoes > 1 then
        bonusFinal = math.floor(bonusBase / nAcoes) - nAcoes;
        if bonusFinal < 0 then
            showMessage("Multiplas Acoes bloqueadas (Regra Anti-Abuso v2.0)!\nDividir +" .. tostring(bonusBase) .. " em " .. tostring(nAcoes) .. " acoes resulta em bonus negativo (" .. tostring(bonusFinal) .. "). Reduza o numero de acoes!");
            return;
        end;
    end;

    local nomeChar = sheet.nome or "Explorador";
    local defAlvo = math.max(0, math.floor(num(sheet.defesaAlvo, 0)));
    local sufixoDef = (defAlvo > 0) and (" [vs Def " .. tostring(defAlvo) .. "]") or "";
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
        local titulo = "[" .. nomeChar .. "] Ataque com " .. nomeArma .. sufixo .. sufixoDef;
        if mesa ~= nil and mesa.activeChat ~= nil then
            mesa.activeChat:rolarDados(rolagem, titulo,
                function(rolado)
                    local d20Nat = nil;
                    local total = (rolado ~= nil and rolado.resultado) or 0;
                    if rolado ~= nil and rolado.ops ~= nil then
                        for i = 1, #rolado.ops do
                            local op = rolado.ops[i];
                            if op.tipo == "dado" and op.resultados ~= nil and #op.resultados >= 1 then
                                d20Nat = op.resultados[1];
                                break;
                            end;
                        end;
                    end;
                    local acertou = (defAlvo == 0) or (d20Nat == 20) or (d20Nat ~= 1 and total >= defAlvo);
                    if d20Nat == 1 then
                        mesa.activeChat:enviarMensagem("[FALHA CRITICA! 1 Natural] Erro automatico e abertura tatica com " .. nomeArma .. "!");
                    elseif d20Nat ~= nil and d20Nat >= margem and acertou then
                        mesa.activeChat:enviarMensagem("[ACERTO CRITICO! Dado " .. tostring(d20Nat) .. " | Total " .. tostring(total) .. (defAlvo > 0 and (" vs Def " .. tostring(defAlvo)) or "") .. "] " .. nomeArma .. " multiplica (dados + FOR/fixo) por x" .. tostring(mult) .. "!");
                    elseif defAlvo > 0 then
                        if acertou then
                            mesa.activeChat:enviarMensagem("[ACERTOU!] " .. nomeArma .. " atingiu (" .. tostring(total) .. " vs Def " .. tostring(defAlvo) .. "). Role o dano!");
                        else
                            mesa.activeChat:enviarMensagem("[ERROU!] " .. nomeArma .. " nao superou a Defesa (" .. tostring(total) .. " vs Def " .. tostring(defAlvo) .. ").");
                        end;
                    end;
                end);
        else
            rolagem:rolarLocalmente();
            local res = rolagem.resultado;
            local infoDef = "";
            if defAlvo > 0 then
                infoDef = (res >= defAlvo) and ("\n[ACERTOU vs Def " .. tostring(defAlvo) .. "]") or ("\n[ERROU vs Def " .. tostring(defAlvo) .. "]");
            end;
            showMessage(titulo .. "\nResultado: " .. tostring(res) .. infoDef);
        end;
    end;
end;

local function rolarDanoArma(idx, isCrit)
    if sheet == nil then return; end;
    local nomeArma = sheet["arma" .. idx .. "_nome"];
    if nomeArma == nil or nomeArma == "" then nomeArma = "Arma " .. tostring(idx); end;
    local dado = sheet["arma" .. idx .. "_dano"];
    if dado == nil or dado == "" then dado = "1d6"; end;
    local aPer = sheet["arma" .. idx .. "_per"] or "per_armas_brancas";
    local danoExtra = num(sheet["arma" .. idx .. "_danoExtra"], 0);
    local mult = num(sheet["arma" .. idx .. "_mult"], 2);

    -- Armas corpo a corpo (Armas Brancas e Luta Desarmada) SEMPRE somam Mod(FOR) no dano!
    local isCorpoACorpo = (aPer == "per_armas_brancas") or (aPer == "per_luta_desarm");
    local modFor = isCorpoACorpo and getMod("forca") or 0;
    local modDano = modFor + danoExtra;

    local expr = dado;
    if modDano > 0 then expr = expr .. " + " .. tostring(modDano);
    elseif modDano < 0 then expr = expr .. " - " .. tostring(math.abs(modDano)); end;

    if isCrit then
        expr = "(" .. expr .. ") * " .. tostring(mult);
    end;

    local rolagem = Firecast.interpretarRolagem(expr);
    local nomeChar = sheet.nome or "Explorador";
    local notaFor = isCorpoACorpo and (" [FOR " .. fmtMod(modFor) .. "]") or " [Distancia]";
    local tag = isCrit and ("DANO CRITICO (x" .. tostring(mult) .. ") — ") or "Dano — ";
    local titulo = "[" .. nomeChar .. "] " .. tag .. nomeArma .. notaFor;
    local mesa = Firecast.getMesaDe(sheet);
    if mesa ~= nil and mesa.activeChat ~= nil then
        mesa.activeChat:rolarDados(rolagem, titulo,
            function(rolado)
                if rolado ~= nil then
                    mesa.activeChat:enviarMensagem("Dano total (" .. expr .. "): " .. tostring(rolado.resultado) .. " | Lembrete: se superar 2/3 do PV Maximo do alvo, ele faz teste de CON ou sofre MORTE INSTANTANEA! (Dados extras como veneno/Oportunista somam apos o critico.)");
                end;
            end);
    else
        rolagem:rolarLocalmente();
        showMessage(titulo .. "\nFormula: " .. expr .. "\nResultado: " .. tostring(rolagem.resultado));
    end;
end;

local function acaoDefensiva(modo)
    if sheet == nil then return; end;
    local nomeChar = sheet.nome or "Explorador";
    local maxTreino = math.max(
        grauEfetivo(sheet.per_aparar_grau, sheet.nivel),
        grauEfetivo(sheet.per_esquiva_grau, sheet.nivel),
        grauEfetivo(sheet.per_escudos_grau, sheet.nivel)
    );
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
        local gEf = grauEfetivo(grau, niv);
        sheet["csk" .. i .. "_nome"] = nome;
        sheet["csk" .. i .. "_attr"] = attr;
        sheet["csk" .. i .. "_grau"] = tostring(grau);
        sheet["csk" .. i .. "_rank"] = nomeGrau(grau, niv);
        sheet["csk" .. i .. "_outros"] = tostring(outros);
        local tot = getMod(attr) + gEf + num(outros, 0);
        sheet["csk" .. i .. "_total"] = fmtMod(tot);
    end;
    sheet._updatingCustom = false;
end;

local function salvarCustomSlot(slotIdx)
    if sheet == nil or sheet._updatingCustom then return; end;
    local node = getCustomSlotNode(slotIdx);
    if node == nil then return; end;
    local niv = math.max(1, math.min(30, math.floor(num(sheet.nivel, 1))));
    local tetoGrad = getTetoGraduacao(niv);
    local gRaw = math.max(0, math.floor(num(sheet["csk" .. slotIdx .. "_grau"], 0)));
    if gRaw > tetoGrad then
        gRaw = tetoGrad;
        sheet._updatingCustom = true;
        sheet["csk" .. slotIdx .. "_grau"] = tostring(tetoGrad);
        sheet._updatingCustom = false;
        local nomeAlvo = sheet["csk" .. slotIdx .. "_nome"];
        if nomeAlvo == nil or nomeAlvo == "" then nomeAlvo = "Pericia Livre #" .. tostring(slotIdx); end;
        sheet.avisoTetoGrad = "TRAVA ATIVA: " .. nomeAlvo .. " ajustada ao teto do Nivel " .. tostring(niv) .. " (+" .. tostring(tetoGrad) .. ")!";
    end;
    node.nome = sheet["csk" .. slotIdx .. "_nome"] or "";
    node.attr = sheet["csk" .. slotIdx .. "_attr"] or "inteligencia";
    node.grau = tostring(gRaw);
    node.outros = sheet["csk" .. slotIdx .. "_outros"] or "0";
    sheet["csk" .. slotIdx .. "_rank"] = nomeGrau(gRaw, niv);
    local tot = getMod(node.attr) + gRaw + num(node.outros, 0);
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
    local grau = grauEfetivo(sheet["csk" .. slotIdx .. "_grau"], sheet.nivel);
    local outros = num(sheet["csk" .. slotIdx .. "_outros"], 0);
    local exNiv = math.max(0, math.min(5, math.floor(num(sheet.exaustaoNivel, 0))));
    local penEx = (exNiv >= 1) and -2 or 0;
    local rk = nomeGrau(grau, sheet.nivel);
    local notaEx = (penEx < 0) and (" [Exaustao Niv." .. tostring(exNiv) .. ": -2]") or "";
    rolarD20("Pericia Livre: " .. nome .. " (+" .. tostring(grau) .. " — " .. rk .. ")" .. notaEx, getMod(attr) + grau + outros + penEx, "");
end;

-- =========================================================================
-- AUTOMACAO DE DOENCAS, SURTOS & COLABORACAO DOS 3 OFICIOS (v2.3)
-- =========================================================================
local function verFichaDoenca()
    if sheet == nil then return; end;
    local did = tostring(sheet.doencaSelecionada or "febre_cisternas");
    local d = DOENCAS_CATALOGO[did] or DOENCAS_CATALOGO["febre_cisternas"];
    local attrSig = (d.attr == "sabedoria") and "SAB" or "CON";
    showMessage(
        "FICHA OFICIAL DE DOENCA — ALENIA RPG\n\n" ..
        d.nome .. " (" .. d.natureza .. ")\n" ..
        "Teste de Resistencia: " .. attrSig .. " CD " .. tostring(d.cd) .. "  |  Ritmo: " .. d.ritmo .. "\n\n" ..
        "1. Exposicao: " .. d.exposicao .. "\n" ..
        "2. Incubacao: " .. d.incubacao .. "\n" ..
        "3. Sinais: " .. d.sinais .. "\n" ..
        "4. Evolucao:\n   - " .. d.efeitos[1] .. "\n   - " .. d.efeitos[2] .. "\n   - " .. d.efeitos[3] .. "\n" ..
        "5. Cuidados: " .. d.cuidados .. "\n" ..
        "6. Sequelas: " .. d.sequelas .. "\n" ..
        "7. Controle do Surto: " .. d.controle
    );
end;

local function contrairDoencaSelecionada()
    if sheet == nil then return; end;
    local did = tostring(sheet.doencaSelecionada or "febre_cisternas");
    local d = DOENCAS_CATALOGO[did] or DOENCAS_CATALOGO["febre_cisternas"];
    local slotLivre = nil;
    for i = 1, 3 do
        local est = math.floor(num(sheet["doenca" .. i .. "_est"], 0));
        local curId = tostring(sheet["doenca" .. i .. "_id"] or "");
        if est > 0 and curId == did and did ~= "personalizada" then
            showMessage("Este personagem ja esta com '" .. d.nome .. "' ativa no Slot " .. tostring(i) .. "!");
            return;
        end;
        if est == 0 and slotLivre == nil then
            slotLivre = i;
        end;
    end;
    if slotLivre == nil then
        showMessage("Todos os 3 slots de doencas ativas estao ocupados! Cure ou limpe um slot antes de adicionar outra.");
        return;
    end;

    sheet["doenca" .. slotLivre .. "_id"] = did;
    sheet["doenca" .. slotLivre .. "_nome"] = d.nome;
    sheet["doenca" .. slotLivre .. "_est"] = "1";
    sheet["doenca" .. slotLivre .. "_attr"] = d.attr;
    sheet["doenca" .. slotLivre .. "_cd"] = tostring(d.cd);
    sheet["doenca" .. slotLivre .. "_suc"] = "0";
    sheet["doenca" .. slotLivre .. "_efeito"] = d.efeitos[1];

    local exSug = (d.exaustao and d.exaustao[1]) or 0;
    local exAtual = math.max(0, math.min(5, math.floor(num(sheet.exaustaoNivel, 0))));
    if exSug > exAtual then
        sheet.exaustaoNivel = tostring(exSug);
    end;

    recalcularFicha();
    local nomeChar = sheet.nome or "Explorador";
    enviarChatOuMsg(
        "[" .. nomeChar .. "] Contraiu doenca: " .. d.nome .. " (Estagio 1: Leve | " ..
        ((d.attr == "sabedoria") and "SAB" or "CON") .. " CD " .. tostring(d.cd) .. " — " .. d.ritmo .. ") — " .. d.efeitos[1]
    );
end;

local function testarDoencaSlot(slotIdx)
    if sheet == nil then return; end;
    local est = math.max(0, math.min(3, math.floor(num(sheet["doenca" .. slotIdx .. "_est"], 0))));
    local nomeD = tostring(sheet["doenca" .. slotIdx .. "_nome"] or ""):gsub("^%s+", ""):gsub("%s+$", "");
    if est == 0 or nomeD == "" then
        showMessage("Este slot de doenca esta vazio ou curado.");
        return;
    end;
    local did = tostring(sheet["doenca" .. slotIdx .. "_id"] or "personalizada");
    local dObj = DOENCAS_CATALOGO[did] or DOENCAS_CATALOGO["personalizada"];
    local attr = tostring(sheet["doenca" .. slotIdx .. "_attr"] or dObj.attr or "constituicao");
    local attrSig = (attr == "sabedoria") and "SAB" or "CON";
    local cd = math.max(5, math.floor(num(sheet["doenca" .. slotIdx .. "_cd"], dObj.cd or 14)));
    local sucAtual = math.max(0, math.floor(num(sheet["doenca" .. slotIdx .. "_suc"], 0)));

    local bonusCuidados = 0;
    local oficios = {};
    if sheet.cuidadoMedico == true then bonusCuidados = bonusCuidados + 2; table.insert(oficios, "Medico"); end;
    if sheet.cuidadoHerbalista == true then bonusCuidados = bonusCuidados + 2; table.insert(oficios, "Herbalista"); end;
    if sheet.cuidadoAlquimista == true then bonusCuidados = bonusCuidados + 2; table.insert(oficios, "Alquimista"); end;
    bonusCuidados = math.min(6, bonusCuidados);

    local exNiv = math.max(0, math.min(5, math.floor(num(sheet.exaustaoNivel, 0))));
    local penEx = (exNiv >= 3) and -3 or 0;
    local modTot = getMod(attr) + bonusCuidados + penEx;

    local expr = (modTot >= 0) and ("1d20 + " .. tostring(modTot)) or ("1d20 - " .. tostring(math.abs(modTot)));
    local rolagem = Firecast.interpretarRolagem(expr);
    local nomeChar = sheet.nome or "Explorador";
    local cuidTxt = (#oficios > 0) and (" [Cuidados +" .. tostring(bonusCuidados) .. ": " .. table.concat(oficios, "+") .. "]") or "";
    local titulo = "[" .. nomeChar .. "] Resistencia a Doenca: " .. nomeD .. " (" .. attrSig .. " vs CD " .. tostring(cd) .. ")" .. cuidTxt;

    local function processarResultado(res)
        local estNomes = { "Leve", "Incapacitante", "Critica" };
        if res >= cd then
            if est > 1 then
                local novoEst = est - 1;
                sheet["doenca" .. slotIdx .. "_est"] = tostring(novoEst);
                sheet["doenca" .. slotIdx .. "_suc"] = "1";
                recalcularFicha();
                enviarChatOuMsg("[" .. nomeChar .. "] SUCESSO (" .. tostring(res) .. " vs CD " .. tostring(cd) .. ") contra " .. nomeD .. "! Recuou para Estagio " .. tostring(novoEst) .. " (" .. estNomes[novoEst] .. ") — " .. tostring(sheet["doenca" .. slotIdx .. "_efeito"] or ""));
            else
                local novoSuc = sucAtual + 1;
                if novoSuc >= 2 then
                    sheet["doenca" .. slotIdx .. "_est"] = "0";
                    sheet["doenca" .. slotIdx .. "_suc"] = "0";
                    sheet["doenca" .. slotIdx .. "_id"] = "";
                    sheet["doenca" .. slotIdx .. "_nome"] = "";
                    recalcularFicha();
                    enviarChatOuMsg("[" .. nomeChar .. "] SUCESSO (" .. tostring(res) .. " vs CD " .. tostring(cd) .. " — 2/2 sucessos)! RECUPERADO de " .. nomeD .. "! (Lembre de verificar eventuais sequelas de casos graves com o Mestre.)");
                else
                    sheet["doenca" .. slotIdx .. "_suc"] = tostring(novoSuc);
                    recalcularFicha();
                    enviarChatOuMsg("[" .. nomeChar .. "] SUCESSO (" .. tostring(res) .. " vs CD " .. tostring(cd) .. ") contra " .. nomeD .. "! Estavel em Leve (" .. tostring(novoSuc) .. "/2 sucessos para cura).");
                end;
            end;
        else
            sheet["doenca" .. slotIdx .. "_suc"] = "0";
            if est < 3 then
                local novoEst = est + 1;
                sheet["doenca" .. slotIdx .. "_est"] = tostring(novoEst);
                local exSug = (dObj.exaustao and dObj.exaustao[novoEst]) or 0;
                local exNow = math.max(0, math.min(5, math.floor(num(sheet.exaustaoNivel, 0))));
                if exSug > exNow then
                    sheet.exaustaoNivel = tostring(exSug);
                end;
                recalcularFicha();
                enviarChatOuMsg("[" .. nomeChar .. "] FALHA (" .. tostring(res) .. " vs CD " .. tostring(cd) .. ") contra " .. nomeD .. "! AGRAVOU para Estagio " .. tostring(novoEst) .. " (" .. estNomes[novoEst] .. ") — " .. tostring(sheet["doenca" .. slotIdx .. "_efeito"] or ""));
            else
                local extraCrit = " Risco grave/morte iminente sem tratamento imediato!";
                if did == "mal_porao" then
                    sheet.pvAtual = "0";
                    extraCrit = " CAIU A 0 PV (MORIBUNDO — teste CON CD 12 por turno)!";
                elseif did == "febre_cisternas" then
                    extraCrit = " DESIDRATACAO SEVERA: risco de coma e morte em 24h sem hidratacao assistida!";
                end;
                recalcularFicha();
                enviarChatOuMsg("[" .. nomeChar .. "] FALHA CRITICA (" .. tostring(res) .. " vs CD " .. tostring(cd) .. ") em Estagio Critico de " .. nomeD .. "!" .. extraCrit);
                showMessage("CRISE CRITICA DE DOENCA!\n\nFalha em Estagio Critico de " .. nomeD .. " (" .. tostring(res) .. " vs CD " .. tostring(cd) .. ").\n" .. extraCrit);
            end;
        end;
    end;

    local mesa = Firecast.getMesaDe(sheet);
    if mesa ~= nil and mesa.activeChat ~= nil then
        mesa.activeChat:rolarDados(rolagem, titulo, function(rolado)
            if rolado ~= nil then processarResultado(rolado.resultado); end;
        end);
    else
        rolagem:rolarLocalmente();
        processarResultado(rolagem.resultado);
    end;
end;

local function limparDoencaSlot(slotIdx)
    if sheet == nil then return; end;
    local nomeD = tostring(sheet["doenca" .. slotIdx .. "_nome"] or ""):gsub("^%s+", ""):gsub("%s+$", "");
    local function limpar()
        sheet["doenca" .. slotIdx .. "_id"] = "";
        sheet["doenca" .. slotIdx .. "_nome"] = "";
        sheet["doenca" .. slotIdx .. "_est"] = "0";
        sheet["doenca" .. slotIdx .. "_attr"] = "constituicao";
        sheet["doenca" .. slotIdx .. "_cd"] = "14";
        sheet["doenca" .. slotIdx .. "_suc"] = "0";
        sheet["doenca" .. slotIdx .. "_efeito"] = "Slot livre (selecione uma doenca acima e clique em + Contrair).";
        recalcularFicha();
    end;
    if nomeD ~= "" and DialogsMod ~= nil and type(DialogsMod.confirmYesNo) == "function" then
        DialogsMod.confirmYesNo("Marcar '" .. nomeD .. "' como curada e limpar este slot?", function(sim) if sim then limpar(); end; end);
    else
        limpar();
    end;
end;

local function aplicarDeltaCobres(deltaPc, motivo)
    if sheet == nil then return false; end;
    local po = math.max(0, math.floor(num(sheet.moedasOuro, 0)));
    local pp = math.max(0, math.floor(num(sheet.moedasPrata, 0)));
    local pc = math.max(0, math.floor(num(sheet.moedasCobre, 0)));
    local bolsaPc = (po * 100) + (pp * 10) + pc;
    local novoPc = bolsaPc + deltaPc;
    if novoPc < 0 then
        showMessage("Moedas fisicas insuficientes! Voce tem " .. string.format("%.1f PP", bolsaPc / 10.0) .. " na bolsa e precisa de " .. string.format("%.1f PP", math.abs(deltaPc) / 10.0) .. ".\n(Se tiver saldo em Cartas de Credito, saque em um banco de Corallis ou Kalis.)");
        return false;
    end;
    if deltaPc >= 0 then
        -- Ao receber, mantem Ouro existente e adiciona ganho em Pratas e Cobres (Padrao Prata)
        local addPp = math.floor(deltaPc / 10);
        local addPc = deltaPc % 10;
        pp = pp + addPp;
        pc = pc + addPc;
        if pc >= 10 then
            pp = pp + math.floor(pc / 10);
            pc = pc % 10;
        end;
    else
        -- Ao gastar, consome primeiro Cobres -> Pratas -> quebra Aureos dando troco em Prata
        local gasto = math.abs(deltaPc);
        local novoTotal = bolsaPc - gasto;
        local ouroMantido = math.min(po, math.floor(novoTotal / 100));
        local resto = novoTotal - (ouroMantido * 100);
        po = ouroMantido;
        pp = math.floor(resto / 10);
        pc = resto % 10;
    end;
    sheet.moedasOuro = tostring(po);
    sheet.moedasPrata = tostring(pp);
    sheet.moedasCobre = tostring(pc);
    recalcularFicha();
    local nomeChar = sheet.nome or "Explorador";
    local sinal = (deltaPc >= 0) and "+" or "-";
    enviarChatOuMsg("[" .. nomeChar .. "] " .. motivo .. ": " .. sinal .. string.format("%.1f PP", math.abs(deltaPc) / 10.0) .. " | Bolsa: " .. tostring(po) .. " PO, " .. tostring(pp) .. " PP, " .. tostring(pc) .. " PC.");
    return true;
end;

local function registrarTransacao()
    if sheet == nil then return; end;
    if DialogsMod == nil or type(DialogsMod.inputQuery) ~= "function" then
        showMessage("Edite diretamente os campos Aureos (PO), Pratas (PP) e Cobres (PC).");
        return;
    end;
    DialogsMod.inputQuery(
        "Transacao em Pratas (PP)",
        "Digite o valor em PP (+ para receber, - para pagar; ex: +60 ou -12.5):",
        "",
        function(valorStr)
            local limpo = tostring(valorStr or ""):gsub(",", "."):gsub("%s+", "");
            local valPp = tonumber(limpo);
            if valPp == nil or valPp == 0 then
                showMessage("Informe um numero valido diferente de zero (ex: +45 ou -5.5).");
                return;
            end;
            local deltaPc = (valPp > 0) and math.floor(valPp * 10 + 0.5) or -math.floor(math.abs(valPp) * 10 + 0.5);
            local acao = (deltaPc >= 0) and "Recebeu pagamento/espolio" or "Pagou despesa";
            aplicarDeltaCobres(deltaPc, acao);
        end,
        function() end,
        false
    );
end;

local function converterTroco()
    if sheet == nil then return; end;
    local po = math.max(0, math.floor(num(sheet.moedasOuro, 0)));
    local pp = math.max(0, math.floor(num(sheet.moedasPrata, 0)));
    local pc = math.max(0, math.floor(num(sheet.moedasCobre, 0)));
    local totalPc = (po * 100) + (pp * 10) + pc;
    local function aplicar(consolidarOuro)
        if consolidarOuro then
            po = math.floor(totalPc / 100);
            local resto = totalPc % 100;
            pp = math.floor(resto / 10);
            pc = resto % 10;
        else
            local resto = totalPc - (po * 100);
            if resto < 0 then
                po = math.floor(totalPc / 100);
                resto = totalPc % 100;
            end;
            pp = math.floor(resto / 10);
            pc = resto % 10;
        end;
        sheet.moedasOuro = tostring(po);
        sheet.moedasPrata = tostring(pp);
        sheet.moedasCobre = tostring(pc);
        recalcularFicha();
        showMessage("Troco consolidado!\nBolsa atual: " .. tostring(po) .. " PO (Aureos), " .. tostring(pp) .. " PP (Pratas), " .. tostring(pc) .. " PC (Cobres).\nPeso fisico: " .. tostring(sheet.pesoMoedas));
    end;
    if DialogsMod ~= nil and type(DialogsMod.confirmYesNo) == "function" then
        DialogsMod.confirmYesNo(
            "Deseja tambem converter cada 10 Pratas (PP) em 1 Aureo (PO) para reduzir peso na carga?\n\n[Sim] = Consolida tudo ate Aureos (PO)\n[Nao] = Converte apenas 10 Cobres -> 1 Prata (mantem Padrao Prata)",
            function(sim) aplicar(sim == true); end
        );
    else
        aplicar(false);
    end;
end;

local function pagarPadraoVida()
    if sheet == nil then return; end;
    local pvKey = sheet.padraoVida or "modesto";
    local pvObj = PADROES_VIDA[pvKey] or PADROES_VIDA["modesto"];
    if pvObj.custo <= 0 then
        local nomeChar = sheet.nome or "Explorador";
        enviarChatOuMsg("[" .. nomeChar .. "] Manteve Padrao de Vida Miseravel (0 PP/mes — sujeito a risco de doenca/roubo e -2 social).");
        return;
    end;
    local custoPc = pvObj.custo * 10;
    if DialogsMod ~= nil and type(DialogsMod.confirmYesNo) == "function" then
        DialogsMod.confirmYesNo(
            "Descontar " .. tostring(pvObj.custo) .. " PP da sua bolsa pelo mes de Padrao de Vida " .. pvObj.nome .. "?",
            function(sim)
                if sim then
                    aplicarDeltaCobres(-custoPc, "Padrao de Vida Mensal (" .. pvObj.nome .. ")");
                end;
            end
        );
    else
        aplicarDeltaCobres(-custoPc, "Padrao de Vida Mensal (" .. pvObj.nome .. ")");
    end;
end;

local function formatarPrecoPc(pc)
    local v = math.max(0, math.floor(num(pc, 0)));
    if v >= 100 and (v % 100 == 0) then
        return tostring(math.floor(v / 10)) .. " PP (" .. tostring(math.floor(v / 100)) .. " PO)";
    elseif v >= 10 and (v % 10 == 0) then
        return tostring(math.floor(v / 10)) .. " PP";
    elseif v >= 10 then
        return tostring(v) .. " PC (" .. string.format("%.1f PP", v / 10.0) .. ")";
    else
        return tostring(v) .. " PC";
    end;
end;

local function parsePesoNum(val)
    local raw = tostring(val or "0"):gsub(",", ".");
    local n = tonumber(raw:match("%-?%d+%.?%d*"));
    if n == nil or n < 0 then return 0; end;
    return n;
end;

local function fmtPesoNum(v)
    local n = tonumber(v) or 0;
    if n <= 0 then return "0"; end;
    if n < 0.1 then
        return string.format("%.2f", n):gsub("0+$", ""):gsub("%.$", "");
    end;
    return string.format("%.2f", n):gsub("0+$", ""):gsub("%.$", "");
end;

local function getInvSlotNodeByGlobal(globalIdx)
    if sheet == nil then return nil; end;
    if sheet.invSlots == nil then sheet.invSlots = {}; end;
    local key = "it" .. tostring(globalIdx);
    if sheet.invSlots[key] == nil then
        sheet.invSlots[key] = {};
    end;
    return sheet.invSlots[key];
end;

local function getInvSlotNode(slotIdx)
    if sheet == nil then return nil, 1; end;
    local pagina = math.max(1, math.floor(num(sheet.invPage, 1)));
    local globalIdx = (pagina - 1) * 10 + slotIdx;
    return getInvSlotNodeByGlobal(globalIdx), globalIdx;
end;

recalcularPesoInventario = function(atualizarCarga)
    if sheet == nil then return 0, 0; end;
    local totalKg = 0;
    local ocupados = 0;
    if sheet.invSlots ~= nil then
        local filhos = NDB.getChildNodes(sheet.invSlots);
        for i = 1, #filhos do
            local nd = filhos[i];
            local nm = tostring(nd.nome or ""):gsub("^%s+", ""):gsub("%s+$", "");
            if nm ~= "" then
                ocupados = ocupados + 1;
                local q = math.max(0, math.floor(num(nd.qtd, 0)));
                local p = parsePesoNum(nd.peso);
                totalKg = totalKg + (q * p);
            end;
        end;
    end;
    sheet.invPesoTotal = string.format("%.1f kg (%d itens)", totalKg, ocupados);
    if (atualizarCarga == true) or (ocupados > 0) then
        local fmt = string.format("%.1f", totalKg):gsub("%.0$", "");
        sheet.cargaAtual = fmt;
    end;
    return totalKg, ocupados;
end;

atualizarPaginaInventario = function()
    if sheet == nil or sheet._updatingInv then return; end;
    sheet._updatingInv = true;
    local pagina = math.max(1, math.floor(num(sheet.invPage, 1)));
    local inicio = (pagina - 1) * 10 + 1;
    local fim = pagina * 10;
    sheet.invPageLabel = "Pag. " .. tostring(pagina) .. " (" .. tostring(inicio) .. "-" .. tostring(fim) .. ")";
    for i = 1, 10 do
        local node = getInvSlotNode(i);
        local nome = (node ~= nil and node.nome) or "";
        local tipo = (node ~= nil and node.tipo and node.tipo ~= "" and node.tipo) or "equip";
        local qtd = (node ~= nil and node.qtd and node.qtd ~= "" and node.qtd) or "";
        local peso = (node ~= nil and node.peso and node.peso ~= "" and node.peso) or "";
        local nota = (node ~= nil and node.nota) or "";
        sheet["inv" .. i .. "_nome"] = nome;
        sheet["inv" .. i .. "_tipo"] = tipo;
        sheet["inv" .. i .. "_qtd"] = tostring(qtd);
        sheet["inv" .. i .. "_peso"] = tostring(peso);
        sheet["inv" .. i .. "_nota"] = nota;
    end;
    sheet._updatingInv = false;
end;

local function salvarInvSlot(slotIdx)
    if sheet == nil or sheet._updatingInv then return; end;
    local node, gIdx = getInvSlotNode(slotIdx);
    if node == nil then return; end;
    local nome = tostring(sheet["inv" .. slotIdx .. "_nome"] or "");
    local tipo = tostring(sheet["inv" .. slotIdx .. "_tipo"] or "equip");
    if tipo == "" then tipo = "equip"; end;
    local qtdStr = tostring(sheet["inv" .. slotIdx .. "_qtd"] or "");
    if nome:gsub("%s+", "") ~= "" and qtdStr:gsub("%s+", "") == "" then
        qtdStr = "1";
        sheet._updatingInv = true;
        sheet["inv" .. slotIdx .. "_qtd"] = "1";
        sheet._updatingInv = false;
    end;
    node.nome = nome;
    node.tipo = tipo;
    node.qtd = qtdStr;
    node.peso = tostring(sheet["inv" .. slotIdx .. "_peso"] or "");
    node.nota = tostring(sheet["inv" .. slotIdx .. "_nota"] or "");
    local maxIdx = math.max(20, math.floor(num(sheet.invMaxIdx, 20)));
    if gIdx > maxIdx then sheet.invMaxIdx = tostring(gIdx); end;
    recalcularPesoInventario(true);
end;

local function mudarPaginaInventario(delta)
    if sheet == nil then return; end;
    local pag = math.max(1, math.floor(num(sheet.invPage, 1)) + delta);
    sheet.invPage = tostring(pag);
    local maxIdx = math.max(20, math.floor(num(sheet.invMaxIdx, 20)));
    if pag * 10 > maxIdx then sheet.invMaxIdx = tostring(pag * 10); end;
    atualizarPaginaInventario();
end;

adicionarOuEmpilharNoInventario = function(nome, tipo, qtdAdd, pesoUn, nota)
    if sheet == nil then return 1, 1, false; end;
    if sheet.invSlots == nil then sheet.invSlots = {}; end;
    local filhos = NDB.getChildNodes(sheet.invSlots);
    local maxIdx = math.max(30, math.floor(num(sheet.invMaxIdx, 30)), #filhos + 15);
    local alvoNome = tostring(nome or ""):gsub("^%s+", ""):gsub("%s+$", ""):lower();
    local alvoTipo = tostring(tipo or "equip");
    local primeiroVazio = nil;

    for idx = 1, maxIdx do
        local key = "it" .. tostring(idx);
        local nd = sheet.invSlots[key];
        local nm = (nd ~= nil and tostring(nd.nome or ""):gsub("^%s+", ""):gsub("%s+$", "")) or "";
        if nm == "" then
            if primeiroVazio == nil then primeiroVazio = idx; end;
        elseif nm:lower() == alvoNome and (tostring(nd.tipo or "equip") == alvoTipo) then
            local qAtual = math.max(0, math.floor(num(nd.qtd, 0)));
            nd.qtd = tostring(qAtual + qtdAdd);
            if parsePesoNum(nd.peso) == 0 and pesoUn > 0 then
                nd.peso = fmtPesoNum(pesoUn);
            end;
            if tostring(nd.nota or "") == "" and tostring(nota or "") ~= "" then
                nd.nota = nota;
            end;
            local pag = math.floor((idx - 1) / 10) + 1;
            return idx, pag, true;
        end;
    end;

    local destIdx = primeiroVazio or (maxIdx + 1);
    if destIdx > maxIdx then
        sheet.invMaxIdx = tostring(destIdx + 10);
    end;
    local nd = getInvSlotNodeByGlobal(destIdx);
    nd.nome = nome;
    nd.tipo = alvoTipo;
    nd.qtd = tostring(qtdAdd);
    nd.peso = fmtPesoNum(pesoUn);
    nd.nota = nota or "";
    local pag = math.floor((destIdx - 1) / 10) + 1;
    return destIdx, pag, false;
end;

local function usarSlotInventario(slotIdx)
    if sheet == nil then return; end;
    local node = getInvSlotNode(slotIdx);
    local nome = tostring((node ~= nil and node.nome) or sheet["inv" .. slotIdx .. "_nome"] or ""):gsub("^%s+", ""):gsub("%s+$", "");
    if nome == "" then
        showMessage("Este slot esta vazio. Digite um item ou compre no Emporio acima.");
        return;
    end;
    local tipo = tostring((node ~= nil and node.tipo) or sheet["inv" .. slotIdx .. "_tipo"] or "equip");
    local qtd = math.max(0, math.floor(num((node ~= nil and node.qtd) or sheet["inv" .. slotIdx .. "_qtd"], 0)));
    local pesoUn = parsePesoNum((node ~= nil and node.peso) or sheet["inv" .. slotIdx .. "_peso"]);
    local nota = tostring((node ~= nil and node.nota) or sheet["inv" .. slotIdx .. "_nota"] or ""):gsub("^%s+", ""):gsub("%s+$", "");
    local nomeChar = sheet.nome or "Explorador";
    local det = (nota ~= "") and (" — " .. nota) or "";

    if tipo == "cons" then
        if qtd <= 0 then
            showMessage("Sem usos/unidades restantes de '" .. nome .. "'!\nCompre mais no Emporio acima ou clique em [+1] para reabastecer.");
            return;
        end;
        local novaQtd = qtd - 1;
        if node ~= nil then node.qtd = tostring(novaQtd); end;
        sheet._updatingInv = true;
        sheet["inv" .. slotIdx .. "_qtd"] = tostring(novaQtd);
        sheet._updatingInv = false;
        recalcularPesoInventario(true);

        local pesoMsg = (pesoUn > 0) and (" | -" .. fmtPesoNum(pesoUn) .. " kg") or "";
        local restoMsg = (novaQtd == 0) and " [ESGOTADO!]" or (" [Restam: " .. tostring(novaQtd) .. "]");
        enviarChatOuMsg("[" .. nomeChar .. "] Usou consumivel: " .. nome .. " (-1" .. pesoMsg .. ")" .. restoMsg .. det);

        -- Rolagem automatica para consumiveis com efeito numerico (v2.2)
        local nmLow = nome:lower();
        local mesa = Firecast.getMesaDe(sheet);
        if nmLow:find("cataplasma") then
            local function aplicarCuraCataplasma(r)
                local cura = math.max(1, math.floor(tonumber(r) or 1));
                local pvMax = math.max(1, math.floor(num(sheet.pvMax, 1)));
                local pvAnt = math.floor(num(sheet.pvAtual, pvMax));
                local pvNovo = math.min(pvMax, pvAnt + cura);
                sheet.pvAtual = tostring(pvNovo);
                recalcularFicha();
                enviarChatOuMsg("[" .. nomeChar .. "] Cataplasma de Ervas curou +" .. tostring(cura) .. " PV! (PV: " .. tostring(pvAnt) .. " -> " .. tostring(pvNovo) .. "/" .. tostring(pvMax) .. ")");
            end;
            if mesa ~= nil and mesa.activeChat ~= nil then
                mesa.activeChat:rolarDados("1d4", "[" .. nomeChar .. "] Cura do Cataplasma de Ervas (+1d4 PV)", function(rolado)
                    aplicarCuraCataplasma(rolado.resultado);
                end);
            else
                aplicarCuraCataplasma(math.random(1, 4));
            end;
        elseif nmLow:find("acido") then
            local gDist = grauEfetivo(sheet.per_armas_dist_grau, sheet.nivel);
            local atkMod = getMod("destreza") + gDist + num(sheet.per_armas_dist_outros, 0);
            local exprAtk = (atkMod >= 0) and ("1d20+" .. tostring(atkMod)) or ("1d20" .. tostring(atkMod));
            if mesa ~= nil and mesa.activeChat ~= nil then
                mesa.activeChat:rolarDados(exprAtk, "[" .. nomeChar .. "] Arremesso de Acido Comum (6m — vs Defesa Esquiva SEM armadura comum)", function()
                    mesa.activeChat:rolarDados("2d6", "[" .. nomeChar .. "] Dano Acido — Frasco de Acido Comum (2d6)");
                end);
            else
                local rAtk = math.random(1, 20) + atkMod;
                local rDmg = math.random(1, 6) + math.random(1, 6);
                showMessage("Frasco de Acido Comum (offline):\nAtaque (vs Def Esquiva sem armadura): " .. tostring(rAtk) .. "\nDano Acido (2d6): " .. tostring(rDmg));
            end;
        elseif nmLow:find("oleo incendiario") or nmLow:find("alcatrao") then
            local gDist = grauEfetivo(sheet.per_armas_dist_grau, sheet.nivel);
            local atkMod = getMod("destreza") + gDist + num(sheet.per_armas_dist_outros, 0);
            local exprAtk = (atkMod >= 0) and ("1d20+" .. tostring(atkMod)) or ("1d20" .. tostring(atkMod));
            if mesa ~= nil and mesa.activeChat ~= nil then
                mesa.activeChat:rolarDados(exprAtk, "[" .. nomeChar .. "] Arremesso de Oleo Incendiario (6m)", function()
                    mesa.activeChat:rolarDados("1d6", "[" .. nomeChar .. "] Dano de Fogo Imediato — Oleo Incendiario (1d6 + 1d4/rodada por 2 rodadas)");
                end);
            else
                local rAtk = math.random(1, 20) + atkMod;
                local rDmg = math.random(1, 6);
                showMessage("Oleo Incendiario (offline):\nAtaque (6m): " .. tostring(rAtk) .. "\nDano Fogo Imediato (1d6): " .. tostring(rDmg) .. " (+1d4/rodada por 2 rodadas)");
            end;
        elseif nmLow:find("calafetagem") then
            if mesa ~= nil and mesa.activeChat ~= nil then
                mesa.activeChat:rolarDados("2d6", "[" .. nomeChar .. "] Reparo de Casco — Kit de Calafetagem (2d6 integridade em 1h)");
            else
                showMessage("Kit de Calafetagem (offline): Reparou " .. tostring(math.random(1, 6) + math.random(1, 6)) .. " pontos de casco.");
            end;
        end;
    else
        local tipoLbl = (tipo == "arma" and "arma") or (tipo == "armadura" and "armadura/escudo") or "equipamento";
        enviarChatOuMsg("[" .. nomeChar .. "] Utilizou " .. tipoLbl .. ": " .. nome .. " (x" .. tostring(math.max(1, qtd)) .. ")" .. det);
    end;
end;

local function ajustarQtdSlotInventario(slotIdx, delta)
    if sheet == nil then return; end;
    local node = getInvSlotNode(slotIdx);
    local nome = tostring((node ~= nil and node.nome) or sheet["inv" .. slotIdx .. "_nome"] or ""):gsub("^%s+", ""):gsub("%s+$", "");
    if nome == "" then
        showMessage("Preencha o nome do item neste slot antes de ajustar a quantidade.");
        return;
    end;
    local qtd = math.max(0, math.floor(num((node ~= nil and node.qtd) or sheet["inv" .. slotIdx .. "_qtd"], 0)));
    local novaQtd = math.max(0, qtd + delta);
    if node ~= nil then node.qtd = tostring(novaQtd); end;
    sheet._updatingInv = true;
    sheet["inv" .. slotIdx .. "_qtd"] = tostring(novaQtd);
    sheet._updatingInv = false;
    recalcularPesoInventario(true);
end;

local function limparSlotInventario(slotIdx)
    if sheet == nil then return; end;
    local node = getInvSlotNode(slotIdx);
    local nome = tostring((node ~= nil and node.nome) or sheet["inv" .. slotIdx .. "_nome"] or ""):gsub("^%s+", ""):gsub("%s+$", "");
    local function executarLimpeza()
        if node ~= nil then
            node.nome = "";
            node.tipo = "equip";
            node.qtd = "";
            node.peso = "";
            node.nota = "";
        end;
        sheet._updatingInv = true;
        sheet["inv" .. slotIdx .. "_nome"] = "";
        sheet["inv" .. slotIdx .. "_tipo"] = "equip";
        sheet["inv" .. slotIdx .. "_qtd"] = "";
        sheet["inv" .. slotIdx .. "_peso"] = "";
        sheet["inv" .. slotIdx .. "_nota"] = "";
        sheet._updatingInv = false;
        recalcularPesoInventario(true);
    end;
    if nome ~= "" and DialogsMod ~= nil and type(DialogsMod.confirmYesNo) == "function" then
        DialogsMod.confirmYesNo(
            "Remover '" .. nome .. "' deste slot do inventario?",
            function(sim) if sim then executarLimpeza(); end; end
        );
    else
        executarLimpeza();
    end;
end;

-- =========================================================================
-- CATALOGO DOS 44 TALENTOS & SLOTS DE TALENTOS DO PERSONAGEM (v2.2)
-- =========================================================================
local function getTalentoSlotNodeByGlobal(globalIdx)
    if sheet == nil then return nil; end;
    if sheet.talentosSlots == nil then sheet.talentosSlots = {}; end;
    local key = "t" .. tostring(globalIdx);
    if sheet.talentosSlots[key] == nil then
        sheet.talentosSlots[key] = {};
    end;
    return sheet.talentosSlots[key];
end;

local function getTalentoSlotNode(slotIdx)
    if sheet == nil then return nil, 1; end;
    local pagina = math.max(1, math.floor(num(sheet.talentosPage, 1)));
    local globalIdx = (pagina - 1) * 6 + slotIdx;
    return getTalentoSlotNodeByGlobal(globalIdx), globalIdx;
end;

atualizarPaginaTalentos = function()
    if sheet == nil or sheet._updatingTal then return; end;
    sheet._updatingTal = true;
    local pagina = math.max(1, math.floor(num(sheet.talentosPage, 1)));
    local inicio = (pagina - 1) * 6 + 1;
    local fim = pagina * 6;
    sheet.talentosPageLabel = "Pag. " .. tostring(pagina) .. " (" .. tostring(inicio) .. "-" .. tostring(fim) .. ")";
    for i = 1, 6 do
        local node = getTalentoSlotNode(i);
        sheet["tal" .. i .. "_nome"] = (node ~= nil and node.nome) or "";
        sheet["tal" .. i .. "_prereq"] = (node ~= nil and node.prereq) or "";
        sheet["tal" .. i .. "_efeito"] = (node ~= nil and node.efeito) or "";
    end;
    sheet._updatingTal = false;
end;

local function salvarTalentoSlot(slotIdx)
    if sheet == nil or sheet._updatingTal then return; end;
    local node = getTalentoSlotNode(slotIdx);
    if node == nil then return; end;
    node.nome = tostring(sheet["tal" .. slotIdx .. "_nome"] or "");
    node.prereq = tostring(sheet["tal" .. slotIdx .. "_prereq"] or "");
    node.efeito = tostring(sheet["tal" .. slotIdx .. "_efeito"] or "");
end;

local function mudarPaginaTalentos(delta)
    if sheet == nil then return; end;
    local pag = math.max(1, math.floor(num(sheet.talentosPage, 1)) + delta);
    sheet.talentosPage = tostring(pag);
    atualizarPaginaTalentos();
end;

local function getTalentoAtual()
    if sheet == nil then return nil, nil; end;
    local catId = tostring(sheet.talentoCat or "marciais");
    local lista = TALENTOS_ITENS[catId];
    if lista == nil or #lista == 0 then
        catId = "marciais";
        lista = TALENTOS_ITENS[catId];
    end;
    if lista == nil or #lista == 0 then return catId, nil; end;
    local tid = tostring(sheet.talentoItem or "");
    for i = 1, #lista do
        if lista[i].id == tid then return catId, lista[i]; end;
    end;
    return catId, lista[1];
end;

local function atualizarPreviewTalento()
    if sheet == nil then return; end;
    local _, t = getTalentoAtual();
    if t == nil then
        sheet.talentoPreview = "Selecione uma categoria e um dos 44 Talentos oficiais de Alenia.";
        return;
    end;
    local ef = tostring(t.efeito or "");
    if #ef > 145 then ef = string.sub(ef, 1, 142) .. "..."; end;
    sheet.talentoPreview = "Pre-req: " .. tostring(t.prereq or "-") .. "  |  Efeito: " .. ef;
end;

local function atualizarItensTalentos(frm, forcar)
    if frm ~= nil then _formRef = frm; end;
    local ref = frm or _formRef or self;
    if sheet == nil then return; end;
    local catId = tostring(sheet.talentoCat or "marciais");
    local lista = TALENTOS_ITENS[catId];
    if lista == nil or #lista == 0 then
        catId = "marciais";
        sheet.talentoCat = catId;
        lista = TALENTOS_ITENS[catId];
    end;
    if lista == nil or #lista == 0 then return; end;

    if (not forcar) and (_ultimaCatTalento == catId) then
        atualizarPreviewTalento();
        return;
    end;
    _ultimaCatTalento = catId;

    local labels = {};
    local vals = {};
    local curId = tostring(sheet.talentoItem or "");
    local found = false;
    for i = 1, #lista do
        table.insert(labels, lista[i].label);
        table.insert(vals, lista[i].id);
        if lista[i].id == curId then found = true; end;
    end;
    if not found then
        curId = lista[1].id;
        sheet.talentoItem = curId;
    end;
    if ref ~= nil and ref.cmbTalentoItem ~= nil then
        pcall(function()
            ref.cmbTalentoItem.items = labels;
            ref.cmbTalentoItem.values = vals;
            ref.cmbTalentoItem.value = curId;
        end);
    end;
    atualizarPreviewTalento();
end;

local function verDetalhesTalento()
    if sheet == nil then return; end;
    local catId, t = getTalentoAtual();
    if t == nil then
        showMessage("Selecione um Talento primeiro.");
        return;
    end;
    local catNome = TALENTOS_CATS[catId] or catId;
    showMessage(
        "CATALOGO DE TALENTOS — ALENIA RPG\n\n" ..
        "Categoria: " .. catNome .. "\n" ..
        "Talento: " .. t.nome .. "\n" ..
        "Pre-requisitos: " .. tostring(t.prereq or "Nenhum") .. "\n\n" ..
        "Efeito em Jogo:\n" .. tostring(t.efeito or "")
    );
end;

local function adicionarTalentoSelecionado()
    if sheet == nil then return; end;
    local _, t = getTalentoAtual();
    if t == nil then
        showMessage("Selecione um Talento valido antes de adicionar.");
        return;
    end;
    if sheet.talentosSlots == nil then sheet.talentosSlots = {}; end;
    local filhos = NDB.getChildNodes(sheet.talentosSlots);
    local maxScan = math.max(24, #filhos + 12);
    local alvoLow = t.nome:lower();
    local primeiroVazio = nil;
    for idx = 1, maxScan do
        local nd = sheet.talentosSlots["t" .. tostring(idx)];
        local nm = (nd ~= nil and tostring(nd.nome or ""):gsub("^%s+", ""):gsub("%s+$", "")) or "";
        if nm == "" then
            if primeiroVazio == nil then primeiroVazio = idx; end;
        elseif nm:lower() == alvoLow then
            showMessage("Voce ja possui o Talento '" .. t.nome .. "' na ficha (regra anti-acumulo de Talentos).");
            return;
        end;
    end;
    local destIdx = primeiroVazio or (maxScan + 1);
    local nd = getTalentoSlotNodeByGlobal(destIdx);
    nd.nome = t.nome;
    nd.prereq = t.prereq or "";
    nd.efeito = t.efeito or "";
    local pag = math.floor((destIdx - 1) / 6) + 1;
    sheet.talentosPage = tostring(pag);
    atualizarPaginaTalentos();
    local nomeChar = sheet.nome or "Explorador";
    enviarChatOuMsg("[" .. nomeChar .. "] Adquiriu o Talento: " .. t.nome .. " (" .. tostring(t.prereq or "-") .. ") — " .. tostring(t.efeito or ""));
end;

local function anunciarTalentoSlot(slotIdx)
    if sheet == nil then return; end;
    local node = getTalentoSlotNode(slotIdx);
    local nome = tostring((node ~= nil and node.nome) or sheet["tal" .. slotIdx .. "_nome"] or ""):gsub("^%s+", ""):gsub("%s+$", "");
    if nome == "" then
        showMessage("Este slot de Talento esta vazio. Escolha um dos 44 Talentos acima ou digite manualmente.");
        return;
    end;
    local efeito = tostring((node ~= nil and node.efeito) or sheet["tal" .. slotIdx .. "_efeito"] or "");
    local nomeChar = sheet.nome or "Explorador";
    enviarChatOuMsg("[TALENTO — " .. nomeChar .. "] Ativou **" .. nome .. "**: " .. efeito);
end;

local function limparTalentoSlot(slotIdx)
    if sheet == nil then return; end;
    local node = getTalentoSlotNode(slotIdx);
    local nome = tostring((node ~= nil and node.nome) or sheet["tal" .. slotIdx .. "_nome"] or ""):gsub("^%s+", ""):gsub("%s+$", "");
    local function limpar()
        if node ~= nil then
            node.nome = "";
            node.prereq = "";
            node.efeito = "";
        end;
        sheet._updatingTal = true;
        sheet["tal" .. slotIdx .. "_nome"] = "";
        sheet["tal" .. slotIdx .. "_prereq"] = "";
        sheet["tal" .. slotIdx .. "_efeito"] = "";
        sheet._updatingTal = false;
    end;
    if nome ~= "" and DialogsMod ~= nil and type(DialogsMod.confirmYesNo) == "function" then
        DialogsMod.confirmYesNo("Remover o Talento '" .. nome .. "' deste slot?", function(sim) if sim then limpar(); end; end);
    else
        limpar();
    end;
end;

local function getItemEmporioAtual()
    if sheet == nil then return nil, nil; end;
    local catId = tostring(sheet.emporioCat or "pacotes");
    local lista = EMPORIO_ITENS[catId];
    if lista == nil or #lista == 0 then
        catId = "pacotes";
        lista = EMPORIO_ITENS[catId];
    end;
    if lista == nil or #lista == 0 then return catId, nil; end;
    local itemId = tostring(sheet.emporioItem or "");
    for i = 1, #lista do
        if lista[i].id == itemId then
            return catId, lista[i];
        end;
    end;
    return catId, lista[1];
end;

local function atualizarPreviewEmporio()
    if sheet == nil then return; end;
    local _, it = getItemEmporioAtual();
    if it == nil then
        sheet.emporioPreview = "Selecione uma categoria e um item do Emporio.";
        return;
    end;
    local qtd = math.max(1, math.min(99, math.floor(num(sheet.emporioQtd, 1))));
    local totalPc = it.precoPc * qtd;
    local pesoTotal = it.pesoKg * qtd;
    local pesoTxt = (pesoTotal > 0) and (string.format("%.1f kg", pesoTotal)) or "0 kg (carrega proprio peso)";
    local tipoTxt = (it.tipo == "cons") and ("Consumivel (" .. tostring(it.usos * qtd) .. " usos)")
        or ((it.pacoteItens ~= nil and #it.pacoteItens > 0) and ("Desempacota " .. tostring(#it.pacoteItens) .. " slots"))
        or ((it.tipo == "arma") and "Arma")
        or ((it.tipo == "armadura") and "Armadura/Escudo")
        or "Equipamento";
    local resumoSpec = tostring(it.spec or "");
    if #resumoSpec > 105 then
        resumoSpec = string.sub(resumoSpec, 1, 102) .. "...";
    end;
    sheet.emporioPreview = "Total (" .. tostring(qtd) .. "x): " .. formatarPrecoPc(totalPc) .. "  |  Peso: " .. pesoTxt .. "  |  " .. tipoTxt .. "  |  " .. resumoSpec;
end;

local function atualizarItensEmporio(frm, forcar)
    if frm ~= nil then _formRef = frm; end;
    local ref = frm or _formRef or self;
    if sheet == nil then return; end;
    local catId = tostring(sheet.emporioCat or "pacotes");
    local lista = EMPORIO_ITENS[catId];
    if lista == nil or #lista == 0 then
        catId = "pacotes";
        sheet.emporioCat = catId;
        lista = EMPORIO_ITENS[catId];
    end;
    if lista == nil or #lista == 0 then return; end;

    if (not forcar) and (_ultimaCatEmporio == catId) then
        atualizarPreviewEmporio();
        return;
    end;
    _ultimaCatEmporio = catId;

    local labels = {};
    local vals = {};
    local curId = tostring(sheet.emporioItem or "");
    local found = false;
    for i = 1, #lista do
        table.insert(labels, lista[i].label);
        table.insert(vals, lista[i].id);
        if lista[i].id == curId then found = true; end;
    end;
    if not found then
        curId = lista[1].id;
        sheet.emporioItem = curId;
    end;

    if ref ~= nil and ref.cmbEmporioItem ~= nil then
        pcall(function()
            ref.cmbEmporioItem.items = labels;
            ref.cmbEmporioItem.values = vals;
            ref.cmbEmporioItem.value = curId;
        end);
    end;
    atualizarPreviewEmporio();
end;

local function verDetalhesEmporio()
    if sheet == nil then return; end;
    local catId, it = getItemEmporioAtual();
    if it == nil then
        showMessage("Selecione um item do Emporio primeiro.");
        return;
    end;
    local qtd = math.max(1, math.min(99, math.floor(num(sheet.emporioQtd, 1))));
    local totalPc = it.precoPc * qtd;
    local pesoUnit = (it.pesoKg > 0) and string.format("%.1f kg", it.pesoKg) or "0 kg (carrega proprio peso)";
    local pesoTot = (it.pesoKg > 0) and string.format("%.1f kg", it.pesoKg * qtd) or "0 kg";
    local catNome = EMPORIO_CATS[catId] or catId;
    local tipoInfo = (it.tipo == "cons")
        and ("Consumivel Utilizavel — concede " .. tostring(it.usos * qtd) .. " uso(s) no slot (" .. fmtPesoNum(it.pesoUn) .. " kg por uso)")
        or ((it.pacoteItens ~= nil and #it.pacoteItens > 0) and ("Pacote Completo — desempacota automaticamente " .. tostring(#it.pacoteItens) .. " itens nos Slots de Inventario (ja com consumiveis prontos para usar!)"))
        or "Equipamento Permanente (guardado em Slot de Inventario)";
    showMessage(
        "EMPORIO DE ALENIA — DETALHES DO ITEM\n\n" ..
        "Categoria: " .. catNome .. "\n" ..
        "Item: " .. it.nome .. "\n" ..
        "Tipo: " .. tipoInfo .. "\n" ..
        "Preco Unitario: " .. formatarPrecoPc(it.precoPc) .. "  |  Total (" .. tostring(qtd) .. "x): " .. formatarPrecoPc(totalPc) .. "\n" ..
        "Peso Unitario: " .. pesoUnit .. "  |  Peso Total: " .. pesoTot .. "\n\n" ..
        "Especificacoes:\n" .. tostring(it.spec or "")
    );
end;

local function comprarItemEmporio()
    if sheet == nil then return; end;
    local _, it = getItemEmporioAtual();
    if it == nil then
        showMessage("Selecione um item valido do Emporio antes de comprar.");
        return;
    end;

    local qtd = math.max(1, math.min(99, math.floor(num(sheet.emporioQtd, 1))));
    sheet.emporioQtd = tostring(qtd);

    local totalPc = it.precoPc * qtd;
    local pesoAdd = it.pesoKg * qtd;

    local po = math.max(0, math.floor(num(sheet.moedasOuro, 0)));
    local pp = math.max(0, math.floor(num(sheet.moedasPrata, 0)));
    local pc = math.max(0, math.floor(num(sheet.moedasCobre, 0)));
    local bolsaPc = (po * 100) + (pp * 10) + pc;
    local cartasPp = math.max(0, math.floor(num(sheet.cartasCredito, 0)));
    local usarBanco = (sheet.emporioUsarBanco == true);
    local bancoPc = usarBanco and (cartasPp * 10) or 0;

    if (bolsaPc + bancoPc) < totalPc then
        local dicaBanco = "";
        if (not usarBanco) and (cartasPp * 10 + bolsaPc >= totalPc) then
            dicaBanco = "\n\nDica: Voce possui " .. tostring(cartasPp) .. " PP em Cartas de Credito. Marque 'Usar Cartas de Credito' se quiser pagar com saldo bancario.";
        end;
        showMessage(
            "Dinheiro insuficiente para comprar " .. tostring(qtd) .. "x " .. it.nome .. "!\n\n" ..
            "Custo Total: " .. formatarPrecoPc(totalPc) .. "\n" ..
            "Disponivel na Bolsa: " .. formatarPrecoPc(bolsaPc) ..
            (usarBanco and ("\nDisponivel no Banco: " .. tostring(cartasPp) .. " PP") or "") ..
            dicaBanco
        );
        return;
    end;

    local fonteTxt = "Bolsa Fisica";
    local sacarBancoPp = 0;
    if bolsaPc < totalPc then
        local faltaPc = totalPc - bolsaPc;
        sacarBancoPp = math.ceil(faltaPc / 10.0);
        fonteTxt = "Bolsa + " .. tostring(sacarBancoPp) .. " PP em Cartas de Credito";
    end;

    local isPacote = (it.pacoteItens ~= nil and #it.pacoteItens > 0);
    local destResumo = isPacote
        and ("Slots de Inventario (desempacota " .. tostring(#it.pacoteItens) .. " itens automaticamente)")
        or ((it.tipo == "cons") and ("Slot Consumivel (" .. tostring(it.usos * qtd) .. " usos — botao [Usar])") or "Slot de Inventario");

    local function executarCompra()
        local poNow = math.max(0, math.floor(num(sheet.moedasOuro, 0)));
        local ppNow = math.max(0, math.floor(num(sheet.moedasPrata, 0)));
        local pcNow = math.max(0, math.floor(num(sheet.moedasCobre, 0)));
        local bolsaNow = (poNow * 100) + (ppNow * 10) + pcNow;
        local bancoNowPp = math.max(0, math.floor(num(sheet.cartasCredito, 0)));
        local usarB = (sheet.emporioUsarBanco == true);
        local extraBancoPp = 0;

        if bolsaNow >= totalPc then
            local novoTotal = bolsaNow - totalPc;
            local ouroMantido = math.min(poNow, math.floor(novoTotal / 100));
            local resto = novoTotal - (ouroMantido * 100);
            poNow = ouroMantido;
            ppNow = math.floor(resto / 10);
            pcNow = resto % 10;
        elseif usarB and (bolsaNow + bancoNowPp * 10 >= totalPc) then
            local faltaPc = totalPc - bolsaNow;
            extraBancoPp = math.ceil(faltaPc / 10.0);
            local trocoPc = (extraBancoPp * 10) - faltaPc;
            bancoNowPp = bancoNowPp - extraBancoPp;
            poNow = 0;
            ppNow = math.floor(trocoPc / 10);
            pcNow = trocoPc % 10;
        else
            showMessage("Saldo alterado: dinheiro insuficiente para concluir a compra.");
            return;
        end;

        sheet.moedasOuro = tostring(poNow);
        sheet.moedasPrata = tostring(ppNow);
        sheet.moedasCobre = tostring(pcNow);
        if extraBancoPp > 0 then
            sheet.cartasCredito = tostring(bancoNowPp);
        end;

        local pagAlvo = math.max(1, math.floor(num(sheet.invPage, 1)));
        local detalheAdicao = "";
        if isPacote then
            local primeiroPag = nil;
            for p = 1, #it.pacoteItens do
                local comp = it.pacoteItens[p];
                local subIt = EMPORIO_BY_ID[comp.id];
                if subIt ~= nil then
                    local totalUsos = (subIt.usos or 1) * (comp.qtd or 1) * qtd;
                    local _, pagSlot = adicionarOuEmpilharNoInventario(subIt.slotNome or subIt.nome, subIt.tipo or "equip", totalUsos, subIt.pesoUn or subIt.pesoKg or 0, subIt.efeito or subIt.spec or "");
                    if primeiroPag == nil then primeiroPag = pagSlot; end;
                end;
            end;
            if primeiroPag ~= nil then pagAlvo = primeiroPag; end;
            detalheAdicao = " (" .. tostring(#it.pacoteItens) .. " itens desempacotados nos Slots)";
        else
            local totalUsos = (it.usos or 1) * qtd;
            local _, pagSlot, empilhou = adicionarOuEmpilharNoInventario(it.slotNome or it.nome, it.tipo or "equip", totalUsos, it.pesoUn or it.pesoKg or 0, it.efeito or it.spec or "");
            pagAlvo = pagSlot;
            if it.tipo == "cons" then
                detalheAdicao = " (+" .. tostring(totalUsos) .. " usos" .. (empilhou and " empilhados" or "") .. " nos Slots)";
            else
                detalheAdicao = empilhou and " (empilhado nos Slots)" or " (adicionado aos Slots)";
            end;
        end;

        sheet.invPage = tostring(pagAlvo);
        atualizarPaginaInventario();
        recalcularPesoInventario(true);
        recalcularFicha();
        atualizarPreviewEmporio();

        local nomeChar = sheet.nome or "Explorador";
        local bancoMsg = (extraBancoPp > 0) and (" | Banco: -" .. tostring(extraBancoPp) .. " PP") or "";
        local pesoMsg = (pesoAdd > 0) and (" | +" .. string.format("%.1f kg", pesoAdd) .. " (Carga: " .. tostring(sheet.cargaAtual) .. " kg)") or "";
        enviarChatOuMsg(
            "[" .. nomeChar .. "] Comprou no Emporio: " .. tostring(qtd) .. "x " .. it.nome ..
            " (-" .. formatarPrecoPc(totalPc) .. bancoMsg .. ")" .. pesoMsg ..
            detalheAdicao .. " | Bolsa: " .. tostring(poNow) .. " PO, " .. tostring(ppNow) .. " PP, " .. tostring(pcNow) .. " PC."
        );
    end;

    if DialogsMod ~= nil and type(DialogsMod.confirmYesNo) == "function" then
        DialogsMod.confirmYesNo(
            "Confirmar compra no Emporio de Alenia?\n\n" ..
            "Item: " .. tostring(qtd) .. "x " .. it.nome .. "\n" ..
            "Custo Total: " .. formatarPrecoPc(totalPc) .. " (" .. fonteTxt .. ")\n" ..
            "Peso Adicionado: " .. ((pesoAdd > 0) and string.format("+%.1f kg", pesoAdd) or "0 kg") .. "\n" ..
            "Destino: " .. destResumo,
            function(sim)
                if sim then executarCompra(); end;
            end
        );
    else
        executarCompra();
    end;
end;

local function compararVersoes(vA, vB)
    local function splitNums(s)
        local t = {};
        for n in tostring(s or "0"):gmatch("%d+") do
            table.insert(t, tonumber(n) or 0);
        end;
        return t;
    end;
    local a = splitNums(vA);
    local b = splitNums(vB);
    local maxLen = math.max(#a, #b);
    for i = 1, maxLen do
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
                local item = lista[i];
                if item ~= nil and item.moduleId == PLUGIN_MODULE_ID and item.version ~= nil and tostring(item.version) ~= "" then
                    ver = tostring(item.version);
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
        showMessage("Nao foi possivel acessar a internet pelo Firecast.\nBaixe a versao mais recente na Biblioteca Online:\n" .. BIBLIOTECA_URL);
        return;
    end;

    sheet.statusAtualizacao = "Verificando atualizacoes oficiais...";
    local urlCheck = PLUGIN_RPK_URL .. "?t=" .. tostring(os.time());

    InternetMod.download(
        urlCheck,
        function(stream, contentType)
            if stream == nil then
                sheet.statusAtualizacao = "Falha: resposta vazia do servidor de atualizacoes.";
                showMessage("Nao foi possivel ler o pacote de atualizacao.");
                return;
            end;

            local details = nil;
            if PluginsMod ~= nil and type(PluginsMod.getRPKDetails) == "function" then
                local okDet, det = pcall(PluginsMod.getRPKDetails, stream);
                if okDet then details = det; end;
            end;

            if details == nil or details.version == nil then
                sheet.statusAtualizacao = "Pacote remoto invalido ou indisponivel no momento.";
                if DialogsMod ~= nil and type(DialogsMod.confirmYesNo) == "function" then
                    DialogsMod.confirmYesNo(
                        "Nao foi possivel inspecionar o pacote de atualizacao agora.\nDeseja abrir a Biblioteca Online de Alenia no navegador?",
                        function(sim)
                            if sim then abrirLinkExterno(BIBLIOTECA_URL); end;
                        end
                    );
                else
                    showMessage("Nao foi possivel inspecionar o pacote remoto. Acesse:\n" .. BIBLIOTECA_URL);
                end;
                return;
            end;

            local verRemota = tostring(details.version);
            local cmp = compararVersoes(verRemota, verLocal);

            local function instalarAgora()
                if PluginsMod == nil or type(PluginsMod.installPlugin) ~= "function" then
                    sheet.statusAtualizacao = "Instalacao automatica indisponivel; abrindo Biblioteca Online...";
                    abrirLinkExterno(BIBLIOTECA_URL);
                    return;
                end;
                pcall(function() stream.position = 0; end);
                local okCall, okInst, errMsg = pcall(PluginsMod.installPlugin, stream, not forcarReinstalacao);
                if okCall and okInst then
                    sheet.pluginVersaoAtual = "v" .. verRemota .. " (reabra)";
                    sheet.statusAtualizacao = "Atualizado com sucesso para v" .. verRemota .. "! Feche e reabra a ficha para aplicar.";
                    showMessage("Ficha Alenia RPG atualizada automaticamente para a versao v" .. verRemota .. "!\n\nFeche e reabra a janela da ficha para carregar todas as novidades.");
                else
                    local detalhe = tostring(errMsg or okInst or "erro desconhecido");
                    sheet.statusAtualizacao = "Falha ao instalar automaticamente (" .. detalhe .. ").";
                    if DialogsMod ~= nil and type(DialogsMod.confirmYesNo) == "function" then
                        DialogsMod.confirmYesNo(
                            "Nao foi possivel instalar automaticamente (" .. detalhe .. ").\nDeseja abrir a Biblioteca Online para baixar o plugin?",
                            function(sim)
                                if sim then abrirLinkExterno(BIBLIOTECA_URL); end;
                            end
                        );
                    else
                        showMessage("Falha ao instalar (" .. detalhe .. "). Baixe pela Biblioteca Online:\n" .. BIBLIOTECA_URL);
                    end;
                end;
            end;

            if cmp > 0 then
                sheet.statusAtualizacao = "Nova versao encontrada: v" .. verRemota .. " (atual: v" .. verLocal .. ").";
                if DialogsMod ~= nil and type(DialogsMod.confirmYesNo) == "function" then
                    DialogsMod.confirmYesNo(
                        "Nova versao da ficha Alenia RPG disponivel!\n\nVersao instalada: v" .. verLocal .. "\nNova versao disponivel: v" .. verRemota .. "\n\nDeseja baixar e atualizar a ficha automaticamente agora mesmo?",
                        function(sim)
                            if sim then
                                instalarAgora();
                            else
                                sheet.statusAtualizacao = "Atualizacao v" .. verRemota .. " disponivel (cancelada pelo usuario).";
                            end;
                        end
                    );
                else
                    instalarAgora();
                end;
            elseif forcarReinstalacao then
                sheet.statusAtualizacao = "Reinstalando v" .. verRemota .. "...";
                instalarAgora();
            else
                sheet.statusAtualizacao = "Sua ficha ja esta atualizada na versao mais recente (v" .. verLocal .. ").";
                showMessage("Tudo certo! Sua ficha Alenia RPG ja esta na versao mais recente (v" .. verLocal .. ").");
            end;
        end,
        function(errorMsg)
            sheet.statusAtualizacao = "Erro de conexao ao verificar atualizacoes: " .. tostring(errorMsg);
            showMessage("Nao foi possivel conectar ao servidor para verificar atualizacoes.\nDetalhe: " .. tostring(errorMsg));
        end,
        function(downloadedBytes, totalBytes)
            if totalBytes ~= nil and totalBytes > 0 then
                local pct = math.min(100, math.floor((downloadedBytes / totalBytes) * 100));
                sheet.statusAtualizacao = "Baixando pacote de atualizacao... (" .. tostring(pct) .. "%)";
            else
                sheet.statusAtualizacao = "Baixando pacote de atualizacao...";
            end;
        end
    );
end;
"""
    )
    return lua


def lua_items_str(lst):
    return "{" + ", ".join("'" + s.replace("'", "\\'") + "'" for s in lst) + "}"


def xml_attr(val: str) -> str:
    return sax.escape(val, {'"': "&quot;"})


def build_lfm() -> str:
    emporio_cats, emporio_items = load_emporio_catalog()
    emporio_cat_items = lua_items_str([c[1] for c in emporio_cats])
    emporio_cat_values = lua_items_str([c[0] for c in emporio_cats])
    init_pack_list = emporio_items["pacotes"]
    emporio_init_items = lua_items_str([
        f"{it['nome']}  [{_fmt_price_label(it['precoPc'])} | {it['pesoKg']:.1f} kg]" if it["pesoKg"] > 0
        else f"{it['nome']}  [{_fmt_price_label(it['precoPc'])}]"
        for it in init_pack_list
    ])
    emporio_init_values = lua_items_str([it["id"] for it in init_pack_list])
    init_item_id = init_pack_list[0]["id"] if init_pack_list else ""

    talentos_cats, talentos_items = load_talentos_catalog()
    talento_cat_items = lua_items_str([c[1] for c in talentos_cats])
    talento_cat_values = lua_items_str([c[0] for c in talentos_cats])
    init_tal_list = talentos_items["marciais"]
    talento_init_items = lua_items_str([f"{t['nome']}  [{t['prereq']}]" for t in init_tal_list])
    talento_init_values = lua_items_str([t["id"] for t in init_tal_list])
    init_talento_id = init_tal_list[0]["id"] if init_tal_list else ""

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
        ty = 84 + row * 42
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

    inv_tipo_items = "{'Consumivel', 'Equipamento', 'Arma', 'Armadura'}"
    inv_tipo_values = "{'cons', 'equip', 'arma', 'armadura'}"
    inv_rows = []
    for i in range(1, 11):
        ty = 82 + (i - 1) * 41
        inv_rows.append(f'''
            <rectangle left="10" top="{ty}" width="1016" height="37" color="{BG_CARD_ALT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="3" yradius="3">
                <edit left="6" top="4" width="254" height="29" field="inv{i}_nome" textPrompt="Slot {i} (compre no Emporio ou digite)..." fontColor="{TEXT_MAIN}" fontSize="13"/>
                <comboBox left="264" top="4" width="102" height="29" field="inv{i}_tipo" items="{xml_attr(inv_tipo_items)}" values="{xml_attr(inv_tipo_values)}" fontSize="12"/>
                <edit left="370" top="4" width="54" height="29" field="inv{i}_qtd" type="number" horzTextAlign="center" fontColor="{TEXT_GOLD}" fontSize="14" fontStyle="bold"/>
                <edit left="428" top="4" width="54" height="29" field="inv{i}_peso" horzTextAlign="center" fontColor="{TEXT_MAIN}" fontSize="13"/>
                <edit left="486" top="4" width="370" height="29" field="inv{i}_nota" textPrompt="Efeito / notas (enviado ao chat ao usar)..." fontColor="{TEXT_MUTED}" fontSize="12"/>
                <button left="860" top="4" width="66" height="29" text="Usar" fontSize="12">
                    <event name="onClick"><![CDATA[usarSlotInventario({i});]]></event>
                </button>
                <button left="930" top="4" width="38" height="29" text="+1" fontSize="12">
                    <event name="onClick"><![CDATA[ajustarQtdSlotInventario({i}, 1);]]></event>
                </button>
                <button left="972" top="4" width="38" height="29" text="X" fontSize="12">
                    <event name="onClick"><![CDATA[limparSlotInventario({i});]]></event>
                </button>
            </rectangle>''')

    talento_rows = []
    for i in range(1, 7):
        ty = 186 + (i - 1) * 41
        talento_rows.append(f'''
            <rectangle left="10" top="{ty}" width="1016" height="37" color="{BG_CARD_ALT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="3" yradius="3">
                <edit left="6" top="4" width="210" height="29" field="tal{i}_nome" textPrompt="Talento {i} (adicione acima ou digite)..." fontColor="{TEXT_GOLD}" fontSize="13" fontStyle="bold"/>
                <edit left="220" top="4" width="186" height="29" field="tal{i}_prereq" textPrompt="Pre-requisitos..." fontColor="{TEXT_MUTED}" fontSize="11"/>
                <edit left="410" top="4" width="474" height="29" field="tal{i}_efeito" textPrompt="Efeito em jogo..." fontColor="{TEXT_MAIN}" fontSize="12"/>
                <button left="888" top="4" width="80" height="29" text="Anunciar" fontSize="12">
                    <event name="onClick"><![CDATA[anunciarTalentoSlot({i});]]></event>
                </button>
                <button left="972" top="4" width="38" height="29" text="X" fontSize="12">
                    <event name="onClick"><![CDATA[limparTalentoSlot({i});]]></event>
                </button>
            </rectangle>''')

    doenca_cat_items = (
        "{'1. Febre das Cisternas (Sede Suja | CON CD 14/dia)', "
        "'2. Tosse de Ferraur (Ocupacional | CON CD 13/sem)', "
        "'3. Tremor das Brumas (Pantanos | CON CD 14/dia)', "
        "'4. Mal do Porao (Mancha do Cais | CON CD 15/dia)', "
        "'5. Cinza da Pele (Cronica | CON CD 12/sem)', "
        "'6. Febre do Coro (Quadro Anomalo | SAB CD 14/sem)', "
        "'7. Outra Doenca / Mal Personalizado (Mestre)'}"
    )
    doenca_cat_values = "{'febre_cisternas', 'tosse_ferraur', 'tremor_brumas', 'mal_porao', 'cinza_pele', 'febre_coro', 'personalizada'}"
    doenca_est_items = "{'0 - Inativo / Curado', '1 - Leve', '2 - Incapacitante', '3 - Critica'}"
    doenca_est_values = "{'0', '1', '2', '3'}"
    doenca_attr_items = "{'CON', 'SAB'}"
    doenca_attr_values = "{'constituicao', 'sabedoria'}"

    doenca_rows = []
    for i in range(1, 4):
        ty = 172 + (i - 1) * 72
        doenca_rows.append(f'''
            <rectangle left="10" top="{ty}" width="1016" height="66" color="{BG_CARD_ALT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                <edit left="6" top="5" width="290" height="28" field="doenca{i}_nome" textPrompt="Slot Doenca {i} (vazio)..." fontColor="{TEXT_CRIMSON}" fontSize="13" fontStyle="bold"/>
                <comboBox left="300" top="5" width="152" height="28" field="doenca{i}_est" items="{xml_attr(doenca_est_items)}" values="{xml_attr(doenca_est_values)}" fontSize="12"/>
                <comboBox left="456" top="5" width="60" height="28" field="doenca{i}_attr" items="{xml_attr(doenca_attr_items)}" values="{xml_attr(doenca_attr_values)}" fontSize="12"/>
                <label left="520" top="5" width="26" height="28" text="CD" fontColor="{TEXT_MUTED}" fontSize="11" fontStyle="bold" horzTextAlign="center" vertTextAlign="center"/>
                <edit left="546" top="5" width="44" height="28" field="doenca{i}_cd" type="number" horzTextAlign="center" fontColor="{TEXT_GOLD}" fontSize="13" fontStyle="bold"/>
                <label left="594" top="5" width="54" height="28" text="Suc(0-2):" fontColor="{TEXT_MUTED}" fontSize="11" horzTextAlign="trailing" vertTextAlign="center"/>
                <edit left="650" top="5" width="38" height="28" field="doenca{i}_suc" type="number" horzTextAlign="center" fontColor="{TEXT_GREEN}" fontSize="13" fontStyle="bold"/>
                <button left="696" top="4" width="180" height="30" text="Testar Resistencia (d20)" fontSize="12">
                    <event name="onClick"><![CDATA[testarDoencaSlot({i});]]></event>
                </button>
                <button left="882" top="4" width="126" height="30" text="Curar / Limpar" fontSize="12">
                    <event name="onClick"><![CDATA[limparDoencaSlot({i});]]></event>
                </button>
                <label left="8" top="37" width="1000" height="24" field="doenca{i}_efeito" fontColor="{TEXT_MUTED}" fontSize="12" vertTextAlign="center"/>
            </rectangle>''')

    recalc_fields = [
        "forca", "destreza", "constituicao", "inteligencia", "sabedoria", "carisma",
        "nivel", "xpAtual", "pvMax", "kitSelecionado", "kitDvFaces", "kitPerBase", "kitMultInt",
        "armaduraDef", "escudoDef", "defesaOutros", "iniciativaOutros",
        "esp_status", "esp_fe", "esp_submundo", "esp_dom", "esp_livre",
        "moedasOuro", "moedasPrata", "moedasCobre", "cartasCredito", "padraoVida",
        "exaustaoNivel", "cuidadoMedico", "cuidadoHerbalista", "cuidadoAlquimista",
        "doenca1_id", "doenca1_nome", "doenca1_est", "doenca2_id", "doenca2_nome", "doenca2_est", "doenca3_id", "doenca3_nome", "doenca3_est"
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
        "customSkillPage", "invPage", "invMaxIdx", "invPageLabel", "invPesoTotal",
        "talentosPage", "talentosPageLabel", "talentoCat", "talentoItem", "talentoPreview", "avisoBonusExt",
        "exaustaoNivel", "exaustaoResumo", "doencaSelecionada", "cuidadosResumo",
        "doenca1_est", "doenca1_attr", "doenca1_cd", "doenca1_suc", "doenca1_efeito",
        "doenca2_est", "doenca2_attr", "doenca2_cd", "doenca2_suc", "doenca2_efeito",
        "doenca3_est", "doenca3_attr", "doenca3_cd", "doenca3_suc", "doenca3_efeito",
        "moedasOuro", "moedasPrata", "moedasCobre",
        "cartasCredito", "bancoOrigem", "padraoVida",
        "emporioCat", "emporioItem", "emporioQtd", "emporioPreview",
        "cdTeste", "defesaAlvo", "xpAtual",
        "pluginVersaoAtual", "statusAtualizacao"
    ]
    def_values = [
        "1", "sem_kit", "00 - Sem Kit (Livre / Media Padrao)", "8",
        "1", "0.75", "18", "18", "0", "0",
        "0", "0", "0", "1",
        "0", "0", "0", "0", "0",
        "1", "1", "30", "Pag. 1 (1-10)", "0.0 kg (0 itens)",
        "1", "Pag. 1 (1-6)", "marciais", init_talento_id, "Selecione uma categoria e um dos 44 Talentos oficiais de Alenia.",
        "Bonus externos (OUT) dentro da regra oficial: apenas maior equipamento aplica | teto combinado +6 (excecao: Rituais +8).",
        "0", "Sem Exaustao (0)", "febre_cisternas", "Bonus Cuidados (3 Oficios): +0 (teto +6)",
        "0", "constituicao", "14", "0", "Slot livre (selecione uma doenca acima e clique em + Contrair).",
        "0", "constituicao", "14", "0", "Slot livre (selecione uma doenca acima e clique em + Contrair).",
        "0", "constituicao", "14", "0", "Slot livre (selecione uma doenca acima e clique em + Contrair).",
        "0", "25", "0",
        "0", "corallis", "modesto",
        "pacotes", init_item_id, "1", "Selecione uma categoria e um item para comprar direto para os Slots de Inventario.",
        "0", "0", "0",
        "v2.3", "Clique no botao acima para checar e instalar atualizacoes automaticamente."
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

    inv_datalinks = []
    for i in range(1, 11):
        ifields = lua_items_str([f"inv{i}_nome", f"inv{i}_tipo", f"inv{i}_qtd", f"inv{i}_peso", f"inv{i}_nota"])
        inv_datalinks.append(f'''
    <dataLink fields="{xml_attr(ifields)}">
        <event name="onChange"><![CDATA[salvarInvSlot({i});]]></event>
    </dataLink>''')

    talentos_datalinks = []
    for i in range(1, 7):
        tfields = lua_items_str([f"tal{i}_nome", f"tal{i}_prereq", f"tal{i}_efeito"])
        talentos_datalinks.append(f'''
    <dataLink fields="{xml_attr(tfields)}">
        <event name="onChange"><![CDATA[salvarTalentoSlot({i});]]></event>
    </dataLink>''')

    lfm = f'''<?xml version="1.0" encoding="UTF-8"?>
<form name="frmAleniaFicha" formType="sheetTemplate" dataType="br.com.alenia.rpg_oficial.ficha" title="Alenia RPG - Ficha Oficial" align="client" theme="dark">
    <script><![CDATA[
{build_lua_script(emporio_cats, emporio_items, talentos_cats, talentos_items)}
    ]]></script>

    <rectangle align="client" color="{BG_MAIN}">
        <!-- CABECALHO FIXO AMPLIADO + BARRA RAPIDA DE CD & DESCANSO -->
        <rectangle align="top" height="148" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="1" margins="{{left=6, right=6, top=6, bottom=4}}" xradius="6" yradius="6">
            <label left="12" top="6" width="260" height="24" text="ALENIA RPG — FICHA v2.3" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold"/>
            <label left="278" top="6" width="170" height="24" field="patamarTexto" fontColor="{TEXT_CRIMSON}" fontSize="14" fontStyle="bold"/>
            <label left="452" top="6" width="320" height="24" field="kitNomeAtual" fontColor="{TEXT_MUTED}" fontSize="14"/>
            <label left="780" top="6" width="250" height="24" text="Golpe Devastador (&gt;2/3 PV):" fontColor="{TEXT_CRIMSON}" fontSize="13" horzTextAlign="trailing"/>

            <label left="12" top="32" width="224" height="18" text="NOME DO PERSONAGEM" fontColor="{TEXT_MUTED}" fontSize="12"/>
            <edit left="12" top="52" width="224" height="40" field="nome" textPrompt="Nome do explorador..." fontColor="{TEXT_MAIN}" fontSize="16" fontStyle="bold"/>

            <label left="244" top="32" width="196" height="18" text="ORIGEM / CIDADE NATAL" fontColor="{TEXT_MUTED}" fontSize="12"/>
            <edit left="244" top="52" width="196" height="40" field="origem" textPrompt="Altavanne, Baldbella, OX..." fontColor="{TEXT_MAIN}" fontSize="15"/>

            <label left="448" top="32" width="64" height="18" text="NIVEL" fontColor="{TEXT_GOLD}" fontSize="12" fontStyle="bold" horzTextAlign="center"/>
            <edit left="448" top="52" width="64" height="40" field="nivel" type="number" fontColor="{TEXT_GOLD}" fontSize="19" fontStyle="bold" horzTextAlign="center"/>

            <label left="520" top="32" width="142" height="18" text="PV (ATUAL / MAX)" fontColor="{TEXT_CRIMSON}" fontSize="12" fontStyle="bold" horzTextAlign="center"/>
            <edit left="520" top="52" width="64" height="40" field="pvAtual" type="number" fontColor="{TEXT_MAIN}" fontSize="18" fontStyle="bold" horzTextAlign="center"/>
            <label left="584" top="52" width="14" height="40" text="/" fontColor="{TEXT_MUTED}" fontSize="18" horzTextAlign="center" vertTextAlign="center"/>
            <edit left="598" top="52" width="64" height="40" field="pvMax" type="number" fontColor="{TEXT_CRIMSON}" fontSize="18" fontStyle="bold" horzTextAlign="center"/>

            <button left="670" top="52" width="110" height="40" text="Receber Dano" fontSize="13">
                <event name="onClick"><![CDATA[receberDano();]]></event>
            </button>

            <rectangle left="788" top="52" width="116" height="40" color="{BG_INPUT}" strokeColor="{BORDER_CRIMSON}" strokeSize="1" xradius="4" yradius="4">
                <label align="client" field="limiarDevastador" fontColor="{TEXT_CRIMSON}" fontSize="14" fontStyle="bold" horzTextAlign="center" vertTextAlign="center"/>
            </rectangle>

            <button left="912" top="52" width="118" height="40" text="Iniciativa" fontSize="14">
                <event name="onClick"><![CDATA[rolarD20("Iniciativa", getMod("destreza") + math.floor(num(sheet.per_percepcao_grau, 0) / 3) + num(sheet.iniciativaOutros, 0), "", 0);]]></event>
            </button>

            <!-- BARRA RAPIDA DE DIFICULDADE (CD) & DESCANSOS -->
            <label left="12" top="104" width="96" height="32" text="CD do Teste:" fontColor="{TEXT_GOLD}" fontSize="13" fontStyle="bold" vertTextAlign="center"/>
            <edit left="110" top="104" width="52" height="32" field="cdTeste" type="number" textPrompt="0" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold" horzTextAlign="center"/>
            <checkBox left="168" top="104" width="164" height="32" field="perguntarCD" text="Perguntar CD ao rolar" fontColor="{TEXT_MAIN}" fontSize="12"/>

            <button left="338" top="106" width="56" height="28" text="Livre" fontSize="11">
                <event name="onClick"><![CDATA[sheet.cdTeste = "0";]]></event>
            </button>
            <button left="398" top="106" width="52" height="28" text="CD 10" fontSize="11">
                <event name="onClick"><![CDATA[sheet.cdTeste = "10";]]></event>
            </button>
            <button left="454" top="106" width="52" height="28" text="CD 15" fontSize="11">
                <event name="onClick"><![CDATA[sheet.cdTeste = "15";]]></event>
            </button>
            <button left="510" top="106" width="52" height="28" text="CD 20" fontSize="11">
                <event name="onClick"><![CDATA[sheet.cdTeste = "20";]]></event>
            </button>
            <button left="566" top="106" width="52" height="28" text="CD 25" fontSize="11">
                <event name="onClick"><![CDATA[sheet.cdTeste = "25";]]></event>
            </button>

            <button left="644" top="105" width="194" height="30" text="Descanso Curto (1dX+CON)" fontSize="12">
                <event name="onClick"><![CDATA[descansoCurto();]]></event>
            </button>
            <button left="844" top="105" width="186" height="30" text="Descanso Longo (+50% PV)" fontSize="12">
                <event name="onClick"><![CDATA[descansoLongo();]]></event>
            </button>
        </rectangle>

        <!-- 5 ABAS PRINCIPAIS -->
        <tabControl align="client" margins="{{left=6, right=6, top=0, bottom=6}}">

            <!-- ABA 1: PRINCIPAL & KIT -->
            <tab title="Principal &amp; Kit">
                <scrollBox align="client">
                    <layout left="0" top="0" width="1056" height="920">
                        <!-- ATRIBUTOS BASE -->
                        <rectangle left="6" top="6" width="1036" height="194" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="6" yradius="6">
                            <label left="12" top="12" width="600" height="26" text="ATRIBUTOS BASE (Teto: 18 Recruta | 20 Lenda | 22 Epico)" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold"/>
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

                        <!-- RETRATO DO EXPLORADOR (CLICAVEL / EDITAVEL) -->
                        <rectangle left="6" top="380" width="214" height="296" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="6" yradius="6">
                            <label left="8" top="8" width="198" height="20" text="RETRATO DO EXPLORADOR" fontColor="{TEXT_GOLD}" fontSize="12" fontStyle="bold" horzTextAlign="center"/>
                            <rectangle left="10" top="32" width="194" height="234" color="{BG_INPUT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                                <label align="client" text="Clique aqui para carregar retrato" fontColor="{TEXT_MUTED}" fontSize="12" horzTextAlign="center" vertTextAlign="center" wordWrap="true"/>
                                <image name="imgRetrato" align="client" field="retratoPersonagem" editable="true" style="proportional" center="true"/>
                            </rectangle>
                            <label left="8" top="270" width="198" height="18" text="Clique na moldura para trocar" fontColor="{TEXT_MUTED}" fontSize="11" horzTextAlign="center"/>
                        </rectangle>

                        <!-- SELETOR & AUTOMACAO DE KITS UNIVERSAIS -->
                        <rectangle left="228" top="380" width="814" height="296" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="6" yradius="6">
                            <label left="12" top="10" width="790" height="26" text="KIT DE PERSONAGEM (36 OFICIOS UNIVERSAIS — DV 1d6 a 1d12)" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold"/>
                            <label left="12" top="44" width="44" height="34" text="Kit:" fontColor="{TEXT_MAIN}" fontSize="14" vertTextAlign="center"/>
                            <comboBox left="56" top="44" width="360" height="36" field="kitSelecionado" items="{xml_attr(kit_items)}" values="{xml_attr(kit_values)}" fontSize="13"/>
                            <button left="424" top="44" width="136" height="36" text="Aplicar Kit" fontSize="14">
                                <event name="onClick"><![CDATA[aplicarKitSelecionado();]]></event>
                            </button>
                            <button left="568" top="44" width="234" height="36" text="Subir Nivel (Rolar 1dX+CON)" fontSize="13">
                                <event name="onClick"><![CDATA[rolarSubirNivelPV();]]></event>
                            </button>

                            <label left="12" top="92" width="144" height="20" text="Dado de Vida (DV)" fontColor="{TEXT_GOLD}" fontSize="12"/>
                            <comboBox left="12" top="114" width="144" height="34" field="kitDvFaces" items="{xml_attr(dv_items)}" values="{xml_attr(dv_values)}" fontSize="12"/>

                            <label left="164" top="92" width="78" height="20" text="Per. Base" fontColor="{TEXT_MUTED}" fontSize="12"/>
                            <edit left="164" top="114" width="76" height="34" field="kitPerBase" type="number" horzTextAlign="center" fontSize="14"/>

                            <label left="248" top="92" width="78" height="20" text="Mult. INT" fontColor="{TEXT_MUTED}" fontSize="12"/>
                            <edit left="248" top="114" width="76" height="34" field="kitMultInt" horzTextAlign="center" fontSize="14"/>

                            <button left="332" top="114" width="114" height="34" text="Usar PV Medio" fontSize="12">
                                <event name="onClick"><![CDATA[recalcularFicha(); sheet.pvMax = sheet.pvSugerido; sheet.pvAtual = sheet.pvSugerido;]]></event>
                            </button>

                            <label left="454" top="92" width="170" height="20" text="Kit de Lenda (Niv. 11-20)" fontColor="{TEXT_GOLD}" fontSize="12"/>
                            <edit left="454" top="114" width="170" height="34" field="kitLenda" textPrompt="(Futuro — Niv. 11+)" fontSize="13"/>

                            <label left="632" top="92" width="170" height="20" text="Kit Epico (Niv. 21-30)" fontColor="{TEXT_CRIMSON}" fontSize="12"/>
                            <edit left="632" top="114" width="170" height="34" field="kitEpico" textPrompt="(Futuro — Niv. 21+)" fontSize="13"/>

                            <label left="12" top="158" width="460" height="22" text="HABILIDADE EXCLUSIVA DO KIT" fontColor="{TEXT_GOLD}" fontSize="14" fontStyle="bold"/>
                            <textEditor left="12" top="184" width="790" height="100" field="kitHabilidade" fontSize="14"/>
                        </rectangle>

                        <!-- PAINEL AUTOMATICO DE EVOLUCAO & XP -->
                        <rectangle left="6" top="684" width="1036" height="222" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="6" yradius="6">
                            <label left="12" top="8" width="1012" height="24" text="EVOLUCAO &amp; EXPERIENCIA (XP: Exploracao, Armadilhas, Social, Contratos &amp; Combates | Niveis 1-30)" fontColor="{TEXT_GOLD}" fontSize="13" fontStyle="bold"/>

                            <!-- BARRA DE XP -->
                            <rectangle left="12" top="36" width="1012" height="50" color="{BG_CARD_ALT}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="5" yradius="5">
                                <label left="10" top="7" width="84" height="36" text="XP ATUAL:" fontColor="{TEXT_GOLD}" fontSize="13" fontStyle="bold" vertTextAlign="center"/>
                                <edit left="96" top="7" width="102" height="36" field="xpAtual" type="number" fontColor="{TEXT_MAIN}" fontSize="17" fontStyle="bold" horzTextAlign="center"/>
                                <label left="200" top="7" width="18" height="36" text="/" fontColor="{TEXT_MUTED}" fontSize="18" horzTextAlign="center" vertTextAlign="center"/>
                                <rectangle left="220" top="7" width="110" height="36" color="{BG_INPUT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                                    <label align="client" field="xpProxNivel" fontColor="{TEXT_GOLD}" fontSize="14" fontStyle="bold" horzTextAlign="center" vertTextAlign="center"/>
                                </rectangle>
                                <button left="338" top="7" width="146" height="36" text="+ Adicionar XP" fontSize="14">
                                    <event name="onClick"><![CDATA[adicionarXP();]]></event>
                                </button>
                                <rectangle left="494" top="7" width="508" height="36" color="{BG_INPUT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                                    <label align="client" field="xpStatus" fontColor="{TEXT_GREEN}" fontSize="13" fontStyle="bold" horzTextAlign="center" vertTextAlign="center"/>
                                </rectangle>
                            </rectangle>

                            <rectangle left="12" top="98" width="194" height="110" color="{BG_CARD_ALT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="5" yradius="5">
                                <label left="4" top="8" width="186" height="20" text="PV MEDIO SUGERIDO" fontColor="{TEXT_MUTED}" fontSize="12" fontStyle="bold" horzTextAlign="center"/>
                                <label left="4" top="32" width="186" height="38" field="pvSugerido" fontColor="{TEXT_GREEN}" fontSize="26" fontStyle="bold" horzTextAlign="center"/>
                                <label left="4" top="78" width="186" height="20" field="proxNivelPv" fontColor="{TEXT_MUTED}" fontSize="12" horzTextAlign="center"/>
                            </rectangle>

                            <rectangle left="216" top="98" width="194" height="110" color="{BG_CARD_ALT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="5" yradius="5">
                                <label left="4" top="8" width="186" height="20" text="PTS PERICIA TOTAIS" fontColor="{TEXT_MUTED}" fontSize="12" fontStyle="bold" horzTextAlign="center"/>
                                <label left="4" top="32" width="186" height="38" field="periciasSugeridas" fontColor="{TEXT_GOLD}" fontSize="26" fontStyle="bold" horzTextAlign="center"/>
                                <label left="4" top="78" width="186" height="20" field="proxNivelPer" fontColor="{TEXT_MUTED}" fontSize="13" horzTextAlign="center"/>
                            </rectangle>

                            <rectangle left="420" top="98" width="194" height="110" color="{BG_CARD_ALT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="5" yradius="5">
                                <label left="4" top="8" width="186" height="20" text="PTS PERICIA GASTOS" fontColor="{TEXT_MUTED}" fontSize="12" fontStyle="bold" horzTextAlign="center"/>
                                <label left="4" top="32" width="186" height="38" field="periciasGastas" fontColor="{TEXT_MAIN}" fontSize="26" fontStyle="bold" horzTextAlign="center"/>
                                <label left="4" top="78" width="186" height="20" text="1-7:1p | 8-11:2p | 12+:3p" fontColor="{TEXT_MUTED}" fontSize="11" horzTextAlign="center"/>
                            </rectangle>

                            <rectangle left="624" top="98" width="194" height="110" color="{BG_CARD_ALT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="5" yradius="5">
                                <label left="4" top="8" width="186" height="20" text="AUMENTOS ATTR." fontColor="{TEXT_MUTED}" fontSize="12" fontStyle="bold" horzTextAlign="center"/>
                                <label left="4" top="32" width="186" height="38" field="aumentosAtributo" fontColor="{TEXT_GOLD}" fontSize="26" fontStyle="bold" horzTextAlign="center"/>
                                <label left="4" top="78" width="186" height="20" field="tetoAtributoTexto" fontColor="{TEXT_GOLD}" fontSize="12" horzTextAlign="center"/>
                            </rectangle>

                            <rectangle left="828" top="98" width="196" height="110" color="{BG_CARD_ALT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="5" yradius="5">
                                <label left="4" top="8" width="188" height="20" text="PATAMAR ATUAL" fontColor="{TEXT_MUTED}" fontSize="12" fontStyle="bold" horzTextAlign="center"/>
                                <label left="4" top="36" width="188" height="34" field="patamarTexto" fontColor="{TEXT_CRIMSON}" fontSize="17" fontStyle="bold" horzTextAlign="center"/>
                                <label left="12" top="78" width="90" height="20" text="Iniciativa:" fontColor="{TEXT_MUTED}" fontSize="13" horzTextAlign="leading"/>
                                <label left="96" top="78" width="88" height="20" field="iniciativaTotal" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold" horzTextAlign="trailing"/>
                            </rectangle>
                        </rectangle>
                    </layout>
                </scrollBox>
            </tab>

            <!-- ABA 2: COMBATE & FERIMENTOS -->
            <tab title="Combate &amp; Ferimentos">
                <scrollBox align="client">
                    <layout left="0" top="0" width="1056" height="1210">
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
                            <button left="862" top="148" width="160" height="42" text="Moribundo (CD 12)" fontSize="14">
                                <event name="onClick"><![CDATA[rolarD20("Teste de Moribundo (3 sucessos estabiliza)", getMod("constituicao"), "", 12);]]></event>
                            </button>
                        </rectangle>

                        <rectangle left="6" top="218" width="1036" height="320" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="6" yradius="6">
                            <label left="12" top="12" width="446" height="26" text="ARSENAL (Corpo a Corpo soma FOR no dano | Trava: 1/2/3/4)" fontColor="{TEXT_GOLD}" fontSize="13" fontStyle="bold"/>
                            <label left="464" top="12" width="74" height="26" text="Def. Alvo:" fontColor="{TEXT_CRIMSON}" fontSize="13" fontStyle="bold" horzTextAlign="trailing" vertTextAlign="center"/>
                            <edit left="542" top="8" width="52" height="34" field="defesaAlvo" type="number" textPrompt="0" fontColor="{TEXT_CRIMSON}" fontSize="15" fontStyle="bold" horzTextAlign="center"/>
                            <label left="602" top="12" width="120" height="26" text="Acoes (N):" fontColor="{TEXT_MAIN}" fontSize="13" horzTextAlign="trailing" vertTextAlign="center"/>
                            <comboBox left="726" top="8" width="296" height="34" field="multiAcoes" items="{{'1 Acao (Bonus Integral)', '2 Acoes (floor(Bonus/2) - 2)', '3 Acoes (floor(Bonus/3) - 3)', '4 Acoes (floor(Bonus/4) - 4)'}}" values="{{'1', '2', '3', '4'}}" fontSize="13"/>

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

                        <!-- PAINEL AUTOMATIZADO DE EXAUSTAO & DOENCAS DE ALENIA (v2.3) -->
                        <rectangle left="6" top="546" width="1036" height="398" color="{BG_CARD}" strokeColor="{BORDER_CRIMSON}" strokeSize="2" xradius="6" yradius="6">
                            <label left="12" top="10" width="520" height="24" text="EXAUSTAO (0-5) &amp; DOENCAS DE ALENIA (SISTEMA ENXUTO)" fontColor="{TEXT_CRIMSON}" fontSize="15" fontStyle="bold"/>
                            <label left="540" top="12" width="122" height="22" text="Nivel de Exaustao:" fontColor="{TEXT_GOLD}" fontSize="12" fontStyle="bold" horzTextAlign="trailing" vertTextAlign="center"/>
                            <comboBox left="668" top="8" width="356" height="30" field="exaustaoNivel" fontSize="12"
                                      items="{{'0 - Sem Exaustao (Normal)', '1 - Nivel 1 (-2 em todas as pericias)', '2 - Nivel 2 (-2 pericias | Deslocamento metade)', '3 - Nivel 3 (-2 pericias | -3 Ataques, Defesas e Resist.)', '4 - Nivel 4 (Tudo acima | PV Max a metade!)', '5 - Nivel 5 (COLAPSO E MORTE IMEDIATA!)'}}"
                                      values="{{'0', '1', '2', '3', '4', '5'}}"/>

                            <rectangle left="12" top="44" width="1012" height="30" color="{BG_INPUT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                                <label left="10" top="2" width="992" height="26" field="exaustaoResumo" fontColor="{TEXT_GOLD}" fontSize="12" fontStyle="bold" vertTextAlign="center"/>
                            </rectangle>

                            <!-- Seletor de Doencas + Colaboracao dos 3 Oficios -->
                            <label left="12" top="82" width="460" height="16" text="CATALOGO DE DOENCAS (6 MALES DE ALENIA + PERSONALIZADA)" fontColor="{TEXT_MUTED}" fontSize="11" fontStyle="bold"/>
                            <comboBox left="12" top="100" width="530" height="34" field="doencaSelecionada" items="{xml_attr(doenca_cat_items)}" values="{xml_attr(doenca_cat_values)}" fontSize="13"/>

                            <button left="552" top="99" width="174" height="36" text="+ Contrair / Adicionar" fontSize="13">
                                <event name="onClick"><![CDATA[contrairDoencaSelecionada();]]></event>
                            </button>
                            <button left="734" top="99" width="144" height="36" text="Ficha (7 Campos)" fontSize="12">
                                <event name="onClick"><![CDATA[verFichaDoenca();]]></event>
                            </button>
                            <rectangle left="886" top="99" width="138" height="36" color="{BG_INPUT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                                <label align="client" text="1x/dia ou 1x/sem" fontColor="{TEXT_MUTED}" fontSize="11" horzTextAlign="center" vertTextAlign="center"/>
                            </rectangle>

                            <!-- Colaboracao Medico + Herbalista + Alquimista (Teto +6) -->
                            <label left="12" top="142" width="186" height="24" text="CUIDADOS ATIVOS (3 OFICIOS):" fontColor="{TEXT_GREEN}" fontSize="11" fontStyle="bold" vertTextAlign="center"/>
                            <checkBox left="204" top="142" width="134" height="24" field="cuidadoMedico" text="Medico (+2)" fontColor="{TEXT_MAIN}" fontSize="12"/>
                            <checkBox left="344" top="142" width="148" height="24" field="cuidadoHerbalista" text="Herbalista (+2)" fontColor="{TEXT_MAIN}" fontSize="12"/>
                            <checkBox left="498" top="142" width="150" height="24" field="cuidadoAlquimista" text="Alquimista (+2)" fontColor="{TEXT_MAIN}" fontSize="12"/>
                            <label left="660" top="142" width="364" height="24" field="cuidadosResumo" fontColor="{TEXT_GREEN}" fontSize="12" fontStyle="bold" horzTextAlign="trailing" vertTextAlign="center"/>

                            {"".join(doenca_rows)}
                        </rectangle>

                        <rectangle left="6" top="954" width="1036" height="242" color="{BG_CARD}" strokeColor="{BORDER_CRIMSON}" strokeSize="1" xradius="6" yradius="6">
                            <label left="12" top="10" width="1010" height="24" text="FERIMENTOS GRAVES &amp; CICATRIZES PERMANENTES (Arbitragem Livre do Mestre)" fontColor="{TEXT_CRIMSON}" fontSize="15" fontStyle="bold"/>

                            <label left="12" top="38" width="500" height="20" text="FERIMENTOS ATIVOS / CONDICOES" fontColor="{TEXT_MUTED}" fontSize="13"/>
                            <textEditor left="12" top="62" width="500" height="168" field="ferimentosAtivos" fontSize="14"/>

                            <label left="524" top="38" width="500" height="20" text="CICATRIZES &amp; SEQUELAS PERMANENTES (Decisao do Mestre)" fontColor="{TEXT_GOLD}" fontSize="13"/>
                            <textEditor left="524" top="62" width="500" height="168" field="cicatrizesPermanentes" fontSize="14"/>
                        </rectangle>
                    </layout>
                </scrollBox>
            </tab>

            <!-- ABA 3: PERICIAS & TALENTOS -->
            <tab title="Pericias &amp; Talentos">
                <scrollBox align="client">
                    <layout left="0" top="0" width="1056" height="1730">
                        <rectangle left="6" top="6" width="1036" height="836" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="6" yradius="6">
                            <label left="12" top="8" width="710" height="22" text="34 PERICIAS — GRADUACAO COM TETO (0 Destr | 1-2 Inic | 3-7 Trein | 8-11 Espec | 12-16 Mestre)" fontColor="{TEXT_GOLD}" fontSize="13" fontStyle="bold"/>
                            <label left="724" top="8" width="156" height="22" text="Pts Gastos / Sugeridos:" fontColor="{TEXT_MUTED}" fontSize="12" horzTextAlign="trailing" vertTextAlign="center"/>
                            <label left="884" top="8" width="56" height="22" field="periciasGastas" fontColor="{TEXT_MAIN}" fontSize="15" fontStyle="bold" horzTextAlign="center" vertTextAlign="center"/>
                            <label left="940" top="8" width="16" height="22" text="/" fontColor="{TEXT_MUTED}" fontSize="15" horzTextAlign="center" vertTextAlign="center"/>
                            <label left="956" top="8" width="64" height="22" field="periciasSugeridas" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold" horzTextAlign="center" vertTextAlign="center"/>

                            <rectangle left="12" top="34" width="198" height="22" color="{BG_INPUT}" strokeColor="{BORDER_CRIMSON}" strokeSize="1" xradius="3" yradius="3">
                                <label align="client" field="tetoGradTexto" fontColor="{TEXT_GOLD}" fontSize="12" fontStyle="bold" horzTextAlign="center" vertTextAlign="center"/>
                            </rectangle>
                            <label left="218" top="34" width="806" height="22" field="avisoTetoGrad" fontColor="{TEXT_CRIMSON}" fontSize="12" vertTextAlign="center"/>

                            <label left="16" top="62" width="168" height="18" text="PERICIA" fontColor="{TEXT_MUTED}" fontSize="12" fontStyle="bold"/>
                            <label left="186" top="62" width="34" height="18" text="ATTR" fontColor="{TEXT_MUTED}" fontSize="11" fontStyle="bold" horzTextAlign="center"/>
                            <label left="222" top="62" width="42" height="18" text="GRAD" fontColor="{TEXT_GOLD}" fontSize="11" fontStyle="bold" horzTextAlign="center"/>
                            <label left="266" top="62" width="96" height="18" text="GRAU AUTO" fontColor="{TEXT_MUTED}" fontSize="11" fontStyle="bold" horzTextAlign="center"/>
                            <label left="366" top="62" width="40" height="18" text="OUT" fontColor="{TEXT_MUTED}" fontSize="11" fontStyle="bold" horzTextAlign="center"/>
                            <label left="410" top="62" width="44" height="18" text="TOT" fontColor="{TEXT_GOLD}" fontSize="11" fontStyle="bold" horzTextAlign="center"/>

                            <label left="528" top="62" width="168" height="18" text="PERICIA" fontColor="{TEXT_MUTED}" fontSize="12" fontStyle="bold"/>
                            <label left="698" top="62" width="34" height="18" text="ATTR" fontColor="{TEXT_MUTED}" fontSize="11" fontStyle="bold" horzTextAlign="center"/>
                            <label left="734" top="62" width="42" height="18" text="GRAD" fontColor="{TEXT_GOLD}" fontSize="11" fontStyle="bold" horzTextAlign="center"/>
                            <label left="778" top="62" width="96" height="18" text="GRAU AUTO" fontColor="{TEXT_MUTED}" fontSize="11" fontStyle="bold" horzTextAlign="center"/>
                            <label left="878" top="62" width="40" height="18" text="OUT" fontColor="{TEXT_MUTED}" fontSize="11" fontStyle="bold" horzTextAlign="center"/>
                            <label left="922" top="62" width="44" height="18" text="TOT" fontColor="{TEXT_GOLD}" fontSize="11" fontStyle="bold" horzTextAlign="center"/>

                            {"".join(skill_rows)}

                            <rectangle left="10" top="802" width="1016" height="24" color="{BG_INPUT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="3" yradius="3">
                                <label left="8" top="1" width="1000" height="22" field="avisoBonusExt" fontColor="{TEXT_GOLD}" fontSize="11" vertTextAlign="center"/>
                            </rectangle>
                        </rectangle>

                        <rectangle left="6" top="850" width="1036" height="292" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="6" yradius="6">
                            <label left="12" top="10" width="560" height="26" text="PERICIAS LIVRES / PERSONALIZADAS (CRIE QUANTAS QUISER!)" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold"/>
                            <button left="590" top="8" width="136" height="32" text="&lt; Pag. Ant." fontSize="13">
                                <event name="onClick"><![CDATA[mudarPaginaCustom(-1);]]></event>
                            </button>
                            <label left="732" top="10" width="96" height="26" field="customSkillPageLabel" fontColor="{TEXT_GOLD}" fontSize="14" fontStyle="bold" horzTextAlign="center" vertTextAlign="center"/>
                            <button left="834" top="8" width="190" height="32" text="Proxima / +10 Slots &gt;" fontSize="13">
                                <event name="onClick"><![CDATA[mudarPaginaCustom(1);]]></event>
                            </button>
                            <label left="12" top="44" width="1010" height="20" text="Digite qualquer pericia nova (ex: Forja de Adamante, Navegacao nos Corais, Dialeto de Yoketsu) — tambem respeita o Teto de Graduacao do nivel." fontColor="{TEXT_MUTED}" fontSize="12"/>

                            {"".join(custom_rows)}
                        </rectangle>

                        <!-- CATALOGO SELECIONAVEL DOS 44 TALENTOS & SLOTS DO PERSONAGEM -->
                        <rectangle left="6" top="1150" width="1036" height="444" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="2" xradius="6" yradius="6">
                            <label left="12" top="10" width="570" height="24" text="CATALOGO DOS 44 TALENTOS &amp; SLOTS DO PERSONAGEM (Niveis pares)" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold"/>

                            <button left="614" top="7" width="96" height="30" text="&lt; Anterior" fontSize="12">
                                <event name="onClick"><![CDATA[mudarPaginaTalentos(-1);]]></event>
                            </button>
                            <label left="714" top="8" width="118" height="28" field="talentosPageLabel" fontColor="{TEXT_GOLD}" fontSize="13" fontStyle="bold" horzTextAlign="center" vertTextAlign="center"/>
                            <button left="836" top="7" width="188" height="30" text="Proxima / +6 Slots &gt;" fontSize="12">
                                <event name="onClick"><![CDATA[mudarPaginaTalentos(1);]]></event>
                            </button>

                            <label left="12" top="40" width="280" height="16" text="CATEGORIA DE TALENTOS" fontColor="{TEXT_MUTED}" fontSize="11" fontStyle="bold"/>
                            <comboBox name="cmbTalentoCat" left="12" top="58" width="286" height="34" field="talentoCat" fontSize="13"
                                      items="{xml_attr(talento_cat_items)}" values="{xml_attr(talento_cat_values)}">
                                <event name="onChange"><![CDATA[_formRef = self; atualizarItensTalentos(self, true);]]></event>
                            </comboBox>

                            <label left="308" top="40" width="460" height="16" text="TALENTO OFICIAL (44 TALENTOS — COM PRE-REQUISITOS)" fontColor="{TEXT_MUTED}" fontSize="11" fontStyle="bold"/>
                            <comboBox name="cmbTalentoItem" left="308" top="58" width="466" height="34" field="talentoItem" fontSize="13"
                                      items="{xml_attr(talento_init_items)}" values="{xml_attr(talento_init_values)}">
                                <event name="onChange"><![CDATA[atualizarPreviewTalento();]]></event>
                            </comboBox>

                            <button left="784" top="57" width="154" height="36" text="+ Adicionar Talento" fontSize="13">
                                <event name="onClick"><![CDATA[adicionarTalentoSelecionado();]]></event>
                            </button>
                            <button left="944" top="57" width="80" height="36" text="Detalhes" fontSize="12">
                                <event name="onClick"><![CDATA[verDetalhesTalento();]]></event>
                            </button>

                            <rectangle left="12" top="100" width="1012" height="38" color="{BG_INPUT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                                <label left="10" top="2" width="992" height="34" field="talentoPreview" fontColor="{TEXT_GOLD}" fontSize="12" vertTextAlign="center" wordWrap="true"/>
                            </rectangle>

                            <label left="16" top="146" width="210" height="16" text="TALENTO ADQUIRIDO" fontColor="{TEXT_GOLD}" fontSize="11" fontStyle="bold"/>
                            <label left="230" top="146" width="186" height="16" text="PRE-REQUISITOS" fontColor="{TEXT_MUTED}" fontSize="11" fontStyle="bold"/>
                            <label left="420" top="146" width="474" height="16" text="EFEITO EM JOGO (CLIQUE EM [ANUNCIAR] PARA ENVIAR NO CHAT)" fontColor="{TEXT_MUTED}" fontSize="11" fontStyle="bold"/>
                            <label left="898" top="146" width="122" height="16" text="ACOES" fontColor="{TEXT_GOLD}" fontSize="11" fontStyle="bold" horzTextAlign="center"/>

                            {"".join(talento_rows)}
                        </rectangle>

                        <rectangle left="6" top="1604" width="1036" height="114" color="{BG_CARD}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="6" yradius="6">
                            <label left="12" top="8" width="1010" height="22" text="NOTAS LIVRES DE MANOBRAS, ESPECIALIZACOES &amp; TALENTOS EXTRAS" fontColor="{TEXT_MUTED}" fontSize="13" fontStyle="bold"/>
                            <textEditor left="12" top="34" width="1012" height="70" field="talentosManobras" fontSize="13"/>
                        </rectangle>
                    </layout>
                </scrollBox>
            </tab>

            <!-- ABA 4: INVENTARIO & SISTEMA MONETARIO -->
            <tab title="Inventario &amp; Moedas">
                <scrollBox align="client">
                    <layout left="0" top="0" width="1056" height="1130">
                        <rectangle left="6" top="6" width="1036" height="196" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="6" yradius="6">
                            <!-- Linha 1: Moedas (Padrao Prata) + Cartas de Credito -->
                            <label left="14" top="8" width="160" height="18" text="AUREOS (PO = 10 PP)" fontColor="{TEXT_GOLD}" fontSize="12" fontStyle="bold"/>
                            <edit left="14" top="28" width="144" height="34" field="moedasOuro" type="number" horzTextAlign="center" fontSize="16"/>

                            <label left="172" top="8" width="180" height="18" text="PRATAS / ESCUDOS (PP)" fontColor="{TEXT_MAIN}" fontSize="12" fontStyle="bold"/>
                            <edit left="172" top="28" width="156" height="34" field="moedasPrata" type="number" horzTextAlign="center" fontSize="16"/>

                            <label left="342" top="8" width="180" height="18" text="COBRES / VINTENS (PC)" fontColor="{TEXT_MUTED}" fontSize="12" fontStyle="bold"/>
                            <edit left="342" top="28" width="156" height="34" field="moedasCobre" type="number" horzTextAlign="center" fontSize="16"/>

                            <label left="512" top="8" width="210" height="18" text="CARTAS DE CREDITO (PP | 0 kg)" fontColor="{TEXT_GREEN}" fontSize="12" fontStyle="bold"/>
                            <edit left="512" top="28" width="186" height="34" field="cartasCredito" type="number" horzTextAlign="center" fontSize="16"/>

                            <label left="712" top="8" width="310" height="18" text="REDE BANCARIA / CUNHAGEM" fontColor="{TEXT_MUTED}" fontSize="12" fontStyle="bold"/>
                            <comboBox left="712" top="28" width="310" height="34" field="bancoOrigem" fontSize="13"
                                      items="{{'Corallis — Cera Azul (5% | Legal)', 'Kalis — Talha Cifrada (8% | Sigilo)', 'Misto (Corallis + Kalis)', 'Sem Conta Bancaria'}}"
                                      values="{{'corallis', 'kalis', 'misto', 'nenhum'}}"/>

                            <!-- Linha 2: Patrimonio, Peso das Moedas e Carga -->
                            <label left="14" top="70" width="240" height="18" text="PATRIMONIO TOTAL (BOLSA + BANCO)" fontColor="{TEXT_GOLD}" fontSize="11" fontStyle="bold"/>
                            <rectangle left="14" top="90" width="240" height="32" color="{BG_INPUT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                                <label align="client" field="patrimonioTotal" fontColor="{TEXT_GOLD}" fontSize="14" fontStyle="bold" horzTextAlign="center" vertTextAlign="center"/>
                            </rectangle>

                            <label left="268" top="70" width="210" height="18" text="PESO DAS MOEDAS (100 = 1 kg)" fontColor="{TEXT_MUTED}" fontSize="11" fontStyle="bold"/>
                            <rectangle left="268" top="90" width="210" height="32" color="{BG_INPUT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                                <label align="client" field="pesoMoedas" fontColor="{TEXT_MAIN}" fontSize="14" fontStyle="bold" horzTextAlign="center" vertTextAlign="center"/>
                            </rectangle>

                            <label left="492" top="70" width="150" height="18" text="CARGA ATUAL (kg)" fontColor="{TEXT_MUTED}" fontSize="11" fontStyle="bold"/>
                            <edit left="492" top="90" width="144" height="32" field="cargaAtual" horzTextAlign="center" fontSize="15"/>

                            <label left="650" top="70" width="170" height="18" text="CAPACIDADE MAX. (FOR x 5)" fontColor="{TEXT_GOLD}" fontSize="11" fontStyle="bold"/>
                            <rectangle left="650" top="90" width="156" height="32" color="{BG_INPUT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                                <label align="client" field="cargaMax" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold" horzTextAlign="center" vertTextAlign="center"/>
                            </rectangle>

                            <button left="820" top="88" width="202" height="34" text="+/- Transacao (PP)" fontSize="13">
                                <event name="onClick"><![CDATA[registrarTransacao();]]></event>
                            </button>

                            <!-- Linha 3: Padrao de Vida Mensal + Botoes Rapidos -->
                            <label left="14" top="130" width="160" height="18" text="PADRAO DE VIDA MENSAL" fontColor="{TEXT_GOLD}" fontSize="11" fontStyle="bold"/>
                            <comboBox left="176" top="128" width="330" height="32" field="padraoVida" fontSize="13"
                                      items="{{'Miseravel (0 PP/mes)', 'Pobre (6 PP/mes)', 'Modesto / Viajante (15 PP/mes)', 'Confortavel (45 PP/mes | Status 2)', 'Abastado (150 PP/mes | Status 3)', 'Aristocratico / Nobre (450 PP/mes | Status 4-5)'}}"
                                      values="{{'miseravel', 'pobre', 'modesto', 'confortavel', 'abastado', 'aristocratico'}}"/>

                            <button left="520" top="128" width="220" height="32" text="Pagar Mes (Padrao de Vida)" fontSize="13">
                                <event name="onClick"><![CDATA[pagarPadraoVida();]]></event>
                            </button>

                            <button left="754" top="128" width="268" height="32" text="Converter Troco (PC/PP/PO)" fontSize="13">
                                <event name="onClick"><![CDATA[converterTroco();]]></event>
                            </button>

                            <label left="14" top="168" width="1008" height="20" field="padraoVidaInfo" fontColor="{TEXT_MUTED}" fontSize="12"/>
                        </rectangle>

                        <!-- CARD EMPORIO AUTOMATICO (COMPRA DIRETA -> DESCONTA MOEDAS + GUARDA NO INVENTARIO + SOMA PESO) -->
                        <rectangle left="6" top="210" width="1036" height="142" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="2" xradius="6" yradius="6">
                            <label left="14" top="8" width="540" height="22" text="EMPORIO AUTOMATICO DE ALENIA (TOMO IX + ARMAS &amp; ARMADURAS)" fontColor="{TEXT_GOLD}" fontSize="14" fontStyle="bold"/>
                            <checkBox left="568" top="7" width="260" height="24" field="emporioUsarBanco" text="Usar Cartas de Credito se faltar bolsa" fontColor="{TEXT_GREEN}" fontSize="12"/>
                            <label left="834" top="8" width="188" height="22" text="155 itens • Debito automatico" fontColor="{TEXT_MUTED}" fontSize="11" horzTextAlign="trailing" vertTextAlign="center"/>

                            <label left="14" top="34" width="320" height="16" text="CATEGORIA DO CATALOGO" fontColor="{TEXT_MUTED}" fontSize="11" fontStyle="bold"/>
                            <comboBox name="cmbEmporioCat" left="14" top="52" width="322" height="34" field="emporioCat" fontSize="13"
                                      items="{xml_attr(emporio_cat_items)}" values="{xml_attr(emporio_cat_values)}">
                                <event name="onChange"><![CDATA[_formRef = self; atualizarItensEmporio(self, true);]]></event>
                            </comboBox>

                            <label left="346" top="34" width="380" height="16" text="ITEM / PACOTE (PRECO E PESO)" fontColor="{TEXT_MUTED}" fontSize="11" fontStyle="bold"/>
                            <comboBox name="cmbEmporioItem" left="346" top="52" width="382" height="34" field="emporioItem" fontSize="13"
                                      items="{xml_attr(emporio_init_items)}" values="{xml_attr(emporio_init_values)}">
                                <event name="onChange"><![CDATA[atualizarPreviewEmporio();]]></event>
                            </comboBox>

                            <label left="738" top="34" width="56" height="16" text="QTD" fontColor="{TEXT_GOLD}" fontSize="11" fontStyle="bold" horzTextAlign="center"/>
                            <edit left="738" top="52" width="56" height="34" field="emporioQtd" type="number" horzTextAlign="center" fontColor="{TEXT_MAIN}" fontSize="15" fontStyle="bold"/>

                            <button left="804" top="51" width="138" height="36" text="Comprar &amp; Guardar" fontSize="13">
                                <event name="onClick"><![CDATA[comprarItemEmporio();]]></event>
                            </button>

                            <button left="948" top="51" width="74" height="36" text="Detalhes" fontSize="12">
                                <event name="onClick"><![CDATA[verDetalhesEmporio();]]></event>
                            </button>

                            <rectangle left="14" top="94" width="1008" height="38" color="{BG_INPUT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                                <label left="10" top="2" width="988" height="34" field="emporioPreview" fontColor="{TEXT_GOLD}" fontSize="12" vertTextAlign="center" wordWrap="true"/>
                            </rectangle>
                        </rectangle>

                        <!-- CARD INVENTARIO EM SLOTS ILIMITADOS & CONSUMIVEIS UTILIZAVEIS -->
                        <rectangle left="6" top="362" width="1036" height="504" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="6" yradius="6">
                            <label left="14" top="10" width="410" height="24" text="INVENTARIO EM SLOTS &amp; CONSUMIVEIS (ILIMITADO)" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold"/>

                            <rectangle left="430" top="8" width="174" height="28" color="{BG_INPUT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                                <label align="client" field="invPesoTotal" fontColor="{TEXT_GREEN}" fontSize="12" fontStyle="bold" horzTextAlign="center" vertTextAlign="center"/>
                            </rectangle>

                            <button left="614" top="7" width="96" height="30" text="&lt; Anterior" fontSize="12">
                                <event name="onClick"><![CDATA[mudarPaginaInventario(-1);]]></event>
                            </button>
                            <label left="714" top="8" width="118" height="28" field="invPageLabel" fontColor="{TEXT_GOLD}" fontSize="13" fontStyle="bold" horzTextAlign="center" vertTextAlign="center"/>
                            <button left="836" top="7" width="188" height="30" text="Proxima / +10 Slots &gt;" fontSize="12">
                                <event name="onClick"><![CDATA[mudarPaginaInventario(1);]]></event>
                            </button>

                            <label left="14" top="40" width="1008" height="18" text="Compras do Emporio entram direto nos slots (Pacotes desempacotam sozinhos!). Em itens do tipo Consumivel, [Usar] desconta 1 carga, atualiza o peso e envia no chat." fontColor="{TEXT_MUTED}" fontSize="11"/>

                            <label left="16" top="62" width="254" height="16" text="NOME DO ITEM" fontColor="{TEXT_MUTED}" fontSize="11" fontStyle="bold"/>
                            <label left="274" top="62" width="102" height="16" text="TIPO" fontColor="{TEXT_MUTED}" fontSize="11" fontStyle="bold" horzTextAlign="center"/>
                            <label left="380" top="62" width="54" height="16" text="QTD/USOS" fontColor="{TEXT_GOLD}" fontSize="10" fontStyle="bold" horzTextAlign="center"/>
                            <label left="438" top="62" width="54" height="16" text="KG/UN" fontColor="{TEXT_MUTED}" fontSize="10" fontStyle="bold" horzTextAlign="center"/>
                            <label left="496" top="62" width="370" height="16" text="EFEITO / ESPECIFICACAO (ENVIADO AO CHAT AO USAR)" fontColor="{TEXT_MUTED}" fontSize="11" fontStyle="bold"/>
                            <label left="870" top="62" width="150" height="16" text="ACOES" fontColor="{TEXT_GOLD}" fontSize="11" fontStyle="bold" horzTextAlign="center"/>

                            {"".join(inv_rows)}
                        </rectangle>

                        <!-- NOTAS COMPLEMENTARES & RETROCOMPATIBILIDADE -->
                        <rectangle left="6" top="876" width="338" height="240" color="{BG_CARD}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="6" yradius="6">
                            <label left="10" top="8" width="318" height="22" text="MOCHILA / KIT (NOTAS LIVRES)" fontColor="{TEXT_GOLD}" fontSize="13" fontStyle="bold"/>
                            <textEditor left="10" top="34" width="318" height="196" field="equipamentoMochila" fontSize="13"/>
                        </rectangle>

                        <rectangle left="354" top="876" width="338" height="240" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="6" yradius="6">
                            <label left="10" top="8" width="318" height="22" text="ARMADURAS, ADAMANTE &amp; RELIQUIAS (RD)" fontColor="{TEXT_GOLD}" fontSize="13" fontStyle="bold"/>
                            <textEditor left="10" top="34" width="318" height="196" field="reliquiasAdamante" fontSize="13"/>
                        </rectangle>

                        <rectangle left="702" top="876" width="340" height="240" color="{BG_CARD}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="6" yradius="6">
                            <label left="10" top="8" width="320" height="22" text="ALQUIMIA, VENENOS &amp; FERRAMENTAS" fontColor="{TEXT_GOLD}" fontSize="13" fontStyle="bold"/>
                            <textEditor left="10" top="34" width="320" height="196" field="alquimiaSuprimentos" fontSize="13"/>
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

            <!-- ABA 6: AUTORIA & ATUALIZACAO -->
            <tab title="Autoria &amp; Atualizacao">
                <scrollBox align="client">
                    <layout left="0" top="0" width="1056" height="680">
                        <!-- CARD DE AUTORIA -->
                        <rectangle left="6" top="6" width="1036" height="176" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="2" xradius="6" yradius="6">
                            <label left="20" top="18" width="996" height="30" text="ALENIA RPG — FICHA OFICIAL PARA RRPG FIRECAST" fontColor="{TEXT_GOLD}" fontSize="19" fontStyle="bold" horzTextAlign="center"/>
                            <label left="20" top="56" width="996" height="34" text="Plugin desenvolvido por Mestre Carlos" fontColor="{TEXT_MAIN}" fontSize="22" fontStyle="bold" horzTextAlign="center"/>
                            <label left="20" top="98" width="996" height="24" text="Sistema d20 Sombrio • 36 Kits Universais • 44 Talentos • Graduacao Livre de Pericias • Atlas &amp; Bestiario" fontColor="{TEXT_MUTED}" fontSize="14" horzTextAlign="center"/>

                            <rectangle left="168" top="130" width="220" height="34" color="{BG_INPUT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                                <label left="8" top="0" width="110" height="34" text="Versao Atual:" fontColor="{TEXT_MUTED}" fontSize="13" vertTextAlign="center"/>
                                <label left="118" top="0" width="94" height="34" field="pluginVersaoAtual" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold" horzTextAlign="center" vertTextAlign="center"/>
                            </rectangle>

                            <rectangle left="404" top="130" width="260" height="34" color="{BG_INPUT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                                <label align="client" text="ID: br.com.alenia.rpg_oficial" fontColor="{TEXT_MUTED}" fontSize="13" horzTextAlign="center" vertTextAlign="center"/>
                            </rectangle>

                            <rectangle left="680" top="130" width="190" height="34" color="{BG_INPUT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                                <label align="client" text="Firecast SDK 3.7b" fontColor="{TEXT_GREEN}" fontSize="13" fontStyle="bold" horzTextAlign="center" vertTextAlign="center"/>
                            </rectangle>
                        </rectangle>

                        <!-- CARD DE ATUALIZACAO AUTOMATICA -->
                        <rectangle left="6" top="194" width="1036" height="244" color="{BG_CARD}" strokeColor="{BORDER_GOLD}" strokeSize="1" xradius="6" yradius="6">
                            <label left="20" top="14" width="996" height="28" text="ATUALIZACAO AUTOMATICA INTEGRADA" fontColor="{TEXT_GOLD}" fontSize="16" fontStyle="bold" horzTextAlign="center"/>
                            <label left="20" top="44" width="996" height="24" text="O verificador consulta a versao oficial mais recente e instala a atualizacao diretamente dentro do seu Firecast." fontColor="{TEXT_MUTED}" fontSize="14" horzTextAlign="center"/>

                            <button left="248" top="80" width="540" height="50" text="Clique aqui para verificar se ha atualizacoes" fontSize="16">
                                <event name="onClick"><![CDATA[verificarEAtualizarPlugin(false);]]></event>
                            </button>

                            <rectangle left="48" top="142" width="940" height="40" color="{BG_INPUT}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="4" yradius="4">
                                <label align="client" field="statusAtualizacao" fontColor="{TEXT_GOLD}" fontSize="14" horzTextAlign="center" vertTextAlign="center"/>
                            </rectangle>

                            <button left="168" top="194" width="330" height="36" text="Forcar Reinstalacao Direta" fontSize="14">
                                <event name="onClick"><![CDATA[verificarEAtualizarPlugin(true);]]></event>
                            </button>
                            <button left="538" top="194" width="330" height="36" text="Abrir Biblioteca Online de Alenia" fontSize="14">
                                <event name="onClick"><![CDATA[abrirLinkExterno(BIBLIOTECA_URL);]]></event>
                            </button>
                        </rectangle>

                        <!-- CARD DE NOVIDADES -->
                        <rectangle left="6" top="450" width="1036" height="224" color="{BG_CARD}" strokeColor="{BORDER_DIM}" strokeSize="1" xradius="6" yradius="6">
                            <label left="20" top="14" width="996" height="26" text="HISTORICO DE VERSOES &amp; RECURSOS DA FICHA" fontColor="{TEXT_GOLD}" fontSize="15" fontStyle="bold"/>
                            <label left="20" top="46" width="996" height="24" text="• v2.3 — Automacao de Exaustao (0-5) e das 6 Doencas de Alenia (3 slots, colaboracao Medico+Herbalista+Alquimista ate +6, rolagem de resistencia e evolucao automatica)." fontColor="{TEXT_MAIN}" fontSize="13"/>
                            <label left="20" top="74" width="996" height="24" text="• v2.2 — Botao Receber Dano (RD + alerta Golpe Devastador), rolagem auto em consumiveis, Catalogo 44 Talentos, Aplicar Kit completo, Retrato clicavel e aviso OUT +6." fontColor="{TEXT_MAIN}" fontSize="13"/>
                            <label left="20" top="102" width="996" height="24" text="• v2.1 — Inventario em Slots Ilimitados com botao [Usar] em todos os consumiveis (desconta uso, atualiza carga e anuncia no chat) + desempacote automatico dos 5 Pacotes." fontColor="{TEXT_MUTED}" fontSize="13"/>
                            <label left="20" top="130" width="996" height="24" text="• v1.5-v2.0 — Emporio Automatico (155 itens), Teto de Graduacao (+4..+16), Sistema Monetario Padrao Prata, Cartas de Credito, XP (Niv. 1-30), CD e dano +FOR." fontColor="{TEXT_MUTED}" fontSize="13"/>
                            <label left="20" top="168" width="996" height="38" text="Nota: Apos uma atualizacao, basta fechar e reabrir a janela da ficha para ativar a nova versao sem perder nenhum dado salvo." fontColor="{TEXT_GREEN}" fontSize="13" wordWrap="true"/>
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
    <dataLink fields="{{'emporioCat', 'emporioItem', 'emporioQtd'}}">
        <event name="onChange"><![CDATA[atualizarItensEmporio(self, false);]]></event>
    </dataLink>
    <dataLink fields="{{'talentoCat', 'talentoItem'}}">
        <event name="onChange"><![CDATA[atualizarItensTalentos(self, false);]]></event>
    </dataLink>
    {"".join(custom_datalinks)}
    {"".join(inv_datalinks)}
    {"".join(talentos_datalinks)}
</form>
'''
    with open(LFM_PATH, "w", encoding="utf-8") as f:
        f.write(lfm)
    total_emp = sum(len(v) for v in emporio_items.values())
    total_cons = sum(1 for v in emporio_items.values() for it in v if it["tipo"] == "cons")
    total_tal = sum(len(v) for v in talentos_items.values())
    print(f"[OK] AleniaFicha.lfm v2.3 gerado ({len(lfm)} bytes, {total_emp} itens Emporio / {total_cons} consumiveis / {total_tal} talentos / 6 doencas + Exaustao).")


if __name__ == "__main__":
    build_lfm()
