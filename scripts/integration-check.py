from pathlib import Path
import json,sys,time,urllib.error,urllib.request
import importlib.util
spec=importlib.util.spec_from_file_location('host_verification',Path(__file__).with_name('verify-host.py'))
host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
api=host.api;root=host.root
action=sys.argv[1]
evidence=root/'.dsh-test/integration.json'
records=json.loads(evidence.read_text(encoding='utf8')) if evidence.exists() else {}
def save():evidence.write_text(json.dumps(records,indent=2,ensure_ascii=False),encoding='utf8')
def wait_task(task_id,limit=360):
    start=time.monotonic();last='';streamed=False
    while time.monotonic()-start<limit:
        t=api('tasks/'+task_id)
        if t['state'] in ['running','repairing'] and (t.get('text') or t.get('thinking')):streamed=True
        status=f"{t['state']} body={len(t.get('text',''))} thinking={len(t.get('thinking',''))}"
        if status!=last:print(status,flush=True);last=status
        if t['state'] not in ['pending','running','repairing','exporting']:return t,streamed
        time.sleep(1)
    raise TimeoutError('bounded task wait exceeded')
if action=='revision':
    original=json.loads((root/'.dsh-test/generated.json').read_text(encoding='utf8'))
    t=api('generate',{'kind':'pages','selection':original['selectedModel'],'sessionId':original['sessionId'],'input':original['snapshot']['input'],'current':{'revision':original['revision'],'content':original['content']},'change':'Change ONLY marketing.hero.cta to "Discover Your Routine". Preserve all seven page body_html strings and all other fields exactly. Return the full JSON structure. Do not use tools.','autoExport':True})
    records['revisionTask']=t['requestId'];save()
    try:api('generate',{'kind':'prompt','prompt':'must not run'})
    except urllib.error.HTTPError as error:assert error.code==400;records['duplicateRejected']=True;save()
    result,streamed=wait_task(t['requestId']);assert result['state']=='completed',result.get('error');assert result['sessionId']==original['sessionId'];assert result['content']['marketing']['hero']['cta']=='Discover Your Routine'
    records['continuedSameSession']=True;records['streamObserved']=streamed;records['unchangedPages']=result['content']['pages']==original['content']['pages'];records['revisionExport']=result.get('export');records['revision']=result['revision'];
    (root/'.dsh-test/revised.json').write_text(json.dumps(result,ensure_ascii=False),encoding='utf8');save()
    assert result['export']['state']=='completed'
    response=host.client.open('http://127.0.0.1:9186'+result['export']['downloadUrl']);(root/'.dsh-test/real-host-export.xlsx').write_bytes(response.read());print('PASS real follow-up + host-written XLSX download',flush=True)
elif action=='cancel-and-failure':
    state=api('state');selection=state['models']['selected']
    t=api('generate',{'kind':'prompt','selection':selection,'prompt':'Write a long 5000-word comparison of everyday clothing materials. Do not call tools.','autoExport':True})
    time.sleep(2);assert api('cancel',{'requestId':t['requestId']})['cancelled'];cancelled,_=wait_task(t['requestId']);assert cancelled['state']=='cancelled' and not cancelled['autoExport'];
    for i in range(30):
        sessions=api('state')['sessions'];found=next((s for s in sessions if s['id']==cancelled['sessionId']),None)
        if found and found['status']=='idle':break
        time.sleep(1)
    assert found and found['status']=='idle';records['realCancel']={'requestId':t['requestId'],'sessionId':cancelled['sessionId'],'hostIdleAfterCancel':True,'export':cancelled.get('export')};save()
    bad=api('generate',{'kind':'prompt','selection':{'provider':'deepseek-not-configured-test','model':'deepseek-invalid-test'},'prompt':'Do not run.'});failed,_=wait_task(bad['requestId']);assert failed['state']=='failed';records['realFailure']=failed['error'];save()
    template=api('prompts',{'title':'Integration saved prompt','content':'Reply with exactly: {{text}}. Do not use tools.','defaults':{},'tags':['verification']})[-1]
    expanded=api('preview',{'content':template['content'],'variables':{'text':'Page Studio real prompt success'}})['text']
    good=api('generate',{'kind':'prompt','selection':selection,'prompt':expanded,'promptId':template['id'],'promptVersion':template['version'],'variables':{'text':'Page Studio real prompt success'}})
    successful,streamed=wait_task(good['requestId']);assert successful['state']=='completed';assert 'Page Studio real prompt success' in successful['content']['text'];records['realPrompt']={'requestId':good['requestId'],'promptVersion':template['version'],'streamed':streamed};save();print('PASS real cancel, failed model route and explicit prompt retry',flush=True)
