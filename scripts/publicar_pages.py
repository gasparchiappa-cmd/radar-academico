"""Publish the current branch through the existing Pages publishing source."""
import json, os, time
from urllib.request import Request, urlopen
BASE='https://api.github.com/repos/'+os.environ['GITHUB_REPOSITORY']
def api(path,method='GET'):
    request=Request(BASE+path,data=b'{}' if method=='POST' else None,method=method,headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'})
    with urlopen(request,timeout=30) as response:return json.load(response)
expected=api('/git/ref/heads/main')['object']['sha']
api('/pages/builds','POST')
for attempt in range(90):
    build=api('/pages/builds/latest')
    if build.get('commit')==expected:
        if build['status']=='built':print('Pages publicado para o commit '+expected);break
        if build['status']=='errored':raise RuntimeError('Pages: '+str(build.get('error')))
    time.sleep(5)
else:raise TimeoutError('Pages não confirmou a publicação do commit esperado')
