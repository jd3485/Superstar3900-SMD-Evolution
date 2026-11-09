#!/usr/bin/env python3
"""V1.1: static math / schematic checks, NOT KiCad ERC, SPICE, or measurements."""
import json,csv,pathlib,re,itertools
p=pathlib.Path(__file__).resolve().parents[1]
s=(p/'04_KiCad/Sorgenti_Protezione_Ingresso_V1.1/S3900E_EFUSE_TPS26600_V1_1_DRAFT.kicad_sch').read_text()
report=json.loads((p/'03_Verifiche/Report_Protezione_V1.1.json').read_text())
rows=list(csv.DictReader((p/'04_KiCad/Sorgenti_Protezione_Ingresso_V1.1/Netlist_Intenzionale_TPS26600_V1.1.csv').open()))
assert len(set(re.findall(r'\(property "Reference" "([UFCDR]\d+)" \(at',s)))==10
assert '(dnp yes)' in s
assert any(x['Ref']=='U200' and x['Name']=='RTN' and x['Net_Intended']=='EFUSE_RTN' for x in rows)
assert any(x['Ref']=='U200' and x['Name']=='GND' and x['Net_Intended']=='GND_MAIN' for x in rows)
assert all(x['Net_Intended']!='GND_MAIN' for x in rows if x['Ref']=='R203')
assert report['UVLO_rise_corner_V'][0] < report['thresholds_typical']['UVLO_rising_V'] < report['UVLO_rise_corner_V'][1]
assert report['OVP_rise_corner_V'][0] < report['thresholds_typical']['OVP_rising_V'] < report['OVP_rise_corner_V'][1]
assert report['native_KiCad_ERC'] is False
print('PASS V1.1: resistor network, nets and RTN/GND separation (STATIC ONLY)')
