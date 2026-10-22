import {readFile,mkdir,writeFile,rename} from 'node:fs/promises';
import {join} from 'node:path';
import {createContext,runInContext} from 'node:vm';
import {randomUUID} from 'node:crypto';
import {validateContent} from '../shared/content.mjs';
export class Exporter{
  constructor(root,store){this.root=root;this.store=store;this.dir=join(store.dir,'exports');this.running=0;this.records=new Map()}
  async init(){await mkdir(this.dir,{recursive:true});this.code=await readFile(join(this.root,'web/xlsx.js'),'utf8')+'\n'+await readFile(join(this.root,'shared/export-runtime.js'),'utf8');this.contact=await readFile(join(this.root,'web/contact.html'),'utf8');await this.create({requestId:'health',revision:'health',content:healthContent()},true);return this}
  async create(result,health=false,published=true){
    const snapshot={requestId:result.requestId,revision:result.revision,attempt:result.attempt,content:structuredClone(result.content)};if(!health)validateContent(snapshot.content);
    const key=[snapshot.requestId,snapshot.attempt||1,snapshot.revision,'xlsx',published].join(':');
    if(!health&&this.records.has(key))return this.records.get(key);
    if(!health&&this.pending?.has(key))return this.pending.get(key);
    this.pending??=new Map();
    const operation=(async()=>{this.running++;try{
      const data={pages:[...snapshot.content.pages,{handle:'contact-us',title:'Contact Us',body_html:this.contact}]};
      const matrix=[['ID','Handle','Command','Title','Author','Body HTML','Created At','Updated At','Published','Published At','Template Suffix'],...data.pages.map(p=>['',p.handle,'MERGE',p.title,'',p.body_html,'','',published,'',p.handle==='contact-us'?'':'page'])];
      const sandbox=createContext({data,matrix,TextEncoder,Uint8Array,DataView});
      runInContext(this.code,sandbox,{timeout:5000});
      const bytes=runInContext('workbook(matrix)',sandbox,{timeout:5000});
      if(bytes.length<1000||bytes[0]!==80||bytes[1]!==75)throw Error('XLSX 渲染失败');
      if(health)return {bytes:bytes.length};
      const id=randomUUID(),name='Pages-and-Menus-'+id+'.xlsx',file=join(this.dir,name),temporary=file+'.tmp';
      await writeFile(temporary,bytes);await rename(temporary,file);
      const record={requestId:snapshot.requestId,attempt:snapshot.attempt||1,resultRevision:snapshot.revision,format:'xlsx',state:'completed',name,bytes:bytes.length,downloadUrl:'/page-studio/api/files/'+name};this.records.set(key,record);return record;
    }finally{this.running--}})();
    this.pending.set(key,operation);try{return await operation}finally{this.pending.delete(key)}
  }
}
function healthContent(){return {pages:[['about-us','About Us'],['customer-service-policy','Customer Service Policy'],['privacy-policy','Privacy Policy'],['refund-policy','Refund Policy'],['shipping-policy','Shipping Policy'],['terms-of-purchase','Terms of Purchase'],['terms-of-use','Terms of Use']].map(([handle,title])=>({handle,title,body_html:'<p>Export module health check.</p>'}))}}
