import {randomUUID} from 'node:crypto';
import {parseContent,generationPrompt,revisionPrompt,repairPrompt,MAX_INPUT} from '../shared/content.mjs';
export class Tasks{
  constructor(adapter,store,exporter){this.adapter=adapter;this.store=store;this.exporter=exporter;this.tasks=new Map();this.active=null;this.disposed=false}
  start(input){
    if(this.active)throw Error('已有生成或修复任务，请等待或停止');
    const requestId=randomUUID();const task={requestId,attempt:1,state:'pending',kind:input.kind||'pages',createdAt:new Date().toISOString(),text:'',thinking:'',raw:[],snapshot:structuredClone(input),autoExport:input.autoExport===true};
    this.tasks.set(requestId,task);this.active=task;task.abort=new AbortController();
    task.promise=this.execute(task).catch(async error=>{task.state=task.abort.signal.aborted?'cancelled':'failed';task.error=error.message;task.autoExport=false;await this.record(task)}).finally(()=>{if(this.active===task)this.active=null});
    return this.view(task);
  }
  async execute(task){
    const input=task.snapshot,selection=input.selection||this.adapter.models().selected;
    const session=await this.adapter.session(selection,input.sessionId);task.sessionId=session.id;task.selectedModel=selection;
    if(task.abort.signal.aborted)throw Error('已取消');task.state='running';
    let prompt;
    if(task.kind==='pages')prompt=input.current?revisionPrompt(input.current,input.input,input.change):generationPrompt(input.input);
    else prompt=input.prompt;
    if(typeof prompt!=='string'||!prompt.trim()||prompt.length>MAX_INPUT)throw Error('提示词为空或超过输入长度限制');
    task.promptSnapshot=prompt;
    const run=async text=>this.adapter.run(session,text,task,chunk=>{if(task.abort.signal.aborted)return;if(chunk.type==='text-delta')task.text+=chunk.text;if(chunk.type==='reasoning-delta')task.thinking+=chunk.text},task.abort.signal);
    let raw=await run(prompt);task.raw.push(raw);
    if(task.kind==='pages'){
      try{task.content=parseContent(raw)}catch(error){task.validationError=error.message;task.state='repairing';task.attempt=2;raw=await run(repairPrompt(raw,error.message));task.raw.push(raw);task.content=parseContent(raw)}
    }else{task.content={text:raw};task.autoExport=false}
    if(task.abort.signal.aborted)throw Error('已取消');
    task.revision=randomUUID();task.state='completed';task.text=raw;
    if(task.autoExport){task.state='exporting';task.export={state:'rendering'};try{task.export=await this.exporter.create(task,false,input.published!==false)}catch(error){task.export={state:'failed',error:error.message}}}
    if(task.abort.signal.aborted)throw Error('已取消');task.state='completed';
    await this.record(task);
  }
  view(task){if(!task)return null;const {abort,promise,...value}=task;return structuredClone(value)}
  record(task){return this.store.history(this.view(task))}
  cancel(id){const task=this.tasks.get(id);if(!task||!['pending','running','repairing','exporting'].includes(task.state))return false;task.autoExport=false;task.abort.abort();task.state='cancelled';return true}
  async dispose(){this.disposed=true;if(this.active)this.cancel(this.active.requestId);await this.active?.promise}
}
