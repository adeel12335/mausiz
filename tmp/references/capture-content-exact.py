from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin
from urllib.request import Request, urlopen
from concurrent.futures import ThreadPoolExecutor
import json, re, hashlib, sys
sys.stdout.reconfigure(encoding='utf-8')
root=Path(r'C:\adeel-projects\mauriz\design\source-content')
pages={'homepage':'https://mauriziodecina.it/','decinabiography':'https://mauriziodecina.it/stuff/decinabiography.htm','decinabiografia':'https://mauriziodecina.it/stuff/decinabiografia.htm','decinapublications':'https://mauriziodecina.it/stuff/decinapublications.htm'}
class SourceParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.links=[]; self.active=None; self.body=False; self.text=[]
    def finish(self):
        if self.active is not None:
            self.active['text']=' '.join(self.active['text'].split())
            self.links.append(self.active); self.active=None
    def handle_starttag(self,tag,attrs):
        if tag=='body': self.body=True
        if tag=='a': self.finish(); self.active={'href':dict(attrs).get('href',''),'text':''}
    def handle_endtag(self,tag):
        if tag=='a': self.finish()
        if tag=='body': self.body=False
    def handle_data(self,value):
        if self.body: self.text.append(value)
        if self.active is not None: self.active['text']+=value
def retrieve(item):
    key,url=item
    raw=urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=40).read()
    (root/(key+'.html')).write_bytes(raw)
    head=raw[:3000].decode('ascii',errors='ignore')
    encoding='utf-8' if re.search(r'charset\s*=\s*[\x22\x27]?utf-8',head,re.I) else 'cp1252'
    source=raw.decode(encoding,errors='replace')
    parser=SourceParser(); parser.feed(source); parser.finish()
    text=' '.join(' '.join(parser.text).split())
    (root/(key+'-verbatim.txt')).write_text(text,encoding='utf-8')
    for link in parser.links: link['absolute_href']=urljoin(url,link['href'])
    return key,{'source_url':url,'raw_source_sha256':hashlib.sha256(raw).hexdigest(),'original_encoding':encoding,'word_count':len(text.split()),'links':parser.links,'body_text':text}
with ThreadPoolExecutor(max_workers=4) as pool: records=dict(pool.map(retrieve,pages.items()))
assert len(records['homepage']['links'])==493
(root/'content-manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
for key,value in records.items(): print(key,'words:',value['word_count'],'links:',len(value['links']),'original byte snapshot saved')
print('Preserved all four source pages byte for byte with their original encoding declarations.')

