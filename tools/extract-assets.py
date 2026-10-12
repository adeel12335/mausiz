from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urljoin, urlsplit, unquote, quote
from urllib.error import HTTPError
from concurrent.futures import ThreadPoolExecutor, as_completed
from lxml import html
import json, hashlib, time
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'design'/'source-content'
PUBLIC=ROOT/'public'
PUBLIC.mkdir(exist_ok=True)
records=json.loads((SOURCE/'content-manifest.json').read_text(encoding='utf-8'))
urls=set()
for key, record in records.items():
    for item in record['links']:
        u=item['absolute_href']
        if urlsplit(u).hostname in ('mauriziodecina.it','www.mauriziodecina.it'): urls.add(u)
    doc=html.document_fromstring((SOURCE/(key+'.html')).read_bytes(),parser=html.HTMLParser(encoding='windows-1252'))
    for src in doc.xpath('//img/@src'):
        urls.add(urljoin(record['source_url'],src))
urls={u for u in urls if urlsplit(u).path not in ('','/')}
def retrieve(original):
    parts=urlsplit(original)
    relative=unquote(parts.path).lstrip('/')
    target=(PUBLIC/relative).resolve()
    if not target.is_relative_to(PUBLIC.resolve()): return {'url':original,'status':'unsafe_path'}
    if relative.lower().endswith(('.htm','.html')):
        return {'url':original,'path':relative,'status':'page','bytes':0}
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists() and target.stat().st_size:
        return {'url':original,'path':relative,'status':'downloaded','bytes':target.stat().st_size,'cached':True}
    safe='https://mauriziodecina.it'+quote(unquote(parts.path),safe="/:@!$&'()*+,;=-._~")+('?' + parts.query if parts.query else '')
    temporary=target.with_name(target.name+'.part')
    error=None
    for attempt in range(2):
        try:
            request=Request(safe,headers={'User-Agent':'Mozilla/5.0 (compatible; website asset migration)'})
            with urlopen(request,timeout=45) as response:
                kind=response.headers.get('Content-Type','')
                if 'text/html' in kind and not relative.lower().endswith(('.html','.htm')): raise ValueError('Unexpected HTML response for asset')
                count=0
                with temporary.open('wb') as output:
                    while True:
                        chunk=response.read(1024*256)
                        if not chunk: break
                        output.write(chunk); count+=len(chunk)
                if not count: raise ValueError('Empty asset response')
            temporary.replace(target)
            return {'url':original,'path':relative,'status':'downloaded','bytes':count,'content_type':kind}
        except HTTPError as exc:
            error='HTTP '+str(exc.code)
            if exc.code<500: break
        except Exception as exc: error=str(exc)
    if temporary.exists(): temporary.unlink()
    return {'url':original,'path':relative,'status':'unavailable','error':error}
completed=[]; total=len(urls)
print('Extracting',total,'unique first-party assets and pages',flush=True)
with ThreadPoolExecutor(max_workers=8) as pool:
    futures=[pool.submit(retrieve,url) for url in sorted(urls)]
    for index,future in enumerate(as_completed(futures),1):
        result=future.result(); completed.append(result)
        if index%25==0 or index==total:
            success=sum(x['status']=='downloaded' for x in completed)
            missing=sum(x['status']=='unavailable' for x in completed)
            size=sum(x.get('bytes',0) for x in completed)
            print(index,'/',total,'downloaded:',success,'unavailable:',missing,'MB:',round(size/1024/1024,1),flush=True)
manifest={'source':'https://mauriziodecina.it/','assets':sorted(completed,key=lambda x:x['url'])}
(ROOT/'asset-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('EXTRACTION COMPLETE',flush=True)

