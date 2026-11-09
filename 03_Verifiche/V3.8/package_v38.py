#!/usr/bin/env python3
"""Create and verify cumulative V3.8 project archive and SHA256 manifest.
The generated manifest does not hash itself; the manifest is still included in the ZIP.
"""
from pathlib import Path
import csv,hashlib,zipfile,sys,json
ROOT=Path(__file__).resolve().parents[2]
ZIP=ROOT.parent/'Superstar3900_SMD_Evolution_V3.8.zip'
MAN=ROOT/'MANIFEST_SHA256_V3.8.csv'
EXCLUDED={'MANIFEST_SHA256_V3.8.csv'}
files=sorted([p for p in ROOT.rglob('*') if p.is_file() and p.relative_to(ROOT).as_posix() not in EXCLUDED],key=lambda p:p.relative_to(ROOT).as_posix())
with MAN.open('w',newline='',encoding='utf-8') as f:
 w=csv.writer(f);w.writerow(['path','size_bytes','sha256'])
 for p in files:
  w.writerow([p.relative_to(ROOT).as_posix(),p.stat().st_size,hashlib.sha256(p.read_bytes()).hexdigest()])
archive_files=files+[MAN]
with zipfile.ZipFile(ZIP,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for p in archive_files:z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(ZIP) as z:
 error=z.testzip()
 assert error is None,('CRC failure',error)
 names=z.namelist(); assert len(names)==len(archive_files) and len(names)==len(set(names))
 recs=list(csv.DictReader(z.read(MAN.name).decode().splitlines()))
 assert len(recs)==len(files)
 for r in recs:
  d=z.read(r['path']);assert len(d)==int(r['size_bytes']);assert hashlib.sha256(d).hexdigest()==r['sha256'],r['path']
 prev=zipfile.ZipFile(ROOT.parent/'Superstar3900_SMD_Evolution_V3.7.zip')
 old=set(prev.namelist());missing=old-set(names)
 assert not missing,missing
 allow={'README.md','RIPRENDI_IN_UNA_NUOVA_CHAT.md','00_Gestione_Progetto/REGISTRO_DECISIONI.md'}
 changed=[n for n in old if prev.read(n)!=z.read(n)]
 assert set(changed).issubset(allow),('unexpected historical changes',changed)
 stats={'revision':'V3.8','entries':len(names),'manifest_sha_entries':len(recs),'crc_ok':True,'all_sha256_verified':True,'v37_historical_entries_preserved':len(old),'modified_prior_files':sorted(changed),'zip_bytes':ZIP.stat().st_size}
print(json.dumps(stats,indent=2))
