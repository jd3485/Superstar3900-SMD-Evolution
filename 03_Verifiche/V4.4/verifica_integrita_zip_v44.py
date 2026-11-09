#!/usr/bin/env python3
"""Validate cumulative V4.4 ZIP SHA-256 manifest and its ZIP CRC."""
import csv, zipfile, hashlib, io, sys
from pathlib import Path

def verify(path):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None,'ZIP CRC failure'
        names={it.filename for it in z.infolist() if not it.is_dir()}
        mf='MANIFEST_SHA256_V4.4.csv'
        data=list(csv.DictReader(io.StringIO(z.read(mf).decode('utf-8'))))
        assert len(data)==len(names)-1,'manifest row count mismatch'
        listed=set()
        for row in data:
            name=row['path']; listed.add(name)
            buf=z.read(name)
            assert len(buf)==int(row['size_bytes']),name+' length mismatch'
            assert hashlib.sha256(buf).hexdigest()==row['sha256'],name+' hash mismatch'
        assert listed==names-{mf},'missing/extra files'
        return len(names),len(data)
if __name__=='__main__':
    n,h=verify(Path(sys.argv[1]))
    print(f'Verified {n} files; {h} SHA-256 entries; CRC OK')
