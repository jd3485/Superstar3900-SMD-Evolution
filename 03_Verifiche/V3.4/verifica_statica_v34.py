# V3.4 - ripetere controlli strutturali, NON sostituisce KiCad ERC/DRC
from pathlib import Path
import re, json
p=Path(__file__).parents[2]/'04_KiCad'/'Modulo_RX_Test_50ohm_V3.4'/'S3900E_RX_TEST_50R_V3_4_GND_STUDY_NOT_FOR_FAB.kicad_pcb'
s=p.read_text(encoding='utf8')
checks={'componenti':s.count('(footprint '),'zone':s.count('(zone '),'via':s.count('(via '),'segmenti':s.count('(segment '),'reti':len([r for r in s.splitlines() if r.startswith('  (net ')])-1}
assert checks=={'componenti':15,'zone':3,'via':2,'segmenti':0,'reti':8},checks
print(json.dumps(checks,indent=2))
