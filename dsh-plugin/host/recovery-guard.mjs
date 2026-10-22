// Copied into the plugin's user-data update directory before replacement.
// Never terminates DSH. Only reinstalls this plugin's saved archive in the same profile.
import {readFile,writeFile,copyFile} from 'node:fs/promises';
import {spawn} from 'node:child_process';
import {join} from 'node:path';
const pendingFile=process.argv[2];
const delay=ms=>new Promise(r=>setTimeout(r,ms));
let pending;try{pending=JSON.parse(await readFile(pendingFile,'utf8'))}catch{process.exit(0)}
const alive=()=>{try{process.kill(pending.pid,0);return true}catch{return false}};
while(alive()){try{await readFile(pendingFile)}catch{process.exit(0)}await delay(5000)}
let healthy=false;
const waitMs=Math.min(300000,Math.max(10000,pending.healthTimeoutMs||300000));
for(let elapsed=0;elapsed<waitMs;elapsed+=5000){try{const h=JSON.parse(await readFile(join(pending.dir,'health.json'),'utf8'));if(h.healthy&&h.version===pending.version&&h.at>pending.at){healthy=true;break}}catch{}await delay(5000)}
if(healthy)process.exit(0);
// The process has exited and the new plugin never became healthy: recover the exact previous artifact.
const child=spawn(pending.exe,['--expose-internals',pending.cli,'plugin','--profile',pending.profile,'add',pending.backup],{stdio:'ignore',windowsHide:true,env:{...process.env,ELECTRON_RUN_AS_NODE:'1'}});
const code=await new Promise(r=>{child.on('error',()=>r(-1));child.on('close',r)});
if(code===0){let state;try{state=JSON.parse(await readFile(pending.stateFile,'utf8'));if(state.schemaVersion!==1)throw Error('unknown schema')}catch{state=JSON.parse(await readFile(join(pending.dir,'state-backup.json'),'utf8'))}state.blockedVersions=[...new Set([...(state.blockedVersions||[]),pending.version])];await writeFile(pending.stateFile,JSON.stringify(state,null,2));await writeFile(pendingFile,JSON.stringify({...pending,recovered:true}))}
await writeFile(join(pending.dir,'recovery.json'),JSON.stringify({failedVersion:pending.version,restoredVersion:code===0?pending.previous:null,exitCode:code,needsRestart:true,at:Date.now()}));
