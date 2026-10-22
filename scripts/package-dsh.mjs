import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {resolve,join} from 'node:path';
import {createHash} from 'node:crypto';
import {packDirectory,inspectArchive} from '../dsh-plugin/host/archive.mjs';
const root=resolve(import.meta.dirname,'..'),dir=join(root,'dsh-plugin');
const meta=JSON.parse(await readFile(join(dir,'package.json'),'utf8'));
const archive=await packDirectory(dir,['package.json',...meta.files]);
const inspection=inspectArchive(archive);
if(inspection.manifest.version!==meta.version)throw Error('version mismatch');
if([...inspection.entries.keys()].some(name=>/node_modules|\.env|state\.json|credentials|generator\.js/.test(name)))throw Error('private data or fixed prose generator in package');
const output=join(root,'release');await mkdir(output,{recursive:true});
const asset=meta.name+'-'+meta.version+'.tgz',sha256=createHash('sha256').update(archive).digest('hex');
await writeFile(join(output,asset),archive);
let recoveryTested=false;
try{const evidence=JSON.parse(await readFile(join(root,'docs/release-validation.json'),'utf8'));recoveryTested=evidence.version===meta.version&&evidence.sha256===sha256&&evidence.nativeRecovery===true}catch{}
const update={plugin:meta.name,version:meta.version,channel:'stable',dsh:meta.engines.dsh,platform:'win32',asset,size:archive.length,sha256,dataSchema:1,requiresRestart:true,recoveryTested,newPermissions:false,irreversibleMigration:false,summary:'Native DSH conversations, prompt execution, versioned editing and Pages/Menus XLSX export. Recovery eligibility is bound to exact archive validation.'};
await writeFile(join(output,'page-studio-update.json'),JSON.stringify(update,null,2));
await writeFile(join(output,'SHA256SUMS'),sha256+'  '+asset+'\n');
console.log(JSON.stringify({asset,version:meta.version,bytes:archive.length,sha256,files:inspection.entries.size}));
