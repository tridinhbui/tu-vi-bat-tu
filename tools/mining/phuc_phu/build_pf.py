import sys, json
ROOT='/Users/buidinhtri/Desktop/tuvibattu/.claude/worktrees/agent-a94676969e59ceb88'
sys.path.insert(0, ROOT + '/tools')
import book_text
SRC='/private/tmp/claude-501/-Users-buidinhtri-Desktop-tuvibattu/96e0ed33-c16b-4662-9fef-4e28af98feb3/scratchpad/pf_src.json'
OUT=ROOT + '/engine/data/kg/mined/kl_phuc_duc_phu_mau.json'
d=json.load(open(SRC))
import glob
d['pages_read']=[];d['entries']=[];d['natures']=[]
for f in sorted(glob.glob(SRC.rsplit('/',1)[0]+'/pf/*.json')):
    x=json.load(open(f))
    for k in ('pages_read','entries','natures'): d[k]+=x.get(k,[])
bad=[]
ids=set()
for coll in ('entries','natures'):
    for e in d[coll]:
        assert e['id'] not in ids, e['id']; ids.add(e['id'])
        ok=book_text.quote_on_page(e['book'],e['page'],e['quote'])
        e['quote_checked']=bool(ok)
        if not ok: bad.append((e['id'],e['book'],e['page'],e['quote']))
        if coll=='entries':
            e.setdefault('timing',False); e.setdefault('skip',None); e.setdefault('notes','')
            c=e.setdefault('condition',{})
            for k,v in (('own_major',[]),('own_major_only',False),('own_stars',[]),('branch',[]),('dignity',{}),('tam_phuong',[]),('with_any',[]),('not',[]),('tuan_triet',None),('other','')):
                c.setdefault(k,v)
        else:
            e.setdefault('notes','')
order=['id','book','page','palace','heading','full_line','quote','quote_checked','condition_text','condition','reading_vi','polarity','concepts','timing','skip','duplicate_of','notes']
ents=[{k:e[k] for k in order if k in e} | {k:v for k,v in e.items() if k not in order} for e in d['entries']]
norder=['id','kind','star','palace','book','page','quote','quote_checked','full_line','text','use','pol','explains','notes']
nats=[{k:e[k] for k in norder if k in e} | {k:v for k,v in e.items() if k not in norder} for e in d['natures']]
out={'source':d['source'],'pages_read':d['pages_read'],'entries':ents,'natures':nats}
json.dump(out,open(OUT,'w'),ensure_ascii=False,indent=1)
print('entries',len(ents),'natures',len(nats),'skipped',sum(1 for e in ents if e.get('skip')),'dups',sum(1 for e in ents if e.get('duplicate_of')))
for b in bad: print('QUOTE FAIL',b)