elif action=='export-edits':
    original=json.loads((root/'.dsh-test/revised.json').read_text(encoding='utf8'));content=original['content'];content['pages'][1]['body_html']+='<p>Saved edit verification: 中文内容。</p>'
    edited=api('revisions',{'requestId':original['requestId'],'content':content});exported=api('export',{'requestId':edited['requestId'],'revision':edited['revision']});duplicate=api('export',{'requestId':edited['requestId'],'revision':edited['revision']});assert exported['name']==duplicate['name'];
    response=host.client.open('http://127.0.0.1:9186'+exported['downloadUrl']);(root/'.dsh-test/real-host-edited.xlsx').write_bytes(response.read());records['savedEditExport']={'revision':edited['revision'],'requestId':edited['requestId'],'deduplicated':True};save();print('PASS saved edits exported without model call',flush=True)
elif action=='busy-update':
    def probe(path,body={}):
        req=urllib.request.Request('http://127.0.0.1:9186/page-studio-test/'+path,data=json.dumps(body).encode(),headers={'Origin':'http://127.0.0.1:9186','Content-Type':'application/json'})
        return json.load(host.client.open(req,timeout=120))
    api('activity',{'clientId':'second-window','dirty':False});assert probe('probe')['dirty'] is True
    records['multipleWindowDirtyPreserved']=True
    api('activity',{'clientId':'upgrade-test','dirty':False})
    t=api('generate',{'kind':'prompt','selection':api('state')['models']['selected'],'prompt':'Write 2000 words about choosing skincare products. Do not call tools.'})
    assert probe('install')['state']=='waiting-idle';records['activeGenerationDeferredUpdate']=True
    api('activity',{'clientId':'upgrade-test','dirty':True});api('cancel',{'requestId':t['requestId']});cancelled,_=wait_task(t['requestId']);
    # Wait until the adapter drained, not merely the early cancelled UI state.
    for i in range(30):
        if probe('probe').get('tasks') is None:break
        time.sleep(1)
    assert probe('probe').get('tasks') is None
    staged=Path.home()/'.dsh/page-studio/page-studio-test/updates/0.1.3.tgz';bytes_=staged.read_bytes();staged.write_bytes(bytes_[:-5]+b'XXXXX')
    api('activity',{'clientId':'upgrade-test','dirty':False})
    try:probe('install');raise AssertionError('corrupt archive accepted')
    except urllib.error.HTTPError as error:
        detail=json.loads(error.read());assert 'SHA-256' in detail['error'];records['corruptArchiveRejected']=True
    api('activity',{'clientId':'upgrade-test','dirty':True});probe('stage',{'version':'0.1.3'});save();print('PASS multiple-window edit gate, active generation gate and corrupt archive rejection',flush=True)
elif action in ['stage','install','probe']:
    body={'version':sys.argv[2]} if action=='stage' else {}
    req=urllib.request.Request('http://127.0.0.1:9186/page-studio-test/'+action,data=json.dumps(body).encode(),headers={'Origin':'http://127.0.0.1:9186','Content-Type':'application/json'})
    print(host.client.open(req,timeout=120).read().decode(),flush=True)
