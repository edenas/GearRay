"""Exact complete-route comparison against retained accepted measurements."""
from pathlib import Path
import argparse,csv,json
ROOT=Path(__file__).resolve().parents[2]
ap=argparse.ArgumentParser();ap.add_argument('--actual',type=Path,required=True);ap.add_argument('--accepted',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
def read(p):return {(r['scenario'],int(r['update'])):r for r in csv.DictReader(p.open(encoding='utf-8-sig',newline=''))}
a,b=read(args.accepted),read(args.actual/'frame-samples.csv');assert len(a)==len(b)==2880 and a.keys()==b.keys()
bad=[{'scenario':k[0],'update':k[1],'field':f} for k in a for f in a[k] if a[k][f]!=b[k].get(f)]
assert not bad,bad[:10]
assert all(int(r['unclosed_spans'])==0 and (r['slot1'],r['slot2'])==('1','2') for r in b.values())
out={'records':len(b),'mismatches':len(bad),'all_existing_columns_identical':True,'fields':list(next(iter(a.values()))),'closed_spans':True,'return_pages':[1,2],'cold_restarts':[{'scenario':k[0],'update':k[1],'count':int(r['world_initializations'])} for k,r in b.items() if int(r['world_initializations'])],'scope':'All warmup and measured rows retained; exact T counts and every old CSV column compared.'}
args.output.write_text(json.dumps(out,indent=2)+'\n');print('PASS',len(b),'records, all fields and whole-loop T counts identical')
