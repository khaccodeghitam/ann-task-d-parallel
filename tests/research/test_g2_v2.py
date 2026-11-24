"""Dataset-free G2 remediation checks. No evaluator, host probing or profiling."""
from collections import Counter
import copy
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from research.task_da import g2_v2_analyzer as a
from research.task_da import g2_v2_contract as c
from research.task_da import g2_v2_guard as g
from research.task_da import g2_v2_runner as r


def cpu(t, host=0, own=0, monitor=0, name='desktop', start=4):
    return dict(monotonic_s=t,hz=100,host_busy_ticks=host,owned=dict(ticks=own,start=start),
                monitor=dict(ticks=monitor,start=7),owned_pid=100,monitor_pid=200,
                processes={'100':dict(comm='task_da_p2_eval',ticks=own,start=start),
                           '200':dict(comm='python',ticks=monitor,start=7),
                           '300':dict(comm=name,ticks=0,start=1)})


def fixture():
    rows=[];latency=np.empty((12,6,2,c.N))
    for b in range(12):
        for j,graph in enumerate(c.GRAPHS):
            for k,p in enumerate(('base','opt')):
                value=(3000+10*b+5*j)*(1 if p=='base' else .94)
                latency[b,j,k]=value
                rows.append(dict(block=b,graph=graph,policy=p,mode='OFF',valid=True,beam=432,
                                 observed_cpus=[0,2],query_count=c.N,mean_us=value,p50_us=value,
                                 p95_us=value,p99_us=value,qps_wall=1e6/value,rss_kib=850000,
                                 cpu_seconds=10,wall_seconds=10,cpu_percent=100,cpu_capacity_percent=50))
    return rows,latency,dict(A_pass=True,B_pass=True,B_authorized=True,parity=True,duplicate_reduction=True)


class RAMTests(unittest.TestCase):
    def test_exact_boundary_and_single_exceedance(self):
        self.assertTrue(a.ram_pair(100000,165536)['hard_pass'])
        self.assertFalse(a.ram_pair(100000,165537)['hard_pass'])
        self.assertTrue(a.ram_pair(1000000,1100000)['hard_pass'])
        self.assertFalse(a.ram_pair(1000000,1100001)['hard_pass'])

    def test_audit_counterexample_is_not_hidden_by_mean(self):
        v=np.array([2.]+[0.]*11)
        upper=v.mean()+a.tcrit(1-.05/18,11)*v.std(ddof=1)/math.sqrt(12)
        self.assertLess(upper,1)
        checks=[a.ram_pair(1000000,float(1000000+100000*x))['hard_pass'] for x in v]
        self.assertFalse(all(checks))

    def test_missing_invalid_rss_never_becomes_zero(self):
        for x in [None,0,-1,.5,float('nan'),float('inf'),True,'123']:
            with self.subTest(x=x),self.assertRaises(ValueError):a.ram_pair(x,1000)
            with self.subTest(x=x),self.assertRaises(ValueError):a.ram_pair(1000,x)


