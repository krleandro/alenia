# Manutenção do Tomo XIII

O compêndio foi criado como edição de trabalho do Mestre. O HTML local contém os perfis completos, inclusive bastidores, e não possui criptografia. Os demais livros e seus cofres não foram regenerados.

## Fontes editáveis

- `nomes_alenia_dados.py`: 45 perfis anteriores, incluindo o registro especial da Sombra.
- `nomes_alenia_exemplos.py`: 19 nomes completos da onomástica, agora desenvolvidos.
- `nomes_alenia_novos.py`: 36 novas figuras ou nomes propostos para papéis antes anônimos.
- `nomes_alenia_editorial.md`: critérios, linhagens, relações, continuidade e situações de jogo.

Execute `python construir_grandes_nomes.py` nesta pasta para atualizar o Markdown, o HTML e o catálogo JSON. Os códigos N001–N100 dependem da ordem dos perfis: acrescente novas fichas ao fim, sem reordenar os blocos existentes. As duas edições de leitura são saídas geradas; incorpore alterações de conteúdo às fontes acima antes de reconstruir.

`nomes_alenia_catalogo.json` registra campos das fichas, origem editorial, referências localizadas e hashes dos doze tomos usados no levantamento. As linhas referem-se à edição lida e podem mudar após novas edições. Referências a papéis anônimos são identificadas como contextuais, sem fingir que o nome proposto já aparecia na fonte.

O Tomo XIII está registrado em `build_livros_html.py` com `gm_only=True`, para seguir o fluxo de volumes reservados numa futura geração integral. A fonte está nesta pasta, no caminho `livros_html/13_Grandes_Nomes_e_Feitos_de_Alenia.md` relativo à raiz de Alenia. O gerador integral não foi executado nesta tarefa. Como nos demais tomos, a proteção da geração integral depende da configuração de senha já utilizada pelo projeto; a edição local de trabalho não equivale a esse fluxo.

## Verificações desta edição

Conferidos: cem códigos únicos, cem nomes distintos, todos os campos preenchidos, referências literais para os 64 nomes anteriores ou exemplificados, arquivos e âncoras locais do HTML, sintaxe Python e JavaScript. As correspondências de fontes não transformam os detalhes biográficos novos em fatos dos volumes antigos. Não houve validação visual da página num navegador nesta edição.
