#!/usr/bin/env python3
"""Check packaged ZIP CRC + the V4.2 manifest hashes, pure Python stdlib."""
import csv, hashlib, io, sys, zipfile
from pathlib import Path

def verify(path):
    with zipfile.ZipFile(path) as z:
        err=z.testzip()
        if err:raise ValueError('CRC mismatch: '+err)
        names={p for p in z.namelist() if not p.endswith('/')}
        manifest='MANIFEST_SHA256_V4.2.csv'
        if manifest not in names:raise ValueError('Manifest missing')
        rows=list(csv.DictReader(io.StringIO(z.read(manifest).decode('utf-8-sig'))))
        if len(rows)!=len(names)-1:raise ValueError('Manifest row count does not match file count')
        keys=[r['path'] for r in rows]
        if len(keys)!=len(set(keys)) or set(keys)!=names-{manifest}:raise ValueError('Manifest path set/duplication mismatch')
        for row in rows:
            n=row['path']; b=z.read(n)
            if len(b)!=int(row['size_bytes']) or hashlib.sha256(b).hexdigest()!=row['sha256']:
                raise ValueError('SHA/size mismatch: '+n)
        # Fixed project delivery invariants
        expected={'README.md','RIPRENDI_IN_UNA_NUOVA_CHAT.md',
            '06_Manuali/MU01_Manuale_Uso_Illustrato_Bozza_V4.0.pdf',
            '04_KiCad/Modulo_RX_Test_50ohm_V3.8/S3900E_RX_TEST_50R_V3_8_SHAPED_LAND_THERMAL_REVIEW_NOT_FOR_FAB.kicad_pcb',
            '03_Verifiche/V4.2/RISULTATO_GEOMETRIA_RF_V4.2.json',
            '00_Gestione_Progetto/REGISTRO_DECISIONI_V4.1_SNAPSHOT.md'}
        if not expected.issubset(names):raise ValueError('Required project files missing: '+str(expected-names))
        return len(names),len(rows)
if __name__=='__main__':
    try:
        z=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2].parent/'Superstar3900_SMD_Evolution_V4.2.zip'
        a,b=verify(z)
    except Exception as e:
        print('ARCHIVE V4.2 FAIL:',str(e),file=sys.stderr);sys.exit(1)
    print(f'ARCHIVE V4.2 PASS: {a} ZIP files; {b} SHA-256 entries; CRC OK')
