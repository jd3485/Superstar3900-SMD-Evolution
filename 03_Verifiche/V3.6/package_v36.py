#!/usr/bin/env python3
"""Package cumulative release V3.6 with fresh current-version SHA-256 manifest.
Old version manifests remain as historic release records and need not match revised README.
"""
from pathlib import Path
import csv,hashlib,zipfile,os
ROOT=Path(__file__).resolve().parents[2]
MANIFEST=ROOT/'MANIFEST_SHA256_V3.6.csv'
ZIP=Path('/mnt/data/Superstar3900_SMD_Evolution_V3.6.zip')
files=sorted(p for p in ROOT.rglob('*') if p.is_file() and p!=MANIFEST and '__pycache__' not in p.parts and not p.name.endswith('.pyc') and '_renders_pdf36' not in p.parts)
with MANIFEST.open('w',newline='',encoding='utf-8') as f:
    w=csv.writer(f);w.writerow(['Percorso_relativo','Dimensione_byte','SHA256'])
    for p in files:
        h=hashlib.sha256(p.read_bytes()).hexdigest()
        w.writerow([p.relative_to(ROOT).as_posix(),p.stat().st_size,h])
with zipfile.ZipFile(ZIP,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
    for p in files+[MANIFEST]: z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(ZIP) as z:
    assert z.testzip() is None
    rows=list(csv.DictReader(z.read('MANIFEST_SHA256_V3.6.csv').decode('utf-8').splitlines()))
    assert len(rows)==len(files)
    for row in rows:
        name=row['Percorso_relativo']; raw=z.read(name)
        assert hashlib.sha256(raw).hexdigest()==row['SHA256'],name
        assert len(raw)==int(row['Dimensione_byte']),name
    print('ARCHIVE_OK',ZIP,'ZIP entries',len(z.namelist()),'SHA files verified',len(rows),'bytes',ZIP.stat().st_size)
