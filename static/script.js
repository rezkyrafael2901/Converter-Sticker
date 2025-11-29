document.addEventListener('DOMContentLoaded', () => {
  const themeSwitch = document.getElementById('themeSwitch');
  const stored = localStorage.getItem('theme') || 'dark';
  if(stored === 'light'){ document.body.classList.add('light-mode'); document.body.classList.remove('dark-mode'); themeSwitch.checked = true; } else { document.body.classList.add('dark-mode'); document.body.classList.remove('light-mode'); }

  themeSwitch.addEventListener('change', ()=>{ if(themeSwitch.checked){ document.body.classList.add('light-mode'); document.body.classList.remove('dark-mode'); localStorage.setItem('theme','light'); } else { document.body.classList.add('dark-mode'); document.body.classList.remove('light-mode'); localStorage.setItem('theme','dark'); } });

  document.querySelectorAll('.tab').forEach(btn=>{ btn.addEventListener('click', ()=>{ document.querySelectorAll('.tab').forEach(b=>b.classList.remove('active')); btn.classList.add('active'); const t=btn.dataset.tab; document.querySelectorAll('.tabpanel').forEach(p=>p.classList.remove('active')); document.getElementById(t).classList.add('active'); // hide downloads
    document.getElementById('dlT2W').classList.add('hidden'); document.getElementById('dlW2T').classList.add('hidden'); document.getElementById('dlZIP').classList.add('hidden'); }); });

  async function postFile(url, formData, loaderEl){ loaderEl.style.display='inline-block'; try{ const res = await fetch(url,{method:'POST',body:formData}); if(!res.ok){ const txt = await res.text(); alert('Convert failed: '+txt); return null; } const blob = await res.blob(); return blob; }catch(e){ alert('Network error: '+e); return null; }finally{ loaderEl.style.display='none'; } }

  // T2W
  const formT2W = document.getElementById('formT2W');
  formT2W.addEventListener('submit', async (e)=>{
    e.preventDefault();
    const file = document.getElementById('inputT2W').files[0];
    if(!file) return alert('Select a .webp file');
    const fd = new FormData(); fd.append('file', file);
    const blob = await postFile('/api/t2w', fd, document.getElementById('loaderT2W'));
    if(!blob) return;
    const url = URL.createObjectURL(blob);
    const a = document.getElementById('dlT2W'); a.href = url; a.download = 'sticker_whatsapp.webp'; a.classList.remove('hidden');
    // auto-open little download confirmation (optional)
  });

  // W2T
  const formW2T = document.getElementById('formW2T');
  formW2T.addEventListener('submit', async (e)=>{
    e.preventDefault();
    const file = document.getElementById('inputW2T').files[0];
    if(!file) return alert('Select a .webp file');
    const fd = new FormData(); fd.append('file', file);
    const blob = await postFile('/api/w2t', fd, document.getElementById('loaderW2T'));
    if(!blob) return;
    const url = URL.createObjectURL(blob);
    const a = document.getElementById('dlW2T'); a.href = url; a.download = 'sticker_telegram.webp'; a.classList.remove('hidden');
  });

  // ZIP batch
  const formZIP = document.getElementById('formZIP');
  formZIP.addEventListener('submit', async (e)=>{
    e.preventDefault();
    const file = document.getElementById('inputZIP').files[0];
    if(!file) return alert('Select a .zip file');
    const fd = new FormData(); fd.append('zipfile', file);
    const blob = await postFile('/api/convert_zip', fd, document.getElementById('loaderZIP'));
    if(!blob) return;
    const url = URL.createObjectURL(blob);
    const a = document.getElementById('dlZIP'); a.href = url; a.download = 'whatsapp_pack.zip'; a.classList.remove('hidden');
  });

});
