# ALENIA RPG — Livro de Regras Oficial (Edição Revisada v2.0)

> *"O aço quebra, os reis sangram e o mar engole até os mais sábios. Só sobrevive em Alenia quem sabe quando atacar, quando aparar e quando calar."*

---

## 1. Visão Geral e Proposta do Sistema

**Alenia** é um sistema próprio de RPG medieval sombrio movido por **d20**, desenhado para campanhas de **exploração continental, intriga política, sobrevivência e combates táticos mortais** — integrado ao **RRPG Firecast**.

### Pilares Fundamentais
1. **Povos Jogáveis Exclusivamente Humanos**: todas as civilizações vivas e personagens jogáveis são humanos, diferenciados por origem cultural, atributos e ofício. Feras naturais e raros horrores lendários existem apenas como ameaças do mundo.
2. **Sem Classes Rígidas + 36 Kits Universais**: qualquer explorador pode aprender qualquer perícia ou manobra. Os **Kits** representam ofícios universais que definem o **Dado de Vida (`1d6` a `1d12`)**, o **multiplicador de Inteligência para perícias**, a formação inicial e uma habilidade de ofício — e podem ser trocados ou complementados ao longo da campanha.
3. **Curva Clara de Poder (Recruta → Lenda → Épico)**: personagens iniciantes (Recrutas) são frágeis e sujeitos a morte súbita; veteranos (Lendas, Nív. 11–20) suportam provações maiores e dominam maestrias raras; figuras Épicas (Nív. 21–30) alcançam feitos míticos — mas o **Golpe Devastador (`> 2/3` do PV)**, venenos, ferimentos graves e inimigos do mesmo patamar mantêm a tensão real.
4. **Combate Tático e Sem Pólvora**: Defesa situacional (*Aparar* vs. *Esquiva*), armaduras comuns **jamais** dão RD (RD é restrita a itens extremamente raros), armas possuem margens e multiplicadores de crítico próprios, **Múltiplas Ações** possuem teto vinculado ao treino e ações defensivas sacrificam o ataque para proteger a si ou aliados.
5. **Magia Estilo *Game of Thrones***: raríssima, ancestral, ritualística, cara e envolta em lendas.

---

## 2. Atributos Base e Geração de Personagem

Todo personagem possui **6 Atributos Base** na escala clássica **3 a 18**:

| Atributo | Sigla | Escopo Principal |
| :--- | :---: | :--- |
| **Força** | `FOR` | Poder muscular, ataques corpo a corpo pesados, dano, atletismo, capacidade de carga |
| **Destreza** | `DES` | Agilidade, iniciativa, Defesa, ataques à distância e ágeis, furtividade, acrobacia |
| **Constituição** | `CON` | Vigor, Pontos de Vida (PV), testes de Moribundo, venenos, fadiga e **Golpe Devastador** |
| **Inteligência** | `INT` | Raciocínio, **Pontos de Perícia**, erudição, engenharia, alquimia, investigação |
| **Sabedoria** | `SAB` | Percepção, intuição, sobrevivência, medicina, navegação, força de vontade |
| **Carisma** | `CAR` | Presença, persuasão, liderança, enganação, intimidação, etiqueta e arte |

### Cálculo do Modificador
$$\text{Modificador} = \left\lfloor \frac{\text{Valor do Atributo} - 10}{2} \right\rfloor$$

| Valor | 3 | 4–5 | 6–7 | 8–9 | 10–11 | 12–13 | 14–15 | 16–17 | 18–19 | 20–21 |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Mod.** | `-4` | `-3` | `-2` | `-1` | `0` | `+1` | `+2` | `+3` | `+4` | `+5` |

### Geração Inicial de Atributos
- **Regra Oficial (Rolagem)**: role **`4d6` e descarte o menor dado** para cada um dos 6 atributos. Na ficha do **RRPG Firecast**, o botão **"Rolar Atributos Iniciais (4d6)"** só funciona quando todos os 6 campos estiverem vazios, preenche os valores automaticamente e anuncia todos os dados (incluindo o descartado) no chat da mesa.
- **Regra Opcional (Compra de Pontos)**: comece com todos os 6 atributos em `8` e distribua **27 pontos** (`9–13` = 1 pt cada; `14–15` = 2 pts cada; máximo inicial `15`).

---

## 3. Atributos Especiais (Opcionais — Evolução Exclusiva por Feitos)

Nem todo personagem possui Atributos Especiais. Eles operam na escala **`0` a `5`** (`0` = não possui; `1–5` = nível de poder/peso narrativo e bônus direto somado em testes pertinentes).

> [!IMPORTANT]
> **Atributos Especiais JAMAIS sobem com pontos de nível.** Eles evoluem (ou diminuem) **exclusivamente por Feitos reais em campanha**, arbitrados pelo Mestre.

| Atributo Especial | O que Representa | Exemplos de Feitos para Evoluir |
| :--- | :--- | :--- |
| **Status** (`0–5`) | Linhagem nobre, patente militar, prestígio acadêmico, renome tribal ou crédito mercantil. | Salvar uma casa nobre em Altavanne, conquistar patente em Corallis, liderar caravanas em Gaddra. |
| **Fé Verdadeira** (`0–5`) | Convicção espiritual autêntica e incorruptível (plural — válida em qualquer tradição sincera de Alenia), capaz de resistir ao horror e produzir bênçãos sutis ou presságios. | Sustentar juramentos sob sacrifício real, enfrentar horrores de Incognito sem recuar, realizar atos de devoção genuína. |
| **Influência no Submundo** (`0–5`) | Redes de informantes, respeito entre piratas do Mar dos Corais/Ravena, contrabandistas e guildas ocultas de Kalis. | Controlar uma rota clandestina, pagar dívidas de sangue, derrubar um rival no submundo. |
| **Dom Antigo** (`0–5`) | *(Raríssimo — exige aval do Mestre)* Sangue ancestral, visões proféticas, ecos de Incognito ou afinidade com rituais esquecidos. | Sobreviver a um rito ancestral, decifrar ruínas de Kelgore ou Incognito, pagar o preço de uma visão verdadeira. |
| **Especial Livre** (`0–5`) | Espaço aberto na ficha para um atributo exclusivo da campanha criado pelo Mestre (ex.: *Honra do Clã*, *Dívida de Sangue*, *Segredo de Kalgard*). | Definido pelo Mestre. |

---

## 4. Testes, Dificuldades e Perícias (Recalibradas)

### Teste Básico
$$\text{Resultado} = 1\text{d}20 + \text{Modificador do Atributo} + \text{Grau de Treino} + \text{Modificadores Situacionais}$$

| Dificuldade (CD) | Grau do Desafio | Exemplos em Alenia |
| :---: | :--- | :--- |
| **10** | Rotineira / Fácil | Negociar suprimentos comuns em Merlinport, escalar muro baixo |
| **15** | Moderada | Navegar recifes calmos, rastrear trilha recente, estancar sangramento |
| **20** | Difícil | Forjar liga superior, infiltrar mansão em Altavanne, tratar fratura grave |
| **25** | Muito Difícil | Cruzar o Mar dos Corais sob tempestade, decifrar inscrição de Kelgore |
| **30** | Lendária / Extrema | Trabalhar adamante puro em campo, sobreviver a tempestade em Incognito |

