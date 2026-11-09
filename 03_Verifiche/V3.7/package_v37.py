#!/usr/bin/env python3
"""Generate SHA256 manifest (excluding self), cumulative ZIP and verify both."""
import csv,hashlib,zipfile,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
MANIFEST=ROOT/'MANIFEST_SHA256_V3.7.csv'
ZIP=Path('/mnt/data/Superstar3900_SMD_Evolution_V3.7.zip')
files=sorted((p for p in ROOT.rglob('*') if p.is_file() and p!=MANIFEST and '__pycache__' not in p.parts and p.suffix!='.pyc'),key=lambda p:p.relative_to(ROOT).as_posix())
with MANIFEST.open('w',newline='',encoding='utf-8') as fp:
    wr=csv.writer(fp);wr.writerow(['path','size_bytes','sha256'])
    for p in files:
        wr.writerow([p.relative_to(ROOT).as_posix(),p.stat().st_size,hashlib.sha256(p.read_bytes()).hexdigest()])
with zipfile.ZipFile(ZIP,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
    for p in files+[MANIFEST]:z.write(p,arcname=p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(ZIP) as z:
    bad=z.testzip()
    if bad:raise ValueError('CRC failed '+bad)
    members=set(z.namelist())
    assert len(members)==len(files)+1
    with z.open(MANIFEST.name) as f:
        import io
        rows=list(csv.DictReader(io.TextIOWrapper(f,encoding='utf-8')))
    assert len(rows)==len(files)
    for row in rows:
        name=row['path'];b=z.read(name)
        assert len(b)==int(row['size_bytes'])
        assert hashlib.sha256(b).hexdigest()==row['sha256'],name
print('Verified',len(members),'files (incl manifest), ZIP bytes',ZIP.stat().st_size)
print('Archive:',ZIP)
