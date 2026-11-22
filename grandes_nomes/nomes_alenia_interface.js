
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
