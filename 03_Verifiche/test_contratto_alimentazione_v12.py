#!/usr/bin/env python3
"""Static label connectivity contract only. NOT KiCad ERC or SPICE."""
import re,json,sys
from pathlib import Path
here=Path(__file__).resolve().parent
folder=here.parent/'04_KiCad'/'Integrazione_Alimentazioni_V1.2'
contract=json.loads((folder/'Contratto_Reti_Alimentazione_V1.2.json').read_text())
labels={}
for kind in ('EFUSE','BUCK','PLL'):
 s=(folder/f'S3900E_12_{kind}_INTEGRATION_DRAFT.kicad_sch').read_text()
 labels[kind]=set(re.findall(r'\(label "([^"]+)"',s))
for c in contract['interfaces']:
 for k in c['must_be_in']:assert c['net'] in labels[k],(k,c['net'])
 for k in c.get('must_not_be_in',[]):assert c['net'] not in labels[k],(k,c['net'])
assert 'TCXO_PIN10_AFC_OR_GND_TBD' in labels['PLL']
assert 'Fuse:Fuse_1206_3216Metric' not in (folder/'S3900E_12_EFUSE_INTEGRATION_DRAFT.kicad_sch').read_text()
print('PASS: etichette e riservatezza delle reti; NON equivalgono a netlist KiCad.')
