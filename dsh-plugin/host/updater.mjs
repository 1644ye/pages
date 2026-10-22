import semver from 'semver';
import {createHash,randomUUID} from 'node:crypto';
import {readFile,writeFile,mkdir,open,rm,copyFile} from 'node:fs/promises';
import {join,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawn} from 'node:child_process';
import {packDirectory,inspectArchive} from './archive.mjs';
const HOST='0.2.0-rc.2';
const digest=bytes=>createHash('sha256').update(bytes).digest('hex');
export function chooseRelease(releases,metas,current,channel='stable'){
  return releases.filter(r=>!r.draft&&(channel==='test'||!r.prerelease)).map(r=>({release:r,meta:metas.get(r.id)})).filter(x=>x.meta&&semver.valid(x.meta.version)&&semver.gt(x.meta.version,current)).sort((a,b)=>semver.rcompare(a.meta.version,b.meta.version));
}
export class Updater{
  constructor(ctx,store,meta,busy,root){Object.assign(this,{ctx,store,meta,busy,root});this.status={state:'source-unconfigured',runningVersion:meta.version,lastChecked:null};this.clients=new Map();this.etags=new Map();this.cache=new Map();this.failures=0}
  get editorDirty(){return [...this.clients.values()].some(c=>c.dirty)}
  get exporting(){return [...this.clients.values()].some(c=>c.exporting)}
  activity(clientId,value){if(typeof clientId!=='string'||clientId.length>100)throw Error('需要工作区标识');this.clients.set(clientId,{dirty:value.dirty===true,exporting:value.exporting===true})}
  async init(){this.dir=join(this.store.dir,'updates');await mkdir(this.dir,{recursive:true});try{const pending=JSON.parse(await readFile(join(this.dir,'pending.json'),'utf8'));if(pending.recovered&&pending.previous===this.meta.version){this.status={...this.status,state:'recovered',failedVersion:pending.version,installedVersion:this.meta.version};await rm(join(this.dir,'pending.json'))}else this.status={...this.status,state:pending.version===this.meta.version?'validating':'pending-restart',installedVersion:pending.version}}catch(e){if(e.code!=='ENOENT')throw e}}
  async confirmHealth(){if(this.status.state!=='validating')return;await this.store.save();this.status={...this.status,state:'activated',installedVersion:this.meta.version};await writeFile(join(this.dir,'activated.json'),JSON.stringify({version:this.meta.version,at:Date.now()}));await rm(join(this.dir,'pending.json'))}
  start(){this.timer=setInterval(()=>{if(this.store.value.settings.autoCheck)this.check().catch(()=>{})},6*60*60*1000);this.timer.unref?.();this.initial=setTimeout(()=>{if(this.store.value.settings.autoCheck)this.check().catch(()=>{})},3000);this.initial.unref?.();this.idle=setInterval(()=>{if(this.staged&&this.store.value.settings.autoInstall&&!this.busy()&&!this.editorDirty&&!this.exporting)this.install(true).catch(()=>{})},15000);this.idle.unref?.()}
  dispose(){clearInterval(this.timer);clearInterval(this.idle);clearTimeout(this.initial);this.disposed=true}
  async request(url){
    const headers={Accept:'application/vnd.github+json','User-Agent':'DSH-Page-Studio'};if(this.etags.has(url))headers['If-None-Match']=this.etags.get(url);
    const response=await fetch(url,{headers,signal:AbortSignal.timeout(15000),redirect:'error'});
    if(response.status===304)return this.cache.get(url);
    if(!response.ok)throw Error(`GitHub HTTP ${response.status}`);
    const obj=await response.json();this.cache.set(url,obj);if(response.headers.get('etag'))this.etags.set(url,response.headers.get('etag'));return obj;
  }
  async asset(url,max){let current=new URL(url);const repo=this.store.value.settings.repository;
    if(current.protocol!=='https:'||current.hostname!=='github.com'||!current.pathname.startsWith('/'+repo+'/releases/download/'))throw Error('安装资产不属于固定仓库 Release');
    for(let i=0;i<5;i++){const r=await fetch(current,{redirect:'manual',signal:AbortSignal.timeout(60000)});if([301,302,303,307,308].includes(r.status)){const next=new URL(r.headers.get('location'),current);if(next.protocol!=='https:'||!['github.com','release-assets.githubusercontent.com','objects.githubusercontent.com'].includes(next.hostname))throw Error('拒绝未知资产重定向');current=next;continue}if(!r.ok)throw Error('资产下载 HTTP '+r.status);let size=0;const chunks=[];for await(const chunk of r.body){size+=chunk.length;if(size>max)throw Error('资产超过大小限制');chunks.push(chunk)}return Buffer.concat(chunks)}throw Error('资产重定向次数过多')
  }
  async check(){
    if(this.checking||this.status.state==='pending-restart')return this.status;
    const repo=this.store.value.settings.repository;if(!repo){this.status.state='source-unconfigured';return this.status}
    if(this.retryAfter&&Date.now()<this.retryAfter){this.status.state='check-backoff';return this.status}
    this.checking=true;this.status.state='checking';
    try{
      const releases=[];for(let page=1;page<=10;page++){const part=await this.request(`https://api.github.com/repos/${repo}/releases?per_page=100&page=${page}`);releases.push(...part);if(part.length<100)break;if(page===10)throw Error('发行记录超过1000条，需收窄发布源')}
      const metas=new Map();for(const r of releases){if(r.draft||(this.store.value.settings.channel!=='test'&&r.prerelease))continue;const asset=r.assets.find(a=>a.name==='page-studio-update.json');if(!asset)continue;metas.set(r.id,JSON.parse((await this.asset(asset.browser_download_url,200000)).toString('utf8')))}
      const sorted=chooseRelease(releases,metas,this.meta.version,this.store.value.settings.channel),compatible=sorted.find(({meta:m})=>m.plugin===this.meta.name&&semver.satisfies(HOST,m.dsh,{includePrerelease:true})&&m.platform==='win32'&&m.dataSchema===1&&!this.store.value.blockedVersions.includes(m.version));
      this.status.lastChecked=new Date().toISOString();this.status.state=compatible?'update-available':sorted.length?'incompatible-update':'up-to-date';this.status.candidate=compatible?.meta||sorted[0]?.meta;delete this.status.error;this.failures=0;this.retryAfter=0;
      if(compatible){this.candidate=compatible;await this.stage();if(this.store.value.settings.autoInstall)await this.install(true)}
    }catch(error){this.status.state='check-failed';this.status.error=error.message;this.retryAfter=Date.now()+Math.min(3600000,30000*2**this.failures++);throw error}finally{this.checking=false}return this.status;
  }
  async stage(){const {release,meta:m}=this.candidate;if(release.tag_name!=='dsh-v'+m.version||!m.asset||!Number.isSafeInteger(m.size)||m.size<=0||m.size>30_000_000||!/^[a-f0-9]{64}$/.test(m.sha256))throw Error('更新元数据/标签不完整或不一致');const asset=release.assets.find(a=>a.name===m.asset);if(!asset)throw Error('发行缺少安装资产');const bytes=await this.asset(asset.browser_download_url,30_000_000);if(bytes.length!==m.size||digest(bytes)!==m.sha256)throw Error('安装包长度或 SHA-256 校验失败');const {manifest}=inspectArchive(bytes);if(manifest.name!==this.meta.name||manifest.version!==m.version||manifest.engines?.dsh!==m.dsh)throw Error('安装包身份/版本/宿主范围不符');const file=join(this.dir,m.version+'.tgz');await writeFile(file,bytes);this.staged={file,meta:m};this.status.state='staged';}
  async install(automatic=false){
    if(!this.staged||this.installing)return;
    if(this.busy()||this.editorDirty||this.exporting){this.status.state='waiting-idle';return}
    const {meta:m,file}=this.staged;
    // Compatibility alone does not prove rollback. Metadata must explicitly attest tested recovery.
    if(automatic&&(!m.recoveryTested||m.newPermissions||m.irreversibleMigration)){this.status.state='manual-review';return}
    const stagedBytes=await readFile(file);if(stagedBytes.length!==m.size||digest(stagedBytes)!==m.sha256)throw Error('暂存安装包长度或 SHA-256 校验失败');const checked=inspectArchive(stagedBytes);if(checked.manifest.name!==this.meta.name||checked.manifest.version!==m.version)throw Error('暂存包身份不符');
    if(m.irreversibleMigration||m.dataSchema!==1)throw Error('不支持不可逆数据迁移或未知数据版本，禁止替换');
    this.installing=true;let lock;
    try{
      lock=await open(join(this.dir,'install.lock'),'wx');
      const backup=join(this.dir,'rollback-'+this.meta.version+'.tgz');await writeFile(backup,await packDirectory(this.root,['package.json',...this.meta.files]));inspectArchive(await readFile(backup));
      await this.store.chain;await copyFile(this.store.file,join(this.dir,'state-backup.json'));
      const cli=process.argv[1];if(!cli?.includes('dsh'))throw Error('未能确认 DSH CLI 恢复入口，禁止自动安装');
      const pending={version:m.version,previous:this.meta.version,backup,exe:process.execPath,cli,profile:this.ctx.profileContext.name||this.ctx.profileContext.dir.split(/[\\/]/).at(-1),pid:process.pid,at:Date.now(),dir:this.dir,stateFile:this.store.file};
      const guard=join(this.dir,'recovery-guard.mjs');await copyFile(fileURLToPath(new URL('./recovery-guard.mjs',import.meta.url)),guard);
      await writeFile(join(this.dir,'pending.json'),JSON.stringify(pending));
      const child=spawn(process.execPath,[guard,join(this.dir,'pending.json')],{detached:true,stdio:'ignore',windowsHide:true,env:{...process.env,ELECTRON_RUN_AS_NODE:'1'}});await new Promise((resolve,reject)=>{child.once('spawn',resolve);child.once('error',reject)});child.unref();
      const result=await this.ctx.pluginManager.installBundle(file,{requestId:randomUUID()});
      if(result.error||result.packageResult?.exitCode!==0)throw Error('宿主安装失败：'+JSON.stringify(result));
      this.status.state='pending-restart';this.status.installedVersion=m.version;this.status.application=result.application;this.staged=null;
    }catch(error){this.status.state='install-failed';this.status.error=error.message;await rm(join(this.dir,'pending.json'),{force:true});throw error}
    finally{await lock?.close();if(lock)await rm(join(this.dir,'install.lock'),{force:true});this.installing=false}
  }
}