### Graduação Livre, Graus Automáticos e Travas de Patamar
Em Alenia, as perícias evoluem por **graduação numérica contínua** (`+0, +1, +2, +3, +4, +5...` — você **não** fica preso a saltos fixos). Conforme os pontos investidos na perícia, a ficha classifica automaticamente o **Grau de Domínio** do personagem, usado como referência para pré-requisitos de Talentos, *Defesa Total* e travas de *Múltiplas Ações*:

| Grau Automático | Graduação (Bônus) | Custo por Graduação | Custo Acumulado (Mínimo) | Requisito Mínimo |
| :--- | :---: | :---: | :---: | :--- |
| **Destreinado** | `+0` | `—` | `0 pts` | Nenhum |
| **Iniciante** | `+1` a `+2` | `1 pt / grad.` | `1 a 2 pts` | Nenhum *(ainda não cumpre pré-requisito "Treinado")* |
| **Treinado** | `+3` a `+7` | `1 pt / grad.` | `3 a 7 pts` | Nível 1+ *(Kit inicial começa em `+3` gratuito)* |
| **Especialista** | `+8` a `+11` | `2 pts / grad.` | `9 a 15 pts` | **Nível 5+** *(veterano reconhecido)* |
| **Mestre** | `+12+` | `3 pts / grad.` | `18+ pts` | **Nível 11+ (Patamar Lenda)** *(ou Feito excepcional aprovado pelo Mestre)* |

*(Nota: Perícias recebidas como **Treinado (`+3`)** pelo Kit inicial já contam com os `3 pts` iniciais pagos — subir uma delas para `+4` custa `1 pt`; chegar a `+7` custa `+4 pts`; subir para `+8` [Especialista, Nív. 5+] custa `+2 pts` adicionais, e assim por diante.)*

### Pontos de Perícia (Uniforme e Equilibrado)
Em todas as fórmulas de perícia, aplica-se sempre a proteção **`máx(0, Mod. INT)`**, garantindo que Inteligência baixa nunca reduza o ganho abaixo da base do Kit:
- **No Nível 1**: recebe as perícias treinadas iniciais do Kit (`+3`) **mais** `máx(2, ⌊Base do Kit + máx(0, Mod. INT) × Mult. INT⌋)` pontos livres.
- **Ao Subir de Nível**: recebe `máx(1, ⌊(Base do Kit + máx(0, Mod. INT) × Mult. INT) × Fator de Patamar⌋)` pontos de perícia.
- **Sem Kit (Média Padrão)**: `Base = 1`, `Mult. INT = 0,75`, `DV = 1d8`.

*(Exemplo de calibração: um **Erudito** com `INT 18 (+4)`, `Base 2`, `Mult. INT 1,25` recebe `7 pts` no Nív. 1 e `7 pts/nível` em Recruta. No Nív. 10 terá ~70 pts totais — podendo distribuir graduações livres como `+5`, `+7` ou `+9` entre dezenas de perícias sem criar nenhum Mestre precoce. No Nív. 20, somando o patamar Lenda `1,5×`, alcançará **4 a 6 Maestrias (`+12+`)** genuínas, mantendo especialização real mesmo até o Nív. 30!)*

### Lista Oficial de Perícias (34 Perícias + Perícias Livres Ilimitadas)
Além das **34 perícias oficiais** abaixo, o jogador pode criar **quantas perícias personalizadas quiser** na ficha do Firecast (ex.: *Forja de Adamante*, *Pilotagem nos Corais*, *Dialeto de Yõketsu*), seguindo os mesmos custos e travas de patamar:

| Categoria | Perícias (Atributo Base) |
| :--- | :--- |
| **Combate (6)** | `Armas Brancas (FOR/DES)`, `Armas à Distância (DES)`, `Luta Desarmada (FOR/DES)`, `Aparar (FOR/DES)`, `Esquiva (DES)`, `Escudos (FOR)` |
| **Físicas & Exploração (8)** | `Atletismo (FOR)`, `Acrobacia (DES)`, `Furtividade (DES)`, `Escalada (FOR)`, `Natação (FOR)`, `Cavalgar (DES)`, `Sobrevivência (SAB)`, `Navegação & Náutica (SAB/INT)` |
| **Percepção & Subterfúgio (5)** | `Percepção (SAB)`, `Investigação (INT)`, `Disfarce (CAR)`, `Ladinagem & Fechaduras (DES)`, `Prestidigitação (DES)` |
| **Sociais & Intriga (6)** | `Persuasão (CAR)`, `Enganação (CAR)`, `Intimidação (CAR/FOR)`, `Intuição (SAB)`, `Etiqueta & Corte (CAR)`, `Barganha & Comércio (CAR/INT)` |
| **Saber, Ciência & Ofícios (9)** | `Medicina & Cirurgia (INT/SAB)`, `Alquimia & Venenos (INT)`, `Forja & Metalurgia (INT/FOR)`, `Engenharia & Mecânica (INT)`, `Herbalismo & Natureza (SAB)`, `História & Lendas (INT)`, `Geografia & Cartografia (INT)`, `Idiomas & Cifras (INT)`, `Religião & Ocultismo (SAB/INT)` |

---

## 5. Níveis, Dados de Vida, Patamares e Troca de Kit (Níveis 1 a 30)

### Como e Quando Subir de Nível
A evolução ocorre por **Marcos de Campanha** definidos pelo Mestre (tipicamente ao concluir um contrato relevante, expedição entre cidades ou arco político — a cada 2 a 4 sessões no patamar Recruta).

### Pontos de Vida por Dado de Vida (Estilo D&D conforme a Natureza do Kit)
- **Dado de Vida (DV) do Kit**:
  - **Combatente Brutal (`1d12`)**: *Bárbaro / Berserker*.
  - **Combatente Pesado (`1d10`)**: *Mercenário, Cavaleiro, Soldado, Guarda-Costas, Lutador*.
  - **Explorador / Híbrido / Suporte Marcial (`1d8`)**: *Sem Kit, Duelista, Arqueiro, Contrabandista, Caçador de Recompensas, Saqueador, Pirata, Navegador, Explorador, Patrulheiro, Domador, Ferreiro, Carpinteiro, Inquisidor, Ermitão*.
  - **Especialista / Erudito / Intriga / Corte (`1d6`)**: *Ladino, Assassino, Espião, Charlatão, Mercador, Alquimista, Médico, Erudito, Engenheiro, Herbalista, Astrônomo, Nobre, Diplomata, Bardo, Sacerdote, Tocado pelo Dom Antigo*.
