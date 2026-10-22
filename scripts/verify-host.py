from pathlib import Path
import re,urllib.request,http.cookiejar,json,sys,time
root=Path(__file__).resolve().parents[1]
logs=[p for p in [root/'.dsh-test/host.log',root/'.dsh-test/host-error.log'] if p.exists()]
log='\n'.join(p.read_text(encoding='utf8',errors='replace') for p in sorted(logs,key=lambda p:p.stat().st_mtime))
urls=re.findall(r'http://127\.0\.0\.1:9186/\?[^\s\x1b]+',log)
if not urls:raise RuntimeError('DSH has not announced its authenticated root URL')
jar=http.cookiejar.CookieJar();client=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
client.open(urls[-1]).read()
def api(path,data=None):
    req=urllib.request.Request('http://127.0.0.1:9186/page-studio/api/'+path,data=None if data is None else json.dumps(data).encode(),headers={'Origin':'http://127.0.0.1:9186','X-Page-Studio':'1','Content-Type':'application/json'})
    return json.load(client.open(req,timeout=60))
action=(sys.argv[1] if len(sys.argv)>1 else 'state') if __name__=='__main__' else 'library'
if action=='state':
    state=api('state');print(json.dumps({k:state[k] for k in ['version','host','profile','models','update']},ensure_ascii=False))
elif action=='generate':
    state=api('state');task=api('generate',{'kind':'pages','selection':state['models']['selected'],'input':{'brand':'','email':'','website':'','refTitle':'Everyday skincare','refBody':'Skincare essentials for hydration, skin barrier care and a dewy-looking finish.','discount':'35','date':'','details':''},'autoExport':True})
    (root/'.dsh-test/task-id.txt').write_text(task['requestId']);print(json.dumps({'requestId':task['requestId'],'state':task['state']}))
elif action=='poll':
    task=api('tasks/'+(root/'.dsh-test/task-id.txt').read_text().strip());print(json.dumps({k:task.get(k) for k in ['requestId','state','sessionId','attempt','turn','error','revision','selectedModel','model']},ensure_ascii=False));print('body characters:',len(task.get('text','')),'reasoning characters:',len(task.get('thinking','')))
    if task['state']=='completed':(root/'.dsh-test/generated.json').write_text(json.dumps(task,ensure_ascii=False),encoding='utf8')
elif action=='cancel':print(api('cancel',{'requestId':(root/'.dsh-test/task-id.txt').read_text().strip()}))
elif action=='prompt':
    state=api('state');task=api('generate',{'kind':'prompt','selection':state['models']['selected'],'prompt':'Reply with exactly: Page Studio real DSH test complete. Do not use tools.'});(root/'.dsh-test/task-id.txt').write_text(task['requestId']);print(task['requestId'])
