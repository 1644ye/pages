import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {dirname,join,resolve,basename} from 'node:path';
import {fileURLToPath} from 'node:url';
import {randomUUID} from 'node:crypto';
import {resolveDshHome} from '@deepseek-ai/dsh-home-paths';
import {DshAdapter} from './adapter.mjs';
import {Tasks} from './tasks.mjs';
import {Store} from './storage.mjs';
import {expandTemplate,validateContent,generationPrompt,revisionPrompt} from '../shared/content.mjs';
import {Updater} from './updater.mjs';
import {Exporter} from './exporter.mjs';
export const name='page-studio';
export const inject=['webServer','connection','agents','agentDefaultModel','llm','profileContext','pluginManager'];
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const meta=JSON.parse(await readFile(join(root,'package.json'),'utf8'));
export const instances=new Map();
async function body(req){let value='';for await(const chunk of req){value+=chunk;if(Buffer.byteLength(value)>2_000_000)throw Error('请求过大')}return value?JSON.parse(value):{}}
export async function apply(ctx){
  const profile=basename(ctx.profileContext.dir);
  const store=await new Store(join(resolveDshHome(),'page-studio',profile)).init();
  const adapter=new DshAdapter(ctx),exporter=await new Exporter(root,store).init(),tasks=new Tasks(adapter,store,exporter);
  const updater=new Updater(ctx,store,meta,()=>!!tasks.active||exporter.running>0,root);
  await updater.init();
  function json(res,value,status=200){res.writeHead(status,{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});res.end(JSON.stringify(value))}
  ctx.effect(()=>ctx.webServer.register({kind:'prefix',path:'/page-studio',handler:async(req,res)=>{
    const admission=ctx.connection.admit(req);if('rejection' in admission){res.writeHead(admission.rejection);res.end('需要先登录 DSH');return}
    try{
      const url=new URL(req.url,'http://localhost'),path=url.pathname.slice('/page-studio'.length);
      if(path.startsWith('/api/')){
        if(req.method==='GET'&&/^\/api\/files\/Pages-and-Menus-[a-f0-9-]{36}\.xlsx$/.test(path)){const name=path.split('/').at(-1),bytes=await readFile(join(exporter.dir,name));res.writeHead(200,{'Content-Type':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet','Content-Disposition':'attachment; filename="'+name+'"','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});res.end(bytes);return}
        if(req.method!=='GET'&&req.headers['x-page-studio']!=='1')return json(res,{error:'缺少请求标识'},403);
        if(req.method==='GET'&&path==='/api/state')return json(res,{version:meta.version,host:'0.2.0-rc.2',profile,models:adapter.models(),sessions:ctx.agents.list().map(a=>({id:a.id,status:a.status,provider:a.options.provider,model:a.options.model})),prompts:store.value.prompts,history:store.value.history,settings:store.value.settings,update:updater.status});
        if(req.method==='GET'&&path==='/api/models')return json(res,await adapter.modelOptions(url.searchParams.get('provider')));
        if(req.method==='GET'&&path.startsWith('/api/tasks/')){const task=tasks.tasks.get(path.split('/').at(-1));return json(res,tasks.view(task)||{error:'任务不存在'},task?200:404)}
        const input=await body(req);
        if(path==='/api/generate'&&req.method==='POST')return json(res,tasks.start(input),202);
        if(path==='/api/export'&&req.method==='POST'){const result=store.value.history.find(h=>h.requestId===input.requestId&&h.revision===input.revision&&h.state==='completed'&&h.kind==='pages');if(!result)throw Error('没有找到已完成且验证通过的精确结果版本');return json(res,await exporter.create(result,false,input.published!==false))}
        if(path==='/api/cancel'&&req.method==='POST')return json(res,{cancelled:tasks.cancel(input.requestId)});
        if(path==='/api/prompts'&&req.method==='POST'){
          if(input.remove){store.value.prompts=store.value.prompts.filter(p=>p.id!==input.id)}else{
            if(typeof input.title!=='string'||typeof input.content!=='string'||!input.title.trim()||input.content.length>110000)throw Error('提示词标题/内容无效');
            const current=store.value.prompts.find(p=>p.id===input.id);const item={id:current?.id||randomUUID(),title:input.title,content:input.content,defaults:input.defaults||{},tags:input.tags||[],version:(current?.version||0)+1};
            store.value.prompts=store.value.prompts.filter(p=>p.id!==item.id);store.value.prompts.push(item);
          }await store.save();return json(res,store.value.prompts);
        }
        if(path==='/api/preview'&&req.method==='POST')return json(res,{text:expandTemplate(input.content,input.variables||{},input.defaults||{})});
        if(path==='/api/compose'&&req.method==='POST')return json(res,{text:input.current?revisionPrompt(input.current,input.input,input.change):generationPrompt(input.input),selection:adapter.models().selected});
        if(path==='/api/revisions'&&req.method==='POST'){
          validateContent(input.content);if(!store.value.history.some(h=>h.requestId===input.requestId))throw Error('原始任务不存在');
          const original=store.value.history.find(h=>h.requestId===input.requestId&&h.kind==='pages');const version={requestId:input.requestId,revision:randomUUID(),state:'completed',kind:'pages',content:input.content,sessionId:original?.sessionId,snapshot:original?.snapshot,edited:true,createdAt:new Date().toISOString()};await store.history(version);return json(res,version);
        }
        if(path==='/api/settings'&&req.method==='POST'){if(input.repository!==undefined&&!/^(?:|[\w.-]+\/[\w.-]+)$/.test(input.repository))throw Error('仓库应为 owner/repo');if(updater.status.state==='pending-restart')throw Error('存在待生效更新，暂不能修改更新来源');store.value.settings={...store.value.settings,...Object.fromEntries(['autoCheck','autoInstall','repository','channel'].filter(k=>k in input).map(k=>[k,input[k]]))};await store.save();return json(res,store.value.settings)}
        if(path==='/api/update/check'&&req.method==='POST'){await updater.check();return json(res,updater.status)}
        if(path==='/api/update/install'&&req.method==='POST'){await updater.install();return json(res,updater.status)}
        if(path==='/api/activity'&&req.method==='POST'){updater.activity(input.clientId,input);return json(res,{ok:true})}
        return json(res,{error:'未知操作'},404);
      }
      const file=path===''||path==='/'?'index.html':decodeURIComponent(path.slice(1));
      if(!/^[\w.-]+$/.test(file))throw Error('不允许的资源路径');
      const content=await readFile(join(root,'web',file));
      res.writeHead(200,{'Content-Type':file.endsWith('.js')?'text/javascript; charset=utf-8':file.endsWith('.css')?'text/css; charset=utf-8':'text/html; charset=utf-8','Cache-Control':'no-store','Content-Security-Policy':"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; frame-src 'self' about:; object-src 'none'; base-uri 'none'",'X-Content-Type-Options':'nosniff'});res.end(content);
    }catch(e){json(res,{error:e.message},400)}
  }}),'page-studio routes');
  instances.set(profile,{store,tasks,adapter,updater,exporter});
  ctx.effect(()=>{updater.start();return async()=>{instances.delete(profile);updater.dispose();await tasks.dispose();await adapter.dispose();await store.chain}},'page-studio lifecycle');
  // No paid generation in a health check. Contract module and user storage are checked on load.
  await writeFile(join(store.dir,'health.json'),JSON.stringify({version:meta.version,pid:process.pid,at:Date.now(),healthy:true}));
  await updater.confirmHealth();
  ctx.logger.info('Page Studio loaded '+meta.version+' (DSH 0.2.0-rc.2)');
}
