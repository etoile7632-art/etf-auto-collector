import csv, io, json, os, hashlib
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/'funds.json'
OUT=ROOT/'data'

def fetch(url):
    req=Request(url,headers={'User-Agent':'ETF-Research-Collector/1.0 (public research; contact repository owner)','Accept':'text/csv,application/json,*/*'})
    with urlopen(req,timeout=25) as r:
        return r.read(),r.headers.get('Content-Type','')

def parse(raw,fmt):
    if fmt=='json':
        obj=json.loads(raw)
        if not isinstance(obj,list): raise ValueError('JSON must be an array of holdings')
        return obj
    if fmt=='csv':
        return list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
    raise ValueError('Unsupported format')

def normalize(rows, mapping):
    result=[]
    for row in rows:
        item={k:row.get(v) for k,v in mapping.items()}
        if not item.get('ticker') or not item.get('name'): continue
        try: item['weight']=float(str(item['weight']).replace('%','').replace(',',''))
        except (TypeError,ValueError): raise ValueError('Invalid weight')
        if not 0<=item['weight']<=100: raise ValueError('Weight out of bounds')
        result.append(item)
    if not result: raise ValueError('No valid holdings')
    if len({r['ticker'] for r in result})!=len(result): raise ValueError('Duplicate tickers')
    if sum(r['weight'] for r in result)>101: raise ValueError('Weight sum > 101%')
    return result

def run():
    funds=json.loads(CONFIG.read_text(encoding='utf-8'))
    OUT.mkdir(exist_ok=True)
    results=[]
    for fund in funds:
        entry={'id':fund['id'],'name':fund['name'],'status':'PENDING','asof':None,'holdings':[],'source':None,'error':None}
        for source in fund.get('sources',[]):
            try:
                if not source.get('url') or 'REPLACE_' in source['url']: continue
                raw,content_type=fetch(source['url'])
                holdings=normalize(parse(raw,source['format']),source['mapping'])
                # Do not infer as-of date from download time. Require date supplied in configuration/source.
                asof=source.get('asof')
                if not asof: raise ValueError('Missing explicit holdings as-of date')
                datetime.strptime(asof,'%Y-%m-%d')
                entry.update(status='VERIFIED',asof=asof,holdings=holdings,source=source['url'],sha256=hashlib.sha256(raw).hexdigest(),error=None)
                break
            except Exception as exc:
                entry['error']=f'{type(exc).__name__}: {str(exc)[:180]}'
        results.append(entry)
    now=datetime.now(timezone.utc)
    output={'generated_at_utc':now.isoformat(),'schema_version':'0.1','funds':results,'verified_count':sum(r['status']=='VERIFIED' for r in results)}
    (OUT/'latest.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/(now.strftime('%Y-%m-%d')+'.json')).write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f"Verified {output['verified_count']}/{len(results)} funds")

if __name__=='__main__':run()
