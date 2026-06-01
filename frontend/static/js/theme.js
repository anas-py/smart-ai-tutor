// Smart AI Tutor — Theme Switcher
(function(){
  var KEY = 'sat_theme';
  function apply(t){
    document.documentElement.setAttribute('data-theme', t);
    localStorage.setItem(KEY, t);
    document.querySelectorAll('.theme-label').forEach(function(el){
      el.textContent = t === 'light' ? 'Dark Mode' : 'Light Mode';
    });
  }
  function toggle(){
    apply(document.documentElement.getAttribute('data-theme')==='light' ? 'dark' : 'light');
  }
  function wire(){
    document.querySelectorAll('[data-theme-toggle]').forEach(function(btn){
      btn.addEventListener('click', function(e){ e.preventDefault(); toggle(); });
    });
  }
  apply(localStorage.getItem(KEY) || 'dark');
  if(document.readyState==='loading'){
    document.addEventListener('DOMContentLoaded', wire);
  } else { wire(); }
  window.toggleTheme = toggle;
})();