- **PV no Nível 1**: `Valor Máximo do DV do Kit + Valor Bruto de Constituição` *(ex.: Mercenário `1d10` com CON 14 começa com `24 PV`; Erudito `1d6` com CON 10 começa com `16 PV`)*.
- **PV ao Subir de Nível**: role **`1dX + Mod. CON`** (mínimo `1 PV` por nível; opção fixa para quem não quiser rolar: metade arredondada para cima do DV + `Mod. CON`, ex.: `1d10` = `6 + Mod. CON`, `1d8` = `5 + Mod. CON`, `1d6` = `4 + Mod. CON`).

### Os 3 Patamares Dinâmicos
| Patamar | Níveis | Pontos de Perícia | Maestria de Combate *(Dano Base)* | Papel no Mundo |
| :--- | :---: | :---: | :--- | :--- |
| **Recruta** | `1 – 10` | `1×` taxa base | Dano normal da arma | Exploradores, soldados e viajantes vulneráveis. Acesso aos **36 Kits Universais**. |
| **Lenda** | `11 – 20` | `1,5×` (+50%) | **`+1` dado individual** do tipo da arma *(Especialista/Mestre)* | Figuras célebres e temidas; destrava grau **Mestre (`+12`)** e futuros **Kits de Lenda**. |
| **Épico** | `21 – 30` | `2×` (o dobro) | **`+2` dados individuais** do tipo da arma *(Mestre)* | Nomes imortais capazes de encarar horrores de Incognito; destrava futuros **Kits Épicos**. |

- **Exemplos de Maestria de Combate**: soma-se `+1` dado individual do mesmo tipo da arma (e **não** o conjunto inteiro de dados) em Lenda, e `+2` dados individuais em Épico.
  - *Espada Longa (`1d8`)*: Recruta `1d8` → Lenda **`2d8`** → Épico **`3d8`**.
  - *Montante (`2d6`)*: Recruta `2d6` → Lenda **`3d6`** *(e não `4d6`)* → Épico **`4d6`**.
  - **Interação com Crítico**: os dados de Maestria integram o dano base da arma e **são multiplicados no Acerto Crítico**, preservando a relevância do *Golpe Devastador* nos patamares avançados.

- **Aumento de Atributo Base**: `+1` em um Atributo Base à escolha a cada **3 níveis** (`3, 6, 9, 12, 15, 18, 21, 24, 27, 30`).
- **Talentos / Manobras**: `1` Talento livre a cada **nível par** (`2, 4, 6...`).
- **Mudança ou Acúmulo de Kit em Campanha**: o Kit inicial define sua formação e equipamento de partida. Se o personagem treinar um novo ofício durante a campanha (com tempo e mentor aprovados pelo Mestre), ele **mantém** todas as perícias e a habilidade já adquiridas e passa a usar o **DV e multiplicadores do novo Kit** nos níveis seguintes (ganhando a habilidade do novo Kit após 2 níveis nele).

---

## 6. Combate Ágil, Tático e Mortal

### Turno, Economia de Ações e Iniciativa
- **Iniciativa**: `1d20 + Mod(DES) + ⌊Grau em Percepção / 3⌋`.
- No seu turno, você dispõe estritamente de:
  - **1 Ação Principal**: atacar, usar manobra tática (*Agarrar, Derrubar, Empurrar, Desengajar, Ajudar*), *Defesa Total*, *Proteger Aliado*, estabilizar aliado ou usar item complexo.
  - **1 Movimento**: deslocar-se até `9m` (6 quadrados), levantar-se do chão (custa metade do Movimento: `4,5m`), recarregar besta leve ou executar interações rápidas explicitamente vinculadas ao Movimento.
  - **1 Reação** *(por rodada)*: usada fora do seu turno para *Ataque de Oportunidade*, *Aparar Relâmpago* ou interceptar golpe com *Proteger Aliado*.
  - **Ações Livres**: atos triviais (falar poucas palavras, largar um objeto, ou efeitos explícitos de Kit como a troca de arma do Mercenário).

### Defesa Situacional, Surpresa e Condições
$$\text{Defesa} = 10 + \text{Mod(DES)} + \text{Bônus de Armadura} + \text{Bônus de Escudo} + \text{Perícia Pertinente}$$

- **Contra ataques corpo a corpo**: soma o grau de treino em **`Aparar`** (ou **`Esquiva`** se desarmado).
- **Contra projéteis / ataques à distância**: soma o grau de treino em **`Esquiva`**.
- **Surpreso / Desprevenido**: ocorre em emboscadas (até o início do primeiro turno da vítima), quando cego ou imobilizado. O alvo usa exclusivamente **`Defesa Desprevenido = 10 + Armadura + Escudo`** (perde `Mod(DES)` e a perícia *Aparar/Esquiva*). Não aplica penalidade extra de `-4` por estar surpreso.
- **Caído / Derrubado**: condição física independente da surpresa. Enquanto estiver no chão, sofre **`-4` na Defesa contra ataques corpo a corpo** (e recebe **`+2` na Defesa contra ataques à distância**, por apresentar perfil reduzido) até gastar metade do seu Movimento (`4,5m`) para se levantar. *(Se estiver Caído e Desprevenido ao mesmo tempo, usa `Defesa Desprevenido - 4` em corpo a corpo.)*
- **Quebrando Defesas Altas**: *Flanquear* concede `+2` no ataque; *Ajudar* concede `+2`; derrubar impõe `-4` na Defesa corpo a corpo.

> [!CAUTION]
> **Regra de Ouro da Armadura**: armaduras comuns **JAMAIS** concedem Redução de Dano (RD). Elas aumentam apenas a **Defesa**. Redução de Dano (`RD Especial`) existe **exclusivamente** em itens extremamente raros (como armaduras lendárias de **Adamante Puro** ou relíquias ancestrais).

### Múltiplas Ações (Regra Storyteller — Com Trava de Treino)
Um combatente pode dividir sua Ação Principal em **`N` ataques** (ou ações físicas rápidas equivalentes — nunca multiplicando Movimento nem Reação, e não aplicável a bestas sem recarga rápida):
1. **Limite Máximo de `N` pelo Grau Automático na Perícia Usada**:
   - **Destreinado / Iniciante (`+0` a `+2`)**: máximo **`1` ação** (não pode dividir).
   - **Treinado (`+3` a `+7`)**: máximo **`2` ações**.
   - **Especialista (`+8` a `+11`)**: máximo **`3` ações**.
   - **Mestre (`+12+`)**: máximo **`4` ações**.
2. **Fórmula do Bônus por Ação** *(para `N ≥ 2`)*:
$$\text{Bônus por Ação} = \left\lfloor \frac{\text{Bônus Total de Ataque}}{N} \right\rfloor - N$$
3. **Regra Anti-Abuso (Bônus Mínimo)**: você só pode declarar `N` ações se o `Bônus por Ação` resultante for **`≥ 0`** (se ficar negativo, reduza `N`). Isso impede "pesca de 20 natural" com dezenas de ataques sem habilidade real.