class CPUTests(unittest.TestCase):
    def test_quiet_preflight_logs_all_samples_without_host_probing(self):
        module=g.guard_module();sequence=iter(range(6))
        def sample(_):
            i=next(sequence)
            capture=cpu(i,host=10*i,own=0,monitor=10*i)
            capture['owned_pid']=None;del capture['processes']['100']
            return dict(monotonic_s=i,sensors={'t':dict(name='k10temp',label='Tctl',value_C=70,critical_mC='95000')},
                        power={'AC':'1'},mem_available=8*2**30,free_disk=40*2**30,swap_used=0,ann=[],
                        v2_cpu=capture)
        module.host_snapshot=sample
        with tempfile.TemporaryDirectory() as tmp,patch.object(g.time,'sleep'):
            path=Path(tmp)/'preflight.jsonl'
            result=g.quiet_preflight(module,tmp,log_path=path)
            self.assertEqual(result['monotonic_s'],5)
            self.assertEqual(len(path.read_text().splitlines()),6)

    def test_base_guard_resource_limits_survive_amd_extension(self):
        module=g.guard_module()
        s=dict(monotonic_s=0,sensors={'t':dict(name='k10temp',label='Tctl',value_C=70,critical_mC='95000')},
               power={'AC':'1'},mem_available=8*2**30,free_disk=40*2**30,swap_used=0,ann=[],v2_cpu=cpu(0))
        for field,value,expected in [('mem_available',2**30,'MemAvailable'),('free_disk',20*2**30,'Disk free'),
                                     ('power',{'AC':'0'},'AC')]:
            check=module.CoolingGuard(copy.deepcopy(s));bad=copy.deepcopy(s);bad[field]=value
            self.assertTrue(any(expected in why for why in check.check(bad)))
        check=module.CoolingGuard(copy.deepcopy(s));bad=copy.deepcopy(s);bad['swap_used']=65*2**20
        bad['monotonic_s']=1;check.check(bad);bad['monotonic_s']=11
        self.assertTrue(any('Swap growth' in why for why in check.check(bad)))

    def test_utilization_is_process_ticks_not_observer_and_can_exceed_100(self):
        captures=[cpu(i,host=200*i,own=180*i,monitor=20*i) for i in range(6)]
        result=g.cpu_metrics(captures)
        self.assertEqual(result['cpu_percent'],180)
        self.assertEqual(result['cpu_capacity_percent'],90)
        self.assertEqual(result['wall_seconds'],5)

    def test_noise_boundary_and_monitor_exclusion(self):
        for foreign,expected in [(2,False),(3,True)]:
            check=g.Contention();reasons=[]
            for i in range(6):
                reasons=check.observe(cpu(i,host=(190+foreign)*i,own=180*i,monitor=10*i))
            self.assertTrue(check.ready)
            self.assertEqual(bool(reasons),expected)

    def test_unknown_heavy_name_is_caught_by_host_aggregate(self):
        check=g.Contention(); reasons=[]
        for i in range(6): reasons=check.observe(cpu(i,host=220*i,own=180*i,monitor=10*i,name='unrecognized'))
        self.assertTrue(reasons)

    def test_named_benchmark_rejected_without_waiting_window(self):
        self.assertTrue(g.Contention().observe(cpu(0,name='stress-ng')))
        self.assertFalse(g.Contention().observe(cpu(0,name='desktop')))

    def test_gap_pid_reuse_negative_and_missing_samples(self):
        for after in [cpu(3,100,50),cpu(1,100,50,start=99),cpu(1,-1,0)]:
            with self.assertRaises(ValueError):g.interval(cpu(0),after)
        with self.assertRaises(ValueError):g.cpu_metrics([cpu(0)])
        with self.assertRaises(ValueError):g.cpu_metrics([cpu(i,host=0,own=0) for i in range(6)])

    def test_stat_comm_with_spaces_and_parenthesis(self):
        fields=['S']+['0']*40;fields[11]='101';fields[12]='23';fields[19]='44'
        value=g.parse_stat('123 (worker (odd)) '+' '.join(fields))
        self.assertEqual(value,dict(comm='worker (odd)',ticks=124,start=44))

    def test_thermal_fail_closed_and_exact_boundaries(self):
        def s(temp):return dict(sensors={'t':dict(name='k10temp',label='Tctl',value_C=temp)})
        self.assertFalse(g.amd_reasons(s(84.999)))
        self.assertTrue(g.amd_reasons(s(85)))
        self.assertFalse(g.amd_reasons(s(94.999),100))
        self.assertTrue(g.amd_reasons(s(95),100))
        for temp in [None,float('nan'),0,121,True]:self.assertTrue(g.amd_reasons(s(temp)))
        self.assertTrue(g.amd_reasons({'sensors':{}}))


