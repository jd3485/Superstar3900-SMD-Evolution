#!/usr/bin/env python3
"""Verify V4.5 ZIP CRC, SHA-256 manifest and optional V4.4 cumulative preservation."""
import argparse, csv, hashlib, io, json, zipfile
from pathlib import PurePosixPath

MANIFEST='MANIFEST_SHA256_V4.5.csv'
SNAPSHOTS={
 'README.md':'00_Gestione_Progetto/README_ROOT_V4.4_SNAPSHOT.md',
 'RIPRENDI_IN_UNA_NUOVA_CHAT.md':'00_Gestione_Progetto/RIPRENDI_ROOT_V4.4_SNAPSHOT.md',
 '00_Gestione_Progetto/REGISTRO_DECISIONI.md':'00_Gestione_Progetto/REGISTRO_DECISIONI_V4.4_SNAPSHOT.md',
}
def verify(current, previous=None):
    with zipfile.ZipFile(current) as z:
        names=z.namelist()
        assert len(names)==len(set(names)), 'Duplicate file names'
        assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names),'Unsafe ZIP paths'
        assert z.testzip() is None, 'ZIP CRC failed'
        rows=list(csv.DictReader(io.StringIO(z.read(MANIFEST).decode('utf8'))))
        expected={r['path']:(int(r['size_bytes']),r['sha256']) for r in rows}
        assert set(expected)==set(names)-{MANIFEST},'Manifest paths not exact ZIP file set'
        for path,(size,sha) in expected.items():
            content=z.read(path)
            assert len(content)==size, 'Size mismatch '+path
            assert hashlib.sha256(content).hexdigest()==sha, 'SHA mismatch '+path
        result={'total_files':len(names),'manifest_file_hashes':len(rows),'crc':'PASS','sha256':'PASS'}
        if previous:
            with zipfile.ZipFile(previous) as prior:
                before=[x for x in prior.namelist() if not x.endswith('/')]
                replaced=[]
                for path in before:
                    old=prior.read(path)
                    if z.read(path)!=old:
                        assert path in SNAPSHOTS,'Untracked changed file '+path
                        assert z.read(SNAPSHOTS[path])==old, 'Snapshot differs '+path
                        replaced.append(path)
                assert len(before)==700, 'Unexpected prior archive size'
                result.update({'prior_files_checked':len(before),'preserved_with_snapshots':replaced,
                               'prior_crc':'PASS' if prior.testzip() is None else 'FAIL'})
        return result

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('v45zip');ap.add_argument('--previous')
    args=ap.parse_args()
    print(json.dumps(verify(args.v45zip,args.previous),ensure_ascii=False,indent=2))