### Ações Defensivas (Sacrificando o Ataque)
Sacrificando sua Ação Principal de ataque até o início do próximo turno:
- **Defesa Total (Si Mesmo)**: ganha **`+4` na Defesa** (`+6` se Especialista em Aparar/Esquiva/Escudos; `+8` se Mestre) e impõe **`-2`** nos ataques corpo a corpo direcionados a você.
- **Proteger Aliado**: escolha 1 aliado adjacente (`1,5m`). Atacantes contra ele sofrem **`-4`** no ataque (`-6` se Especialista em Aparar/Escudos; `-8` se Mestre), e você pode escolher **absorver o golpe no lugar do aliado** caso ainda acerte.

### Críticos por Arma e O Que Multiplica
- **Acerto Crítico**: ocorre quando o resultado natural do `1d20` cair dentro da **Margem de Crítico da arma** (ex.: `19–20`, `18–20`, `20`) **e** o ataque superar a Defesa (ou for `20` natural, que sempre acerta).
- **O Que Multiplica**: multiplica-se pelo **Multiplicador da arma (`×2`, `×3`, `×4`)** o pacote completo de dano base: `(Dados da arma + Dados de Maestria de Lenda/Épico + Modificador de atributo + Bônus fixo da arma/adamante)`. Dados bônus circunstanciais externos (como *Golpe Oportunista* do Ladino ou dano de veneno) são rolados e somados **após** a multiplicação!
- **Falha Crítica (`1` natural)**: erro automático + abertura tática — o atacante deve gastar seu **Movimento** (ou sua **Reação** da rodada) para recuperar a postura/destravar a arma; se já tiver gasto ambos, um inimigo adjacente recebe `+2` no próximo ataque contra ele.

### Golpe Devastador (`> 2/3` do PV Máximo) — Morte Instantânea
Sempre que um **único ataque** causar dano **estritamente maior que `2/3` do PV Máximo** do alvo (`⌊PV Máx × 2 / 3⌋ + 1`):
- O alvo realiza imediatamente um **Teste de Constituição** (`CD 15 + ⌊(Dano - Limiar) / 2⌋`).
- **Falha**: **Morte Instantânea** (golpe fatal em órgão vital).
- **Sucesso**: sobrevive reduzindo PV normalmente, mas sofre automaticamente um **Ferimento Grave**.

---

## 7. Procedimentos de Mesa: Moribundo, Cura, Manobras e Sobrevivência

### Estado Moribundo & Estabilização
Ao cair a **`0 PV`** (sem morrer instantaneamente), o personagem cai inconsciente e **Moribundo**:
- **A cada turno seu**: role **`1d20 + Mod(CON)` contra CD 12**.
  - **3 Sucessos** (não precisam ser consecutivos): estabiliza em `0 PV` (inconsciente por `1d4` horas, desperta com `1 PV`).
  - **3 Falhas**: morre.
  - **20 natural**: acorda imediatamente com `1 PV`. **1 natural**: conta como 2 falhas.
  - **Dano sofrido enquanto moribundo**: impõe 1 falha automática (ou 2 se crítico).
- **Estabilizar Aliado**: Ação Principal + teste de **Medicina CD 15** (ou uso de atadura/cataplasma reduz CD para `12`) estabiliza imediatamente.

### Descanso, Recuperação Natural e Ferimentos Graves
- **Descanso Curto (`1 hora` de repouso e água/curativos)**: recupera **`1 Dado de Vida do Kit + Mod. CON`** em PV (máximo 1× entre combates pesados; até 2× por dia).
- **Descanso Longo (`8 horas` em abrigo seguro com alimentação)**: recupera **`50%` do PV Máximo** (arredondado para cima) e reduz **1 nível de Exaustão**.
- **Ferimentos Graves & Cicatrizes *(Arbitragem Livre do Mestre)***: gatilhos incluem cair a `0 PV`, sobreviver a *Golpe Devastador* ou sofrer crítico marcante. Exemplos para o Mestre adaptar livremente:
  - *Sangramento*: `1d4` PV/turno até Medicina CD 15;
  - *Fratura / Membro Avariado*: `-3` em ações usando o membro até `1d4` semanas (reduzido à metade com Cirurgião);
  - *Concussão*: `-2` em testes mentais e Percepção até Descanso Longo;
  - *Cicatriz / Sequela Permanente*: arbitrada pelo Mestre em traumas extremos sem tratamento adequado.

### Manobras Táticas e Ataque de Oportunidade
- **Ataque de Oportunidade (Reação)**: provocado sempre que uma criatura **sai voluntariamente do alcance corpo a corpo** (`1,5m`, ou `3m` para piques) de um inimigo consciente, armado e que possa vê-la — ou realiza ação que baixa totalmente a guarda adjacente a um inimigo (como disparar arco/besta ou prestar socorro médico em corpo a corpo). Consome a **Reação** do inimigo para **1 único ataque básico** *(sem Múltiplas Ações)*. Deslocamento forçado (como ser empurrado) **nunca** provoca Ataque de Oportunidade.
- **Desengajar (Ação Principal)**: permite percorrer todo o seu Movimento (`9m`) no turno **sem provocar Ataques de Oportunidade** ao deixar o alcance corpo a corpo de inimigos.
- **Ajudar (Ação Principal)**: exige estar adjacente (`1,5m`) ao aliado ou ao inimigo distraído em combate (ou até `9m` por voz/sinal fora de combate). Concede **`+2`** no próximo ataque ou teste de perícia do aliado antes do início do seu próximo turno. **Limite**: no máximo **1 ajudante em combate** (`+2` máx.); em tarefas fora de combate, até **2 ajudantes** (`+4` máx., se o espaço permitir).
- **Agarrar (Ação Principal)**: ataque corpo a corpo (*Atletismo* ou *Luta Desarmada*) contra Defesa Aparar/Esquiva do alvo. Alvo agarrado tem deslocamento `0` e `-2` em ataques; escapar custa Ação Principal (*Atletismo/Acrobacia* oposto).
- **Derrubar / Empurrar `3m` (Ação Principal)**: teste oposto de *Atletismo* (ou *Armas Brancas* com haste) contra *Atletismo/Acrobacia* do alvo. Alvo derrubado fica **Caído** (`-4` na Defesa corpo a corpo, `+2` contra projéteis à distância; gasta `4,5m` de Movimento para levantar).
- **Flanquear**: dois aliados conscientes em lados opostos de um mesmo inimigo em corpo a corpo recebem **`+2` no acerto** contra ele.

### Fome, Sede, Frio/Calor e Exaustão (Níveis 1 a 5)
Um dia sem água (ou 3 dias sem comida, ou uma noite sem abrigo em frio/calor extremo sem sucesso em Sobrevivência CD 15) impõe **+1 nível de Exaustão**:
1. **Nível 1**: `-2` em todos os testes de perícia.
2. **Nível 2**: deslocamento reduzido à metade.
3. **Nível 3**: `-3` em ataques, Defesa e testes de resistência.
4. **Nível 4**: PV Máximo reduzido à metade.
5. **Nível 5**: colapso e morte (se não socorrido imediatamente).

