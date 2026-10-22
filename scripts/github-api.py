"""GitHub administration via the existing Git credential manager; never prints credentials."""
import json,subprocess,urllib.request,urllib.error,urllib.parse,time,sys,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        redirected=super().redirect_request(req,fp,code,msg,headers,newurl)
        if redirected and urllib.parse.urlparse(req.full_url).netloc!=urllib.parse.urlparse(newurl).netloc:redirected.remove_header('Authorization')
        return redirected
def request(path,method='GET',data=None,binary=None,authenticated=True,raw=False):
    headers={'Accept':'application/vnd.github+json','User-Agent':'Page-Studio-Release','X-GitHub-Api-Version':'2022-11-28'}
    if authenticated:
        result=subprocess.run(['git','-c','credential.interactive=never','credential','fill'],input='protocol=https\nhost=github.com\n\n',text=True,capture_output=True,cwd=ROOT)
        if result.returncode:raise RuntimeError('Git credential manager has no usable GitHub login')
        credential=dict(line.split('=',1) for line in result.stdout.splitlines() if '=' in line)
        headers['Authorization']='Bearer '+credential['password']
    payload=None
    if data is not None:payload=json.dumps(data).encode();headers['Content-Type']='application/json'
    if binary is not None:payload=binary;headers['Content-Type']='application/octet-stream'
    url=path if path.startswith('https://') else 'https://api.github.com/'+path.lstrip('/')
    for attempt in range(3):
        try:
            with urllib.request.build_opener(SafeRedirect()).open(urllib.request.Request(url,data=payload,headers=headers,method=method),timeout=60) as response:
                content=response.read();return content if raw else json.loads(content) if content else None
        except urllib.error.HTTPError as error:
            if error.code<500:raise RuntimeError('GitHub HTTP '+str(error.code)+': '+error.read().decode()[:500]) from None
            if attempt==2:raise RuntimeError('GitHub HTTP '+str(error.code)) from None
        except (OSError,urllib.error.URLError) as error:
            if attempt==2:raise RuntimeError('GitHub connection failed: '+str(error)) from None
        time.sleep(2)
if __name__=='__main__':
    path=sys.argv[1];method=sys.argv[2] if len(sys.argv)>2 else 'GET'
    data=json.loads(pathlib.Path(sys.argv[3]).read_text(encoding='utf8')) if len(sys.argv)>3 else None
    print(json.dumps(request(path,method,data),ensure_ascii=False,indent=2))
