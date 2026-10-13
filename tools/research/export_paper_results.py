#!/usr/bin/env python3
"""Regenerate compact CSV/JSON/SVG without ANN execution; explicit provisional opt-in."""
import argparse,csv,json
from pathlib import Path
from paper_paired_campaign import summarize,summarize_uncertified
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--campaign',required=True,type=Path);p.add_argument('--output',required=True,type=Path);p.add_argument('--provisional',action='store_true');a=p.parse_args()
s=(summarize_uncertified if a.provisional else summarize)(a.campaign);rows=s.pop('records',s.pop('runs',[]));a.output.mkdir(parents=True,exist_ok=False)
(a.output/'SUMMARY.json').write_text(json.dumps(s,indent=2)+'\n')
keys=['sequence','block','T','W','L','run_id','status','qps','mean_latency_us','p999_latency_us','recall','mean_ios']
with (a.output/'runs.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=keys,lineterminator='\n');w.writeheader()
 for r in rows:w.writerow({**{k:r[k] for k in keys if k in r},**{k:r['metrics'][k] for k in keys if k in r['metrics']},'status':'UNCERTIFIED' if a.provisional else r['status']})
points=' '.join(f"{60+i*35},{300-(r['metrics']['qps']-1500)/5000*250:.2f}" for i,r in enumerate(rows))
label='UNCERTIFIED' if a.provisional else 'VALID'
(a.output/'chronological_qps.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="380"><rect width="100%" height="100%" fill="white"/><text x="40" y="25">{label}: chronological QPS; baseline1500, vertical span5000</text><path d="M60 50V300H1350" fill="none" stroke="black"/><polyline points="{points}" fill="none" stroke="#2463a0"/></svg>')