### Perseguições e Acidentes Marítimos
- **Perseguições**: resolvidas em **3 a 5 rodadas** de testes opostos (Atletismo, Acrobacia, Cavalgar ou Navegação, somando obstáculos narrativos); quem acumular 3 vitórias alcança ou despista o oponente.
- **Navegação Perigosa (Mar dos Corais / Mar Intransponível)**: cada dia de travessia em área de recife ou tempestade exige teste de **Navegação & Náutica** do piloto (CD `15` calmo, `20` recifes/neblina, `25` tempestade). Falha reduz velocidade pela metade ou causa impacto no casco (`2d6` a `4d6` de avaria; barcos pequenos afundam com `30–50` de dano sem reparo de Carpinteiro).

---

## 8. Talentos e Manobras (Níveis Pares — 44 Talentos em 4 Categorias)

A cada **nível par** (`2, 4, 6, 8, 10...`), o explorador escolhe **1 Talento** dentre as quatro categorias abaixo — **Marciais & Táticos**, **Sobrevivência & Exploração**, **Sociais & Intriga** e **Mentais & Erudição**.

### Regras de Pré-Requisitos e Cadeias
- **Pré-requisitos obrigatórios**: para escolher um Talento, você deve atender a **todos** os requisitos listados (valor mínimo de Atributo Base, grau de treino em perícia, Patamar/Nível mínimo, Atributo Especial ou **Talento anterior** na árvore).
- **Especialização em cadeia**: vários Talentos formam progressões em dois degraus *(ex.: `Língua de Prata` → `Teia de Cortes` ou `Mente Analítica` → `Dedução de Campo`)*. Você pode combinar livremente Talentos de categorias diferentes.
- **Anti-acúmulo**: salvo menção explícita, o mesmo Talento não pode ser adquirido duas vezes, nenhum Talento concede RD passiva a armaduras comuns e nenhum Talento viola os limites de treino de *Múltiplas Ações*.

### 8.1 Talentos Marciais e Táticos (12 Talentos)
| Talento | Pré-requisitos | Efeito em Jogo |
| :--- | :--- | :--- |
| **Aparar Relâmpago** | `DES 12+`, Treinado em *Aparar* | `1×/rodada`, usa sua **Reação** para somar **`+2`** na Defesa contra um ataque corpo a corpo. |
| **Riposta Mortal** | `DES 14+`, Especialista em *Aparar*, **Aparar Relâmpago** | Quando um ataque corpo a corpo contra você errar após *Aparar Relâmpago* ou *Defesa Total*, você desfere imediatamente **`1` contra-ataque básico** contra o atacante *(parte da mesma Reação)*. |
| **Muralha de Aço** | `FOR 13+`, Treinado em *Escudos* ou *Aparar* | Ao usar *Proteger Aliado*, cobre até **`2` aliados adjacentes** e anula bônus de *Flanquear* contra eles. |
| **Bastião Inquebrável** | `FOR 15+`, `CON 14+`, Especialista em *Escudos*, **Muralha de Aço** | Quando absorve golpe pelo aliado em *Proteger Aliado* ou mantém *Defesa Total* com escudo, reduz o dano desse impacto em **`⌊Mod. FOR + Mod. CON⌋`** *(mín. `2`, bloqueio ativo — não é RD passiva)* e ignora *Empurrar* ou *Derrubar*. |
| **Golpe Preciso** | `FOR 13+` ou `DES 13+`, Treinado em *Armas Brancas* ou *Distância* | Reduz em **`1`** a Margem de Crítico de um tipo de arma escolhido *(ex.: `19–20` → `18–20`; não acumula na mesma arma)*. |
| **Anatomia Letal** | `INT 12+` ou `SAB 13+`, Nív. `6+`, **Golpe Preciso** | Em Acertos Críticos com a arma escolhida, reduz em **`2`** o limiar do *Golpe Devastador* do alvo **ou** impõe **Sangramento** (`1d4` PV/turno até Medicina CD 15). |
| **Fluxo de Lâminas** | `DES 14+`, Treinado em *Armas Brancas* ou *Luta Desarmada* | Reduz em **`1`** a penalidade `-N` em *Múltiplas Ações* *(ex.: em 2 ações subtrai `1` em vez de `2`; mantém teto de treino e bônus mínimo `≥ 0`)*. |
| **Tempestade de Aço** | `DES 16+`, Patamar Lenda (`Nív. 11+`), Especialista em *Armas Brancas*, **Fluxo de Lâminas** | Ao usar *Múltiplas Ações* contra inimigos distintos em alcance, o primeiro ataque em cada alvo diferente recebe **`+2`** no acerto. |
| **Tiro Firme** | `DES 13+`, Treinado em *Armas à Distância* | Ignora cobertura parcial e vento moderado com arcos/bestas; recarrega besta leve como Ação Livre `1×/turno`. |
| **Olho de Falcão** | `DES 15+`, `SAB 13+`, Especialista em *Armas à Distância*, **Tiro Firme** | Aumenta em **`+50%`** o alcance efetivo de arcos/bestas; se gastar seu **Movimento** mirando imóvel antes de disparar `1` tiro único, soma **`+3`** no acerto e **`+1d6`** no dano *(não multiplica em crítico)*. |
| **Quebra-Guarda** | `FOR 14+`, Treinado em *Armas Brancas* ou *Atletismo* | **`+3`** em *Derrubar*, *Empurrar* e *Agarrar*; ao derrubar um oponente com arma pesada ou haste, causa dano igual ao seu `Mod. FOR` *(mín. `1`)*. |
| **Combate de Cais** | `FOR 12+` ou `DES 12+` | Sem penalidade com armas improvisadas (`1d6`), **`+2`** contra alvos Caídos ou Agarrados e pode usar *Ajudar* em combate como distração suja *(alvo testa DES CD 14 ou sofre `-2` na próxima Defesa)*. |

