import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,writeFile,rm,access} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import {spawn} from 'node:child_process';
const guard=resolve(import.meta.dirname,'../host/recovery-guard.mjs');
function run(args){return new Promise((resolve,reject)=>{const c=spawn(process.execPath,args,{windowsHide:true,stdio:'ignore'});c.on('error',reject);c.on('exit',code=>resolve({code,pid:c.pid}))})}
for(const scenario of ['healthy','confirmed','superseded'])test('recovery helper never rolls back a '+scenario+' activation',async()=>{
 const dir=await mkdtemp(join(tmpdir(),'page-studio-guard-'));
 try{
  const old=await run(['-e','process.exit(0)']),pending=join(dir,'pending.json'),sentinel=join(dir,'rollback-ran'),cli=join(dir,'unexpected-rollback.cjs');
  await writeFile(cli,'require("node:fs").writeFileSync('+JSON.stringify(sentinel)+',"unexpected");');
  const value={pid:old.pid,version:'0.1.7',previous:'0.1.4',at:Date.now()-1000,dir,exe:process.execPath,cli,profile:'test',backup:'not-needed',healthTimeoutMs:10000};
  if(scenario==='healthy'){await writeFile(pending,JSON.stringify(value));await writeFile(join(dir,'health.json'),JSON.stringify({version:'0.1.7',healthy:true,at:Date.now()}))}
  if(scenario!=='healthy')await writeFile(pending,JSON.stringify(value));
  const running=run([guard,pending]);
  if(scenario!=='healthy'){await new Promise(r=>setTimeout(r,300));if(scenario==='confirmed')await rm(pending);else await writeFile(pending,JSON.stringify({...value,version:'0.1.8'}))}
  const child=await running;assert.equal(child.code,0);await assert.rejects(access(sentinel));
 }finally{await rm(dir,{recursive:true,force:true})}
});
