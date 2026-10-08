"""Immutable package tests use tiny native-format files, never real BigANN downloads."""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
import types
import unittest
from unittest import mock
from jsonschema import Draft202012Validator, ValidationError

REPO=Path(__file__).resolve().parents[2]
def module(name):
    spec=importlib.util.spec_from_file_location(name,REPO/'tools/research'/f'{name}.py')
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
package=module('package_manifest');sys.modules['package_manifest']=package;index_tool=module('finalize_bigann_index');runner=module('run_ann_experiment');mirror=module('mlflow_mirror');acquire=module('acquire_bigann_prefix')

class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.base=self.root/'base.bbin';self.base.write_bytes(struct.pack('<II',3,2)+bytes(6))
        self.query=self.root/'query.bbin';self.query.write_bytes(struct.pack('<II',1,2)+bytes(2))
        self.gt=self.root/'gt.bin';self.gt.write_bytes(struct.pack('<II',1,10)+struct.pack('<10I',*([1]*10))+bytes(40))
        self.prefix=self.root/'index';self.components={}
        for role,suffix in {'disk_index':'_disk.index','tags':'_disk.index.tags','pq_compressed':'_pq_compressed.bin','pq_pivots':'_pq_pivots.bin'}.items():
            p=Path(str(self.prefix)+suffix);p.write_bytes(b'synthetic not loaded');self.components[role]=p
        self.exe=self.root/'benchmark';self.exe.write_text('#!/usr/bin/env python3\nprint("L I/O Width QPS AvgLat(us) P99 Lat Mean Hops Mean IOs Recall@10\\n20 32 1000 100 200 10 10 95")\n');self.exe.chmod(0o755)
        self.input=self.root/'INPUT_PACKAGE.json';self.index=self.root/'INDEX_PACKAGE.json';self.evidence=self.root/'evidence'
        self.spec={'package_kind':'input','package_id':'tiny-v1','logical_dataset':'tiny','N':3,'D':2,'dtype':'uint8','metric':'l2',
                   'files':[{'role':'base','path':str(self.base),'vector_count':3,'dimension':2,'dtype':'uint8'},
                            {'role':'query','path':str(self.query),'vector_count':1,'dimension':2,'dtype':'uint8'},
                            {'role':'ground_truth','path':str(self.gt),'vector_count':1,'top_k':10,'dtype':'uint32_ids_float32_distances'}],
                   'source_provenance':[{'source_url':'https://example.test/fixture','acquisition_method':'synthetic'}],
                   'conversion':[{'exact_command':'synthetic identity','tool_commit':'test','tool_binary_sha256':'0'*64}]}
        self.input_hash=package.finalize(self.spec,self.input)
        build={key:'test' for key in ('builder_commit','command','timestamp_start','timestamp_end','log_path')}
        build.update(builder_binary_sha256='0'*64,log_sha256='1'*64,wall_time_s=1)
        self.indexspec={'package_kind':'index','package_id':'tiny-index-v1','logical_dataset':'tiny','N':3,'D':2,'dtype':'uint8','metric':'l2',
             'input_package_manifest_sha256':self.input_hash,'index_prefix':str(self.prefix),'build':build,
             'parameters':{'R':64,'L':100,'pq_bytes':32,'memory_budget_GiB':8,'threads':8,'metric':'l2','neighbor_type':'pq','algorithm':'Vamana'},
             'files':[{'role':role,'path':str(p),'dtype':'opaque'} for role,p in self.components.items()]}
        self.index_hash=package.finalize(self.indexspec,self.index)
    def tearDown(self):self.temp.cleanup()
    def cli(self,*extra):
        return ['--executable',str(self.exe),'--benchmark-profile','pipeann-b9ec4ba','--dataset-id','tiny','--dataset-path',str(self.base),
                '--data-type','uint8','--query',str(self.query),'--ground-truth',str(self.gt),'--index-prefix',str(self.prefix),
                '--neighbor-type','pq','--mem-l','0','--evidence-root',str(self.evidence),*extra]
    def bound(self,*extra):return self.cli('--input-package-manifest',str(self.input),'--index-package-manifest',str(self.index),*extra)
    def execute(self,argv):
        with contextlib.redirect_stdout(io.StringIO()) as output:code=runner.run(runner.parser().parse_args(argv))
        return code,json.loads(output.getvalue())
    def rewrite(self,path,value):
        raw=package.serialize(value);path.write_bytes(raw);path.with_suffix('.sha256').write_text(hashlib.sha256(raw).hexdigest()+'  '+path.name+'\n')
    def test_schema_and_runtime_validation(self):
        schema=json.loads((REPO/'schemas/research/package.schema.json').read_text());Draft202012Validator.check_schema(schema)
        for path in (self.input,self.index):
            value,digest=package.load_verified(path);Draft202012Validator(schema).validate(value);self.assertEqual(digest,package.digest_file(path))
            del value['schema_version']
            with self.assertRaises(ValidationError):Draft202012Validator(schema).validate(value)
            with self.assertRaises(ValueError):package.validate_manifest(value)
    def test_serialization_is_deterministic(self):
        self.assertEqual(package.serialize({'z':2,'a':1}),package.serialize({'a':1,'z':2}))
        with self.assertRaises(ValueError):package.serialize({'bad':float('nan')})
    def test_sha_verification_rejects_corruption(self):
        self.input.write_bytes(self.input.read_bytes()+b' ')
        with self.assertRaisesRegex(ValueError,'SHA256'):package.load_verified(self.input)
    def test_corrupt_json_and_wrong_schema_rejected_even_with_matching_sha(self):
        raw=b'{broken';self.input.write_bytes(raw);self.input.with_suffix('.sha256').write_text(hashlib.sha256(raw).hexdigest()+'  '+self.input.name+'\n')
        with self.assertRaisesRegex(ValueError,'Corrupt'):package.load_verified(self.input)
        value=json.loads(self.index.read_text());value['schema_version']=99;self.rewrite(self.index,value)
        with self.assertRaisesRegex(ValueError,'schema'):package.load_verified(self.index)
    def test_no_overwrite(self):
        before=self.input.read_bytes()
        with self.assertRaises(FileExistsError):package.finalize(self.spec,self.input)
        self.assertEqual(before,self.input.read_bytes())
    def test_large_entry_has_required_full_digest(self):
        value=json.loads(self.index.read_text());value['files'][0]['size_bytes']=10*2**30
        package.validate_manifest(value)
        value['files'][0]['sha256']=None
        with self.assertRaises(ValueError):package.validate_manifest(value)
    def test_finalize_hashes_each_component_exactly_once(self):
        with mock.patch.object(package,'digest_file',wraps=package.digest_file) as digest:
            package.finalize(self.spec,self.root/'second.json')
        self.assertEqual(digest.call_count,3)
    def test_binding_does_not_rehash_components(self):
        args=runner.resolve(runner.parser().parse_args(self.bound()))
        with mock.patch.object(package,'digest_file',side_effect=AssertionError('component rehash')):
            result=package.bindings(args)
        self.assertEqual(result['input_package_manifest_sha256'],self.input_hash)
        self.assertEqual(result['index_package_manifest_sha256'],self.index_hash)
    def test_bound_dry_run_is_side_effect_free(self):
        code,result=self.execute(self.bound('--dry-run'));self.assertEqual(code,0);self.assertFalse(self.evidence.exists())
        self.assertEqual(result['input_package_manifest_sha256'],self.input_hash)
    def test_path_role_mismatch_rejected(self):
        other=self.root/'other.bbin';other.write_bytes(self.query.read_bytes())
        with self.assertRaisesRegex(ValueError,'Query/GT'):runner.resolve(runner.parser().parse_args(self.bound('--query',str(other))))
        othergt=self.root/'othergt';othergt.write_bytes(self.gt.read_bytes())
        with self.assertRaisesRegex(ValueError,'Query/GT'):runner.resolve(runner.parser().parse_args(self.bound('--ground-truth',str(othergt))))
    def test_index_dependency_and_component_roles_rejected(self):
        value=json.loads(self.index.read_text());value['input_package_manifest_sha256']='a'*64;self.rewrite(self.index,value)
        with self.assertRaisesRegex(ValueError,'different input'):runner.resolve(runner.parser().parse_args(self.bound()))
        value['input_package_manifest_sha256']=self.input_hash
        value['files'][0]['role'],value['files'][1]['role']=value['files'][1]['role'],value['files'][0]['role'];self.rewrite(self.index,value)
        with self.assertRaisesRegex(ValueError,'role mismatch'):runner.resolve(runner.parser().parse_args(self.bound()))
    def test_changed_component_rejected_without_rehash(self):
        self.query.write_bytes(self.query.read_bytes())
        stat=self.query.stat();os.utime(self.query,ns=(stat.st_atime_ns,stat.st_mtime_ns+1000000))
        with self.assertRaisesRegex(ValueError,'mtime'):package.load_verified(self.input)
    def test_ground_truth_ids_not_clamped(self):
        self.gt.write_bytes(struct.pack('<II',1,10)+struct.pack('<10I',*([3]*10))+bytes(40))
        with self.assertRaisesRegex(ValueError,'ID outside'):package.finalize(self.spec,self.root/'invalid.json')
    def test_historical_no_package_compatible(self):
        code,result=self.execute(self.cli());self.assertEqual(code,0)
        manifest=json.loads((Path(result['run_directory'])/'manifest.json').read_text())
        self.assertIsNone(manifest['input_package_manifest_sha256']);self.assertIsNone(manifest['index_package_manifest_sha256'])
    def test_official_sift10m_requires_packages(self):
        with self.assertRaisesRegex(ValueError,'require both'):runner.resolve(runner.parser().parse_args(self.cli('--dataset-id','sift10m')))
    def test_mlflow_mirrors_package_digests(self):
        code,result=self.execute(self.bound());self.assertEqual(code,0);directory=Path(result['run_directory'])
        client=mock.Mock();client.get_experiment_by_name.return_value=types.SimpleNamespace(experiment_id='1')
        client.get_experiment.return_value=types.SimpleNamespace(artifact_location=(self.evidence/'mlflow/artifacts').as_uri())
        client.create_run.return_value=types.SimpleNamespace(info=types.SimpleNamespace(run_id='one'))
        with mock.patch.dict(sys.modules,{'mlflow':types.SimpleNamespace(MlflowClient=lambda **kwargs:client)}),mock.patch.dict(os.environ):
            result=mirror.mirror(directory,self.evidence)
        self.assertEqual(result['status'],'success');tags=client.create_run.call_args.kwargs['tags'];params={call.args[1]:call.args[2] for call in client.log_param.call_args_list}
        for record in (tags,params):
            self.assertEqual(record['input_package_manifest_sha256'],self.input_hash);self.assertEqual(record['index_package_manifest_sha256'],self.index_hash)
    def test_full_component_verification_is_explicit(self):
        value,digest=package.load_verified(self.input)
        with mock.patch.object(package,'digest_file',wraps=package.digest_file) as call:package.check_components(value,full=True)
        self.assertEqual(call.call_count,3)
    def synthetic_index(self):
        n,d,r,pq=3,2,2,1
        nodes=4096//(d+4*(r+1))
        raw=struct.pack('<II9Q',9,1,n,d,0,d+4*(r+1),nodes,n,0,r,0)
        self.components['disk_index'].write_bytes(raw+bytes(8192-len(raw)))
        self.components['tags'].write_bytes(struct.pack('<II3I',n,1,0,1,2))
        self.components['pq_compressed'].write_bytes(struct.pack('<II',n,pq)+bytes(n*pq))
        offsets=[4096];blocks=[]
        for rows,cols in ((256,d),(d,1),(d,1),(pq+1,1)):
            payload=struct.pack('<II',rows,cols)+bytes(rows*cols*4)
            if rows==pq+1 and cols==1:payload=struct.pack('<II2I',2,1,0,d)
            blocks.append(payload);offsets.append(offsets[-1]+len(payload))
        header=struct.pack('<II5Q',5,1,*offsets)
        self.components['pq_pivots'].write_bytes(header+bytes(4096-len(header))+b''.join(blocks))
        return n,d,r,pq
    def test_canonical_index_structure_validation(self):
        shape=self.synthetic_index();files,validation=index_tool.validate_index(self.prefix,*shape)
        self.assertTrue(validation['identity_tags_valid']);self.assertTrue(validation['pq_structure_valid'])
        self.assertEqual(validation['expected_disk_size_bytes'],8192)
    def test_index_structure_rejects_corrupt_pq_and_tags(self):
        shape=self.synthetic_index();self.components['pq_pivots'].write_bytes(b'corrupt')
        with self.assertRaisesRegex(ValueError,'PQ'):index_tool.validate_index(self.prefix,*shape)
        shape=self.synthetic_index();self.components['tags'].write_bytes(struct.pack('<II3I',3,1,0,1,1))
        with self.assertRaisesRegex(ValueError,'identity tags'):index_tool.validate_index(self.prefix,*shape)
    def test_index_structure_rejects_truncated_disk(self):
        shape=self.synthetic_index();self.components['disk_index'].write_bytes(b'bad')
        with self.assertRaisesRegex(ValueError,'Truncated'):index_tool.validate_index(self.prefix,*shape)
    def test_duplicate_roles_and_wrong_schema_types_rejected(self):
        value=json.loads(self.index.read_text());value['files'][1]['role']=value['files'][0]['role']
        with self.assertRaisesRegex(ValueError,'Duplicate'):package.validate_manifest(value)
        value=json.loads(self.index.read_text());value['build']['wall_time_s']='unknown'
        with self.assertRaisesRegex(ValueError,'schema'):package.validate_manifest(value)

    def test_range_rejects_full_body_before_read(self):
        stream=mock.Mock(status=200,headers={'Content-Range':'bytes 0-15/100','Content-Length':'16'})
        with mock.patch.object(acquire.urllib.request,'urlopen',return_value=stream):
            with self.assertRaisesRegex(ValueError,'refusing full-body'):acquire.response('https://example.test/base',0,15,100)
        stream.read.assert_not_called();stream.close.assert_called_once()
    def test_range_rejects_wrong_offset_length_or_changed_etag(self):
        for header in ({'Content-Range':'bytes 1-16/100','Content-Length':'16'},
                       {'Content-Range':'bytes 0-15/100','Content-Length':'15'},
                       {'Content-Range':'bytes 0-15/100','Content-Length':'16','ETag':'changed'}):
            stream=mock.Mock(status=206,headers=header)
            with mock.patch.object(acquire.urllib.request,'urlopen',return_value=stream):
                with self.assertRaises(ValueError):acquire.response('https://example.test/base',0,15,100,'expected')
            stream.read.assert_not_called();stream.close.assert_called_once()

if __name__=='__main__':unittest.main()
