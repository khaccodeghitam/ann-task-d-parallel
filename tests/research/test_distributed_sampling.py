"""G0-C1 protocol tests use bounded synthetic traces and a fake benchmark."""
import copy
import csv
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from jsonschema import Draft202012Validator
from test_causal_trace import raw_trace, trace, runner, CAUSAL_OPTIONS, REPO, valid_events
import test_run_ann_experiment as fixtures
from test_run_ann_experiment import TABLE
from trace_sampling import parse_explicit_qids, explicit_policy, requested_ids


def v2_raw(dropped=0):
    old=raw_trace(dropped=dropped)
    fields=list(trace.HEADER.unpack_from(old)); fields[0:2]=[b'PANTRC02',2]
    policy=explicit_policy([0],1)
    return trace.HEADER.pack(*fields)+struct.pack('<4Q',1,1,90,120)+struct.pack('<Q',0)+bytes.fromhex(policy['sha256'])+old[trace.HEADER.size:]


def manifest():
    return {'run_id':'synthetic','trace_mode':'DETAIL','query_count':1,'threads':1,'wcap':32,
            'trace_config':{'detail_first_n':1,'event_capacity':32,'sample_policy':explicit_policy([0],1)}}


class SamplingTests(unittest.TestCase):
    def test_canonical_digest(self):
        p=parse_explicit_qids('0,4,9',10)
        self.assertEqual(p['sha256'],hashlib.sha256(b'0,4,9\n').hexdigest())
        self.assertEqual(requested_ids(p,10,'DETAIL'),[0,4,9])

    def test_malformed_configuration(self):
        for text in ('','1,1','2,1','10','-1','+1','01','0,','0,,1','0, 1','0,１','1\n','x','9'*100):
            with self.subTest(text=text),self.assertRaises(ValueError):parse_explicit_qids(text,10)

    def test_count_bound(self):
        with self.assertRaises(ValueError):parse_explicit_qids(','.join(map(str,range(1025))),2000)

    def test_text_bound(self):
        with self.assertRaises(ValueError):parse_explicit_qids('1'*16385,10)

    def test_query_bound(self):
        with self.assertRaises(ValueError):parse_explicit_qids('0',1000001)

    def test_types_and_range(self):
        for ids in ([True],[1.0],[-1],[10],[2,1],[1,1],[]):
            with self.subTest(ids=ids),self.assertRaises(ValueError):explicit_policy(ids,10)

    def test_digest_tampering(self):
        p=explicit_policy([0],1);p['sha256']='0'*64
        with self.assertRaises(ValueError):requested_ids(p,1,'DETAIL')

    def test_explicit_requires_detail(self):
        for mode in ('OFF','LIGHT'):
            with self.assertRaises(ValueError):requested_ids(explicit_policy([0],1),1,mode)

    def test_legacy_first_n(self):
        self.assertEqual(requested_ids({'kind':'first_n','first_n':4},2,'DETAIL'),[0,1])
        self.assertEqual(requested_ids({'kind':'first_n','first_n':4},2,'LIGHT'),[])

    def test_exact_membership(self):
        self.assertTrue(trace.check_events(valid_events(),expected_qids=[0])['trace_valid'])
        for ids in ([1],[0,1],[],[0,0]):
            self.assertFalse(trace.check_events(valid_events(),expected_qids=ids)['trace_valid'])


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def export(self,raw=None,m=None):
        (self.root/'ann_trace.bin').write_bytes(v2_raw() if raw is None else raw)
        return trace.export_trace(self.root,manifest() if m is None else m)
    def checker(self):
        return subprocess.run([sys.executable,str(REPO/'tools/research/check_causal_trace.py'),str(self.root/'events.jsonl'),'--health',str(self.root/'trace_health.json')],capture_output=True,text=True)

    def test_valid_v2_health_schema_phase(self):
        h=self.export();self.assertTrue(h['trace_valid'],h)
        self.assertEqual(h['requested_sample_qids'],[0]);self.assertEqual(h['observed_sample_qids'],[0])
        self.assertEqual(h['sampled_query_phase'][0],{'query_id':0,'start_relative_ns':10,'end_relative_ns':18})
        self.assertEqual(self.checker().returncode,0)
        Draft202012Validator(json.loads((REPO/'schemas/research/causal_trace_health.schema.json').read_text())).validate(h)
        events=[json.loads(l) for l in (self.root/'events.jsonl').read_text().splitlines()]
        validator=Draft202012Validator(json.loads((REPO/'schemas/research/causal_events.schema.json').read_text()))
        for e in events:validator.validate(e)

    def test_v1_unchanged_schema(self):
        m=manifest();m['trace_config'].pop('sample_policy')
        h=self.export(raw_trace(),m);self.assertTrue(h['trace_valid']);self.assertEqual(h['schema_version'],2)
        e=json.loads((self.root/'events.jsonl').read_text().splitlines()[0]);self.assertNotIn('benchmark_relative_ns',e)

    def test_raw_digest_corruption(self):
        raw=bytearray(v2_raw());raw[trace.HEADER.size+32+8]^=1
        self.assertFalse(self.export(raw)['trace_valid'])

    def test_raw_unknown_policy(self):
        raw=bytearray(v2_raw());struct.pack_into('<Q',raw,trace.HEADER.size,2)
        self.assertFalse(self.export(raw)['trace_valid'])

    def test_raw_out_of_range_id(self):
        raw=bytearray(v2_raw());struct.pack_into('<Q',raw,trace.HEADER.size+32,1)
        self.assertFalse(self.export(raw)['trace_valid'])

    def test_raw_truncation(self):
        self.assertFalse(self.export(v2_raw()[:-1])['trace_valid'])

    def test_raw_wrong_phase(self):
        raw=bytearray(v2_raw());struct.pack_into('<Q',raw,trace.HEADER.size+16,110)
        self.assertFalse(self.export(raw)['trace_valid'])

    def test_manifest_identity_mismatch(self):
        m=manifest();m['trace_config']['sample_policy']={'kind':'first_n','first_n':1}
        self.assertFalse(self.export(m=m)['trace_valid'])

    def test_missing_sample_flag(self):
        raw=bytearray(v2_raw());offset=trace.HEADER.size+32+8+32+10*34*8
        struct.pack_into('<Q',raw,offset+3*8,0)
        self.assertFalse(self.export(raw)['trace_valid'])

    def test_sample_missing_end(self):
        events=valid_events();events.pop(-2)
        old=raw_trace(events);fields=list(trace.HEADER.unpack_from(old));fields[:2]=[b'PANTRC02',2]
        raw=trace.HEADER.pack(*fields)+v2_raw()[trace.HEADER.size:trace.HEADER.size+72]+old[trace.HEADER.size:]
        self.assertFalse(self.export(raw)['trace_valid'])

    def test_event_drops_invalid(self):
        self.assertFalse(self.export(v2_raw(dropped=1))['trace_valid'])

    def test_health_digest_tampering_checker(self):
        h=self.export();h['sampling_sha256']='0'*64;(self.root/'trace_health.json').write_text(json.dumps(h))
        self.assertEqual(self.checker().returncode,1)

    def test_health_extra_member_checker(self):
        h=self.export();h['observed_sample_qids']=[0,1];(self.root/'trace_health.json').write_text(json.dumps(h))
        self.assertEqual(self.checker().returncode,1)

    def test_relative_timestamp_tampering_checker(self):
        self.export();p=self.root/'events.jsonl';events=[json.loads(l) for l in p.read_text().splitlines()];events[0]['benchmark_relative_ns']+=1;p.write_text(''.join(json.dumps(e)+'\n' for e in events))
        self.assertEqual(self.checker().returncode,1)

    def test_forged_valid_health_nonzero_drop_checker(self):
        h=self.export();h['events_dropped']=1;(self.root/'trace_health.json').write_text(json.dumps(h))
        self.assertEqual(self.checker().returncode,1)