### 8.2 Talentos de Sobrevivência, Vigor e Exploração (10 Talentos)
| Talento | Pré-requisitos | Efeito em Jogo |
| :--- | :--- | :--- |
| **Sangue Frio** | `CON 12+` ou `SAB 12+` | **`+3`** em testes de CON contra *Golpe Devastador* e em testes de SAB contra medo, pânico e horrores sobrenaturais. |
| **Vontade de Ferro** | `CON 14+`, `SAB 13+`, Nív. `6+`, **Sangue Frio** | Exige **`4` falhas** *(em vez de `3`)* para morrer no estado *Moribundo*; `1×/Descanso Longo`, ignora os efeitos de `1` nível de *Exaustão* durante uma cena inteira. |
| **Passo Silencioso** | `DES 13+`, Treinado em *Furtividade* | Move-se em velocidade normal (`9m`) em *Furtividade* sem penalidade e recebe **`+2`** para ocultar rastros. |
| **Fantasma da Bruma** | `DES 15+`, Especialista em *Furtividade*, **Passo Silencioso** | Em penumbra, neblina ou mata densa, pode tentar esconder-se novamente usando o **Movimento** após agir *(Percepção oposta)*; seu primeiro ataque saindo de ocultação soma **`+1d6`** de dano *(não multiplica em crítico)*. |
| **Lobo do Mar** | `DES 12+` ou `SAB 12+`, Treinado em *Navegação* ou *Acrobacia* | Ignora penalidades de convés instável, recifes e embarcações sob tempestade; **`+2`** em *Natação* e *Navegação* sob mau tempo. |
| **Leme de Tempestade** | `SAB 14+`, Especialista em *Navegação & Náutica*, **Lobo do Mar** | Reduz em **`3`** a CD de navegação em recifes/tempestades *(Mar dos Corais / Mar Intransponível)* e reduz à **metade** qualquer avaria no casco sob seu comando. |
| **Mãos de Cirurgião** | `INT 12+` ou `SAB 12+`, Treinado em *Medicina & Cirurgia* | **`+3`** em *Medicina* para estabilizar, estancar sangramentos e reduzir pela metade o tempo de recuperação de *Ferimentos Graves*. |
| **Bisturi de Baldbella** | `INT 14+`, `SAB 13+`, Especialista em *Medicina & Cirurgia*, **Mãos de Cirurgião** | Em *Descanso Curto*, um aliado tratado por você recupera **`+1d6` PV extras** e remove `1` veneno leve/sangramento; reduz em **`3`** a CD de cirurgias extremas *(incluindo extração de toxinas ou parasitas)*. |
| **Passo de Caravana** | `CON 13+`, Treinado em *Sobrevivência* | Suporta o dobro do tempo sem água ou abrigo antes de testar *Exaustão* e recebe **`+2`** em *Sobrevivência* para guiar e abrigar até `6` companheiros. |
| **Caçador de Fronteira** | `SAB 13+`, Treinado em *Sobrevivência* e *Percepção* | Ao examinar rastros por `5 min`, descobre direção, número aproximado e um hábito/vulnerabilidade da presa *(arbitrado pelo Mestre)*, ganhando **`+2`** na Iniciativa se o confronto ocorrer na cena. |

### 8.3 Talentos Sociais, Intriga e Liderança (11 Talentos)
| Talento | Pré-requisitos | Efeito em Jogo |
| :--- | :--- | :--- |
| **Voz de Comando** | `CAR 12+` | Como **Ação Principal**, concede **`+2`** no próximo ataque ou na Defesa *(até seu próximo turno)* de até `4` aliados que possam ouvi-lo. |
| **Estandarte Vivo** | `CAR 15+`, Nív. `6+`, **Voz de Comando** | Sua *Voz de Comando* alcança todos os aliados a até `18m`, soma **`+3`** contra medo/horror e, `1×/combate`, permite a `1` aliado realizar um Movimento livre *(sem Ataque de Oportunidade)* ou um novo teste contra medo/paralisia. |
| **Língua de Prata** | `CAR 13+`, Treinado em *Persuasão* ou *Enganação* | **`+2`** em *Persuasão* e *Enganação* em audiências ou negociações; `1×/sessão`, se falhar em um teste social por `3` ou menos, pode reformular o argumento e rolar novamente *(aceitando o 2º resultado)*. |
| **Teia de Cortes** | `CAR 15+`, `INT 12+`, Especialista em *Etiqueta* ou *Persuasão*, **Língua de Prata** | Após `1h` em corte, taverna ou salão mercantil, identifica quem detém o poder real na sala e um conflito oculto entre facções locais, ganhando **`+3`** em testes sociais usando essa alavanca na cena. |
| **Máscara de Mil Rostos** | `CAR 13+`, Treinado em *Disfarce* e *Enganação* | Monta disfarces em metade do tempo, imita sotaques regionais de Alenia sem penalidade e impõe **`-3`** na *Percepção/Intuição* de quem tentar desmascará-lo. |
| **Sussurro de Kalgard** | `CAR 14+`, `SAB 13+`, Especialista em *Enganação* ou *Intimidação*, **Máscara de Mil Rostos** ou **Língua de Prata** | Após `10 min` de conversa, pode plantar uma suspeita ou boato plausível *(Enganação/Persuasão vs. Intuição do alvo)*; em sucesso, o alvo age com cautela ou desconfiança contra o terceiro citado até obter prova contrária. |
| **Presença Aterradora** | `CAR 13+` ou `FOR 14+`, Treinado em *Intimidação* | **`+2`** em *Intimidação*; em combate, gasta **Ação Principal** para intimidar `1` inimigo inteligente a até `9m` *(Intimidação vs. SAB do alvo)*: em sucesso, o alvo sofre **`-2`** nos ataques por `2 rodadas` *(1×/alvo/cena)*. |
| **Olhar do Árbitro** | `SAB 13+`, Treinado em *Intuição* | **`+3`** em *Intuição* para detectar mentiras, coerção, emboscadas disfarçadas ou influência emocional anômala; percebe na hora se alguém age sob chantagem ou medo oculto. |
| **Crédito de Porto** | `CAR 12+` ou `INT 12+`, Treinado em *Barganha & Comércio* | Consegue **`15%` de desconto** em compras comuns e **`+15%`** na venda de cargas; em qualquer porto ou rota de caravana, obtém abrigo seguro, barco ou crédito modesto *(até `50 PP`)* sem garantia imediata. |
| **Rede de Informantes** | `CAR 14+` ou `INT 14+`, `Submundo 1+` ou `Status 1+`, **Crédito de Porto** ou **Língua de Prata** | `1×/aventura` *(ou ao chegar a uma grande cidade)*, aciona contatos para obter sem rolagem um mapa de acesso, salvo-conduto discreto, rota de fuga ou dossiê básico sobre um NPC *(o Mestre define o favor futuro)*. |
| **Coração de Cronista** | `CAR 13+` | Durante *Descanso Curto* ou *Longo*, suas histórias, cantos ou discursos elevam o moral: até `5` aliados recuperam **`+1d4` PV extras** no Descanso Curto ou ganham **`+2`** no primeiro teste contra medo/Exaustão do dia seguinte. |

