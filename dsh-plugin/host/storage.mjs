import {mkdir,readFile,writeFile,rename} from 'node:fs/promises';
import {join} from 'node:path';
import {randomUUID} from 'node:crypto';
export class Store{
  constructor(dir){this.dir=dir;this.file=join(dir,'state.json');this.chain=Promise.resolve();this.value={schemaVersion:1,prompts:[],history:[],settings:{autoCheck:true,autoInstall:true,channel:'stable',repository:''},blockedVersions:[]}}
  async init(){await mkdir(this.dir,{recursive:true});try{const parsed=JSON.parse(await readFile(this.file,'utf8'));if(parsed.schemaVersion!==1)throw Error('不支持的数据版本，保留原文件并停止写入');this.value={...this.value,...parsed,settings:{...this.value.settings,...parsed.settings}}}catch(e){if(e.code!=='ENOENT')throw e}return this}
  save(){const snapshot=JSON.stringify(this.value,null,2);const next=this.chain.catch(()=>{}).then(async()=>{const tmp=this.file+'.'+randomUUID()+'.tmp';await writeFile(tmp,snapshot,{mode:0o600});await rename(tmp,this.file)});this.chain=next;return next}
  history(entry){this.value.history.unshift(structuredClone(entry));this.value.history=this.value.history.slice(0,80);return this.save()}
}
