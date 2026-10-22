import {test} from 'node:test';
import assert from 'node:assert/strict';
import {Tasks} from '../host/tasks.mjs';
const store=()=>({value:{history:[]},history:async function(row){this.value.history.unshift(structuredClone(row))}});
const tick=()=>new Promise(r=>setImmediate(r));
test('cancelled completion and duplicate clicks cannot export or become a new result',async()=>{
  let resolve;const adapter={models:()=>({selected:{provider:'deepseek-test',model:'deepseek-test'}}),session:async()=>({id:'s'}),run:()=>new Promise(r=>resolve=r)};
  let exports=0;const s=store(),tasks=new Tasks(adapter,s,{create:()=>{exports++}});
  const task=tasks.start({kind:'prompt',prompt:'test',autoExport:true});await tick();assert.throws(()=>tasks.start({kind:'prompt',prompt:'duplicate'}),/已有/);
  tasks.cancel(task.requestId);resolve('late stale response');await tasks.tasks.get(task.requestId).promise;
  assert.equal(tasks.tasks.get(task.requestId).state,'cancelled');assert.equal(exports,0);assert.equal(s.value.history[0].autoExport,false);
});
test('format repair is bounded to one attempt and failure never exports',async()=>{
  let calls=0,exports=0;const adapter={models:()=>({selected:{}}),session:async()=>({id:'s'}),run:async()=>{calls++;return calls===1?'invalid JSON':'{"_repairStatus":"failed","reason":"missing content"}'}};
  const tasks=new Tasks(adapter,store(),{create:()=>{exports++}});const row=tasks.start({input:{refTitle:'Example'},autoExport:true});await tasks.tasks.get(row.requestId).promise;
  assert.equal(calls,2);assert.equal(exports,0);assert.equal(tasks.tasks.get(row.requestId).state,'failed');assert.equal(tasks.tasks.get(row.requestId).attempt,2);
});
test('explicit retry makes a distinct request and cannot replace old request record',async()=>{
  let fail=true;const adapter={models:()=>({selected:{}}),session:async()=>({id:'s'}),run:async()=>{if(fail)throw Error('real-like model error');return 'new result'}};
  const tasks=new Tasks(adapter,store());const a=tasks.start({kind:'prompt',prompt:'first'});await tasks.tasks.get(a.requestId).promise;fail=false;
  const b=tasks.start({kind:'prompt',prompt:'retry'});await tasks.tasks.get(b.requestId).promise;
  assert.notEqual(a.requestId,b.requestId);assert.equal(tasks.tasks.get(a.requestId).state,'failed');assert.equal(tasks.tasks.get(b.requestId).text,'new result');assert.equal(tasks.tasks.get(b.requestId).state,'completed');
});
