import sys
import unittest
import csv
import json
import struct
import tempfile
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools/research'))
from paper_native_v3 import SafetyGuard, block_validity, check_diagnostics, quality_against_canonical, verify_native_package
from paper_rebaseline import canonical_bytes, digest, run_order
import run_paper_native_v3_suite as suite
from finalize_paper_native_index import validate_structure, finalize
from analyze_paper_native_v3 import analyze


def snapshot(t=0, pl1='115000000'):
    return dict(timestamp=str(t), monotonic_s=t, mem_available=10*2**30,
                free_disk=100*2**30, power={'AC': '1'}, rapl={'PL1': pl1},
                ann=[], sensors={}, swap_used=0)


class NativeV3Tests(unittest.TestCase):
    def test_benign_policy_does_not_stop_build(self):
        self.assertEqual(SafetyGuard(snapshot()).check(snapshot(5, '105000000')), [])

    def test_ac_loss_still_stops(self):
        s = snapshot(); s['power']['AC'] = '0'
        self.assertIn('AC online state changed', SafetyGuard(snapshot()).check(s))

    def test_memory_guard(self):
        s = snapshot(); s['mem_available'] = 2**30
        self.assertTrue(SafetyGuard(snapshot()).check(s))

    def test_thermal_guard(self):
        s = snapshot(); s['sensors'] = {'cpu': dict(value_C=98, critical_mC='100000', name='coretemp', label='Package')}
        self.assertTrue(SafetyGuard(snapshot()).check(s))

    def test_foreign_ann_guard(self):
        s = snapshot(); s['ann'] = [{'pid': 42}]
        self.assertTrue(SafetyGuard(snapshot()).check(s, 1))
        self.assertFalse(SafetyGuard(snapshot()).check(s, 42))

    def test_policy_transition_confounds_whole_block(self):
        result = block_validity([snapshot(), snapshot(5, '105000000'), snapshot(10)])
        self.assertEqual(result['status'], 'ENV_CONFOUNDED')
        self.assertEqual(len(result['transitions']), 2)

    def test_between_block_transition_not_automatic_invalidation(self):
        self.assertEqual(block_validity([snapshot(), snapshot(5)])['status'], 'COMPARABLE')
        self.assertEqual(block_validity([snapshot(10, '105000000'), snapshot(15, '105000000')])['status'], 'COMPARABLE')

    def test_no_observations_is_unknown(self):
        self.assertEqual(block_validity([])['status'], 'UNKNOWN')

    def test_unavailable_power_evidence_unknown(self):
        s=snapshot();s['rapl']={}
        self.assertEqual(block_validity([s])['status'],'UNKNOWN')

    def test_exit_zero_does_not_hide_read_failure(self):
        for message in ('ERROR. Found point with no out-neighbors','Failed Bad file descriptor','EBADF'):
            with self.assertRaises(ValueError):check_diagnostics(message)
        check_diagnostics('Calculated num_pq_chunks :32')

    def test_sustained_swap_still_stops(self):
        guard=SafetyGuard(snapshot());s=snapshot();s['swap_used']=65*2**20
        self.assertFalse(guard.check(s));s['monotonic_s']=10
        self.assertTrue(guard.check(s))

    def test_all_result_exact_distances_and_independent_recall(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'base').write_bytes(struct.pack('<II',3,128)+bytes(128)+bytes([1])*128+bytes([2])*128)
            (p/'query').write_bytes(struct.pack('<II',1,128)+bytes(128))
            (p/'GT').write_bytes(struct.pack('<II',1,3)+struct.pack('<3I',0,1,2)+struct.pack('<3f',0,128,512))
            (p/'out').write_text('query_id,returned,rank,node_id,distance,latency_us,io_count\n0,2,0,0,0,10,2\n0,2,1,1,128,10,2\n')
            result=quality_against_canonical(p/'out',p/'base',p/'query',p/'GT',1,2,3)
            self.assertEqual(result['recall'],100);self.assertEqual(result['exact_squared_L2_checked'],2)
            (p/'out').write_text((p/'out').read_text().replace(',128,10,',',127,10,'))
            with self.assertRaisesRegex(ValueError,'squared-L2 mismatch'):
                quality_against_canonical(p/'out',p/'base',p/'query',p/'GT',1,2,3)

    def test_native_schema_and_checksum_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'INDEX_PACKAGE.json';p.write_bytes(canonical_bytes({'schema':'unsupported'}))
            p.with_suffix('.sha256').write_text(digest(p)+'  '+p.name+'\n')
            with self.assertRaisesRegex(ValueError,'schema'):verify_native_package(p)
            p.write_bytes(p.read_bytes()+b' ')
            with self.assertRaisesRegex(ValueError,'digest'):verify_native_package(p)

    def test_native_disk_records_coordinates_edges_and_pq(self):
        import numpy as np
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);prefix=p/'index';n=10;dimension=128;r=4;stride=dimension+4*(r+1);slots=4096//stride
            vectors=np.arange(n*dimension,dtype=np.uint8).reshape(n,dimension)
            (p/'base').write_bytes(struct.pack('<II',n,dimension)+vectors.tobytes())
            header=struct.pack('<II9Q',9,1,n,dimension,0,stride,slots,0,0,8192,8192)
            data=bytearray(4096)
            for i in range(n):
                start=i*stride;data[start:start+dimension]=vectors[i].tobytes()
                struct.pack_into('<3I',data,start+dimension,2,(i+1)%n,(i+2)%n)
            disk=Path(str(prefix)+'_disk.index');disk.write_bytes(header.ljust(4096,b'\0')+data)
            Path(str(prefix)+'_pq_compressed.bin').write_bytes(struct.pack('<II',n,32)+bytes(n*32))
            result=validate_structure(prefix,p/'base',n,dimension,r)
            self.assertEqual(result['nodes_checked'],10);self.assertTrue(result['all_coordinates_equal_canonical'])
            struct.pack_into('<I',data,dimension+4,n)
            disk.write_bytes(header.ljust(4096,b'\0')+data)
            with self.assertRaisesRegex(ValueError,'Out-of-range'):validate_structure(prefix,p/'base',n,dimension,r)

    def test_failed_build_cannot_be_finalized(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'BUILD_PLAN.json').write_text(json.dumps({'prefix':str(p/'index')}));(p/'disk_build').mkdir()
            (p/'disk_build/manifest.json').write_text(json.dumps({'exit_code':-15,'guard_failure':'thermal'}))
            with self.assertRaisesRegex(ValueError,'Incomplete/failed'):finalize(p)

    def synthetic_suite(self,p,fail_sequence=None,missing_telemetry=False):
        plan=dict(protocol='PAPER_NATIVE_V3_STOCK_v1',execution_ready=True,order=run_order(),subjects={v:dict(binary='FAKE',prefix='FAKE',mem_L=10 if v=='PAPER' else 0,commit='test',tree='test',binary_sha256='test',index_sha256='test',profile=v) for v in ('PAPER','MODERN')},
                  query='FAKE',truth='FAKE',input_sha256='test',suite_timeout_s=100,per_run_timeout_s=10,secondary_min_comparable_blocks=4,
                  minimum_primary_recall_percent=90,between_block_pause_s=15,within_block_pause_s=5)
        (p/'PLAN.json').write_bytes(canonical_bytes(plan));(p/'PLAN.sha256').write_text(digest(p/'PLAN.json')+'  PLAN.json\n')
        def fake_execute(spec,directory):
            directory.mkdir();(directory/'host.jsonl').write_text(json.dumps(snapshot())+'\n')
            if spec['sequence']==fail_sequence:raise ValueError('synthetic thermal stop')
            (directory/'stdout.log').write_text(f"{spec['l_search']} {spec['wcap']} 5000 1500 3000 0 100 98\n")
            (directory/'stderr.log').write_text('')
            manifest=dict(spec,exit_code=0,wall_time_s=1,initial_host=snapshot())
            (directory/'manifest.json').write_bytes(canonical_bytes(manifest))
            return manifest
        def fake_telemetry(*args):
            if missing_telemetry:raise ValueError('Required telemetry absent')
            return {'synthetic':True}
        with patch.object(suite,'validate_plan',return_value=True),patch.object(suite,'host_snapshot',side_effect=lambda *a:snapshot()),patch.object(suite,'execute',side_effect=fake_execute),patch.object(suite,'telemetry',side_effect=fake_telemetry),patch.object(suite.time,'sleep') as sleep,patch('builtins.print'):
            records=suite.run(p)
        return records,sleep

    def test_full_fake_66_order_and_fixed_pauses(self):
        with tempfile.TemporaryDirectory() as d:
            records,sleep=self.synthetic_suite(Path(d))
            self.assertEqual([r['cell'] for r in records],[r['cell'] for r in run_order()])
            self.assertTrue(all(r['status']=='completed_quality_valid' for r in records))
            self.assertEqual(len(sleep.call_args_list),65)
            self.assertTrue(all(call.args[0] in (5,15) for call in sleep.call_args_list))
            self.assertEqual(len(json.loads((Path(d)/'blocks.json').read_text())),6)
            summary=analyze(Path(d))
            self.assertEqual(summary['completed_quality_valid'],66)
            self.assertEqual(summary['paired']['PAPER_T16/PAPER_T8']['qps']['result']['median'],0)
            with self.assertRaises(FileExistsError):suite.run(Path(d))

    def test_fake_failure_preserves_partial_evidence_no_retry(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);records,_=self.synthetic_suite(p,fail_sequence=3)
            self.assertEqual(len(records),3);self.assertEqual(records[-1]['status'],'invalid_or_interrupted')
            self.assertTrue((p/'runs'/records[-1]['run_id']/'host.jsonl').exists())
            self.assertEqual(json.loads((p/'EXECUTION.json').read_text())['not_run'],63)

    def test_missing_telemetry_fails(self):
        with tempfile.TemporaryDirectory() as d:
            records,_=self.synthetic_suite(Path(d),missing_telemetry=True)
            self.assertEqual(len(records),1);self.assertEqual(records[0]['status'],'invalid_or_interrupted')

    def test_block_policy_cannot_pass_invalid_plan(self):
        for plan in ({'protocol':'other'}, {'protocol':'PAPER_NATIVE_V3_STOCK_v1','execution_ready':False}):
            with self.assertRaises(ValueError):suite.validate_plan(plan)

    def test_independent_analyzer_rejects_corruption(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);records,_=self.synthetic_suite(p,fail_sequence=2)
            directory=Path(records[0]['evidence'])
            (directory/'stdout.log').write_text('ERROR Failed Bad file descriptor\n')
            with self.assertRaisesRegex(ValueError,'Corrupt finalized'):analyze(p)

    def test_independent_analyzer_rejects_wrong_order(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);records,_=self.synthetic_suite(p,fail_sequence=2)
            records[0]['threads']=16;(p/'attempts.json').write_bytes(canonical_bytes(records))
            with self.assertRaisesRegex(ValueError,'order/config'):analyze(p)

    def fake_validated_plan(self,p):
        binaries={}
        subjects={}
        commits={'PAPER':'c4cd32c6816c063f56ecc64f9d7b63c909202cab','MODERN':'b9ec4ba86ff5d70bec277984777197f28dc2cf42'}
        for version,commit in commits.items():
            binary=p/version;binary.write_bytes(b'non-ANN fake executable identity')
            index=p/(version+'.index.json');index.write_text(version)
            subjects[version]=dict(binary=str(binary),binary_sha256=digest(binary),commit=commit,tree='tree',source_repo=version,index_manifest=str(index),index_sha256=digest(index))
        inp=p/'INPUT.json';inp.write_text('synthetic input identity')
        audits={}
        for name,sha in [('input',digest(inp)),('paper',subjects['PAPER']['index_sha256']),('modern',subjects['MODERN']['index_sha256'])]:
            file=p/(name+'.json');file.write_text(json.dumps(dict(exit_code=0,manifest_sha256=sha,argv=['verify','--full-components'])))
            audits[name]=str(file)
        quality={}
        for version in commits:
            f=p/(version+'.quality.json');f.write_text(json.dumps(dict(query_count=10000,exact_squared_L2_checked=100000,validation_pass=True)))
            quality[version]=dict(path=str(f),sha256=digest(f))
        return dict(protocol='PAPER_NATIVE_V3_STOCK_v1',execution_ready=True,order=run_order(),subjects=subjects,input_manifest=str(inp),input_sha256=digest(inp),wrapper_fingerprints={},pre_audits=audits,quality_validation=quality)

    def validate_with_mocked_prerequisites(self,plan):
        def git(argv,**kwargs):
            repo=argv[2]
            return plan['subjects'][repo]['commit']+'\ntree\n' if 'rev-parse' in argv else ''
        with patch.object(suite.subprocess,'check_output',side_effect=git),patch.object(suite,'load_verified',side_effect=[({},plan['input_sha256']),({},plan['subjects']['MODERN']['index_sha256'])]),patch.object(suite,'verify_native_package'):
            return suite.validate_plan(plan)

    def test_pre_audit_required_and_failure_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);plan=self.fake_validated_plan(p)
            self.assertTrue(self.validate_with_mocked_prerequisites(plan))
            Path(plan['pre_audits']['paper']).write_text(json.dumps(dict(exit_code=1,manifest_sha256='PAPER',argv=['verify','--full-components'])))
            with self.assertRaisesRegex(ValueError,'pre-audit'):self.validate_with_mocked_prerequisites(plan)

    def test_quality_incomplete_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);plan=self.fake_validated_plan(p);q=Path(plan['quality_validation']['PAPER']['path'])
            q.write_text(json.dumps(dict(query_count=9999,exact_squared_L2_checked=99990,validation_pass=True)))
            plan['quality_validation']['PAPER']['sha256']=digest(q)
            with self.assertRaisesRegex(ValueError,'quality validation'):self.validate_with_mocked_prerequisites(plan)

    def test_wrong_pinned_subject_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            plan=self.fake_validated_plan(Path(d));plan['subjects']['PAPER']['commit']='not-approved'
            with self.assertRaisesRegex(ValueError,'Pinned subject'):suite.validate_plan(plan)

    def test_wrong_binary_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            plan=self.fake_validated_plan(Path(d));plan['subjects']['PAPER']['binary_sha256']='0'*64
            with self.assertRaisesRegex(ValueError,'Binary mismatch'):suite.validate_plan(plan)


if __name__ == '__main__':
    unittest.main()
