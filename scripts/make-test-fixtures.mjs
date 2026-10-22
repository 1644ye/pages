import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {resolve,join} from 'node:path';
import {packDirectory,inspectArchive,packEntries} from '../dsh-plugin/host/archive.mjs';
const root=resolve(import.meta.dirname,'..'),dir=join(root,'dsh-plugin'),dest=join(root,'.dsh-test/fixtures');await mkdir(dest,{recursive:true});
const meta=JSON.parse(await readFile(join(dir,'package.json'),'utf8'));
const entries=inspectArchive(await packDirectory(dir,['package.json',...meta.files])).entries;
for(const[version,broken]of [['0.1.4',false],['0.1.5',true]]){
 const next=new Map(entries);next.set('package/package.json',Buffer.from(JSON.stringify({...meta,version})));
 if(broken)next.set('package/host/index.mjs',Buffer.from("throw new Error('INTENTIONAL LOCAL RECOVERY TEST');\n"));
 await writeFile(join(dest,version+'.tgz'),packEntries([...next]));
}
console.log('Prepared local-only 0.1.4 upgrade and intentionally broken 0.1.5 fixtures. No GitHub release.');
