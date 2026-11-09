from pathlib import Path
import re, json
here=Path(__file__).resolve().parents[2]/'04_KiCad'/'Modulo_RX_Test_50ohm_V3.3'
t=(here/'S3900E_RX_TEST_50R_V3_3_PLACEMENT_DRAFT.kicad_pcb').read_text()
assert t.count('  (footprint ')==15
assert t.count('  (net ')==9
assert '(start 20 20) (end 130 82)' in t
assert all(name in t for name in ['RF_LNA_INPUT','RF_LNA_IC_IN','RF_BIAS_OUT','RF_LNA_OUT','RF_ATTEN_IN','RF_ATTEN_OUT','+5V_BENCH','GND_RF'])
assert not re.search(r'\(segment |\(zone |\(via ',t)
assert t.count('(pad "2" smd rect')>=2
print('PASS: static PCB structure checks (not native KiCad DRC)')