class PlanAndAuthorizationTests(unittest.TestCase):
    def test_native_loader_overrides_are_not_silent_dependency_substitutions(self):
        c.require_default_loader({})
        for name in ('LD_PRELOAD','LD_LIBRARY_PATH','LD_AUDIT'):
            with self.subTest(name=name),self.assertRaises(ValueError):c.require_default_loader({name:'/synthetic/override'})

    def test_native_runtime_substitution_is_rejected_before_ann_inputs(self):
        f=dict(native_runtime_sha256={'/synthetic/libc.so':'a'*64},artifact_sha256={},graph_sha256={},validation_baseline={})
        artifacts={'graphs':{graph:'/not-opened/'+graph for graph in c.GRAPHS}}
        with patch.object(r,'sha',return_value='a'*64):r.verify_artifacts(f,artifacts)
        with patch.object(r,'sha',return_value='changed'),self.assertRaises(ValueError):r.verify_artifacts(f,artifacts)

    def test_partial_campaign_cannot_be_analyzed_as_go(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp)/'HOLD.json').write_text('{}')
            with self.assertRaises(ValueError):r.load_campaign(tmp)
            with self.assertRaises(ValueError):r.quality_context(Path(tmp)/'quality.json')

    def test_unsigned_template_is_not_authorization(self):
        template=json.loads((c.ROOT/'configs/axd_g2_v2_approval.UNAPPROVED.json').read_text())
        with self.assertRaises(ValueError):c.authorize(template,'f'*64,'a'*64,'quality','/future/raw')

    def test_process_metric_fixture_checks_raw_rss_cpu_and_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);item=dict(c.schedule()[0]);item.update(name=r.name(item),argv=['FIXTURE_NOT_EXECUTED'])
            visited,frontier=c.POLICIES[item['policy']]
            row=dict(mode='OFF',instrumentation=False,workers=2,sync_interval=16,beam=432,jobs=1,merge_impl='flat',
                     visited_policy=visited,frontier_mode=frontier,query_id=0,ids=list(range(10)),
                     squared_l2=list(map(float,range(10))),complete_top_k=True,counters=None,latency_ns=3000000)
            with (out/'beam_432_p2_OFF.jsonl').open('w') as stream:
                for i in range(c.N):row['query_id']=i;stream.write(json.dumps(row)+'\n')
            artifacts={'graphs':{item['graph']:'/fixture/graph'},'base':'/fixture/base','queries':'/fixture/queries','test':'/fixture/ids'}
            summary=dict(requested_cpus=[0,2],observed_cpus=[0,2],workers=2,sync_interval=16,jobs=1,k=10,entry=0,
                         warmup_count=100,query_count=c.N,mode='OFF',merge_impl='flat',graph_format='pipnn',
                         visited_policy=visited,frontier_mode=frontier,graph_path='/fixture/graph',base_path='/fixture/base',
                         query_path='/fixture/queries',vm_hwm_kib=850000,
                         runs=[dict(beam=432,batch_wall_ns=30000000000,qps_wall=c.N/30,
                                    latency_us=dict(mean=3000,p50=3000,p95=3000,p99=3000))])
            (out/'p2_eval_summary.json').write_text(json.dumps(summary))
            guard=dict(exit_code=0,guard_failure=None,host_samples=6,pid=100,process_start_ticks='4')
            (out/'manifest.json').write_text(json.dumps(guard))
            (out/'host.jsonl').write_text(''.join(json.dumps(dict(monotonic_s=i,v2_cpu=cpu(i,200*i,180*i,20*i)))+'\n' for i in range(6)))
            with patch.object(r,'ids',return_value=list(range(c.N))):
                result=r.process_result(item,out,artifacts,guard)
                self.assertEqual(result['cpu_percent'],180)
                self.assertEqual(result['rss_source'],'p2_eval_summary.vm_hwm_kib')
                summary['vm_hwm_kib']=-1;(out/'p2_eval_summary.json').write_text(json.dumps(summary))
                with self.assertRaises(ValueError):r.process_result(item,out,artifacts,guard)

    def test_component_hash_tamper_and_no_data_required_for_freeze(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'component.py').write_text('fixture\n')
            f=dict(protocol=c.PROTOCOL,revision=c.REVISION,beam=432,cpus=[0,2],workers=2,
                   components={'component.py':c.sha(root/'component.py')})
            path=root/'freeze.json';path.write_text(json.dumps(f))
            with patch.object(c,'ROOT',root):
                c.load_freeze(path,environment=False)
                (root/'component.py').write_text('tampered\n')
                with self.assertRaises(ValueError):c.load_freeze(path,environment=False)

    def test_balanced_schedule_and_fixed_argv(self):
        tasks=c.schedule();self.assertEqual(len(tasks),144)
        counts={graph:Counter() for graph in c.GRAPHS}
        for b in range(12):
            block=tasks[b*12:(b+1)*12]
            for pos in range(6):
                pair=block[pos*2:pos*2+2]
                self.assertEqual(pair[0]['graph'],pair[1]['graph'])
                counts[pair[0]['graph']][pos,tuple(i['policy'] for i in pair)]+=1
        self.assertTrue(all(len(x)==12 and set(x.values())=={1} for x in counts.values()))
        artifacts={k:'/missing/'+k for k in ['binary','base','queries','val','test','warmup']}
        artifacts['graphs']={graph:'/missing/'+graph for graph in c.GRAPHS}
        # No Path.read/open, guard, host capture or subprocess is needed for planning.
        with patch.object(Path,'open',side_effect=AssertionError('plan read an artifact')):
            p=r.plan(artifacts,'off','/future/raw')
        self.assertEqual(p[0]['argv'][p[0]['argv'].index('--beams')+1],'432')
        self.assertEqual(p[0]['argv'][p[0]['argv'].index('--cpu-list')+1],'0,2')
        self.assertEqual(len(r.plan(artifacts,'quality','/future/quality')),18)

    def test_no_implicit_off_authorization_or_package_substitution(self):
        approval=dict(schema=c.SCHEMA,owner='FIXTURE_ONLY',approved_at='2026-11-23T00:00:00+07:00',protocol=c.PROTOCOL,
                      revision=c.REVISION,freeze_sha256='f'*64,artifacts_sha256='a'*64,output_directory='/future/raw',
                      scope='QUALITY_ONLY',quota_s=3600,quiet_host_confirmed=True)
        self.assertEqual(c.authorize(approval,'f'*64,'a'*64,'quality','/future/raw'),'QUALITY_ONLY')
        with self.assertRaises(ValueError):c.authorize(approval,'f'*64,'a'*64,'off','/future/raw',quality_digest='q'*64)
        with self.assertRaises(ValueError):c.authorize(approval,'changed','a'*64,'quality','/future/raw')
        with self.assertRaises(ValueError):c.authorize(approval,'f'*64,'a'*64,'quality','/different')

    def test_write_never_overwrites(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'receipt.json';c.write_new(path,{'fixture':True})
            with self.assertRaises(FileExistsError):c.write_new(path,{'fixture':False})
            self.assertTrue(json.loads(path.read_text())['fixture'])


class StatisticalTests(unittest.TestCase):
    def test_exact_output_and_counter_invariants_fixture(self):
        counters=dict(distance_evaluations=15,unique_distance_evaluations=10,duplicate_distance_evaluations=5,
                      expansions=3,unique_expansions=3,duplicate_expansions=0,neighbor_attempts=20,
                      already_seen_attempts=6,frontier_insertions=10,sync_merge_count=2,
                      sync_wait_ns=0,barrier_wait_ns=0,merge_time_ns=0,worker_idle_ns=0,
                      per_worker_expansions=[2,1],per_worker_distance_evaluations=[8,7],per_worker_idle_rounds=[0,1])
        base=[dict(mode='ON',instrumentation=True,workers=2,sync_interval=16,beam=432,jobs=1,
                   merge_impl='flat',visited_policy='baseline',frontier_mode='full',query_id=i,
                   ids=list(range(10)),squared_l2=list(map(float,range(10))),complete_top_k=True,counters=copy.deepcopy(counters)) for i in range(2)]
        opt=copy.deepcopy(base)
        for row in opt:
            row.update(visited_policy='barrier_all_evaled',frontier_mode='incremental')
            row['counters'].update(distance_evaluations=11,duplicate_distance_evaluations=1,
                                   already_seen_attempts=10,per_worker_distance_evaluations=[6,5])
        self.assertEqual(a.pair_on(base,opt)['duplicate_l2_saved'],8)
        bad=copy.deepcopy(opt);bad[0]['squared_l2'][0]=1e-14
        with self.assertRaises(ValueError):a.pair_on(base,bad)
        bad=copy.deepcopy(opt);bad.reverse()
        with self.assertRaises(ValueError):a.pair_on(base,bad)
        bad=copy.deepcopy(opt);bad[0]['counters']['unique_expansions']=2
        with self.assertRaises(ValueError):a.pair_on(base,bad)

    def test_t_quantiles_and_geometric_not_arithmetic(self):
        self.assertAlmostEqual(a.tcrit(.975,11),2.200985160091638,10)
        self.assertAlmostEqual(a.tcrit(1-.05/18,11),3.436841338533786,10)
        b=np.array([1,1,1,1,1,100.]);opt=np.array([.9,.9,.9,.9,.9,99.9])
        self.assertGreater(a.reduction(float(np.log(b/opt).mean())),.03)
        self.assertLess(1-opt.mean()/b.mean(),.03)
        self.assertAlmostEqual(a.reduction(c.THETA),.03)

    def test_quality_floor_and_arm_equivalence_are_separate(self):
        recalls=np.ones((6,c.N))
        self.assertTrue(a.quality_gate(recalls)['A_pass'])
        self.assertTrue(a.quality_gate(recalls)['B_pass'])
        recalls[3:,:50]=0
        self.assertTrue(a.quality_gate(recalls)['A_pass'])
        self.assertFalse(a.quality_gate(recalls)['B_pass'])
        recalls[:]=.9
        self.assertFalse(a.quality_gate(recalls)['A_pass'])
        with self.assertRaises(ValueError):a.quality_gate(recalls[:,:10])

    def test_weighted_percentiles_match_explicit_sample_and_zero_weights(self):
        rng=np.random.default_rng(812)
        values=rng.uniform(.1,100,size=30);cluster=np.arange(30)//10
        counts=np.array([[3,0,0],[0,3,0],[0,0,3],[1,1,1],[2,0,1]])
        result=a.weighted_tails(values,cluster,counts)
        for row,count in zip(result,counts):
            explicit=np.repeat(values,count[cluster])
            np.testing.assert_allclose(row,np.quantile(explicit,[.95,.99],method='linear'),rtol=1e-14)
        with self.assertRaises(ValueError):a.weighted_tails(values,cluster,np.array([[1,0,0]]))

    def test_bootstrap_paired_seed_and_joint_process_variability(self):
        x=np.empty((4,2,2,20))
        for b in range(4):
            x[b,:,0]=np.arange(1,21)
            x[b,:,1]=np.arange(1,21)*(1-.03*b)
        query=a.bootstrap(x,joint=False,resamples=64,block_length=5)
        joint=a.bootstrap(x,joint=True,resamples=64,block_length=5)
        self.assertEqual(joint,a.bootstrap(x,joint=True,resamples=64,block_length=5))
        self.assertLess(query['primary_log_ci95'][1]-query['primary_log_ci95'][0],1e-12)
        self.assertGreater(joint['primary_log_ci95'][1]-joint['primary_log_ci95'][0],.001)

    def test_missing_pairs_invalid_telemetry_and_raw_mismatch_are_rejected(self):
        rows,latency,quality=fixture()
        with self.assertRaises(ValueError):a.analyze(rows[:-1],latency,quality)
        for key,value in [('valid',False),('rss_kib',0),('cpu_percent',1),('mean_us',1)]:
            bad=copy.deepcopy(rows);bad[0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):a.analyze(bad,latency,quality)
        with self.assertRaises(ValueError):a.analyze(rows,latency,dict(A_pass=False))

    def test_full_fixture_primary_and_hard_ram_hold_without_real_data(self):
        rows,latency,quality=fixture()
        # Use a small, deterministic bootstrap *only in fixture*; CLI production remains 10,000.
        real=a.bootstrap
        with patch.object(a,'bootstrap',side_effect=lambda x,**kw:real(x,resamples=64,**kw)):
            result=a.analyze(rows,latency,quality)
            c.validate_schema(result,'analysis')
            self.assertEqual(result['verdict'],'GO_A_FIXED_COHORT')
            self.assertAlmostEqual(result['primary_reduction'],.06)
            bad=copy.deepcopy(rows)
            next(row for row in bad if row['block']==0 and row['graph']==c.GRAPHS[0] and row['policy']=='opt')['rss_kib']=1100000
            result=a.analyze(bad,latency,quality)
            self.assertFalse(result['ram_hard_pass'])
            self.assertEqual(result['verdict'],'HOLD')

    def test_production_resample_count_and_build_search_fixture(self):
        rows,latency,quality=fixture()
        build={graph:dict(wall_s=42 if graph.startswith('stock') else 34,graph_bytes=200000000) for graph in c.GRAPHS}
        result=a.analyze(rows,latency,quality,build=build)
        self.assertEqual(result['joint_bootstrap']['resamples'],10000)
        self.assertEqual(result['joint_bootstrap']['query_block_length'],100)
        self.assertEqual(result['build_search']['status'],'GO_B_SYSTEM_FIXED_COHORT')
        c.validate_schema(result,'analysis')
        points=result['build_search']['contrasts']['fast_opt_vs_stock_base']['workloads']['100000']
        self.assertGreater(points['ci95_s'][0],0)
        self.assertEqual(a.build_search(np.ones((12,6,2)),{'B_pass':False},build,{})['status'],'HOLD_QUALITY_B')

    def test_exact_three_percent_is_hold_not_roundoff_go_or_pivot(self):
        rows,latency,quality=fixture()
        for row in rows:
            value=1000 if row['policy']=='base' else 970
            for field in ['mean_us','p50_us','p95_us','p99_us']:row[field]=value
        latency[:,:,0,:]=1000;latency[:,:,1,:]=970
        real=a.bootstrap
        with patch.object(a,'bootstrap',side_effect=lambda x,**kw:real(x,resamples=64,**kw)):
            self.assertEqual(a.analyze(rows,latency,quality)['verdict'],'HOLD')


if __name__=='__main__':unittest.main()