class HarnessSamplingTests(unittest.TestCase):
    def setUp(self):
        self.fixture=fixtures.RunnerTests();self.fixture.setUp()
    def tearDown(self):self.fixture.tearDown()
    def args(self,*extra):
        return runner.parser().parse_args(self.fixture.cli(*CAUSAL_OPTIONS,'--no-host-telemetry',*extra))
    def test_distributed_fake_benchmark_success(self):
        f=self.fixture
        f.executable.write_text('#!/usr/bin/env python3\nimport os\nfrom pathlib import Path\nassert os.environ["PIPEANN_TRACE_SAMPLE_QIDS"]=="0"\nPath(os.environ["PIPEANN_TRACE_OUTPUT"]).write_bytes('+repr(v2_raw())+')\nprint('+repr(TABLE)+')\n')
        code,result=f.execute(*CAUSAL_OPTIONS,'--no-host-telemetry','--trace-sample-policy','explicit_qids','--trace-sample-qids','0')
        self.assertEqual(code,0);p=Path(result['run_directory']);m=json.loads((p/'manifest.json').read_text());s=json.loads((p/'summary.json').read_text())
        self.assertEqual(m['trace_sample_sha256'],explicit_policy([0],1)['sha256']);self.assertEqual(m['trace_sample_count'],1)
        self.assertEqual(m['trace_config']['protocol'],'PANTRC02/v2');self.assertEqual(s['run_status'],'success');self.assertTrue(s['trace_valid'])
        Draft202012Validator(json.loads((REPO/'schemas/research/manifest.schema.json').read_text())).validate(m)
        with (f.evidence/'summaries/run_index.csv').open() as stream:row=next(csv.DictReader(stream))
        self.assertEqual(row['trace_sample_sha256'],m['trace_sample_sha256'])
    def test_invalid_explicit_configuration_rejected(self):
        for extra in (['--trace-sample-policy','explicit_qids'],['--trace-sample-policy','explicit_qids','--trace-sample-qids','1'],['--trace-sample-qids','0'],['--trace-sample-policy','explicit_qids','--trace-sample-qids','0','--trace-mode','LIGHT']):
            with self.subTest(extra=extra),self.assertRaises(ValueError):runner.resolve(self.args(*extra))
    def test_first_n_clears_ambient_explicit(self):
        args=runner.resolve(self.args());env=runner.trace_environment(args,Path('/tmp/synthetic'))
        self.assertIsNone(env['PIPEANN_TRACE_SAMPLE_POLICY']);self.assertIsNone(env['PIPEANN_TRACE_SAMPLE_QIDS'])
    def test_historical_status_index_migration(self):
        f=self.fixture;(f.evidence/'summaries').mkdir(parents=True);path=f.evidence/'summaries/run_index.csv'
        with path.open('w',newline='') as stream:
            writer=csv.DictWriter(stream,runner.V2_STATUS_INDEX_COLUMNS);writer.writeheader();writer.writerow({'run_id':'historical','run_status':'success'})
        runner.update_run_index(f.evidence,{'run_id':'new','trace_sample_policy':'explicit_qids'},{'run_status':'success'})
        with path.open() as stream:rows=list(csv.DictReader(stream))
        self.assertEqual(rows[0]['trace_sample_policy'],'');self.assertEqual(rows[0]['run_status'],'success')

    def test_mlflow_sampling_identity_small_only(self):
        import types
        import mlflow_mirror
        f=self.fixture;f.executable.write_text('#!/usr/bin/env python3\nimport os\nfrom pathlib import Path\nPath(os.environ["PIPEANN_TRACE_OUTPUT"]).write_bytes('+repr(v2_raw())+')\nprint('+repr(TABLE)+')\n')
        code,result=f.execute(*CAUSAL_OPTIONS,'--no-host-telemetry','--trace-sample-policy','explicit_qids','--trace-sample-qids','0')
        self.assertEqual(code,0);directory=Path(result['run_directory'])
        client=mock.Mock();client.get_experiment_by_name.return_value=types.SimpleNamespace(experiment_id='1')
        client.get_experiment.return_value=types.SimpleNamespace(artifact_location=(f.evidence/'mlflow/artifacts').as_uri())
        client.create_run.return_value=types.SimpleNamespace(info=types.SimpleNamespace(run_id='mirror'))
        with mock.patch.dict(sys.modules,{'mlflow':types.SimpleNamespace(MlflowClient=lambda **kw:client)}), mock.patch.dict(os.environ):
            mirrored=mlflow_mirror.mirror(directory,f.evidence)
        self.assertEqual(mirrored['status'],'success')
        client.log_param.assert_any_call('mirror','trace_sample_sha256',explicit_policy([0],1)['sha256'])
        client.set_tag.assert_any_call('mirror','trace_sample_policy','explicit_qids')
        self.assertEqual({Path(c.args[1]).name for c in client.log_artifact.call_args_list},{'summary.json','command.sh'})


