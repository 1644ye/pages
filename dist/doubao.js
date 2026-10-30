'use strict';
function initDoubao(){
  const button=document.getElementById('openDoubao'), panel=document.getElementById('doubaoPanel'), frame=document.getElementById('doubaoFrame'), layout=document.getElementById('promptConversation');
  function toggle(open){
    panel.hidden=!open;
    layout.classList.toggle('conversation-open',open);
    button.setAttribute('aria-expanded',String(open));
    button.textContent=open?'收起豆包对话':'打开豆包对话';
    // Load only after a user click. Hiding preserves the live iframe and its session.
    if(open&&!frame.getAttribute('src'))frame.src='https://www.doubao.com/chat/';
  }
  button.onclick=()=>toggle(panel.hidden);
  document.getElementById('closeDoubao').onclick=()=>toggle(false);
}
if(typeof document.querySelectorAll==='function')initDoubao();
