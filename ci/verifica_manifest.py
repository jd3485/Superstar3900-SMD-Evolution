#!/usr/bin/env python3
"""Confronta i file della release con il manifest SHA256 (solo libreria standard)."""
from pathlib import Path
import argparse,csv,hashlib,sys

def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as stream:
  for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('manifest');ap.add_argument('--attesi',type=int,default=None);args=ap.parse_args()
 root=Path(__file__).resolve().parents[1]
 mf=(root/args.manifest).resolve()
 if not mf.is_relative_to(root.resolve()):raise SystemExit('Manifest fuori dalla radice')
 with mf.open(newline='',encoding='utf-8-sig') as f:rows=list(csv.DictReader(f))
 if args.attesi is not None and len(rows)!=args.attesi:raise SystemExit(f'Attesi {args.attesi}; trovati {len(rows)}')
 errors=[];seen=set()
 for r in rows:
  rel=r['relative_path'];target=(root/rel).resolve()
  if rel in seen or not target.is_relative_to(root.resolve()):errors.append(f'Percorso non valido: {rel}');continue
  seen.add(rel)
  if not target.is_file():errors.append(f'Mancante: {rel}')
  elif digest(target)!=r['sha256']:errors.append(f'SHA errato: {rel}')
  elif target.stat().st_size!=int(r['bytes']):errors.append(f'Dimensione errata: {rel}')
 print(f'MANIFEST {mf.name}: {len(rows)} file; errori {len(errors)}')
 for e in errors[:30]:print('ERRORE:',e)
 return 0 if not errors else 1
if __name__=='__main__':sys.exit(main())
