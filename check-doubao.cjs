const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync('dist/index.html','utf8');
assert.match(html,/id="generatePrompt"/);
assert.match(html,/id="doubaoPanel" hidden/);
assert.doesNotMatch(html.match(/<iframe id="doubaoFrame"[^>]*>/)[0],/\bsrc=/);
const nodes=new Map();
function get(id){if(!nodes.has(id))nodes.set(id,{hidden:id==='doubaoPanel',attributes:{},classList:{toggle(){}},setAttribute(k,v){this.attributes[k]=v},getAttribute(k){return this[k]||null}});return nodes.get(id)}
const ctx={document:{getElementById:get,querySelectorAll(){}}};
vm.runInNewContext(fs.readFileSync('dist/doubao.js','utf8'),ctx);
assert.equal(get('doubaoFrame').src,undefined);
get('openDoubao').onclick();
assert.equal(get('doubaoPanel').hidden,false);
assert.equal(get('doubaoFrame').src,'https://www.doubao.com/chat/');
get('closeDoubao').onclick();
assert.equal(get('doubaoPanel').hidden,true);
assert.equal(get('doubaoFrame').src,'https://www.doubao.com/chat/');
get('openDoubao').onclick();
assert.equal(get('openDoubao').attributes['aria-expanded'],'true');
console.log('PASS: prompt button retained, Doubao lazy load, collapse preserves iframe session.');
