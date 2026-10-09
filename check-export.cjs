const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert');
const nodes=new Map();const get=id=>{if(!nodes.has(id))nodes.set(id,{value:'',checked:false});return nodes.get(id)};
const ctx={document:{getElementById:get},TextEncoder,Uint8Array,DataView,Date,setTimeout,console};vm.createContext(ctx);vm.runInContext(fs.readFileSync('dist/app.js','utf8'),ctx);
const bytes=vm.runInContext(`workbook([headers,['','about-us','MERGE','About Us','','<p>Example & sample "quoted", 中文</p>','','',false,'','page']])`,ctx);assert(bytes.length>1000);fs.writeFileSync('export-check.xlsx',bytes);console.log('JavaScript export executed successfully.');
