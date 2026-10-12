from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin
import re, json, html, sys
sys.stdout.reconfigure(encoding='utf-8')
root=Path(r'C:\adeel-projects\mauriz\design\source-content')
class SourceParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links=[]; self.active=None; self.body=False; self.body_text=[]
    def finish_link(self):
        if self.active is not None:
            self.active['text']=' '.join(self.active['text'].split())
            self.links.append(self.active); self.active=None
    def handle_starttag(self,tag,attrs):
        if tag=='body': self.body=True
        if tag=='a':
            self.finish_link()
            self.active={'href':dict(attrs).get('href',''),'text':''}
    def handle_endtag(self,tag):
        if tag=='a': self.finish_link()
        if tag=='body': self.body=False
    def handle_data(self,value):
        if self.body: self.body_text.append(value)
        if self.active is not None: self.active['text']+=value
records={}
for path in root.glob('*.html'):
    source=path.read_text(encoding='utf-8')
    parser=SourceParser(); parser.feed(source); parser.finish_link()
    text=' '.join(' '.join(parser.body_text).split())
    (root/(path.stem+'-verbatim.txt')).write_text(text,encoding='utf-8')
    url='https://mauriziodecina.it/'+('' if path.stem=='homepage' else 'stuff/'+path.stem+'.htm')
    for link in parser.links: link['absolute_href']=urljoin(url,link['href'])
    records[path.stem]={'source_url':url,'word_count':len(text.split()),'links':parser.links,'body_text':text}
    print(path.stem, 'words:', len(text.split()), 'links:',len(parser.links))
    if path.stem=='homepage':
        for match in re.finditer('Attività didattica',text):
            print(text[match.start():match.start()+230])
(root/'content-manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
print('All original page text and link destinations captured.')

