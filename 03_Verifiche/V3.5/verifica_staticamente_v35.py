#!/usr/bin/env python3
"""V3.5 simple structural test -- NOT a KiCad DRC or impedance field solver."""
import json, re
from pathlib import Path
r=Path(__file__).resolve().parents[2]
p=r/'04_KiCad/Modulo_RX_Test_50ohm_V3.5/S3900E_RX_TEST_50R_V3_5_PILOT_ROUTES_NOT_FOR_FAB.kicad_pcb'
t=p.read_text(encoding='utf8')
summary=json.loads((Path(__file__).parent/'Rapporto_Verifica_Routing_V3.5.json').read_text(encoding='utf8'))['summary']
assert t.count('(footprint ')==summary['footprints']==15
assert t.count('(segment ')==summary['segments']
assert t.count('(zone ')==3 and t.count('(via ')==4
assert 'ADL5535_SOT89_FIG17_REVIEW' in t
assert t.count('CONSMA002_REVIEW_CENTER_FEATURE_UNRESOLVED')==4
assert 'NOT FOR FAB' in t
print('STATIC V3.5 CHECK PASSED',summary)
