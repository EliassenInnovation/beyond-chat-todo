from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import sys
root=Path(sys.argv[1]).resolve()
class Page(HTMLParser):
 def __init__(self,text):
  super().__init__();self.ids=set();self.links=[];self.feed(text)
 def handle_starttag(self,t,a):
  a=dict(a)
  if 'id' in a:self.ids.add(a['id'])
  for k in ['href','src']:
   if k in a:self.links.append(a[k])
pages={p:Page(p.read_text()) for p in root.rglob('*.html')}
errors=[]
for p,page in pages.items():
 for u in page.links:
  v=urlsplit(u)
  if v.scheme or v.netloc or u.startswith('/') or not u:continue
  target=(p.parent/unquote(v.path)).resolve() if v.path else p
  if target.is_dir():target=target/'index.html'
  if not target.exists():errors.append((str(p.relative_to(root)),u,'missing file'))
  elif v.fragment and target in pages and unquote(v.fragment) not in pages[target].ids:errors.append((str(p.relative_to(root)),u,'missing anchor'))
print('Checked',len(pages),'pages;',len(errors),'broken links/anchors')
for e in errors: print(e)
raise SystemExit(bool(errors))
