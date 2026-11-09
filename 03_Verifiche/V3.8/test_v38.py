#!/usr/bin/env python3
"""Read-only acceptance check of the V3.8 static model and artifacts."""
import json, sys, importlib.util
from pathlib import Path
R=Path(__file__).resolve().parents[2]
p=R/'03_Verifiche/V3.8/Audit_Footprint_Termico_V3.8.json'
d=json.loads(p.read_text())
checks=dict(d['checks'])
checks['report_all_pass']=d['all_pass']
checks['no_native_drc_claim']=d['native_kicad_drc_ran'] is False
checks['release_blocked']='BLOCKED' in d['manufacturing_release']
checks['pdf_report_present']=(R/'Superstar3900_Dossier_Tecnico_V3.8.pdf').is_file()
checks['schematic_pin_crosswalk']=d['audit']['schematic_pin_assignments_ok']==31
checks['no_gerber_or_drill_output']=not list(R.rglob('*.gbr')) and not list(R.rglob('*.drl'))
checks['footprint_library_both_files']=len(list((R/'04_KiCad/Modulo_RX_Test_50ohm_V3.8/S3900E_V38_Review.pretty').glob('*.kicad_mod')))==2
try:
 import fitz
 checks['pdf_three_pages']=len(fitz.open(R/'Superstar3900_Dossier_Tecnico_V3.8.pdf'))==3
except ImportError:checks['pdf_three_pages']=False
out={'revision':'V3.8','passed':sum(checks.values()),'total':len(checks),'all_pass':all(checks.values()),'checks':checks}
(R/'03_Verifiche/V3.8/Esito_Test_V3.8.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print('V3.8 acceptance: ',sum(checks.values()),'/',len(checks),'passed')
sys.exit(0 if out['all_pass'] else 1)
