"""Build the documented format-1 index with a verified immutable Git commit."""
from pathlib import Path
import json,subprocess,sys,time,re
root=Path(__file__).resolve().parents[1]
commit=sys.argv[1] if len(sys.argv)>1 else subprocess.check_output(['git','rev-parse','HEAD'],cwd=root).decode().strip()
if not re.fullmatch('[a-f0-9]{40}',commit):raise ValueError('Full immutable commit required')
meta=json.loads((root/'dsh-plugin/package.json').read_text(encoding='utf8'))
index={'format':1,'title':{'en':'Shopify Page Studio','zh':'Shopify 页面工作台'},'metadata':{'categories':{'workflow':{'title':{'en':'Workflow and automation','zh':'工作流与自动化'}}},'labels':{k:{'title':v} for k,v in [('shopify','Shopify'),('xlsx','Matrixify XLSX'),('prompts','Prompt workbench')]}},'plugins':[{'name':meta['name'],'title':{'en':'Shopify Page Studio','zh':'Shopify 页面工作台'},'description':{'en':meta['description'],'zh':'DeepSeek 对话生成、提示词工作台与 Shopify 页面和菜单 XLSX 导出。'},'author':'1644ye','homepage':meta['homepage'],'repository':{'url':'https://github.com/1644ye/pages','directory':'dsh-plugin'},'metadata':{'category':'workflow','labels':['shopify','xlsx','prompts']},'versions':[{'version':meta['version'],'publishTimestamp':int(time.time()),'engines':meta['engines'],'source':{'type':'git','url':'https://github.com/1644ye/pages','commit':commit,'path':'dsh-plugin'}}]}]}
dest=root/'market/index.json';dest.parent.mkdir(exist_ok=True);dest.write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Built format-1 market index, pinned commit '+commit)