### 8.4 Talentos Mentais, Erudição e Ofício (11 Talentos)
| Talento | Pré-requisitos | Efeito em Jogo |
| :--- | :--- | :--- |
| **Mente Analítica** | `INT 13+`, Treinado em *Investigação* | **`+3`** em *Investigação* e *História & Lendas* para reconstruir cenas, detectar documentos forjados ou estudar ruínas; encontra pistas secundárias em metade do tempo. |
| **Dedução de Campo** | `INT 15+`, `SAB 13+`, Especialista em *Investigação*, **Mente Analítica** | Como **Ação Principal** em combate *(ou `1 min` observando antes)*, testa *Investigação/Intuição* CD `15` contra um inimigo visível; em sucesso, descobre sua fraqueza *(menor Defesa, vulnerabilidade ou RD)* e você + `1` aliado ganham **`+2`** no acerto contra ele por `3 rodadas`. |
| **Estrategista de Batalha** | `INT 14+`, `SAB 12+` | Usa **`Mod. INT`** no lugar de `Mod. DES` na **Iniciativa**; no início do combate, pode trocar sua posição na ordem de Iniciativa com `1` aliado voluntário que possa ouvi-lo. |
| **Mestre Tático** | `INT 16+`, Nív. `8+`, **Estrategista de Batalha** | Ao usar a ação *Ajudar* em combate, orienta até **`2` aliados a até `9m`** por voz *(sem precisar ficar adjacente a `1,5m`)*, concedendo `+2` a cada um até seu próximo turno. |
| **Sentidos Aguçados** | `SAB 13+`, Treinado em *Percepção* | **`+3`** em *Percepção* e **`+2`** fixo na Iniciativa; não pode ser surpreendido por emboscadas mundanas enquanto estiver consciente e não incapacitado. |
| **Memória Enciclopédica** | `INT 13+` | Recorda mapas, brasões, tratados e diálogos com precisão; **`+2`** em *História*, *Geografia*, *Religião* e *Idiomas*, e pode realizar testes de conhecimento mesmo em perícias Destreinadas sem penalidade por falta de biblioteca. |
| **Poliglota das Cinco Terras** | `INT 13+`, Treinado em *Idiomas & Cifras* | Aprende imediatamente `2` idiomas/dialetos ou cifras de Alenia, recebe **`+3`** para decifrar códigos de Kalis e inscrições de Kelgore/Incognito, e capta o sentido geral de línguas desconhecidas após breve contato. |
| **Mãos de Alquimista** | `INT 13+`, Treinado em *Alquimia & Venenos* ou *Herbalismo* | Reduz em **`25%`** o custo de reagentes e pela metade o tempo de preparo de venenos, antídotos, óleo incendiário e extratos; aumenta em **`+2`** a CD das misturas que você mesmo preparar. |
| **Engenho de Armadilhas** | `INT 13+`, Treinado em *Engenharia & Mecânica* | **`+3`** para montar ou desarmar armadilhas, fechaduras complexas e mecanismos antigos; em `10 min` com materiais de campo, monta armadilha improvisada *(alerta, laço que derruba ou estacas de `1d8`, Percepção CD `15 + Mod. INT`)*. |
| **Mente Blindada** | `SAB 14+` | **`+3`** em testes de SAB contra manipulação, intimidação, ilusões sensoriais, sussurros de *Thanatos/Incognito* e impulsos psíquicos; `1×/sessão`, pode refazer um teste de SAB fracassado contra horror ou coerção. |
| **Vigia dos Ritos Antigos** | `INT 14+` ou `SAB 14+`, `Fé Verdadeira 1+` ou `Dom Antigo 1+`, Treinado em *Religião & Ocultismo* | Soma **`+2`** adicional na *Preparação Ritualística* *(respeitando o teto de `+8`)*, reduz em `1d6` qualquer dano de sacrifício ritual *(mín. `1`)* e pressente relíquias de Incognito ou condutores ativos de adamante a até `18m`. |

### 8.5 Mapa Rápido das Cadeias de Evolução
- **Duelista & Escudeiro**: *Aparar Relâmpago* → *Riposta Mortal* | *Muralha de Aço* → *Bastião Inquebrável*
- **Letalidade & Velocidade**: *Golpe Preciso* → *Anatomia Letal* | *Fluxo de Lâminas* → *Tempestade de Aço* | *Tiro Firme* → *Olho de Falcão*
- **Sobrevivência & Ofício**: *Sangue Frio* → *Vontade de Ferro* | *Passo Silencioso* → *Fantasma da Bruma* | *Lobo do Mar* → *Leme de Tempestade* | *Mãos de Cirurgião* → *Bisturi de Baldbella*
- **Liderança & Intriga**: *Voz de Comando* → *Estandarte Vivo* | *Língua de Prata* → *Teia de Cortes* | *Máscara de Mil Rostos* → *Sussurro de Kalgard* | *Crédito de Porto* → *Rede de Informantes*
- **Estratégia & Intelecto**: *Mente Analítica* → *Dedução de Campo* | *Estrategista de Batalha* → *Mestre Tático*

---

## 9. Equipamentos, Economia e Tabela de Preços de Referência

> **Padrão Monetário**: `1 Moeda de Ouro (PO) = 10 Moedas de Prata (PP) = 100 Moedas de Cobre (PC)`. Não existe pólvora em Alenia.

### Tabela de Preços do Cotidiano & Viagem
| Item / Serviço | Preço Médio | Observação |
| :--- | :---: | :--- |
| Refeição simples + caneca em estalagem | `2 PC` | `1 PP` para banquete de frutos do mar em Baldbella |
| Hospedagem (salão comum / quarto privado) | `3 PC` / `1 PP` | Por noite em Merlinport ou Dahrma |
| Rações secas de viagem (1 semana) | `5 PP` | Indispensável em Gaddra ou pântanos |
| Salário diário (trabalhador / mercenário) | `3 PC` / `2 PP` | Mercenários veteranos cobram `5 PP/dia` + espólio |
| Passagem marítima (Merlinport ↔ Alineus) | `15 PP` | Travessia clandestina no Mar Intransponível: `80–150 PP` |
| Consulta cirúrgica (tratar Ferimento Grave) | `20 PP` | Cirurgiões renomados de Baldbella cobram até `50 PP` |
| Cavalo de estrada / Mula de carga | `120 PP` / `45 PP` | Montarias do deserto em OX: `150 PP` |
| Estojo médico / Gazuas / Bolsa alquímica | `25 PP` / `20 PP` / `40 PP` | Ferramentas profissionais de ofício |

### Tabela de Armas Comuns
| Arma | Preço | Dano | Margem / Mult. | Propriedades |
| :--- | :---: | :---: | :---: | :--- |
| **Adaga / Punhal** | `4 PP` | `1d4` | `19–20 / ×2` | Leve, Ágil (`FOR/DES`), Arremesso 6m |
| **Espada Curta** | `15 PP` | `1d6` | `19–20 / ×2` | Leve, Ágil (`FOR/DES`) |
| **Florete / Estoque** | `30 PP` | `1d6` | `18–20 / ×2` | Ágil (`DES`), Perfurante |
| **Espada Longa** | `25 PP` | `1d8` | `19–20 / ×2` | Versátil (`1d10` em 2 mãos) |
| **Lâmina Oriental (Yõketsu)** | `55 PP` | `1d8` | `18–20 / ×2` | Ágil em 2 mãos, corte preciso |
| **Cimitarra / Sabre** | `25 PP` | `1d6` | `18–20 / ×2` | Ágil (`DES`), ideal em convés/sela |
| **Machado de Batalha** | `20 PP` | `1d8` | `20 / ×3` | Versátil (`1d10` em 2 mãos) |
| **Machado Grande** | `35 PP` | `1d12` | `20 / ×3` | Duas mãos, Pesada |
| **Montante / Espada Grande** | `50 PP` | `2d6` | `19–20 / ×2` | Duas mãos, Pesada |
| **Lança / Pique** | `10 PP` | `1d8` | `20 / ×3` | Alcance (`3m` se pique), Versátil |
| **Martelo de Guerra** | `22 PP` | `1d8` | `20 / ×3` | Contundente |
| **Picareta de Guerra** | `18 PP` | `1d6` | `20 / ×4` | Perfurante letal |
| **Arco Curto / Longo** | `20 / 45 PP` | `1d6 / 1d8` | `20 / ×3` | 2 mãos, Alcance 24m / 45m |
| **Besta Leve / Pesada** | `35 / 75 PP` | `1d8 / 1d10` | `19–20 / ×2` | Recarga (Mov. / Ação Principal) |

