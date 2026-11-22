"""Build the local GM working edition, without rebuilding other books or their vaults."""
from pathlib import Path
import collections
import hashlib
import html
import json
import re

import sys
ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(REPO_ROOT / 'livros_html'))

from nomes_alenia_dados import PROFILES as BASE, parse_rows
from nomes_alenia_exemplos import ROWS as EXAMPLES
from nomes_alenia_novos import ROWS as NEW

OUT = REPO_ROOT / '13_Grandes_Nomes_e_Feitos_de_Alenia'
GROUPS = ['Coroa e memória','Portos e regências','Matas e fronteiras','Mares e exploração',
          'Fé e conhecimento','Ofícios e trabalho','Intriga e justiça','Crime e margens',
          'Artes e cotidiano','Memórias e ameaças']
LABELS = [('origin','Origem e presença'),('lineage','Linhagem e formação'),
          ('appearance','Aparência'),('personality','Personalidade e contradição'),
          ('deeds','Feitos e legado'),('desire','Desejo ou herança em disputa'),
          ('scene','Entrada em cena e voz')]

CSS = '''
.names-mode .book-page{max-width:1080px;padding:40px 5%;overflow-wrap:anywhere}
.names-hero{border-bottom:2px solid var(--gold);padding-bottom:24px;margin-bottom:25px}
.names-hero h1{font-size:clamp(30px,5vw,52px);line-height:1.15}
.names-note{border-left:4px solid var(--crimson);padding:12px 18px;background:#7a1f1d0b}
.names-controls{display:flex;flex-wrap:wrap;gap:12px;padding:18px 0;align-items:end}
.names-controls label{display:flex;flex-direction:column;gap:5px;font-size:15px;flex:1 1 180px}
.names-controls input,.names-controls select{padding:10px;min-width:0;width:100%;font:inherit;color:var(--ink);background:var(--vellum);border:1px solid var(--gold)}
.names-card{padding:26px 0;border-top:1px solid var(--border);scroll-margin-top:75px}
.names-card h3{font-size:27px;line-height:1.25;margin-top:8px}
.names-meta{font:13px/1.6 Arial,sans-serif;color:var(--ink-soft);margin:10px 0 20px}
.names-code{font:12px Arial,sans-serif;color:var(--crimson);letter-spacing:.1em}
.names-card p{font-size:18px;line-height:1.6}.names-card p strong{color:var(--crimson-dark)}
.names-index{columns:3;column-gap:24px}.names-index a{display:block;break-inside:avoid;font-size:15px;margin:0 0 8px}
.names-editorial{margin:20px 0}.names-editorial summary{cursor:pointer;font-size:20px;font-weight:bold;color:var(--crimson)}
.names-mode [hidden]{display:none!important}.names-mode table{display:block;overflow-x:auto}
.names-stat{font-size:20px;color:var(--ink-soft)}.names-ref{font-size:14px}
@media(max-width:700px){.names-mode .book-page{padding:24px 20px}.names-index{columns:1}.names-card h3{font-size:24px}}
@media print{.names-controls,.names-back{display:none}.names-mode .book-page{padding:0;max-width:none}.names-card{break-before:page}.names-card p{font-size:11pt}.names-index{columns:2}}
'''

JS = r'''
(() => {
 const root=document.getElementById('names-root'); if(!root)return;
 const cards=[...root.querySelectorAll('.names-card')];
 const q=document.getElementById('names-query'), sphere=document.getElementById('names-sphere'), kind=document.getElementById('names-kind');
 const norm=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
 function filter(){let count=0;const query=norm(q.value.trim());
  cards.forEach(c=>{c.hidden=!!((sphere.value&&c.dataset.sphere!==sphere.value)||(kind.value&&c.dataset.kind!==kind.value)||(query&&!norm(c.dataset.search).includes(query)));if(!c.hidden)count++;});
  root.querySelectorAll('.names-group').forEach(g=>g.hidden=![...g.querySelectorAll('.names-card')].some(c=>!c.hidden));
  document.getElementById('names-count').textContent=`${count} de ${cards.length} perfis`;
  document.getElementById('names-empty').hidden=count!==0;
 }
 [q,sphere,kind].forEach(el=>el.addEventListener(el===q?'input':'change',filter));
 function reveal(){const id=location.hash.slice(1);const card=document.getElementById(id);if(card?.classList.contains('names-card')){q.value='';sphere.value='';kind.value='';filter();card.scrollIntoView();}}
 window.addEventListener('hashchange',reveal);filter();if(location.hash)setTimeout(reveal,50);
 window.addEventListener('beforeprint',()=>{root.querySelectorAll('[hidden]').forEach(e=>{e.dataset.printHidden='1';e.hidden=false;});});
 window.addEventListener('afterprint',()=>{root.querySelectorAll('[data-print-hidden]').forEach(e=>{delete e.dataset.printHidden;});filter();});
})();
'''

