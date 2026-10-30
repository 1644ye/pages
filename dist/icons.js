'use strict';
function initIconTool(){
  const el=id=>document.getElementById(id), results=el('iconResults'), status=el('iconStatus');
  const blobs=[];
  function clear(){blobs.splice(0).forEach(URL.revokeObjectURL);results.replaceChildren()}
  async function request(path,url){
    const response=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url}),signal:AbortSignal.timeout(25000)});
    if(!response.ok){let message='读取失败';try{message=(await response.json()).error||message}catch{}throw Error(message)}
    return response;
  }
  el('extractIcons').onclick=async()=>{
    if(location.protocol==='file:' || location.hostname!=='127.0.0.1'){
      status.textContent='请先关闭此页，运行压缩包内的 start-icon-tool.cmd（需要 Python 3.10+），在自动打开的页面中使用此功能。Mac / Linux 可运行 python3 icon-server.py。';return;
    }
    let url=el('iconWebsite').value.trim();
    if(!url){status.textContent='请填写网站地址。';return}
    if(!/^https?:\/\//i.test(url))url='https://'+url;
    try{const parsed=new URL(url);if(!['https:','http:'].includes(parsed.protocol))throw Error()}catch{status.textContent='请输入有效的 http:// 或 https:// 网站地址。';return}
    clear();el('extractIcons').disabled=true;status.textContent='正在读取网站的图标声明…';
    try{
      const data=await (await request('/api/icons',url)).json();
      status.textContent=`找到 ${data.icons.length} 个图标或候选地址。点击“预览并下载”读取原始图片；不改尺寸和格式。`;
      data.icons.forEach(icon=>{
        const card=document.createElement('div');card.className='icon-card';
        const heading=document.createElement('b');heading.textContent=`${icon.kind} · ${icon.sizes}`;
        const address=document.createElement('input');address.readOnly=true;address.value=icon.url;address.setAttribute('aria-label','图标地址');
        const preview=document.createElement('img');preview.alt='网站图标预览';preview.hidden=true;
        const button=document.createElement('button');button.type='button';button.className='secondary';button.textContent='预览并下载';
        const note=document.createElement('p');note.className='hint';
        let blobUrl, extension;
        button.onclick=async()=>{
          button.disabled=true;note.textContent='正在下载图标…';
          try{
            if(!blobUrl){const response=await request('/api/icon-file',icon.url);extension=response.headers.get('X-Icon-Extension')||'ico';blobUrl=URL.createObjectURL(await response.blob());blobs.push(blobUrl);preview.src=blobUrl;preview.hidden=false}
            const link=document.createElement('a');link.href=blobUrl;link.download=`website-icon.${extension}`;link.click();
            button.textContent='再次下载';note.textContent='已读取原始图标并发起下载。';
          }catch(error){note.textContent='图标读取失败：'+error.message+'。可复制上方地址在浏览器打开；默认路径候选可能不存在。'}
          finally{button.disabled=false}
        };
        card.append(heading,address,preview,button,note);results.append(card);
      });
    }catch(error){status.textContent='提取失败：'+error.message+'。请确认从启动脚本打开工具、网络可用且网站无需登录；部分网站会拦截自动访问。'}
    finally{el('extractIcons').disabled=false}
  };
  window.addEventListener('beforeunload',()=>blobs.forEach(URL.revokeObjectURL));
}
if(typeof document.querySelectorAll==='function')initIconTool();
