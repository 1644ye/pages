// Test-only overlay; never included in the installable package.
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
import {readFile,writeFile} from 'node:fs/promises';
import {join} from 'node:path';
import {createHash} from 'node:crypto';
export const name='page-studio-local-verification';
export const inject=['webServer','connection','profileContext','pluginManager'];
export function apply(ctx){
  const require=createRequire(join(ctx.profileContext.dir,'package.json'));
  const modulePath=require.resolve('dsh-shopify-page-studio');
  ctx.effect(()=>ctx.webServer.register({kind:'prefix',path:'/page-studio-test',handler:async(req,res)=>{
    const admit=ctx.connection.admit(req);if('rejection'in admit){res.writeHead(admit.rejection);res.end();return}
    try{const {instances}=await import(pathToFileURL(modulePath));const instance=instances.get(ctx.profileContext.name);if(!instance)throw Error('real plugin instance is not ready');
      const path=new URL(req.url,'http://localhost').pathname;let value;
      if(path.endsWith('/stage')&&req.method==='POST'){
        let body='';for await(const chunk of req){body+=chunk;if(body.length>20000)throw Error('too large')};const input=JSON.parse(body);
        if(!/^[0-9]+\.[0-9]+\.[0-9]+$/.test(input.version))throw Error('test version required');
        const bytes=await readFile(join(process.env.PAGE_STUDIO_FIXTURES,input.version+'.tgz'));
        const meta={plugin:'dsh-shopify-page-studio',version:input.version,dsh:'0.2.0-rc.2',dataSchema:1,recoveryTested:true,size:bytes.length,sha256:createHash('sha256').update(bytes).digest('hex')};
        const file=join(instance.updater.dir,input.version+'.tgz');await writeFile(file,bytes);instance.updater.staged={file,meta};instance.updater.status.state='staged';value={staged:meta.version};
      }else if(path.endsWith('/install')&&req.method==='POST'){await instance.updater.install(true);value=instance.updater.status;
        if(value.state==='pending-restart'){const file=join(instance.updater.dir,'pending.json');const p=JSON.parse(await readFile(file));p.healthTimeoutMs=15000;await writeFile(file,JSON.stringify(p))}
      }else value={tasks:instance.tasks.active?.state,dirty:instance.updater.editorDirty,exporting:instance.updater.exporting,update:instance.updater.status};
      res.writeHead(200,{'Content-Type':'application/json'});res.end(JSON.stringify(value));
    }catch(error){res.writeHead(400,{'Content-Type':'application/json'});res.end(JSON.stringify({error:error.message}))}
  }}),'local verification route');
}