def main():
    profiles=[]
    for rows,kind in [(BASE,'Anterior desenvolvido'),(parse_rows(EXAMPLES),'Nome-modelo desenvolvido'),(parse_rows(NEW),'Nova figura ou papel nomeado')]:
        for row in rows:
            profiles.append(dict(row,code=f'N{len(profiles)+1:03}',kind=kind))
    assert len(profiles)==100 and len({p['name'] for p in profiles})==100
    assert set(p['sphere'] for p in profiles)==set(GROUPS)
    source_files={p.name[:2]:p for p in ROOT.parent.glob('[0-1][0-9]_*.md') if int(p.name[:2])<=12}
    source_text={k:p.read_text(encoding='utf-8') for k,p in source_files.items()}
    aliases={
        'Severor II Valerion':['Severor II'], 'Severor III Valerion':['Severor III'],
        'Loreo, comprador de Baldbella':['Loreo'], 'O Regente das Cinzas':['Regente das Cinzas'],
        'Aemilius de Pontáuria':['Aemilius de Pontáuria'], 'Severin da Brasa Velada':['Severin'],
    }
    for p in profiles:
        p['evidence']=[]
        for number in re.findall(r'\b(?:0[1-9]|1[0-2])\b',p['source']):
            terms=[p['name']]+aliases.get(p['name'],[])
            occurrences=[i for i,line in enumerate(source_text[number].splitlines(),1)
                         if any(term in line.replace('*','') for term in terms)]
            p['evidence'].append({'book':number,'file':source_files[number].name,'lines':occurrences,
                                  'scope':'nome e papel' if occurrences else 'papel anônimo ou referência contextual'})
    by_name={p['name']:p for p in profiles}
    pattern=re.compile('|'.join(re.escape(n) for n in sorted(by_name,key=len,reverse=True)))
    def text_linked(text,current):
        result=[];start=0
        for m in pattern.finditer(text):
            result.append(html.escape(text[start:m.start()]))
            target=by_name[m.group()]
            label=html.escape(m.group())
            result.append(label if target['code']==current else f'<a href="#{target["code"].lower()}">{label}</a>')
            start=m.end()
        result.append(html.escape(text[start:]));return ''.join(result)
    editorial=(ROOT/'nomes_alenia_editorial.md').read_text(encoding='utf-8')
    opening,appendix=editorial.split('## Relações que já produzem cenas',1)
    appendix='## Relações que já produzem cenas'+appendix
    md=[opening,'## Índice alfabético\n']
    for p in sorted(profiles,key=lambda x:x['name']):
        md.append(f'- [{p["code"]} — {p["name"]}](#{p["code"].lower()}) · {p["sphere"]} · {p["kind"]}')
    for group in GROUPS:
        md.append('\n## '+group+'\n')
        for p in [x for x in profiles if x['sphere']==group]:
            portrait_rel = f'ilustracoes/npc_{p["code"]}.jpg'
            portrait_md = [f'![Retrato {p["code"]}]({portrait_rel})\n'] if (REPO_ROOT / portrait_rel).exists() else []
            md.extend([f'<a id="{p["code"].lower()}"></a>\n',f'### {p["code"]} — {p["name"]}\n',
                       *portrait_md,
                       f'**Registro:** {p["kind"]}. **Época:** {p["period"]}.\n'])
            for key,label in LABELS:md.append(f'**{label}:** {p[key]}\n')
            refs=[f'[{e["file"]}]({e["file"]})'+(f' (linhas {", ".join(map(str,e["lines"][:8]))})' if e['lines'] else ' (papel antes anônimo)') for e in p['evidence']]
            md.append('**Base de referência:** '+('; '.join(refs) if refs else 'Criação desta edição, situada na geografia e nas instituições dos tomos II e V.')+'\n')
    md.extend([appendix,'\n## Fontes consultadas\n'])
    md.extend(f'- [{p.name}]({p.name})' for p in source_files.values())
    OUT.with_suffix('.md').write_text('\n'.join(md),encoding='utf-8')
    manifest={'edition':'418 EF — edição do Mestre','counts':dict(collections.Counter(p['kind'] for p in profiles)),
              'sources':[{'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in source_files.values()],
              'profiles':profiles}
    (ROOT/'nomes_alenia_catalogo.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'100 perfis; {len(OUT.with_suffix(".md").read_text(encoding="utf-8").split())} palavras; 12 fontes; Markdown ({OUT.with_suffix(".md").name}) e JSON gerados. Execute livros_html/build_livros_html.py com ALENIA_GM_PASSWORD para compilar o HTML criptografado.')

if __name__=='__main__':main()
