'use strict';
const APP_VERSION='2026.10.30.2';
function initUpdates(){
  const status=document.getElementById('updateStatus'), check=document.getElementById('checkUpdate'), install=document.getElementById('installUpdate');
  let latest;
  const local=location.protocol==='http:'&&location.hostname==='127.0.0.1';
  document.getElementById('appVersion').textContent=APP_VERSION;
  async function api(path,body={}){
    const response=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body),signal:AbortSignal.timeout(120000)});
    const result=await response.json();if(!response.ok)throw Error(result.error||'请求失败');return result;
  }
  check.onclick=async()=>{
    check.disabled=true;install.hidden=true;status.textContent='正在检查 GitHub 正式发布…';
    try{
      if(local){latest=await api('/api/update-check')}
      else{
        const response=await fetch('https://api.github.com/repos/1644ye/pages/releases/latest',{signal:AbortSignal.timeout(20000)});
        if(!response.ok)throw Error('GitHub 暂时不可用或请求过于频繁');
        const release=await response.json(),version=release.tag_name.replace(/^offline-v/,'');
        if(!/^\d{4}\.\d{2}\.\d{2}(\.\d+)?$/.test(version))throw Error('最新发布不是可识别的离线版本');
        const key=v=>v.split('.').map(x=>x.padStart(8,'0')).concat(['00000000']).slice(0,4).join('.');
        latest={available:key(version)>key(APP_VERSION),latest:version,tag:release.tag_name};
      }
      status.textContent=latest.available?`发现新版 ${latest.latest}。${local?'点击下方按钮下载并更新，更新期间请勿编辑。':'自动更新需通过 start-icon-tool.cmd 启动；也可点击 GitHub 查看并下载。'}`:`当前 ${APP_VERSION}，GitHub 正式版 ${latest.latest}，暂无更新。`;
      install.hidden=!latest.available||!local;
    }catch(error){status.textContent='检查失败：'+error.message+'。可点击 GitHub 链接手动查看。'}
    finally{check.disabled=false}
  };
  function snapshot(){
    const fields=[...document.querySelectorAll('input,textarea')].filter(el=>el.type!=='file').map(el=>({id:el.id,name:el.name,value:el.value,checked:el.checked}));
    sessionStorage.setItem('pageStudioUpdateDraft',JSON.stringify({fields,data,selected}));
  }
  install.onclick=async()=>{
    install.disabled=true;check.disabled=true;
    try{
      snapshot();status.textContent='正在下载并校验新版，完成后自动重启并恢复当前内容…';
      await api('/api/update-install',{tag:latest.tag});
      let version;
      for(let i=0;i<60;i++){
        await new Promise(resolve=>setTimeout(resolve,1000));
        try{const response=await fetch('/api/version',{cache:'no-store',signal:AbortSignal.timeout(1500)});if(response.ok){version=await response.json();if(version.version===latest.latest){location.reload();return}}}catch{}
      }
      throw Error('新版未能启动，已尝试恢复旧版。请重新运行启动脚本；当前内容仍保存在本页');
    }catch(error){status.textContent='更新未完成：'+error.message}
    finally{install.disabled=false;check.disabled=false}
  };
  (async()=>{
    try{
      const saved=sessionStorage.getItem('pageStudioUpdateDraft');if(!saved)return;
      const draft=JSON.parse(saved);
      if(draft.data){await load(draft.data);selected=draft.selected||0;render()}
      for(const field of draft.fields){
        const el=field.id?document.getElementById(field.id):[...document.getElementsByName(field.name)].find(el=>el.value===field.value);
        if(el){el.value=field.value;el.checked=field.checked}
      }
      document.getElementById('promptOptions').dispatchEvent(new Event('change',{bubbles:true}));
      sessionStorage.removeItem('pageStudioUpdateDraft');status.textContent='已启动版本 '+APP_VERSION+'，并恢复更新前的输入和页面内容。';
    }catch{status.textContent='草稿恢复失败，浏览器中仍保留备份，请暂勿关闭此标签页。'}
  })();
}
if(typeof document.querySelectorAll==='function')initUpdates();
