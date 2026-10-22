import {randomUUID} from 'node:crypto';
import {createUserMessage} from '@deepseek-ai/dsh-llm';
export class DshAdapter{
  constructor(ctx){this.ctx=ctx;this.owned=new Map();this.locks=new Set()}
  models(){return {selected:this.ctx.agentDefaultModel.currentSelection(),providers:this.ctx.llm.listProviders()}}
  async modelOptions(provider){return this.ctx.llm.listModels(provider)}
  async session(selection,id){
    if(!/deepseek/i.test(selection.provider+' '+selection.model))throw Error('请选择宿主已配置的 DeepSeek 模型，当前模型不是 DeepSeek');
    if(id){const a=this.ctx.agents.get(id);if(a){if(a.status!=='idle')throw Error('所选会话正在执行任务');if(a.options.provider!==selection.provider||a.options.model!==selection.model)throw Error('所选会话模型与预览不一致，请使用其实际模型或新建会话');return a}const h=await this.ctx.agents.resume({resumeSessionId:id,agentOptions:selection});this.owned.set(h.agent.id,h);return h.agent}
    const h=await this.ctx.agents.create({sessionId:'page-studio-'+randomUUID(),agentOptions:selection,meta:{cwd:process.cwd()}});this.owned.set(h.agent.id,h);return h.agent;
  }
  async run(agent,text,task,onFrame,signal){
    if(this.locks.has(agent.id)||agent.status!=='idle')throw Error('同一会话已有活动任务');
    this.locks.add(agent.id);
    const message=createUserMessage({content:[{type:'text',text}],source:{kind:'user'}});
    task.messageId=message.id;task.sessionId=agent.id;
    let admitted=false,turn,final,ending,streamIndex=-1,attempt;
    const events=[];
    const stopSession=this.ctx.on('session/event',(session,event)=>{
      if(session.id!==agent.id)return;
      if(event.type==='user/message'&&event.data.id===message.id){admitted=true;task.userEventSeq=event.seq}
      if(event.type==='turn/start')turn=event.data.turn;
      if(admitted&&event.type==='assistant/message'&&event.data.turn===turn&&!event.data.interrupted){final=event;task.assistantMessageId=event.data.message.id;task.model=event.data.message.source;}
      if(admitted&&event.type==='turn/end'&&event.data.turn===turn){ending=event;task.turn=turn;task.turnEndSeq=event.seq}
      if(admitted&&['tool/call','tool/result'].includes(event.type)){events.push({type:event.type,seq:event.seq});task.tools=events}
    },{global:true});
    const stopStream=this.ctx.on('agent/assistant-stream',({agent:subject,frame})=>{
      if(subject.id!==agent.id||!admitted||signal.aborted)return;
      if(frame.type==='start'&&frame.turn===turn){attempt=frame.attemptId;streamIndex=-1;task.text='';task.thinking='';task.hostAttempt=attempt}
      // Only start frames carry turn/step. Chunk frames are correlated by attemptId.
      if(frame.type==='chunk'&&frame.attemptId===attempt&&frame.index>streamIndex){streamIndex=frame.index;task.streamChunks=(task.streamChunks||0)+1;onFrame(frame.chunk)}
    },{global:true});
    const cancel=()=>agent.cancel({kind:'user'});signal.addEventListener('abort',cancel,{once:true});
    try{
      if(signal.aborted)throw Error('已取消');
      agent.followup(message);await agent.whenIdle();
      if(signal.aborted)throw Error('已取消');
      if(!admitted||ending?.data.reason?.kind!=='completed'||!final)throw Error('DSH 未确认本次消息成功完成：'+JSON.stringify(ending?.data.reason||'缺少匹配 turn/end'));
      const source=final.data.message.source;if(source.provider!==agent.options.provider||source.model!==agent.options.model)throw Error('实际生成模型与预览模型不符');
      const text=final.data.message.content.filter(b=>b.type==='text').map(b=>b.text).join('\n');
      if(!text.trim())throw Error('DSH 最终正文为空');return text;
    }finally{stopSession();stopStream();signal.removeEventListener('abort',cancel);this.locks.delete(agent.id)}
  }
  async dispose(){await Promise.allSettled([...this.owned.values()].map(h=>h.dispose()));this.owned.clear()}
}
