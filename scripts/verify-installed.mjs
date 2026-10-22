// Compare the actual installed package files to the final release archive.
import {readFile} from 'node:fs/promises';
import {join,resolve} from 'node:path';
import {createHash} from 'node:crypto';
import {packDirectory} from '../dsh-plugin/host/archive.mjs';
const root=resolve(import.meta.dirname,'..'),meta=JSON.parse(await readFile(join(root,'dsh-plugin/package.json'),'utf8'));
const profile=process.argv[2]||'page-studio-test',installed=join(process.env.USERPROFILE,'.dsh/profiles',profile,'node_modules',meta.name);
const actual=JSON.parse(await readFile(join(installed,'package.json'),'utf8'));
const digest=blob=>createHash('sha256').update(blob).digest('hex');
const expected=digest(await readFile(join(root,'release',meta.name+'-'+meta.version+'.tgz'))),got=digest(await packDirectory(installed,['package.json',...actual.files]));
if(actual.version!==meta.version||got!==expected)throw Error('Installed package differs from the exact release archive');
console.log('PASS exact installed archive '+actual.version+' SHA256 '+got);
