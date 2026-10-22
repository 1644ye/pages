"""Read the public release anonymously and verify the actual downloaded bytes."""
import json,urllib.request,hashlib,pathlib,time
root=pathlib.Path(__file__).resolve().parents[1]
version=json.loads((root/'dsh-plugin/package.json').read_text(encoding='utf8'))['version']
def download(url):
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Page-Studio-Verification'}),timeout=60) as response:return response.read()
        except OSError:
            if attempt==2:raise
            time.sleep(2)
release=json.loads(download('https://api.github.com/repos/1644ye/pages/releases/tags/dsh-v'+version))
assert not release['draft'] and not release['prerelease']
assets={a['name']:a for a in release['assets']}
meta=json.loads(download(assets['page-studio-update.json']['browser_download_url']))
blob=download(assets[meta['asset']]['browser_download_url'])
assert meta['version']==version and len(blob)==meta['size'] and hashlib.sha256(blob).hexdigest()==meta['sha256']
assert meta['recoveryTested'] is True
checksums=download(assets['SHA256SUMS']['browser_download_url']).decode()
assert meta['sha256']+'  '+meta['asset'] in checksums
zipname='PageStudio-DSH-'+version+'-Windows.zip';zipbytes=download(assets[zipname]['browser_download_url'])
import zipfile,io
with zipfile.ZipFile(io.BytesIO(zipbytes)) as z:
    assert z.testzip() is None and z.read(meta['asset'])==blob
(root/'.dsh-test/downloaded-release.tgz').write_bytes(blob)
print(json.dumps({'release':release['html_url'],'publicDownload':True,'archiveSha256':meta['sha256'],'bytes':len(blob),'zipIntegrity':True}))