*(Regra de Dano: **armas corpo a corpo** — inclusive armas ágeis que atacam com `DES` — e armas de arremesso **sempre somam `Mod(FOR)` ao dano**; arcos e bestas usam o dano base da arma + eventuais bônus fixos de adamante ou talento.)*

### Armaduras e Escudos *(Bônus de Defesa — Zero RD)*
| Proteção | Preço | Bônus Defesa | Penalidade Furt./Acrob. | Observação |
| :--- | :---: | :---: | :---: | :--- |
| **Gibão Reforçado** | `12 PP` | `+1` | `0` | Discreta para viagem |
| **Couro Batido** | `25 PP` | `+2` | `0` | Padrão de exploradores |
| **Cota de Malha** | `75 PP` | `+3` | `-2` | Boa proteção contra cortes |
| **Brigantina / Meia-Placa** | `180 PP` | `+4` | `-3` | Favorita de mercenários veteranos |
| **Placas Completas** | `450 PP` | `+5` | `-5` | Exige `FOR 13+` |
| **Broquel / Escudo Médio / Torre** | `10 / 20 / 45 PP` | `+1 / +2 / +3` | `0 / -1 / -3` | Torre dá `+2` extra em *Proteger Aliado* |

### O Adamante de Aurora *(Metal Estratégico)*
- **Armas de Adamante** *(raríssimas — a partir de `800–2.000 PP` ou concessão real)*: nunca perdem o fio, concedem **`+1` no acerto e `+2` no dano**, e ignoram até `3` pontos de `RD Especial`.
- **Peças de Armadura em Adamante Puro / Relíquias Antigas**: única fonte de **`RD Especial`** (`RD 2` a `RD 5`, arbitrado pelo Mestre).

---

## 10. Magia, Rituais e Fé Verdadeira (Calibrados)

A magia em Alenia é rara, lenta, perigosa e cercada de lendas — **não existem magias instantâneas de combate**. Testes de rituais ancestrais ou milagres sutis utilizam **`1d20 + Dom Antigo`** ou **`1d20 + Fé Verdadeira`** (sempre mediante aval narrativo do Mestre).

### Dificuldades e Preparação Ritualística
Como `1d20 + Atributo Especial (máx. 5)` alcança naturalmente até `25`, **ritos maiores exigem preparação concreta** para acumular bônus antes da rolagem:

| Grau do Rito / Prodígio | CD | Exemplos |
| :--- | :---: | :--- |
| **Sutil / Presságio** | `15` | Sonho profético vago, acalmar medo de um grupo, pressentir mentira ou perigo próximo |
| **Menor / Bênção** | `20` | Estancar praga em um enfermo, visão dirigida pelo fogo, selar uma porta contra horrores |
| **Maior / Proibido** | `25` | Maldição de sangue, despertar ecos em ruínas de Kelgore, desviar um golpe mortal |
| **Lendário *(Exige Preparo)*** | `28–30` | Rito colossal ligado aos segredos de Incognito ou Thanatos |

**Modificadores de Preparação Ritualística** *(cumulativos até `+8`)*:
- **Tempo e Concentração** *(horas de vigília, jejum ou canto)*: **`+2`**
- **Componentes Raros** *(ervas da Ilha das Safiras, cinzas de Thanatos, relíquia verdadeira)*: **`+2`**
- **Local de Poder / Consagração** *(santuário antigo, ruínas de Kelgore, eclipse observado)*: **`+2`**
- **Sacrifício de Sangue / Vitalidade** *(sofrer `1d6` a `2d6` de dano não mitigável ou 1 nível de Exaustão)*: **`+2` a `+4`**
- **Auxílio de Acólitos / Coro de Fiéis**: **`+1` por par de ajudantes** *(máx. `+2`)*


### O Simbionte da Comunhão *(Regras dos 4 Estágios & Remoção)*
Quando um personagem entra em contato prolongado com águas de uma colônia ativa, recebe implantação deliberada ou passa por um falso rito de cura ligado ao **Regente das Cinzas**, uma larva simbionte pode se alojar no corpo. A progressão **não tem velocidade fixa** — avança conforme exposição à rede, luto extremo ou escolha voluntária do hospedeiro:

| Estágio | Benefício Mecânico e Narrativo | Consequência e Teste |
| :--- | :--- | :--- |
| **I. Contato** | Conforto emocional, sono sem pesadelos e **`+1`** em testes contra medo ou desespero. | Sonhos compartilhados e sensações ou lembranças sem origem clara. |
| **II. Enlace** | **1× por cena**, acessa a memória de outro hospedeiro para receber **`+3`** em um teste de perícia que não domina *(ex.: corrente marítima, idioma ou ofício antigo)*. | Emoções alheias atravessam decisões e relações; em gatilhos ligados à rede, faz **SAB CD 14** *(soma `Fé Verdadeira`)* para não ceder ao impulso. |
| **III. Confluência** | Coordenação silenciosa com outros conectados (**`+2`** em Iniciativa e Flanqueio quando juntos) e **`+3`** em testes de CON contra *Golpe Devastador* e *Exaustão*. | Fronteiras pessoais se dissolvem; agir diretamente contra uma colônia ou emissário exige **SAB CD 17** *(soma `Fé Verdadeira`)*. |
| **IV. Entrega** | Participação plena na memória coletiva; imune a medo comum e recupera `+1d6` PV extras em descansos perto de uma colônia. | O indivíduo já não consegue recusar diretivas centrais do Regente *(pode ser aceita voluntariamente por NPCs; **para PJs, jamais ocorre sem aviso claro e acordo prévio com o jogador**)*. |

- **Remoção do Simbionte *(Custo Físico e Dramático)***: nos **Estágios I e II**, a extração é viável por **cirurgia especializada** (*Medicina & Cirurgia CD 20*, reduzida para `17` com extratos da *Ilha das Safiras* ou rito de *Fé Verdadeira*; causa `2d6` de dano e exige 1 semana de repouso). No **Estágio III**, exige cirurgia extrema (`CD 25`) + separação da influência de adamante; no **Estágio IV** ou em **Despertos de Thanatos**, a remoção simples pode ser fatal sem o método multicultural desenvolvido em campanha. Além do risco físico, o hospedeiro perde subitamente o conforto e as vozes de entes queridos que só ouvia pela Comunhão.
