'use strict';
const workspaceClientId=crypto.randomUUID();
const api=async(path,body)=>{if(path==='activity')body={...body,clientId:workspaceClientId};const response=await fetch('/page-studio/api/'+path,{method:body===undefined?'GET':'POST',headers:{'Content-Type':'application/json','X-Page-Studio':'1'},body:body===undefined?undefined:JSON.stringify(body)});const value=await response.json();if(!response.ok)throw Error(value.error||'HTTP '+response.status);return value};
let hostState,currentTask,currentRevision,dirty=false,queuedResult,exportedTasks=new Set(),pollTimer;
function userInput(){return inputs()}
function selectedModel(){const [provider,model]=$('dshModel').value.split('|');const old=hostState.models.selected;return{provider,model,...old.provider===provider&&old.model===model&&old.reasoningEffort?{reasoningEffort:old.reasoningEffort}:{}}}
function targetSession(){return $('sessionId').value.trim()||undefined}
function taskInput(autoExport=false){return{kind:'pages',input:userInput(),selection:selectedModel(),sessionId:targetSession(),autoExport,published:$('published').checked}}
async function showPreview(){try{const payload=taskInput();const preview=await api('compose',payload);$('sendPreview').value=preview.text;$('contextInfo').textContent=`模型：${payload.selection.provider} / ${payload.selection.model}；会话：${payload.sessionId||'新建专用会话'}；材料：仅当前表单（现有会话仅在明确填写 ID 后使用其历史）。`;}catch(e){setStatus(e.message)}}
function setRunning(running){$('generate').disabled=running;$('generateExport').disabled=running;$('runPrompt').disabled=running;$('cancelTask').disabled=!running;$('continueTask').disabled=running}
async function begin(payload){if(currentTask&&['running','pending','repairing'].includes(currentTask.state))throw Error('已有活动任务');$('sendPreview').value=(payload.kind==='pages'?(await api('compose',payload)).text:payload.prompt);currentTask=await api('generate',payload);$('taskId').textContent=`请求 ${currentTask.requestId}`;$('sessionId').value=currentTask.sessionId||payload.sessionId||'';setRunning(true);poll()}
async function applyResult(task){
  await load(task.content);currentRevision={requestId:task.requestId,revision:task.revision,content:structuredClone(task.content)};dirty=false;
  $('historySelect').value='';$('sessionId').value=task.sessionId||'';
  if(task.autoExport&&!exportedTasks.has(task.requestId+':'+task.revision)){
    if(task.export?.state!=='completed'){setStatus('正文已完成，但导出失败：'+(task.export?.error||'没有成功文件')+'；可点击导出重试，不再调用模型。');return}
    exportedTasks.add(task.requestId+':'+task.revision);deliver(task.export,true);
  }else setStatus('生成完成，已保存结果版本；可以编辑或导出。');
  await refreshState();
}
async function poll(){clearTimeout(pollTimer);if(!currentTask)return;try{
  const task=await api('tasks/'+currentTask.requestId);if(task.requestId!==currentTask.requestId)return;currentTask=task;
  $('streamText').textContent=task.text||'';$('thinkingText').textContent=task.thinking||'';$('taskId').textContent=`${task.requestId} · ${task.state} · attempt ${task.attempt} · ${task.sessionId||''}`;
  if(['pending','running','repairing','exporting'].includes(task.state)){setStatus(task.state==='repairing'?'正在进行唯一一次结构修复…':task.state==='exporting'?'正文验证通过，正在生成本次 XLSX…':'DSH 正在生成…');pollTimer=setTimeout(poll,500);return}
  setRunning(false);
  if(task.state==='completed'){
    if(task.kind==='pages'){if(dirty){queuedResult=task;$('applyNewResult').hidden=false;setStatus('新结果已完成；当前编辑尚未保存。请先保存编辑，再应用新结果。')}else await applyResult(task)}
    else{$('promptAnswer').value=task.content.text;setStatus('提示词已由 DSH 执行完成，结果保留在提示词结果区。');await refreshState()}
  }else setStatus(task.error||'任务已取消；未触发自动导出。');
}catch(error){setStatus('任务查询失败：'+error.message+'；可在历史中恢复，未自动重发或导出。');setRunning(false)}}
$('form').onsubmit=async e=>{e.preventDefault();try{await begin(taskInput(false))}catch(error){setStatus(error.message)}};
$('generateExport').onclick=async()=>{try{await begin(taskInput(true))}catch(error){setStatus(error.message)}};
$('previewSend').onclick=showPreview;
$('cancelTask').onclick=async()=>{if(currentTask){await api('cancel',{requestId:currentTask.requestId});currentTask.autoExport=false;setStatus('已请求终止 DSH 底层任务；不会自动导出。')}};
$('editor').addEventListener('input',()=>{dirty=true;api('activity',{dirty:true}).catch(()=>{})});
const oldSave=$('saveEdit').onclick;
$('saveEdit').onclick=async()=>{try{oldSave();if(!currentRevision)return;const content={...currentRevision.content,pages:data.pages.filter(p=>p.handle!=='contact-us').map(p=>structuredClone(p))};const version=await api('revisions',{requestId:currentRevision.requestId,content});currentRevision=version;dirty=false;await api('activity',{dirty:false});await refreshState();setStatus('当前编辑已保存为新版本。')}catch(error){setStatus('保存失败：'+error.message)}};
$('applyNewResult').onclick=async()=>{if(dirty){setStatus('请先保存编辑或重新载入已保存版本');return}if(queuedResult){const task=queuedResult;queuedResult=null;$('applyNewResult').hidden=true;await applyResult(task)}};
$('continueTask').onclick=async()=>{try{if(dirty)throw Error('请先保存编辑');if(!currentRevision)throw Error('请先生成或载入结果');if(!$('changeRequest').value.trim())throw Error('请填写修改要求');const input=taskInput(false);input.current={revision:currentRevision.revision,content:currentRevision.content};input.change=$('changeRequest').value;input.sessionId=targetSession();await begin(input)}catch(error){setStatus(error.message)}};
$('historySelect').onchange=async()=>{if(dirty){setStatus('请先保存编辑');return}const h=hostState.history.find(x=>x.revision===$('historySelect').value);if(h?.kind==='pages'&&h.content){await load(h.content);currentRevision=h;dirty=false;$('sessionId').value=h.sessionId||'';for(const[id,value]of Object.entries(h.snapshot?.input||{})){if($(id)&&typeof value==='string')$(id).value=value}}};
function deliver(record,automatic=false){const a=$('fileReady');a.href=record.downloadUrl;a.download=record.name;a.hidden=false;a.textContent='文件已生成：点击下载 '+record.name;if(automatic)a.click();setStatus(automatic?'XLSX 已由宿主保存并发起下载；如浏览器限制自动下载，请点击文件链接。':'当前精确结果版本的 XLSX 已生成，请点击文件链接下载。')}
const legacyExport=$('export').onclick;
$('export').onclick=async()=>{try{if(dirty)throw Error('请先保存编辑后再导出');if(!currentRevision){legacyExport();return}deliver(await api('export',{requestId:currentRevision.requestId,revision:currentRevision.revision,published:$('published').checked}),true)}catch(error){setStatus('导出失败：'+error.message)}};
function variables(){return JSON.parse($('promptVariables').value||'{}')}
$('savePrompt').onclick=async()=>{try{await api('prompts',{id:$('savedPrompt').value||undefined,title:$('promptTitle').value,content:$('promptOutput').value,defaults:JSON.parse($('promptDefaults').value||'{}'),tags:$('promptTags').value.split(',').map(x=>x.trim()).filter(Boolean)});await refreshState();setStatus('提示词已保存到用户数据区')}catch(error){setStatus(error.message)}};
$('deletePrompt').onclick=async()=>{if($('savedPrompt').value){await api('prompts',{remove:true,id:$('savedPrompt').value});await refreshState()}};
$('savedPrompt').onchange=()=>{const p=hostState.prompts.find(p=>p.id===$('savedPrompt').value);if(p){$('promptTitle').value=p.title;$('promptOutput').value=p.content;$('promptDefaults').value=JSON.stringify(p.defaults);$('promptTags').value=p.tags.join(',')}};
async function expandedPrompt(){return(await api('preview',{content:$('promptOutput').value,variables:variables(),defaults:JSON.parse($('promptDefaults').value||'{}')})).text}
$('previewPrompt').onclick=async()=>{try{$('sendPreview').value=await expandedPrompt();setStatus('已展示变量展开后的实际发送内容。')}catch(error){setStatus(error.message)}};
$('runPrompt').onclick=async()=>{try{const saved=hostState.prompts.find(p=>p.id===$('savedPrompt').value);await begin({kind:'prompt',prompt:await expandedPrompt(),promptId:saved?.id,promptVersion:saved?.version,variables:variables(),selection:selectedModel(),sessionId:targetSession(),context:'only expanded prompt + explicitly chosen session'})}catch(error){setStatus(error.message)}};
$('saveSettings').onclick=async()=>{try{await api('settings',{repository:$('releaseRepository').value.trim(),autoCheck:$('autoCheck').checked,autoInstall:$('autoInstall').checked,channel:$('updateChannel').value});await refreshState()}catch(error){setStatus(error.message)}};
$('checkUpdate').onclick=async()=>{try{await api('update/check',{});await refreshState()}catch(error){setStatus('更新检查失败：'+error.message);await refreshState()}};
$('installUpdate').onclick=async()=>{try{await api('update/install',{});await refreshState()}catch(error){setStatus('安装失败：'+error.message)}};
async function refreshState(){
  hostState=await api('state');$('hostVersion').textContent=`DSH ${hostState.host} · 插件 ${hostState.version} · Profile ${hostState.profile}`;
  const previous=$('dshModel').value;$('dshModel').replaceChildren();const selected=hostState.models.selected;
  const opt=document.createElement('option');opt.value=selected.provider+'|'+selected.model;opt.textContent=opt.value+'（宿主默认）';$('dshModel').append(opt);
  for(const p of hostState.models.providers.filter(p=>/deepseek/i.test(p.id))){try{const models=await api('models?provider='+encodeURIComponent(p.id));for(const model of models){const value=p.id+'|'+model.id;if(value===opt.value)continue;const option=document.createElement('option');option.value=value;option.textContent=value;$('dshModel').append(option)}}catch(error){setStatus('读取模型列表失败：'+error.message)}}
  if([...$('dshModel').options].some(o=>o.value===previous))$('dshModel').value=previous;
  for(const[id,items,label]of [['savedPrompt',hostState.prompts,p=>p.title+' · v'+p.version],['historySelect',hostState.history.filter(p=>p.state==='completed'&&p.kind==='pages'),p=>(p.edited?'编辑':'生成')+' · '+p.createdAt+' · '+p.revision?.slice(0,8)]]){const select=$(id),old=select.value;select.replaceChildren(new Option('选择…',''));for(const p of items)select.append(new Option(label(p),id==='savedPrompt'?p.id:p.revision));select.value=old}
  $('releaseRepository').value=hostState.settings.repository;$('autoCheck').checked=hostState.settings.autoCheck;$('autoInstall').checked=hostState.settings.autoInstall;$('updateChannel').value=hostState.settings.channel;showUpdate(hostState.update);
}
function showUpdate(update){$('updateState').textContent=JSON.stringify(update,null,2);$('updateNotice').hidden=!['pending-restart','recovered','install-failed','check-failed','manual-review'].includes(update.state);$('updateNotice').textContent=update.state==='pending-restart'?'新版 '+update.installedVersion+' 已安装。请先保存工作，然后退出并重新打开 DSH；当前仍运行旧版。':update.state==='recovered'?'新版启动失败，已恢复旧版；失败版本不会再次自动安装。':update.state==='manual-review'?'发现更新，但该版本尚未满足自动安装条件，请查看更新设置。':update.error||''}
const updateTimer=setInterval(()=>api('state').then(s=>showUpdate(s.update)).catch(()=>{}),15000);
window.addEventListener('beforeunload',()=>clearInterval(updateTimer));
window.addEventListener('beforeunload',()=>{clearTimeout(pollTimer)});
setRunning(false);refreshState().catch(error=>setStatus('无法连接 DSH：'+error.message));
