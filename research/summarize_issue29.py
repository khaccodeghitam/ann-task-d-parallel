"""Descriptive strata only; does not refit or select the frozen models."""
import argparse
import json
from pathlib import Path
import statistics
from oracle_disagreement import load_rows, disagreement, cluster_ci, group_states


def summarize(path):
    rows=load_rows(path);groups=group_states(rows);strata={}
    for split in ('all','validation','test'):
        for step in (8,24):
            subset=[r for r in rows if r['step']==step and (split=='all' or r['split']==split)]
            d=disagreement(subset);strata[f'{split}_step{step}']={k:v for k,v in d.items() if k not in ('queries','states')}
    ranks=[];distance_penalties=[]
    for rs in groups.values():
        near=min(rs,key=lambda r:(r['distance_norm'],r['node']));best=min(rs,key=lambda r:(-r['Gk'],r['distance_norm'],r['node']))
        if best['Gk']-near['Gk']>1e-12:
            ranks.append(round(best['frontier_rank']*12)+1);distance_penalties.append(best['distance_norm']-near['distance_norm'])
    return dict(scope='Post-execution descriptive strata, no tuning or threshold change; timestamps are surrogate expansion steps, not ANN phases.',
        strata=strata,beneficial_oracle_rank_histogram={str(r):ranks.count(r) for r in sorted(set(ranks))},
        median_normalized_distance_penalty=statistics.median(distance_penalties) if distance_penalties else 0,
        count_beneficial_states=len(ranks))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rows',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError('New output required')
    a.output.write_text(json.dumps(summarize(a.rows),indent=2)+'\n')
