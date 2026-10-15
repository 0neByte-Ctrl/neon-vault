#!/usr/bin/env python3
"""Import District203 without renaming existing Neon Vault IDs.
Runs on the user's GitHub runner or locally with an extracted upstream directory.
The sandbox deliverable does not contain a downloaded upstream payload.
"""
from __future__ import annotations
import urllib.parse
import argparse, concurrent.futures, copy, hashlib, html, json, os, re, shutil, subprocess, sys, time, unicodedata, urllib.request
from pathlib import Path, PurePosixPath
UPSTREAM='https://github.com/district203/district203.github.io'
RAW='https://raw.githubusercontent.com/district203/district203.github.io/'
ALIASES={'adofai':'adanceoffireandice','adventurecapatalist':'adventurecapitalist','ducklife':'ducklife1','1on1soccer':'1on1soccer','basketbros':'basketbros','basketballstars':'basketballstars','snowrider':'snowrider3d','fireboywatergirl':'fireboyandwatergirl','fivenightsatfreddys':'fnaf','fivenightsatfreddys2':'fnaf2','fivenightsatfreddys3':'fnaf3','fivenightsatfreddys4':'fnaf4','retrobowlcollege':'retrobowlcollege','geometrydash':'geometrydash'}
def norm(s):
 s=unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower().replace('&','and')
 s=re.sub(r'[^a-z0-9]','',s)
 return ALIASES.get(s,s)
def safe_path(text):
 from urllib.parse import unquote
 text=unquote(str(text)).split('?',1)[0].split('#',1)[0].strip('/')
 p=PurePosixPath(text)
 if not text or '\\' in text or p.is_absolute() or '..' in p.parts or any(c in text for c in ['\x00','\n','\r']):raise ValueError('Unsafe upstream path: '+repr(text))
 return str(p)
def get_json(url):
 req=urllib.request.Request(url,headers={'User-Agent':'Neon-Vault-District-Importer','Accept':'application/vnd.github+json'})
 with urllib.request.urlopen(req,timeout=90) as r:return json.load(r)
def catalog_read(path):
 s=path.read_text();prefix='window.NV_CATALOG='
 if not s.startswith(prefix):raise ValueError('Unrecognized Neon Vault catalog format')
 return json.loads(s[len(prefix):].rstrip().removesuffix(';'))
def catalog_write(path,data):path.write_text('window.NV_CATALOG='+json.dumps(data,separators=(',',':'))+';')
def folder_bytes(path):return sum(p.stat().st_size for p in path.rglob('*') if p.is_file() and not p.is_symlink())
def load_source(source):
 games=json.loads((source/'games.json').read_text())
 if isinstance(games,dict):games=games.get('games',[])
 if not isinstance(games,list) or not games:raise ValueError('Upstream games.json is empty or malformed')
 return games
def rewrite_root_urls(dest):
 """Preserve subfolder deploys; only map static root references that exist upstream.
 Dynamic asset construction remains engine-specific and is reported, not guessed.
 """
 count=0
 for f in dest.rglob('*'):
  if f.suffix.lower() not in ['.html','.htm','.js','.css','.json','.webmanifest']:continue
  if f.stat().st_size>6_000_000:continue
  try:s=f.read_text(encoding='utf-8')
  except UnicodeError:continue
  original=s
  def rewrite(m):
   quote,url=m.groups();path=url.split('?',1)[0].split('#',1)[0]
   target=dest/path.lstrip('/')
   if not target.exists():return m.group(0)
   rel=os.path.relpath(target,f.parent).replace(os.sep,'/')
   # URLs are resolved from the document for JS strings; only rewrite HTML/CSS.
   if f.suffix.lower() in ['.js','.json']:return m.group(0)
   return quote+rel+url[len(path):]+quote
  s=re.sub(r'([\"\'])(/[^/\"\'\s<>]+)\1',rewrite,s)
  if s!=original:f.write_text(s);count+=1
 return count
