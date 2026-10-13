"""Portable, read-only paper-native bundle validation; hashes once per campaign."""
import json
from pathlib import Path
import shutil
import struct
from paper_rebaseline import digest

ROLES = {'base','query','ground_truth','disk_index','pq_compressed','pq_pivots',
         'memory_graph','memory_data','memory_tags'}
PAPER = 'd18dcd16fece1c9d1dea356d783ebba2ed649e54'


def components(manifest, data_root, index_root):
    if manifest.get('schema') != 'portable-paper-sift10m-v1' or manifest.get('subject') != 'PAPER_GCC13_PORTABLE':
        raise ValueError('Only the explicitly named paper-native bundle is supported')
    if manifest.get('upstream_commit') != PAPER or manifest.get('parameters',{}).get('pq_bytes') != 32:
        raise ValueError('Wrong upstream or PQ configuration; modern indexes are not interchangeable')
    if manifest.get('dataset') != dict(N=10000000,D=128,dtype='uint8',metric='l2',queries=10000,gt_top_k=100):
        raise ValueError('Dataset binding mismatch')
    files = manifest['files']
    if len(files) != len(ROLES) or {f['role'] for f in files} != ROLES:
        raise ValueError('Missing or duplicate bundle role')
    roots = {'data':Path(data_root).resolve(), 'index':Path(index_root).resolve()}
    found = {}
    for f in files:
        relative = Path(f['path'])
        if relative.is_absolute() or '..' in relative.parts or f['root'] not in roots:
            raise ValueError('Unsafe component path')
        if f['root'] != ('data' if f['role'] in ('base','query','ground_truth') else 'index'):
            raise ValueError('Role/root mismatch')
        path = roots[f['root']]/relative
        if not path.resolve().is_relative_to(roots[f['root']]):
            raise ValueError('Component escapes root')
        found[f['role']] = (path,f)
    return found


def verify(manifest_path, data_root, index_root, full=True):
    manifest_path=Path(manifest_path); m=json.loads(manifest_path.read_text())
    files=components(m,data_root,index_root)
    for role,(path,f) in files.items():
        if not path.is_file() or path.stat().st_size != f['size_bytes']:
            raise ValueError('Missing/truncated component: '+role)
        if full and digest(path) != f['sha256']:
            raise ValueError('Checksum mismatch: '+role)
    entry=m['entry_nodes']
    if not 0<entry<=10000000: raise ValueError('Invalid entry cardinality')
    shapes={'base':(10000000,128),'query':(10000,128),'ground_truth':(10000,100),
            'pq_compressed':(10000000,32),'memory_data':(entry,128),'memory_tags':(entry,1)}
    for role,shape in shapes.items():
        with files[role][0].open('rb') as f:
            if struct.unpack('<II',f.read(8)) != shape: raise ValueError('Wrong shape: '+role)
        element_bytes=8 if role=='ground_truth' else 4 if role=='memory_tags' else 1
        if files[role][0].stat().st_size!=8+shape[0]*shape[1]*element_bytes:
            raise ValueError('Wrong payload size: '+role)
    with files['disk_index'][0].open('rb') as f:
        if struct.unpack('<II',f.read(8)) != (9,1): raise ValueError('Wrong disk metadata')
        meta=struct.unpack('<9Q',f.read(72))
    if meta[:2]!=(10000000,128) or meta[3:5]!=(388,10) or meta[7]!=4096004096 or files['disk_index'][0].stat().st_size!=meta[7]:
        raise ValueError('Disk geometry differs from native R64 uint8 contract')
    if Path(index_root,m['index_prefix']+'_disk.index.tags').exists():
        raise ValueError('Unexpected disk tags alter implicit native mapping')
    return dict(valid=True,manifest_sha256=digest(manifest_path),full_hashes=full,
                files={role:dict(path=str(path),size_bytes=path.stat().st_size,
                                mtime_ns=path.stat().st_mtime_ns,sha256=f['sha256'])
                       for role,(path,f) in files.items()})


def unchanged(fingerprint):
    for role,f in fingerprint['files'].items():
        p=Path(f['path']);s=p.stat()
        if s.st_size!=f['size_bytes'] or s.st_mtime_ns!=f['mtime_ns']:
            raise ValueError('Verified component changed: '+role)


def copy_bundle(manifest_path,data_root,index_root,destination):
    verify(manifest_path,data_root,index_root,True)
    dest=Path(destination)
    if dest.exists():raise FileExistsError('Destination must be absent; never overwrite')
    dest.mkdir(parents=True)
    m=json.loads(Path(manifest_path).read_text())
    for role,(src,f) in components(m,data_root,index_root).items():
        target=dest/f['root']/f['path'];target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,target)
        if digest(target)!=f['sha256']:raise ValueError('Copied bytes differ: '+role)
    shutil.copyfile(manifest_path,dest/'MANIFEST.json')
    verify(dest/'MANIFEST.json',dest/'data',dest/'index',True)
    return dict(valid=True,destination=str(dest))
