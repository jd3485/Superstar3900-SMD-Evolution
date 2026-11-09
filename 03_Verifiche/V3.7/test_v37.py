#!/usr/bin/env python3
"""Read-only acceptance audit for V3.7 deliverables; no native KiCad DRC claimed."""
import importlib.util,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BD=ROOT/'03_Verifiche/V3.7/build_v37.py'
s=importlib.util.spec_from_file_location('v37',BD);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
a=m.load_v36_module();a.inspect=lambda p:m.rotated_inspect(a,p)
node,nets,items,pads,pmap=a.inspect(m.DST)
entries=m.test_footprint(a,node)
report,shapes=a.audit(m.DST,record=False)
checks={
 'parse_KiCad_compat_sexpr':node[0]=='kicad_pcb',
 '15_components':len(entries)==15,
 '8_nets':len(nets)==9,
 '43_tracks':len(a.subs(node,'segment'))==43,
 '64_vias':len(a.subs(node,'via'))==64,
 '4_unfilled_zones':len(a.subs(node,'zone'))==4 and 'filled_polygon' not in m.DST.read_text(),
 'all_7_signal_net_connectivity':not report['unconnected_nonground_nets'],
 '31_schematic_pin_compat':report['schematic_pin_assignments_ok']==31 and not report['schematic_pin_mismatches'],
 '24_ground_pads_reach_via':report['ground_pad_count']==24 and not report['ground_pads_without_explicit_local_via'],
 'zero_inter_net_2d_clashes':report['2d_clash_count']==0,
 'min_clearance_at_least_0_20':report['min_2d_inter_net_copper_clearance_mm']>=.20,
 'no_sma_central_drill':all('drill' not in str(entries[r]) for r in ['J101','J102','J103','J104']),
 'all_4_sma_centers_smd_2_05':all(any(p[1]=='1' and p[2]=='smd' and a.one(p,'size')[1:]==['2.050','2.050'] for p in a.subs(entries[r],'pad')) for r in ['J101','J102','J103','J104']),
 'both_footprint_modules':len(list(m.LIB.glob('*.kicad_mod')))==2,
 'pdf_dossier':(ROOT/'Superstar3900_Dossier_Tecnico_V3.7.pdf').exists(),
 'no_gerber_generated':not list(ROOT.rglob('*.gbr')) and not list(ROOT.rglob('*.drl')),
}
try:
 import fitz
 checks['pdf_3_pages']=len(fitz.open(ROOT/'Superstar3900_Dossier_Tecnico_V3.7.pdf'))==3
except ImportError:checks['pdf_3_pages']=False
results={'revision':'V3.7','checks':checks,'all_pass':all(checks.values()),'native_kicad_drc_ran':False,'manufacturer_footprint_approved':False,'pcbway_release':False}
(ROOT/'03_Verifiche/V3.7/Esito_Test_V3.7.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print('Tests',len(checks),'PASSED',sum(checks.values()),'FAILED',[k for k,v in checks.items() if not v]);sys.exit(not results['all_pass'])
