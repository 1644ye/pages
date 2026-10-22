"""Publish only a validated local archive. Uses existing Git login, no tokens in files."""
from pathlib import Path
import importlib.util,json,subprocess,hashlib,urllib.parse
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('github_api',root/'scripts/github-api.py');gh=importlib.util.module_from_spec(spec);spec.loader.exec_module(gh)
meta=json.loads((root/'dsh-plugin/package.json').read_text(encoding='utf8'));version=meta['version'];tag='dsh-v'+version
update=json.loads((root/'release/page-studio-update.json').read_text(encoding='utf8'))
archive=root/'release'/update['asset']
if update['version']!=version or hashlib.sha256(archive.read_bytes()).hexdigest()!=update['sha256'] or not update['recoveryTested']:raise RuntimeError('Exact archive must have recorded recovery validation before publishing')
commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root).decode().strip()
remote=gh.request('repos/1644ye/pages/commits/main')['sha']
if remote!=commit:raise RuntimeError('Push and verify main before release')
releases=gh.request('repos/1644ye/pages/releases');release=next((r for r in releases if r['tag_name']==tag),None)
if release and not release['draft']:raise RuntimeError('Release already published; refusing to replace assets')
if release is None:
    release=gh.request('repos/1644ye/pages/releases','POST',{'tag_name':tag,'target_commitish':commit,'name':'Shopify Page Studio '+version,'body':(root/'docs'/('release-notes-'+version+'.md')).read_text(encoding='utf8'),'draft':True,'prerelease':False})
assets=[archive,root/'release'/('PageStudio-DSH-'+version+'-Windows.zip'),root/'release/page-studio-update.json',root/'release/SHA256SUMS',root/'docs'/('release-notes-'+version+'.md')]
existing={a['name']:a for a in gh.request('repos/1644ye/pages/releases/'+str(release['id'])+'/assets')}
for path in assets:
    if path.name in existing:
        if existing[path.name]['size']!=path.stat().st_size:raise RuntimeError('Existing draft asset differs; refusing replacement')
        continue
    uploaded=gh.request(release['upload_url'].split('{')[0]+'?name='+urllib.parse.quote(path.name),method='POST',binary=path.read_bytes())
    if uploaded['size']!=path.stat().st_size:raise RuntimeError('Uploaded asset size mismatch')
verified=gh.request('repos/1644ye/pages/releases/'+str(release['id']))
if {a['name'] for a in verified['assets']}!={p.name for p in assets}:raise RuntimeError('Release asset set does not match expected files')
result=gh.request('repos/1644ye/pages/releases/'+str(release['id']),'PATCH',{'draft':False,'make_latest':'true'})
print(json.dumps({'url':result['html_url'],'tag':tag,'targetCommit':commit,'assets':[{'name':a['name'],'url':a['browser_download_url']} for a in result['assets']]},indent=2))
