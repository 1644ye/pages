// Clean CI profile smoke test. No credentials and no model calls.
import {spawn,spawnSync} from 'node:child_process';
import {readFile,mkdir} from 'node:fs/promises';
import {resolve,join} from 'node:path';
const root=resolve(import.meta.dirname,'..'),meta=JSON.parse(await readFile(join(root,'dsh-plugin/package.json'),'utf8'));
const cli=join(root,'.dsh-ci/node_modules/@deepseek-ai/dsh/lib/bin.js'),home=join(root,'.dsh-ci/home');await mkdir(home,{recursive:true});
const env={...process.env,DSH_HOME:home};
function command(args){const run=spawnSync(process.execPath,['--expose-internals',cli,...args],{cwd:root,env,encoding:'utf8',windowsHide:true});if(run.status!==0)throw Error('DSH install/config command failed: '+run.stderr)}
command(['--profile','ci','--from-default-profile','web','--dump-default-config']);
command(['plugin','--profile','ci','add',join(root,'release',meta.name+'-'+meta.version+'.tgz')]);
const child=spawn(process.execPath,['--expose-internals',cli,'--profile','ci','--port','9187','--no-open'],{cwd:root,env,stdio:['ignore','pipe','pipe'],windowsHide:true});
let log='';child.stdout.on('data',x=>log+=x);child.stderr.on('data',x=>log+=x);
try{
 let ready=false;for(let i=0;i<90;i++){
   const match=log.match(/http:\/\/127\.0\.0\.1:9187\/\?[^\s\x1b]+/);
   if(match){const auth=await fetch(match[0],{redirect:'manual'}),cookie=auth.headers.get('set-cookie')?.split(';')[0];const response=await fetch('http://127.0.0.1:9187/page-studio/api/state',{headers:{Cookie:cookie||'',Origin:'http://127.0.0.1:9187'}});if(response.ok){const state=await response.json();if(state.version!==meta.version)throw Error('installed version mismatch');ready=true;break}}
   if(child.exitCode!==null)throw Error('isolated DSH exited before readiness');await new Promise(r=>setTimeout(r,1000));
 }
 if(!ready)throw Error('DSH plugin did not become healthy in the clean CI profile');
 console.log('PASS clean DSH profile installation and authenticated plugin health: '+meta.version);
}finally{child.kill('SIGINT')}
