#!/usr/bin/env python3
"""Ahorra360 catalog updater. Stdlib-only, atomic, incremental and safe."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, re, shutil, sys, time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'; RAW=DATA/'raw'/'snpsap'; PUBLISHED=DATA/'published'; STATE=DATA/'state'/'sync.json'
DEFAULT_API=os.getenv('SNPSAP_API_BASE','https://www.subvenciones.gob.es/bdnstrans/api').rstrip('/')
USER_AGENT='Ahorra360/2.0 (+catalog updater; respectful weekly synchronization)'
KEYWORDS={
 'Vivienda y alquiler':['vivienda','alquiler','arrendamiento','hipoteca','inquilino'],
 'Rehabilitación y reformas':['rehabilit','reforma','ventana','aislamiento','accesibilidad','barrera arquitect'],
 'Eficiencia energética':['eficiencia energ','autoconsumo','solar','fotovolta','aerotermia','energía renovable','bono social'],
 'Familias':['familia','nacimiento','hijo','conciliación','maternidad','paternidad'],
 'Jóvenes':['joven','menor de 35','menores de 35','emancipación'],
 'Mayores y dependencia':['mayor','jubilad','dependencia','discapacidad','cuidador'],
 'Empleo y formación':['desemple','empleo','formación','beca'],
 'Movilidad':['vehículo eléctrico','movilidad','transporte','punto de recarga'],
 'Fiscalidad y deducciones':['deducción','bonificación fiscal','impuesto','irpf'],
 'Autónomos':['autónom','autoempleo']}
EXCLUDE=['sociedad anónima deportiva','entidades locales','ayuntamientos beneficiarios','investigación universitaria','cooperación internacional','sector agrario','explotaciones agrarias']

def now(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
def parse_date(s):
 if not s:return None
 for f in ('%d/%m/%Y','%Y-%m-%d','%Y/%m/%d'):
  try:return dt.datetime.strptime(str(s)[:10],f).date().isoformat()
  except ValueError:pass
 return None
def first(d,*keys):
 for k in keys:
  v=d.get(k)
  if v not in (None,'',[]):return v
 return None
def slugify(s):return re.sub(r'-+','-',re.sub(r'[^a-z0-9]+','-',s.lower().translate(str.maketrans('áéíóúüñ','aeiouun')))).strip('-')[:110]
def request_json(url,retries=4):
 for attempt in range(retries):
  try:
   req=Request(url,headers={'Accept':'application/json','User-Agent':USER_AGENT})
   with urlopen(req,timeout=45) as r:return json.loads(r.read().decode('utf-8-sig'))
  except (HTTPError,URLError,TimeoutError,json.JSONDecodeError) as e:
   if attempt==retries-1:raise
   time.sleep(min(2**attempt,12))
def extract_rows(payload):
 if isinstance(payload,list):return payload,None
 for key in ('content','data','resultados','results','items','convocatorias'):
  value=payload.get(key) if isinstance(payload,dict) else None
  if isinstance(value,list):return value,payload.get('totalPages') or payload.get('paginas')
  if isinstance(value,dict):
   for k in ('content','items','results'):
    if isinstance(value.get(k),list):return value[k], value.get('totalPages')
 return [],None
def category(text):
 text=text.lower(); scores={k:sum(1 for w in ws if w in text) for k,ws in KEYWORDS.items()}; best=max(scores,key=scores.get)
 return (best,scores[best]) if scores[best] else ('Otras prestaciones económicas',0)
def normalize(x):
 code=str(first(x,'numeroConvocatoria','codigoBDNS','id','numero') or '')
 title=str(first(x,'descripcion','titulo','title','descripcionLeng') or '').strip()
 if not code or not title:return None
 text=' '.join(str(first(x,k) or '') for k in ('descripcion','titulo','finalidad','objeto','beneficiarios','nivel1','nivel2','nivel3'))
 cat,score=category(text); low=text.lower(); excluded=any(w in low for w in EXCLUDE)
 relevance='EXCLUDED' if excluded else ('HIGH' if score>=2 else 'MEDIUM' if score==1 else 'LOW')
 pub=parse_date(first(x,'fechaRecepcion','fechaRegistro','fechaPublicacion'))
 opening=parse_date(first(x,'fechaInicioSolicitud','fechaInicio','fechaApertura'))
 closing=parse_date(first(x,'fechaFinSolicitud','fechaFin','fechaCierre'))
 today=dt.date.today().isoformat(); status='PENDIENTE_DE_VERIFICACIÓN'
 if closing and closing<today:status='HISTÓRICA'
 elif opening and opening>today:status='PRÓXIMA'
 elif opening and opening<=today and (not closing or closing>=today):status='ABIERTA'
 source_url=f'https://www.subvenciones.gob.es/bdnstrans/GE/es/convocatoria/{code}'
 return {'id':f'bdns-{code}','bdns_id':code,'slug':slugify(title)+'-'+code,'title':title,'official_title':title,'summary':str(first(x,'objeto','descripcion') or title),'description':None,'category':cat,'subcategory':None,'tags':[],'audience':[],'household_relevance':relevance,'territory':str(first(x,'nivel1','region','ambito') or 'España'),'autonomous_community':first(x,'nivel2','comunidadAutonoma'),'province':first(x,'nivel3','provincia'),'municipality':first(x,'municipio'),'granting_authority':str(first(x,'organo','organoConvocante','departamento') or 'No disponible'),'publication_date':pub,'opening_date':opening,'closing_date':closing,'status':status,'amount_min':None,'amount_max':None,'amount_description':None,'beneficiaries':[],'requirements':[],'documentation':[],'source_name':'SNPSAP / BDNS','source_url':source_url,'application_url':None,'official_reference':f'BDNS {code}','opportunity_type':'AYUDA_PUBLICA','last_verified_at':today,'created_at':today,'updated_at':today,'confidence_level':'MEDIA' if score else 'BAJA','verification_notes':'Importación automática desde SNPSAP. Fechas, cuantías y requisitos deben contrastarse en la ficha oficial.','source_payload_hash':hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False).encode()).hexdigest()}
def load_json(path,default):
 try:return json.loads(path.read_text('utf-8'))
 except (FileNotFoundError,json.JSONDecodeError):return default
def atomic_write(path,data):
 path.parent.mkdir(parents=True,exist_ok=True); tmp=path.with_suffix(path.suffix+'.tmp'); tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8'); tmp.replace(path)
def validate(items):
 ids=set(); errors=[]
 for i,x in enumerate(items):
  for k in ('id','slug','title','source_url','status','last_verified_at'):
   if not x.get(k):errors.append(f'{i}: falta {k}')
  if x.get('id') in ids:errors.append(f"duplicado {x.get('id')}")
  ids.add(x.get('id'))
  if x.get('opening_date') and x.get('closing_date') and x['opening_date']>x['closing_date']:errors.append(f"fechas incoherentes {x['id']}")
 return errors
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--days',type=int,default=int(os.getenv('SYNC_DAYS','14')));ap.add_argument('--page-size',type=int,default=int(os.getenv('SYNC_PAGE_SIZE','100')));ap.add_argument('--max-pages',type=int,default=int(os.getenv('SYNC_MAX_PAGES','20')));ap.add_argument('--full',action='store_true');ap.add_argument('--include-low',action='store_true');ap.add_argument('--dry-run',action='store_true');args=ap.parse_args()
 state=load_json(STATE,{})
 start=dt.date(2016,1,1) if args.full else dt.date.today()-dt.timedelta(days=args.days)
 end=dt.date.today(); stamp=now().replace(':','-'); raw_rows=[]
 for page in range(args.max_pages):
  qs=urlencode({'page':page,'pageSize':args.page_size,'order':'fechaRecepcion','direccion':'desc','fechaDesde':start.strftime('%d/%m/%Y'),'fechaHasta':end.strftime('%d/%m/%Y')})
  url=f'{DEFAULT_API}/convocatorias/busqueda?{qs}'; print(f'[fetch] page={page} {url}')
  payload=request_json(url); rows,total=extract_rows(payload); raw_rows.extend(rows)
  if len(rows)<args.page_size or (total is not None and page+1>=int(total)):break
  time.sleep(float(os.getenv('SYNC_DELAY_SECONDS','0.5')))
 if not raw_rows:raise SystemExit('La API no devolvió convocatorias; se conserva el catálogo publicado.')
 RAW.mkdir(parents=True,exist_ok=True); atomic_write(RAW/f'{stamp}.json',raw_rows)
 existing=load_json(PUBLISHED/'opportunities.json',load_json(DATA/'opportunities.json',[])); by_id={x['id']:x for x in existing if x.get('id')}
 added=updated=excluded=0
 for row in raw_rows:
  item=normalize(row)
  if not item:continue
  if item['household_relevance']=='EXCLUDED' or (item['household_relevance']=='LOW' and not args.include_low):excluded+=1;continue
  old=by_id.get(item['id'])
  if old:
   item['created_at']=old.get('created_at',item['created_at'])
   if old.get('source_payload_hash')==item.get('source_payload_hash'):item['updated_at']=old.get('updated_at',item['updated_at'])
   else:updated+=1
  else:added+=1
  by_id[item['id']]=item
 catalog=sorted(by_id.values(),key=lambda x:(x.get('publication_date') or '',x['id']),reverse=True); errors=validate(catalog)
 if errors:raise SystemExit('Validación fallida:\n'+'\n'.join(errors[:30]))
 report={'run_at':now(),'from':start.isoformat(),'to':end.isoformat(),'fetched':len(raw_rows),'published_total':len(catalog),'added':added,'updated':updated,'excluded':excluded,'dry_run':args.dry_run}
 print(json.dumps(report,ensure_ascii=False,indent=2))
 if not args.dry_run:
  atomic_write(PUBLISHED/'opportunities.json',catalog);atomic_write(PUBLISHED/'metadata.json',report);atomic_write(STATE,{'last_successful_sync':now(),'last_report':report})
if __name__=='__main__':main()