def merge(root,source,budget_mb=800,commit='local'):
 catpath=root/'data/catalog.js';cat=catalog_read(catpath);before=copy.deepcopy(cat)
 (root/'data').mkdir(exist_ok=True)
 games=load_source(source)
 # Only complete entries with an actual entry point are eligible for replacement.
 candidates=[];skipped=[];seen=set()
 for sg in games:
  if not isinstance(sg,dict) or not sg.get('name') or not sg.get('href'):continue
  try:href=safe_path(sg['href'])
  except ValueError as e:skipped.append({'name':sg.get('name'),'reason':str(e)});continue
  if href in seen:continue
  seen.add(href)
  path=source/'games'/href
  entry=path if path.is_file() else next((path/n for n in ['index.html','index.htm'] if (path/n).is_file()),None)
  if entry is None:skipped.append({'name':sg['name'],'href':href,'reason':'No packaged HTML entry point'});continue
  candidates.append((sg,href,entry))
 index={}
 for sg,href,entry in candidates:
  for n in {norm(sg['name']),norm(href)}:index.setdefault(n,[]).append((sg,href,entry))
 replacements=[];additions=[];unmatched=[];used=set();previous={}
 # Never replace the first-party Neon 2048 with a distinct third-party 2048 edition.
 for old in cat['games']:
  if old.get('integrated'):unmatched.append(old['id']);continue
  matches={v[1]:v for n in {norm(old['title']),norm(old['id'])} for v in index.get(n,[])}
  # Exact title wins; no fuzzy matching of sequels or differently named editions.
  exact=[v for v in matches.values() if norm(v[0]['name'])==norm(old['title'])]
  picked=exact[0] if len(exact)==1 else next(iter(matches.values())) if len(matches)==1 else None
  if not picked:unmatched.append(old['id']);continue
  sg,href,entry=picked;used.add(href);previous[old['id']]=copy.deepcopy(old)
  update_game(old,sg,href,entry,source)
  replacements.append({'id':old['id'],'title':old['title'],'districtPath':href})
 for sg,href,entry in candidates:
  if href in used:continue
  slug=re.sub('[^a-z0-9-]','-',href.lower()).strip('-')
  gid='district-'+slug
  if any(x['id']==gid for x in cat['games']):raise ValueError('New ID collision: '+gid)
  item={'id':gid,'title':sg['name'],'kind':'game','image':'assets/city.png','categories':sg.get('categories') or ['Miscellaneous']}
  update_game(item,sg,href,entry,source);cat['games'].append(item);additions.append({'id':gid,'title':item['title'],'districtPath':href})
 # Preserve originals byte-for-byte in the catalog for unmatched games and all other collections.
 original={x['id']:x for x in before['games']}
 assert all(original[gid]==next(x for x in cat['games'] if x['id']==gid) for gid in unmatched)
 for section in ['movies','cloud','tools']:assert cat[section]==before[section]
 # Native payload is copied by whole game directory, never half an engine.
 target=root/'district203';target.mkdir(exist_ok=True)
 budget=int(budget_mb*1024*1024);remaining=budget-folder_bytes(root)
 copied=[];linked=[];roots={}
 for sg,href,entry in candidates:
  group=href.split('/')[0];roots[group]=source/'games'/group
 # Copy smallest complete game folders first to fit GitHub Pages' total-site limit.
 sizes={group:(folder_bytes(path) if path.is_dir() else path.stat().st_size) for group,path in roots.items()}
 for group in sorted(roots,key=lambda n:(sizes[n],n)):
  src=roots[group];size=sizes[group]
  if size>remaining:linked.append(group);continue
  dst=target/'games'/group;dst.parent.mkdir(parents=True,exist_ok=True)
  if src.is_dir():shutil.copytree(src,dst,dirs_exist_ok=True,ignore=shutil.ignore_patterns('.git','node_modules','*.php'))
  else:shutil.copy2(src,dst)
  copied.append(group);remaining-=size
 # Shared assets used by some local engines. No upstream workflows or server files execute.
 for name in ['css','js','images','img','assets','media','ruffle','fonts','favicon.ico','favicon.png','LICENSE','NOTICE']:
  src=source/name
  if not src.exists() or src.is_symlink():continue
  size=folder_bytes(src) if src.is_dir() else src.stat().st_size
  if size>remaining:continue
  dst=target/name
  if src.is_dir():shutil.copytree(src,dst,dirs_exist_ok=True,ignore=shutil.ignore_patterns('.git','node_modules'))
  else:shutil.copy2(src,dst)
  remaining-=size
 if (source/'LICENSE').is_file():shutil.copy2(source/'LICENSE',target/'LICENSE')
 rewrite_count=rewrite_root_urls(target)
 native=0
 for item in cat['games']:
  if item.get('source')!='District203':continue
  item['nativeAvailable']=(root/item['nativeUrl']).is_file()
  item['hosted']=item['nativeAvailable']
  if item['nativeAvailable']:native+=1
  # Keep original image if available; new ones use a genuine packaged image where found.
  if item.get('districtImage') and (root/item['districtImage']).is_file():item['image']=item['districtImage']
  item.pop('districtImage',None)
 catalog_write(catpath,cat)
 report={'upstream':UPSTREAM,'commit':commit,'replaced':replacements,'added':additions,'unchangedIds':unmatched,'skipped':skipped,'nativeGamesCopied':native,'nativeFoldersOverBudget':linked,'siteBudgetMB':budget_mb,'rewrittenTextFiles':rewrite_count,'totalGames':len(cat['games']),'status':'imported','runtimePolicy':'Cross-origin District203 host by default. Native copies require a separate configured game origin or restricted local mode.'}
 (root/'data/district-import.json').write_text(json.dumps(report,indent=2))
 (root/'data/district-status.js').write_text('window.NV_DISTRICT_STATUS='+json.dumps({k:report[k] for k in ['commit','status','nativeGamesCopied','totalGames']}|{'replacedCount':len(replacements),'addedCount':len(additions)})+';')
 (root/'data/district-replaced-originals.json').write_text(json.dumps(previous,separators=(',',':')))
 return report

