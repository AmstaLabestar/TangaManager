document.addEventListener('DOMContentLoaded', function(){
  // small interactive touches: fade-in rows
  document.querySelectorAll('.row-fade').forEach((r, i)=>{
    r.style.opacity = 0; r.style.transform = 'translateY(6px)';
    setTimeout(()=>{ r.style.transition = 'opacity .45s ease, transform .45s cubic-bezier(.2,.9,.3,1)'; r.style.opacity=1; r.style.transform='translateY(0)'; }, 80*i);
  });

  // graceful click ripple for buttons (lightweight)
  document.querySelectorAll('.btn').forEach(btn=>{
    btn.addEventListener('click', e=>{
      const r=document.createElement('span');
      r.className='ripple'; r.style.left=(e.offsetX-8)+'px'; r.style.top=(e.offsetY-8)+'px';
      btn.appendChild(r); setTimeout(()=>r.remove(),600);
    });
  });
});