class SmokeValidationTests(unittest.TestCase):
    def setUp(self):
        import analyze_g0c1
        self.analyzer=analyze_g0c1;self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.plan={'detail_smoke':{'qids':[0]},'search':{'query_count':1},'harness_commit':'harness',
                   'subjects':{'instrumented':{'commit':'subject','binary_sha256':'binary'}},
                   'input_package_sha256':'input','index_package_sha256':'index','trace_health_zero_fields':list(trace.FAILURE_COUNTERS)}
        self.m=manifest();self.m.update(harness_git_commit='harness',harness_git_dirty=False,subject_git_commit='subject',subject_git_dirty=False,
            executable_sha256='binary',input_package_manifest_sha256='input',index_package_manifest_sha256='index',
            causal_trace_enabled=True,environment={'OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'8','OMP_DYNAMIC':'FALSE'},mlflow_run_id='mirror')
        (self.root/'ann_trace.bin').write_bytes(v2_raw());self.h=trace.export_trace(self.root,self.m)
        self.summary={'benchmark_status':'success','run_status':'success','trace_valid':True}
    def tearDown(self):self.temp.cleanup()
    def validate(self):
        for name,obj in [('manifest',self.m),('summary',self.summary),('trace_health',self.h)]:
            (self.root/(name+'.json')).write_text(json.dumps(obj))
        runner.checksums(self.root)
        return self.analyzer.validate_smoke(self.root,self.plan,1)
    def test_valid_smoke(self):self.assertTrue(self.validate()['trace_valid'])
    def test_wrong_subject(self):
        self.m['subject_git_commit']='wrong'
        with self.assertRaises(ValueError):self.validate()
    def test_wrong_package(self):
        self.m['input_package_manifest_sha256']='wrong'
        with self.assertRaises(ValueError):self.validate()
    def test_wrong_placement(self):
        self.m['environment']['OMP_PROC_BIND']='spread'
        with self.assertRaises(ValueError):self.validate()
    def test_extra_sample(self):
        self.h['observed_sample_qids']=[0,1]
        with self.assertRaises(ValueError):self.validate()
    def test_trace_failure(self):
        self.h['events_dropped']=1
        with self.assertRaises(ValueError):self.validate()
    def test_missing_query_row(self):
        self.h['query_rows']=0
        with self.assertRaises(ValueError):self.validate()
