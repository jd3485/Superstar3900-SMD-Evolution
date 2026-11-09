#!/usr/bin/env python3
"""Verify V4.3 ZIP internal SHA256 manifest and zip CRC."""
import csv,zipfile,hashlib,sys,io
from pathlib import Path

def verify(path):
 with zipfile.ZipFile(path) as z:
  assert z.testzip() is None,'ZIP CRC failed'
  names=set(i.filename for i in z.infolist() if not i.is_dir())
  manifest='MANIFEST_SHA256_V4.3.csv'
  rows=list(csv.DictReader(io.StringIO(z.read(manifest).decode('utf-8'))))
  assert len(rows)==len(names)-1
  listed=set()
  for row in rows:
   n=row['path'];listed.add(n)
   data=z.read(n)
   assert len(data)==int(row['size_bytes']),n+' length mismatch'
   assert hashlib.sha256(data).hexdigest()==row['sha256'],n+' SHA256 mismatch'
  assert listed==names-{manifest},'Missing or extra files'
  return len(names),len(rows)
if __name__=='__main__':
 n,h=verify(Path(sys.argv[1]));print(f'Verified: {n} files, {h} SHA256 rows, CRC OK')