def update_game(item,sg,href,entry,source):
 from urllib.parse import quote
 original='https://district203.github.io/games/'+quote(href,safe='/')+('' if PurePosixPath(href).suffix else '/')
 local='district203/'+str(entry.relative_to(source)).replace(os.sep,'/')
 item.update(source='District203',url=original,original=original,nativeUrl=local,districtPath=href,districtRanking=sg.get('ranking',999999),hosted=False)
 # Preserve existing IDs, titles, category assignments and favorites/watch history.
 item.setdefault('categories',sg.get('categories') or ['Miscellaneous'])
 base=entry.parent
 images=sorted([p for p in base.iterdir() if p.suffix.lower() in ['.png','.jpg','.jpeg','.webp'] and p.is_file()],key=lambda p:(not any(w in p.stem.lower() for w in ['icon','thumb','logo','cover']),len(p.name)))
 if images:item['districtImage']='district203/'+str(images[0].relative_to(source)).replace(os.sep,'/')

def download_sparse_source(dest:Path,ref:str):
 """Uses one recursive GitHub tree request, then downloads raw source in parallel.
 No upstream scripts, package managers, workflows or install hooks are executed.
 """
 if not re.fullmatch(r'[A-Za-z0-9._/-]+',ref) or '..' in ref:raise ValueError('Invalid ref')
 commit=get_json('https://api.github.com/repos/district203/district203.github.io/commits/'+ref)['sha']
 tree=get_json('https://api.github.com/repos/district203/district203.github.io/git/trees/'+commit+'?recursive=1')
 if tree.get('truncated'):raise RuntimeError('GitHub returned a truncated tree. Use an extracted local source checkout instead.')
 entries=[e for e in tree['tree'] if e['type']=='blob' and (e['path'].startswith('games/') or e['path'].split('/')[0] in ['games.json','LICENSE','NOTICE','css','js','images','img','assets','media','ruffle','fonts','favicon.ico','favicon.png']) and not any(x in PurePosixPath(e['path']).parts for x in ['node_modules','.git','.github'])]
 total=sum(e.get('size',0) for e in entries)
 if total>10*1024**3:raise RuntimeError('Source exceeds the runner download safety limit. Use a local extracted checkout.')
 dest.mkdir(parents=True,exist_ok=True)
 def download(e):
  path=safe_path(e['path']);out=dest/path;out.parent.mkdir(parents=True,exist_ok=True)
  for retry in range(4):
   try:
    req=urllib.request.Request(RAW+commit+'/'+urllib.parse.quote(path,safe='/'),headers={'User-Agent':'Neon-Vault-Importer'})
    with urllib.request.urlopen(req,timeout=180) as r,open(out,'wb') as f:shutil.copyfileobj(r,f)
    if out.stat().st_size!=e.get('size',out.stat().st_size):raise RuntimeError('Incomplete upstream file: '+path)
    return
   except Exception:
    out.unlink(missing_ok=True)
    if retry==3:raise
    time.sleep(2**retry)
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
  for i,_ in enumerate(pool.map(download,entries),1):
   if i%250==0:print(f'Downloaded {i}/{len(entries)} upstream files',flush=True)
 print(f'Downloaded {len(entries)} files / {total/1024**2:.1f} MB at {commit}',flush=True)
 return commit

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--site',type=Path,required=True);ap.add_argument('--source',type=Path);ap.add_argument('--download-to',type=Path);ap.add_argument('--ref',default='main');ap.add_argument('--budget-mb',type=int,default=800);a=ap.parse_args()
 if not a.source and not a.download_to:ap.error('Use --source EXTRACTED_DIRECTORY or --download-to TEMP_DIRECTORY')
 commit='local';src=a.source
 if a.download_to:src=a.download_to;commit=download_sparse_source(src,a.ref)
 if (a.site/'data/district-import.json').exists():raise RuntimeError('Start from the unmerged seed site, not a previous merged build.')
 r=merge(a.site,src,a.budget_mb,commit)
 print(json.dumps({'replaced':len(r['replaced']),'added':len(r['added']),'nativeGamesCopied':r['nativeGamesCopied'],'unchanged':len(r['unchangedIds']),'skipped':len(r['skipped'])},indent=2))
if __name__=='__main__':main()
