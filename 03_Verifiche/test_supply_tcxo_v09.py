#!/usr/bin/env python3
"""V0.9 structural smoke test only: no KiCad ERC or SPICE validation."""
import re,json,pathlib,csv
root=pathlib.Path(__file__).resolve().parents[1]
src=root/'04_KiCad/Sorgenti_Modulo_PLL_V0.9/S3900E_PLL_V0_9_LDO_TCXO_DRAFT.kicad_sch'
t=src.read_text()
refs=re.findall(r'\(symbol \(lib_id "S3900E:[^"]*"\) \(at [^)]*\) \(unit 1\).*?\(property "Reference" "([A-Z]+\d+)"',t,re.S)
assert len(refs)==len(set(refs))
for r in ('U1','U2','U3','Y1','R60','R61','C58'):
 assert r in refs,r
for n in ('3V3_REF_LDO','5V_RF_PREREGULATED','PLL_OSCINP_AC'):
 assert t.count('"'+n+'"')>=2,n
assert 'OSCIN_M_AC_PENDING' not in t
assert '(no_connect (at 91.9 86.36)' in t
for r in ('U2','U3'):
 assert t.count('(reference "'+r+'")')==1
assert abs((5-3.3)*0.090-0.153)<1e-9
assert 0<39e6*0.28e-6<12
print('PASS V0.9: component refs, named nets, reference NC and budget arithmetic. No ERC.')
